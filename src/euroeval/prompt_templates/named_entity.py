"""Templates for the Named Entity Recognition task."""

from dataclasses import asdict

from ..types import TemplateDict
from .base import BasePromptConfig, PromptConfig


def get_ner_templates() -> TemplateDict:
    """Get the templates for the named entity recognition task."""
    # Using a getter to avoid error with circular imports
    from ..data_models import Language
    from ..languages import DA, DE, EN, ES, FO, FR, IS, IT, NB, NL, NN, NO, SV

    NER_DEFAULTS = BasePromptConfig(
        labels=[
            "o",
            "b-loc",
            "i-loc",
            "b-org",
            "i-org",
            "b-per",
            "i-per",
            "b-misc",
            "i-misc",
        ],
        num_few_shot_examples=8,
        max_generated_tokens=128,
    )
    NER_DEFAULTS_DICT = asdict(NER_DEFAULTS)
    NER_DEFAULTS_DICT.pop("prompt_label_mapping")

    NER_TAG_MAPPING = {
        "per": {
            DA: "person",
            DE: "person",
            EN: "person",
            ES: "persona",
            FO: "persónur",
            FR: "personne",
            IS: "einstaklingur",
            IT: "persona",
            NB: "person",
            NL: "persoon",
            NN: "person",
            NO: "person",
            SV: "person",
        },
        "loc": {
            DA: "sted",
            DE: "ort",
            EN: "location",
            ES: "lugar",
            FO: "staður",
            FR: "lieu",
            IS: "staðsetning",
            IT: "posizione",
            NB: "sted",
            NL: "locatie",
            NN: "sted",
            NO: "sted",
            SV: "plats",
        },
        "org": {
            DA: "organisation",
            DE: "organisation",
            EN: "organization",
            ES: "organización",
            FO: "felagsskapur",
            FR: "organisation",
            IS: "stofnun",
            IT: "organizzazione",
            NB: "organisasjon",
            NL: "organisatie",
            NN: "organisasjon",
            NO: "organisasjon",
            SV: "organisation",
        },
        "misc": {
            DA: "diverse",
            DE: "verschiedenes",
            EN: "miscellaneous",
            ES: "misceláneo",
            FO: "ymiskt",
            FR: "divers",
            IS: "ýmislegt",
            IT: "varie",
            NB: "diverse",
            NL: "diversen",
            NN: "diverse",
            NO: "diverse",
            SV: "diverse",
        },
    }

    def get_ner_mapping(language: Language) -> dict[str, str]:
        """Get the translations for all NER tags in the specified language.

        Args:
            language: The language for the target language.

        Returns:
            The translated tags for the specified language.
        """
        try:
            # Add 'b-' or 'i-' prefix to get the actual tag
            return {
                f"{prefix}{tag}": language_to_local_label[language]
                for tag, language_to_local_label in NER_TAG_MAPPING.items()
                for prefix in ["b-", "i-"]
            }
        except KeyError:
            raise KeyError(f"No NER tag mapping found for language '{language}'.")

    return {
        DA: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(DA),
            prompt_prefix="Følgende er sætninger og JSON-ordbøger med de navngivne "
            "enheder, som forekommer i den givne sætning.",
            prompt_template="Sætning: {text}\nNavngivne enheder: {label}",
            instruction_prompt="Sætning: {text}\n\nIdentificér de navngivne enheder i "
            "sætningen. Du skal outputte dette som en JSON-ordbog med nøglerne "
            "{labels_str}. Værdierne skal være lister over de navngivne enheder af den "
            "type, præcis som de forekommer i sætningen.",
        ),
        DE: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(DE),
            prompt_prefix="Es folgen Sätze und JSON-Wörterbücher mit den benannten "
            "Entitäten, die in der angegebenen Phrase vorkommen.",
            prompt_template="Satz: {text}\nBenannte Entitäten: {label}",
            instruction_prompt="Satz: {text}\n\nIdentifizieren Sie die benannten "
            "Entitäten im Satz. Sie sollten dies als JSON-Wörterbuch mit den "
            "Schlüsseln {labels_str} ausgeben. Die Werte sollten Listen der "
            "benannten Entitäten dieses Typs sein, genau wie sie im Satz erscheinen.",
        ),
        EN: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(EN),
            prompt_prefix="Below are sentences and JSON dictionaries with the named "
            "entities that occur in the given sentence.",
            prompt_template="Sentence: {text}\nNamed entities: {label}",
            instruction_prompt="Sentence: {text}\n\nIdentify the named entities in the "
            "sentence. You should output this as a JSON dictionary with the keys being "
            "{labels_str}. The values should be lists of the named entities of that "
            "type, exactly as they appear in the sentence.",
        ),
        ES: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(ES),
            prompt_prefix="Lo siguiente son oraciones y diccionarios JSON con las "
            "entidades nombradas que aparecen en la oración dada.",
            prompt_template="Oración: {text}\nEntidades nombradas: {label}",
            instruction_prompt="Oración: {text}\n\nIdentifica las entidades nombradas "
            "en la oración. Debes producir esto como un diccionario JSON con las "
            "claves {labels_str}. Los valores deben ser listas de las "
            "entidades nombradas de ese tipo, exactamente como aparecen en la oración.",
        ),
        FO: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(FO),
            prompt_prefix="Her eru nakrir setningar og nakrar JSON orðabøkur við "
            "nevndar eindir, sum eru í setningunum.",
            prompt_template="Setningur: {text}\nNevndar eindir: {label}",
            instruction_prompt="Setningur: {text}\n\nGreinið nevndu einingarnar í "
            "setningunni. Þú ættir að skila þessu sem JSON orðabók með lyklunum "
            "{labels_str}. Gildin ættu að vera listi yfir nevndu einingarnar af "
            "þeirri gerð, nákvæmlega eins og þær koma fram í setningunni.",
        ),
        FR: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(FR),
            prompt_prefix="Vous trouverez ci-dessous des phrases et des "
            "dictionnaires JSON avec les entités nommées qui apparaissent dans la "
            "phrase donnée.",
            prompt_template="Sentence: {text}\nEntités nommées: {label}",
            instruction_prompt="Sentence: {text}\n\nIdentifiez les entités nommées "
            "dans la phrase. Vous devez produire ceci sous forme de dictionnaire JSON "
            "avec les clés {labels_str}. Les valeurs doivent être des listes des "
            "entités nommées de ce type, exactement comme elles apparaissent dans "
            "la phrase.",
        ),
        IS: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(IS),
            prompt_prefix="Eftirfarandi eru setningar ásamt JSON lyklum með nefndum "
            "einingum sem koma fyrir í setningunum.",
            prompt_template="Setning: {text}\nNefndar einingar: {label}",
            instruction_prompt="Setning: {text}\n\nGreinið nefndu einingarnar í "
            "setningunni. Þú ættir að skila þessu sem JSON orðabók með lyklunum "
            "{labels_str}. Gildin ættu að vera listi yfir nefndu "
            "einingarnar af þeirri gerð, nákvæmlega eins og þær koma fram í "
            "setningunni.",
        ),
        IT: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(IT),
            prompt_prefix="Di seguito sono riportate le frasi e i dizionari JSON "
            "con le entità denominate presenti nella frase data.",
            prompt_template="Frase: {text}\nEntità denominate: {label}",
            instruction_prompt="Frase: {text}\n\nIdentificare le entità nominate nella "
            "frase. Il risultato dovrebbe essere un dizionario JSON con le chiavi "
            "{labels_str}. I valori devono essere elenchi di entità "
            "nominate di quel tipo, esattamente come appaiono nella frase.",
        ),
        NB: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(NB),
            prompt_prefix="Følgende er fraser og JSON-ordbøker med de navngitte "
            "enhetene som forekommer i den gitte frasen.",
            prompt_template="Frase: {text}\nNavngitte enheter: {label}",
            instruction_prompt="Frase: {text}\n\nIdentifiser de navngitte enhetene i "
            "frasen. Du bør outputte dette som en JSON-ordbok med nøklene {labels_str}."
            "Verdiene skal være lister over de navngitte enhetene "
            "av den typen, akkurat som de vises i frasen.",
        ),
        NL: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(NL),
            prompt_prefix="Hieronder staan zinnen en JSON woordenboeken met de "
            "genoemde entiteiten die voorkomen in de gegeven zin.",
            prompt_template="Zin: {text}\nGenoemde entiteiten: {label}",
            instruction_prompt="Zin: {text}\n\nIdentificeer de genoemde entiteiten "
            "in de zin. Je moet dit uitvoeren als een JSON-woordenboek met de sleutels "
            "{labels_str}. De waarden moeten lijsten zijn van de "
            "genoemde entiteiten van dat type, precies zoals ze voorkomen in de zin.",
        ),
        NN: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(NN),
            prompt_prefix="Følgende er fraser og JSON-ordbøker med de navngitte "
            "enhetene som forekommer i den gitte frasen.",
            prompt_template="Frase: {text}\nNavngitte enheter: {label}",
            instruction_prompt="Frase: {text}\n\nIdentifiser de navngitte enhetene i "
            "frasen. Du bør outputte dette som en JSON-ordbok med nøklene {labels_str}."
            "Verdiene skal være lister over de navngitte enhetene "
            "av den typen, akkurat som de vises i frasen.",
        ),
        NO: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(NO),
            prompt_prefix="Følgende er fraser og JSON-ordbøker med de navngitte "
            "enhetene som forekommer i den gitte frasen.",
            prompt_template="Frase: {text}\nNavngitte enheter: {label}",
            instruction_prompt="Frase: {text}\n\nIdentifiser de navngitte enhetene i "
            "frasen. Du bør outputte dette som en JSON-ordbok med nøklene {labels_str}."
            "Verdiene skal være lister over de navngitte enhetene "
            "av den typen, akkurat som de vises i frasen.",
        ),
        SV: PromptConfig(
            **NER_DEFAULTS_DICT,
            prompt_label_mapping=get_ner_mapping(SV),
            prompt_prefix="Följande är meningar och JSON-ordböcker med de namngivna "
            "enheter som förekommer i den givna meningen.",
            prompt_template="Mening: {text}\nNamngivna entiteter: {label}",
            instruction_prompt="Mening: {text}\n\nIdentifiera de namngivna enheterna i "
            "meningen. Du ska outputta detta som en JSON-ordbok med nycklarna "
            "{labels_str}. Värdena ska vara listor över de namngivna enheter av den "
            "typen, precis som de förekommer i meningen.",
        ),
    }
