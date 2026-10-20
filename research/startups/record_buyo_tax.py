"""Record the BUYO Vietnam parent row; do not mix in its branch or Singapore entity."""
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
snapshot = 'sources/buyo_tax_0110114634.txt'
text = (DATA / snapshot).read_text(encoding='utf-8')
lines = text.splitlines()
start = next(i for i, line in enumerate(lines) if line.split('\t') == ['1', '0110114634', ''])
quote = '\n'.join(lines[start:start + 3])
legal_name = 'CÔNG TY TNHH GIẢI PHÁP CÔNG NGHỆ BUYO'
assert legal_name in quote and quote.count('0110114634') == 1
assert '0110114634-001' not in quote
with (DATA / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
company = next(c for c in candidates if c['id'] == 'S056')
company.update(legal_name=legal_name, tax_id='0110114634', country='VN')
company['notes'] = ('Official Vietnam parent tax0110114634 active20Oct2026, exact legal name matches Techport provider profile. '
    'Parent registered address Hanoi; Techport HCMC contact address and active HCMC branch0110114634-001 are not substituted for parent. '
    'Singapore202313125C remains separate. Physical bio-composite/resin products; company process description not independent biodegradation/safety verification. '
    'P4G16Apr2025grant release is recent discovery; programme Active observed14Oct2026 and own ISPAE conference26Jun2026 are distinct owners/origins. '
    'No current capacity, certifications, carbon reduction, paid sales or grant-disbursement audit.')
record = dict(id='E_BUYO_TAX_20261020', company_id='S056', kind='tax', tax_id='0110114634',
    legal_name=legal_name, status='NNT đang hoạt động', quote=quote, snapshot=snapshot,
    sha256=hashlib.sha256(text.encode()).hexdigest(), url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp',
    publisher_owner='Cục Thuế', retrieved_at='2026-10-20', checked_at='2026-10-20', row_scope='parent_company',
    reviewed=True, reviewer='Codex: exact official parent row read from user-completed lookup tab',
    caveat='Parent row only. Separate branch also shown active but excluded from this quote; no Singapore tax substitution, representative or product/certification audit.')
assert not validate_evidence(record, date(2026, 10, 20), DATA)
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
print('Recorded exact BUYO Vietnam parent tax row; branch and Singapore remain separate.')
