import re
from typing import Optional

# Regex para identificação de termos protegidos (tokens técnicos, URLs, etc.)
URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>()\[\]{}\"']+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
ISBN_RE = re.compile(
    r"\bISBN(?:-1[03])?:?\s*(?:97[89][-\s]?)?(?:\d[-\s]?){9,12}[\dXx]\b",
    re.IGNORECASE,
)
TECHNICAL_TOKEN_RE = re.compile(
    r"\b(?:[A-Za-z_]\w*\.[A-Za-z_]\w*|"
    r"(?=[A-Za-z0-9_]*[A-Z])[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+|"
    r"[A-Za-z]+-[A-Za-z0-9]*\d[A-Za-z0-9-]*|"
    r"[A-Za-z]*\d[A-Za-z0-9-]*|v?\d+(?:\.\d+){1,})\b"
)
PROTECTED_PLACEHOLDER_RE = re.compile(r"\[\[(P\d+)\]\]")
_TRAILING_PUNCTUATION = ".,;:)]}"


def is_equation_like(text: str) -> bool:
    """
    Verifica se o texto possui características de fórmulas matemáticas ou código.
    Implementa heurísticas baseadas em densidade de caracteres especiais e padrões matemáticos.
    """
    if not text.strip():
        return False

    math_symbols = r"∑|∏|∫|∂|∆|∇|±|∓|÷|×|√|∞|∝|∩|∪|⊂|⊃|⊆|⊇|⊕|⊗|⊥|∠|≡|≈|≠|≤|≥|≪|≫"
    math_patterns = [
        r"\d+[\^|_]\d+",  # Exponentes ou subscritos
        r"[a-z]_[i|j|k|n]",  # Variáveis indexadas comuns
        r"\\frac\{.*?\}\{.*?\}",  # Frações LaTeX simples
        r"\b(?:sin|cos|tan|lim|log|exp)\b",  # Operadores comuns com boundaries
        r"\(.*?\)\^2",  # Expressões ao quadrado
        r"[A-Z]\(.*?\|.*?\)",  # Probabilidade condicional P(A|B)
        r"[A-Z]\([A-Z]/[A-Z]\)",  # Razões simples
        r"[a-zA-Z]=\d+",  # Atribuição simples x=10
        math_symbols,
    ]

    # Se contém padrões matemáticos explícitos
    if any(re.search(pattern, text) for pattern in math_patterns):
        # Filtro de falsos positivos para símbolos monetários
        if "$" in text and re.match(r"^\$\d+(\.\d+)?\.?$", text.strip()):
            return False
        return True

    return False


def protection_reason(
    text: str,
    font_name: str = "",
    is_math: bool = False,
) -> str:
    """
    Determina o motivo pelo qual um fragmento de texto não deve ser traduzido.
    """
    if is_math:
        return "math"
    if URL_RE.search(text):
        return "url"
    if EMAIL_RE.search(text):
        return "email"
    if ISBN_RE.search(text):
        return "isbn"
    if (
        "terminal" in font_name.lower()
        or "consolas" in font_name.lower()
        or "mono" in font_name.lower()
    ):
        if "import " in text or "def " in text or "class " in text:
            return "code"
    if TECHNICAL_TOKEN_RE.search(text) and len(text) < 30:
        return "technical_token"
    if is_equation_like(text):
        return "math"

    return ""


def is_translatable(
    text: str, font_name: Optional[str] = None, is_math: Optional[bool] = None
) -> bool:
    """
    Filtro global para determinar se um span de texto deve ser enviado para tradução.
    """
    clean_text = text.strip()
    if not clean_text or len(clean_text) <= 1:
        return False

    if protection_reason(clean_text, font_name or "", is_math or False):
        return False

    return True


def protected_terms(text: str) -> list[str]:
    """
    Identifica termos protegidos dentro de uma string de texto para o showcase.
    """
    found = []
    found.extend(URL_RE.findall(text))
    found.extend(EMAIL_RE.findall(text))
    found.extend(ISBN_RE.findall(text))
    found.extend(TECHNICAL_TOKEN_RE.findall(text))
    return list(set(found))


def normalize_whitespace(text: str) -> str:
    """Remove espaços excessivos e normaliza quebras de linha para o tradutor."""
    return re.sub(r"\s+", " ", text).strip()
