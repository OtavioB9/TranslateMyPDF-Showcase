import fitz

from utils.logger import get_logger

from .models import PageData

logger = get_logger(__name__)


class OCRExtractor:
    def __init__(self, tesseract_cmd: str = "tesseract", dpi: int = 300):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def extract_page(self, page: fitz.Page) -> PageData:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")
