"""Resolve AirX/Veritas brand scope; do not infer active tax status from search rows."""
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
manifest = {s['id']: s for s in json.loads((D / 'source_manifest.json').read_text(encoding='utf-8'))}
search = 'sources/airx_tvpl_search_20261020.txt'
manifest['airx_tvpl_search'] = dict(id='airx_tvpl_search', source_type='directory', publisher_owner='Thư Viện Pháp Luật',
    url='https://thuvienphapluat.vn/ma-so-thue/tra-cuu-ma-so-thue-doanh-nghiep?timtheo=ma-so-thue&tukhoa=0313231485',
    snapshot=search, sha256=hashlib.sha256((D / search).read_text(encoding='utf-8').encode()).hexdigest(), fetched_at='2026-10-20')
s = manifest['airx_commercial_20261020']
t = (D / s['snapshot']).read_text(encoding='utf-8')
a = t.index('AirX Carbon phát triển')
b = t.index('MST: 0313231485', a) + len('MST: 0313231485')
evidence = [json.loads(l) for l in (D / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if l]
for kind, source, quote, caveat in [
    ('identity', 'airx_commercial_20261020', t[a:b],
     'Contiguous own-page span links AirX Carbon context to footer VeritasVN/MST. Brochure and JETRO also connect English brand/legal name. Intervening awards/customer/eco claims are not adopted as verified facts.'),
    ('counter_review', 'airx_tvpl_search', '1\t0313231485\t\nCÔNG TY CỔ PHẦN VERITAS VIỆT NAM',
     'Exact parent search row; branch0313231485-001 separate. No status in search result, detail human verification unavailable. GDT two CAPTCHA codes rejected20Oct; no tax or secondary-tax record added.'),
    ('counter_review', 'airx_commercial_20261020', 'Cập nhật lần cuối: 05/2026',
     'FAQ timestamp only, not global page freshness. Own counters/customers/export shares and carbon-negative/biodegradable/certification claims remain unaudited; template success message is not a submitted form.')]:
    s = manifest[source]
    e = dict(id=f'E_{source}_{kind}_S055', company_id='S055', kind=kind, quote=quote, url=s['url'],
        snapshot=s['snapshot'], sha256=s['sha256'], publisher_owner=s['publisher_owner'], retrieved_at='2026-10-20',
        reviewed=True, reviewer='Codex: brand/legal relation read; parent versus branch and claim scope retained', caveat=caveat)
    if kind == 'counter_review':
        e.update(search_queries=['AirX Carbon Veritas'], review_note=caveat)
    assert not validate_evidence(e, date(2026, 10, 20), D)
    old = next((x for x in evidence if x['id'] == e['id']), None)
    if old:
        evidence[evidence.index(old)] = e
    else:
        evidence.append(e)
with (D / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
c = next(x for x in candidates if x['id'] == 'S055')
addition = (' Brand mapping20Oct2026: owncommercialpage contains AirXCarbon context and exactVeritasVNlegalfooter/MST0313231485, corroborating brochure/JETROEnglishname. '
    'GDT twoCAPTCHA submissions rejected; TVPLsearch exactparentplusbranch0313231485-001, detailverification blocked, noactive statusconfirmed. '
    'FAQMay2026 notallpageupdate; customer/counter/export/carbonnegative/biodegradation claims unaudited. No form submitted.')
if addition not in c['notes']:
    c['notes'] += addition
with (D / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    w = csv.DictWriter(handle, fieldnames=list(candidates[0]))
    w.writeheader()
    w.writerows(candidates)
(D / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
(D / 'source_manifest.json').write_text(json.dumps(list(manifest.values()), ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: s[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for s in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded3 AirX identity/scope records; tax status still pending.')
