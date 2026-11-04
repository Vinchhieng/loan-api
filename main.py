import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/model.json"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    if model.get("kind") != "demonstration_rules_v1":
        raise ValueError("Unsupported model format")
    app.state.model = model
    yield


app = FastAPI(title="Loan Prediction API", version="1.0.0", lifespan=lifespan,
              description="Educational demonstration only. Uses illustrative rules, not a trained credit model.")


class LoanApplication(BaseModel):
    annual_income: float = Field(gt=0, le=1_000_000_000, examples=[60000])
    loan_amount: float = Field(gt=0, le=1_000_000_000, examples=[10000])
    credit_score: int = Field(ge=300, le=850, examples=[720])


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/predict")
def predict(application: LoanApplication):
    model = app.state.model
    approved = (application.credit_score >= model["minimum_credit_score"]
                and application.loan_amount / application.annual_income <= model["maximum_loan_income_ratio"])
    return {"prediction": "approved" if approved else "rejected",
            "model_version": model["version"], "demonstration_only": True}
