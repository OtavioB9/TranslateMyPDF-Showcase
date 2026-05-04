"""
Testes unitários para o orquestrador de tradução (BatchTranslator).
Valida o sistema de cache SQLite, lógica de fallback automático entre provedores
(Google/DeepL), preservação de termos protegidos (tokens) e o processamento
inteligente de spans com formatação ou cores diferenciadas.
"""

import pytest

from core.extractor import SpanData
from core.translator import BatchTranslator, TranslationProvider

pytestmark = pytest.mark.unit


def test_translation_fallback_instance_state(
    mock_google_provider, mock_deepl_provider, mock_db, mocker
):
    translator = BatchTranslator(source="en", target="pt", primary=mock_deepl_provider)

    # Garantir que o DB não tenha nada
    mocker.patch.object(translator.db, "get_translation", return_value=None)
    mocker.patch.object(translator.db, "get_translations_bulk", return_value={})

    spy_deepl = mocker.spy(mock_deepl_provider, "translate_batch")
    spy_google = mocker.spy(mock_google_provider, "translate_batch")

    # Texto longo para evitar qualquer filtro
    s1 = SpanData(
        "this is a long sentence for translation",
        (0, 0, 10, 10),
        12,
        "Arial",
        0,
        (0, 0, 0),
        (0, 0),
        1,
    )
    s1.block_index = 10

    # Forçar erro de cota
    mock_deepl_provider._raise_quota = True

    # Executa tradução
    res = translator.translate_spans([s1])

    # Verificamos chamadas
    assert spy_deepl.called
    assert spy_google.called

    # Verificamos se fallback rodou
    assert any(
        s.translated_text == "pt_this is a long sentence for translation"
        for s in res
        if s.translated_text
    )

    # O sinalizador deve estar True!!
    assert translator._using_fallback is True


def test_batching_logic_with_monkeypatch(mock_google_provider, mock_db, monkeypatch):
    monkeypatch.setattr("core.translator.BATCH_SIZE", 2)
    translator = BatchTranslator(source="en", target="pt", primary=mock_google_provider)
    mock_db.get_translation.return_value = None

    spans = [
        SpanData(f"text_{i}", (0, 0, 10, 10), 12, "Arial", 0, (0, 0, 0), (0, 0), 1)
        for i in range(5)
    ]
    for i, s in enumerate(spans):
        s.block_index = i

    translator.translate_spans(spans)
    assert all(s.translated_text == f"pt_text_{i}" for i, s in enumerate(spans))


def test_bullet_marker_is_not_sent_to_translation(mock_google_provider, mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=mock_google_provider)
    bullet = SpanData("\u2022", (10, 10, 14, 24), 10, "Arial", 0, (0, 0, 0), (10, 20), 1)
    text = SpanData(
        "Should I build this AI application?",
        (20, 10, 220, 24),
        10,
        "Arial",
        0,
        (0, 0, 0),
        (20, 20),
        1,
    )
    bullet.block_index = 7
    text.block_index = 7
    bullet.metadata["is_bullet"] = True

    translator.translate_spans([bullet, text])

    assert bullet.translated_text is None
    assert text.translated_text == "pt_Should I build this AI application?"


class MarkerAwareProvider(TranslationProvider):
    def translate_batch(self, texts: list[str]) -> list[str]:
        return [
            ("A OpenAI [[L0]]observou em seu cartao de sistema GPT-4V[[/L0]] em 2023.")
            if "[[L0]]" in text
            else f"pt_{text}"
            for text in texts
        ]

    def is_quota_exceeded(self, exception: Exception) -> bool:
        return False


class CacheRepairProvider(TranslationProvider):
    def __init__(self):
        self.seen: list[str] = []

    def translate_batch(self, texts: list[str]) -> list[str]:
        self.seen.extend(texts)
        return [
            ("[[L0]]Chip Huyen[[/L0]] trabalha na intersecao entre IA, dados e narrativa.")
            for _text in texts
        ]

    def is_quota_exceeded(self, exception: Exception) -> bool:
        return False


