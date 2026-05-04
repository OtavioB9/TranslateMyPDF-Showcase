"""
Testes unitários do extrator de conteúdo (PDFExtractor).
Valida heurísticas de extração, incluindo: detecção de Drop Caps,
tratamento de sumários (TOC), mesclagem lógica de parágrafos quebrados
e identificação de hiperlinks.
"""

from unittest.mock import MagicMock

import fitz
import pytest

from core.extractor import PDFExtractor

pytestmark = pytest.mark.unit


def create_mock_page(blocks_data):
    page_mock = MagicMock(spec=fitz.Page)
    page_mock.number = 0
    page_mock.rect = fitz.Rect(0, 0, 600, 800)
    page_mock.get_text.return_value = {"blocks": blocks_data}
    return page_mock


def test_extractor_marks_drop_caps_as_math():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (10, 10, 300, 100),
            "lines": [
                {
                    "bbox": (10, 10, 30, 60),
                    "spans": [
                        {
                            "text": "T",
                            "size": 50.0,
                            "font": "Bold",
                            "bbox": (10, 10, 30, 60),
                            "color": 0,
                            "origin": (10, 50),
                            "flags": 0,
                        }
                    ],
                },
                {
                    "bbox": (10, 70, 300, 90),
                    "spans": [
                        {
                            "text": "This is a normal paragraph.",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (10, 70, 300, 90),
                            "color": 0,
                            "origin": (10, 85),
                            "flags": 0,
                        }
                    ],
                },
            ],
        }
    ]
    page_mock = create_mock_page(blocks)
    page_data = extractor.extract_page(page_mock)

    t_span = next((s for s in page_data.spans if s.text == "T"), None)
    assert t_span is not None
    assert t_span.is_math is True


def test_extractor_ignores_image_blocks():
    extractor = PDFExtractor()
    blocks = [{"type": 1, "bbox": (0, 0, 100, 100)}]
    page_mock = create_mock_page(blocks)
    page_data = extractor.extract_page(page_mock)
    assert len(page_data.spans) == 0


def test_extractor_splits_multiple_toc_entries_on_same_line():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (80, 50, 432, 66),
            "lines": [
                {
                    "bbox": (80, 50, 432, 66),
                    "spans": [
                        {
                            "text": "Evaluation Criteria                                      160",
                            "size": 10.5,
                            "font": "Regular",
                            "bbox": (80, 50, 245, 66),
                            "color": 0,
                            "origin": (80, 62),
                            "flags": 0,
                        },
                        {
                            "text": "Domain-Specific Capability                              161",
                            "size": 10.5,
                            "font": "Regular",
                            "bbox": (250, 50, 432, 66),
                            "color": 0,
                            "origin": (250, 62),
                            "flags": 0,
                        },
                    ],
                }
            ],
        }
    ]
    page_mock = create_mock_page(blocks)
    page_data = extractor.extract_page(page_mock)

    entries = [s for s in page_data.spans if s.metadata.get("layout_role") == "toc_entry"]

    assert len(entries) == 2
    assert entries[0].block_index != entries[1].block_index


def test_extractor_marks_standalone_toc_marker():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (70, 50, 85, 66),
            "lines": [
                {
                    "bbox": (70, 50, 85, 66),
                    "spans": [
                        {
                            "text": "5.",
                            "size": 12.0,
                            "font": "Bold",
                            "bbox": (70, 50, 85, 66),
                            "color": 0,
                            "origin": (70, 62),
                            "flags": 16,
                        }
                    ],
                }
            ],
        }
    ]
    page_mock = create_mock_page(blocks)
    page_data = extractor.extract_page(page_mock)

    assert page_data.spans[0].metadata.get("layout_role") == "toc_marker"


def test_extractor_marks_spans_intersecting_link_annotations():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (10, 10, 220, 30),
            "lines": [
                {
                    "bbox": (10, 10, 220, 30),
                    "spans": [
                        {
                            "text": "OpenAI",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (10, 10, 60, 25),
                            "color": 0xCC0000,
                            "origin": (10, 22),
                            "flags": 0,
                        },
                        {
                            "text": "released a model",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (65, 10, 180, 25),
                            "color": 0,
                            "origin": (65, 22),
                            "flags": 0,
                        },
                    ],
                }
            ],
        }
    ]
    page_mock = create_mock_page(blocks)
    page_mock.get_links.return_value = [
        {"from": fitz.Rect(10, 10, 60, 25), "uri": "https://openai.com"}
    ]

    page_data = extractor.extract_page(page_mock)

    link_span = next(s for s in page_data.spans if s.text == "OpenAI")
    body_span = next(s for s in page_data.spans if s.text == "released a model")
    assert link_span.is_hyperlink is True
    assert link_span.link_uri == "https://openai.com"
    assert body_span.is_hyperlink is False
    assert body_span.link_uri is None


