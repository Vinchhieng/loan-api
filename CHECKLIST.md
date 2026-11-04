# Verification checklist

Status: local verification only. The original seven-requirement table was not supplied; the seven sections below are provisional and must be reconciled with it before submission.

The bundled model is an illustrative rule model, not a trained loan model.

## 1. Production image and size

```powershell
docker image inspect loan-api:1.0.0 --format '{{.Id}} {{.Size}} {{.Config.User}}'
```

```text
sha256:9d77fca75f5d8efb71a2584116ec737a61b061a52d5437fc2d0f5cdadbca2baa 208876305 10001:10001
```

## 2. Non-root runtime user

```powershell
docker compose exec -T api id
```

```text
uid=10001(app) gid=10001(app) groups=10001(app)
```

## 3. Health check and Compose startup

```powershell
docker compose ps
```

```text
NAME            IMAGE                COMMAND                  SERVICE   CREATED         STATUS                   PORTS
module4-api-1   loan-api:1.0.0       "uvicorn main:app --…"   api       3 minutes ago   Up 3 minutes (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
module4-db-1    postgres:17-alpine   "docker-entrypoint.s…"   db        3 minutes ago   Up 3 minutes (healthy)   5432/tcp
```

## 4. Bundled configurable model

```powershell
docker run --rm -e MODEL_PATH=/app/models/model.json --entrypoint python loan-api:1.0.0 -c "import main; print(main.MODEL_PATH, main.MODEL_PATH.exists())"
```

```text
/app/models/model.json True
```

## 5. Standalone prediction without mounted local files

```powershell
docker exec loan-api-standalone python -c "import urllib.request,json; r=urllib.request.Request('http://localhost:8000/predict',data=json.dumps(dict(annual_income=60000,loan_amount=10000,credit_score=720)).encode(),headers={'Content-Type':'application/json'}); s=urllib.request.urlopen(r); print(s.status,s.read().decode())"
```

```text
200 {"prediction":"approved","model_version":"demo-1.0.0","demonstration_only":true}
```

## 6. Database initialization

```powershell
docker compose exec -T db psql -U loan -d loans -c '\dt'
```

```text
          List of relations
 Schema |    Name     | Type  | Owner 
--------+-------------+-------+-------
 public | predictions | table | loan
(1 row)
```

## 7. Vulnerability and secret scan

