# Lesson 4.4-4.6 command evidence

Commands and actual output captured by verify-lessons.ps1. No assessment table was provided; these checks follow the supplied lesson screenshots.

## 1. Five API tests and configurable model path

```powershell
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

```powershell
docker run --rm -e MODEL_PATH=/missing.joblib loan-api:1.0.0
```

```text
docker.exe : INFO:     Started server process [1]
At D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4\verify-lessons.ps1:9 char:15
+     $output = & docker @DockerArgs 2>&1 | Out-String
+               ~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (INFO:     Started server process [1]:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
INFO:     Waiting for application startup.
ERROR:    Traceback (most recent call last):
  File "/opt/venv/lib/python3.12/site-packages/starlette/routing.py", line 661, in lifespan
    async with self.lifespan_context(app) as maybe_state:
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/main.py", line 14, in lifespan
    model = joblib.load(MODEL_PATH)
            ^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/joblib/numpy_pickle.py", line 741, in load
    with open(filename, "rb") as f:
         ^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/missing.joblib'

ERROR:    Application startup failed. Exiting.
Exit code: 3
```

## 2. Read-only model bind mount changes model version without rebuilding

```powershell
docker run --rm --mount 'type=bind,source=D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4/models,target=/models' loan-api:slim python train.py --version 1.1.0 --out /models/model.joblib
```

```text
Saved model 1.1.0 to /models/model.joblib
Exit code: 0
```

```powershell
docker run -d --name loan-model-switch -e MODEL_PATH=/models/model.joblib --mount 'type=bind,source=D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4/models,target=/models,readonly' loan-api:1.0.0
```

```text
2017c94d1ac239ea35d633aa2977dcdb5e12d81846790dd0ead92c0df55cf1dc
Exit code: 0
```

```powershell
docker exec loan-model-switch python -c 'import time,urllib.request; time.sleep(3); print(urllib.request.urlopen(''http://localhost:8000/health'').read().decode())'
```

```text
{"status":"ok","model_version":"1.1.0"}
Exit code: 0
```

```powershell
docker rm -f loan-model-switch
```

```text
loan-model-switch
Exit code: 0
```

## 3. Named volume data survives container removal

```powershell
docker volume create loan-lesson-notes
```

```text
loan-lesson-notes
Exit code: 0
```

```powershell
docker run --rm -v loan-lesson-notes:/data python:3.12-slim sh -c 'echo "first run" >> /data/notes.txt; cat /data/notes.txt'
```

```text
first
Exit code: 0
```

```powershell
docker run --rm -v loan-lesson-notes:/data python:3.12-slim sh -c 'echo "second run" >> /data/notes.txt; cat /data/notes.txt'
```

```text
second
Exit code: 0
```

```powershell
docker volume rm loan-lesson-notes
```

```text
loan-lesson-notes
Exit code: 0
```

## 4. Containers reach the API by name without publishing a port

```powershell
docker network create loan-lesson-net
```

```text
46cb33f0959811ecd088a09c823e587293e5d32a3ac4f5fcf4182a79efda6432
Exit code: 0
```

```powershell
docker run -d --name loan-network-api --network loan-lesson-net loan-api:1.0.0
```

```text
71c179861cf04d0dd7113db73145322af7cc9111bf9e4df0a24a8d30a6adea91
Exit code: 0
```

```powershell
docker run --rm --network loan-lesson-net curlimages/curl:8.10.1 --retry 10 --retry-connrefused --retry-delay 1 --fail -sS http://loan-network-api:8000/health
```

```text
docker.exe : Unable to find image 'curlimages/curl:8.10.1' locally
At D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4\verify-lessons.ps1:9 char:15
+     $output = & docker @DockerArgs 2>&1 | Out-String
+               ~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (Unable to find ...8.10.1' locally:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
8.10.1: Pulling from curlimages/curl
4ca545ee6d5d: Pulling fs layer
43c4264eed91: Pulling fs layer
b68d62cb323c: Pulling fs layer
4ca545ee6d5d: Download complete
b68d62cb323c: Download complete
43c4264eed91: Download complete
43c4264eed91: Pull complete
b68d62cb323c: Pull complete
4ca545ee6d5d: Pull complete
Digest: sha256:d9b4541e214bcd85196d6e92e2753ac6d0ea699f0af5741f8c6cccbfcf00ef4b
Status: Downloaded newer image for curlimages/curl:8.10.1
{"status":"ok","model_version":"1.0.0"}
Exit code: 0
```

```powershell
docker rm -f loan-network-api
```

```text
loan-network-api
Exit code: 0
```

```powershell
docker network rm loan-lesson-net
```

```text
loan-lesson-net
Exit code: 0
```

## 5. Compose services, seeded database, and database persistence

```powershell
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

```powershell
docker compose ps
```

```text
NAME                IMAGE            COMMAND                  SERVICE   CREATED         STATUS                   PORTS
module4-adminer-1   adminer:4.8.1    "entrypoint.sh php -…"   adminer   2 minutes ago   Up 2 minutes             127.0.0.1:8080->8080/tcp
module4-api-1       loan-api:1.0.0   "uvicorn main:app --…"   api       2 minutes ago   Up 2 minutes (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
module4-db-1        postgres:17      "docker-entrypoint.s…"   db        2 minutes ago   Up 2 minutes (healthy)   5432/tcp
Exit code: 0
```

```powershell
docker compose exec -T api python -c 'import urllib.request; print(urllib.request.urlopen(''http://localhost:8000/health'').read().decode())'
```

```text
{"status":"ok","model_version":"1.0.0"}
Exit code: 0
```

```powershell
docker compose exec -T db psql -U loans -d loans -c 'SELECT b.full_name,a.amount_usd,a.term_months,a.status FROM loan_applications a JOIN borrowers b ON b.id=a.borrower_id ORDER BY a.id;'
```

```text
   full_name    | amount_usd | term_months |  status  
----------------+------------+-------------+----------
 Sok Dara       |       1500 |          12 | pending
 Chan Sreyneang |        800 |           6 | approved
 Kim Vuthy      |       3200 |          24 | pending
 Heng Malis     |       2000 |          18 | rejected
 Sok Dara       |        600 |           6 | pending
 Heng Malis     |       1200 |          12 | pending
(6 rows)
Exit code: 0
```

```powershell
docker compose exec -T db psql -U loans -d loans -c 'UPDATE loan_applications SET status=''approved'' WHERE id=101;'
```

```text
UPDATE 1
Exit code: 0
```

```powershell
docker compose down
```

```text
docker.exe :  Container module4-adminer-1 Stopping 
At D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4\verify-lessons.ps1:9 char:15
+     $output = & docker @DockerArgs 2>&1 | Out-String
+               ~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: ( Container module4-adminer-1 Stopping :String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
 Container module4-api-1 Stopping 
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

```powershell
docker compose up -d --wait
```

```text
docker.exe :  Network module4_default Creating 
At D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4\verify-lessons.ps1:9 char:15
+     $output = & docker @DockerArgs 2>&1 | Out-String
+               ~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: ( Network module4_default Creating :String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
 Network module4_default Creating 
 Network module4_default Created 
 Network module4_default Created 
 Container module4-db-1 Creating 
 Container module4-db-1 Created 
 Container module4-adminer-1 Creating 
 Container module4-api-1 Creating 
 Container module4-api-1 Created 
 Container module4-adminer-1 Created 
 Container module4-db-1 Starting 
 Container module4-db-1 Started 
 Container module4-adminer-1 Starting 
 Container module4-db-1 Waiting 
 Container module4-adminer-1 Started 
 Container module4-db-1 Healthy 
 Container module4-api-1 Starting 
 Container module4-api-1 Started 
 Container module4-api-1 Waiting 
 Container module4-db-1 Waiting 
 Container module4-adminer-1 Waiting 
 Container module4-adminer-1 Healthy 
 Container module4-db-1 Healthy 
 Container module4-api-1 Healthy
Exit code: 0
```

```powershell
docker compose exec -T db psql -U loans -d loans -c 'SELECT id,status FROM loan_applications WHERE id=101;'
```

```text
 id  |  status  
-----+----------
 101 | approved
(1 row)
Exit code: 0
```

```powershell
docker compose down -v
```

```text
docker.exe :  Container module4-api-1 Stopping 
At D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4\verify-lessons.ps1:9 char:15
+     $output = & docker @DockerArgs 2>&1 | Out-String
+               ~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: ( Container module4-api-1 Stopping :String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
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
 Volume module4_pgdata Removing 
 Network module4_default Removing 
 Volume module4_pgdata Removed 
 Network module4_default Removed
Exit code: 0
```

```powershell
docker compose up -d --wait
```

```text
docker.exe :  Network module4_default Creating 
At D:\VinchhiengKhlim\Techpreneur 2.0\AI Engineer and Deployment\Dichi Learning\Module 4\verify-lessons.ps1:9 char:15
+     $output = & docker @DockerArgs 2>&1 | Out-String
+               ~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: ( Network module4_default Creating :String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
 Volume module4_pgdata Creating 
 Volume module4_pgdata Creating 
 Network module4_default Creating 
 Volume module4_pgdata Created 
 Volume module4_pgdata Created 
 Network module4_default Created 
 Network module4_default Created 
 Container module4-db-1 Creating 
 Container module4-db-1 Created 
 Container module4-adminer-1 Creating 
 Container module4-api-1 Creating 
 Container module4-api-1 Created 
 Container module4-adminer-1 Created 
 Container module4-db-1 Starting 
 Container module4-db-1 Started 
 Container module4-db-1 Waiting 
 Container module4-adminer-1 Starting 
 Container module4-adminer-1 Started 
 Container module4-db-1 Healthy 
 Container module4-api-1 Starting 
 Container module4-api-1 Started 
 Container module4-adminer-1 Waiting 
 Container module4-api-1 Waiting 
 Container module4-db-1 Waiting 
 Container module4-adminer-1 Healthy 
 Container module4-db-1 Healthy 
 Container module4-api-1 Healthy
Exit code: 0
```

```powershell
docker compose exec -T db psql -U loans -d loans -c 'SELECT id,status FROM loan_applications WHERE id=101;'
```

```text
 id  | status  
-----+---------
 101 | pending
(1 row)
Exit code: 0
```

## 6. Image sizes, non-root runtime, health status, and excluded build files

```powershell
docker image ls loan-api
```

```text
IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
loan-api:1.0.0   98ecbde59e24        578MB          134MB   U    
loan-api:full    bf10e9fef2dd       2.02GB          508MB        
loan-api:slim    22529c51752c        598MB          139MB
Exit code: 0
```

```powershell
docker compose exec -T api whoami
```

```text
appuser
Exit code: 0
```

```powershell
docker compose ps
```

```text
NAME                IMAGE            COMMAND                  SERVICE   CREATED          STATUS                    PORTS
module4-adminer-1   adminer:4.8.1    "entrypoint.sh php -…"   adminer   18 seconds ago   Up 17 seconds             127.0.0.1:8080->8080/tcp
module4-api-1       loan-api:1.0.0   "uvicorn main:app --…"   api       18 seconds ago   Up 6 seconds (healthy)    0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
module4-db-1        postgres:17      "docker-entrypoint.s…"   db        19 seconds ago   Up 17 seconds (healthy)   5432/tcp
Exit code: 0
```

```powershell
docker compose exec -T api python -c 'import importlib.util,pathlib; print(''/app:'', sorted(p.name for p in pathlib.Path(''/app'').iterdir())); print(''pytest:'',importlib.util.find_spec(''pytest'')); print(''train.py:'',pathlib.Path(''/app/train.py'').exists()); print(''tests:'',pathlib.Path(''/app/tests'').exists())'
```

```text
/app: ['main.py', 'model.joblib', 'schemas.py']
pytest: None
train.py: False
tests: False
Exit code: 0
```

```powershell
docker compose logs --tail 20 api
```

```text
api-1  | INFO:     Started server process [1]
api-1  | INFO:     Waiting for application startup.
api-1  | INFO:     Application startup complete.
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
api-1  | INFO:     127.0.0.1:46452 - "GET /health HTTP/1.1" 200 OK
Exit code: 0
```

