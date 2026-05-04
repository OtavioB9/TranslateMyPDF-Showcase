from core.document_map import DocumentMap
from core.models import PageData, SpanData
from core.validation import QualityReport


def _span(
    text: str,
    bbox: tuple[float, float, float, float],
    block_index: int,
    color: tuple[float, float, float] = (0, 0, 0),
) -> SpanData:
    span = SpanData(
        text=text,
        bbox=bbox,
        font_size=10.0,
        font_name="helv",
        font_flags=0,
        color=color,
        origin=(bbox[0], bbox[1]),
        page_number=0,
    )
    span.block_index = block_index
    return span


def test_quality_report_flags_missing_color_overlay_and_overflow_risk():
    body = _span("See", (10, 10, 30, 24), 1)
    colored = _span("Figure 1-3", (32, 10, 260, 24), 1, color=(0.6, 0, 0))
    colored.is_hyperlink = True
    body.translated_text = "Veja a Figura 1-3 com detalhes adicionais demais para a caixa."

    narrow = _span("Short text", (10, 40, 70, 54), 2)
    narrow.translated_text = (
        "Texto traduzido muito mais longo que provavelmente nao cabe nesta caixa estreita"
    )

    table = _span("Cell value", (10, 70, 60, 90), 3)
    table.is_table_cell = True

    page = PageData(page_number=0, width=600, height=800, spans=[body, colored, narrow, table])
    document_map = DocumentMap.from_pages("sample.pdf", [page])

    report = QualityReport.from_document_map(document_map)

    assert report.total_issues == 3
    assert report.issue_count_by_type["missing_color_overlay"] == 1
    assert report.issue_count_by_type["overflow_risk"] == 1
    assert report.issue_count_by_type["table_cell_without_translation"] == 1
    assert report.pages_with_risk == [0]

    link_issue = next(issue for issue in report.issues if issue.type == "missing_color_overlay")
    assert link_issue.bbox == (32, 10, 260, 24)
    assert link_issue.block_type == "text"
    assert link_issue.source_text == "Figure 1-3"
    assert link_issue.translated_text == body.translated_text
    assert link_issue.color_hex == "#990000"
    assert link_issue.is_hyperlink is True
    assert link_issue.visual_category == "hyperlink"


def test_quality_report_flags_missing_protected_span_in_translation():
    body = _span("Use", (10, 10, 30, 24), 1)
    token = _span("API_KEY", (32, 10, 80, 24), 1)
    body.translated_text = "Use a chave de API."
    token.metadata["is_protected"] = True
    token.metadata["protection_reason"] = "technical_token"

    page = PageData(page_number=0, width=600, height=800, spans=[body, token])
    document_map = DocumentMap.from_pages("sample.pdf", [page])

    report = QualityReport.from_document_map(document_map)

    issue = next(issue for issue in report.issues if issue.type == "protected_span_missing")
    assert issue.severity == "warning"
    assert issue.source_text == "API_KEY"
    assert issue.visual_category == "protected_span"


def test_quality_report_flags_directly_translated_protected_span():
    token = _span("GPT-4V", (10, 10, 60, 24), 1)
    token.translated_text = "GPT quatro"
    token.metadata["is_protected"] = True
    token.metadata["protection_reason"] = "technical_token"

    page = PageData(page_number=0, width=600, height=800, spans=[token])
    document_map = DocumentMap.from_pages("sample.pdf", [page])

    report = QualityReport.from_document_map(document_map)

    issue = next(issue for issue in report.issues if issue.type == "protected_span_changed")
    assert issue.severity == "warning"
    assert issue.source_text == "GPT-4V"
    assert issue.translated_text == "GPT quatro"


def test_quality_report_demotes_non_link_colored_text_to_info():
    body = _span("Read the publisher name", (10, 10, 180, 24), 1)
    colored = _span("O'Reilly", (182, 10, 260, 24), 1, color=(0.8, 0, 0))
    body.translated_text = "Leia a editora no rodape."

    page = PageData(page_number=0, width=600, height=800, spans=[body, colored])
    document_map = DocumentMap.from_pages("sample.pdf", [page])

    report = QualityReport.from_document_map(document_map)

    assert report.total_issues == 1
    issue = report.issues[0]
    assert issue.type == "changed_colored_text"
    assert issue.severity == "info"
    assert issue.visual_category == "colored_text"
    assert report.pages_with_risk == []


def test_quality_report_ignores_toc_colored_text_changes():
    toc = _span("1. Intro........1", (10, 10, 120, 24), 1, color=(0.6, 0, 0))
    toc.metadata["layout_role"] = "toc_entry"
    toc.translated_text = "1. Introducao........1"

    page = PageData(page_number=0, width=600, height=800, spans=[toc])
    document_map = DocumentMap.from_pages("sample.pdf", [page])

    report = QualityReport.from_document_map(document_map)

    assert report.total_issues == 0


def test_quality_report_accepts_table_cell_block_translation():
    first = _span("Photo and video editing", (10, 10, 80, 24), 1)
    second = _span("Design", (10, 26, 36, 40), 1)
    for span in [first, second]:
        span.is_table_cell = True
    first.translated_text = "Edicao de fotos e videos\nDesign"

    page = PageData(page_number=0, width=600, height=800, spans=[first, second])
    document_map = DocumentMap.from_pages("sample.pdf", [page])

    report = QualityReport.from_document_map(document_map)

    assert "table_cell_without_translation" not in report.issue_count_by_type


def test_quality_report_uses_more_tolerant_table_overflow_threshold():
    cell = _span("Coding", (10, 10, 30, 24), 1)
    cell.is_table_cell = True
    cell.metadata["table_cell_bbox"] = (8.0, 8.0, 120.0, 28.0)
    cell.translated_text = "Codificacao"

    page = PageData(page_number=0, width=600, height=800, spans=[cell])
    document_map = DocumentMap.from_pages("sample.pdf", [page])

    report = QualityReport.from_document_map(document_map)

    assert "overflow_risk" not in report.issue_count_by_type


def test_quality_report_serializes_to_json_dict():
    span = _span("Hello", (10, 10, 50, 24), 1)
    span.translated_text = "Ola"
    page = PageData(page_number=0, width=600, height=800, spans=[span])
    document_map = DocumentMap.from_pages("sample.pdf", [page])

    payload = QualityReport.from_document_map(document_map).to_json_dict()

    assert payload["source_path"] == "sample.pdf"
    assert payload["total_issues"] == 0
    assert payload["summary"]["pages"] == 1
