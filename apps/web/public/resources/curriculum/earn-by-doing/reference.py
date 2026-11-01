import json
from pathlib import Path
from lab_engine import run
p=Path(__file__).resolve().parent
source=json.loads((p/'input.json').read_text())
expected=json.loads((p/'expected.json').read_text())
actual=run('earn-by-doing',source)
assert actual==expected,(actual,expected)
print(json.dumps(actual,indent=2))
print('PASS: constructed fixture only; not independent assessment or a live model call.')
