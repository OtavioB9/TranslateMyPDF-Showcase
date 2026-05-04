"""
Testes de API para os endpoints de visualização e processamento do LayrPDF.
Valida o ciclo de vida do upload, geração de preview e relatórios de qualidade.
"""

import json
import os
from pathlib import Path

import fitz
from fastapi.testclient import TestClient

import api_server


def test_root_endpoint_returns_api_status():
    """Verifica se o endpoint raiz responde com o status e versão da API."""
    client = TestClient(api_server.app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "LayrPDF API",
        "status": "ok",
        "health_url": "/health",
    }


def _write_pdf(path: Path, text: str) -> None:
    """Função auxiliar para criar um PDF minimalista para testes de I/O."""
    doc = fitz.open()
    page = doc.new_page(width=240, height=180)
    page.insert_text((24, 48), text)
    doc.save(path)
    doc.close()


def test_preview_info_returns_original_page_count(tmp_path, monkeypatch):
    """Valida se o endpoint de info retorna a contagem correta de páginas do documento original."""
    monkeypatch.setattr(api_server, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(api_server, "OUTPUT_DIR", tmp_path / "output")
    api_server.UPLOAD_DIR.mkdir()
    api_server.OUTPUT_DIR.mkdir()
    api_server.jobs.clear()

    job_id = "job-info"
    filename = "sample.pdf"
    _write_pdf(api_server.UPLOAD_DIR / f"{job_id}_{filename}", "Original")
    api_server.jobs[job_id] = {"id": job_id, "filename": filename, "status": "pending"}

    client = TestClient(api_server.app)
    response = client.get(f"/preview/{job_id}/info")

    assert response.status_code == 200
    assert response.json() == {"page_count": 1}


def test_upload_returns_total_pages_for_selected_pdf(tmp_path, monkeypatch):
    """Verifica se o upload de um arquivo PDF registra o job corretamente e retorna o total de páginas."""
    monkeypatch.setattr(api_server, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(api_server, "OUTPUT_DIR", tmp_path / "output")
    api_server.UPLOAD_DIR.mkdir()
    api_server.OUTPUT_DIR.mkdir()
    api_server.jobs.clear()

    pdf_path = tmp_path / "sample.pdf"
    _write_pdf(pdf_path, "Original")

    client = TestClient(api_server.app)
    with pdf_path.open("rb") as pdf:
        response = client.post(
            "/upload",
            files={"file": ("sample.pdf", pdf, "application/pdf")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total_pages"] == 1
    assert api_server.jobs[body["job_id"]]["total_pages"] == 1


def test_preview_renders_original_and_translated_png(tmp_path, monkeypatch):
    """Garante que o preview de páginas individuais renderiza imagens PNG tanto para original quanto traduzido."""
    monkeypatch.setattr(api_server, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(api_server, "OUTPUT_DIR", tmp_path / "output")
    api_server.UPLOAD_DIR.mkdir()
    api_server.OUTPUT_DIR.mkdir()
    api_server.jobs.clear()

    job_id = "job-preview"
    filename = "sample.pdf"
    _write_pdf(api_server.UPLOAD_DIR / f"{job_id}_{filename}", "Original")
    _write_pdf(api_server.OUTPUT_DIR / f"translated_{job_id}_{filename}", "Traduzido")
    api_server.jobs[job_id] = {"id": job_id, "filename": filename, "status": "completed"}

    client = TestClient(api_server.app)

    original = client.get(f"/preview/{job_id}/0?version=original")
    translated = client.get(f"/preview/{job_id}/0?version=translated")

    assert original.status_code == 200
    assert original.headers["content-type"] == "image/png"
    assert original.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert translated.status_code == 200
    assert translated.headers["content-type"] == "image/png"
    assert translated.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_preview_translated_returns_404_before_output_exists(tmp_path, monkeypatch):
    """Verifica se o preview traduzido retorna 404 caso o processamento ainda não tenha gerado o arquivo de saída."""
    monkeypatch.setattr(api_server, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(api_server, "OUTPUT_DIR", tmp_path / "output")
    api_server.UPLOAD_DIR.mkdir()
    api_server.OUTPUT_DIR.mkdir()
    api_server.jobs.clear()

    job_id = "job-missing-output"
    filename = "sample.pdf"
    _write_pdf(api_server.UPLOAD_DIR / f"{job_id}_{filename}", "Original")
    api_server.jobs[job_id] = {"id": job_id, "filename": filename, "status": "processing"}

    client = TestClient(api_server.app)
    response = client.get(f"/preview/{job_id}/0?version=translated")

    assert response.status_code == 404


def test_quality_endpoint_returns_generated_report(tmp_path, monkeypatch):
    """Valida se o endpoint de qualidade retorna o JSON do relatório de auditoria gerado pelo motor LayrPDF."""
    monkeypatch.setattr(api_server, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(api_server, "OUTPUT_DIR", tmp_path / "output")
    api_server.UPLOAD_DIR.mkdir()
    api_server.OUTPUT_DIR.mkdir()
    api_server.jobs.clear()

    job_id = "job-quality"
    filename = "sample.pdf"
    report_path = api_server.OUTPUT_DIR / f"translated_{job_id}_{filename}"
    report_payload = {
        "source_path": "input.pdf",
        "summary": {"pages": 1},
        "issues": [],
        "total_issues": 0,
        "issue_count_by_type": {},
        "pages_with_risk": [],
    }
    report_path.with_suffix(".quality.json").write_text(
        json.dumps(report_payload),
        encoding="utf-8",
    )
    api_server.jobs[job_id] = {"id": job_id, "filename": filename, "status": "completed"}

    client = TestClient(api_server.app)
    response = client.get(f"/quality/{job_id}")

    assert response.status_code == 200
    assert response.json() == report_payload


def test_quality_endpoint_returns_404_before_report_exists(tmp_path, monkeypatch):
    """Garante que o endpoint de qualidade retorna 404 quando o relatório ainda não foi gerado."""
    monkeypatch.setattr(api_server, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(api_server, "OUTPUT_DIR", tmp_path / "output")
    api_server.UPLOAD_DIR.mkdir()
    api_server.OUTPUT_DIR.mkdir()
    api_server.jobs.clear()

    job_id = "job-quality-missing"
    filename = "sample.pdf"
    api_server.jobs[job_id] = {"id": job_id, "filename": filename, "status": "processing"}

    client = TestClient(api_server.app)
    response = client.get(f"/quality/{job_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Relatorio de qualidade nao encontrado."


def test_latest_quality_endpoint_returns_newest_report(tmp_path, monkeypatch):
    """Verifica se o endpoint 'latest' retorna o relatório de qualidade com o timestamp mais recente."""
    monkeypatch.setattr(api_server, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(api_server, "OUTPUT_DIR", tmp_path / "output")
    api_server.UPLOAD_DIR.mkdir()
    api_server.OUTPUT_DIR.mkdir()
    api_server.jobs.clear()

    old_report = api_server.OUTPUT_DIR / "translated_old.quality.json"
    new_report = api_server.OUTPUT_DIR / "translated_new.quality.json"
    old_report.write_text(json.dumps({"total_issues": 3}), encoding="utf-8")
    new_report.write_text(json.dumps({"total_issues": 1}), encoding="utf-8")
    os.utime(old_report, (1000, 1000))
    os.utime(new_report, (2000, 2000))

    client = TestClient(api_server.app)
    response = client.get("/quality/latest")

    assert response.status_code == 200
    assert response.json()["total_issues"] == 1


def test_latest_quality_endpoint_returns_404_without_reports(tmp_path, monkeypatch):
    """Garante que o endpoint 'latest' retorna 404 quando não existem relatórios no diretório de saída."""
    monkeypatch.setattr(api_server, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(api_server, "OUTPUT_DIR", tmp_path / "output")
    api_server.UPLOAD_DIR.mkdir()
    api_server.OUTPUT_DIR.mkdir()
    api_server.jobs.clear()

    client = TestClient(api_server.app)
    response = client.get("/quality/latest")

    assert response.status_code == 404
    assert response.json()["detail"] == "Nenhum relatorio de qualidade encontrado."
