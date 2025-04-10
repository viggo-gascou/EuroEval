"""The different prompt templates used in EuroEval."""

import typing as t

from .base import PromptConfig
from .common_sense import get_common_sense_templates
from .knowledge import get_knowledge_templates
from .linguistic_acceptability import get_linguistic_acceptability_templates
from .multiple_choice import get_multiple_choice_templates
from .named_entity import get_ner_templates
from .reading_comprehension import get_reading_comprehension_templates
from .sentiment import get_sentiment_templates
from .summarization import get_summarization_templates

if t.TYPE_CHECKING:
    from ..data_models import Language, Task
    from ..tasks import COMMON_SENSE, KNOW, LA, MCRC, NER, RC, SENT, SUMM


def get_prompt_templates(task: "Task", language: "Language") -> PromptConfig:
    """Get template for a given task and language."""
    from ..tasks import COMMON_SENSE, KNOW, LA, MCRC, NER, RC, SENT, SUMM

    templates_dict = {
        COMMON_SENSE: get_common_sense_templates(),
        KNOW: get_knowledge_templates(),
        LA: get_linguistic_acceptability_templates(),
        MCRC: get_multiple_choice_templates(),
        NER: get_ner_templates(),
        RC: get_reading_comprehension_templates(),
        SENT: get_sentiment_templates(),
        SUMM: get_summarization_templates(),
    }

    return templates_dict[task][language]


__all__ = ["PromptConfig", "get_prompt_templates"]
