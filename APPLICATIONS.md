# Application workflow and champion serving

The API implements all six operation/path pairs from the Module 2 specification, including the `/api/v1` server prefix. Create an application for fictional borrower 1 with amount_usd 1500 and term_months 12, then POST to its `/predictions` subresource. No prediction request body is required. Creation returns 201 and Location; decisions only transition pending applications and repeated decisions return 409. Listing returns `{items, next_cursor}`, filters by status/province, and uses an exclusive ascending-ID cursor. Invalid query filters return 400.

## Deliberate specification changes

- X-API-Key replaces Bearer authentication to follow Lesson 6.6. It is required when API_KEY is set, including the legacy prediction alias.
- GET /health, POST /predict, and POST /api/v1/predictions are additional operational/legacy routes. The legacy prediction model remains distinguishable from the champion.
- Creating an application for a nonexistent borrower returns an additional documented 404 behavior.
- Generated OpenAPI uses FastAPI's current schema dialect. Pagination is validated manually to preserve 400 responses; its query parameter schema currently represents incoming query strings rather than Module 2's integer type.
- The four borrowers are fictional demo profiles. The earlier SQL lesson did not include income or repayment history, so this service explicitly enriches those demo profiles with synthetic monthly income, previous-loan counts, and late-payment counts. It does not infer or import anyone's personal financial data.

## Champion provenance

`champion.json` is a numeric export of the exact Module 5 StandardScaler + LogisticRegression champion, registered as loan-default version 1, run 4e001c82aed946b8a11950c3b7278761. It contains the source model's SHA-256, feature order, scaling parameters, coefficients, and a recorded probability-parity reference. The offline exporter reads the existing trusted skops artifact; the serving image does not need MLflow, pandas, or skops and does not unpickle this champion.

At startup the service verifies that its numeric export reproduces the recorded MLflow prediction within 1e-12. Application-bound predictions use this frozen champion snapshot and health reports its registry version and run ID. Alias changes in MLflow take effect only after exporting and shipping a new snapshot through the pipeline; the service never silently changes models.

The original decision-tree model remains available through the two standalone prediction routes for backward compatibility. Health's model_version refers to that legacy model; its champion object identifies the separate application risk model.

## Storage trade-off

SQLite provides transactional decisions and storage across process restarts when the same file remains available. APPLICATION_DB_PATH selects the file. The production container places it in /tmp because the non-root user cannot write the application code directory.

**Render's free container filesystem is ephemeral: redeployment or replacement can erase applications and predictions.** This accepted classroom trade-off avoids adding a paid datastore. Do not store real customer data or use the synthetic model for lending. Durable PostgreSQL storage, authenticated users, real outcomes, and independent model validation are required before a real production lending deployment.

## Verification

The pipeline checks the exact live SHA, public health, missing/invalid/valid API keys on the application list and both prediction aliases, a created application's champion probability, and acceptance of a valid 24-month term. It retains a partial release-evidence artifact even if a later contract check fails.
