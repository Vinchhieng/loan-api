# Capstone evidence tracker

Status: preparation in progress. No production release has been verified.

Repository: https://github.com/Vinchhieng/loan-api

| Requirement | Evidence | Status |
| --- | --- | --- |
| Green main CI; required test check | Actions run URL and branch-rule screenshot | Pending |
| Live OpenAPI comparison | Save live schema and compare with Module 2 | Pending |
| Tracked runs, champion, memo | Module 5 evidence/lifecycle/report.md and registry.json | Available locally; not yet packaged |
| Drift chart and alert plan | Module 5 evidence/lifecycle/drift.png and report.md | Available locally; not yet packaged |
| Improvement through PR | API-key protection includes legacy prediction route; health reports release SHA | Implemented locally; PR pending |
| Pipeline graph, verify log, live health | Actions test -> deploy -> verify | Workflow prepared; execution pending |
| Merge to live timing | PR merged_at to first verified matching healthy SHA, UTC | Pending; verification wait alone is not this timing |
| API-key checks and TLS grade | Public health; missing key 401; valid key 200; additionally invalid key 401 | Live checks pending |
| Bad-release drill and prevention test | Failing PR/run or rollback run, recovered health, regression test | Pending; exact course drill not supplied |
| Recovery timing | Rollback request UTC to first healthy recovered SHA UTC | Pending |
| Five-minute slides | Architecture, decision, trade-off, next steps | Pending |

## Setup remaining

1. Merge a green foundation PR after configuring a branch rule requiring the `test` job.
2. Create a Render web service linked to this repository, Docker runtime, Dockerfile.prod, health path /health. Configure API_KEY privately. Keep automatic deployments off for pipeline-controlled releases. Initial service creation can trigger a deployment; record this bootstrap separately and do not claim it as a pipeline release.
3. Store Render's deploy hook as RENDER_DEPLOY_HOOK_URL in GitHub's production environment. Store the same API_KEY there; set repository variable APP_URL to the HTTPS service URL. Do not paste secrets into documents or logs.
4. Run the release workflow on main. Capture the graph and verify log; use the first verified health SHA timestamp for release evidence.
5. Ship a subsequent improvement via PR and measure merge to live. Revert any bad release via PR so recovery also passes through the pipeline.

## Contract differences identified before deployment

Module 2 uses server prefix /api/v1 and defines application creation/list/get/update, borrower application listing, and application-bound predictions. The current deployment project implements standalone POST /api/v1/predictions plus legacy POST /predict and GET /health. The Module 2 application routes are absent: this remains a contract gap, not an endpoint match. The API-key lesson replaces the specification's Bearer authentication with X-API-Key; document that intentional authentication change. The legacy route receives identical protection to prevent bypassing authentication.

## Model limitation

The current Docker entrypoint serves the Module 4 synthetic decision tree. Module 5's registered champion is a separate logistic-regression lifecycle service. Gathering its lifecycle evidence does not prove the Docker service serves that champion. Champion integration remains an explicit capstone decision to resolve before final submission. All models use synthetic data and must not be used for real lending.
