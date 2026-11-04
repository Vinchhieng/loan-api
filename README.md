# Loan API

FastAPI container deployment project for Lessons 4.4-4.7. A scikit-learn decision tree is trained during the image build and bundled as `model.joblib`. **Training uses reproducible synthetic data and synthetic labels, not real borrower outcomes. This model must not be used for real lending decisions.** The original lesson training script was not supplied; this repository provides its own educational implementation.

## Run

```powershell
docker compose up --build -d
```

Open http://localhost:8000/docs. Expand `POST /predict`, click **Try it out**, and execute:

```json
{"annual_income":60000,"loan_amount":10000,"credit_score":720}
```

Both `/predict` and `/api/v1/predictions` accept the example request. `/health` returns `{"status":"ok","model_version":"1.0.0"}`. The API loads its model once during startup and runs independently of PostgreSQL.

Compose starts three services: API, PostgreSQL 17, and Adminer 4.8.1. The database contains the lesson's four fictional borrowers and six loan applications. Predictions are not written into those sample tables.

Open http://localhost:8080 for Adminer. Select PostgreSQL, server `db`, username `loans`, password `loans_dev_only`, and database `loans`. Adminer is bound to localhost. This database password is development-only, as allowed by the assignment.

Published image: [vinchhieng/loan-api on Docker Hub](https://hub.docker.com/r/vinchhieng/loan-api). Both `1.0.0` and `latest` were published. [Step 4 screenshot after registry pull](./evidence/registry-docs-200.png).

`MODEL_PATH` defaults to `model.joblib`; Compose explicitly sets `/app/model.joblib`. Only load trusted Joblib artifacts because deserialization can execute code. A missing file prevents startup.

## Alternate model without rebuilding

Use the same Python dependency versions as the image when training another artifact. The following PowerShell commands use the development image so no host Python installation is needed:

```powershell
docker build -t loan-api:slim .
New-Item -ItemType Directory -Force models
docker run --rm --mount "type=bind,source=$((Get-Location).Path)/models,target=/models" loan-api:slim python train.py --version 1.1.0 --out /models/model.joblib
docker run --rm -p 8001:8000 --mount "type=bind,source=$((Get-Location).Path)/models,target=/models,readonly" -e MODEL_PATH=/models/model.joblib loan-api:1.0.0
```

Open http://localhost:8001/health to see version `1.1.0`. The bundled version remains `1.0.0`.

## Tests and lesson evidence

```powershell
docker build -t loan-api:slim .
docker run --rm --mount "type=bind,source=$((Get-Location).Path)/tests,target=/tests,readonly" loan-api:slim python -m pytest -v -p no:cacheprovider /tests
docker build -t loan-api:full -f Dockerfile.full .
docker build -t loan-api:1.0.0 -f Dockerfile.prod .
```

[verify-lessons.ps1](./verify-lessons.ps1) records tests, model mounting, volumes, networking, Compose, persistence, image sizes, and runtime contents. **It resets the Compose sample database with `docker compose down -v` as part of the lesson. Do not use it against a database containing data you want to keep.** Production images omit the training script, tests, and development dependencies. See [CHECKLIST.md](./CHECKLIST.md) for actual command output and vulnerability notes.

## Publish

Authenticate interactively; never store credentials in this repository.

```powershell
docker login
docker tag loan-api:1.0.0 vinchhieng/loan-api:1.0.0
docker tag loan-api:1.0.0 vinchhieng/loan-api:latest
docker push vinchhieng/loan-api:1.0.0
docker push vinchhieng/loan-api:latest
```

After publishing, stop Compose and remove the specific local tags (keep database volumes):

```powershell
docker compose down
docker image rm vinchhieng/loan-api:1.0.0 vinchhieng/loan-api:latest loan-api:1.0.0
docker run --rm -p 8000:8000 vinchhieng/loan-api:1.0.0
```

Open `/docs`, send the example request, and save a screenshot showing HTTP 200. Check Docker Hub lists both tags. See [CHECKLIST.md](./CHECKLIST.md) for actual validation status.
