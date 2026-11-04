"""Assemble CHECKLIST.md from recorded command output; does not run checks."""
import json
from pathlib import Path
import re


root = Path(__file__).resolve().parent
lesson = (root / 'evidence/lesson-verification.md').read_text(encoding='utf-8-sig')
lesson = lesson[lesson.index('## 1.'):]
lesson = lesson.replace('## 6.', 'Adminer was also opened in the browser, connected to PostgreSQL using server `db`, and the same join query returned all six expected rows. [Adminer query screenshot](./evidence/adminer-six-rows.png).\n\n## 6.', 1)
scan = json.loads((root / 'evidence/trivy.json').read_text(encoding='utf-8-sig'))
secrets = json.loads((root / 'evidence/repository-secrets.json').read_text(encoding='utf-8-sig'))
findings = [v for result in scan.get('Results', []) for v in result.get('Vulnerabilities', [])]
image_secrets = sum(len(r.get('Secrets', [])) for r in scan.get('Results', []))
repo_secrets = sum(len(r.get('Secrets', [])) for r in secrets.get('Results', []))
lines = ['# Loan API verification checklist', '',
         'Verified against the supplied Lessons 4.4-4.6 exercise screenshots. The exact seven-row assessment table was not supplied; these seven numbered sections group the demonstrated capabilities and are not a claim that an unseen rubric has been satisfied.', '',
         'The image trains and bundles a scikit-learn model using reproducible synthetic data. The original course training script was not available. The API is an educational deployment exercise, not a validated lending model.', '',
         'Production image: `' + scan['Metadata']['ImageID'] + '`.', '',
         'PowerShell wraps some native stderr messages with NativeCommandError metadata. Recorded exit codes distinguish successful commands from the intentionally failing missing-model startup (exit 3).', '',
         lesson,
         '## 7. Image vulnerability and repository secret scans', '',
         'Command executed:', '', '```powershell',
         'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --mount "type=bind,source=$((Get-Location).Path)/evidence,target=/evidence" -v loan-trivy-cache:/root/.cache/ aquasec/trivy:latest image --quiet --severity HIGH,CRITICAL --scanners vuln,secret --format json --output /evidence/trivy.json loan-api:1.0.0',
         '```', '',
         f'Actual result: {sum(v["Severity"] == "HIGH" for v in findings)} HIGH package findings; {sum(v["Severity"] == "CRITICAL" for v in findings)} CRITICAL; {image_secrets} detected image secrets. Full output: [Trivy JSON](./evidence/trivy.json).', '',
         '| Package | CVE | Severity | Disposition |', '| --- | --- | --- | --- |']
for v in findings:
    if v.get('FixedVersion'):
        note = f'Fix available in {v["FixedVersion"]}; remediation remains pending.'
    else:
        note = (f'No fixed version listed for the scanned Debian release (status: {v.get("Status", "unknown")}). '
                'Rebuilt from the current base; monitor vendor fixes and rebuild. Non-root operation does not eliminate this vulnerability.')
    lines.append(f'| {v["PkgName"]} | {v["VulnerabilityID"]} | {v["Severity"]} | {note} |')
lines.extend(['', 'Repository scan command:', '', '```powershell',
              'docker run --rm --mount "type=bind,source=$((Get-Location).Path),target=/src,readonly" --mount "type=bind,source=$((Get-Location).Path)/evidence,target=/evidence" aquasec/trivy:latest fs --quiet --scanners secret --skip-dirs /src/.git --skip-dirs /src/evidence --format json --output /evidence/repository-secrets.json /src',
              '```', '', f'Actual result: {repo_secrets} detected repository secrets. [Raw output](./evidence/repository-secrets.json). Scan excludes Git metadata and generated evidence. Detection is not a guarantee that no secret exists. The development-only Compose database password is the assignment exception.', '',
              '## Publish both tags and pull from the registry', '',
              'The following is actual output from [verify-release.py](./verify-release.py). Repeated layer progress is omitted here; [the complete log](./evidence/registry-verification.md) is retained.', ''])
registry = (root / 'evidence/registry-verification.md').read_text(encoding='utf-8')
# Omit repetitive transport progress while retaining commands, digests and results.
registry = '\n'.join(line for line in registry.splitlines()
                     if not re.match(r'^[a-f0-9]{12}: (Waiting|Layer already exists|Already exists|Pushed|Pulling fs layer|Pull complete|Download complete|Mounted from)', line))
lines.extend([registry, '',
              'Both tags were also confirmed on the public [Docker Hub tags page](https://hub.docker.com/r/vinchhieng/loan-api/tags). [Tags screenshot](./evidence/docker-hub-tags.png).', '',
              'After removing the local image tags, the registry run downloaded the image record from Docker Hub. Docker reused cached layers. No local files were mounted (`Mounts: []`).', '',
              'Opened `/docs` on the fresh registry container, used Try it out on POST /predict with annual_income 60000, loan_amount 10000, credit_score 720, and received HTTP 200. [Required Step 4 screenshot](./evidence/registry-docs-200.png).', '',
              '## Scope and remaining assessment uncertainty', '',
              '- The exact seven-row requirements table and original model implementation were not supplied. Compare this evidence to that table before claiming all seven assessment criteria are satisfied.',
              '- Training data and labels are synthetic; no claim of real loan-prediction accuracy is made.',
              '- The database reproduces the supplied sample records and persistence exercise; the prediction endpoint does not write to those tables.',
              '- The API image scan covers the published API image. It does not certify the separate PostgreSQL or lesson-pinned Adminer images.',
              '- The unresolved HIGH findings are documented individually above; no zero-vulnerability claim is made.', ''])
(root / 'CHECKLIST.md').write_text('\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()) + '\n', encoding='utf-8')
print('CHECKLIST.md assembled from recorded evidence.')
