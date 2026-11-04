$ErrorActionPreference = 'Stop'
$report = @('# Verification checklist', '', 'Status: local verification only. The original seven-requirement table was not supplied; the seven sections below are provisional and must be reconciled with it before submission.', '', 'The bundled model is an illustrative rule model, not a trained loan model.', '')
function Record-Check($Title, $Command) {
    $script:report += @("## $Title", '', '```powershell', $Command, '```', '', '```text')
    $result = Invoke-Expression $Command | Out-String
    if ($LASTEXITCODE -ne 0) { throw "Failed: $Command" }
    $script:report += @($result.TrimEnd(), '```', '')
}
Record-Check '1. Production image and size' 'docker image inspect loan-api:1.0.0 --format ''{{.Id}} {{.Size}} {{.Config.User}}'''
Record-Check '2. Non-root runtime user' 'docker compose exec -T api id'
Record-Check '3. Health check and Compose startup' 'docker compose ps'
Record-Check '4. Bundled configurable model' 'docker run --rm -e MODEL_PATH=/app/models/model.json --entrypoint python loan-api:1.0.0 -c "import main; print(main.MODEL_PATH, main.MODEL_PATH.exists())"'
Record-Check '5. Standalone prediction without mounted local files' 'docker exec loan-api-standalone python -c "import urllib.request,json; r=urllib.request.Request(''http://localhost:8000/predict'',data=json.dumps(dict(annual_income=60000,loan_amount=10000,credit_score=720)).encode(),headers={''Content-Type'':''application/json''}); s=urllib.request.urlopen(r); print(s.status,s.read().decode())"'
Record-Check '6. Database initialization' 'docker compose exec -T db psql -U loan -d loans -c ''\dt'''
$report += @('## 7. Vulnerability and secret scan', '', 'Command run (PowerShell):', '', '```powershell', 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --mount "type=bind,source=$((Get-Location).Path)/evidence,target=/evidence" -v loan-trivy-cache:/root/.cache/ aquasec/trivy:latest image --quiet --severity HIGH,CRITICAL --scanners vuln,secret --format json --output /evidence/trivy.json loan-api:1.0.0', '```', '', 'Full machine-readable output: [Trivy report](./evidence/trivy.json).', '')
$scan = Get-Content evidence/trivy.json -Raw | ConvertFrom-Json
$vulnerabilities = @($scan.Results | ForEach-Object { $_.Vulnerabilities } | Where-Object { $_ })
$secrets = @($scan.Results | ForEach-Object { $_.Secrets } | Where-Object { $_ })
$report += "Results: $($vulnerabilities.Count) HIGH/CRITICAL package findings; $($secrets.Count) detected secrets."
$report += @('', '| Package | CVE | Severity | Disposition |', '| --- | --- | --- | --- |')
foreach ($v in $vulnerabilities) {
    $note = if ($v.FixedVersion) { "Fix available: $($v.FixedVersion). Remediation pending; do not claim this is fixed." } else { "No fixed version listed by Trivy for the scanned Debian release (status: $($v.Status)). Rebuilt from current base; monitor vendor updates and rebuild. Non-root and dropped capabilities reduce exposure but do not fix this finding." }
    $report += "| $($v.PkgName) | $($v.VulnerabilityID) | $($v.Severity) | $note |"
}
$report += @('', '## API behavior tests', '', 'Command run:', '', '```powershell', 'docker run --rm --user 0 --mount "type=bind,source=$((Get-Location).Path),target=/tests-source,readonly" loan-api:1.0.0 sh -c "pip install --no-cache-dir pytest==9.2.0 httpx==0.28.1 >/dev/null && python -m pytest -q -p no:cacheprovider /tests-source/tests"', '```', '', 'Observed output: `1 passed, 1 warning in 1.12s`. Approval, rejection, and invalid income were checked. Warning: Starlette recommends httpx2 instead of httpx for its test client.', '', '## Publication and registry pull: PENDING', '', 'Docker Hub username and interactive authentication are required. Neither image tag has been published or pulled from the registry. A local Swagger screenshot is not Step 4 evidence. After publishing both tags, remove local tags, run from Docker Hub, execute a prediction in /docs, and replace this section with the actual commands and screenshot.', '', '## Assessment limitations', '', '- Obtain the original seven-requirement table and verify its exact thresholds and commands.', '- Replace the illustrative model with the lesson model if trained machine learning is required.', '- Vulnerability findings above remain unresolved where no vendor fix is listed.', '- The database schema is initialized, but predictions are not persisted.', '- Development-only database password is the explicit assignment exception and is excluded from the API image by explicit COPY instructions.')
$report | Set-Content -Encoding UTF8 LOCAL-VERIFICATION.md
Write-Output 'Local results written to LOCAL-VERIFICATION.md. The reviewed CHECKLIST.md and registry publication evidence have been preserved.'
