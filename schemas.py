from typing import Literal

from pydantic import BaseModel, Field


class LoanApplication(BaseModel):
    annual_income: float = Field(gt=0, le=1_000_000_000, examples=[60000])
    loan_amount: float = Field(gt=0, le=1_000_000_000, examples=[10000])
    credit_score: int = Field(ge=300, le=850, examples=[720])


class Prediction(BaseModel):
    prediction: Literal["approved", "rejected"]
    model_version: str
    synthetic_training_data: bool
