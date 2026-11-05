import joblib
import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(main, 'API_KEY', '')
    monkeypatch.setattr(main, 'APPLICATION_DB_PATH', str(tmp_path / 'applications.db'))
    with TestClient(main.app) as value:
        yield value


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    body = response.json()
    assert {key: body[key] for key in ('status', 'model_version', 'git_sha')} == {'status': 'ok', 'model_version': '1.0.0', 'git_sha': main.GIT_SHA}
    assert body['champion']['version'] == '1'
    assert body['champion']['run_id'] == '4e001c82aed946b8a11950c3b7278761'


def test_api_key_and_legacy_route(client, monkeypatch):
    monkeypatch.setattr(main, 'API_KEY', 'unit-test-only')
    payload = {'annual_income': 60000, 'loan_amount': 10000, 'credit_score': 720}
    assert client.get('/health').status_code == 200
    for route in ('/predict', '/api/v1/predictions'):
        assert client.post(route, json=payload).status_code == 401
        assert client.post(route, json=payload, headers={'x-api-key': 'wrong'}).status_code == 401
        assert client.post(route, json=payload, headers={'x-api-key': 'unit-test-only'}).status_code == 200


def test_health_reports_release_sha(client, monkeypatch):
    monkeypatch.setattr(main, 'GIT_SHA', 'a' * 40)
    assert client.get('/health').json()['git_sha'] == 'a' * 40


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
    monkeypatch.setattr(main, 'APPLICATION_DB_PATH', str(tmp_path / 'applications.db'))
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
