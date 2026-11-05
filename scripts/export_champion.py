"""Export this project's trusted Module 5 sklearn champion as numeric JSON.

Requires skops in the offline training environment, not in the serving image.
"""
import argparse
import hashlib
import json
from pathlib import Path

import skops.io

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=Path, required=True)
parser.add_argument('--registry', type=Path, required=True)
parser.add_argument('--parity', type=Path, required=True)
parser.add_argument('--out', type=Path, default=Path('champion.json'))
args = parser.parse_args()
registry = next(row for row in json.loads(args.registry.read_text()) if row['alias'] == 'champion')
model = skops.io.load(args.model)
scaler, classifier = [step for _, step in model.steps]
assert classifier.classes_.tolist() == [0, 1]
assert type(scaler).__name__ == 'StandardScaler'
assert type(classifier).__name__ == 'LogisticRegression'
artifact = {
    'model_name': 'loan-default', 'registry_version': registry['version'],
    'alias_at_export': 'champion', 'run_id': registry['run_id'],
    'source_model_sha256': hashlib.sha256(args.model.read_bytes()).hexdigest(),
    'synthetic_training_data': True, 'features': model.feature_names_in_.tolist(),
    'mean': scaler.mean_.tolist(), 'scale': scaler.scale_.tolist(),
    'coefficients': classifier.coef_[0].tolist(), 'intercept': float(classifier.intercept_[0]),
    'reference_case': json.loads(args.parity.read_text())
}
args.out.write_text(json.dumps(artifact, indent=2) + '\n', encoding='utf-8')
print('Exported numeric champion snapshot from run ' + registry['run_id'])
