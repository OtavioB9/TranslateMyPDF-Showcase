from __future__ import annotations

from pathlib import Path

import fitz

from core.document_map import DocumentMap
from core.extractor import PDFExtractor
from core.models import PageData


class CoordinateMapBuilder:
    """
    Construtor do DocumentMap canônico a partir de um PDF de origem.
    Responsável por extrair a geometria completa do documento e encapsulá-la
    em uma estrutura hierárquica serializável.
    """

    def __init__(self, extractor: PDFExtractor | None = None) -> None:
        self.extractor = extractor or PDFExtractor()

    def build(self, input_path: Path, limit_pages: int | None = None) -> DocumentMap:
        """
        Extrai a geometria do PDF e retorna um DocumentMap consolidado.
        """
        pages: list[PageData] = []
        doc = fitz.open(str(input_path))
        try:
            if doc.needs_pass:
                raise ValueError("PDF criptografado requer senha para mapeamento.")

            page_count = len(doc)
            actual_total = min(page_count, limit_pages) if limit_pages is not None else page_count
            for page_index in range(max(actual_total, 0)):
                page = doc[page_index]
                # Extração vetorial da geometria da página
                page_data = self.extractor.extract_page(page)
                page_data.rotation = int(page.rotation)
                pages.append(page_data)

            metadata = {
                str(key): str(value)
                for key, value in dict(doc.metadata or {}).items()
                if value is not None
            }
        finally:
            doc.close()

        return DocumentMap.from_pages(str(input_path), pages, metadata=metadata)
