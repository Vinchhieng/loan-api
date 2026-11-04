from fastapi.testclient import TestClient
from main import app


def test_prediction_and_validation():
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        assert client.post('/predict', json={'annual_income': 60000, 'loan_amount': 10000, 'credit_score': 720}).json()['prediction'] == 'approved'
        assert client.post('/predict', json={'annual_income': 60000, 'loan_amount': 50000, 'credit_score': 720}).json()['prediction'] == 'rejected'
        assert client.post('/predict', json={'annual_income': 0, 'loan_amount': 10000, 'credit_score': 720}).status_code == 422
