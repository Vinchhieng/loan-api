# Capstone preflight evidence

Executed 2026-11-05 on the Module 6 checkout. This is local evidence, not a live production verification.

- Python 3.13.0, project-local environment; dependencies from requirements-dev.txt installed successfully.
- `python train.py`: generated the synthetic decision-tree model, version 1.0.0.
- `python -m pytest -v --junitxml=evidence/capstone/local-tests.xml`: **7 passed**, one Starlette warning about the future test-client migration from httpx to httpx2. No test failures.
- `docker build -f Dockerfile.prod -t loan-api:module6 .`: **exit 0**, using Python 3.12 slim, training in the builder, running as appuser.
- Built image index digest: `sha256:f9e8cf0d7c3e805c8dea90d98d17ca9a0901d8d68a557e6824dc69e0b731c69b`.
- Authentication tests: missing and invalid key return 401; correct key returns 200 on both prediction routes; health remains public.
- SHA test: health reports the configured release SHA.

The local JUnit file is excluded from Git to avoid publishing machine-specific filesystem paths. GitHub Actions uploads its own JUnit artifact.

## Important limits

No Render service is authenticated or configured yet. No live URL, TLS grade, deployment timing, production rollback timing, or successful Actions run is claimed here. Module 2 comparison against a live schema remains pending.