class RecordingProvider(TranslationProvider):
    def __init__(self):
        self.seen: list[str] = []

    def translate_batch(self, texts: list[str]) -> list[str]:
        self.seen.extend(texts)
        return [f"pt_{text}" for text in texts]

    def is_quota_exceeded(self, exception: Exception) -> bool:
        return False


class ProtectedTokenMungingProvider(TranslationProvider):
    def __init__(self):
        self.seen: list[str] = []

    def translate_batch(self, texts: list[str]) -> list[str]:
        self.seen.extend(texts)
        translated = []
        for text in texts:
            translated.append(
                text.replace("GPT-4V", "GPT quatro")
                .replace("API_KEY", "CHAVE_API")
                .replace("support@example.com", "suporte@exemplo.com")
                .replace("https://example.com/api/v1", "https://exemplo.com/api/v1")
                .replace("ISBN 978-1-098-16630-4", "ISBN traduzido")
            )
        return translated

    def is_quota_exceeded(self, exception: Exception) -> bool:
        return False


def test_colored_spans_are_translated_with_overlay_markers(mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=MarkerAwareProvider())

    body_a = SpanData("OpenAI", (10, 10, 50, 24), 10, "Arial", 0, (0, 0, 0), (10, 20), 1)
    colored = SpanData(
        "noted in their GPT-4V system card",
        (55, 10, 210, 24),
        10,
        "Arial",
        0,
        (0.6, 0, 0),
        (55, 20),
        1,
    )
    body_b = SpanData("in 2023.", (215, 10, 260, 24), 10, "Arial", 0, (0, 0, 0), (215, 20), 1)
    for span in [body_a, colored, body_b]:
        span.block_index = 1

    translator.translate_spans([body_a, colored, body_b])

    target = next(span for span in [body_a, colored, body_b] if span.translated_text)
    assert target.translated_text == ("A OpenAI observou em seu cartao de sistema GPT-4V em 2023.")
    assert "[[L0]]" not in target.translated_text
    assert colored.metadata["color_overlay_text"] == ("observou em seu cartao de sistema GPT-4V")


def test_translator_restores_protected_terms_after_provider_translation(mock_db):
    provider = ProtectedTokenMungingProvider()
    translator = BatchTranslator(source="en", target="pt", primary=provider)
    source = (
        "Use GPT-4V with API_KEY, email support@example.com, visit "
        "https://example.com/api/v1, and cite ISBN 978-1-098-16630-4."
    )
    span = SpanData(source, (10, 10, 420, 40), 10, "Arial", 0, (0, 0, 0), (10, 20), 1)
    span.block_index = 1

    translator.translate_spans([span])

    assert provider.seen == ["Use [[P0]] with [[P1]], email [[P2]], visit [[P3]], and cite [[P4]]."]
    assert span.translated_text is not None
    assert "GPT-4V" in span.translated_text
    assert "API_KEY" in span.translated_text
    assert "support@example.com" in span.translated_text
    assert "https://example.com/api/v1" in span.translated_text
    assert "ISBN 978-1-098-16630-4" in span.translated_text
    assert "GPT quatro" not in span.translated_text
    assert "CHAVE_API" not in span.translated_text


def test_translator_rejects_cached_marker_url_mismatch(mock_db):
    provider = CacheRepairProvider()
    translator = BatchTranslator(source="en", target="pt", primary=provider)

    colored = SpanData(
        "Chip Huyen",
        (10, 10, 60, 24),
        10,
        "Arial",
        0,
        (0.6, 0, 0),
        (10, 20),
        1,
    )
    body = SpanData(
        "works at the intersection of AI, data, and storytelling.",
        (62, 10, 280, 24),
        10,
        "Arial",
        0,
        (0, 0, 0),
        (62, 20),
        1,
    )
    for span in [colored, body]:
        span.block_index = 1

    source_text, _overlays = BatchTranslator._text_with_color_overlay_markers([colored, body])
    bad_cached_translation = (
        "Os livros da O'Reilly estao disponiveis em [[L0]]http://oreilly.com[[/L0]]."
    )
    mock_db.get_translations_bulk.return_value = {source_text: bad_cached_translation}

    translator.translate_spans([colored, body])

    target = next(span for span in [colored, body] if span.translated_text)
    assert provider.seen == [source_text]
    assert (
        target.translated_text == "Chip Huyen trabalha na intersecao entre IA, dados e narrativa."
    )
    assert colored.metadata["color_overlay_text"] == "Chip Huyen"


