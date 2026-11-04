"""Train a reproducible educational model. No real borrower data is used."""
import argparse
from pathlib import Path

import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier


def train(version: str, out: str):
    rng = np.random.default_rng(42)
    income = rng.uniform(12000, 150000, 6000)
    amount = rng.uniform(100, 80000, 6000)
    score = rng.integers(300, 851, 6000)
    features = np.column_stack((income, amount, score))
    # Synthetic labels illustrate training, not real credit outcomes.
    labels = ((score >= 650) & (amount / income <= 0.5)).astype(int)
    model = DecisionTreeClassifier(max_depth=8, random_state=42).fit(features, labels)
    destination = Path(out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "version": version,
                 "features": ["annual_income", "loan_amount", "credit_score"],
                 "training_data": "synthetic", "seed": 42}, destination)
    print(f"Saved model {version} to {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--out", default="model.joblib")
    args = parser.parse_args()
    train(args.version, args.out)
