import pytest

from utils.text import (
    is_equation_like,
    is_translatable,
    protected_terms,
    protection_reason,
)

pytestmark = pytest.mark.unit


def test_is_equation_like_blocks_formulas():
    # Deve ser True (é matemático)
    assert is_equation_like("∑(x_i - μ)² / N") is True
    assert is_equation_like("P(A|B) = P(B|A)P(A)/P(B)") is True
    assert is_equation_like("lim_{x->0} sin(x)/x = 1") is True


def test_is_equation_like_allows_regular_text_with_math_symbols():
    # Frases gramaticais, mesmo com símbolos, devem passar como texto (is_equation_like = False)
    assert is_equation_like("The total value is $500.00.") is False
    assert is_equation_like("Let x be the number of apples.") is False
    assert is_equation_like("For all positive values where n > 0") is False


def test_is_translatable_blocks_code_and_short_strings():
    # Textos muito curtos
    assert is_translatable("a", font_name="Arial", is_math=False) is False
    assert is_translatable("  ", font_name="Arial", is_math=False) is False

    # Código ou URLs
    assert is_translatable("import os", font_name="Terminal", is_math=False) is False
    assert is_translatable("http://example.com/api/v1", font_name="Arial", is_math=False) is False


def test_is_translatable_blocks_flags():
    # Textos que já estão com flags explícitas passadas pelo pipeline
    assert is_translatable("The quick brown fox", font_name="Arial", is_math=True) is False


def test_is_translatable_allows_regular_prose():
    assert (
        is_translatable(
            "This is a standard English sentence that needs translation.",
            font_name="Times",
            is_math=False,
        )
        is True
    )


def test_protection_reason_classifies_protected_span_types():
    assert protection_reason("https://example.com/api/v1", "Arial", False) == "url"
    assert protection_reason("support@example.com", "Arial", False) == "email"
    assert protection_reason("ISBN 978-1-098-16630-4", "Arial", False) == "isbn"
    assert protection_reason("import pathlib", "Consolas", False) == "code"
    assert protection_reason("GPT-4V", "Arial", False) == "technical_token"
    assert protection_reason("E = mc^2", "Arial", True) == "math"


def test_protected_terms_finds_inline_tokens_without_regular_words():
    terms = protected_terms(
        "Use GPT-4V with API_KEY, email support@example.com, and cite ISBN 978-1-098-16630-4."
    )

    assert "GPT-4V" in terms
    assert "API_KEY" in terms
    assert "support@example.com" in terms
    assert "ISBN 978-1-098-16630-4" in terms
    assert "Use" not in terms
    assert "email" not in terms
