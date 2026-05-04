"""
Testes unitários para o extrator OCR (OCRExtractor).
Valida a detecção do binário Tesseract no ambiente local e o tratamento
de erros quando o motor de OCR não está disponível.
"""

import pytest

from core.ocr_extractor import OCRExtractor

pytestmark = pytest.mark.unit


def test_ocr_extractor_reports_missing_tesseract_before_extraction():
    extractor = OCRExtractor(tesseract_cmd="Z:\\missing\\tesseract.exe")

    assert extractor.is_available() is False
    with pytest.raises(RuntimeError, match="Tesseract OCR indisponivel"):
        extractor.ensure_available()


def test_ocr_extractor_discovers_per_user_windows_install(tmp_path, monkeypatch):
    install_path = tmp_path / "Programs" / "Tesseract-OCR" / "tesseract.exe"
    install_path.parent.mkdir(parents=True)
    install_path.write_text("", encoding="utf-8")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    extractor = OCRExtractor()

    assert extractor.tesseract_cmd == str(install_path)
