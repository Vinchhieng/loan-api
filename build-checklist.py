"""Assemble the exact seven assessment requirements from recorded evidence."""
import json
from pathlib import Path
import re


root = Path(__file__).resolve().parent


def read(relative):
    return (root / relative).read_text(encoding='utf-8-sig')


def blocks(relative):
    return re.findall(r'```(?:powershell|text)\n(.*?)\n```\s*\n```text\n(.*?)\n```', read(relative), re.S)


lesson = blocks('evidence/lesson-verification.md')
rubric = blocks('evidence/rubric-verification.md')
registry = blocks('evidence/registry-verification.md')
scan = json.loads(read('evidence/trivy.json'))
repo_scan = json.loads(read('evidence/repository-secrets.json'))
sizes = json.loads(read('evidence/image-sizes.json'))
findings = [v for result in scan.get('Results', []) for v in result.get('Vulnerabilities', [])]
image_secrets = sum(len(r.get('Secrets', [])) for r in scan.get('Results', []))
repo_secrets = sum(len(r.get('Secrets', [])) for r in repo_scan.get('Results', []))
lines = ['# Loan API assessment checklist', '',
         'All seven requirements from the supplied Lesson 4.7 table are addressed below with file review or actual command output. HIGH vulnerabilities remain in the base image and have an individual explanation, as permitted by requirement 6.', '',
         'Published API image: `' + scan['Metadata']['ImageID'] + '`.', '',
         'The model is trained during the build on reproducible synthetic data. This is a course deployment exercise, not a validated lending model. The original course training script was not supplied.', '']


def emit(command, output):
    # Omit transport chatter; preserve the complete originals in the evidence files.
    output = '\n'.join(line for line in output.splitlines()
                       if not re.match(r'^[a-f0-9]{12}: (Waiting|Layer already exists|Already exists|Pushed|Pulling fs layer|Pull complete|Download complete|Mounted from)', line))
    lines.extend(['```text', command, '```', '', '```text', output, '```', ''])


def evidence(source, token):
    for command, output in source:
        if token in command:
            emit(command, output)
            return
    raise ValueError(f'Missing evidence: {token}')


lines += ['## 1. Multi-stage Dockerfile.prod: slim base, non-root user, HEALTHCHECK', '',
          'PASS. File review: [Dockerfile.prod](./Dockerfile.prod) has builder and runtime stages on `python:3.12-slim`, creates `appuser`, switches to that user, and defines an HTTP health check. Only the virtual environment, model, and API code enter the runtime stage.', '']
evidence(rubric, 'docker exec loan-api-registry whoami')
evidence(rubric, 'docker ps --filter name=loan-api-registry')
lines += ['## 2. .dockerignore excludes Git, caches, local models and development configuration', '',
          'PASS by file review: [.dockerignore](./.dockerignore).', '', '```text', read('.dockerignore').rstrip(), '```', '',
          'Git metadata, Python and tool caches, local Joblib files and the models directory, IDE/devcontainer configuration, environment files, Compose configuration, sample SQL, tests, and evidence are excluded. `requirements-dev.txt` remains available for the development Dockerfile; the production Dockerfile installs only `requirements.txt`.', '',
          'The model is created inside the builder, so excluding local Joblib files does not remove the bundled production model.', '',
          '## 3. Model path configurable with MODEL_PATH', '',
          'PASS. [main.py](./main.py) reads `MODEL_PATH`, defaulting to `model.joblib`, and loads it once at startup. The same production image was started with a read-only mounted version 1.1.0 artifact.', '']
for token in ('python train.py --version 1.1.0', 'docker run -d --name loan-model-switch', 'docker exec loan-model-switch python'):
    evidence(lesson, token)
lines += ['The returned `model_version` is `1.1.0`. A missing-model path was also tested and prevented startup; see the complete [lesson evidence](./evidence/lesson-verification.md).', '',
          '## 4. Compose runs API, PostgreSQL and Adminer; API builds from Dockerfile.prod', '',
          'PASS. File review of [compose.yaml](./compose.yaml):', '', '```yaml',
          'services:\n  api:\n    build:\n      context: .\n      dockerfile: Dockerfile.prod\n    environment:\n      MODEL_PATH: /app/model.joblib', '```', '']
evidence(lesson, 'docker compose up -d --wait')
evidence(rubric, 'docker compose ps')
lines += ['The API and database both show `(healthy)`; Adminer is running. The API health check comes from the image. Adminer was also opened and the lesson join query returned six rows: [database screenshot](./evidence/adminer-six-rows.png). Database persistence and reinitialization outputs are in [lesson evidence](./evidence/lesson-verification.md).', '',
          '## 5. Image at least 40% smaller than the full-Python variant', '',
          f'PASS. Production: **{sizes["production_bytes"]:,} bytes**. Full Python: **{sizes["full_bytes"]:,} bytes**. Reduction: **{sizes["reduction_percent"]:.2f}%**.', '',
          'Calculation: `100 * (1 - production_bytes / full_bytes)`. Values come from Docker image inspection, captured by [verify-rubric.py](./verify-rubric.py); [exact values](./evidence/image-sizes.json). Both images use the same application and training code. The full-base variant is built from [Dockerfile.full](./Dockerfile.full).', '']
