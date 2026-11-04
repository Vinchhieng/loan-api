"""Record focused evidence for the supplied seven-row assessment table."""
import json
from pathlib import Path
import subprocess


root = Path(__file__).resolve().parent
lines = ['# Assessment verification', '']


def run(*args):
    result = subprocess.run(['docker', *args], capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    output = result.stdout + result.stderr
    lines.extend(['```text', subprocess.list2cmdline(['docker', *args]), '```', '',
                  '```text', output.rstrip(), f'Exit code: {result.returncode}', '```', ''])
    (root / 'evidence/rubric-verification.md').write_text(
        '\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()) + '\n', encoding='utf-8')
    result.check_returncode()
    return result.stdout


run('exec', 'loan-api-registry', 'whoami')
run('ps', '--filter', 'name=loan-api-registry')
images = json.loads(run('image', 'inspect', 'vinchhieng/loan-api:1.0.0', 'loan-api:full'))
sizes = {'production_bytes': images[0]['Size'], 'full_bytes': images[1]['Size']}
sizes['reduction_percent'] = 100 * (1 - sizes['production_bytes'] / sizes['full_bytes'])
assert sizes['reduction_percent'] >= 40
(root / 'evidence/image-sizes.json').write_text(json.dumps(sizes, indent=2) + '\n', encoding='utf-8')
# Reuse the already published image; ignore-file changes do not change runtime files.
run('tag', 'vinchhieng/loan-api:1.0.0', 'loan-api:1.0.0')
run('stop', 'loan-api-registry')
run('compose', 'up', '-d', '--wait')
run('compose', 'ps')
run('compose', 'exec', '-T', 'api', 'whoami')
run('image', 'ls', 'loan-api')
run('buildx', 'imagetools', 'inspect', 'vinchhieng/loan-api:1.0.0')
run('buildx', 'imagetools', 'inspect', 'vinchhieng/loan-api:latest')
print(json.dumps(sizes, indent=2))
