import joblib
import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client():
    with TestClient(main.app) as value:
        yield value


def test_health(client):
    assert client.get('/health').json() == {'status': 'ok', 'model_version': '1.0.0'}


def test_prediction_routes(client):
    payload = {'annual_income': 60000, 'loan_amount': 10000, 'credit_score': 720}
    for route in ('/predict', '/api/v1/predictions'):
        response = client.post(route, json=payload)
        assert response.status_code == 200
        assert response.json() == {'prediction': 'approved', 'model_version': '1.0.0', 'synthetic_training_data': True}


def test_rejected_application(client):
    assert client.post('/predict', json={'annual_income': 60000, 'loan_amount': 50000, 'credit_score': 400}).json()['prediction'] == 'rejected'


def test_validation(client):
    for bad in ({'annual_income': 0, 'loan_amount': 1000, 'credit_score': 720},
                {'annual_income': 60000, 'loan_amount': 1000, 'credit_score': 900}, {}):
        assert client.post('/predict', json=bad).status_code == 422


def test_model_configuration_and_missing_file(tmp_path, monkeypatch):
    artifact = joblib.load(main.MODEL_PATH)
    artifact['version'] = '1.1.0'
    alternate = tmp_path / 'alternate.joblib'
    joblib.dump(artifact, alternate)
    monkeypatch.setattr(main, 'MODEL_PATH', str(alternate))
    with TestClient(main.app) as client:
        assert client.get('/health').json()['model_version'] == '1.1.0'
    monkeypatch.setattr(main, 'MODEL_PATH', str(tmp_path / 'missing.joblib'))
    with pytest.raises(FileNotFoundError):
        with TestClient(main.app):
            pass
