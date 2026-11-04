# Loan API

Educational FastAPI container deployment project. **The included JSON model uses illustrative rules; it is not a trained loan prediction model and must not be used for real lending decisions.** The original lesson model and seven-requirement table were not supplied.

## Run

```powershell
docker compose up --build -d
```

Open http://localhost:8000/docs. Expand `POST /predict`, click **Try it out**, and execute:

```json
{"annual_income":60000,"loan_amount":10000,"credit_score":720}
```

The API runs independently of PostgreSQL. Compose includes a development database and initializes a predictions table for the module's database exercise; the API does not persist predictions.

Local verification screenshot (before registry publication): [Swagger HTTP 200](./evidence/local-docs-200.png). This does not replace the required screenshot after pulling from Docker Hub.

`MODEL_PATH` selects a JSON model file using the included schema. The default model is bundled in the image, so standalone runs need no local files. An invalid or missing model prevents startup.

## Publish

Authenticate interactively; never store credentials in this repository. Replace YOUR_USERNAME below with your Docker Hub username.

```powershell
docker login
docker tag loan-api:1.0.0 YOUR_USERNAME/loan-api:1.0.0
docker tag loan-api:1.0.0 YOUR_USERNAME/loan-api:latest
docker push YOUR_USERNAME/loan-api:1.0.0
docker push YOUR_USERNAME/loan-api:latest
```

After publishing, stop Compose and remove the specific local tags (keep database volumes):

```powershell
docker compose down
docker image rm YOUR_USERNAME/loan-api:1.0.0 YOUR_USERNAME/loan-api:latest loan-api:1.0.0
docker run --rm -p 8000:8000 YOUR_USERNAME/loan-api:1.0.0
```

Open `/docs`, send the example request, and save a screenshot showing HTTP 200. Check Docker Hub lists both tags. See [CHECKLIST.md](./CHECKLIST.md) for actual validation status.
