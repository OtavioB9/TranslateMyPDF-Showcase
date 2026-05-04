import fitz

from utils.logger import get_logger

from .models import PageData

logger = get_logger(__name__)


class TableDetector:
    def detect_tables(self, page: fitz.Page, page_data: PageData):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _tag_spans_in_cell(self, page_data: PageData, cell_rect: fitz.Rect, uid: int):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")
