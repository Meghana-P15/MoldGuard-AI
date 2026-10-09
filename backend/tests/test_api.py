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
    assert set(body["probabilities"]) == {"G", "Y", "R"}
    assert body["predicted_energy"] > 0


def test_optimize():
    r = client.post("/api/optimize", json=VALID)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "recommended_parameters" in body
    assert "projected" in body


def test_invalid_bounds():
    bad = {**VALID, "Tinj": 999}
    r = client.post("/api/predict", json=bad)
    assert r.status_code == 422
