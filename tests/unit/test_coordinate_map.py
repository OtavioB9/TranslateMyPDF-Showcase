"""
Validação do mapeamento de coordenadas (CoordinateMapBuilder).
Garante que a estrutura canônica do PDF (blocos, spans, hiperlinks e rotação)
seja extraída e mapeada corretamente para o modelo de dados DocumentMap.
"""

from pathlib import Path

import fitz

from tools.coordinate_map import CoordinateMapBuilder


def test_coordinate_map_builder_extracts_canonical_pdf_structure(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    try:
        page = doc.new_page(width=200, height=200)
        page.insert_text((20, 40), "Hello coordinate map", fontsize=10)
        page.insert_link(
            {
                "kind": fitz.LINK_URI,
                "from": fitz.Rect(0, 0, 200, 200),
                "uri": "https://example.com",
            }
        )
        page.set_rotation(90)
        doc.save(str(pdf_path))
    finally:
        doc.close()

    document_map = CoordinateMapBuilder().build(pdf_path)

    assert document_map.source_path == str(pdf_path)
    assert document_map.page_count == 1
    assert document_map.pages[0].rotation == 90
    assert document_map.pages[0].blocks

    spans = [span for block in document_map.pages[0].blocks for span in block.spans]
    assert any(span.text == "Hello coordinate map" for span in spans)
    assert any(span.is_hyperlink for span in spans)
