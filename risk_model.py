"""Serve a frozen numeric export of the tracked champion without unpickling it."""
import json
import math
from pathlib import Path


class ChampionModel:
    def __init__(self, path):
        self.artifact = json.loads(Path(path).read_text(encoding='utf-8'))
        a = self.artifact
        expected = ['amount_usd', 'term_months', 'monthly_income_usd', 'previous_loans', 'late_payments']
        if a['features'] != expected or a['synthetic_training_data'] is not True:
            raise ValueError('Unexpected champion feature contract or training provenance')
        for name in ('mean', 'scale', 'coefficients'):
            if len(a[name]) != len(expected) or not all(math.isfinite(v) for v in a[name]):
                raise ValueError('Invalid champion numeric parameters')
        if not math.isfinite(a['intercept']) or not all(v > 0 for v in a['scale']):
            raise ValueError('Invalid champion scale or intercept')
        reference = a['reference_case']
        if abs(self.predict(reference['applicant']) - reference['mlflow_probability']) > reference['tolerance']:
            raise ValueError('Champion export does not reproduce the recorded MLflow prediction')

    @property
    def version(self):
        return self.artifact['registry_version']

    def predict(self, values):
        a = self.artifact
        score = a['intercept'] + sum((values[name] - mean) / scale * coefficient
                                    for name, mean, scale, coefficient in
                                    zip(a['features'], a['mean'], a['scale'], a['coefficients']))
        if score >= 0:
            return 1 / (1 + math.exp(-score))
        odds = math.exp(score)
        return odds / (1 + odds)
