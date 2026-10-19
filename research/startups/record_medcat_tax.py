"""Attach the exact official parent tax row to the existing reviewed MedCAT dossier."""
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from startup_tool import validate_evidence

DATA = ROOT / 'data/startups'
snapshot = 'sources/medcat_tax_0110578065.txt'
text = (DATA / snapshot).read_text(encoding='utf-8')
lines = text.splitlines()
start = next(i for i, line in enumerate(lines) if line.split('\t') == ['1', '0110578065', ''])
quote = '\n'.join(lines[start:start + 3])
with (DATA / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
company = next(c for c in candidates if c['id'] == 'S026')
assert company['legal_name'] == 'CÔNG TY CỔ PHẦN MEDCAT'
assert company['legal_name'] in quote and quote.count('0110578065') == 1
company.update(tax_id='0110578065', country='VN')
company['notes'] = company['notes'].replace(
    'Parent candidate MST0110578065 from secondary directories only, not official tax or entered as verified ID.',
    'Official single parent tax row0110578065 active19Oct2026; legal name matches company own Hanoi report. Tax status does not verify clinical effectiveness, software security or product approval.')
record = dict(id='E_MEDCAT_TAX_20261019', company_id='S026', kind='tax', tax_id='0110578065',
    legal_name=company['legal_name'], status='NNT đang hoạt động', quote=quote, snapshot=snapshot,
    sha256=hashlib.sha256(text.encode()).hexdigest(), url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp',
    publisher_owner='Cục Thuế', retrieved_at='2026-10-19', checked_at='2026-10-19', row_scope='parent_company',
    reviewed=True, reviewer='Codex: visible official single parent row after authorised CAPTCHA lookup',
    caveat='Parent MedCAT only, not MedCAT TPA; no representative, clinical effectiveness, security or regulatory product approval verified.')
assert not validate_evidence(record, date(2026, 10, 19), DATA)
evidence = [json.loads(line) for line in (DATA / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]
old = next((e for e in evidence if e['id'] == record['id']), None)
if old:
    evidence[evidence.index(old)] = record
else:
    evidence.append(record)
with (DATA / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(candidates[0]))
    writer.writeheader()
    writer.writerows(candidates)
(DATA / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
print('Recorded MedCAT parent tax row; TPA remains separate.')
