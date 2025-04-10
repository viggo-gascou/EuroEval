"""Templates for the Summarization task."""

from dataclasses import asdict

from ..types import TemplateDict
from .base import BasePromptConfig, PromptConfig


def get_summarization_templates() -> TemplateDict:
    """Get the templates for the summarization task."""
    # Using a getter to avoid error with circular imports
    from ..languages import DA, DE, EN, ES, FO, FR, IS, IT, NB, NL, NN, NO, SV

    SUMMARIZATION_DEFAULTS = BasePromptConfig(
        num_few_shot_examples=1, max_generated_tokens=256
    )

    return {
        DA: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Følgende er dokumenter med tilhørende resuméer.",
            prompt_template="Dokument: {text}\nResumé: {target_text}",
            instruction_prompt="Dokument: {text}\n\nSkriv et resumé af ovenstående "
            "dokument.",
        ),
        DE: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Nachstehend finden Sie Dokumente mit zugehörigen "
            "Zusammenfassungen.",
            prompt_template="Dokument: {text}\nZusammenfassung: {target_text}",
            instruction_prompt="Nachrichtenartikel: {text}\n\nSchreiben Sie eine "
            "Zusammenfassung des oben genannten Dokuments.",
        ),
        EN: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="The following are documents with accompanying summaries.",
            prompt_template="Document: {text}\nSummary: {target_text}",
            instruction_prompt="Document: {text}\n\nWrite a summary of the above "
            "document.",
        ),
        ES: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="A continuación se presentan documentos con resúmenes "
            "adjuntos.",
            prompt_template="Documento: {text}\nResumen: {target_text}",
            instruction_prompt="Documento: {text}\n\nEscriba un resumen del "
            "documento anterior.",
        ),
        FO: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="",
            prompt_template="",
            instruction_prompt="",
        ),
        FR: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Les documents suivants sont accompagnés d'un résumé.",
            prompt_template="Document: {text}\nRésumé: {target_text}",
            instruction_prompt="Document: {text}\n\nRédigez un résumé du "
            "document ci-dessus.",
        ),
        IS: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Eftirfarandi eru skjöl með meðfylgjandi samantektum.",
            prompt_template="Skjal: {text}\nSamantekt: {target_text}",
            instruction_prompt="Skjal: {text}\n\nSkrifaðu samantekt á ofangreindu "
            "skjali.",
        ),
        IT: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Di seguito sono riportati i documenti con le relative "
            "sintesi.",
            prompt_template="Documento: {text}\nSintesi: {target_text}",
            instruction_prompt="Documento: {text}\n\nScrivete una sintesi del "
            "documento di cui sopra.",
        ),
        NB: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Nedenfor følger dokumenter med tilhørende sammendrag.",
            prompt_template="Dokument: {text}\nSammendrag: {target_text}",
            instruction_prompt="Dokument: {text}\n\nSkriv et sammendrag av "
            "dokumentet ovenfor.",
        ),
        NL: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Hieronder volgen documenten met bijbehorende "
            "samenvattingen.",
            prompt_template="Document: {text}\nSamenvatting: {target_text}",
            instruction_prompt="Document: {text}\n\nSchrijf een samenvatting van het "
            "bovenstaande document.",
        ),
        NN: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Nedenfor følger dokumenter med tilhørende sammendrag.",
            prompt_template="Dokument: {text}\nSammendrag: {target_text}",
            instruction_prompt="Dokument: {text}\n\nSkriv et sammendrag av "
            "dokumentet ovenfor.",
        ),
        NO: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Nedenfor følger dokumenter med tilhørende sammendrag.",
            prompt_template="Dokument: {text}\nSammendrag: {target_text}",
            instruction_prompt="Dokument: {text}\n\nSkriv et sammendrag av "
            "dokumentet ovenfor.",
        ),
        SV: PromptConfig(
            **asdict(SUMMARIZATION_DEFAULTS),
            prompt_prefix="Nedan följer dokument med tillhörande sammanfattningar.",
            prompt_template="Dokument: {text}\nSammanfattning: {target_text}",
            instruction_prompt="Dokument: {text}\n\nSkriv en sammanfattning av "
            "ovanstående dokument.",
        ),
    }
