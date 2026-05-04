from pathlib import Path
from unittest.mock import MagicMock

import fitz
import pytest

from core.extractor import PageData, SpanData
from core.font_manager import FontManager
from core.redactor import PDFRedactor

pytestmark = pytest.mark.unit


def _span(text, bbox, color=(0, 0, 0)):
    return SpanData(
        text=text,
        bbox=bbox,
        font_size=10.5,
        font_name="helv",
        font_flags=0,
        color=color,
        origin=(bbox[0], bbox[1]),
        page_number=1,
    )


def test_shrink_loop_lowers_font_size_until_fit():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.insert_textbox.side_effect = [-1.0, -1.0, 5.0]

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)

    final_bbox, final_size = redactor._find_fitting_size(
        temp_page=page_mock,
        bbox=(0, 0, 100, 20),
        text="Encolha-me",
        font_name="helv",
        color=(0, 0, 0),
        initial_size=12.0,
        bottom_limit=21.0,
        right_limit=106.0,
    )

    assert page_mock.insert_textbox.call_count == 3
    assert final_size == 11.0


def test_find_fitting_size_expands_vertically_before_shrinking():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)

    def insert_textbox(rect, *args, **kwargs):
        return 5.0 if rect.height >= 70 and kwargs["fontsize"] == 12.0 else -1.0

    page_mock.insert_textbox.side_effect = insert_textbox

    fm = MagicMock()
    fm._buffers = {}
    redactor = PDFRedactor(font_manager=fm)

    final_bbox, final_size = redactor._find_fitting_size(
        temp_page=page_mock,
        bbox=(10, 10, 160, 24),
        text="Texto traduzido mais longo que precisa de espaco vertical livre.",
        font_name="helv",
        color=(0, 0, 0),
        initial_size=12.0,
        bottom_limit=140.0,
        right_limit=400.0,
    )

    assert final_size == 12.0
    assert fitz.Rect(final_bbox).height >= 70


def test_fitting_candidates_keep_margin_before_next_obstacle():
    fm = MagicMock()
    fm._buffers = {}
    redactor = PDFRedactor(font_manager=fm)

    candidates = redactor._fitting_bbox_candidates(
        bbox=(90, 437, 432, 552),
        initial_size=10.0,
        bottom_limit=607.0,
        right_limit=520.0,
        alignment=fitz.TEXT_ALIGN_JUSTIFY,
    )

    assert candidates
    assert all(rect.y1 <= 603.0 for rect in candidates)


def test_fitting_candidates_preserve_horizontal_body_bounds():
    fm = MagicMock()
    fm._buffers = {}
    redactor = PDFRedactor(font_manager=fm)

    candidates = redactor._fitting_bbox_candidates(
        bbox=(72, 264, 432, 316),
        initial_size=20.0,
        bottom_limit=500.0,
        right_limit=520.0,
        alignment=fitz.TEXT_ALIGN_JUSTIFY,
    )

    assert candidates
    assert all(rect.x0 == 72 for rect in candidates)
    assert all(rect.x1 <= 434 for rect in candidates)


def test_fitting_candidates_expand_centered_blocks_horizontally():
    fm = MagicMock()
    fm._buffers = {}
    redactor = PDFRedactor(font_manager=fm)

    candidates = redactor._fitting_bbox_candidates(
        bbox=(180, 140, 324, 164),
        initial_size=20.0,
        bottom_limit=260.0,
        right_limit=500.0,
        alignment=fitz.TEXT_ALIGN_CENTER,
    )

    assert any(rect.width > 200 for rect in candidates)
    assert any(rect.x0 < 180 and rect.x1 > 324 for rect in candidates)


def test_redactor_limits_cover_text_before_overlapping_image():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 450, 570)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._visual_obstacles = MagicMock(return_value=[(126.0, 180.0, 350.0, 505.0)])
    redactor._find_fitting_size = MagicMock(return_value=((22, 145, 248, 178), 14.0))

    subtitle = _span(
        "Building Applications with Foundation Models",
        (22.0, 145.0, 248.0, 200.0),
        color=(0.57, 0.32, 0.24),
    )
    subtitle.block_index = 1
    subtitle.translated_text = "Construindo Aplicativos com Modelos Fundamentais"

    page_data = PageData(page_number=0, width=450, height=570, spans=[subtitle])

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    bottom_limit = redactor._find_fitting_size.call_args.args[6]
    assert bottom_limit <= 178.0


