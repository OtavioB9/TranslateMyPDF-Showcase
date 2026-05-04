"""
Testes de integridade do modelo DocumentMap.
Verifica se a representação hierárquica do documento preserva a estrutura de
páginas, blocos e spans, além de inferir corretamente metadados de proteção
(URLs, e-mails, tokens técnicos).
"""

from core.document_map import DocumentMap
from core.models import PageData, SpanData, TableRegionData


def _span(
    text: str,
    bbox: tuple[float, float, float, float],
    block_index: int,
    color: tuple[float, float, float] = (0, 0, 0),
) -> SpanData:
    span = SpanData(
        text=text,
        bbox=bbox,
        font_size=10.0,
        font_name="helv",
        font_flags=0,
        color=color,
        origin=(bbox[0], bbox[1]),
        page_number=0,
    )
    span.block_index = block_index
    return span


def test_document_map_preserves_page_block_and_span_structure():
    body = _span("Hello", (10, 10, 50, 24), 1)
    body.translated_text = "Ola"

    link = _span("Figure 1-3", (52, 10, 100, 24), 1, color=(0.6, 0, 0))
    link.is_hyperlink = True
    link.metadata["color_overlay_text"] = "Figura 1-3"

    toc = _span("1. Intro........1", (20, 40, 200, 56), 2)
    toc.metadata["layout_role"] = "toc_entry"

    table = _span("Cell", (10, 70, 60, 90), 3)
    table.is_table_cell = True
    table.metadata["table_cell_bbox"] = (8.0, 68.0, 120.0, 96.0)

    math = _span("x^2", (10, 100, 35, 116), 4)
    math.is_math = True

    page = PageData(
        page_number=0,
        width=600,
        height=800,
        rotation=90,
        spans=[body, link, toc, table, math],
        table_regions=[
            TableRegionData(
                id="p0-t0",
                page_number=0,
                bbox=(8.0, 68.0, 120.0, 96.0),
                extraction_strategy="pymupdf",
            )
        ],
    )

    document_map = DocumentMap.from_pages("sample.pdf", [page])

    assert document_map.source_path == "sample.pdf"
    assert document_map.page_count == 1
    assert document_map.pages[0].rotation == 90
    assert document_map.pages[0].tables[0].id == "p0-t0"
    assert document_map.pages[0].tables[0].bbox == (8.0, 68.0, 120.0, 96.0)
    assert document_map.pages[0].block_count == 4
    assert document_map.pages[0].span_count == 5
    assert document_map.pages[0].blocks[0].block_type == "text"
    assert document_map.pages[0].blocks[1].block_type == "toc"
    assert document_map.pages[0].blocks[2].block_type == "table"
    assert document_map.pages[0].blocks[2].bbox == (8.0, 68.0, 120.0, 96.0)
    assert document_map.pages[0].blocks[3].block_type == "math"

    link_span = document_map.pages[0].blocks[0].spans[1]
    assert link_span.id == "p0-b1-l0-s1"
    assert link_span.has_non_body_color is True
    assert link_span.is_hyperlink is True
    assert link_span.color_overlay_text == "Figura 1-3"

    table_span = document_map.pages[0].blocks[2].spans[0]
    assert table_span.table_cell_bbox == (8.0, 68.0, 120.0, 96.0)

    math_span = document_map.pages[0].blocks[3].spans[0]
    assert math_span.is_protected is True
    assert math_span.protection_reason == "math"
    assert math_span.math_strategy == "protect"


def test_document_map_infers_protected_span_metadata_from_text():
    url = _span("https://example.com/api/v1", (10, 10, 150, 24), 1)
    email = _span("support@example.com", (10, 30, 120, 44), 2)
    token = _span("GPT-4V", (10, 50, 60, 64), 3)
    page = PageData(page_number=0, width=600, height=800, spans=[url, email, token])

    document_map = DocumentMap.from_pages("sample.pdf", [page])
    spans = [block.spans[0] for block in document_map.pages[0].blocks]

    assert [span.protection_reason for span in spans] == [
        "url",
        "email",
        "technical_token",
    ]
    assert all(span.is_protected for span in spans)
