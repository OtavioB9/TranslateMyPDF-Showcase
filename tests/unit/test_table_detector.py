"""
Detecção e estruturação de tabelas (TableDetector).
Valida a identificação de regiões de tabela via PyMuPDF e o mapeamento
correto de spans para células, linhas e colunas (metadados de grid).
"""

from types import SimpleNamespace

import fitz

from core.models import PageData, SpanData
from core.table_detector import TableDetector


def _span(text: str, bbox: tuple[float, float, float, float]) -> SpanData:
    return SpanData(
        text=text,
        bbox=bbox,
        font_size=10.0,
        font_name="helv",
        font_flags=0,
        color=(0, 0, 0),
        origin=(bbox[0], bbox[1]),
        page_number=0,
    )


def test_table_detector_records_cell_metadata(mocker):
    page = mocker.Mock(spec=fitz.Page)
    page.number = 0
    table = SimpleNamespace(
        rows=[
            SimpleNamespace(
                cells=[
                    fitz.Rect(10, 10, 80, 30),
                    fitz.Rect(80, 10, 160, 30),
                ]
            )
        ]
    )
    page.find_tables.return_value = SimpleNamespace(tables=[table])
    page_data = PageData(
        page_number=0,
        width=200,
        height=200,
        spans=[
            _span("Input", (15, 12, 70, 25)),
            _span("Output", (90, 12, 150, 25)),
            _span("Outside", (10, 50, 70, 65)),
        ],
    )

    TableDetector().detect_tables(page, page_data)

    input_span = page_data.spans[0]
    output_span = page_data.spans[1]
    outside_span = page_data.spans[2]

    assert input_span.is_table_cell is True
    assert input_span.metadata["table_id"] == 0
    assert input_span.metadata["table_row"] == 0
    assert input_span.metadata["table_col"] == 0
    assert input_span.metadata["table_cell_id"] == "0:0:0"
    assert input_span.metadata["table_cell_bbox"] == (10.0, 10.0, 80.0, 30.0)
    assert output_span.metadata["table_cell_id"] == "0:0:1"
    assert output_span.metadata["table_cell_bbox"] == (80.0, 10.0, 160.0, 30.0)
    assert outside_span.is_table_cell is False
    assert len(page_data.table_regions) == 1
    assert page_data.table_regions[0].id == "p0-t0"
    assert page_data.table_regions[0].bbox == (10.0, 10.0, 160.0, 30.0)
    assert page_data.table_regions[0].extraction_strategy == "pymupdf"
