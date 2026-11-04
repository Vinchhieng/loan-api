# Publication and registry verification

## Compose prediction and request log

```text
docker compose exec -T api python -c "import urllib.request; r=urllib.request.Request('http://localhost:8000/api/v1/predictions',data='{\"annual_income\": 60000, \"loan_amount\": 10000, \"credit_score\": 720}'.encode(),headers={'Content-Type':'application/json'}); s=urllib.request.urlopen(r); print(s.status,s.read().decode())"
```

```text
200 {"prediction":"approved","model_version":"1.0.0","synthetic_training_data":true}
Exit code: 0
```

```text
docker compose logs --tail 10 api
```

```text
api-1  | INFO:     Started server process [1]
api-1  | INFO:     Waiting for application startup.
api-1  | INFO:     Application startup complete.
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
api-1  | INFO:     127.0.0.1:46452 - "GET /health HTTP/1.1" 200 OK
api-1  | INFO:     127.0.0.1:41442 - "GET /health HTTP/1.1" 200 OK
api-1  | INFO:     127.0.0.1:43858 - "GET /health HTTP/1.1" 200 OK
api-1  | INFO:     127.0.0.1:49142 - "POST /api/v1/predictions HTTP/1.1" 200 OK
Exit code: 0
```

## Published tags

```text
docker tag loan-api:1.0.0 vinchhieng/loan-api:1.0.0
```

```text

Exit code: 0
```

```text
docker push vinchhieng/loan-api:1.0.0
```

```text
The push refers to repository [docker.io/vinchhieng/loan-api]
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Layer already exists
f574edac59d9: Waiting
44136fa355b3: Waiting
f574edac59d9: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
f574edac59d9: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Already exists
acca7542dfc7: Waiting
f574edac59d9: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
acca7542dfc7: Waiting
f574edac59d9: Waiting
294e72231f57: Waiting
acca7542dfc7: Waiting
f574edac59d9: Waiting
3eb771151506: Waiting
3eb771151506: Layer already exists
66046de8b609: Waiting
acca7542dfc7: Layer already exists
f574edac59d9: Layer already exists
1d7f6920939a: Waiting
e031ef6dddc7: Waiting
1d7f6920939a: Waiting
e031ef6dddc7: Waiting
66046de8b609: Waiting
1d7f6920939a: Waiting
e031ef6dddc7: Waiting
6dce7b81aa44: Waiting
66046de8b609: Layer already exists
1d7f6920939a: Waiting
e031ef6dddc7: Waiting
6dce7b81aa44: Waiting
6dce7b81aa44: Waiting
1d7f6920939a: Waiting
e031ef6dddc7: Waiting
6dce7b81aa44: Waiting
1d7f6920939a: Waiting
e031ef6dddc7: Waiting
6dce7b81aa44: Waiting
e031ef6dddc7: Waiting
6dce7b81aa44: Waiting
6dce7b81aa44: Waiting
294e72231f57: Pushed
acbfbaebd054: Waiting
acbfbaebd054: Waiting
acbfbaebd054: Waiting
acbfbaebd054: Waiting
acbfbaebd054: Waiting
acbfbaebd054: Waiting
1d7f6920939a: Pushed
acbfbaebd054: Waiting
acbfbaebd054: Waiting
6dce7b81aa44: Pushed
acbfbaebd054: Pushed
e031ef6dddc7: Pushed
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
docker tag loan-api:1.0.0 vinchhieng/loan-api:latest
```

```text

Exit code: 0
```

```text
docker push vinchhieng/loan-api:latest
```

```text
The push refers to repository [docker.io/vinchhieng/loan-api]
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
3eb771151506: Waiting
294e72231f57: Waiting
44136fa355b3: Waiting
6fc242d221a6: Waiting
6fc242d221a6: Waiting
f574edac59d9: Waiting
acca7542dfc7: Waiting
3eb771151506: Waiting
294e72231f57: Already exists
44136fa355b3: Already exists
f574edac59d9: Waiting
acca7542dfc7: Waiting
3eb771151506: Waiting
6fc242d221a6: Waiting
f574edac59d9: Waiting
acca7542dfc7: Waiting
3eb771151506: Waiting
6fc242d221a6: Waiting
6fc242d221a6: Layer already exists
f574edac59d9: Waiting
acca7542dfc7: Waiting
3eb771151506: Waiting
66046de8b609: Waiting
1d7f6920939a: Waiting
3eb771151506: Waiting
66046de8b609: Waiting
1d7f6920939a: Waiting
f574edac59d9: Waiting
acca7542dfc7: Waiting
3eb771151506: Waiting
66046de8b609: Waiting
1d7f6920939a: Waiting
f574edac59d9: Waiting
acca7542dfc7: Waiting
acca7542dfc7: Layer already exists
6dce7b81aa44: Waiting
acbfbaebd054: Waiting
3eb771151506: Layer already exists
66046de8b609: Layer already exists
1d7f6920939a: Layer already exists
e031ef6dddc7: Waiting
f574edac59d9: Layer already exists
e031ef6dddc7: Waiting
6dce7b81aa44: Waiting
acbfbaebd054: Waiting
e031ef6dddc7: Layer already exists
6dce7b81aa44: Waiting
acbfbaebd054: Layer already exists
6dce7b81aa44: Layer already exists
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

## Local image removal and registry run

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
44136fa355b3: Already exists
acbfbaebd054: Pulling fs layer
e031ef6dddc7: Pulling fs layer
6dce7b81aa44: Pulling fs layer
1d7f6920939a: Pulling fs layer
acbfbaebd054: Already exists
e031ef6dddc7: Already exists
6dce7b81aa44: Already exists
1d7f6920939a: Already exists
1d7f6920939a: Pull complete
294e72231f57: Download complete
e031ef6dddc7: Pull complete
6dce7b81aa44: Pull complete
acbfbaebd054: Pull complete
Digest: sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c
Status: Downloaded newer image for vinchhieng/loan-api:1.0.0
fc6c0593f3968f5b510d16417e98bee92d54302d9bda9e3461f5ec8f27e05905
Exit code: 0
```

```text
docker ps --filter name=loan-api-registry
```

```text
CONTAINER ID   IMAGE                       COMMAND                  CREATED         STATUS                   PORTS                                         NAMES
fc6c0593f396   vinchhieng/loan-api:1.0.0   "uvicorn main:app --…"   7 seconds ago   Up 5 seconds (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   loan-api-registry
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

```text
docker image inspect vinchhieng/loan-api:1.0.0 --format {{.Id}}
```

```text
sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c
Exit code: 0
```
