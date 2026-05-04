from dataclasses import dataclass


@dataclass(frozen=True)
class TocEntry:
    """Representação de uma entrada de Sumário (TOC) decomposta."""

    prefix: str
    title: str
    page: str
    has_leaders: bool = True


def split_toc_entry(text: str) -> TocEntry | None:
    """
    Decompõe uma linha de texto em componentes de sumário (ex: "1. Intro....10").
    Utiliza regex determinística para separar prefixo numérico, título e numeração.
    """
    # Lógica de decomposição de TOC protegida no showcase
    raise NotImplementedError("Lógica de análise de TOC protegida.")


def compose_toc_entry(
    prefix: str,
    translated_title: str,
    page: str,
    has_leaders: bool = True,
) -> str:
    """
    Reconstrói uma linha de sumário após a tradução do título.
    Preserva o estilo original (pontilhados/espaçamentos) e a numeração da página.
    """
    # Lógica de reconstrução visual de TOC protegida no showcase
    raise NotImplementedError("Lógica de reconstrução de TOC protegida.")