def test_redactor_does_not_compress_cover_title_against_overlapping_subtitle():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 450, 570)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_cover_display_size = MagicMock(return_value=((28, 65, 465, 149), 54.0))

    title = _span("AI Engineering", (28.0, 65.0, 465.0, 149.0))
    subtitle = _span(
        "Building Applications with Foundation Models",
        (31.0, 145.0, 248.0, 201.0),
        color=(0.57, 0.32, 0.24),
    )
    title.block_index = 1
    subtitle.block_index = 2
    title.font_size = 68.0
    subtitle.font_size = 24.0
    title.translated_text = "Engenharia de IA"
    subtitle.translated_text = "Construindo Aplicativos com Modelos Fundamentais"

    page_data = PageData(page_number=0, width=450, height=570, spans=[title, subtitle])

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    first_call = redactor._find_cover_display_size.call_args_list[0]
    assert first_call.args[1:] == (
        (28.0, 65.0, 465.0, 149.0),
        "Engenharia de IA",
        "helv",
        (0, 0, 0),
        68.0,
        fitz.TEXT_ALIGN_LEFT,
    )


def test_redactor_limits_expansion_before_adjacent_logical_block():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 504, 648)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((312, 339, 467, 404), 8.0))

    current = _span(
        "Chip Huyen works at the intersection of AI.",
        (312.9, 339.0, 467.3, 404.0),
    )
    next_block = _span(
        "learning systems design at Stanford.",
        (312.9, 404.2, 460.0, 430.0),
    )
    current.block_index = 1
    next_block.block_index = 2
    current.translated_text = (
        "Chip Huyen trabalha na interseção de IA, dados e narrativa. "
        "Anteriormente, ela trabalhou na Snorkel AI e na NVIDIA."
    )
    next_block.translated_text = "design de sistemas de aprendizagem em Stanford."

    page_data = PageData(page_number=1, width=504, height=648, spans=[current, next_block])

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    first_call = redactor._find_fitting_size.call_args_list[0]
    assert first_call.args[6] == pytest.approx(404.2)


def test_cover_display_fitting_prefers_shrinking_inside_original_box():
    doc = fitz.open()
    try:
        temp_page = doc.new_page(width=450, height=570)
        font_manager = FontManager(Path(__file__).parents[2] / "fonts")
        font_manager.register_for_page(temp_page)
        redactor = PDFRedactor(font_manager=font_manager)

        bbox, font_size = redactor._find_cover_display_size(
            temp_page,
            (31.7, 145.3, 248.5, 200.8),
            "Construindo Aplicativos com Modelos Fundamentais",
            "NotoSans",
            (0.57, 0.32, 0.24),
            24.0,
            fitz.TEXT_ALIGN_LEFT,
        )
    finally:
        doc.close()

    assert bbox == (31.7, 145.3, 248.5, 200.8)
    assert 14.0 <= font_size < 24.0


def test_redactor_draws_compact_metadata_as_single_line():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 504, 648)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((72, 179, 193, 188), 5.0))

    span = _span("Acquisitions Editor: Nicole Butterfield", (72, 179, 193, 191))
    span.block_index = 1
    span.font_size = 8.0
    span.origin = (72, 188)
    span.translated_text = "Aq.: Nicole Butterfield"
    page_data = PageData(page_number=5, width=504, height=648, spans=[span])

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    page_mock.insert_text.assert_called_once()
    assert page_mock.insert_text.call_args.args[1] == "Aq.: Nicole Butterfield"


def test_redactor_draws_illustrator_metadata_as_single_line():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 504, 648)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((264, 218, 364, 227), 5.0))

    span = _span("Illustrator: Kate Dullea", (264, 218, 364, 230))
    span.block_index = 1
    span.font_size = 8.0
    span.origin = (264, 227)
    span.translated_text = "Ilust.: Kate Dullea"
    page_data = PageData(page_number=5, width=504, height=648, spans=[span])

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    page_mock.insert_text.assert_called_once()
    assert page_mock.insert_text.call_args.args[1] == "Ilust.: Kate Dullea"


