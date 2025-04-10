"""Templates for the Knowledge task."""

from dataclasses import asdict

from ..types import TemplateDict
from .base import BasePromptConfig, PromptConfig


def get_knowledge_templates() -> TemplateDict:
    """Get the templates for knowledge task."""
    # Using a getter to avoid error with circular imports
    from ..languages import DA, DE, EN, ES, FO, FR, IS, IT, NB, NL, NN, NO, SV

    KNOWLEDGE_DEFAULTS = BasePromptConfig(
        labels=["a", "b", "c", "d"],
        num_few_shot_examples=5,
        max_generated_tokens=5,
        prompt_label_mapping="auto",
    )

    return {
        DA: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Følgende er multiple choice spørgsmål (med svar).",
            prompt_template="Spørgsmål: {text}\nSvar: {label}",
            instruction_prompt="Spørgsmål: {text}\n\nBesvar ovenstående spørgsmål ved "
            "at svare med {labels_str}, og intet andet.",
        ),
        DE: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Die folgenden Fragen sind Multiple-Choice-Fragen "
            "(mit Antworten).",
            prompt_template="Frage: {text}\nAntwort: {label}",
            instruction_prompt="Frage: {text}\n\nBeantworten Sie die obige Frage mit "
            "{labels_str}, und nichts anderes.",
        ),
        EN: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="The following are multiple choice questions (with answers).",
            prompt_template="Question: {text}\nAnswer: {label}",
            instruction_prompt="Question: {text}\n\nAnswer the above question by "
            "replying with {labels_str}, and nothing else.",
        ),
        ES: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Las siguientes son preguntas de opción múltiple "
            "(con respuestas).",
            prompt_template="Pregunta: {text}\nRespuesta: {label}",
            instruction_prompt="Pregunta: {text}\n\nResponda la pregunta anterior "
            "usando solo {labels_str}, y nada más.",
        ),
        FO: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="",
            prompt_template="",
            instruction_prompt="",
        ),
        FR: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Les questions suivantes sont des questions à choix "
            "multiples (avec réponses).",
            prompt_template="Question: {text}\nRéponse: {label}",
            instruction_prompt="Question: {text}\n\nRépondez à la question ci-dessus "
            "par {labels_str}, et rien d'autre.",
        ),
        IS: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Eftirfarandi eru fjölvalsspurningar (með svörum).",
            prompt_template="Spurningar: {text}\nSvara: {label}",
            instruction_prompt="Spurningar: {text}\n\nSvaraðu eftirfarandi spurningum "
            "með {labels_str}, og engu öðru.",
        ),
        IT: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Le seguenti sono domande a scelta multipla "
            "(con relative risposte).",
            prompt_template="Domanda: {text}\nRéponse: {label}",
            instruction_prompt="Domanda: {text}\n\nRispondete alla domanda precedente "
            "con {labels_str}, e nient'altro.",
        ),
        NB: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Følgende er flervalgsspørsmål (med svar).",
            prompt_template="Spørsmål: {text}\nSvar: {label}",
            instruction_prompt="Spørsmål: {text}\n\nBesvar følgende spørsmål med "
            "{labels_str}, og ikke noe annet.",
        ),
        NL: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Hieronder staan meerkeuzevragen (met antwoorden).",
            prompt_template="Vraag: {text}\nAntwoord: {label}",
            instruction_prompt="Vraag: {text}\n\nBeantwoord de bovenstaande vraag met "
            "{labels_str}, en niets anders.",
        ),
        NN: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Følgende er flervalgsspørsmål (med svar).",
            prompt_template="Spørsmål: {text}\nSvar: {label}",
            instruction_prompt="Spørsmål: {text}\n\nBesvar følgende spørsmål med "
            "{labels_str}, og ikke noe annet.",
        ),
        NO: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Følgende er flervalgsspørsmål (med svar).",
            prompt_template="Spørsmål: {text}\nSvar: {label}",
            instruction_prompt="Spørsmål: {text}\n\nBesvar følgende spørsmål med "
            "{labels_str}, og ikke noe annet.",
        ),
        SV: PromptConfig(
            **asdict(KNOWLEDGE_DEFAULTS),
            prompt_prefix="Följande är flervalsfrågor (med svar).",
            prompt_template="Fråga: {text}\nSvar: {label}",
            instruction_prompt="Fråga: {text}\n\nBesvara följande fråga med "
            "{labels_str}, och inget annat.",
        ),
    }