def test_extractor_marks_internal_link_annotations_without_uri():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (10, 10, 220, 30),
            "lines": [
                {
                    "bbox": (10, 10, 220, 30),
                    "spans": [
                        {
                            "text": "Acknowledgments",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (10, 10, 90, 25),
                            "color": 0x990000,
                            "origin": (10, 22),
                            "flags": 0,
                        },
                        {
                            "text": "on page xx",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (95, 10, 170, 25),
                            "color": 0x990000,
                            "origin": (95, 22),
                            "flags": 0,
                        },
                    ],
                }
            ],
        }
    ]
    page_mock = create_mock_page(blocks)
    page_mock.get_links.return_value = [
        {
            "from": fitz.Rect(10, 10, 170, 25),
            "page": 21,
            "nameddest": "acknowledgments",
        }
    ]

    page_data = extractor.extract_page(page_mock)

    linked_spans = [s for s in page_data.spans if s.text.strip()]
    assert all(s.is_hyperlink for s in linked_spans)
    assert all(s.link_uri is None for s in linked_spans)


def test_extractor_records_source_block_line_and_span_indexes():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (10, 10, 220, 60),
            "lines": [
                {
                    "bbox": (10, 10, 220, 30),
                    "spans": [
                        {
                            "text": "First",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (10, 10, 40, 25),
                            "color": 0,
                            "origin": (10, 22),
                            "flags": 0,
                        }
                    ],
                },
                {
                    "bbox": (10, 35, 220, 55),
                    "spans": [
                        {
                            "text": "Second",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (10, 35, 60, 50),
                            "color": 0,
                            "origin": (10, 47),
                            "flags": 0,
                        },
                        {
                            "text": "Third",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (65, 35, 100, 50),
                            "color": 0,
                            "origin": (65, 47),
                            "flags": 0,
                        },
                    ],
                },
            ],
        }
    ]
    page_mock = create_mock_page(blocks)
    page_mock.get_links.return_value = []

    page_data = extractor.extract_page(page_mock)

    first, second, third = page_data.spans
    assert first.raw_block_index == 0
    assert first.line_index == 0
    assert first.span_index == 0
    assert second.line_index == 1
    assert second.span_index == 0
    assert third.line_index == 1
    assert third.span_index == 1


def test_extractor_keeps_bullet_continuation_in_same_block():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (35, 100, 280, 145),
            "lines": [
                {
                    "bbox": (35, 100, 280, 116),
                    "spans": [
                        {
                            "text": "•",
                            "size": 11.0,
                            "font": "Regular",
                            "bbox": (35, 100, 40, 116),
                            "color": 0,
                            "origin": (35, 112),
                            "flags": 0,
                        },
                        {
                            "text": "Understand what AI engineering is and how it differs",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (44, 100, 280, 116),
                            "color": 0,
                            "origin": (44, 112),
                            "flags": 0,
                        },
                    ],
                },
                {
                    "bbox": (44, 117, 250, 132),
                    "spans": [
                        {
                            "text": "from traditional machine learning engineering",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (44, 117, 250, 132),
                            "color": 0,
                            "origin": (44, 129),
                            "flags": 0,
                        }
                    ],
                },
            ],
        }
    ]
    page_mock = create_mock_page(blocks)
    page_mock.get_links.return_value = []

    page_data = extractor.extract_page(page_mock)
    bullet = next(s for s in page_data.spans if s.text == "•")
    first_line = next(s for s in page_data.spans if s.text.startswith("Understand"))
    continuation = next(s for s in page_data.spans if s.text.startswith("from traditional"))

    assert bullet.metadata["is_bullet"] is True
    assert first_line.block_index == bullet.block_index
    assert continuation.block_index == bullet.block_index


