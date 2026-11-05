import json

import pytest

from scripts import deploy_render


@pytest.fixture
def deployment_env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    values = {'RENDER_API_KEY': 'test-render-credential', 'API_KEY': 'test-service-credential',
              'RENDER_OWNER_ID': 'tea-example', 'RELEASE_SHA': 'a' * 40,
              'GITHUB_OUTPUT': str(tmp_path / 'output')}
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return tmp_path


def service(repo=deploy_render.REPOSITORY):
    return {'id': 'srv-example', 'name': deploy_render.SERVICE_NAME, 'repo': repo,
            'type': 'web_service', 'branch': 'main', 'autoDeployTrigger': 'off',
            'serviceDetails': {'url': 'https://capstone.example.com'}}


def test_refuses_to_deploy_other_repository(deployment_env, monkeypatch):
    calls = []

    def api(path, method='GET', payload=None):
        calls.append(method)
        return [{'service': service('https://github.com/someone/other')}]

    monkeypatch.setattr(deploy_render, 'render_request', api)
    with pytest.raises(SystemExit, match='does not match'):
        deploy_render.deploy()
    assert calls == ['GET']


def test_pipeline_provisions_free_service_and_keeps_credentials_private(deployment_env, monkeypatch, capsys):
    calls = []

    def api(path, method='GET', payload=None):
        calls.append((path, method, payload))
        if method == 'GET':
            return []
        if path == '/services':
            return {'service': service()}
        return {'id': 'dep-example'}

    monkeypatch.setattr(deploy_render, 'render_request', api)
    deploy_render.deploy()
    creation = calls[1][2]
    assert creation['serviceDetails']['plan'] == 'free'
    assert creation['autoDeployTrigger'] == 'off'
    assert creation['envVars'] == [{'key': 'API_KEY', 'value': 'test-service-credential'}]
    assert calls[2][2] == {'commitId': 'a' * 40}
    evidence = json.loads((deployment_env / 'deployment-request.json').read_text())
    assert evidence['service_created_by_pipeline'] is True
    public_output = capsys.readouterr().out + (deployment_env / 'deployment-request.json').read_text() + (deployment_env / 'output').read_text()
    assert 'test-render-credential' not in public_output
    assert 'test-service-credential' not in public_output


def test_no_creation_without_credentials(deployment_env, monkeypatch):
    monkeypatch.delenv('API_KEY')
    with pytest.raises(SystemExit, match='API_KEY'):
        deploy_render.deploy()
