"""Templates for the Sentiment Analysis task."""

from dataclasses import asdict

from ..types import TemplateDict
from .base import BasePromptConfig, PromptConfig


def get_sentiment_templates() -> TemplateDict:
    """Get the templates for the sentiment analysis task.

    Returns:
        The templates for the sentiment analysis task.
    """
    # Using a getter to avoid error with circular imports
    from ..data_models import Language
    from ..languages import DA, DE, EN, ES, FO, FR, IS, IT, NB, NL, NN, NO, SV

    SENTIMENT_DEFAULTS = BasePromptConfig(
        labels=["positive", "neutral", "negative"],
        num_few_shot_examples=12,
        max_generated_tokens=5,
    )
    SENT_DEFAULTS_DICT = asdict(SENTIMENT_DEFAULTS)
    SENT_DEFAULTS_DICT.pop("prompt_label_mapping")

    SENT_LABEL_MAPPING = {
        "positive": {
            DA: "positiv",
            DE: "positiv",
            EN: "positive",
            ES: "positivo",
            FO: "positivt",
            FR: "positif",
            IS: "jákvætt",
            IT: "positivo",
            NB: "positiv",
            NL: "positief",
            NN: "positiv",
            NO: "positiv",
            SV: "positiv",
        },
        "neutral": {
            DA: "neutral",
            DE: "neutral",
            EN: "neutral",
            ES: "neutral",
            FO: "neutralt",
            FR: "neutre",
            IS: "hlutlaust",
            IT: "neutro",
            NB: "nøytral",
            NL: "neutraal",
            NN: "nøytral",
            NO: "nøytral",
            SV: "neutral",
        },
        "negative": {
            DA: "negativ",
            DE: "negativ",
            EN: "negative",
            ES: "negativo",
            FO: "negativt",
            FR: "négatif",
            IS: "neikvætt",
            IT: "negativo",
            NB: "negativ",
            NL: "negatief",
            NN: "negativ",
            NO: "negativ",
            SV: "negativ",
        },
    }

    def get_label_mapping(language: Language) -> dict[str, str]:
        """Get the translations for all labels in the specified language.

        Args:
            language: The language for the target language.

        Returns:
            The translated labels for the specified language.
        """
        try:
            return {
                label: language_to_local_label[language]
                for label, language_to_local_label in SENT_LABEL_MAPPING.items()
            }
        except KeyError:
            raise KeyError(f"No SENT label mapping found for language '{language}'.")

    return {
        DA: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(DA),
            prompt_prefix="Følgende er dokumenter og deres sentiment, som kan være "
            "{labels_str}.",
            prompt_template="Dokument: {text}\nSentiment: {label}",
            instruction_prompt="Dokument: {text}\n\nKlassificer sentimentet i "
            "dokumentet. Svar kun med {labels_str}, og intet andet.",
        ),
        DE: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(DE),
            prompt_prefix="Nachfolgend finden Sie Dokumente und ihre Bewertung, die "
            "{labels_str} sein kann.",
            prompt_template="Dokument: {text}\nStimmung: {label}",
            instruction_prompt="Dokument: {text}\n\nKlassifizieren Sie die Stimmung im "
            "Dokument. Antworten Sie mit {labels_str}, und nichts anderes.",
        ),
        EN: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(EN),
            prompt_prefix="The following are documents and their sentiment, which can "
            "be {labels_str}.",
            prompt_template="Document: {text}\nSentiment: {label}",
            instruction_prompt="Document: {text}\n\nClassify the sentiment in the "
            "document. Answer with {labels_str}, and nothing else.",
        ),
        ES: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(ES),
            prompt_prefix="A continuación se muestran los documentos y su "
            "sentimiento, que puede ser {labels_str}.",
            prompt_template="Documento: {text}\nSentimiento: {label}",
            instruction_prompt="Documento: {text}\n\nClasifica el sentimiento del "
            "documento. Responde con {labels_str}, y nada más.",
        ),
        FO: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(FO),
            prompt_prefix="Niðanfyri eru skjøl og teirra kenslur, sum kunnu vera "
            "{labels_str}.",
            prompt_template="Skjal: {text}\nKensla: {label}",
            instruction_prompt="Skjal: {text}\n\nFlokka kensluna í skjalinum. Svara "
            "við {labels_str}, og einki annað.",
        ),
        FR: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(FR),
            prompt_prefix="Les documents suivants sont accompagnés de leur sentiment, "
            "qui peut être {labels_str}.",
            prompt_template="Document: {text}\nSentiment: {label}",
            instruction_prompt="Document: {text}\n\nClassez le sentiment dans le "
            "document. Répondez par {labels_str}, et rien d'autre.",
        ),
        IS: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(IS),
            prompt_prefix="Eftirfarandi eru skjöl og viðhorf þeirra, sem geta verið "
            "{labels_str}.",
            prompt_template="Skjal: {text}\nViðhorf: {label}",
            instruction_prompt="Skjal: {text}\n\nFlokkaðu viðhorfið í skjalinu. "
            "Svaraðu með {labels_str}, og ekkert annað.",
        ),
        IT: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(IT),
            prompt_prefix="Di seguito sono riportati i documenti e il loro sentiment, "
            "che può essere {labels_str}.",
            prompt_template="Documento: {text}\nSentimento: {label}",
            instruction_prompt="Documento: {text}\n\nClassificare il sentiment del "
            "documento. Rispondere con {labels_str}, e nient'altro.",
        ),
        NB: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(NB),
            prompt_prefix="Her følger dokumenter og deres sentiment, som kan være "
            "{labels_str}",
            prompt_template="Dokument: {text}\nSentiment: {label}",
            instruction_prompt="Dokument: {text}\n\nKlassifiser følelsen i teksten. "
            "Svar med {labels_str}, og ikke noe annet.",
        ),
        NL: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(NL),
            prompt_prefix="Hieronder volgen documenten en hun sentiment, dat "
            "{labels_str} kan zijn.",
            prompt_template="Document: {text}\nSentiment: {label}",
            instruction_prompt="Document: {text}\n\nClassificeer het sentiment in het "
            "document. Antwoord met {labels_str}, en verder niets.",
        ),
        NN: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(NN),
            prompt_prefix="Her følger dokumenter og deres sentiment, som kan være "
            "{labels_str}",
            prompt_template="Dokument: {text}\nSentiment: {label}",
            instruction_prompt="Dokument: {text}\n\nKlassifiser følelsen i teksten. "
            "Svar med {labels_str}, og ikke noe annet.",
        ),
        NO: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(NO),
            prompt_prefix="Her følger dokumenter og deres sentiment, som kan være "
            "{labels_str}",
            prompt_template="Dokument: {text}\nSentiment: {label}",
            instruction_prompt="Dokument: {text}\n\nKlassifiser følelsen i teksten. "
            "Svar med {labels_str}, og ikke noe annet.",
        ),
        SV: PromptConfig(
            **SENT_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(SV),
            prompt_prefix="Nedan följer dokument och deras sentiment, som kan vara "
            "{labels_str}.",
            prompt_template="Dokument: {text}\nSentiment: {label}",
            instruction_prompt="Dokument: {text}\n\nKlassificera känslan i dokumentet. "
            "Svara med {labels_str}, och inget annat.",
        ),
    }