def test_extractor_merges_adjacent_raw_blocks_from_same_paragraph():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (145, 215, 432, 227),
            "lines": [
                {
                    "bbox": (145, 215, 432, 227),
                    "spans": [
                        {
                            "text": "This book offers a comprehensive guide to the essential",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (145, 215, 432, 227),
                            "color": 0,
                            "origin": (145, 227),
                            "flags": 0,
                        }
                    ],
                }
            ],
        },
        {
            "type": 0,
            "bbox": (182, 228.5, 432, 253),
            "lines": [
                {
                    "bbox": (182, 228.5, 432, 241),
                    "spans": [
                        {
                            "text": "aspects of building generative AI systems.",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (182, 228.5, 432, 241),
                            "color": 0,
                            "origin": (182, 239),
                            "flags": 0,
                        }
                    ],
                },
                {
                    "bbox": (200, 240, 432, 253),
                    "spans": [
                        {
                            "text": "A must-read for any professional.",
                            "size": 10.0,
                            "font": "Regular",
                            "bbox": (200, 240, 432, 253),
                            "color": 0,
                            "origin": (200, 252),
                            "flags": 0,
                        }
                    ],
                },
            ],
        },
        {
            "type": 0,
            "bbox": (217, 255, 432, 269),
            "lines": [
                {
                    "bbox": (217, 255, 432, 269),
                    "spans": [
                        {
                            "text": "--Vittorio Cretella, former global CIO",
                            "size": 10.0,
                            "font": "Italic",
                            "bbox": (217, 255, 432, 269),
                            "color": 0,
                            "origin": (217, 267),
                            "flags": 2,
                        }
                    ],
                }
            ],
        },
    ]
    page_mock = create_mock_page(blocks)
    page_mock.get_links.return_value = []

    page_data = extractor.extract_page(page_mock)

    first = next(s for s in page_data.spans if s.text.startswith("This book"))
    continuation = next(s for s in page_data.spans if s.text.startswith("aspects"))
    attribution = next(s for s in page_data.spans if s.text.startswith("--Vittorio"))
    assert continuation.block_index == first.block_index
    assert attribution.block_index != first.block_index


def test_extractor_does_not_merge_copyright_page_metadata_blocks():
    extractor = PDFExtractor()
    blocks = [
        {
            "type": 0,
            "bbox": (72, 58, 124, 82),
            "lines": [
                {
                    "bbox": (72, 58, 124, 70),
                    "spans": [
                        {
                            "text": "AI Engineering",
                            "size": 8.0,
                            "font": "Bold",
                            "bbox": (72, 58, 124, 70),
                            "color": 0,
                            "origin": (72, 68),
                            "flags": 16,
                        }
                    ],
                },
                {
                    "bbox": (72, 70, 124, 82),
                    "spans": [
                        {
                            "text": "by Chip Huyen",
                            "size": 8.0,
                            "font": "Regular",
                            "bbox": (72, 70, 124, 82),
                            "color": 0,
                            "origin": (72, 80),
                            "flags": 0,
                        }
                    ],
                },
            ],
        },
        {
            "type": 0,
            "bbox": (72, 87, 328, 99),
            "lines": [
                {
                    "bbox": (72, 87, 328, 99),
                    "spans": [
                        {
                            "text": (
                                "Copyright © 2025 Developer Experience Advisory LLC. "
                                "All rights reserved."
                            ),
                            "size": 8.0,
                            "font": "Regular",
                            "bbox": (72, 87, 328, 99),
                            "color": 0,
                            "origin": (72, 97),
                            "flags": 0,
                        }
                    ],
                }
            ],
        },
        {
            "type": 0,
            "bbox": (72, 103, 208, 115),
            "lines": [
                {
                    "bbox": (72, 103, 208, 115),
                    "spans": [
                        {
                            "text": "Printed in the United States of America.",
                            "size": 8.0,
                            "font": "Regular",
                            "bbox": (72, 103, 208, 115),
                            "color": 0,
                            "origin": (72, 113),
                            "flags": 0,
                        }
                    ],
                }
            ],
        },
    ]
    page_mock = create_mock_page(blocks)
    page_mock.get_links.return_value = []

    page_data = extractor.extract_page(page_mock)

    title = next(s for s in page_data.spans if s.text == "AI Engineering")
    copyright_span = next(s for s in page_data.spans if s.text.startswith("Copyright"))
    printed = next(s for s in page_data.spans if s.text.startswith("Printed"))
    assert copyright_span.block_index != title.block_index
    assert printed.block_index != copyright_span.block_index


def test_extractor_orders_merge_candidates_by_page_position_not_raw_order():
    page_data = MagicMock()
    footer = MagicMock()
    footer.block_index = 1
    footer.raw_block_index = 0
    footer.line_index = 0
    footer.bbox = (72, 556, 137, 568)
    title = MagicMock()
    title.block_index = 2
    title.raw_block_index = 2
    title.line_index = 0
    title.bbox = (72, 58, 124, 70)
    copyright_span = MagicMock()
    copyright_span.block_index = 3
    copyright_span.raw_block_index = 3
    copyright_span.line_index = 0
    copyright_span.bbox = (72, 87, 328, 99)
    page_data.spans = [footer, title, copyright_span]

    blocks = PDFExtractor._ordered_logical_blocks(page_data)

    assert blocks[0] == [title]
    assert blocks[-1] == [footer]
