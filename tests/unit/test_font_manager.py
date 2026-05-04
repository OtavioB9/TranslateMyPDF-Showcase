"""
Gerenciamento e mapeamento de fontes (FontManager).
Valida a lógica de substituição de fontes proprietárias por alternativas
open-source equivalentes (família Noto), preservando o estilo visual.
"""

from pathlib import Path

from core.font_manager import FontManager


def test_font_manager_maps_cover_sans_fonts_to_sans_family():
    manager = FontManager(Path(__file__).parents[2] / "fonts")

    assert manager.resolve_font("Gilroy-SemiBold", 0) == "NotoSansBold"
    assert manager.resolve_font("GuardianSansNarrow-Regul", 0) == "NotoSans"
