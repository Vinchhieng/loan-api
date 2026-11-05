# Capstone evidence tracker

Live service: https://loan-api-vinchhieng-capstone.onrender.com

The authoritative release status is the latest main Actions run, including `verify`. This index records the verified baseline and controlled drill; the submitted report contains final recovery timestamps and screenshots.

Repository: https://github.com/Vinchhieng/loan-api

| Requirement | Evidence | Status |
| --- | --- | --- |
| Green main CI; required test check | Main baseline run 41977811694 passed all three jobs; main requires test with administrator bypass disabled | Recorded |
| Live OpenAPI comparison | All six Module 2 operation/path pairs matched; the direct score preview adds a fourth operational/legacy route | Recorded |
| Tracked runs, champion, memo | Six Module 5 runs and registry metadata; numeric serving snapshot identifies the exact champion run | Gathered |
| Drift chart and alert plan | Fourteen-day synthetic chart and calibrated 95th/99th percentile alert policy in submitted evidence | Gathered |
| Improvement through PR | PR #1 security/pipeline and PR #3 application API/champion integration | Merged |
| Pipeline graph, verify log, live health | Main baseline run 41977811694; pipeline provisions even the first Render service | Passed |
| Merge to live timing | PR #3 merged 06:02:49Z; first matching healthy observation 06:04:59.137514Z | 130.137514 seconds |
| API-key checks and TLS grade | Application list: missing 401, invalid 401, valid 200; public health; SSL Labs A on both endpoints | Recorded |
| Bad-release drill and prevention test | PR #6 loan-limit regression failed the required test and was closed unmerged. PR #8 inverted direct score: live Swagger returned 0.722 instead of 0.278 | Demonstrated |
| Recovery | Render rollback restored pipeline-built SHA be1aff3 and the correct 0.278. PR #9 restores main and adds numerical CI/live checks | Final observed duration in submitted report |
| Five-minute slides | Architecture, frozen-model decision, ephemeral-storage trade-off, operational timings, next steps | Supplied with report |

## Operational setup

1. Main requires a PR, passing test, and an up-to-date branch. These rules also apply to administrators.
2. The pipeline now creates the free Render Docker service itself, with Dockerfile.prod, /health, API_KEY, and auto-deploy disabled. Do not create or deploy it by hand.
3. GitHub repository secrets RENDER_API_KEY and API_KEY and the RENDER_OWNER_ID variable are configured. Secret values are not committed. The deploy job emits the public app URL for the verify job; no APP_URL variable or deploy-hook secret is needed.
4. Every main merge runs test, deploy and verify. Artifacts retain the deployment request, live health/checks, and OpenAPI. A failed verify job means release verification failed even if health is green.
5. Forward releases use the PR and pipeline route. The subsequently supplied Hands-on 1 explicitly requires a dashboard rollback: Render deployment dep-dbm33mrm8hqs73ejc6kg restored existing pipeline artifact dep-dbm30tuc6qcc73fr63r0. No dashboard Manual Deploy was used. The submission discloses dashboard recovery rather than claiming that it was a pipeline action. This is a literal exception to the capstone's pipeline-only wording for trainer interpretation.

## Supplied Hands-on 1 drill

The application-bound champion probability already had exact tests. PR #7 added the lesson's direct score preview in main.py without deleting those protections; its initial contract test checked authentication, response range, version, and invalid inputs. PR #8 changed only its return expression to round(1 - probability, 3); all 31 existing tests passed. Live /docs demonstrated 0.722 for the recorded Module 5 applicant instead of the correct rounded 0.278. Render rollback was requested at 07:35:54Z; the healthy baseline SHA was observed at 07:36:53.518Z, and the correct Swagger result at 07:37:08.547Z (74.547 seconds to observed business recovery).

PR #9's new regression test first failed against the inversion, then all 32 tests passed after restoration. It also adds numerical preview verification to the pipeline. The bad release's verify job failed on credential synchronization after API-key rotation, not on the numerical defect; the live Swagger result is the numerical detection evidence. The earlier PR #4/#5 term-validation drill remains additional historical evidence.

## Contract differences identified before deployment

All six required operation/path pairs are implemented with the /api/v1 server prefix. Intentional changes: X-API-Key replaces Bearer authentication; four operational/legacy routes are added, including the direct score preview; manually validated pagination query schemas use strings; creation for an unknown borrower additionally returns 404; generated OpenAPI is 3.1 instead of 3.0. See [application documentation](./APPLICATIONS.md).

## Model limitation

Application-bound predictions serve the exact frozen Module 5 champion, version 1, run 4e001c82aed946b8a11950c3b7278761. Its numeric export records provenance and reproduces the reference MLflow probability within 1e-12. The original decision tree remains on legacy standalone routes; health distinguishes both models. All data is synthetic. Free-tier SQLite storage is erased when the container filesystem is replaced; durable PostgreSQL and independent outcome validation remain next steps. Never use this classroom service for real lending.

## Pull request

[Security/pipeline PR #1](https://github.com/Vinchhieng/loan-api/pull/1), [deployment-response fix #2](https://github.com/Vinchhieng/loan-api/pull/2), [application/champion PR #3](https://github.com/Vinchhieng/loan-api/pull/3), [controlled fault #4](https://github.com/Vinchhieng/loan-api/pull/4). The new [supported-term regression test](./tests/test_applications.py) fails on the bad implementation and passes after restoration.
