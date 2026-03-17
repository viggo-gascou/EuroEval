"""Language detection module."""

import collections.abc as c
import typing as t

from ..caching_utils import cache_arguments
from ..constants import MIN_LANG_CONFIDENCE_SCORE
from ..languages import (
    DANISH,
    NORWEGIAN,
    NORWEGIAN_BOKMÅL,
    NORWEGIAN_NYNORSK,
    get_correct_language_codes,
)

if t.TYPE_CHECKING:
    from lingua import LanguageDetector as LinguaLanguageDetector

    from ..data_models import DatasetConfig

from lingua import IsoCode639_1, LanguageDetectorBuilder
from lingua import Language as LinguaLanguage


class LanguageDetector:
    """Language detector class."""

    def __init__(self) -> None:
        """Initialize the language detector."""
        self.model: "LinguaLanguageDetector | None" = None

    def download(self) -> None:
        """Download and initialize the language detection model."""
        if self.model is not None:
            return

        self.model = (
            LanguageDetectorBuilder.from_all_spoken_languages()
            .with_preloaded_language_models()
            .build()
        )

    def __call__(
        self, predictions: c.Sequence, dataset_config: "DatasetConfig"
    ) -> list[float]:
        """Classify if the predictions are in the dataset languages.

        Args:
            predictions:
                The predictions to detect the language of.
            dataset_config:
                The dataset configuration.

        Returns:
            List of binary scores (1.0 or 0.0) for each prediction, where 1.0
            indicates the prediction is in the correct language(s) and 0.0 indicates
            it is not.
        """
        # Danish and Norwegian variants are mutually included since they are
        # difficult to distinguish, even for humans, and some sentences can be
        # identical across them.
        danish_and_norwegian = {DANISH, NORWEGIAN_BOKMÅL, NORWEGIAN_NYNORSK}
        dataset_languages = set(dataset_config.languages)

        # extend with danish_and_norwegian if any are present
        if danish_and_norwegian & dataset_languages:
            dataset_languages |= danish_and_norwegian

        # Exclude the source language for translation tasks
        # as it is tuple for translation tasks, otherwise a single language is returned
        main_lang = dataset_config.main_language
        if isinstance(main_lang, tuple):
            source_lang, _ = main_lang
            dataset_languages.discard(source_lang)

        target_language_codes = get_correct_language_codes(
            language_codes=[lang.code for lang in dataset_languages]
        )

        # Skipping "no" norwegian as lingua does not have a code for it
        detector_languages = [
            LinguaLanguage.from_iso_code_639_1(IsoCode639_1.from_str(lang))
            for lang in target_language_codes
            if lang != NORWEGIAN.code
        ]

        return self._detect_language(
            predictions=tuple(predictions),
            detector_languages=detector_languages,
            target_language_codes=tuple(target_language_codes),
        )

    @cache_arguments("predictions", "target_language_codes")
    def _detect_language(
        self,
        predictions: tuple[str],
        detector_languages: list[LinguaLanguage],
        target_language_codes: tuple[str],
    ) -> list[float]:
        """Internal method that performs language detection with caching.

        Args:
            predictions:
                The predictions to detect the language of.
            detector_languages:
                The detector languages to use for filtering.
            target_language_codes:
                The target language codes (used for cache key).

        Returns:
            List of binary scores (1.0 or 0.0) for each prediction, where 1.0
            indicates the prediction is in the correct language(s) and 0.0 indicates
            it is not. Score is 1.0 if the sum of confidence values for target
            languages exceeds MIN_LANG_CONFIDENCE_SCORE
        """
        if self.model is None:
            self.download()

        assert self.model is not None, (
            "Model is not initialized, please call download() first"
        )

        conf_values = self.model.compute_language_confidence_values_in_parallel(
            list(predictions)
        )
        scores = []
        for confidence in conf_values:
            # sum the confidence values so we get a single value for datasets
            # with 'multiple' languages, like Danish and Norwegian
            lang_confidence = sum(
                conf.value for conf in confidence if conf.language in detector_languages
            )
            scores.append(1.0 if lang_confidence > MIN_LANG_CONFIDENCE_SCORE else 0.0)
        return scores


language_detector = LanguageDetector()
