"""
Tratamento estratégico de Sumários (TOC).
Valida a quebra de entradas de sumário em (prefixo, título, página),
a preservação de "dotted leaders" (pontilhados) e a tradução isolada
do título sem corromper a numeração das páginas.
"""

import pytest

from core.models import SpanData
from core.toc import compose_toc_entry, split_toc_entry
from core.translator import BatchTranslator

pytestmark = pytest.mark.unit


def _span(text, block_index=1):
    span = SpanData(
        text=text,
        bbox=(80, 50, 432, 65),
        font_size=10.5,
        font_name="MinionPro",
        font_flags=0,
        color=(0, 0, 0),
        origin=(80, 50),
        page_number=1,
        block_index=block_index,
    )
    return span


def test_split_toc_entry_with_dotted_leaders():
    entry = split_toc_entry("5. Prompt Engineering. . . . . . . . . . . . . . . 211")

    assert entry is not None
    assert entry.prefix == "5."
    assert entry.title == "Prompt Engineering"
    assert entry.page == "211"
    assert entry.has_leaders is True


def test_split_toc_entry_with_roman_page_and_long_dotted_leaders():
    entry = split_toc_entry(
        "Preface. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  xi"
    )

    assert entry is not None
    assert entry.prefix == ""
    assert entry.title == "Preface"
    assert entry.page == "xi"


def test_split_toc_entry_with_wide_spacing():
    entry = split_toc_entry("Evaluation Criteria                                      160")

    assert entry is not None
    assert entry.prefix == ""
    assert entry.title == "Evaluation Criteria"
    assert entry.page == "160"
    assert entry.has_leaders is False


def test_compose_toc_entry_preserves_page_and_rebuilds_leaders():
    text = compose_toc_entry(prefix="5.", translated_title="Engenharia de Prompt", page="211")

    assert text.startswith("5. Engenharia de Prompt")
    assert text.endswith("211")
    assert ". . ." in text


def test_compose_toc_entry_preserves_no_leader_style():
    text = compose_toc_entry(
        prefix="",
        translated_title="Criterios de Avaliacao",
        page="160",
        has_leaders=False,
    )

    assert text.startswith("Criterios de Avaliacao")
    assert text.endswith("160")
    assert "." not in text


def test_translator_translates_toc_title_only(mock_google_provider, mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=mock_google_provider)
    span = _span("Prompt Engineering. . . . . . . . . . . . . . . 211")
    span.metadata["layout_role"] = "toc_entry"

    translator.translate_spans([span])

    assert span.translated_text is not None
    assert span.translated_text.startswith("pt_Prompt Engineering")
    assert span.translated_text.endswith("211")
    assert ". . ." in span.translated_text
    assert "pt_211" not in span.translated_text


def test_translator_preserves_toc_numeric_marker(mock_google_provider, mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=mock_google_provider)
    span = _span("5.")
    span.metadata["layout_role"] = "toc_marker"

    translator.translate_spans([span])

    assert span.translated_text == "5."


def test_translator_rebuilds_toc_leaders_for_nontranslatable_acronym(mock_google_provider, mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=mock_google_provider)
    span = _span("RAG                                      253")
    span.metadata["layout_role"] = "toc_entry"

    translator.translate_spans([span])

    assert span.translated_text is not None
    assert span.translated_text.startswith("RAG")
    assert span.translated_text.endswith("253")
    assert ". . ." not in span.translated_text


def test_translator_uses_toc_entry_span_when_marker_shares_block(mock_google_provider, mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=mock_google_provider)
    marker = _span("5.", block_index=7)
    entry = _span("Prompt Engineering. . . . . . . . . . . . . . . 211", block_index=7)
    marker.metadata["layout_role"] = "toc_entry"
    entry.metadata["layout_role"] = "toc_entry"

    translator.translate_spans([marker, entry])

    assert marker.translated_text is None
    assert entry.translated_text is not None
    assert entry.translated_text.startswith("5. pt_Prompt Engineering")
    assert entry.translated_text.endswith("211")
    assert ". . ." in entry.translated_text