def test_single_line_visual_center_is_detected_as_centered():
    fm = MagicMock()
    fm._buffers = {}
    redactor = PDFRedactor(font_manager=fm)
    spans = [
        _span("Praise for", (180.0, 140.0, 240.0, 164.0)),
        _span("AI Engineering", (242.0, 140.0, 324.0, 164.0)),
    ]

    alignment = redactor._detect_alignment(
        spans,
        redactor._merge_bboxes(spans),
        page_width=504.0,
    )

    assert alignment == fitz.TEXT_ALIGN_CENTER


def test_mixed_style_paragraph_is_not_detected_as_centered():
    fm = MagicMock()
    fm._buffers = {}
    redactor = PDFRedactor(font_manager=fm)
    spans = [
        _span("If I could use only one word to describe", (72.0, 264.8, 341.1, 279.0)),
        _span("scale", (342.1, 264.7, 361.6, 279.0)),
        _span(". The AI models", (361.6, 264.8, 432.0, 279.0)),
        _span("behind applications like ChatGPT, Google", (72.0, 277.4, 432.0, 291.6)),
        _span("scale that they’re consuming", (72.0, 290.0, 195.6, 304.2)),
        _span("a nontrivial portion", (196.1, 290.0, 280.1, 304.2), color=(0.6, 0, 0)),
        _span("of the world’s electricity, and we’re", (280.1, 290.0, 432.0, 304.2)),
        _span("at risk of", (72.0, 302.6, 111.2, 316.8)),
        _span(
            "running out of publicly available internet data",
            (111.2, 302.6, 304.4, 316.8),
            color=(0.6, 0, 0),
        ),
        _span("to train them.", (304.4, 302.6, 364.7, 316.8)),
    ]

    alignment = redactor._detect_alignment(spans, redactor._merge_bboxes(spans))

    assert alignment == fitz.TEXT_ALIGN_JUSTIFY


def test_redactor_translates_and_reinserts():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)

    page_data = PageData(page_number=1, width=600, height=800)
    span = SpanData(
        text="hello",
        bbox=(10, 10, 50, 25),
        font_size=10.0,
        font_name="helv",
        font_flags=0,
        color=(1, 0, 0),
        origin=(10, 20),
        page_number=1,
    )
    span.block_index = 0
    span.translated_text = "olá"
    page_data.spans.append(span)

    redactor.apply_page(page_mock, page_data)

    assert page_mock.insert_textbox.call_count == 1
    args, kwargs = page_mock.insert_textbox.call_args
    assert args[1] == "olá"
    assert kwargs.get("color") == (1, 0, 0)


def test_redactor_does_not_redact_untranslated_math_spans():
    page_mock = MagicMock(spec=fitz.Page)
    fm = MagicMock()
    fm._buffers = {}
    redactor = PDFRedactor(font_manager=fm)

    page_data = PageData(page_number=1, width=600, height=800)
    math_span = SpanData(
        text="E = mc^2",
        bbox=(10, 10, 80, 25),
        font_size=10.0,
        font_name="Symbol",
        font_flags=0,
        color=(0, 0, 0),
        origin=(10, 20),
        page_number=1,
        is_math=True,
    )
    math_span.block_index = 1
    page_data.spans.append(math_span)

    redactor._mark_redactions(page_mock, page_data)

    page_mock.add_redact_annot.assert_not_called()


def test_redactor_does_not_redact_untranslated_protected_spans():
    page_mock = MagicMock(spec=fitz.Page)
    fm = MagicMock()
    fm._buffers = {}
    redactor = PDFRedactor(font_manager=fm)

    code = _span("API_KEY", (10, 10, 60, 25))
    body = _span("Use the value from your environment.", (65, 10, 260, 25))
    for span in [code, body]:
        span.block_index = 1
    code.metadata["is_protected"] = True
    code.metadata["protection_reason"] = "technical_token"
    body.translated_text = "Use o valor do seu ambiente."

    page_data = PageData(page_number=1, width=600, height=800, spans=[code, body])

    redactor._mark_redactions(page_mock, page_data)

    redaction_rects = [call.args[0] for call in page_mock.add_redact_annot.call_args_list]
    assert redaction_rects
    assert all(rect[0] > 60 for rect in redaction_rects)


