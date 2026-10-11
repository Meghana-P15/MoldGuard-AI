from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def _payload():
    meta = client.get('/api/meta').json()
    return {
        'machine': meta['machines'][0],
        'material': meta['materials'][0],
        **meta['defaults'],
        'cycles': 1000,
        'part_weight_g': meta['part_weight']['median_g'],
    }


def test_health_real_data_only():
    response = client.get('/health')
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'ok'
    assert body['synthetic_data_used'] is False
    assert body['datasets'] == ['modelo.xlsx', 'test_dataset.csv']
    assert body['risk_model_type'] == 'defect_rate_regression_with_thresholds'


def test_meta_contains_real_options_and_tmold():
    response = client.get('/api/meta')
    assert response.status_code == 200
    body = response.json()
    assert body['machines']
    assert body['materials']
    assert set(body['defaults']) == {'Tinj', 'tinj', 'Pinj', 'Ph', 'Tmold', 'th'}
    assert body['risk_thresholds']['good_max'] < body['risk_thresholds']['warning_max']


def test_analyze_end_to_end():
    response = client.post('/api/analyze', json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body['batch_decision'] in {'GOOD', 'WARNING', 'HIGH_RISK', 'REVIEW_REQUIRED'}
    assert body['prediction'] in {'G', 'Y', 'R'}
    assert body['predicted_defect_rate'] >= 0
    assert body['model_mode'] == 'real_data_only'
    assert body['data_sources'] == ['modelo.xlsx', 'test_dataset.csv']
    assert body['optimization']['candidate_search']['generated'] == 1800
    assert body['energy']['predicted_power_watts'] > 0
    assert isinstance(body['evidence'], list)
    assert body['rag_backend'] in {'sentence-transformers+faiss', 'tfidf-fallback'}


def test_validation_rejects_unknown_machine():
    payload = _payload()
    payload['machine'] = 'NOT-A-REAL-MACHINE'
    response = client.post('/api/analyze', json=payload)
    assert response.status_code == 422


def test_history_records_analysis():
    client.post('/api/analyze', json=_payload())
    response = client.get('/api/history?limit=5')
    assert response.status_code == 200
    assert response.json()['items']
