"""
test_db_chunking.py — Verifica que get_translations_bulk não estoura o limite
de variáveis do SQLite com inputs maiores que 900 itens.
"""

from pathlib import Path

from database.db import TranslationDatabase


def _make_db(tmp_path: Path) -> TranslationDatabase:
    db_path = tmp_path / "test_cache.db"
    return TranslationDatabase(db_path)


def test_bulk_lookup_above_sqlite_limit(tmp_path):
    """950 textos únicos não devem lançar OperationalError."""
    db = _make_db(tmp_path)

    source, target = "en", "pt"
    batch = {f"text_{i}": f"texto_{i}" for i in range(950)}
    db.save_batch(source, target, batch)

    texts = list(batch.keys())
    result = db.get_translations_bulk(source, target, texts)

    assert len(result) == 950, (
        f"Esperado 950 resultados, obtido {len(result)}. "
        "Chunking provavelmente falhou ou silenciou exceção."
    )
    assert result["text_0"] == "texto_0"
    assert result["text_499"] == "texto_499"
    assert result["text_949"] == "texto_949"


def test_bulk_lookup_exactly_at_chunk_boundary(tmp_path):
    """900 textos — exatamente o tamanho do chunk — sem divisão extra."""
    db = _make_db(tmp_path)
    batch = {f"word_{i}": f"palavra_{i}" for i in range(900)}
    db.save_batch(source="en", target="pt", translation_dict=batch)

    result = db.get_translations_bulk("en", "pt", list(batch.keys()))
    assert len(result) == 900


def test_bulk_lookup_empty_input(tmp_path):
    """Input vazio deve retornar dict vazio sem exceção."""
    db = _make_db(tmp_path)
    result = db.get_translations_bulk("en", "pt", [])
    assert result == {}


def test_bulk_lookup_partial_cache_hit(tmp_path):
    """Textos não-cacheados são simplesmente ausentes no resultado — sem KeyError."""
    db = _make_db(tmp_path)
    db.save_batch("en", "pt", {"hello": "olá"})

    result = db.get_translations_bulk("en", "pt", ["hello", "world"])
    assert result.get("hello") == "olá"
    assert "world" not in result
