import os
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI
from schemas import LoanApplication, Prediction

MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load trusted artifacts only: Joblib deserialization can execute code.
    model = joblib.load(MODEL_PATH)
    if not all(key in model for key in ("model", "version", "features")):
        raise ValueError("Invalid model artifact")
    app.state.model = model
    yield
    del app.state.model


app = FastAPI(title="Loan Prediction API", version="1.0.0", lifespan=lifespan,
              description="Course deployment exercise. Model trained on synthetic data; not for real lending decisions.")


@app.get("/health")
def health():
    return {"status": "ok", "model_version": app.state.model["version"]}


@app.post("/predict", response_model=Prediction)
@app.post("/api/v1/predictions", response_model=Prediction)
def predict(application: LoanApplication):
    artifact = app.state.model
    values = application.model_dump()
    features = [[values[name] for name in artifact["features"]]]
    approved = bool(artifact["model"].predict(features)[0])
    return Prediction(prediction="approved" if approved else "rejected",
                      model_version=artifact["version"], synthetic_training_data=True)
