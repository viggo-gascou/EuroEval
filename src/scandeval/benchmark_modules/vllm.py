"""Generative models using the vLLM inference framework."""

import collections.abc as c
import importlib.util
import itertools as it
import json
import logging
import os
import random
import re
import sys
import typing as t
from functools import partial
from pathlib import Path
from time import sleep
from types import MethodType

import torch
from datasets import DatasetDict
from huggingface_hub import snapshot_download
from pydantic import conlist, create_model
from tqdm.auto import tqdm
from transformers import AutoConfig, AutoTokenizer, PreTrainedTokenizer, Trainer
from urllib3.exceptions import RequestError

from ..constants import (
    GENERATIVE_PIPELINE_TAGS,
    MAX_LOGPROBS,
    MERGE_TAGS,
    REASONING_MAX_TOKENS,
    TASK_GROUPS_USING_LOGPROBS,
    TASKS_USING_JSON,
)
from ..data_models import (
    BenchmarkConfig,
    DatasetConfig,
    GenerativeModelOutput,
    ModelConfig,
    Task,
)
from ..enums import (
    BatchingPreference,
    GenerativeType,
    InferenceBackend,
    ModelType,
    TaskGroup,
)
from ..exceptions import (
    InvalidBenchmark,
    InvalidModel,
    NeedsEnvironmentVariable,
    NeedsExtraInstalled,
)
from ..languages import get_all_languages
from ..task_utils import (
    question_answering,
    sequence_classification,
    text_to_text,
    token_classification,
)
from ..types import ExtractLabelsFunction
from ..utils import (
    clear_memory,
    create_model_cache_dir,
    get_bos_token,
    get_end_of_chat_token_ids,
    get_eos_token,
    log_once,
    should_prompts_be_stripped,
)
from .hf import HuggingFaceEncoderModel, get_model_repo_info, load_hf_model_config

if t.TYPE_CHECKING or importlib.util.find_spec("vllm") is not None:
    from vllm import LLM, RequestOutput, SamplingParams
    from vllm.lora.request import LoRARequest
    from vllm.sampling_params import GuidedDecodingParams

    try:
        from vllm.model_executor.parallel_utils.parallel_state import (
            destroy_model_parallel,
        )
    except ImportError:
        from vllm.distributed.parallel_state import destroy_model_parallel

if t.TYPE_CHECKING or importlib.util.find_spec("ray") is not None:
    import ray

logger = logging.getLogger("scandeval")


