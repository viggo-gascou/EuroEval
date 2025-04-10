"""Templates for the Multiple Choice Reading Comprehension task."""

from dataclasses import asdict

from ..types import TemplateDict
from .base import BasePromptConfig, PromptConfig


def get_multiple_choice_templates() -> TemplateDict:
    """Get the templates for the multiple choice reasoning task."""
    # Using a getter to avoid error with circular imports
    from ..languages import DA, DE, EN, ES, FO, FR, IS, IT, NB, NL, NN, NO, SV

    MULTIPLE_CHOICE_DEFAULTS = BasePromptConfig(
        labels=["a", "b", "c", "d"],
        num_few_shot_examples=5,
        max_generated_tokens=5,
        prompt_label_mapping="auto",
    )

    return {
        DA: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Følgende er tekster med tilhørende multiple choice "
            "spørgsmål og svar.",
            prompt_template="{text}\nSvar: {label}",
            instruction_prompt="{text}\n\nBesvar ovenstående spørgsmål ved at svare "
            "med {labels_str}, og intet andet.",
        ),
        DE: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Die folgenden Texte sind mit dazugehörigen "
            "Multiple-Choice-Fragen und Antworten.",
            prompt_template="{text}\nAntwort: {label}",
            instruction_prompt="{text}\n\nBeantworten Sie die obige Frage mit "
            "{labels_str} , und nichts anderes.",
        ),
        EN: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="The following are texts with accompanying multiple choice "
            "questions and answers.",
            prompt_template="{text}\nAnswer: {label}",
            instruction_prompt="{text}\n\nAnswer the above question by replying with "
            "{labels_str}, and nothing else.",
        ),
        ES: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="",
            prompt_template="",
            instruction_prompt="",
        ),
        FO: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="",
            prompt_template="",
            instruction_prompt="",
        ),
        FR: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Les textes suivants sont accompagnés de questions à choix "
            "multiples et de réponses.",
            prompt_template="{text}\nRéponse: {label}",
            instruction_prompt="{text}\n\nRépondez à la question ci-dessus par "
            "{labels_str}, et rien d'autre.",
        ),
        IS: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Eftirfarandi eru textar með tilheyrandi fjölvalsspurningum "
            "og svörum.",
            prompt_template="{text}\nSvara: {label}",
            instruction_prompt="{text}\n\nSvaraðu eftirfarandi spurningum með "
            "{labels_str}, og engu öðru.",
        ),
        IT: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="",
            prompt_template="",
            instruction_prompt="",
        ),
        NB: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Her følger tekster med tilhørende multiple choice spørsmål "
            "og svar.",
            prompt_template="{text}\nSvar: {label}",
            instruction_prompt="{text}\n\nBesvar følgende spørsmål med {labels_str}, "
            "og ikke noe annet.",
        ),
        NL: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Hieronder staan teksten met bijbehorende multiple choice "
            "vragen en antwoorden.",
            prompt_template="{text}\nAntwoord: {label}",
            instruction_prompt="{text}\n\nBeantwoord de bovenstaande vraag met "
            "{label_str}, en niets anders.",
        ),
        NN: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Her følger tekster med tilhørende multiple choice spørsmål "
            "og svar.",
            prompt_template="{text}\nSvar: {label}",
            instruction_prompt="{text}\n\nBesvar følgende spørsmål med {labels_str}, "
            "og ikke noe annet.",
        ),
        NO: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Her følger tekster med tilhørende multiple choice spørsmål "
            "og svar.",
            prompt_template="{text}\nSvar: {label}",
            instruction_prompt="{text}\n\nBesvar følgende spørsmål med {labels_str}, "
            "og ikke noe annet.",
        ),
        SV: PromptConfig(
            **asdict(MULTIPLE_CHOICE_DEFAULTS),
            prompt_prefix="Nedan följer texter med tillhörande multiple choice frågor "
            "och svar.",
            prompt_template="{text}\nSvar: {label}",
            instruction_prompt="{text}\n\nBesvara följande fråga med {labels_str}, "
            "och inget annat.",
        ),
    }
