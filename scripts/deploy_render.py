"""Provision and deploy only this capstone service, from GitHub Actions.

Authentication stays in environment secrets. Never print HTTP request headers,
request bodies, or response bodies: service creation includes the API key.
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = 'https://api.render.com/v1'
REPOSITORY = 'https://github.com/Vinchhieng/loan-api'
SERVICE_NAME = 'loan-api-vinchhieng-capstone'


def render_request(path, method='GET', payload=None):
    request = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={'Authorization': 'Bearer ' + os.environ['RENDER_API_KEY'],
                 'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        hint = ' Payment verification is required in Render.' if error.code == 402 else ''
        raise SystemExit(f'Render API returned HTTP {error.code}.{hint} Response omitted to protect credentials.') from None
    except OSError:
        raise SystemExit('Render API request failed. Check the service dashboard before retrying; the request may have completed.') from None


def deploy():
    for name in ('RENDER_API_KEY', 'API_KEY', 'RENDER_OWNER_ID', 'RELEASE_SHA'):
        if not os.environ.get(name):
            raise SystemExit(f'Missing required configuration: {name}')
    owner = os.environ['RENDER_OWNER_ID']
    sha = os.environ['RELEASE_SHA']
    if not re.fullmatch(r'[a-f0-9]{40}', sha):
        raise SystemExit('RELEASE_SHA must be a full commit SHA')
    query = urllib.parse.urlencode({'ownerId': owner, 'name': SERVICE_NAME, 'limit': 100})
    rows = render_request('/services?' + query)
    services = [row['service'] for row in rows if row['service']['name'] == SERVICE_NAME]
    if len(services) > 1:
        raise SystemExit('More than one matching capstone service; refusing ambiguous deployment')
    created = not services
    if created:
        result = render_request('/services', 'POST', {
            'type': 'web_service', 'name': SERVICE_NAME, 'ownerId': owner,
            'repo': REPOSITORY, 'branch': 'main', 'autoDeployTrigger': 'off',
            'envVars': [{'key': 'API_KEY', 'value': os.environ['API_KEY']}],
            'serviceDetails': {
                'runtime': 'docker', 'plan': 'free', 'region': 'singapore',
                'numInstances': 1, 'healthCheckPath': '/health',
                'envSpecificDetails': {'dockerfilePath': './Dockerfile.prod', 'dockerContext': '.'}
            }
        })
        service = result['service']
    else:
        service = services[0]
    if service.get('repo', '').removesuffix('.git') != REPOSITORY or service.get('branch') != 'main' or service.get('type') != 'web_service':
        raise SystemExit('Capstone service source does not match the intended repository, branch, and type')
    service_id = service['id']
    if service.get('autoDeployTrigger') != 'off' and service.get('autoDeploy') != 'no':
        raise SystemExit('Turn off automatic deployment before pipeline releases')
    app_url = service['serviceDetails']['url'].rstrip('/')
    if not app_url.startswith('https://'):
        raise SystemExit('Render did not provide an HTTPS service URL')
    requested_at = datetime.now(timezone.utc).isoformat()
    release = render_request('/services/' + service_id + '/deploys', 'POST', {'commitId': sha})
    evidence = {'service_id': service_id, 'service_created_by_pipeline': created,
                'app_url': app_url, 'requested_sha': sha, 'deploy_id': release.get('id'),
                'deploy_requested_at': requested_at}
    Path('deployment-request.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write(f'app_url={app_url}\nservice_id={service_id}\n')
    print(json.dumps(evidence))


if __name__ == '__main__':
    deploy()
