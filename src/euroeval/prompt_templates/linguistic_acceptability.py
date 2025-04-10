"""Templates for the Linguistic Acceptability task."""

from dataclasses import asdict

from ..types import TemplateDict
from .base import BasePromptConfig, PromptConfig


def get_linguistic_acceptability_templates() -> TemplateDict:
    """Get the templates for the linguistic acceptability task."""
    # Using a getter to avoid error with circular imports
    from ..data_models import Language
    from ..languages import DA, DE, EN, ES, FO, FR, IS, IT, NB, NL, NN, NO, SV

    LA_DEFAULTS = BasePromptConfig(
        labels=["incorrect", "correct"],
        num_few_shot_examples=12,
        max_generated_tokens=5,
    )
    LA_DEFAULTS_DICT = asdict(LA_DEFAULTS)
    LA_DEFAULTS_DICT.pop("prompt_label_mapping")

    LA_LABEL_MAPPING = {
        "correct": {
            DA: "ja",
            DE: "ja",
            EN: "yes",
            ES: "sí",
            FO: "ja",
            FR: "oui",
            IS: "já",
            IT: "si",
            NB: "ja",
            NL: "ja",
            NN: "ja",
            NO: "ja",
            SV: "ja",
        },
        "incorrect": {
            DA: "nej",
            DE: "nein",
            EN: "no",
            ES: "no",
            FO: "nei",
            FR: "non",
            IS: "nei",
            IT: "no",
            NB: "nei",
            NL: "nee",
            NN: "nei",
            NO: "nei",
            SV: "nej",
        },
    }

    def get_label_mapping(language: Language) -> dict[str, str]:
        """Get the translations for all labels in the specified language.

        Args:
            language: The language code for the target language.

        Returns:
            The translated labels for the specified language.
        """
        try:
            return {
                label: language_to_local_label[language]
                for label, language_to_local_label in LA_LABEL_MAPPING.items()
            }
        except KeyError:
            raise KeyError(f"No LA label mapping found for language '{language}'.")

    return {
        DA: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(DA),
            prompt_prefix="Følgende er sætninger og om de er grammatisk korrekte.",
            prompt_template="Sætning: {text}\nGrammatisk korrekt: {label}",
            instruction_prompt="Sætning: {text}\n\nBestem om sætningen er grammatisk "
            "korrekt eller ej. Svar med 'ja', hvis sætningen er korrekt, og 'nej', "
            "hvis den ikke er, og intet andet.",
        ),
        DE: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(DE),
            prompt_prefix="Die folgenden Sätze und ob sie grammatikalisch korrekt "
            "sind.",
            prompt_template="Satz: {text}\nGrammatikalisch richtig: {label}",
            instruction_prompt="Satz: {text}\n\nBestimmen Sie, ob der Satz "
            "grammatikalisch korrekt ist oder nicht. Antworten Sie mit 'ja', wenn der "
            "Satz korrekt ist und 'nein', wenn er es nicht ist, und nichts anderes.",
        ),
        EN: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(EN),
            prompt_prefix="The following are sentences and whether they are "
            "grammatically correct.",
            prompt_template="Sentence: {text}\nGrammatically correct: {label}",
            instruction_prompt="Sentence: {text}\n\nDetermine whether the sentence is "
            "grammatically correct or not. Reply with 'yes' if the sentence is "
            "correct and 'no' if it is not, and nothing else.",
        ),
        ES: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(ES),
            prompt_prefix="Lo siguiente son textos y si son gramaticalmente correctos.",
            prompt_template="Texto: {text}\nGramaticalmente correcto: {label}",
            instruction_prompt="Texto: {text}\n\nDetermina si el texto es "
            "gramaticalmente correcto o no. Responde con 'sí' si el texto es "
            "correcto, y 'no' si no lo es.",
        ),
        FO: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(FO),
            prompt_prefix="Hetta eru nakrir setningar og um teir eru mállæruliga "
            "rættir.",
            prompt_template="Setningur: {text}\nMállæruliga rættur: {label}",
            instruction_prompt="Setningur: {text}\n\nGreinið hvort setningurin er "
            "mállæruliga rættur ella ikki. Svarið skal vera 'ja' um setningurin er "
            "rættur og 'nei' um hann ikki er, og einki annað.",
        ),
        FR: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(FR),
            prompt_prefix="Les phrases suivantes indiquent si elles sont "
            "grammaticalement correctes.",
            prompt_template="Phrase : {text}\nCorrect du point de vue "
            "grammatical: {label}",
            instruction_prompt="Phrase: {text}\n\nDéterminez si la phrase est "
            "grammaticalement correcte ou non. Répondez par 'oui' si la phrase est "
            "correcte et par 'non' si elle ne l'est pas, et rien d'autre.",
        ),
        IS: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(IS),
            prompt_prefix="Eftirfarandi eru setningar og hvort þær eru málfræðilega "
            "réttar.",
            prompt_template="Setning: {text}\nMálfræðilega rétt: {label}",
            instruction_prompt="Setning: {text}\n\nGreinið hvort setningin er "
            "málfræðilega rétt eða ekki. Svarið skal vera 'já' ef setningin er rétt "
            "og 'nei' ef hún er ekki, og engu öðru.",
        ),
        IT: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(IT),
            prompt_prefix="Di seguito sono riportate le frasi e la loro correttezza "
            "grammaticale.",
            prompt_template="Frase : {text}\nGrammaticalmente corretto : {label}",
            instruction_prompt="Frase: {text}\n\nStabilite se la frase è "
            "grammaticalmente corretta o meno. Rispondete con 'si' se la frase è "
            "corretta e con 'no' se non lo è, e nient'altro.",
        ),
        NB: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(NB),
            prompt_prefix="Følgende er setninger og hvorvidt de er grammatisk "
            "korrekte.",
            prompt_template="Setning: {text}\nGrammatisk korrekt: {label}",
            instruction_prompt="Setning: {text}\n\nBestem om setningen er grammatisk "
            "korrekt eller ikke. Svar med 'ja' hvis setningen er korrekt og 'nei' "
            "hvis den ikke er, og ikke noe annet.",
        ),
        NL: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(NL),
            prompt_prefix="Hieronder staan zinnen en of ze grammaticaal correct zijn.",
            prompt_template="Zin: {text}\nGrammaticaal correct: {label}",
            instruction_prompt="Zin: {text}\n\nBepaal of de zin grammaticaal correct "
            "is of niet. Antwoord met 'ja' als de zin correct is en 'nee' als dat "
            "niet het geval is, en niets anders.",
        ),
        NN: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(NN),
            prompt_prefix="Følgende er setninger og hvorvidt de er grammatisk "
            "korrekte.",
            prompt_template="Setning: {text}\nGrammatisk korrekt: {label}",
            instruction_prompt="Setning: {text}\n\nBestem om setningen er grammatisk "
            "korrekt eller ikke. Svar med 'ja' hvis setningen er korrekt og 'nei' "
            "hvis den ikke er, og ikke noe annet.",
        ),
        NO: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(NO),
            prompt_prefix="Følgende er setninger og hvorvidt de er grammatisk "
            "korrekte.",
            prompt_template="Setning: {text}\nGrammatisk korrekt: {label}",
            instruction_prompt="Setning: {text}\n\nBestem om setningen er grammatisk "
            "korrekt eller ikke. Svar med 'ja' hvis setningen er korrekt og 'nei' "
            "hvis den ikke er, og ikke noe annet.",
        ),
        SV: PromptConfig(
            **LA_DEFAULTS_DICT,
            prompt_label_mapping=get_label_mapping(SV),
            prompt_prefix="Följande är meningar och huruvida de är grammatiskt "
            "korrekta.",
            prompt_template="Mening: {text}\nGrammatisk korrekt: {label}",
            instruction_prompt="Mening: {text}\n\nBestäm om meningen är grammatiskt "
            "korrekt eller inte. Svara med 'ja' om meningen är korrekt och 'nej' "
            "om den inte är, och inget annat.",
        ),
    }
