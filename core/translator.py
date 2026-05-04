from abc import ABC, abstractmethod
from typing import List, Optional

from database.db import TranslationDatabase  # noqa: F401
from utils.logger import get_logger

logger = get_logger(__name__)
BATCH_SIZE = 80
MAX_CHARS_PER_BATCH = 4000


class TranslationProvider(ABC):
    @abstractmethod
    def translate_batch(self, texts: List[str]) -> List[str]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    @abstractmethod
    def is_quota_exceeded(self, exception: Exception) -> bool:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")


class GoogleProvider(TranslationProvider):
    def __init__(self, source="en", target="pt"):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def translate_batch(self, texts: List[str]) -> List[str]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def is_quota_exceeded(self, e: Exception) -> bool:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")


class DeepLProvider(TranslationProvider):
    def __init__(self, auth_key: str, source="en", target="pt"):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def translate_batch(self, texts: List[str]) -> List[str]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def is_quota_exceeded(self, e: Exception) -> bool:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")


class BatchTranslator:
    def __init__(
        self, source: str = "en", target: str = "pt", primary: Optional[TranslationProvider] = None
    ):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def translate_spans(self, spans: list) -> list:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _build_translation_map(self, texts: list[str]) -> dict[str, str]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _create_batches(self, texts: list[str]) -> list[list[str]]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _translate_batch_with_fallback(self, batch: list[str]) -> list[str]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")