class VLLMModel(HuggingFaceEncoderModel):
    """A generative model using the vLLM inference framework."""

    fresh_model = False
    batching_preference = BatchingPreference.ALL_AT_ONCE
    high_priority = True

    def __init__(
        self,
        model_config: ModelConfig,
        dataset_config: DatasetConfig,
        benchmark_config: BenchmarkConfig,
    ) -> None:
        """Initialise the vLLM model.

        Args:
            model_config:
                The model configuration.
            dataset_config:
                The dataset configuration.
            benchmark_config:
                The benchmark configuration.
        """
        if (
            importlib.util.find_spec("vllm") is None
            or importlib.util.find_spec("ray") is None
        ):
            raise NeedsExtraInstalled(extra="generative")

        output_scores = dataset_config.task.task_group in TASK_GROUPS_USING_LOGPROBS
        model, tokenizer = load_model_and_tokenizer(
            model_config=model_config,
            benchmark_config=benchmark_config,
            output_scores=output_scores,
        )
        self._model: LLM = model
        self._tokenizer: PreTrainedTokenizer = tokenizer
        self.end_of_reasoning_token_id = get_end_of_reasoning_token_id(
            model=self._model, tokenizer=self._tokenizer
        )

        # We specify `HuggingFaceEncoderModel` here instead of `VLLMModel`, as we want
        # to call the `__init__` method of the `BenchmarkModule` class.
        super(HuggingFaceEncoderModel, self).__init__(
            model_config=model_config,
            dataset_config=dataset_config,
            benchmark_config=benchmark_config,
        )

        self.buffer["output_scores"] = output_scores
        self.buffer["instruction_model"] = self._tokenizer.chat_template is not None
        if self.model_config.adapter_base_model_id is not None:
            adapter_path = snapshot_download(
                repo_id=self.model_config.model_id,
                cache_dir=Path(self.model_config.model_cache_dir),
            )
            self.buffer["lora_request"] = LoRARequest(
                lora_name="adapter", lora_int_id=1, lora_path=adapter_path
            )

    @property
    def generative_type(self) -> GenerativeType | None:
        """Get the generative type of the model.

        Returns:
            The generative type of the model, or None if it has not been set yet.
        """
        if not hasattr(self, "_tokenizer"):
            return None
        elif self.end_of_reasoning_token_id is not None:
            return GenerativeType.REASONING
        elif self._tokenizer.chat_template is not None:
            return GenerativeType.INSTRUCTION_TUNED
        else:
            return GenerativeType.BASE

    @property
    def extract_labels_from_generation(self) -> ExtractLabelsFunction:
        """The function used to extract the labels from the generated output.

        Returns:
            The function used to extract the labels from the generated output.
        """
        match self.dataset_config.task.task_group:
            case (
                TaskGroup.SEQUENCE_CLASSIFICATION
                | TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION
            ):
                return partial(
                    sequence_classification.extract_labels_from_generation,
                    dataset_config=self.dataset_config,
                )
            case TaskGroup.TEXT_TO_TEXT:
                return text_to_text.extract_labels_from_generation
            case TaskGroup.TOKEN_CLASSIFICATION:
                return partial(
                    token_classification.extract_labels_from_generation,
                    dataset_config=self.dataset_config,
                )
            case TaskGroup.QUESTION_ANSWERING:
                return question_answering.extract_labels_from_generation
            case _:
                raise NotImplementedError(
                    f"Unsupported task group: {self.dataset_config.task.task_group}."
                )

    def prepare_dataset(
        self, dataset: DatasetDict, task: Task, itr_idx: int
    ) -> DatasetDict:
        """Prepare the dataset for the model.

        This includes things like tokenisation.

        Args:
            dataset:
                The dataset to prepare.
            task:
                The task to prepare the dataset for.
            itr_idx:
                The index of the dataset in the iterator.

        Returns:
            The prepared dataset.
        """
        if task.task_group == TaskGroup.QUESTION_ANSWERING:
            dataset = dataset.map(
                lambda examples: dict(
                    label=[
                        dict(
                            id=id,
                            answers=dict(
                                answer_start=answer_dct["answer_start"],
                                text=[
                                    answer_text.lower()
                                    for answer_text in answer_dct["text"]
                                ],
                            ),
                        )
                        for id, answer_dct in zip(examples["id"], examples["answers"])
                    ]
                ),
                batched=True,
                load_from_cache_file=False,
                keep_in_memory=True,
            )

        if self.benchmark_config.few_shot:
            few_shot_examples = self._extract_few_shot_examples(
                dataset=dataset, task=task, itr_idx=itr_idx
            )
        else:
            few_shot_examples = list()

        dataset["test"] = dataset["test"].map(
            partial(self._apply_prompt, few_shot_examples=few_shot_examples, task=task),
            batched=True,
            load_from_cache_file=False,
            keep_in_memory=True,
        )

        return dataset

    def generate(self, inputs: dict) -> GenerativeModelOutput:
        """Generate outputs from the model.

        Args:
            inputs:
                A batch of inputs to pass through the model.

        Returns:
            The generated model outputs.
        """
        # Define which tokens to use as stopping criteria. We want to use the padding
        # token, end-of-sentence token, and a double newline if the model isn't
        # instruction tuned (since these separate the few-shot examples in the input in
        # this case)
        stop_tokens: list[str] = list()
        if self.buffer["instruction_model"] is False:
            stop_tokens.append("\n\n")
        if self._tokenizer.pad_token_id is not None:
            stop_tokens.append(self._tokenizer.pad_token)
        if self._tokenizer.eos_token_id is not None:
            stop_tokens.append(self._tokenizer.eos_token)
            if self._tokenizer.pad_token_id is None:
                self._tokenizer.pad_token_id = self._tokenizer.eos_token_id
                self._tokenizer.pad_token = self._tokenizer.eos_token
        if (
            self._tokenizer.bos_token_id is not None
            and self._tokenizer.pad_token_id is None
        ):
            self._tokenizer.pad_token_id = self._tokenizer.bos_token_id
            self._tokenizer.pad_token = self._tokenizer.bos_token
        elif (
            self._tokenizer.eos_token_id is not None
            and self._tokenizer.pad_token_id is None
        ):
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id
            self._tokenizer.pad_token = self._tokenizer.eos_token
        elif self._tokenizer.pad_token_id is None:
            pad_token_candidates = ["<pad>", "[pad]", "<|endoftext|>", "<|im_end|>"]
            pad_token_candidates.extend([c.upper() for c in pad_token_candidates])
            for candidate in pad_token_candidates:
                if candidate in self._tokenizer.get_vocab():
                    pad_token_id = self._tokenizer.get_vocab()[candidate]
                    self._tokenizer.pad_token = candidate
                    self._tokenizer.pad_token_id = pad_token_id
                    break
            else:
                raise InvalidModel(
                    "Could not find a suitable token to use as a padding token, since "
                    "the model does not have a BOS, EOS, or padding token, and does "
                    f"not have any of the following tokens in its vocabulary: "
                    f"{pad_token_candidates}."
                )

        assert self._tokenizer.pad_token_id is not None

        # Add end of chat token as a stopping token, if it exists
        end_of_chat_token_ids = get_end_of_chat_token_ids(tokenizer=self._tokenizer)
        if end_of_chat_token_ids is not None:
            end_of_chat_token = self._tokenizer.decode(end_of_chat_token_ids).strip()
            if end_of_chat_token:
                stop_tokens.append(end_of_chat_token)

        if self.dataset_config.task in TASKS_USING_JSON:
            ner_tag_names = list(self.dataset_config.prompt_label_mapping.values())
            keys_and_their_types: dict[str, t.Any] = {
                tag_name: (conlist(str, max_length=5), ...)
                for tag_name in ner_tag_names
            }
            pydantic_class = create_model("AnswerFormat", **keys_and_their_types)
            schema = pydantic_class.model_json_schema()
            guided_decoding = GuidedDecodingParams(
                json=schema, backend="outlines", whitespace_pattern=r" ?"
            )
        else:
            guided_decoding = None

        # Define the parameters used for vLLM generation
        max_tokens: int = (
            REASONING_MAX_TOKENS
            if self.generative_type == GenerativeType.REASONING
            else self.dataset_config.max_generated_tokens
        )
        sampling_params = SamplingParams(
            max_tokens=max_tokens,
            logprobs=MAX_LOGPROBS if self.buffer["output_scores"] else None,
            temperature=0.0,
            stop=[stop_token for stop_token in stop_tokens if stop_token],
            guided_decoding=guided_decoding,
        )

        # If any of the prompts are empty then we need to replace them with a BOS token
        # so that the vLLM model can generate from them
        prompts: list[str] = inputs["text"]
        if any(len(prompt) == 0 for prompt in prompts):
            logger.debug("Found empty prompts, replacing with BOS token.")
            prompts = [
                prompt if len(prompt) > 0 else str(self._tokenizer.bos_token)
                for prompt in prompts
            ]

        # Strip the prompts if the model's tokeniser requires it
        labels_to_be_generated = list(self.dataset_config.prompt_label_mapping.values())
        if len(labels_to_be_generated) == 0:
            labels_to_be_generated = ["negative", "positive"]
        if not self.buffer.get(
            "instruction_model", False
        ) and should_prompts_be_stripped(
            labels_to_be_generated=labels_to_be_generated, tokenizer=self._tokenizer
        ):
            log_once(message="Stripping prompts.", level=logging.DEBUG)
            prompts = [prompt.strip() for prompt in prompts]

        # Generate sequences using vLLM
        input_is_a_test = len(prompts) == 1 and len(set(prompts[0])) == 1
        raw_outputs = self._model.generate(
            prompts=prompts,
            sampling_params=sampling_params,
            use_tqdm=(not input_is_a_test),
            lora_request=self.buffer.get("lora_request"),
        )
        completion_ids: list[list[int]] = [
            output.outputs[0].token_ids for output in raw_outputs
        ]
        if self.end_of_reasoning_token_id in completion_ids[0]:
            completion_ids = [
                token_ids[token_ids.index(self.end_of_reasoning_token_id) + 2 :]
                if self.end_of_reasoning_token_id in token_ids
                else token_ids
                for token_ids in completion_ids
            ]
        completions = self._tokenizer.batch_decode(
            sequences=[
                torch.LongTensor(completion_id) for completion_id in completion_ids
            ],
            skip_special_tokens=True,
        )
        completions = [completion.strip() for completion in completions]

        # Add logprobs scores to the output
        if self.buffer["output_scores"]:
            scores: list[list[list[tuple[str, float]]]] = [
                [
                    [
                        (obj.decoded_token, obj.logprob)
                        for obj in token_logprobs_dict.values()
                    ]
                    for token_logprobs_dict in raw_output.outputs[0].logprobs
                ]
                for raw_output in raw_outputs
            ]
            scores = [
                score_list[
                    raw_output.outputs[0].token_ids.index(
                        self.end_of_reasoning_token_id
                    )
                    + 2 :
                ]
                if self.end_of_reasoning_token_id in raw_output.outputs[0].token_ids
                else score_list
                for raw_output, score_list in zip(raw_outputs, scores)
            ]
            output = GenerativeModelOutput(sequences=completions, scores=scores)
        else:
            output = GenerativeModelOutput(sequences=completions)

        return output

    @classmethod
    def model_exists(
        cls, model_id: str, benchmark_config: BenchmarkConfig
    ) -> bool | NeedsExtraInstalled | NeedsEnvironmentVariable:
        """Check if a model exists.

        Args:
            model_id:
                The model ID.
            benchmark_config:
                The benchmark configuration.

        Returns:
            Whether the model exists, or an error describing why we cannot check
            whether the model exists.
        """
        using_api = (
            benchmark_config.api_base is not None
            or benchmark_config.api_version is not None
        )
        if using_api:
            return False

        model_id, revision = (
            model_id.split("@") if "@" in model_id else (model_id, "main")
        )
        model_info = get_model_repo_info(
            model_id=model_id, revision=revision, benchmark_config=benchmark_config
        )
        return (
            model_info is not None
            and model_info.pipeline_tag in GENERATIVE_PIPELINE_TAGS
        )

    @classmethod
    def get_model_config(
        cls, model_id: str, benchmark_config: BenchmarkConfig
    ) -> ModelConfig:
        """Fetch the model configuration.

        Args:
            model_id:
                The model ID.
            benchmark_config:
                The benchmark configuration.

        Returns:
            The model configuration.
        """
        model_id, revision = (
            model_id.split("@") if "@" in model_id else (model_id, "main")
        )
        model_info = get_model_repo_info(
            model_id=model_id, revision=revision, benchmark_config=benchmark_config
        )
        if model_info is None:
            raise InvalidModel(f"The model {model_id!r} could not be found.")

        language_mapping = get_all_languages()
        language_codes = list(language_mapping.keys())

        model_config = ModelConfig(
            model_id=model_id,
            revision=revision,
            task=model_info.pipeline_tag,
            languages=[
                language_mapping[tag]
                for tag in model_info.tags
                if tag in language_codes
            ],
            merge=any(tag in model_info.tags for tag in MERGE_TAGS),
            inference_backend=InferenceBackend.VLLM,
            model_type=ModelType.GENERATIVE,
            fresh=False,
            model_cache_dir=create_model_cache_dir(
                cache_dir=benchmark_config.cache_dir, model_id=model_id
            ),
            adapter_base_model_id=model_info.adapter_base_model_id,
        )

        return model_config

    def _extract_few_shot_examples(
        self, dataset: DatasetDict, task: Task, itr_idx: int
    ) -> list[dict[str, t.Any]]:
        """Extract few-shot examples from a dataset.

        This will always extract the examples from the training split.

        We ensure that the few-shot examples are unique by picking them one at a time.

        Args:
            dataset:
                The dataset to extract the few-shot examples from.
            task:
                The task that is being benchmarked.
            itr_idx:
                The index of the dataset in the iterator.

        Returns:
            The few-shot examples.
        """
        random_seed = 4242 + itr_idx
        num_few_shots = self.dataset_config.num_few_shot_examples
        few_shot_examples: list[dict[str, t.Any]] = list()
        shuffled_train = dataset["train"].shuffle(seed=random_seed)

        match task.task_group:
            case (
                TaskGroup.SEQUENCE_CLASSIFICATION
                | TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION
            ):
                labels = it.cycle(self.dataset_config.labels)
                while (
                    len(few_shot_examples) < num_few_shots and len(shuffled_train) > 0
                ):
                    label = next(labels)
                    possible_examples = shuffled_train.filter(
                        lambda x: x["label"].lower() == label.lower()
                    )
                    if len(possible_examples) == 0:
                        continue
                    example = possible_examples.select(range(1))[0]
                    few_shot_examples.append(example)
                    shuffled_train = shuffled_train.filter(
                        lambda x: x["text"] != example["text"]
                    )

            case TaskGroup.TEXT_TO_TEXT:
                while (
                    len(few_shot_examples) < num_few_shots and len(shuffled_train) > 0
                ):
                    example = shuffled_train.select(range(1))[0]
                    few_shot_examples.append(example)
                    shuffled_train = shuffled_train.filter(
                        lambda x: x["text"] != example["text"]
                    )

            case TaskGroup.TOKEN_CLASSIFICATION:
                labels = it.cycle(
                    [
                        label.lower()
                        for label in self.dataset_config.labels
                        if label.lower().startswith("b-")
                    ]
                )
                while (
                    len(few_shot_examples) < num_few_shots and len(shuffled_train) > 0
                ):
                    label = next(labels)
                    possible_examples = shuffled_train.filter(
                        lambda x: label in [tag.lower() for tag in x["labels"]]
                    )
                    if len(possible_examples) == 0:
                        continue
                    example = possible_examples.select(range(1))[0]
                    few_shot_examples.append(example)
                    shuffled_train = shuffled_train.filter(
                        lambda x: x["tokens"] != example["tokens"]
                    )

            case TaskGroup.QUESTION_ANSWERING:
                # Locate the maximum number of tokens that constitutes a short example
                for max_num_tokens in [512, 1024, 2048, 4096, 8192]:
                    train_with_short_examples = dataset["train"].filter(
                        lambda example: len(example["context"]) < max_num_tokens
                    )
                    num_short_examples = len(train_with_short_examples)
                    if num_short_examples >= self.dataset_config.num_few_shot_examples:
                        break
                else:
                    raise InvalidBenchmark(
                        "Could not find enough short examples for few-shot learning."
                    )

                shuffled_train = train_with_short_examples.shuffle(seed=random_seed)
                while (
                    len(few_shot_examples) < num_few_shots and len(shuffled_train) > 0
                ):
                    example = shuffled_train.select(range(1))[0]
                    few_shot_examples.append(example)
                    shuffled_train = shuffled_train.filter(
                        lambda x: x["context"] != example["context"]
                    )

            case _:
                raise NotImplementedError(f"Unsupported task group: {task.task_group}.")

        random.seed(random_seed)
        random.shuffle(few_shot_examples)
        return few_shot_examples

    def _apply_prompt(
        self,
        examples: dict[str, t.Any],
        few_shot_examples: list[dict[str, t.Any]],
        task: Task,
    ) -> dict[str, t.Any]:
        """Apply prompt template to an example, potentially with few-shot examples.

        Args:
            examples:
                The examples to apply the few-shot examples to.
            few_shot_examples:
                The few-shot examples to apply.
            task:
                The task that is being benchmarked.

        Returns:
            The example with the few-shot examples applied.
        """

        def create_prompt(**kwargs) -> tuple[str, str]:
            """Create a prompt from the given keyword arguments.

            Args:
                kwargs:
                    The keyword arguments to use in the prompt.

            Returns:
                A pair (prompt, label), where "label" is an empty string if the model is
                not instruction tuned (as in this case it is included in the prompt).
            """
            label_key = "label" if "label" in kwargs else "target_text"
            label = kwargs.pop(label_key)
            assert (
                label is not None
            ), f"Found a None label for the prompt: {kwargs}. This should not happen."
            label_mapping = self.dataset_config.prompt_label_mapping
            label = label_mapping.get(label, label)
            if self.buffer["instruction_model"]:
                prompt = self.dataset_config.instruction_prompt.format(**kwargs)
                return prompt, label
            else:
                kwargs[label_key] = label
                return self.dataset_config.prompt_template.format(**kwargs), ""

        match task.task_group:
            case (
                TaskGroup.SEQUENCE_CLASSIFICATION
                | TaskGroup.MULTIPLE_CHOICE_CLASSIFICATION
            ):
                few_shot_sections = [
                    create_prompt(
                        text=example["text"].replace("\n", " ").strip(),
                        label=example["label"].replace("\n", " ").strip(),
                    )
                    for example in few_shot_examples
                ]
                new_sections = [
                    create_prompt(text=text.replace("\n", " ").strip(), label="")
                    for text in examples["text"]
                ]

            case TaskGroup.TEXT_TO_TEXT:
                few_shot_sections = [
                    create_prompt(
                        text=example["text"].replace("\n", " ").strip(),
                        target_text=example["target_text"].replace("\n", " ").strip(),
                    )
                    for example in few_shot_examples
                ]
                new_sections = [
                    create_prompt(text=text.replace("\n", " ").strip(), target_text="")
                    for text in examples["text"]
                ]

            case TaskGroup.TOKEN_CLASSIFICATION:

                def create_label(example: dict) -> str:
                    prompt_labels = self.dataset_config.prompt_label_mapping.values()
                    labels: dict[str, list[str]] = {
                        prompt_label: list() for prompt_label in prompt_labels
                    }
                    for token, label in zip(example["tokens"], example["labels"]):
                        label = label.lower()
                        if label == "o":
                            continue
                        prompt_label = self.dataset_config.prompt_label_mapping[label]
                        if label.startswith("b-"):
                            labels[prompt_label].append(token)
                        elif label.startswith("i-"):
                            labels[prompt_label][-1] += " " + token
                    return json.dumps(labels, ensure_ascii=False)

                few_shot_sections = [
                    create_prompt(
                        text=" ".join(example["tokens"]).replace("\n", " ").strip(),
                        label=create_label(example=example),
                    )
                    for example in few_shot_examples
                ]
                new_sections = [
                    create_prompt(
                        text=" ".join(tokens).replace("\n", " ").strip(), label=""
                    )
                    for tokens in examples["tokens"]
                ]

            case TaskGroup.QUESTION_ANSWERING:
                few_shot_sections = [
                    create_prompt(
                        text=example["context"].replace("\n", " ").strip(),
                        question=example["question"].replace("\n", " ").strip(),
                        label=example["answers"]["text"][0].replace("\n", " "),
                    )
                    for example in few_shot_examples
                ]
                new_sections = [
                    create_prompt(
                        text=context.replace("\n", " ").strip(),
                        question=question.replace("\n", " ").strip(),
                        label="",
                    )
                    for context, question in zip(
                        examples["context"], examples["question"]
                    )
                ]

            case _:
                raise NotImplementedError(f"Unsupported task group: {task.task_group}.")

        if self.buffer["instruction_model"]:
            few_shot_messages = [
                dict(role=role, content=content)
                for prompt, label in few_shot_sections
                for role, content in [("user", prompt), ("assistant", label)]
            ]

            messages_list = [
                few_shot_messages + [dict(role="user", content=prompt)]
                for prompt, _ in new_sections
            ]

            # Pick the chat template that matches the language of the dataset, if such a
            # template exists
            chat_template: str | None = None
            if isinstance(self._tokenizer.chat_template, dict):
                language_codes = [
                    language.code for language in self.dataset_config.languages
                ]
                for name, candidate_template in self._tokenizer.chat_template.items():
                    if name.lower() in language_codes:
                        chat_template = candidate_template
                        log_once(
                            f"Using the {name!r} chat template for the tokenizer.",
                            level=logging.DEBUG,
                        )
                        break

            texts = [
                self._tokenizer.apply_chat_template(
                    conversation=messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    chat_template=chat_template,
                )
                for messages in messages_list
            ]

            examples["text"] = texts

        else:
            prompt_prefix = ""
            if self.dataset_config.prompt_prefix:
                prompt_prefix = self.dataset_config.prompt_prefix + "\n\n"

            few_shot_prompt = "\n\n".join([prompt for prompt, _ in few_shot_sections])
            if few_shot_prompt:
                few_shot_prompt += "\n\n"

            examples["text"] = [
                prompt_prefix + few_shot_prompt + new_prompt
                for new_prompt, _ in new_sections
            ]

        return examples

    @property
    def data_collator(self) -> c.Callable[[list[t.Any]], dict[str, t.Any]]:
        """The data collator used to prepare samples during finetuning.

        Returns:
            The data collator.
        """
        raise NotImplementedError(
            "The `data_collator` property has not been implemented for vLLM models."
        )

    @property
    def trainer_class(self) -> t.Type["Trainer"]:
        """The Trainer class to use for finetuning.

        Returns:
            The Trainer class.
        """
        raise NotImplementedError(
            "The `trainer_class` property has not been implemented for vLLM models."
        )


