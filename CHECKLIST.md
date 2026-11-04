# Loan API assessment checklist

All seven requirements from the supplied Lesson 4.7 table are addressed below with file review or actual command output. HIGH vulnerabilities remain in the base image and have an individual explanation, as permitted by requirement 6.

Published API image: `sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c`.

The model is trained during the build on reproducible synthetic data. This is a course deployment exercise, not a validated lending model. The original course training script was not supplied.

## 1. Multi-stage Dockerfile.prod: slim base, non-root user, HEALTHCHECK

PASS. File review: [Dockerfile.prod](./Dockerfile.prod) has builder and runtime stages on `python:3.12-slim`, creates `appuser`, switches to that user, and defines an HTTP health check. Only the virtual environment, model, and API code enter the runtime stage.

```text
docker exec loan-api-registry whoami
```

```text
appuser
Exit code: 0
```

```text
docker ps --filter name=loan-api-registry
```

```text
CONTAINER ID   IMAGE                       COMMAND                  CREATED         STATUS                   PORTS                                         NAMES
fc6c0593f396   vinchhieng/loan-api:1.0.0   "uvicorn main:app --…"   7 minutes ago   Up 7 minutes (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   loan-api-registry
Exit code: 0
```

## 2. .dockerignore excludes Git, caches, local models and development configuration

PASS by file review: [.dockerignore](./.dockerignore).

```text
.git
.env
.env.*
!.env.example
.venv
venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
.vscode
.idea
.devcontainer
compose*.yaml
compose*.yml
init.sql
*.pyc
*.pem
*.key
tests
evidence
CHECKLIST.md
README.md
*.joblib
models
verify.ps1
verify-lessons.ps1
verify-release.py
build-checklist.py
verify-rubric.py
```

Git metadata, Python and tool caches, local Joblib files and the models directory, IDE/devcontainer configuration, environment files, Compose configuration, sample SQL, tests, and evidence are excluded. `requirements-dev.txt` remains available for the development Dockerfile; the production Dockerfile installs only `requirements.txt`.

The model is created inside the builder, so excluding local Joblib files does not remove the bundled production model.

## 3. Model path configurable with MODEL_PATH

PASS. [main.py](./main.py) reads `MODEL_PATH`, defaulting to `model.joblib`, and loads it once at startup. The same production image was started with a read-only mounted version 1.1.0 artifact.

```text
docker run --rm --mount 'type=bind,source=D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4/models,target=/models' loan-api:slim python train.py --version 1.1.0 --out /models/model.joblib
```

```text
Saved model 1.1.0 to /models/model.joblib
Exit code: 0
```

```text
docker run -d --name loan-model-switch -e MODEL_PATH=/models/model.joblib --mount 'type=bind,source=D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4/models,target=/models,readonly' loan-api:1.0.0
```

```text
2017c94d1ac239ea35d633aa2977dcdb5e12d81846790dd0ead92c0df55cf1dc
Exit code: 0
```

```text
docker exec loan-model-switch python -c 'import time,urllib.request; time.sleep(3); print(urllib.request.urlopen(''http://localhost:8000/health'').read().decode())'
```

```text
{"status":"ok","model_version":"1.1.0"}
Exit code: 0
```

The returned `model_version` is `1.1.0`. A missing-model path was also tested and prevented startup; see the complete [lesson evidence](./evidence/lesson-verification.md).

## 4. Compose runs API, PostgreSQL and Adminer; API builds from Dockerfile.prod