def test_translator_rejects_cached_marker_when_source_has_no_marker(mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=MarkerAwareProvider())

    span = SpanData(
        "Every AI engineer building real-world applications should read this book.",
        (10, 10, 320, 24),
        10,
        "Arial",
        0,
        (0, 0, 0),
        (10, 20),
        1,
    )
    span.block_index = 1
    source_text, _overlays = BatchTranslator._text_with_color_overlay_markers([span])
    mock_db.get_translations_bulk.return_value = {
        source_text: "[[L0]]Chip Huyen[[/L0]] trabalha na intersecao de IA."
    }

    translator.translate_spans([span])

    assert span.translated_text == (
        "pt_Every AI engineer building real-world applications should read this book."
    )


def test_translator_rejects_cached_translation_that_is_too_short(mock_db):
    provider = RecordingProvider()
    translator = BatchTranslator(source="en", target="pt", primary=provider)
    source = (
        "Just like language models, multimodal models need data to scale up. "
        "Self-supervision works for multimodal models too. This dataset enabled "
        "CLIP to become the first model that could generalize to multiple image "
        "classification tasks without requiring additional training."
    )
    span = SpanData(source, (10, 10, 420, 90), 10, "Arial", 0, (0, 0, 0), (10, 20), 1)
    span.block_index = 1
    mock_db.get_translations_bulk.return_value = {
        source: "aumento em comparação com 2,4%.",
    }

    translator.translate_spans([span])

    assert provider.seen == [source]
    assert span.translated_text == f"pt_{source}"


def test_translator_orders_same_line_spans_by_x_position(mock_db):
    provider = RecordingProvider()
    translator = BatchTranslator(source="en", target="pt", primary=provider)

    url = SpanData(
        "https://oreilly.com",
        (310, 52.1, 390, 64),
        8,
        "Arial",
        0,
        (0.8, 0, 0),
        (310, 62),
        1,
    )
    text = SpanData(
        "For news and information about our books and courses, visit",
        (72, 52.3, 305, 64),
        8,
        "Arial",
        0,
        (0, 0, 0),
        (72, 62),
        1,
    )
    period = SpanData(".", (392, 52.3, 395, 64), 8, "Arial", 0, (0, 0, 0), (392, 62), 1)
    for span in [url, text, period]:
        span.block_index = 1

    translator.translate_spans([url, text, period])

    assert provider.seen == [
        "For news and information about our books and courses, visit [[L0]][[P0]][[/L0]]."
    ]


def test_translator_preserves_contact_block_lines(mock_db):
    provider = RecordingProvider()
    translator = BatchTranslator(source="en", target="pt", primary=provider)
    lines = [
        ("O'Reilly Media, Inc.", (90, 424, 170, 436)),
        ("1005 Gravenstein Highway North", (90, 438, 230, 450)),
        ("support@oreilly.com", (90, 452, 180, 464)),
        ("https://oreilly.com/about/contact.html", (90, 466, 260, 478)),
    ]
    spans = [
        SpanData(text, bbox, 8, "Arial", 0, (0, 0, 0), (bbox[0], bbox[3]), 1)
        for text, bbox in lines
    ]
    for line_index, span in enumerate(spans):
        span.block_index = 1
        span.line_index = line_index

    translator.translate_spans(spans)

    assert provider.seen == []
    translated = next(span.translated_text for span in spans if span.translated_text)
    assert translated == (
        "O'Reilly Media, Inc.\n"
        "1005 Gravenstein Highway North\n"
        "support@oreilly.com\n"
        "https://oreilly.com/about/contact.html"
    )


