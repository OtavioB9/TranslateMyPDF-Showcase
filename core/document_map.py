from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .models import PageData

# Definições de tipos canônicos para o mapeamento espacial do PDF
BlockType = Literal["text", "toc", "table", "math", "link"]
MathStrategy = Literal["protect", "rasterize", ""]
TableExtractionStrategy = Literal["pymupdf", "pdfplumber", "manual"]
BBox = tuple[float, float, float, float]
RGBColor = tuple[float, float, float]


class SpanMap(BaseModel):
    """Representação canônica de um span (fragmento de texto) no mapa de coordenadas."""

    id: str
    text: str
    translated_text: str | None = None
    bbox: BBox
    origin: tuple[float, float]
    page_number: int
    block_id: str
    block_index: int
    line_no: int
    span_index: int
    font_raw: str
    font_clean: str = ""
    font_family: str = ""
    size: float
    color: RGBColor
    color_hex: str
    flags: int
    has_non_body_color: bool = False
    is_hyperlink: bool = False
    hyperlink_uri: str | None = None
    is_math: bool = False
    math_strategy: MathStrategy = ""
    is_protected: bool = False
    protection_reason: str = ""
    is_table_cell: bool = False
    table_cell_bbox: BBox | None = None
    layout_role: str = ""
    color_overlay_text: str | None = None
    reading_order: int = 0


class BlockMap(BaseModel):
    """Representação canônica de um bloco lógico agrupado a partir de spans."""

    id: str
    page_number: int
    block_index: int
    bbox: BBox
    block_type: BlockType = "text"
    spans: list[SpanMap] = Field(default_factory=list)
    column_index: int = 0
    reading_order: int = 0
    is_protected: bool = False
    protection_reason: str = ""

    @property
    def has_translation(self) -> bool:
        """Verifica se algum span neste bloco possui tradução."""
        return any(span.translated_text for span in self.spans)

    @property
    def source_text(self) -> str:
        """Retorna o texto original concatenado do bloco."""
        return " ".join(span.text for span in self.spans if span.text.strip()).strip()

    @property
    def translated_text(self) -> str:
        """Retorna o texto traduzido concatenado do bloco."""
        return " ".join(span.translated_text for span in self.spans if span.translated_text).strip()


class TableRegion(BaseModel):
    """Representação de uma região de tabela identificada durante a extração."""

    id: str
    page_number: int
    bbox: BBox
    extraction_strategy: TableExtractionStrategy = "pymupdf"


class PageMap(BaseModel):
    """Representação canônica de uma página PDF dentro do DocumentMap."""

    page_number: int
    width: float
    height: float
    rotation: int = 0
    dominant_body_color: RGBColor = (0.0, 0.0, 0.0)
    dominant_font: str = ""
    dominant_size: float = 0.0
    blocks: list[BlockMap] = Field(default_factory=list)
    tables: list[TableRegion] = Field(default_factory=list)

    @property
    def block_count(self) -> int:
        return len(self.blocks)

    @property
    def span_count(self) -> int:
        return sum(len(block.spans) for block in self.blocks)


class DocumentMap(BaseModel):
    """
    Mapa estrutural completo de um documento PDF para tradução.
    Funciona como a 'Single Source of Truth' para os módulos de tradução,
    validação e redação visual.
    """

    source_path: str
    pages: list[PageMap] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @classmethod
    def from_pages(
        cls,
        source_path: str,
        pages: list[PageData],
        metadata: dict[str, str] | None = None,
    ) -> DocumentMap:
        """
        Constrói um DocumentMap a partir de objetos PageData extraídos.
        Realiza o agrupamento lógico de spans em blocos e identifica o papel
        de layout de cada elemento.
        """
        # Implementação do construtor de mapa protegida no showcase
        raise NotImplementedError("Lógica de construção de DocumentMap protegida.")
