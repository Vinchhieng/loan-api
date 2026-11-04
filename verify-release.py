"""Publish and verify the course image. Requires an authenticated Docker CLI.

Stops this project's Compose services and removes only the three loan API image
tags below, as required by the registry-pull exercise. Keeps database volumes.
"""
import json
from pathlib import Path
import subprocess
import time


LOG = Path('evidence/registry-verification.md')
lines = ['# Publication and registry verification', '']


def run(*args):
    command = ['docker', *args]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, encoding='utf-8', errors='replace')
    lines.extend(['```text', subprocess.list2cmdline(command), '```', '',
                  '```text', result.stdout.rstrip(), f'Exit code: {result.returncode}', '```', ''])
    LOG.write_text('\n'.join(lines), encoding='utf-8')
    print(f'{subprocess.list2cmdline(command)}: exit {result.returncode}', flush=True)
    result.check_returncode()
    return result.stdout


payload = json.dumps({'annual_income': 60000, 'loan_amount': 10000, 'credit_score': 720})
request_code = ("import urllib.request; r=urllib.request.Request('http://localhost:8000/api/v1/predictions',"
                f"data={payload!r}.encode(),headers={{'Content-Type':'application/json'}}); "
                "s=urllib.request.urlopen(r); print(s.status,s.read().decode())")
lines.extend(['## Compose prediction and request log', ''])
run('compose', 'exec', '-T', 'api', 'python', '-c', request_code)
run('compose', 'logs', '--tail', '10', 'api')
lines.extend(['## Published tags', ''])
for tag in ('1.0.0', 'latest'):
    run('tag', 'loan-api:1.0.0', f'vinchhieng/loan-api:{tag}')
    run('push', f'vinchhieng/loan-api:{tag}')
    run('buildx', 'imagetools', 'inspect', f'vinchhieng/loan-api:{tag}')
lines.extend(['## Local image removal and registry run', ''])
run('compose', 'down')
run('image', 'rm', 'vinchhieng/loan-api:1.0.0', 'vinchhieng/loan-api:latest', 'loan-api:1.0.0')
run('image', 'ls', '--filter', 'reference=vinchhieng/loan-api')
run('run', '--rm', '-d', '--name', 'loan-api-registry', '-p', '8000:8000', 'vinchhieng/loan-api:1.0.0')
for _ in range(60):
    status = subprocess.run(['docker', 'inspect', '--format', '{{.State.Health.Status}}',
                             'loan-api-registry'], capture_output=True, text=True)
    if status.stdout.strip() == 'healthy':
        break
    time.sleep(1)
else:
    raise RuntimeError('Registry container did not become healthy')
run('ps', '--filter', 'name=loan-api-registry')
run('exec', 'loan-api-registry', 'python', '-c', request_code)
run('inspect', '--format', '{{json .Mounts}}', 'loan-api-registry')
run('image', 'inspect', 'vinchhieng/loan-api:1.0.0', '--format', '{{.Id}}')
print('Release verification completed. Capture /docs HTTP 200 and Docker Hub tag screenshots next.', flush=True)