Command run (PowerShell):

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --mount "type=bind,source=$((Get-Location).Path)/evidence,target=/evidence" -v loan-trivy-cache:/root/.cache/ aquasec/trivy:latest image --quiet --severity HIGH,CRITICAL --scanners vuln,secret --format json --output /evidence/trivy.json loan-api:1.0.0
```

Full machine-readable output: [Trivy report](./evidence/trivy.json).

Results: 45 HIGH/CRITICAL package findings; 0 detected secrets.

| Package | CVE | Severity | Disposition |
| --- | --- | --- | --- |
| bsdutils | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| bsdutils | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| bsdutils | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| bsdutils | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libacl1 | CVE-2026-54369 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libblkid1 | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libblkid1 | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libblkid1 | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libblkid1 | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| liblastlog2-2 | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| liblastlog2-2 | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| liblastlog2-2 | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| liblastlog2-2 | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libmount1 | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libmount1 | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libmount1 | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libmount1 | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libncursesw6 | CVE-2025-69720 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libsmartcols1 | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libsmartcols1 | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libsmartcols1 | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libsmartcols1 | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libsqlite3-0 | CVE-2026-119373 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libsystemd0 | CVE-2026-16742 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libtinfo6 | CVE-2025-69720 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libudev1 | CVE-2026-16742 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libuuid1 | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libuuid1 | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libuuid1 | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| libuuid1 | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| login | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| login | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| login | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| login | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| mount | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| mount | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| mount | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| mount | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| ncurses-base | CVE-2025-69720 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| ncurses-bin | CVE-2025-69720 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| perl-base | CVE-2026-9538 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: fix_deferred). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| util-linux | CVE-2026-76642 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| util-linux | CVE-2026-78408 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| util-linux | CVE-2026-78409 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |
| util-linux | CVE-2026-78410 | HIGH | No fixed version listed by Trivy for the scanned Debian release (status: affected). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding. |

## API behavior tests

Command run:

```powershell
docker run --rm --user 0 --mount "type=bind,source=$((Get-Location).Path),target=/tests-source,readonly" loan-api:1.0.0 sh -c "pip install --no-cache-dir pytest==9.2.0 httpx==0.28.1 >/dev/null && python -m pytest -q -p no:cacheprovider /tests-source/tests"
```

Observed output: `1 passed, 1 warning in 1.12s`. Approval, rejection, and invalid income were checked. Warning: Starlette recommends httpx2 instead of httpx for its test client.

## Publication and registry pull: VERIFIED

Commands executed:

```powershell
docker tag loan-api:1.0.0 vinchhieng/loan-api:1.0.0
docker tag loan-api:1.0.0 vinchhieng/loan-api:latest
docker push vinchhieng/loan-api:1.0.0
docker push vinchhieng/loan-api:latest
docker buildx imagetools inspect vinchhieng/loan-api:1.0.0
docker buildx imagetools inspect vinchhieng/loan-api:latest
```

Both pushes succeeded. Both tags resolve to:

```text
sha256:9d77fca75f5d8efb71a2584116ec737a61b061a52d5437fc2d0f5cdadbca2baa
```

One initial registry inspection timed out during TLS authentication; retry succeeded. The [Docker Hub tags page](https://hub.docker.com/r/vinchhieng/loan-api/tags) was opened and both tags were visible. [Tags screenshot](./evidence/docker-hub-tags.png).

### Step 4: remove local images, pull and run

```powershell
docker compose down
docker rm -f loan-api-standalone
docker image rm vinchhieng/loan-api:1.0.0 vinchhieng/loan-api:latest loan-api:1.0.0
docker image ls --filter reference=vinchhieng/loan-api
docker run --rm -d --name loan-api-registry -p 8000:8000 vinchhieng/loan-api:1.0.0
```

Observed output (relevant excerpts):

```text
Untagged: vinchhieng/loan-api:1.0.0
Untagged: vinchhieng/loan-api:latest
Untagged: loan-api:1.0.0
Deleted: sha256:9d77fca75f5d8efb71a2584116ec737a61b061a52d5437fc2d0f5cdadbca2baa
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
Unable to find image 'vinchhieng/loan-api:1.0.0' locally
1.0.0: Pulling from vinchhieng/loan-api
Digest: sha256:9d77fca75f5d8efb71a2584116ec737a61b061a52d5437fc2d0f5cdadbca2baa
Status: Downloaded newer image for vinchhieng/loan-api:1.0.0
342ce5308743e0d59f654ee01571812d6c661b5036a2a92e7961882cf64b8bfc
```

Docker reused cached layers, but the local image tags and image record were deleted before the registry pull. No local files were mounted. The container became healthy. The command uses detached mode to keep the terminal available while testing.

Opened http://localhost:8000/docs, expanded POST /predict, clicked Try it out, and executed:

```json
{"annual_income":60000,"loan_amount":10000,"credit_score":720}
```

Actual Swagger server response:

```text
200
{"prediction":"approved","model_version":"demo-1.0.0","demonstration_only":true}
```

[Required Step 4 screenshot: Swagger HTTP 200 after registry pull](./evidence/registry-docs-200.png).

## Assessment limitations

- Obtain the original seven-requirement table and verify its exact thresholds and commands.
- Replace the illustrative model with the lesson model if trained machine learning is required.
- Vulnerability findings above remain unresolved where no vendor fix is listed.
- The database schema is initialized, but predictions are not persisted.
- Development-only database password is the explicit assignment exception and is excluded from the API image by explicit COPY instructions.