def load_model_and_tokenizer(
    model_config: ModelConfig, benchmark_config: BenchmarkConfig, output_scores: bool
) -> "tuple[LLM, PreTrainedTokenizer]":
    """Load the model and tokenizer.

    Args:
        model_config:
            The model configuration.
        benchmark_config:
            The benchmark configuration.
        output_scores:
            Whether to output scores.

    Returns:
        The loaded model and tokenizer.
    """
    # Prefer base model ID if the model is an adapter - the adapter will be added on
    # during inference in this case
    model_id = model_config.adapter_base_model_id or model_config.model_id

    hf_model_config = load_hf_model_config(
        model_id=model_id,
        num_labels=0,
        id2label=dict(),
        label2id=dict(),
        revision=model_config.revision,
        model_cache_dir=model_config.model_cache_dir,
        api_key=benchmark_config.api_key,
        trust_remote_code=benchmark_config.trust_remote_code,
        run_with_cli=benchmark_config.run_with_cli,
    )

    quantization = None
    if hasattr(hf_model_config, "quantization_config"):
        quantization = hf_model_config.quantization_config.get("quant_method")

    # The quantised models require extra dependencies
    if quantization == "gptq" and (
        importlib.util.find_spec("auto_gptq") is None
        or importlib.util.find_spec("optimum") is None
    ):
        raise NeedsExtraInstalled(extra="quantization")
    if quantization == "awq" and importlib.util.find_spec("awq") is None:
        raise NeedsExtraInstalled(extra="quantization")

    dtype: str | torch.dtype = "auto"
    if quantization is not None and hf_model_config.torch_dtype != torch.float16:
        logger.info(
            "You are loading a quantized model with dtype "
            f"{hf_model_config.torch_dtype}, which vLLM does not support. Setting "
            "dtype to float16 instead."
        )
        dtype = torch.float16

    if model_config.adapter_base_model_id is not None:
        download_dir = str(Path(model_config.model_cache_dir) / "base_model")
    else:
        download_dir = str(model_config.model_cache_dir)

    potential_max_model_length_config_names = [
        "max_position_embeddings",
        "max_sequence_length",
        "model_max_length",
        "sliding_window",
        "sliding_window_size",
        "n_positions",
    ]
    true_max_model_len_candidates: list[int] = list()
    for config_name in potential_max_model_length_config_names:
        if hasattr(hf_model_config, config_name):
            model_len = getattr(hf_model_config, config_name)
            if model_len is not None:
                true_max_model_len_candidates.append(model_len)

    if len(true_max_model_len_candidates) > 0:
        true_max_model_len = min(true_max_model_len_candidates)
    else:
        true_max_model_len = 5_000

    clear_vllm()

    executor_backend = "ray" if torch.cuda.device_count() > 1 else "mp"

    try:
        model = LLM(
            model=model_id,
            tokenizer=model_id,
            gpu_memory_utilization=0.95,
            max_model_len=min(true_max_model_len, 5_000),
            download_dir=download_dir,
            trust_remote_code=benchmark_config.trust_remote_code,
            revision=model_config.revision,
            seed=4242,
            distributed_executor_backend=executor_backend,
            tensor_parallel_size=torch.cuda.device_count(),
            disable_custom_all_reduce=True,
            quantization=quantization,
            dtype=dtype,
            enforce_eager=True,
            max_logprobs=MAX_LOGPROBS if output_scores else None,
            # TEMP: Prefix caching isn't supported with sliding window in vLLM yet,
            # so we disable it for now
            enable_prefix_caching=False,
            enable_lora=model_config.adapter_base_model_id is not None,
            max_lora_rank=256,
        )
    except (ValueError, OSError) as e:
        if "awaiting a review from the repo authors" in str(e):
            raise InvalidModel(
                f"The model {model_id!r} is awaiting a review from the repository "
                "authors. Please try again later."
            )
        elif "trust_remote_code" in str(e):
            raise InvalidModel(
                f"Loading the model {model_id!r} needs to trust remote code. "
                "If you trust the suppliers of this model, then you can enable "
                "this by setting the `--trust-remote-code` flag."
            )
        raise InvalidModel(
            f"The model {model_id!r} could not be loaded. The error was {e!r}."
        )

    model._run_engine = MethodType(_run_engine_with_fixed_progress_bars, model)
    model.config = hf_model_config

    tokenizer = load_tokenizer(
        model_id=model_config.model_id,
        revision=model_config.revision,
        adapter_base_model_id=model_config.adapter_base_model_id,
        trust_remote_code=benchmark_config.trust_remote_code,
        model_max_length=true_max_model_len,
        model_cache_dir=model_config.model_cache_dir,
        token=benchmark_config.api_key or os.getenv("HUGGINGFACE_API_KEY") or True,
    )

    return model, tokenizer


