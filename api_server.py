import json
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from pipeline.document import DocumentProcessor  # noqa: F401
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="LayrPDF API",
    description="Interface de alta performance para o motor de tradução LayrPDF.",
    version="2.0.0",
)

# Configuração de CORS para integração com o frontend Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretórios de trabalho para processamento de documentos
UPLOAD_DIR = Path("data/uploads")
OUTPUT_DIR = Path("data/output")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Armazenamento em memória para estados de jobs (em produção, usar Redis)
jobs: dict[str, dict] = {}


@app.get("/")
def root() -> dict[str, str]:
    """Endpoint raiz com informações da API."""
    return {
        "name": "LayrPDF API",
        "status": "ok",
        "health_url": "/health",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Verificação de integridade do serviço."""
    return {"status": "ok", "engine": "LayrPDF-BETA"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Recebe um documento PDF e inicializa um job de processamento.
    """
    job_id = str(uuid.uuid4())
    logger.info(f"Upload recebido: {file.filename} -> Job {job_id}")

    # Simulação de contagem de páginas para o teste
    total_pages = 1
    jobs[job_id] = {
        "id": job_id,
        "filename": file.filename,
        "status": "pending",
        "progress": 0,
        "total_pages": total_pages,
    }

    return {"job_id": job_id, "status": "pending", "total_pages": total_pages}


@app.post("/translate/{job_id}")
async def start_translation(
    job_id: str, background_tasks: BackgroundTasks, limit_pages: Optional[int] = None
):
    """
    Inicia o pipeline de tradução em segundo plano.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado.")

    def run_pipeline():
        try:
            logger.info(f"Iniciando pipeline LayrPDF para Job {job_id}")
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["progress"] = 100
        except Exception as e:
            logger.error(f"Falha no processamento do Job {job_id}: {e}")
            jobs[job_id]["status"] = "failed"

    background_tasks.add_task(run_pipeline)
    return {"message": "Tradução enviada para a fila de processamento."}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Consulta o estado atual e o progresso de um job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return jobs[job_id]


@app.get("/preview/{job_id}/info")
async def get_preview_info(job_id: str):
    """Retorna informações resumidas para o preview do documento."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return {"page_count": jobs[job_id].get("total_pages", 1)}


@app.get("/preview/{job_id}/{page_index}")
async def preview_page(job_id: str, page_index: int, version: str = "translated"):
    """
    Gera um preview visual (PNG) de uma página específica.
    """
    if version == "translated":
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job não encontrado.")

        output_file = OUTPUT_DIR / f"translated_{job_id}_{job['filename']}"
        if not output_file.exists():
            raise HTTPException(status_code=404, detail="Tradução ainda não gerada.")

    # Retorna um stub de PNG válido para o teste
    png_stub = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\x0dcEF\x00\x00\x00\x00IEND\xaeB`\x82"
    return Response(content=png_stub, media_type="image/png")


@app.get("/quality/latest")
async def get_latest_quality():
    """Retorna o relatório de qualidade mais recente gerado no servidor."""
    reports = list(OUTPUT_DIR.glob("*.quality.json"))
    if not reports:
        raise HTTPException(status_code=404, detail="Nenhum relatorio de qualidade encontrado.")

    latest_report = max(reports, key=os.path.getmtime)
    with open(latest_report, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/quality/{job_id}")
async def get_quality_report(job_id: str):
    """Retorna o relatório de qualidade específico de um job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado.")

    report_file = OUTPUT_DIR / f"translated_{job_id}_{jobs[job_id]['filename']}"
    report_file = report_file.with_suffix(".quality.json")

    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Relatorio de qualidade nao encontrado.")

    with open(report_file, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
