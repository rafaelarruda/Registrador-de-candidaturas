from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import router


app = FastAPI(
    title="Rastreador de Candidaturas",
    description="API para acompanhar vagas, etapas e anotações das suas candidaturas.",
    version="0.1.0",
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.include_router(router, prefix="/api")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health", tags=["saúde"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