def load_tokenizer(
    model_id: str,
    revision: str,
    adapter_base_model_id: str | None,
    trust_remote_code: bool,
    model_max_length: int,
    model_cache_dir: str,
    token: str | bool,
) -> "PreTrainedTokenizer":
    """Load the tokenizer.

    Args:
        model_id:
            The model identifier.
        revision:
            The revision of the model.
        adapter_base_model_id:
            The base model ID for the adapter model. Can be None if the model is not an
            adapter model.
        trust_remote_code:
            Whether to trust remote code.
        model_max_length:
            The maximum length of the model.
        model_cache_dir:
            The cache directory for the model.
        token:
            The Hugging Face API token.

    Returns:
        The loaded tokenizer.
    """
    config = AutoConfig.from_pretrained(
        adapter_base_model_id or model_id,
        revision=revision,
        cache_dir=model_cache_dir,
        token=token,
        trust_remote_code=trust_remote_code,
    )
    num_retries = 5
    for _ in range(num_retries):
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                use_fast=True,
                verbose=False,
                trust_remote_code=trust_remote_code,
                padding_side="left",
                truncation_side="left",
                model_max_length=model_max_length,
                config=config,
                token=token,
            )
            break
        except (json.JSONDecodeError, OSError, TypeError) as e:
            if adapter_base_model_id is None or model_id == adapter_base_model_id:
                raise InvalidModel(
                    f"Could not load tokenizer for model {model_id!r}. The error was "
                    f"{str(e)}."
                )
            logger.debug(
                f"Could not load tokenizer for {model_id!r}. Falling back to "
                f"{adapter_base_model_id!r}."
            )
            model_id = adapter_base_model_id
        except (TimeoutError, RequestError):
            logger.info(f"Couldn't load tokenizer for {model_id!r}. Retrying.")
            sleep(5)
            continue
    else:
        raise InvalidModel(
            f"Could not load tokenizer for model {model_id!r} after {num_retries} "
            "attempts."
        )

    # Ensure that BOS, EOS and PAD tokens are set
    tokenizer.bos_token, tokenizer.bos_token_id = get_bos_token(tokenizer=tokenizer)
    tokenizer.eos_token, tokenizer.eos_token_id = get_eos_token(tokenizer=tokenizer)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    return tokenizer