def test_redactor_uses_body_color_when_link_span_is_colored():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.insert_textbox.return_value = 5.0
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((10, 10, 240, 45), 10.0))

    red_link = _span("OpenAI", (10, 10, 48, 25), color=(0.8, 0.0, 0.0))
    body_a = _span("released a new model", (50, 10, 170, 25), color=(0, 0, 0))
    body_b = _span("for developers.", (172, 10, 240, 25), color=(0, 0, 0))
    for span in [red_link, body_a, body_b]:
        span.block_index = 1
    red_link.translated_text = "A OpenAI lancou um novo modelo para desenvolvedores."

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[red_link, body_a, body_b],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    _, kwargs = page_mock.insert_textbox.call_args
    assert kwargs["color"] == (0, 0, 0)


def test_redactor_keeps_url_color_without_coloring_entire_paragraph():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.insert_textbox.return_value = 5.0
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((10, 10, 360, 45), 10.0))

    body_a = _span("See ", (10, 10, 30, 25), color=(0, 0, 0))
    url = _span(
        "http://oreilly.com/catalog/9781098166304",
        (31, 10, 250, 25),
        color=(0.8, 0.0, 0.0),
    )
    body_b = _span(" for release details.", (252, 10, 360, 25), color=(0, 0, 0))
    for span in [body_a, url, body_b]:
        span.block_index = 1
    url.is_hyperlink = True
    url.link_uri = "http://oreilly.com/catalog/9781098166304"
    body_a.translated_text = (
        "Veja http://oreilly.com/catalog/9781098166304 para detalhes de lancamento."
    )

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[body_a, url, body_b],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    main_call = page_mock.insert_textbox.call_args_list[0]
    assert main_call.kwargs["color"] == (0, 0, 0)

    overlay_calls = [
        call
        for call in page_mock.insert_textbox.call_args_list[1:]
        if call.args[1] == "http://oreilly.com/catalog/9781098166304"
    ]
    assert overlay_calls
    assert overlay_calls[0].kwargs["color"] == (0.8, 0.0, 0.0)


def test_redactor_uses_translated_color_overlay_text():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.insert_textbox.return_value = 5.0
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.draw_rect.return_value = None

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((10, 10, 360, 60), 10.0))
    redactor._layout_words = MagicMock(
        return_value=[
            (10, 10, 18, 22, "A"),
            (20, 10, 50, 22, "OpenAI"),
            (52, 10, 92, 22, "observou"),
            (94, 10, 106, 22, "em"),
            (108, 10, 126, 22, "seu"),
            (128, 10, 166, 22, "cartao"),
            (168, 10, 178, 22, "de"),
            (180, 10, 222, 22, "sistema"),
            (224, 10, 270, 22, "GPT-4V"),
        ]
    )

    body_a = _span("OpenAI", (10, 10, 50, 25), color=(0, 0, 0))
    colored = _span("noted in their GPT-4V system card", (52, 10, 220, 25), color=(0.8, 0, 0))
    body_b = _span("in 2023.", (222, 10, 260, 25), color=(0, 0, 0))
    for span in [body_a, colored, body_b]:
        span.block_index = 1
    colored.metadata["color_overlay_text"] = "observou em seu cartao de sistema GPT-4V"
    body_a.translated_text = "A OpenAI observou em seu cartao de sistema GPT-4V em 2023."

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[body_a, colored, body_b],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    overlay_calls = [
        call
        for call in page_mock.insert_textbox.call_args_list[1:]
        if call.args[1] == "observou em seu cartao de sistema GPT-4V"
    ]
    assert overlay_calls
    assert overlay_calls[0].kwargs["color"] == (0.8, 0, 0)


