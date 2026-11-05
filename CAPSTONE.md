# Capstone evidence tracker

Status: preparation in progress. No production release has been verified.

Repository: https://github.com/Vinchhieng/loan-api

| Requirement | Evidence | Status |
| --- | --- | --- |
| Green main CI; required test check | PR #1 test run succeeded; main and required branch rule still pending | In progress |
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
2. The pipeline now creates the free Render Docker service itself, with Dockerfile.prod, /health, API_KEY, and auto-deploy disabled. Do not create or deploy it by hand.
3. GitHub repository secrets RENDER_API_KEY and API_KEY and the RENDER_OWNER_ID variable are configured. Secret values are not committed. The deploy job emits the public app URL for the verify job; no APP_URL variable or deploy-hook secret is needed.
4. Merge the green PR and run the release workflow on main. Capture the graph and verify log; use the first verified health SHA timestamp for release evidence. Retain deployment-request and release-evidence artifacts.
5. Ship a subsequent improvement via PR and measure merge to live. Revert any bad release via PR so recovery also passes through the pipeline.

## Contract differences identified before deployment

Module 2 uses server prefix /api/v1 and defines application creation/list/get/update, borrower application listing, and application-bound predictions. The current deployment project implements standalone POST /api/v1/predictions plus legacy POST /predict and GET /health. The Module 2 application routes are absent: this remains a contract gap, not an endpoint match. The API-key lesson replaces the specification's Bearer authentication with X-API-Key; document that intentional authentication change. The legacy route receives identical protection to prevent bypassing authentication.

## Model limitation

The current Docker entrypoint serves the Module 4 synthetic decision tree. Module 5's registered champion is a separate logistic-regression lifecycle service. Gathering its lifecycle evidence does not prove the Docker service serves that champion. Champion integration remains an explicit capstone decision to resolve before final submission. All models use synthetic data and must not be used for real lending.

## Pull request

[PR #1](https://github.com/Vinchhieng/loan-api/pull/1). Its initial test run [41972609326](https://github.com/Vinchhieng/loan-api/actions/runs/41972609326) passed tests and the production image build. The pipeline-only provisioning update must pass its own CI run before merge.
