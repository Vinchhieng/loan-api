from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'APPLICATION_DB_PATH', str(tmp_path / 'applications.db'))
    monkeypatch.setattr(main, 'API_KEY', '')
    with TestClient(main.app) as value:
        yield value


def create(client, borrower=1, amount=1500):
    return client.post('/api/v1/applications', json={'borrower_id': borrower, 'amount_usd': amount, 'term_months': 12})


def test_application_resource_and_decision_state(client):
    response = create(client)
    assert response.status_code == 201
    row = response.json()
    location = response.headers['location']
    assert location.endswith('/api/v1/applications/' + str(row['id']))
    assert row['status'] == 'pending'
    assert client.get(location).json() == row
    assert client.patch(location, json={'status': 'approved'}).json()['status'] == 'approved'
    assert client.patch(location, json={'status': 'rejected'}).status_code == 409
    assert client.patch(location, json={'status': 'pending'}).status_code == 422
    assert client.patch(location, json={'status': 'approved', 'amount_usd': 900}).status_code == 422


def test_cursor_and_filters(client):
    first = create(client).json()
    second = create(client).json()
    create(client, borrower=2)
    page = client.get('/api/v1/applications?province=Battambang&limit=1').json()
    assert [row['id'] for row in page['items']] == [first['id']]
    assert page['next_cursor'] == first['id']
    page = client.get('/api/v1/applications', params={'province': 'Battambang', 'after': page['next_cursor'], 'limit': 1}).json()
    assert [row['id'] for row in page['items']] == [second['id']]
    assert page['next_cursor'] is None
    assert len(client.get('/api/v1/borrowers/1/applications').json()['items']) == 2
    assert client.get('/api/v1/borrowers/4/applications').json() == {'items': [], 'next_cursor': None}
    assert client.get('/api/v1/applications', params={'province': "' OR 1=1 --"}).json()['items'] == []


@pytest.mark.parametrize('query', ['limit=0', 'limit=101', 'limit=abc', 'after=0', 'after=abc', 'status=unknown'])
def test_invalid_filters_are_400(client, query):
    assert client.get('/api/v1/applications?' + query).status_code == 400


def test_contract_validation_and_missing_resources(client):
    assert create(client, amount=99).status_code == 422
    assert create(client, amount=5001).status_code == 422
    assert create(client, borrower=999).status_code == 404
    assert client.post('/api/v1/applications', json={'borrower_id': 1, 'amount_usd': 100, 'term_months': 5}).status_code == 422
    assert client.get('/api/v1/applications/999').status_code == 404
    assert client.get('/api/v1/borrowers/999/applications').status_code == 404
    assert client.post('/api/v1/applications/999/predictions').status_code == 404


@pytest.mark.parametrize('term', [3, 6, 12, 18, 24])
def test_all_supported_terms(client, term):
    response = client.post('/api/v1/applications', json={'borrower_id': 1, 'amount_usd': 1500, 'term_months': term})
    assert response.status_code == 201
    assert response.json()['term_months'] == term


def test_registered_champion_matches_module5_probability(client):
    row = create(client).json()
    response = client.post(f"/api/v1/applications/{row['id']}/predictions")
    assert response.status_code == 201
    prediction = response.json()
    assert prediction['model_version'] == '1'
    assert prediction['application_id'] == row['id']
    assert prediction['default_probability'] == pytest.approx(0.27825003205504184, abs=1e-12)


def test_application_list_key_checks(client, monkeypatch):
    monkeypatch.setattr(main, 'API_KEY', 'test-only-key')
    route = '/api/v1/applications'
    assert client.get('/health').status_code == 200
    assert client.get(route).status_code == 401
    assert client.get(route, headers={'X-API-Key': 'wrong'}).status_code == 401
    assert client.get(route, headers={'X-API-Key': 'test-only-key'}).status_code == 200


def test_application_survives_process_restart(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'APPLICATION_DB_PATH', str(tmp_path / 'restart.db'))
    monkeypatch.setattr(main, 'API_KEY', '')
    with TestClient(main.app) as client:
        application_id = create(client).json()['id']
    with TestClient(main.app) as restarted:
        assert restarted.get(f'/api/v1/applications/{application_id}').status_code == 200


def test_concurrent_decisions_only_allow_one_winner(client):
    application_id = create(client).json()['id']
    path = f'/api/v1/applications/{application_id}'
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(lambda status: client.patch(path, json={'status': status}).status_code, ['approved', 'rejected']))
    assert sorted(statuses) == [200, 409]


def test_module2_operation_paths_are_documented(client):
    paths = client.get('/openapi.json').json()['paths']
    expected = {'/api/v1/applications': {'get', 'post'}, '/api/v1/applications/{application_id}': {'get', 'patch'},
                '/api/v1/borrowers/{borrower_id}/applications': {'get'}, '/api/v1/applications/{application_id}/predictions': {'post'}}
    for path, methods in expected.items():
        assert methods <= set(paths[path])
