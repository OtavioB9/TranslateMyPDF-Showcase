import fitz

from utils.logger import get_logger

from .models import PageData, SpanData

logger = get_logger(__name__)
_MATH_FONTS = (
    "cmmi",
    "cmsy",
    "cmr",
    "cmex",
    "msam",
    "msbm",
    "symbol",
    "mtextra",
    "mathtime",
    "euclid",
    "stmary",
)


class PDFExtractor:
    def __init__(self):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def extract_page(self, page: fitz.Page) -> PageData:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _group_paragraphs(self, page_data: PageData, raw_blocks: list):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _parse_span(self, raw_span: dict, page_number: int) -> SpanData | None:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    @staticmethod
    def _int_to_rgb(color_int: int) -> tuple[float, float, float]:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    @staticmethod
    def _ordered_logical_blocks(page_data: PageData) -> list:
        """Stub para ordenação lógica de blocos para os testes."""
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    @staticmethod
    def is_math_font(font_name: str) -> bool:
        """Verifica se a fonte pertence ao grupo de fontes matemáticas."""
        return any(math_font in font_name.lower() for math_font in _MATH_FONTS)

    @staticmethod
    def normalize_bbox(
        bbox: tuple[float, float, float, float],
    ) -> tuple[float, float, float, float]:
        """Normaliza as coordenadas da caixa delimitadora."""
        return tuple(round(coord, 2) for coord in bbox) # type: ignore
