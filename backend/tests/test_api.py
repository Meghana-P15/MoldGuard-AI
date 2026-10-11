from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

VALID = {
    "Tinj": 230,
    "tinj": 1.5,
    "Pinj": 32,
    "Ph": 18,
    "Bp": 22,
    "th": 6,
    "cycles": 10000,
    "part_weight_g": 18.5,
    "material_code": "PP",
    "machine_id": "DEMO-01",
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()


def test_predict():
    r = client.post("/api/predict", json=VALID)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["prediction"] in {"G", "Y", "R"}
    assert body["decision"] in {"LOW_RISK", "REVIEW_REQUIRED", "HIGH_RISK"}
    assert set(body["probabilities"]) == {"G", "Y", "R"}
    assert body["predicted_energy"] > 0
    assert "distribution" in body
    assert "material_impact" in body


def test_optimize():
    r = client.post("/api/optimize", json=VALID)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "recommended_parameters" in body
    assert "projected" in body
    assert "guardrail" in body
    assert "material_impact" in body


def test_analyze():
    r = client.post("/api/analyze", json=VALID)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "run_id" in body
    assert "prediction" in body
    assert "optimization" in body
    assert "evidence" in body


def test_knowledge():
    r = client.get("/api/knowledge", params={"query": "holding pressure process guidance"})
    assert r.status_code == 200
    assert "items" in r.json()


def test_invalid_bounds():
    bad = {**VALID, "Tinj": 999}
    r = client.post("/api/predict", json=bad)
    assert r.status_code == 422


def test_agent_run_local():
    payload = {
        "objective": "Evaluate this planned batch and reduce waste if justified.",
        "batch": VALID,
    }
    r = client.post("/api/agent/run", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["mode"] == "local-deterministic-orchestrator"
    assert body["human_review_required"] is True
    assert body["decision"] in {"REVIEW_REQUIRED", "RECOMMEND_WITH_REVIEW"}
    assert "quality" in body
    assert "optimization" in body
    assert "safety" in body
    assert len(body["timeline"]) >= 5
