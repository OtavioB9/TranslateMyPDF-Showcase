"""
Validação do pipeline de exportação e auditoria de qualidade.
Garante que o sistema gere relatórios JSON detalhando métricas de tradução,
mapeamento de arquivos e auditoria de riscos visuais.
"""

import json
from pathlib import Path

import pytest

from core.models import PageData, SpanData
from pipeline.document import DocumentProcessor

pytestmark = pytest.mark.unit


def test_document_processor_writes_quality_report(tmp_path: Path):
    """Verifica se o DocumentProcessor gera corretamente o arquivo de relatório de qualidade (JSON)."""
    processor = DocumentProcessor()
    output_path = tmp_path / "translated.pdf"
    input_path = tmp_path / "input.pdf"
    span = SpanData(
        text="Hello",
        bbox=(10, 10, 50, 24),
        font_size=10,
        font_name="helv",
        font_flags=0,
        color=(0, 0, 0),
        origin=(10, 20),
        page_number=0,
        translated_text="Ola",
    )
    span.block_index = 1
    page = PageData(page_number=0, width=600, height=800, spans=[span])

    report_path = processor._write_quality_report(input_path, output_path, [page])

    assert report_path == tmp_path / "translated.quality.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["source_path"] == str(input_path)
    assert payload["summary"]["pages"] == 1
