"""Record the Voria parent row visibly returned by the official tax portal."""
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from startup_tool import normal, validate_evidence

DATA = ROOT / 'data/startups'
snapshot = 'sources/voria_tax_3604052503.txt'
text = (DATA / snapshot).read_text(encoding='utf-8')
legal_name = 'CÔNG TY TNHH CÔNG NGHỆ VORIA SOLUTION'
lines = text.splitlines()
start = next(i for i, line in enumerate(lines) if line.split('\t') == ['1', '3604052503', ''])
quote = '\n'.join(lines[start:start + 3])
assert legal_name in quote and 'NNT đang hoạt động' in quote
assert quote.count('3604052503') == 1

with (DATA / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
company = next(c for c in candidates if c['id'] == 'S035')
assert company['brand'] == 'VORIA SOLUTION'
company.update(legal_name=legal_name, tax_id='3604052503', country='VN')
company['notes'] = ('Official parent tax row active on 2026-10-19 after user completed lookup. '
    'Official legal name contains exact VORIA SOLUTION brand; English App Store provider and VN developer address corroborate identity. '
    'Hybrid app/Hub; SIHUB exhibition and developer app update are distinct events/owners. '
    'ICU trial self-report, not clinical validation or commercial acceptance. '
    'Google Play encryption declaration unresolved; no runtime security test, medical approval or representative verified.')

evidence = [json.loads(line) for line in (DATA / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]
base = dict(company_id='S035', quote=quote, snapshot=snapshot,
    sha256=hashlib.sha256(text.encode()).hexdigest(),
    url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp', publisher_owner='Cục Thuế',
    retrieved_at='2026-10-19', reviewed=True,
    reviewer='Codex: visible official single parent row read after user completed CAPTCHA',
    caveat='Official row establishes legal name, parent MST and tax status only; no representative, clinical performance or product approval verified.')
for kind in ('tax', 'identity'):
    record = dict(base, id=f'E_VORIA_TAX_20261019_{kind}', kind=kind)
    if kind == 'tax':
        record.update(tax_id='3604052503', legal_name=legal_name,
            status='NNT đang hoạt động', checked_at='2026-10-19', row_scope='parent_company')
    else:
        assert all(normal(company[k]) in normal(quote) for k in ('brand', 'legal_name'))
    assert not validate_evidence(record, date(2026, 10, 19), DATA)
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
print('Recorded Voria official tax and legal identity; product gates remain separate.')
