from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.schemas import BatchInput, PredictResponse, OptimizeResponse
from backend.app.services.model_service import ModelService
from backend.app.services.history_service import HistoryService

app = FastAPI(
    title="MoldGuard AI API",
    version="1.0.0",
    description="Injection-molding scrap-risk, energy, explanation and optimization API.",
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "MoldGuard AI",
        "message": "Prevent scrap before production.",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    try:
        bundle = ModelService.bundle()
        return {"status": "ok", "model_mode": bundle.model_mode}
    except Exception as exc:
        return {"status": "degraded", "error": str(exc)}


@app.post("/api/predict", response_model=PredictResponse)
def predict(batch: BatchInput):
    result = ModelService.predict(batch.model_params(), batch.cycles)
    HistoryService.save("predict", batch.model_dump(), result)
    return result


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize(batch: BatchInput):
    result = ModelService.optimize(batch.model_params(), batch.cycles)
    HistoryService.save("optimize", batch.model_dump(), result)
    return result


@app.get("/api/history")
def history(limit: int = Query(20, ge=1, le=100)):
    return {"items": HistoryService.list(limit)}