def test_translator_translates_short_link_list_lines(mock_db):
    provider = RecordingProvider()
    translator = BatchTranslator(source="en", target="pt", primary=provider)
    spans = [
        SpanData(
            "For news and information about our books and courses, visit",
            (72, 52, 300, 64),
            8,
            "Arial",
            0,
            (0, 0, 0),
            (72, 62),
            1,
        ),
        SpanData(
            "https://oreilly.com.",
            (305, 52, 390, 64),
            8,
            "Arial",
            0,
            (0.8, 0, 0),
            (305, 62),
            1,
        ),
        SpanData(
            "Find us on LinkedIn:",
            (72, 66, 160, 78),
            8,
            "Arial",
            0,
            (0, 0, 0),
            (72, 76),
            1,
        ),
        SpanData(
            "https://linkedin.com/company/oreilly-media",
            (165, 66, 360, 78),
            8,
            "Arial",
            0,
            (0.8, 0, 0),
            (165, 76),
            1,
        ),
    ]
    for span in spans:
        span.block_index = 1

    translator.translate_spans(spans)

    assert provider.seen == [
        "For news and information about our books and courses, visit [[P0]].",
        "Find us on LinkedIn: [[P0]]",
    ]
    translated = next(span.translated_text for span in spans if span.translated_text)
    assert translated == (
        "pt_For news and information about our books and courses, visit "
        "https://oreilly.com.\n"
        "pt_Find us on LinkedIn: https://linkedin.com/company/oreilly-media"
    )


def test_translator_keeps_regular_paragraph_with_one_link_as_single_block(mock_db):
    provider = RecordingProvider()
    translator = BatchTranslator(source="en", target="pt", primary=provider)
    spans = [
        SpanData(
            "We have a web page for this book, where we list errata, examples,",
            (72, 52, 390, 64),
            8,
            "Arial",
            0,
            (0, 0, 0),
            (72, 62),
            1,
        ),
        SpanData(
            "and any additional information. You can access this page at",
            (72, 66, 330, 78),
            8,
            "Arial",
            0,
            (0, 0, 0),
            (72, 76),
            1,
        ),
        SpanData(
            "https://oreil.ly/ai-engineering.",
            (335, 66, 470, 78),
            8,
            "Arial",
            0,
            (0.8, 0, 0),
            (335, 76),
            1,
        ),
    ]
    for span in spans:
        span.block_index = 1

    translator.translate_spans(spans)

    assert provider.seen == [
        "We have a web page for this book, where we list errata, examples, and any "
        "additional information. You can access this page at "
        "[[L0]][[P0]].[[/L0]]"
    ]
    translated = next(span.translated_text for span in spans if span.translated_text)
    assert "\n" not in translated


def test_translator_uses_compact_credit_label_translation(mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=MarkerAwareProvider())
    span = SpanData(
        "Acquisitions Editor: Nicole Butterfield",
        (72, 179, 193, 191),
        8,
        "Arial",
        0,
        (0, 0, 0),
        (72, 189),
        1,
    )
    span.block_index = 1
    mock_db.get_translations_bulk.return_value = {}

    translator.translate_spans([span])

    assert span.translated_text == "Aq.: Nicole Butterfield"


def test_table_cell_translation_preserves_source_line_breaks(mock_google_provider, mock_db):
    translator = BatchTranslator(source="en", target="pt", primary=mock_google_provider)
    first = SpanData(
        "Photo and video editing",
        (160, 210, 228, 221),
        8,
        "Arial",
        0,
        (0, 0, 0),
        (160, 219),
        1,
    )
    second = SpanData(
        "Design",
        (160, 222, 182, 233),
        8,
        "Arial",
        0,
        (0, 0, 0),
        (160, 231),
        1,
    )
    for line_index, span in enumerate([first, second]):
        span.block_index = 1
        span.line_index = line_index
        span.is_table_cell = True

    translator.translate_spans([first, second])

    assert first.translated_text == "pt_Photo and video editing\npt_Design"
    assert second.translated_text is None
