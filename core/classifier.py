import fitz

from utils.logger import get_logger

from .models import PageType

logger = get_logger(__name__)


class PageClassifier:
    def __init__(self, min_char_threshold: int = 50, image_area_threshold: float = 0.8):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def classify(self, page: fitz.Page) -> PageType:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")