def test_redactor_recomposes_toc_leaders_before_fitting():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((10, 10, 240, 25), 10.5))

    long_toc = (
        "7. Ajuste fino supervisionado e preferencias "
        ". . . . . . . . . . . . . . . . . . . . . . . . 307"
    )
    span = _span(
        "7. Finetuning........................................307",
        (10, 10, 432, 25),
    )
    span.block_index = 1
    span.translated_text = long_toc
    span.metadata["layout_role"] = "toc_entry"

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[span],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    redactor._find_fitting_size.assert_not_called()
    inserted_texts = [call.args[1] for call in page_mock.insert_textbox.call_args_list]
    assert inserted_texts[0].startswith("7. Ajuste fino supervisionado")
    assert any(". ." in text for text in inserted_texts)
    assert inserted_texts[-1] == "307"


def test_redactor_keeps_toc_page_aligned_without_dotted_leaders():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((10, 10, 320, 25), 10.5))

    span = _span(
        "Evaluation Criteria                                      160",
        (10, 10, 320, 25),
    )
    span.block_index = 1
    span.translated_text = "Criterios de Avaliacao            160"
    span.metadata["layout_role"] = "toc_entry"

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[span],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    redactor._find_fitting_size.assert_not_called()
    inserted_texts = [call.args[1] for call in page_mock.insert_textbox.call_args_list]
    assert inserted_texts == ["Criterios de Avaliacao", "160"]
    page_call = page_mock.insert_textbox.call_args_list[-1]
    assert page_call.kwargs["align"] == fitz.TEXT_ALIGN_RIGHT


def test_redactor_draws_toc_page_number_at_original_size():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((86, 64, 432, 78), 5.0))

    span = _span(
        "Summary                                                                 403",
        (86.4, 64.9, 432.0, 78.0),
    )
    span.block_index = 1
    span.translated_text = "Resumo            403"
    span.metadata["layout_role"] = "toc_entry"

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[span],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    redactor._find_fitting_size.assert_not_called()
    title_call = page_mock.insert_textbox.call_args_list[0]
    assert title_call.args[1] == "Resumo"
    assert title_call.kwargs["fontsize"] == 10.5
    page_call = page_mock.insert_textbox.call_args_list[-1]
    page_rect, page_text = page_call.args[:2]
    assert page_text == "403"
    assert page_call.kwargs["fontsize"] == 10.5
    assert page_call.kwargs["align"] == fitz.TEXT_ALIGN_RIGHT
    assert page_rect.x1 == 432.0


def test_redactor_draws_dotted_toc_page_number_without_shrinking():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((72, 88, 432, 104), 5.0))

    span = _span(
        "9. Inference Optimization. . . . . . . . . . . . . . . . . . . . . 405",
        (72.0, 88.8, 432.0, 104.0),
    )
    span.font_size = 12.0
    span.block_index = 1
    span.translated_text = "9. Otimizacao de Inferencia . . . . . . . . . . . . . . . . . . 405"
    span.metadata["layout_role"] = "toc_entry"

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[span],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    redactor._find_fitting_size.assert_not_called()
    inserted_texts = [call.args[1] for call in page_mock.insert_textbox.call_args_list]
    page_call = page_mock.insert_textbox.call_args_list[-1]
    title_call = page_mock.insert_textbox.call_args_list[0]
    assert any(". ." in text for text in inserted_texts)
    assert title_call.kwargs["fontsize"] == 12.0
    assert page_call.args[1] == "405"
    assert page_call.kwargs["fontsize"] == 12.0
    assert page_call.kwargs["align"] == fitz.TEXT_ALIGN_RIGHT


def test_redactor_renders_toc_entry_on_real_page():
    doc = fitz.open()
    page = doc.new_page(width=504, height=648)
    font_manager = FontManager(Path(__file__).parents[2] / "fonts")
    font_manager.register_for_page(page)
    redactor = PDFRedactor(font_manager=font_manager)

    rendered = redactor._insert_toc_entry(
        page,
        "Avaliar Sistemas de IA . . . . . . . . . . . . . . . . . . 159",
        (86.4, 52.82, 432.0, 67.2),
        "NotoSerifBold",
        12.0,
        (0, 0, 0),
    )

    text = page.get_text()
    doc.close()
    assert rendered is True
    assert "Avaliar Sistemas de IA" in text
    assert "159" in text