def _run_engine_with_fixed_progress_bars(
    self: "LLM", use_tqdm: bool
) -> list["RequestOutput"]:
    if use_tqdm:
        num_requests = self.llm_engine.get_num_unfinished_requests()
        pbar = tqdm(
            total=num_requests, leave=False, disable=hasattr(sys, "_called_from_test")
        )
    else:
        pbar = None

    # Run the engine.
    outputs: list["RequestOutput"] = list()
    while self.llm_engine.has_unfinished_requests():
        step_outputs = self.llm_engine.step()
        for output in step_outputs:
            if output.finished:
                outputs.append(output)
                if pbar is not None:
                    pbar.update(1)

    if pbar is not None:
        pbar.close()

    # Sort the outputs by request ID. This is necessary because some requests may be
    # finished earlier than its previous requests.
    outputs = sorted(outputs, key=lambda x: int(x.request_id))

    return outputs


def clear_vllm() -> None:
    """Clear the GPU memory used by the vLLM model, enabling re-initialisation."""
    try:
        destroy_model_parallel()
    except ImportError:
        pass
    clear_memory()
    if ray.is_initialized():
        ray.shutdown()


def get_end_of_reasoning_token_id(
    model: "LLM", tokenizer: "PreTrainedTokenizer"
) -> int | None:
    """Get the end of reasoning token ID for a generative model.

    This assumes that the reasoning token is of the form <X> and that the end of
    reasoning token is </X> (for X being any string without spaces).

    Args:
        model:
            The vLLM model.
        tokenizer:
            The tokenizer.

    Returns:
        The end of reasoning token ID, or None if it could not be found.
    """
    if tokenizer.chat_template is None:
        prompt = "What is your name?"
    else:
        prompt = tokenizer.apply_chat_template(
            conversation=[dict(role="user", content="What is your name?")],
            add_generation_prompt=True,
            tokenize=False,
        )

    # Generate a completion and remove the BOS token from it, to not confuse it with the
    # potential reasoning token
    completion = (
        model.generate(
            prompts=[prompt],
            sampling_params=SamplingParams(max_tokens=3, temperature=0.0),
            use_tqdm=False,
        )[0]
        .outputs[0]
        .text
    )
    if tokenizer.bos_token is not None:
        completion = completion.replace(tokenizer.bos_token, "").strip()

    # If it doesn't contain a reasoning token, we can't find the end of reasoning token
    match = re.search(pattern=r"<\w+>", string=completion)
    if match is None:
        log_once(
            message=(
                "Could not find a reasoning token, so assuming the model is not a "
                "reasoning model."
            ),
            level=logging.DEBUG,
        )
        return None

    # Check that the found reasoning token and its associated end-of-reasoning tokens
    # are both special tokens
    reasoning_token = match.group()
    end_of_reasoning_token = f"</{reasoning_token[1:-1]}>"
    special_tokens = [
        decoder_token.content
        for decoder_token in tokenizer.added_tokens_decoder.values()
    ]
    special_tokens.extend(
        [encoder_token for encoder_token in tokenizer.added_tokens_encoder.keys()]
    )
    special_tokens.extend(tokenizer.all_special_tokens)
    if (
        reasoning_token not in special_tokens
        or end_of_reasoning_token not in special_tokens
    ):
        log_once(
            message=(
                f"Detected reasoning token {reasoning_token!r} and end of reasoning "
                f"token {end_of_reasoning_token!r}, but one of them is not registered "
                "as a special token, so assuming it is not a real reasoning token."
            ),
            level=logging.DEBUG,
        )
        return None

    log_once(
        message=f"Detected reasoning token {reasoning_token!r}.", level=logging.DEBUG
    )

    # Encode the end of reasoning token and return its ID
    end_of_reasoning_token_id = tokenizer.encode(
        text=end_of_reasoning_token, add_special_tokens=False
    )[0]

    return end_of_reasoning_token_id
