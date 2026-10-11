import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from ai.moldguard_ai.config import FEATURE_LABELS, FEATURE_UNITS, PARAM_BOUNDS
from backend.app.config import settings
from backend.app.schemas import AnalyzeResponse, BatchInput, OptimizeResponse, PredictResponse
from backend.app.services.history_service import HistoryService
from backend.app.services.knowledge_service import KnowledgeService
from backend.app.services.model_service import ModelService
from backend.app.services.monitoring_service import MonitoringService
from backend.app.services.orchestration_service import OrchestrationService

app = FastAPI(
    title="MoldGuard AI API",
    version="3.0.0",
    description=(
        "Real-data injection-molding decision support: defect-rate XGBoost regression with explicit "
        "risk thresholds, OOD Isolation Forest, real electrical energy XGBoost, constrained optimization, "
        "semantic RAG evidence, structured monitoring and history."
    ),
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def observability(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["x-request-id"] = request_id
        return response
    except Exception as exc:
        MonitoringService.error(
            "api_exception",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            error=str(exc),
        )
        MonitoringService.metric("ApiErrorCount", 1, Path=request.url.path)
        raise
    finally:
        latency_ms = (time.perf_counter() - started) * 1000.0
        MonitoringService.log(
            "api_request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            latency_ms=round(latency_ms, 3),
        )
        MonitoringService.metric(
            "ApiLatencyMs", latency_ms, unit="Milliseconds", Path=request.url.path
        )
        if status_code >= 500:
            MonitoringService.metric("Api5xxCount", 1, Path=request.url.path)


@app.get("/")
def root():
    return {"name": "MoldGuard AI", "version": "3.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    try:
        bundle = ModelService.bundle()
        return {
            "status": "ok",
            "model_mode": bundle.model_mode,
            "synthetic_data_used": bundle.metadata.get("synthetic_data_used"),
            "datasets": bundle.metadata.get("raw_datasets", []),
            "risk_model_type": bundle.metadata.get("risk_model_type"),
            "rag_backend": KnowledgeService.backend_name(),
            "cloudwatch_metrics_enabled": settings.enable_cloudwatch_metrics,
        }
    except Exception as exc:
        return {"status": "degraded", "error": str(exc)}


@app.get("/api/meta")
def meta():
    bundle = ModelService.bundle()
    md = bundle.metadata
    defaults = {
        feature: round(float(md["feature_stats"][feature]["median"]), 3)
        for feature in md.get("feature_stats", {})
    }
    return {
        "machines": md.get("known_machines", []),
        "materials": md.get("energy_material_profiles", []),
        "part_weight": md.get("part_weight", {}),
        "defaults": defaults,
        "parameter_bounds": PARAM_BOUNDS,
        "feature_labels": FEATURE_LABELS,
        "feature_units": FEATURE_UNITS,
        "datasets": md.get("raw_datasets", []),
        "energy_machine_names": md.get("energy_machine_names", []),
        "risk_model_type": md.get("risk_model_type"),
        "risk_thresholds": md.get("defect_thresholds", {}),
        "defect_model_metrics": {
            "mae_percentage_points": md.get("defect_validation_mae", 0.0) * 100.0,
            "r2": md.get("defect_r2"),
        },
        "energy_model_metrics": {
            "mae_watts": md.get("energy_validation_mae_watts"),
            "r2": md.get("energy_r2"),
        },
        "rag_backend": KnowledgeService.backend_name(),
        "model_mode": bundle.model_mode,
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(batch: BatchInput):
    try:
        result = OrchestrationService.analyze(batch)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    HistoryService.save("analyze", batch.model_dump(), result)
    return result


@app.post("/api/predict", response_model=PredictResponse)
def predict(batch: BatchInput):
    try:
        ModelService.validate_context(batch.machine, batch.material)
        bundle = ModelService.bundle()
        risk = bundle.predict_risk(batch.model_params())
        energy = bundle.predict_energy(batch.model_params(), batch.material)
        result = {
            "prediction": risk["prediction"],
            "risk_level": risk["risk_level"],
            "predicted_defect_rate": round(float(risk["predicted_defect_rate"]), 6),
            "predicted_defect_percent": round(float(risk["predicted_defect_percent"]), 4),
            "defect_uncertainty_percentage_points": round(
                float(risk["uncertainty_percentage_points"]), 4
            ),
            "top_risk_factors": risk["top_risk_factors"],
            "predicted_energy": round(float(energy["kwh_per_cycle"]), 8),
            "projected_energy": round(float(energy["kwh_per_cycle"] * batch.cycles), 5),
            "model_mode": bundle.model_mode,
            "note": (
                "Defect-rate/OOD models use real modelo.xlsx measurements; energy uses real "
                "test_dataset.csv telemetry. The datasets are not falsely row-wise paired."
            ),
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    HistoryService.save("predict", batch.model_dump(), result)
    return result


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize(batch: BatchInput):
    try:
        full = OrchestrationService.analyze(batch)
        result = dict(full["optimization"])
        result["projected"] = {
            "cycles": batch.cycles,
            "current_energy": full["energy"]["current_batch_kwh"],
            "optimized_energy": full["energy"]["optimized_batch_kwh"],
            "energy_saved": full["impact"]["energy_reduction_kwh"],
        }
        result["model_mode"] = full["model_mode"]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    HistoryService.save("optimize", batch.model_dump(), result)
    return result


@app.get("/api/history")
def history(limit: int = Query(20, ge=1, le=100)):
    return {"items": HistoryService.list(limit)}