def test_redactor_places_bullet_text_after_original_indent():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[1]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((44, 100, 280, 132), 10.0))

    bullet = _span("â€¢", (35, 100, 40, 116))
    first_line = _span("Understand what AI engineering is", (44, 100, 280, 116))
    continuation = _span("from traditional machine learning", (44, 117, 250, 132))
    for span in [bullet, first_line, continuation]:
        span.block_index = 1
    bullet.metadata["is_bullet"] = True
    first_line.translated_text = (
        "Entenda o que e engenharia de IA e como ela difere "
        "da engenharia tradicional de aprendizado de maquina"
    )

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[bullet, first_line, continuation],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    fitted_bbox = redactor._find_fitting_size.call_args.args[1]
    assert fitted_bbox[0] == 44
    assert page_mock.insert_textbox.call_count == 1
    text_call = page_mock.insert_textbox.call_args_list[0]
    assert text_call.args[1].startswith("Entenda o que e engenharia de IA")


def test_redactor_strips_translated_bullet_from_bullet_item():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((44, 100, 280, 132), 10.0))

    bullet = _span("\u2022", (35, 100, 40, 116))
    first_line = _span("Should I build this AI application?", (44, 100, 280, 116))
    for span in [bullet, first_line]:
        span.block_index = 1
    bullet.metadata["is_bullet"] = True
    first_line.translated_text = "\u2022 Devo construir este aplicativo de IA?"

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[bullet, first_line],
    )

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    text_call = page_mock.insert_textbox.call_args_list[0]
    assert text_call.args[1] == "Devo construir este aplicativo de IA?"


def test_redactor_preserves_original_bullet_marker_in_place():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_fitting_size = MagicMock(return_value=((90, 100, 280, 132), 10.0))

    bullet = _span("\u2022", (80, 100, 85, 116))
    space = _span(" ", (85, 100, 90, 116))
    first_line = _span("You are building an AI application", (90, 100, 280, 116))
    for span in [bullet, space, first_line]:
        span.block_index = 1
    bullet.metadata["is_bullet"] = True
    first_line.translated_text = "\u2022 Voce esta construindo um aplicativo de IA"

    page_data = PageData(
        page_number=1,
        width=600,
        height=800,
        spans=[bullet, space, first_line],
    )

    redactor._mark_redactions(page_mock, page_data)
    redaction_rects = [call.args[0] for call in page_mock.add_redact_annot.call_args_list]
    assert all(rect[0] > 85 for rect in redaction_rects)

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    inserted_texts = [call.args[1] for call in page_mock.insert_textbox.call_args_list]
    assert inserted_texts == ["Voce esta construindo um aplicativo de IA"]


def test_redactor_uses_recorded_table_cell_bbox_for_table_text():
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_drawings.return_value = []
    page_mock.get_images.return_value = []
    page_mock.insert_textbox.return_value = 5.0

    fm = MagicMock()
    fm._buffers = {}
    fm.resolve_font.return_value = "helv"
    fm.dominant_span.side_effect = lambda spans: spans[0]
    redactor = PDFRedactor(font_manager=fm)
    redactor._find_table_fitting_size = MagicMock(return_value=((103, 101, 247, 129), 5.0))

    first = _span("Photo and video editing", (108, 105, 175, 116))
    second = _span("Design", (108, 117, 130, 128))
    for span in [first, second]:
        span.block_index = 1
        span.is_table_cell = True
        span.metadata["table_cell_bbox"] = (100.0, 100.0, 250.0, 130.0)
    first.translated_text = "Edicao de fotos e videos\nDesign"

    page_data = PageData(page_number=1, width=600, height=800, spans=[first, second])

    redactor._reinsert_text(page_mock, MagicMock(), page_data)

    redactor._find_table_fitting_size.assert_called_once()
    fitted_bbox = redactor._find_table_fitting_size.call_args.args[1]
    assert fitted_bbox == (103.0, 101.0, 247.0, 129.0)
    inserted = page_mock.insert_textbox.call_args_list[0]
    assert inserted.args[1] == "Edicao de fotos e videos\nDesign"
    assert inserted.kwargs["align"] == fitz.TEXT_ALIGN_LEFT
