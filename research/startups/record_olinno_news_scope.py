"""Keep the Enfue newspaper interview separate from Olinno company activity."""
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from startup_tool import validate_evidence

D = ROOT / 'data/startups'
snapshot = 'sources/olinno_baodanang_20260226.txt'
pdf = 'sources/olinno_baodanang_20260226.pdf'
text = (D / snapshot).read_text(encoding='utf-8')
pages = PdfReader(D / pdf).pages
article_pages = '\n'.join(p.extract_text() or '' for p in pages[9:11])
assert 'olinno' not in article_pages.casefold() and '0401950376' not in article_pages
start = text.index('Đồng thời, tôi đặt mục tiêu đưa Enfue')
end = text.index('Hiện nay, Enfue', start)
quote = text[start:end].strip()
record = dict(id='E_OLINNO_ENFUE_PDF_LIMIT_20261020', company_id='S049', kind='counter_review',
    quote=quote, url='https://bqn.1cdn.vn/2026/02/25/26-2-2026.pdf', publisher_owner='Báo Đà Nẵng',
    snapshot=snapshot, sha256=hashlib.sha256(text.encode()).hexdigest(), method='pdf_embedded_text',
    pdf_file=pdf, pdf_sha256=hashlib.sha256((D / pdf).read_bytes()).hexdigest(),
    retrieved_at='2026-10-20', published_at='2026-02-26', reviewed=True,
    reviewer='Codex: original16pagePDF extracted, article pages10–11 visually read',
    review_note='Original interview names Enfue/NguyenXuanHuy, not Olinno orMST0401950376 in article pages10–11. '
        'Independent publication26Feb2026 exists for Enfue but cannot be assigned to Olinno merely through founder/product association. '
        'Existing enfueJSC footer and secondaryMST0402222179 remain separate identity leads, not verified transfer or merger. '
        'One million users and100000companies by2030 are targets; reported recruiting/cost reductions and users not independently audited.',
    caveat='PDF2940746bytes/16pages; masthead26Feb2026 rather than25Febuploadpath sets publicationdate. '
        'No activity record added for Olinno; its second independent recent publisher remains missing. '
        'Old2Jan2025VKUevent outside365days; advanceTascoannouncement/relativeLinkedInages not completed-event dates.')
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
c = next(c for c in cs if c['id'] == 'S049')
note = (' Báo Đà Nẵng26/02/2026, PDF gốc trang10–11: phỏng vấn về Enfue, không nêu Olinno/MST0401950376; '
    'chưa tính thành chủ nguồn hoạt động thứ hai của Olinno. Mục tiêu1triệungười/100nghìncôngty đến2030 chưa phải số đạt được.')
if note not in c['notes']:
    c['notes'] += note
with (D / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    w = csv.DictWriter(handle, fieldnames=list(cs[0]))
    w.writeheader()
    w.writerows(cs)
print('Recorded Enfue interview scope and target limits; Olinno remains pending.')
