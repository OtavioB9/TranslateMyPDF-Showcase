from pathlib import Path

import fitz

from .models import SpanData


class FontManager:
    BOLD_FLAG = 16
    ITALIC_FLAG = 2
    MONO_FLAG = 8
    SERIF_FLAG = 4
    _FILES = {
        "NotoSerif": "NotoSerif-Regular.ttf",
        "NotoSerifBold": "NotoSerif-Bold.ttf",
        "NotoSerifIt": "NotoSerif-Italic.ttf",
        "NotoSerifBI": "NotoSerif-BoldItalic.ttf",
        "NotoSans": "NotoSans-Regular.ttf",
        "NotoSansBold": "NotoSans-Bold.ttf",
        "NotoSansIt": "NotoSans-Italic.ttf",
        "NotoSansBI": "NotoSans-BoldItalic.ttf",
    }
    _SANS_KEYWORDS = {
        "arial",
        "helvetica",
        "gothic",
        "sans",
        "verdana",
        "tahoma",
        "calibri",
        "futura",
        "inter",
        "roboto",
        "open sans",
        "montserrat",
        "lato",
        "barlow",
    }
    _SERIF_KEYWORDS = {
        "times",
        "roman",
        "garamond",
        "serif",
        "georgia",
        "palatino",
        "minion",
        "caslon",
        "baskerville",
        "merriweather",
        "crimson",
    }

    def __init__(self, fonts_dir: Path):
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def register_for_page(self, page: fitz.Page) -> None:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def clear_page_cache(self) -> None:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def resolve_font(self, original_font: str, flags: int) -> str:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def dominant_span(self, block_spans: list) -> "SpanData":
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")

    def _is_sans(self, font_name: str, flags: int) -> bool:
        raise NotImplementedError("Proprietary core logic abstracted for showcase repository.")
