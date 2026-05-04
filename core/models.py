from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Literal, Optional


class PageType(Enum):
    """Classificação do motor de extração necessário para a página."""

    VECTOR = auto()
    IMAGE = auto()


@dataclass
class SpanData:
    """Dados atômicos de um fragmento de texto extraído do PDF."""

    text: str
    bbox: tuple[float, float, float, float]
    font_size: float
    font_name: str
    font_flags: int
    color: tuple[float, float, float]
    origin: tuple[float, float]
    page_number: int
    block_index: int = 0
    is_table_cell: bool = False
    translated_text: Optional[str] = None
    is_math: bool = False
    is_hyperlink: bool = False
    link_uri: Optional[str] = None
    raw_block_index: int = 0
    line_index: int = 0
    span_index: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class TableRegionData:
    """Região de tabela detectada para processamento especializado."""

    id: str
    page_number: int
    bbox: tuple[float, float, float, float]
    extraction_strategy: Literal["pymupdf", "pdfplumber", "manual"] = "pymupdf"


@dataclass
class PageData:
    """Coleção de dados estruturados de uma página única."""

    page_number: int
    width: float
    height: float
    rotation: int = 0
    page_type: PageType = PageType.VECTOR
    background_color: tuple[float, float, float] = (1.0, 1.0, 1.0)
    spans: list[SpanData] = field(default_factory=list)
    table_regions: list[TableRegionData] = field(default_factory=list)
