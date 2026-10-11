from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.schemas import (
    BatchInput,
    PredictResponse,
    OptimizeResponse,
    AnalyzeResponse,
    AgentRunRequest,
    AgentRunResponse,
)
from backend.app.services.model_service import ModelService
from backend.app.services.history_service import HistoryService
from backend.app.services.knowledge_service import KnowledgeService
from backend.app.services.agent_service import AgentService
from agentic.schemas import AgentRequest, AgentBatch

app = FastAPI(
    title="MoldGuard AI API",
    version="3.0.0",
    description=(
        "Injection-molding decision-support API with deterministic ML, "
        "constrained optimization, RAG and optional AgentCore/Strands orchestration."
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


@app.get("/")
def root():
    return {
        "name": "MoldGuard AI",
        "version": "3.0.0",
        "message": "Prevent scrap before production.",
        "agent_mode": settings.agent_mode,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    try:
        bundle = ModelService.bundle()
        kb = KnowledgeService.instance()
        return {
            "status": "ok",
            "model_mode": bundle.model_mode,
            "knowledge_documents": len(kb.docs),
            "retrieval_mode": kb.mode,
            "agent_mode": settings.agent_mode,
            "agentcore_configured": bool(settings.agentcore_runtime_arn),
        }
    except Exception as exc:
        return {"status": "degraded", "error": str(exc)}


@app.post("/api/predict", response_model=PredictResponse)
def predict(batch: BatchInput):
    result = ModelService.predict(
        batch.model_params(),
        batch.cycles,
        batch.part_weight_g,
    )
    HistoryService.save("predict", batch.model_dump(), result)
    return result


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize(batch: BatchInput):
    result = ModelService.optimize(
        batch.model_params(),
        batch.cycles,
        batch.part_weight_g,
    )
    HistoryService.save("optimize", batch.model_dump(), result)
    return result


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(batch: BatchInput):
    result = ModelService.analyze(
        batch.model_params(),
        batch.cycles,
        batch.part_weight_g,
    )
    pred = result["prediction"]
    top = ", ".join(x["feature"] for x in pred.get("top_risk_factors", []))
    query = (
        f"Injection molding recommendation for {batch.material_code or 'material'}; "
        f"predicted class {pred['prediction']}; decision {pred['decision']}; "
        f"main drivers {top}. What validated process guidance should the operator review?"
    )
    result["evidence"] = KnowledgeService.instance().retrieve(query, k=3)
    HistoryService.save("analyze", batch.model_dump(), result)
    return result


@app.post("/api/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest):
    agent_request = AgentRequest(
        objective=request.objective,
        batch=AgentBatch(**request.batch.model_dump()),
    )
    result = AgentService.run(agent_request)
    HistoryService.save("agent_run", request.model_dump(), result)
    return result


@app.get("/api/knowledge")
def knowledge(query: str = Query(..., min_length=3), k: int = Query(3, ge=1, le=8)):
    return {
        "query": query,
        "items": KnowledgeService.instance().retrieve(query, k=k),
    }


@app.get("/api/history")
def history(limit: int = Query(20, ge=1, le=100)):
    return {"items": HistoryService.list(limit)}
