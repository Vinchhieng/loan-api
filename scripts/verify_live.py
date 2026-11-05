"""Verify release identity and authentication without logging secrets."""
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def request(path, key=None, payload=None):
    headers = {'Content-Type': 'application/json'}
    if key:
        headers['X-API-Key'] = key
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base + path, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, None


if __name__ == '__main__':
    base = os.environ['APP_URL'].rstrip('/')
    expected = os.environ['EXPECTED_SHA']
    key = os.environ['API_KEY']
    if not base.startswith('https://') or not key or len(expected) != 40:
        raise SystemExit('HTTPS APP_URL, API_KEY, and full EXPECTED_SHA are required')
    started = time.monotonic()
    deadline = started + 900
    while time.monotonic() < deadline:
        try:
            status, health = request('/health')
            if status == 200 and health.get('status') == 'ok' and health.get('git_sha') == expected:
                live_at = datetime.now(timezone.utc).isoformat()
                break
        except (OSError, ValueError):
            pass
        time.sleep(10)
    else:
        raise SystemExit('Release did not become healthy with expected SHA within 900 seconds')
    evidence = {'first_observed_healthy_at': live_at, 'health': health,
                'verification_wait_seconds': round(time.monotonic() - started, 2), 'checks': []}
    Path('release-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps(evidence))
    payload = {'annual_income': 60000, 'loan_amount': 10000, 'credit_score': 720}
    for path in ('/api/v1/predictions', '/predict'):
        for supplied, expected_status, label in ((None, 401, 'missing'), ('invalid-drill-key', 401, 'invalid'), (key, 200, 'valid')):
            status, body = request(path, supplied, payload)
            if status != expected_status:
                raise SystemExit(f'{path}: {label} key expected {expected_status}, received {status}')
            if status == 200 and body.get('prediction') != 'approved':
                raise SystemExit('Known prediction regression detected')
            print(f'{path}: {label} key -> {status}')
            evidence['checks'].append({'path': path, 'key_case': label, 'status': status})
    for supplied, expected_status, label in ((None, 401, 'missing'), ('invalid-drill-key', 401, 'invalid'), (key, 200, 'valid')):
        status, body = request('/api/v1/applications', supplied)
        if status != expected_status:
            raise SystemExit(f'Application list: {label} key expected {expected_status}, received {status}')
        if status == 200 and not isinstance(body.get('items'), list):
            raise SystemExit('Application list does not contain a paginated items array')
        print(f'/api/v1/applications: {label} key -> {status}')
        evidence['checks'].append({'path': '/api/v1/applications', 'key_case': label, 'status': status})
    status, application = request('/api/v1/applications', key, {'borrower_id': 1, 'amount_usd': 1500, 'term_months': 12})
    if status != 201 or not isinstance(application.get('id'), int):
        raise SystemExit('Synthetic application creation failed')
    status, prediction = request(f"/api/v1/applications/{application['id']}/predictions", key, {})
    if status != 201 or abs(prediction.get('default_probability', -1) - 0.27825003205504184) > 1e-12:
        raise SystemExit('Registered champion parity check failed')
    evidence['champion_parity'] = {'expected': 0.27825003205504184, 'actual': prediction['default_probability'],
                                   'model_version': prediction['model_version'], 'tolerance': 1e-12}
    print('Application workflow and registered champion parity passed')
    status, _ = request('/api/v1/applications', key, {'borrower_id': 1, 'amount_usd': 1500, 'term_months': 24})
    evidence['supported_24_month_term_status'] = status
    Path('release-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    if status != 201:
        raise SystemExit(f'24-month contract check expected 201, received {status}')
    print('24-month application contract check passed')
    score_payload = {'amount_usd': 1500, 'term_months': 12, 'monthly_income_usd': 350,
                     'previous_loans': 1, 'late_payments': 0}
    status, preview = request('/api/v1/score', key, score_payload)
    evidence['score_preview'] = {'status': status, 'expected_probability': 0.278,
                                 'actual_probability': preview.get('probability_default') if preview else None}
    Path('release-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    if status != 200 or abs(preview.get('probability_default', -1) - 0.278) > 1e-12:
        raise SystemExit('Direct score default-probability regression detected')
    print('Direct score Module 5 probability check passed')
    status, schema = request('/openapi.json')
    if status != 200 or '/api/v1/predictions' not in schema.get('paths', {}):
        raise SystemExit('OpenAPI verification failed')
    evidence['verified_at'] = datetime.now(timezone.utc).isoformat()
    evidence['openapi_paths'] = sorted(schema['paths'])
    Path('release-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    Path('live-openapi.json').write_text(json.dumps(schema, indent=2), encoding='utf-8')
    print('Release verification passed')
