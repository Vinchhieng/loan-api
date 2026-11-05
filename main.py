import os
import hmac
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from schemas import LoanApplication, Prediction
from loan_store import LoanStore
from loan_routes import router
from risk_model import ChampionModel

MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")
GIT_SHA = os.getenv("RENDER_GIT_COMMIT", os.getenv("GIT_SHA", "local"))
API_KEY = os.getenv("API_KEY", "")
APPLICATION_DB_PATH = os.getenv('APPLICATION_DB_PATH', 'loan-api.db')
CHAMPION_PATH = os.getenv('CHAMPION_PATH', 'champion.json')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load trusted artifacts only: Joblib deserialization can execute code.
    model = joblib.load(MODEL_PATH)
    if not all(key in model for key in ("model", "version", "features")):
        raise ValueError("Invalid model artifact")
    app.state.model = model
    app.state.champion = ChampionModel(CHAMPION_PATH)
    app.state.store = LoanStore(APPLICATION_DB_PATH)
    yield
    del app.state.model


app = FastAPI(title="Loan Prediction API", version="1.0.0", lifespan=lifespan,
              description="Course deployment exercise. Model trained on synthetic data; not for real lending decisions.")
app.include_router(router)


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    if API_KEY and (request.url.path.startswith("/api/") or request.url.path == "/predict"):
        supplied = request.headers.get("x-api-key", "")
        if not hmac.compare_digest(supplied.encode(), API_KEY.encode()):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid API key"})
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": app.state.model["version"], "git_sha": GIT_SHA,
            "champion": {"name": "loan-default", "version": app.state.champion.version,
                         "run_id": app.state.champion.artifact['run_id'], "synthetic_training_data": True}}


@app.post("/predict", response_model=Prediction)
@app.post("/api/v1/predictions", response_model=Prediction)
def predict(application: LoanApplication):
    artifact = app.state.model
    values = application.model_dump()
    features = [[values[name] for name in artifact["features"]]]
    approved = bool(artifact["model"].predict(features)[0])
    return Prediction(prediction="approved" if approved else "rejected",
                      model_version=artifact["version"], synthetic_training_data=True)
