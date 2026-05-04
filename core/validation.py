from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from .document_map import BBox, DocumentMap

IssueSeverity = Literal["info", "warning", "error"]


class QualityIssue(BaseModel):
    """Representação de um problema de qualidade identificado no layout ou tradução."""

    type: str
    severity: IssueSeverity
    page_number: int
    block_id: str
    span_id: str | None = None
    message: str
    bbox: BBox | None = None
    block_type: str = ""
    layout_role: str = ""
    source_text: str = ""
    translated_text: str = ""
    color_hex: str | None = None
    hyperlink_uri: str | None = None
    is_hyperlink: bool = False
    protection_reason: str = ""
    visual_category: str = ""


class QualityReport(BaseModel):
    """Relatório estruturado de auditoria de qualidade pós-tradução."""

    source_path: str
    summary: dict[str, int] = Field(default_factory=dict)
    issues: list[QualityIssue] = Field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return len(self.issues)

    @classmethod
    def from_document_map(cls, document_map: DocumentMap) -> QualityReport:
        """
        Gera um relatório de auditoria a partir do mapa estrutural do documento.
        Analisa riscos de overflow, quebra de links e integridade de termos protegidos.
        """
        # Lógica de auditoria heurística protegida no showcase
        raise NotImplementedError("Lógica de auditoria de qualidade protegida.")

    def to_json_dict(self) -> dict[str, Any]:
        """Converte o relatório para um dicionário serializável para exportação JSON."""
        payload = self.model_dump(mode="json")
        payload["total_issues"] = self.total_issues
        return payload
