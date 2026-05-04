"""
Testes de redação visual e reinserção de texto (LayrPDF Redactor).
Valida a preservação de fundos originais, limites de expansão vertical para evitar
sobreposições e a detecção de obstáculos (vetores e imagens).
"""

from unittest.mock import MagicMock

import fitz
import pytest

from core.models import PageData, SpanData
from core.redactor import PDFRedactor


@pytest.fixture
def redactor():
    mock_fm = MagicMock()
    mock_fm._buffers = {}
    return PDFRedactor(mock_fm)


def test_redaction_fill_is_transparent(redactor):
    """Garante que a redação de prosa use fill=None para preservar o fundo original."""
    doc = fitz.open()
    page = doc.new_page()
    page.draw_rect(page.rect, color=(1, 0, 0), fill=(1, 0, 0))  # Fundo vermelho

    page_data = PageData(
        page_number=0,
        width=page.rect.width,
        height=page.rect.height,
        spans=[
            SpanData(
                text="Texto puro",
                bbox=(10, 10, 100, 30),
                font_size=12,
                font_name="Helvetica",
                font_flags=0,
                color=(0, 0, 0),
                origin=(10, 10),
                page_number=0,
                block_index=1,
                is_math=False,
            )
        ],
    )

    redactor._mark_redactions(page, page_data)
    page.apply_redactions()

    # Pega um pixel de dentro da área redigida
    pix = page.get_pixmap(clip=fitz.Rect(15, 15, 20, 20))
    r, g, b = pix.samples[:3]

    # O fundo vermelho deve ter sido preservado
    assert (r, g, b) == (255, 0, 0), "A redação cobriu a cor de fundo nativa da página"


def test_safe_bottom_limit_prevents_overlap(redactor):
    """Garante que o insert_textbox e os fallbacks respeitam o bottom_limit."""
    doc = fitz.open()
    temp_page = doc.new_page()

    # Bloco atual forçando expansão (texto longo num bbox pequeno)
    bbox = (10, 10, 100, 20)  # altura de 10pt
    text = "Um texto muito muito longo que precisa de bastante expansão vertical para caber"

    # O próximo bloco está logo abaixo (y=21)
    bottom_limit = 21.0
    right_limit = 200.0

    final_bbox, _ = redactor._find_fitting_size(
        temp_page, bbox, text, "Helvetica", (0, 0, 0), 12.0, bottom_limit, right_limit
    )

    # O bbox final nunca deve invadir o bottom_limit
    assert final_bbox[3] < bottom_limit, (
        f"O bbox expandido {final_bbox} invadiu o bottom_limit {bottom_limit}"
    )


def test_right_limit_nao_usa_bottom_limit_parcial(redactor, mocker):
    """
    Simula cenário de bug: O loop de right_limit não deve ser afetado por um bottom_limit
    que ainda está sendo calculado ou que pertence a outro fluxo.
    Validamos se a lógica de dois passes em _reinsert_text está correta.
    """
    page = MagicMock(spec=fitz.Page)
    page.rect = fitz.Rect(0, 0, 600, 800)

    # Bloco A (nosso alvo): (10, 10, 100, 50)
    # Bloco B (lateral): (110, 20, 200, 40) -> Deve limitar right_limit para 110
    # Bloco C (abaixo): (10, 150, 100, 200) -> Deve limitar bottom_limit para 150

    page_data = PageData(
        page_number=0,
        width=600,
        height=800,
        spans=[
            SpanData("A", (10, 10, 100, 50), 12, "Arial", 0, (0, 0, 0), (10, 10), 0, 1, False),
            SpanData("B", (110, 20, 200, 40), 12, "Arial", 0, (0, 0, 0), (110, 20), 0, 2, False),
            SpanData("C", (10, 150, 100, 200), 12, "Arial", 0, (0, 0, 0), (10, 150), 0, 3, False),
        ],
    )
    # Mock tradução para passar pelo _block_should_translate
    for s in page_data.spans:
        s.translated_text = "trad"

    # Espionamos insert_textbox
    mocker.patch.object(page, "insert_textbox")
    mocker.patch.object(redactor.font_manager, "resolve_font", return_value="Arial")
    mocker.patch.object(redactor, "_find_fitting_size", return_value=((10, 10, 110, 50), 12))

    temp_page = MagicMock()
    redactor._reinsert_text(page, temp_page, page_data)

    # Verifica se os limites passados para _find_fitting_size foram os corretos
    # call_args.args[6] é bottom_limit, call_args.args[7] é right_limit
    # O primeiro chamado é o Bloco A (index 0 no blocks.items() se ordenado?)
    # Na verdade, blocks.items() segue ordem de inserção. Bloco A foi o primeiro.
    call_args = redactor._find_fitting_size.call_args_list[0][0]
    arg_bottom = call_args[6]
    arg_right = call_args[7]

    assert arg_bottom == 150, f"Bottom limit incorreto: {arg_bottom}"
    assert arg_right == 110, f"Right limit incorreto: {arg_right}"


def test_drawn_box_top_limits_vertical_expansion(redactor, mocker):
    """Linhas/caixas desenhadas abaixo do texto devem limitar a reinserção."""
    page = MagicMock(spec=fitz.Page)
    page.rect = fitz.Rect(0, 0, 600, 800)
    page.get_drawings.return_value = [
        {"rect": fitz.Rect(10, 60, 220, 60)},  # borda superior de um card/figura
    ]
    page.get_images.return_value = []

    page_data = PageData(
        page_number=0,
        width=600,
        height=800,
        spans=[
            SpanData(
                "Paragraph before card",
                (10, 10, 200, 50),
                12,
                "Arial",
                0,
                (0, 0, 0),
                (10, 10),
                0,
                1,
                False,
                translated_text="Texto traduzido antes do card",
            )
        ],
    )

    mocker.patch.object(page, "insert_textbox")
    mocker.patch.object(redactor.font_manager, "resolve_font", return_value="Arial")
    mocker.patch.object(redactor, "_find_fitting_size", return_value=((10, 10, 200, 50), 12))

    redactor._reinsert_text(page, MagicMock(), page_data)

    call_args = redactor._find_fitting_size.call_args_list[0][0]
    assert call_args[6] == 60