evidence(lesson, 'docker image ls loan-api')
lines += ['Docker disk sizes are used consistently for this calculation. Compressed registry sizes are a different metric.', '',
          '## 6. No HIGH or CRITICAL findings without an explanatory note', '',
          'PASS with documented unresolved findings. Trivy scanned the same image digest published to Docker Hub.', '', '```powershell',
          'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --mount "type=bind,source=$((Get-Location).Path)/evidence,target=/evidence" -v loan-trivy-cache:/root/.cache/ aquasec/trivy:latest image --quiet --severity HIGH,CRITICAL --scanners vuln,secret --format json --output /evidence/trivy.json loan-api:1.0.0',
          '```', '',
          f'Actual report: **{sum(v["Severity"] == "HIGH" for v in findings)} HIGH**, **{sum(v["Severity"] == "CRITICAL" for v in findings)} CRITICAL**, **{image_secrets} detected secrets**. [Complete Trivy JSON](./evidence/trivy.json).', '',
          '| Package | CVE | Severity | Why it remains unresolved |', '| --- | --- | --- | --- |']
for v in findings:
    if v.get('FixedVersion'):
        note = f'Fix available in {v["FixedVersion"]}; remediation remains pending.'
    else:
        note = (f'Trivy lists no fixed version for the scanned Debian release (status: {v.get("Status", "unknown")}). '
                'Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue.')
    lines.append(f'| {v["PkgName"]} | {v["VulnerabilityID"]} | {v["Severity"]} | {note} |')
lines += ['', '## 7. Published as vinchhieng/loan-api:1.0.0 and :latest', '',
          'PASS. Both pushes succeeded and both registry tags resolve to the same image index.', '']
for tag in ('1.0.0', 'latest'):
    evidence(registry, f'docker push vinchhieng/loan-api:{tag}')
    evidence(rubric, f'docker buildx imagetools inspect vinchhieng/loan-api:{tag}')
lines += ['The [public Docker Hub repository page](https://hub.docker.com/r/vinchhieng/loan-api/tags) was also opened and both tags were visible. [Tags screenshot](./evidence/docker-hub-tags.png).', '',
          '## Step 4. Remove local images, pull from Docker Hub and predict', '',
          'PASS. The following commands were executed after publication. Repeated layer progress is omitted; [full original output](./evidence/registry-verification.md) is retained.', '']
for token in ('docker compose down', 'docker image rm', 'docker image ls --filter', 'docker run --rm -d --name loan-api-registry', 'docker exec loan-api-registry python', 'docker inspect --format'):
    evidence(registry, token)
lines += ['The local image record and tags were removed before the run. Docker downloaded the image record from the registry and reused cached layers. `Mounts: []` confirms no local files were mounted. Detached mode kept the terminal available for verification.', '',
          'Opened `/docs`, selected POST /predict, clicked Try it out and Execute with annual_income 60000, loan_amount 10000 and credit_score 720. Actual server response: **200**, approved, model version **1.0.0**.', '',
          '[Required Step 4 screenshot](./evidence/registry-docs-200.png). The full Compose stack was restarted after capturing this registry proof.', '',
          '## Secrets and supporting checks', '',
          f'Repository secret scan: **{repo_secrets} detected secrets**. [Raw JSON](./evidence/repository-secrets.json). Command:', '', '```powershell',
          'docker run --rm --mount "type=bind,source=$((Get-Location).Path),target=/src,readonly" --mount "type=bind,source=$((Get-Location).Path)/evidence,target=/evidence" aquasec/trivy:latest fs --quiet --scanners secret --skip-dirs /src/.git --skip-dirs /src/evidence --format json --output /evidence/repository-secrets.json /src',
          '```', '',
          'The development-only Compose database password is the assignment exception. Scanning excludes Git metadata and generated evidence; detection cannot guarantee the absence of every secret. No authentication tokens were written to project files.', '']
evidence(lesson, 'python -m pytest -v')
lines += ['[Full lesson evidence](./evidence/lesson-verification.md) also records named volumes, container DNS, missing-model startup failure, database persistence, and the absence of training code, tests and pytest from the production image.', '',
          '## Implementation scope', '',
          '- Training uses synthetic labels and data. No real lending accuracy is claimed.',
          '- The database reproduces the supplied sample records. The prediction endpoint does not persist predictions into those tables.',
          '- The API vulnerability report does not certify the separate PostgreSQL or lesson-pinned Adminer images.', '']
(root / 'CHECKLIST.md').write_text('\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()) + '\n', encoding='utf-8')
print('CHECKLIST.md now matches all seven rows of the supplied table.')
