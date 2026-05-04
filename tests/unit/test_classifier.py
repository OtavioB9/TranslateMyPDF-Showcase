"""
Testes unitários para o classificador de páginas (PageClassifier).
Identifica se uma página é predominantemente vetorial (texto nativo)
ou baseada em imagem (escaneada) para direcionar o motor de extração correto.
"""

from unittest.mock import MagicMock

import fitz
import pytest

from core.classifier import PageClassifier
from core.models import PageType

pytestmark = pytest.mark.unit


def test_classifier_returns_vector_for_dense_text():
    classifier = PageClassifier()
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.number = 0
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_text.return_value = "A" * 100
    assert classifier.classify(page_mock) == PageType.VECTOR


def test_classifier_returns_image_for_empty_text_and_images():
    classifier = PageClassifier()
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.number = 0
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_text.return_value = ""
    # fitz version might expect list of tuples
    page_mock.get_images.return_value = [(1, 0, 100, 100, 8, "DeviceRGB", "", "img", "DCTDecode")]
    page_mock.get_image_rects.return_value = [fitz.Rect(0, 0, 600, 800)]
    assert classifier.classify(page_mock) == PageType.IMAGE


def test_classifier_returns_vector_as_fallback():
    classifier = PageClassifier()
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.number = 0
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_text.return_value = "Short"
    page_mock.get_images.return_value = []
    assert classifier.classify(page_mock) == PageType.VECTOR
