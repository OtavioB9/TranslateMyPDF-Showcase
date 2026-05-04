from typing import Optional

import fitz

from utils.logger import get_logger

from .font_manager import FontManager
from .models import PageData

logger = get_logger(__name__)
FONT_SHRINK_STEP = 0.5
MINIMUM_FONT_SIZE = 6.0


class PDFRedactor:
    def __init__(self, font_manager: FontManager):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def apply_page(self, page: fitz.Page, page_data: PageData) -> None:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    @staticmethod
    def _block_should_translate(block_spans: list) -> bool:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _mark_redactions(self, page: fitz.Page, page_data: PageData) -> None:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _reinsert_text(self, page: fitz.Page, temp_page: fitz.Page, page_data: PageData) -> None:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _normalize_text(self, text: str) -> str:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _find_fitting_size(
        self,
        temp_page: fitz.Page,
        bbox: tuple,
        text: str,
        font_name: str,
        color: tuple,
        initial_size: float,
        bottom_limit: float,
        right_limit: float,
    ) -> tuple[tuple, float]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    @staticmethod
    def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _merge_bboxes(self, block_spans: list) -> tuple:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _detect_alignment(self, block_spans: list, block_bbox: tuple) -> int:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    @staticmethod
    def _is_neutral_color(r: float, g: float, b: float) -> bool:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    @staticmethod
    def _detect_background(
        page: fitz.Page, block_bbox: Optional[tuple] = None
    ) -> tuple[float, float, float]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")