PASS. File review of [compose.yaml](./compose.yaml):

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      MODEL_PATH: /app/model.joblib
```

```text
docker compose up -d --wait
```

```text
docker.exe :  Container module4-adminer-1 Running
At D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4\verify-lessons.ps1:9 char:15
+     $output = & docker @DockerArgs 2>&1 | Out-String
+               ~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: ( Container module4-adminer-1 Running :String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

 Container module4-api-1 Running
 Container module4-db-1 Running
 Container module4-db-1 Waiting
 Container module4-db-1 Healthy
 Container module4-api-1 Waiting
 Container module4-db-1 Waiting
 Container module4-adminer-1 Waiting
 Container module4-db-1 Healthy
 Container module4-adminer-1 Healthy
 Container module4-api-1 Healthy
Exit code: 0
```

```text
docker compose ps
```

```text
NAME                IMAGE            COMMAND                  SERVICE   CREATED         STATUS                   PORTS
module4-adminer-1   adminer:4.8.1    "entrypoint.sh php -…"   adminer   5 minutes ago   Up 5 minutes             127.0.0.1:8080->8080/tcp
module4-api-1       loan-api:1.0.0   "uvicorn main:app --…"   api       7 seconds ago   Up 6 seconds (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
module4-db-1        postgres:17      "docker-entrypoint.s…"   db        5 minutes ago   Up 5 minutes (healthy)   5432/tcp
Exit code: 0
```

The API and database both show `(healthy)`; Adminer is running. The API health check comes from the image. Adminer was also opened and the lesson join query returned six rows: [database screenshot](./evidence/adminer-six-rows.png). Database persistence and reinitialization outputs are in [lesson evidence](./evidence/lesson-verification.md).

## 5. Image at least 40% smaller than the full-Python variant

PASS. Production: **578,386,536 bytes**. Full Python: **2,022,429,181 bytes**. Reduction: **71.40%**.

Calculation: `100 * (1 - production_bytes / full_bytes)`. Values come from Docker image inspection, captured by [verify-rubric.py](./verify-rubric.py); [exact values](./evidence/image-sizes.json). Both images use the same application and training code. The full-base variant is built from [Dockerfile.full](./Dockerfile.full).

```text
docker image ls loan-api
```

```text
IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
loan-api:1.0.0   98ecbde59e24        578MB          134MB   U
loan-api:full    bf10e9fef2dd       2.02GB          508MB
loan-api:slim    22529c51752c        598MB          139MB
Exit code: 0
```

Docker disk sizes are used consistently for this calculation. Compressed registry sizes are a different metric.

## 6. No HIGH or CRITICAL findings without an explanatory note

PASS with documented unresolved findings. Trivy scanned the same image digest published to Docker Hub.

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --mount "type=bind,source=$((Get-Location).Path)/evidence,target=/evidence" -v loan-trivy-cache:/root/.cache/ aquasec/trivy:latest image --quiet --severity HIGH,CRITICAL --scanners vuln,secret --format json --output /evidence/trivy.json loan-api:1.0.0
```

Actual report: **45 HIGH**, **0 CRITICAL**, **0 detected secrets**. [Complete Trivy JSON](./evidence/trivy.json).

| Package | CVE | Severity | Why it remains unresolved |
| --- | --- | --- | --- |
| bsdutils | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| bsdutils | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| bsdutils | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| bsdutils | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libacl1 | CVE-2026-54369 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libblkid1 | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libblkid1 | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libblkid1 | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libblkid1 | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| liblastlog2-2 | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| liblastlog2-2 | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| liblastlog2-2 | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| liblastlog2-2 | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libmount1 | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libmount1 | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libmount1 | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libmount1 | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libncursesw6 | CVE-2025-69720 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libsmartcols1 | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libsmartcols1 | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libsmartcols1 | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libsmartcols1 | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libsqlite3-0 | CVE-2026-119373 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libsystemd0 | CVE-2026-16742 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libtinfo6 | CVE-2025-69720 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libudev1 | CVE-2026-16742 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libuuid1 | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libuuid1 | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libuuid1 | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| libuuid1 | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| login | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| login | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| login | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| login | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| mount | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| mount | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| mount | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| mount | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| ncurses-base | CVE-2025-69720 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| ncurses-bin | CVE-2025-69720 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| perl-base | CVE-2026-9538 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: fix_deferred). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| util-linux | CVE-2026-76642 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| util-linux | CVE-2026-78408 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| util-linux | CVE-2026-78409 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |
| util-linux | CVE-2026-78410 | HIGH | Trivy lists no fixed version for the scanned Debian release (status: affected). Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation reduces exposure but does not fix this issue. |

## 7. Published as vinchhieng/loan-api:1.0.0 and :latest

PASS. Both pushes succeeded and both registry tags resolve to the same image index.

```text
docker push vinchhieng/loan-api:1.0.0
```

```text
The push refers to repository [docker.io/vinchhieng/loan-api]
1.0.0: digest: sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c size: 856
Exit code: 0
```

```text
docker buildx imagetools inspect vinchhieng/loan-api:1.0.0
```

```text
Name:      docker.io/vinchhieng/loan-api:1.0.0
MediaType: application/vnd.oci.image.index.v1+json
Digest:    sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c

Manifests:
  Name:        docker.io/vinchhieng/loan-api:1.0.0@sha256:24ec2e8542954d8c92b9630b8392ca3337dba1227064b4e932145f2673e781d2
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/amd64

  Name:        docker.io/vinchhieng/loan-api:1.0.0@sha256:4bfa14b18e708e43ca4224e96b49820561f4d9655d8ce12b0d6ec45ec3d871d1
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    unknown/unknown
  Annotations:
    vnd.docker.reference.digest: sha256:24ec2e8542954d8c92b9630b8392ca3337dba1227064b4e932145f2673e781d2
    vnd.docker.reference.type:   attestation-manifest
Exit code: 0
```

```text
docker push vinchhieng/loan-api:latest
```

```text
The push refers to repository [docker.io/vinchhieng/loan-api]
latest: digest: sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c size: 856
Exit code: 0
```

```text
docker buildx imagetools inspect vinchhieng/loan-api:latest
```

```text
Name:      docker.io/vinchhieng/loan-api:latest
MediaType: application/vnd.oci.image.index.v1+json
Digest:    sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c

Manifests:
  Name:        docker.io/vinchhieng/loan-api:latest@sha256:24ec2e8542954d8c92b9630b8392ca3337dba1227064b4e932145f2673e781d2
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/amd64

  Name:        docker.io/vinchhieng/loan-api:latest@sha256:4bfa14b18e708e43ca4224e96b49820561f4d9655d8ce12b0d6ec45ec3d871d1
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    unknown/unknown
  Annotations:
    vnd.docker.reference.digest: sha256:24ec2e8542954d8c92b9630b8392ca3337dba1227064b4e932145f2673e781d2
    vnd.docker.reference.type:   attestation-manifest
Exit code: 0
```

The [public Docker Hub repository page](https://hub.docker.com/r/vinchhieng/loan-api/tags) was also opened and both tags were visible. [Tags screenshot](./evidence/docker-hub-tags.png).

## Step 4. Remove local images, pull from Docker Hub and predict

PASS. The following commands were executed after publication. Repeated layer progress is omitted; [full original output](./evidence/registry-verification.md) is retained.

```text
docker compose down
```

```text
 Container module4-api-1 Stopping
 Container module4-adminer-1 Stopping
 Container module4-adminer-1 Stopped
 Container module4-adminer-1 Removing
 Container module4-adminer-1 Removed
 Container module4-api-1 Stopped
 Container module4-api-1 Removing
 Container module4-api-1 Removed
 Container module4-db-1 Stopping
 Container module4-db-1 Stopped
 Container module4-db-1 Removing
 Container module4-db-1 Removed
 Network module4_default Removing
 Network module4_default Removed
Exit code: 0
```

```text
docker image rm vinchhieng/loan-api:1.0.0 vinchhieng/loan-api:latest loan-api:1.0.0
```

```text
Untagged: vinchhieng/loan-api:1.0.0
Untagged: vinchhieng/loan-api:latest
Untagged: loan-api:1.0.0
Deleted: sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c
Exit code: 0
```

```text
docker image ls --filter reference=vinchhieng/loan-api
```

```text
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
Exit code: 0
```

```text
docker run --rm -d --name loan-api-registry -p 8000:8000 vinchhieng/loan-api:1.0.0
```

```text
Unable to find image 'vinchhieng/loan-api:1.0.0' locally
1.0.0: Pulling from vinchhieng/loan-api
Digest: sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c
Status: Downloaded newer image for vinchhieng/loan-api:1.0.0
fc6c0593f3968f5b510d16417e98bee92d54302d9bda9e3461f5ec8f27e05905
Exit code: 0
```

```text
docker exec loan-api-registry python -c "import urllib.request; r=urllib.request.Request('http://localhost:8000/api/v1/predictions',data='{\"annual_income\": 60000, \"loan_amount\": 10000, \"credit_score\": 720}'.encode(),headers={'Content-Type':'application/json'}); s=urllib.request.urlopen(r); print(s.status,s.read().decode())"
```

```text
200 {"prediction":"approved","model_version":"1.0.0","synthetic_training_data":true}
Exit code: 0
```

```text
docker inspect --format "{{json .Mounts}}" loan-api-registry
```

```text
[]
Exit code: 0
```

The local image record and tags were removed before the run. Docker downloaded the image record from the registry and reused cached layers. `Mounts: []` confirms no local files were mounted. Detached mode kept the terminal available for verification.

Opened `/docs`, selected POST /predict, clicked Try it out and Execute with annual_income 60000, loan_amount 10000 and credit_score 720. Actual server response: **200**, approved, model version **1.0.0**.

[Required Step 4 screenshot](./evidence/registry-docs-200.png). The full Compose stack was restarted after capturing this registry proof.

## Secrets and supporting checks

Repository secret scan: **0 detected secrets**. [Raw JSON](./evidence/repository-secrets.json). Command:

```powershell
docker run --rm --mount "type=bind,source=$((Get-Location).Path),target=/src,readonly" --mount "type=bind,source=$((Get-Location).Path)/evidence,target=/evidence" aquasec/trivy:latest fs --quiet --scanners secret --skip-dirs /src/.git --skip-dirs /src/evidence --format json --output /evidence/repository-secrets.json /src
```

The development-only Compose database password is the assignment exception. Scanning excludes Git metadata and generated evidence; detection cannot guarantee the absence of every secret. No authentication tokens were written to project files.

```text
docker run --rm --mount 'type=bind,source=D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4/tests,target=/tests,readonly' loan-api:slim python -m pytest -v -p no:cacheprovider /tests
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.16, pytest-9.2.0, pluggy-1.7.0 -- /usr/local/bin/python
rootdir: /tests
plugins: anyio-4.16.0
collecting ... collected 5 items

../tests/test_api.py::test_health PASSED                                 [ 20%]
../tests/test_api.py::test_prediction_routes PASSED                      [ 40%]
../tests/test_api.py::test_rejected_application PASSED                   [ 60%]
../tests/test_api.py::test_validation PASSED                             [ 80%]
../tests/test_api.py::test_model_configuration_and_missing_file PASSED   [100%]

=============================== warnings summary ===============================
../usr/local/lib/python3.12/site-packages/fastapi/testclient.py:1
  /usr/local/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 5 passed, 1 warning in 2.95s =========================
Exit code: 0
```

[Full lesson evidence](./evidence/lesson-verification.md) also records named volumes, container DNS, missing-model startup failure, database persistence, and the absence of training code, tests and pytest from the production image.

## Implementation scope

- Training uses synthetic labels and data. No real lending accuracy is claimed.
- The database reproduces the supplied sample records. The prediction endpoint does not persist predictions into those tables.
- The API vulnerability report does not certify the separate PostgreSQL or lesson-pinned Adminer images.
