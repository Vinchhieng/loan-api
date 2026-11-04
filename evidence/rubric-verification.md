# Assessment verification

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

```text
docker image inspect vinchhieng/loan-api:1.0.0 loan-api:full
```

```text
[
    {
        "Id": "sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c",
        "RepoTags": [
            "vinchhieng/loan-api:1.0.0"
        ],
        "RepoDigests": [
            "vinchhieng/loan-api@sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-11-04T18:27:22.066053792Z",
        "Config": {
            "User": "appuser",
            "ExposedPorts": {
                "8000/tcp": {}
            },
            "Env": [
                "PATH=/opt/venv/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305",
                "PYTHON_VERSION=3.12.16",
                "PYTHON_SHA256=b5796915dc45ff745cfb4e990a7e7c93d6f546328a102ce31448d69ebc37575c",
                "PYTHONDONTWRITEBYTECODE=1",
                "PYTHONUNBUFFERED=1"
            ],
            "Cmd": [
                "uvicorn",
                "main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "WorkingDir": "/app",
            "Labels": {
                "com.docker.compose.project": "module4",
                "com.docker.compose.service": "api",
                "com.docker.compose.version": "5.6.0"
            },
            "ArgsEscaped": true,
            "Healthcheck": {
                "Test": [
                    "CMD",
                    "python",
                    "-c",
                    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
                ],
                "Interval": 30000000000,
                "Timeout": 3000000000,
                "StartPeriod": 10000000000,
                "Retries": 3
            }
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 578386536,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:a5d6d345f6afa08d7c31272055746d60a838b290bfcc82c0a23e8e984d61a933",
                "sha256:fab99bd4639aec48a77ec4d2e3564c0907e0e1e962bbf773219a0b503a168955",
                "sha256:bca572b9549074f7cbc5f2d9d29f589038ff21c5f68cef2965167a33f177a9c0",
                "sha256:cae4cb2b5e819765b847e67faa443b377607452f2ec949d142cad15d9d7ea0b3",
                "sha256:b962f1f163c3733c5feb2dc7d3e2a8bffc2f450121ff88e5a7e2efdf23a1314d",
                "sha256:6e7165fa054e1e9408d55fc35f1ffcccaf834f96e1beba6c7ecc4dd87a6b9a49",
                "sha256:10d759994fb48ca1698f3a593d4b1ec341829fbab494039b118e73cf32ab99e5",
                "sha256:c034f4dce55587ebb8e4c25a48ecdb09fded9034025416ffbb5936478e298cb1",
                "sha256:4620ee5de968821c262e49918748da97b0fec0ec914d0be4c782c50159dc942c"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-11-04T18:33:06.580148952Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:98ecbde59e24348cf7d9dc1c2d5d22cfe6f40be9d7fdfe2d0d8ff094d2e1534c",
            "size": 856
        },
        "Identity": {
            "Pull": [
                {
                    "Repository": "docker.io/vinchhieng/loan-api"
                }
            ]
        }
    },
    {
        "Id": "sha256:bf10e9fef2dd36ed385c17074d6b62883cbec0c3d1038563e8c42ad938eb1578",
        "RepoTags": [
            "loan-api:full"
        ],
        "RepoDigests": [
            "loan-api@sha256:bf10e9fef2dd36ed385c17074d6b62883cbec0c3d1038563e8c42ad938eb1578"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-11-04T18:29:43.709635154Z",
        "Config": {
            "ExposedPorts": {
                "8000/tcp": {}
            },
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305",
                "PYTHON_VERSION=3.12.16",
                "PYTHON_SHA256=b5796915dc45ff745cfb4e990a7e7c93d6f546328a102ce31448d69ebc37575c"
            ],
            "Cmd": [
                "uvicorn",
                "main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload"
            ],
            "WorkingDir": "/app",
            "ArgsEscaped": true
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 2022429181,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:a7eea2ea48f1fe9bbea4c9bfe79b0921a63d76281466618b89b02f51170e2e5b",
                "sha256:5aa0bbcb6d7b5c543dacfd6f36ee3b5c59e06c7cd803a0a557a9ff691df5e01a",
                "sha256:57211054af4ad11d76ec0a5d765d4e93d29b539cc5828e4a55ae8630fcfe946d",
                "sha256:ae11e9196e0a4482564382ed5ea2f73a15c7fc256c8df555c183294f5fabc9ab",
                "sha256:17b7ccf02d190cb32137a539b5f704194e186aa70f14cdd782d5177c4b98eaef",
                "sha256:5567aada98ecc5700323e6bb1f0b8b81e90538aaeed9ad799982caf72f58ac02",
                "sha256:1bf0463e6c12de1285986929aee9550a350cffaa62a69316e13f4ad0f8057b6e",
                "sha256:6af19c52e7824377cfaf25d7f27c6b36477e2c53b86e20af219cdcf60c0f1cad",
                "sha256:9dc4fad34d6736aacff982671af4efce86d3c17a3f1282953f868225280f5746",
                "sha256:b6f7fa9eb6ccbf9d1b0563e706341e3e42a4aec750c18c1fd384a2ba49a5fa2e",
                "sha256:3fb8860b9cd31abb20c9af8d8fee40420f7155d58e5b9c64e205f48afd529e95",
                "sha256:5d294de89826e54b9aa374fbc36eef717d2ea5dd30e58fb85b0598d373c5b876"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-11-04T18:30:04.067532177Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:bf10e9fef2dd36ed385c17074d6b62883cbec0c3d1038563e8c42ad938eb1578",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "sg2edm7pl12p6zinku9ble3bm",
                    "CreatedAt": "2026-11-04T18:30:38.05079848Z"
                }
            ]
        }
    }
]
Exit code: 0
```

```text
docker tag vinchhieng/loan-api:1.0.0 loan-api:1.0.0
```

```text

Exit code: 0
```

```text
docker stop loan-api-registry
```

```text
loan-api-registry
Exit code: 0
```

```text
docker compose up -d --wait
```

```text
 Container module4-db-1 Running
 Container module4-adminer-1 Running
 Container module4-api-1 Creating
 Container module4-api-1 Created
 Container module4-db-1 Waiting
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

```text
docker compose exec -T api whoami
```

```text
appuser
Exit code: 0
```

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
