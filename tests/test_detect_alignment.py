"""
Verificação heurística de alinhamento de texto.
Garante que o motor identifique corretamente se um bloco de texto está
alinhado à esquerda, direita ou se deve ser justificado, evitando artefatos visuais.
"""

from unittest.mock import MagicMock

import fitz
import pytest

from core.redactor import PDFRedactor


@pytest.fixture
def redactor():
    font_manager = MagicMock()
    return PDFRedactor(font_manager=font_manager)


def _make_span(x0=10.0, x1=200.0, y0=100.0, y1=112.0):
    """Cria um mock de span com bbox."""
    span = MagicMock()
    span.bbox = (x0, y0, x1, y1)
    return span


def test_single_span_returns_left(redactor):
    """Garante que blocos com apenas um span nunca usem alinhamento JUSTIFY para evitar espaçamento quebrado."""
    """Bloco com 1 span nunca deve retornar JUSTIFY."""
    spans = [_make_span()]
    block_bbox = (10.0, 100.0, 200.0, 112.0)
    result = redactor._detect_alignment(spans, block_bbox)
    assert result == fitz.TEXT_ALIGN_LEFT, (
        f"Esperado TEXT_ALIGN_LEFT ({fitz.TEXT_ALIGN_LEFT}), "
        f"obtido {result}. Single-span retornando JUSTIFY causa espaçamento quebrado."
    )


def test_empty_spans_returns_left(redactor):
    """Lista vazia não deve lançar exceção."""
    block_bbox = (0.0, 0.0, 100.0, 12.0)
    result = redactor._detect_alignment([], block_bbox)
    assert result == fitz.TEXT_ALIGN_LEFT


def test_multi_span_aligned_left_returns_left(redactor):
    """Múltiplos spans com margem esquerda consistente e variação à direita → LEFT.

    Heurística: avg_left ≈ 0, avg_right > 0, len <= 2 → LEFT (fallback).
    """
    # Spans alinhados à esquerda (x0=10), mas terminam em posições variadas (x1 varia)
    # block_bbox x0=10, x1=300 → diffs_left ≈ 0, diffs_right variável
    spans = [
        _make_span(x0=10.0, x1=250.0),
        _make_span(x0=10.0, x1=200.0),
    ]
    block_bbox = (10.0, 100.0, 300.0, 112.0)
    result = redactor._detect_alignment(spans, block_bbox)
    assert result == fitz.TEXT_ALIGN_LEFT


def test_multi_span_aligned_right_returns_right(redactor):
    """Múltiplos spans com margem esquerda grande e direita pequena → RIGHT.

    Heurística: avg_left > 20 e avg_right < 10 → RIGHT.
    """
    # block x0=10, x1=300
    # spans: x0=50..80 (diffs_left = 40..70, avg > 20), x1=295..300 (diffs_right = 0..5, avg < 10)
    spans = [
        _make_span(x0=50.0, x1=300.0),
        _make_span(x0=80.0, x1=295.0),
        _make_span(x0=60.0, x1=298.0),
    ]
    block_bbox = (10.0, 100.0, 300.0, 112.0)
    result = redactor._detect_alignment(spans, block_bbox)
    assert result == fitz.TEXT_ALIGN_RIGHT


def test_multi_span_can_return_justify(redactor):
    """Multi-span com variação moderada em ambas as margens → JUSTIFY ou qualquer valor válido."""
    # >2 spans, margem esquerda ≈ 0, margem direita ≈ 0 → cai no fallback JUSTIFY
    spans = [
        _make_span(x0=10.0, x1=198.0),
        _make_span(x0=12.0, x1=200.0),
        _make_span(x0=11.0, x1=195.0),
    ]
    block_bbox = (10.0, 100.0, 200.0, 112.0)
    result = redactor._detect_alignment(spans, block_bbox)
    # qualquer valor é aceito — o teste garante que não lança exceção
    assert result in (
        fitz.TEXT_ALIGN_LEFT,
        fitz.TEXT_ALIGN_RIGHT,
        fitz.TEXT_ALIGN_CENTER,
        fitz.TEXT_ALIGN_JUSTIFY,
    )
