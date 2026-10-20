"""Use the original attachment to separate the Korean recruiter from a VN company."""
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from startup_tool import validate_evidence

D = ROOT / 'data/startups'
snapshot = 'sources/plantner_ctu_recruitment_original.txt'
pdf = 'sources/plantner_ctu_recruitment_original.pdf'
text = (D / snapshot).read_text(encoding='utf-8')
start = text.index('Chúng tôi hiện là một tập đoàn Hàn Quốc')
end = text.index('Bên cạnh đó', start)
quote = text[start:end].strip()
record = dict(id='E_PLANTNER_CTU_PDF_SCOPE_20261020', company_id='S054', kind='counter_review',
    quote=quote, url='https://coa.ctu.edu.vn/images/upload/tuyendung/2025/Thang1/Recruitment-Opportunity-for-Graduates---Vietnamese.pdf',
    publisher_owner='PLANTNER INC. (Korea), recruitment document hosted by CTU', snapshot=snapshot,
    sha256=hashlib.sha256(text.encode()).hexdigest(), method='pdf_embedded_text', pdf_file=pdf,
    pdf_sha256=hashlib.sha256((D / pdf).read_bytes()).hexdigest(), retrieved_at='2026-10-20',
    reviewed=True, reviewer='Codex: three-page original extracted; page2 visually read',
    search_queries=['Plantner mã số thuế', 'Plantner Việt Nam 2026 phân'],
    review_note='Original attachment identifies KoreanPLANTNERINC and says VN establishment planned alongside recruitment. CTU title CoPhan is not a VN registration fact. '
        'No exactpublicationdate in inspecteddocument; /2025/Thang1 path is archival context, not verifiedeventdate. Historicalplan not currentabsence of VN company. '
        'NoMST, incorporationcompletion, currentregistration or fertilizerapproval verified.',
    caveat='PDF513588bytes/3pages. Supersedes unresolved scope interpretation of CTU title, not the remaining exactVNlegalname/tax gate. Relative lastyear/thisyear not converted to eventdates.')
assert not validate_evidence(record, date(2026, 10, 20), D)
es = [json.loads(l) for l in (D / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if l]
old = next((e for e in es if e['id'] == record['id']), None)
if old:
    es[es.index(old)] = record
else:
    es.append(record)
(D / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in es) + '\n', encoding='utf-8')
with (D / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    cs = list(csv.DictReader(handle))
c = next(c for c in cs if c['id'] == 'S054')
c['notes'] = c['notes'].replace('CTU recruitment title says CoPhanPlantner, unresolved scope/date.',
    'CTU recruitment title says CoPhan but original3pagePDF names KoreanPLANTNERINC and onlyplans VN incorporation; not evidence of a VN jointstock entity. Exactpublicationdate not verified.')
with (D / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    w = csv.DictWriter(handle, fieldnames=list(cs[0]))
    w.writeheader()
    w.writerows(cs)
print('Recorded original Plantner recruitment PDF scope; Vietnam legal identity still pending.')
