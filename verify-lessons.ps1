# Run after building loan-api:slim, loan-api:full, and loan-api:1.0.0.
# The persistence exercise resets only this Compose project's sample database.
$ErrorActionPreference = 'Continue'
$script:lines = @('# Lesson 4.4-4.6 command evidence', '', 'Commands and actual output captured by verify-lessons.ps1. No assessment table was provided; these checks follow the supplied lesson screenshots.', '')
function Heading($text) { $script:lines += @("## $text", '') }
function Run-Docker {
    param([string[]]$DockerArgs, [int]$ExpectedExit = 0)
    $display = 'docker ' + (($DockerArgs | ForEach-Object { if ($_ -match '[\s"'']') { "'" + $_.Replace("'", "''") + "'" } else { $_ } }) -join ' ')
    $output = & docker @DockerArgs 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    $script:lines += @('```powershell', $display, '```', '', '```text', $output.TrimEnd(), "Exit code: $exitCode", '```', '')
    $script:lines | Set-Content -Encoding UTF8 evidence/lesson-verification.md
    if ($exitCode -ne $ExpectedExit) { throw "Unexpected exit code for $display (expected $ExpectedExit)" }
    Write-Output "$display : exit $exitCode"
}
$health = "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
Heading '1. Five API tests and configurable model path'
Run-Docker -DockerArgs @('run','--rm','--mount',"type=bind,source=$((Get-Location).Path)/tests,target=/tests,readonly",'loan-api:slim','python','-m','pytest','-v','-p','no:cacheprovider','/tests')
Run-Docker -DockerArgs @('run','--rm','-e','MODEL_PATH=/missing.joblib','loan-api:1.0.0') -ExpectedExit 3
Heading '2. Read-only model bind mount changes model version without rebuilding'
New-Item -ItemType Directory -Force models | Out-Null
Run-Docker -DockerArgs @('run','--rm','--mount',"type=bind,source=$((Get-Location).Path)/models,target=/models",'loan-api:slim','python','train.py','--version','1.1.0','--out','/models/model.joblib')
Run-Docker -DockerArgs @('run','-d','--name','loan-model-switch','-e','MODEL_PATH=/models/model.joblib','--mount',"type=bind,source=$((Get-Location).Path)/models,target=/models,readonly",'loan-api:1.0.0')
$poll = "import time,urllib.request; time.sleep(3); print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
Run-Docker -DockerArgs @('exec','loan-model-switch','python','-c',$poll)
Run-Docker -DockerArgs @('rm','-f','loan-model-switch')
Heading '3. Named volume data survives container removal'
Run-Docker -DockerArgs @('volume','create','loan-lesson-notes')
Run-Docker -DockerArgs @('run','--rm','-v','loan-lesson-notes:/data','python:3.12-slim','sh','-c','echo "first run" >> /data/notes.txt; cat /data/notes.txt')
Run-Docker -DockerArgs @('run','--rm','-v','loan-lesson-notes:/data','python:3.12-slim','sh','-c','echo "second run" >> /data/notes.txt; cat /data/notes.txt')
Run-Docker -DockerArgs @('volume','rm','loan-lesson-notes')
Heading '4. Containers reach the API by name without publishing a port'
Run-Docker -DockerArgs @('network','create','loan-lesson-net')
Run-Docker -DockerArgs @('run','-d','--name','loan-network-api','--network','loan-lesson-net','loan-api:1.0.0')
Run-Docker -DockerArgs @('run','--rm','--network','loan-lesson-net','curlimages/curl:8.10.1','--retry','10','--retry-connrefused','--retry-delay','1','--fail','-sS','http://loan-network-api:8000/health')
Run-Docker -DockerArgs @('rm','-f','loan-network-api')
Run-Docker -DockerArgs @('network','rm','loan-lesson-net')
Heading '5. Compose services, seeded database, and database persistence'
Run-Docker -DockerArgs @('compose','up','-d','--wait')
Run-Docker -DockerArgs @('compose','ps')
Run-Docker -DockerArgs @('compose','exec','-T','api','python','-c',$health)
Run-Docker -DockerArgs @('compose','exec','-T','db','psql','-U','loans','-d','loans','-c','SELECT b.full_name,a.amount_usd,a.term_months,a.status FROM loan_applications a JOIN borrowers b ON b.id=a.borrower_id ORDER BY a.id;')
Run-Docker -DockerArgs @('compose','exec','-T','db','psql','-U','loans','-d','loans','-c',"UPDATE loan_applications SET status='approved' WHERE id=101;")
Run-Docker -DockerArgs @('compose','down')
Run-Docker -DockerArgs @('compose','up','-d','--wait')
Run-Docker -DockerArgs @('compose','exec','-T','db','psql','-U','loans','-d','loans','-c','SELECT id,status FROM loan_applications WHERE id=101;')
# This project was just seeded with the lesson's fictional records.
Run-Docker -DockerArgs @('compose','down','-v')
Run-Docker -DockerArgs @('compose','up','-d','--wait')
Run-Docker -DockerArgs @('compose','exec','-T','db','psql','-U','loans','-d','loans','-c','SELECT id,status FROM loan_applications WHERE id=101;')
Heading '6. Image sizes, non-root runtime, health status, and excluded build files'
Run-Docker -DockerArgs @('image','ls','loan-api')
Run-Docker -DockerArgs @('compose','exec','-T','api','whoami')
Run-Docker -DockerArgs @('compose','ps')
$contents = "import importlib.util,pathlib; print('/app:', sorted(p.name for p in pathlib.Path('/app').iterdir())); print('pytest:',importlib.util.find_spec('pytest')); print('train.py:',pathlib.Path('/app/train.py').exists()); print('tests:',pathlib.Path('/app/tests').exists())"
Run-Docker -DockerArgs @('compose','exec','-T','api','python','-c',$contents)
Run-Docker -DockerArgs @('compose','logs','--tail','20','api')
Write-Output 'Lesson checks complete; run Trivy separately for section 7.'
