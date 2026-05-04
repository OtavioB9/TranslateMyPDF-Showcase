"""
Teste de integração fumaça (Smoke Test) do pipeline completo.
Valida a orquestração entre Classificação, Extração, Tradução e Redação
em um fluxo contínuo, garantindo a interoperabilidade dos módulos.
"""

import fitz
import pytest

from core.classifier import PageClassifier
from core.extractor import PDFExtractor
from core.font_manager import FontManager
from core.redactor import PDFRedactor
from core.translator import BatchTranslator

pytestmark = pytest.mark.integration


def test_full_pipeline_smoke(tmp_db, mock_google_provider, tmp_path, mocker):
    # Setup de diretório de fontes fake para o FontManager não crashar no __init__
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    for f in FontManager._FILES.values():
        (fonts_dir / f).write_bytes(b"fake font data")

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello world from integration test")

    # 1. Classificação
    classifier = PageClassifier()
    classifier.classify(page)

    # 2. Extração
    extractor = PDFExtractor()
    page_data = extractor.extract_page(page)
    assert len(page_data.spans) > 0

    # 3. Tradução
    translator = BatchTranslator(source="en", target="pt", primary=mock_google_provider)
    translator.translate_spans(page_data.spans)

    # 4. Redação
    # Mockamos register_for_page para não tentar carregar o buffer fake como fonte real
    mocker.patch.object(FontManager, "register_for_page")

    # Mockamos fitz.Page.insert_textbox globalmente para evitar crash de fonte real ausente
    # Já que register_for_page foi mockado, o fitz não terá as fontes "Noto..." registradas
    # e falharia ao tentar usar no insert_textbox real.
    insert_textbox_mock = mocker.patch("fitz.Page.insert_textbox", return_value=1.0)
    mocker.patch("fitz.Page.insert_font")
    mock_font_cls = mocker.patch("fitz.Font")
    mock_font_cls.return_value.text_length.return_value = 10.0  # Valor fake, mas numérico
    # E o add_redact_annot para não crashar se algo for estranho
    mocker.patch("fitz.Page.add_redact_annot")
    mocker.patch("fitz.Page.apply_redactions")

    fm = FontManager(fonts_dir=fonts_dir)
    redactor = PDFRedactor(font_manager=fm)
    redactor.apply_page(page, page_data)

    # Verificação de fluxo: insert_textbox foi chamado no temp_page
    # (que agora está usando o patch global)
    assert insert_textbox_mock.called
    doc.close()
