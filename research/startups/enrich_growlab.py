"""Join Growlab's own legal name to the exact official parent tax row."""
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
manifest = {s['id']: s for s in json.loads((DATA / 'source_manifest.json').read_text(encoding='utf-8'))}
evidence = [json.loads(s) for s in (DATA / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if s]
discovery = next(e for e in evidence if e['id'] == 'E_techfest_final_hanoi_2025_discovery_S051')
manifest['growlab_award'] = dict(discovery, fetched_at=discovery['retrieved_at'])
text = (DATA / 'sources/growlab_tax_0318576613.txt').read_text(encoding='utf-8')
manifest['growlab_tax'] = dict(id='growlab_tax', source_type='government', publisher_owner='Cục Thuế',
    url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp', snapshot='sources/growlab_tax_0318576613.txt',
    sha256=hashlib.sha256(text.encode()).hexdigest(), fetched_at='2026-10-20', method='browser_dom', status='fetched_browser')
with (DATA / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
c = next(c for c in candidates if c['id'] == 'S051')
c.update(legal_name='CÔNG TY TNHH GROWLAB', tax_id='0318576613', country='VN', physical='yes', website='https://growlab.com.vn/')
c['notes'] = ('Official parent0318576613 active20Oct2026, own site names CongtyTNHHGrowlab; registered14Road72CatLai distinct from current lab/contact40Road39HiepBinh. '
    'Physical Multipuno coconut tissue-culture seedlings; vendor yield80-100percent/100plusfruit/4years unverified. '
    'Government12Dec2025TECHFESTaward and current ownseedlingoffer20Oct2026 distinct owners/origins; no prize disbursement or actualStartupWorldCupattendance inferred. '
    'Patent assertion in award article not independently verified or assigned to legal owner. OwnMay2025workshop outside365daywindow. '
    'LinkedInHTTPfailed; no hiringdate derived from relativeage or deadline10May2026. No customers/revenue/capacity/safety/cropperformance audit.')

def add(kind, source, quote, **extra):
    s = manifest[source]
    record = dict(id=f'E_{source}_{kind}_S051', company_id='S051', kind=kind, quote=quote,
        url=s['url'], publisher_owner=s['publisher_owner'], snapshot=s['snapshot'], sha256=s['sha256'],
        retrieved_at=s['fetched_at'], reviewed=True, reviewer='Codex: exact legal parent, source dates and product limits read', **extra)
    assert not validate_evidence(record, date(2026, 10, 20), DATA)
    old = next((e for e in evidence if e['id'] == record['id']), None)
    if old:
        evidence[evidence.index(old)] = record
    else:
        evidence.append(record)

lines = text.splitlines()
i = next(i for i, l in enumerate(lines) if l.split('\t') == ['1', '0318576613', ''])
quote = '\n'.join(lines[i:i+3])
add('tax', 'growlab_tax', quote, tax_id=c['tax_id'], legal_name=c['legal_name'], status='NNT đang hoạt động',
    checked_at='2026-10-20', row_scope='parent_company', caveat='Parent row only; status is not product efficacy, safety or patent verification.')
add('identity', 'growlab_company', 'Công ty TNHH Growlab', caveat='Own site names same legal company; official parent tax independently confirms exact name. Contact/lab address not substituted for registered office.')
add('technology', 'growlab_company', 'Kỹ thuật Công nghệ Sinh học tiên tiến', caveat='Vendor description, not an independently reproduced process or patent ownership confirmation.')
add('product', 'growlab_company', 'Dừa Sáp nuôi cấy mô Multipuno™', caveat='Physical seedlings offered; yield, waxy-fruit ratio, time to harvest and lifetime unverified.')
add('startup', 'growlab_award', discovery['quote'], caveat='Government startup-award context; patent assertion and prize disbursement not independently verified.')
add('activity', 'growlab_award', discovery['quote'], event_date='2025-12-12', origin_id='growlab_techfest_award_20251212',
    event_date_basis='Article states final took place12December2025 and reports Growlab championship.', caveat='Award result, not proof prize received or actual2026WorldCupattendance; republications same origin.')
add('activity', 'growlab_company', 'Dừa Sáp nuôi cấy mô Multipuno™', event_date='2026-10-20', origin_id='growlab_seedling_offer_observed_20261020',
    event_date_basis='Current product offer observed20Oct2026, not launch or sale date.', caveat='Own offering, different owner/origin from government award; no paid-sales inference.')
add('counter_review', 'growlab_company', 'Dừa Sáp nuôi cấy mô Multipuno™', search_queries=['Growlab giải thể đóng cửa', 'Growlab Multipuno failed criticism'],
    review_note='No verified closure for exact VN entity in relevant opened sources; official parent active. Unrelated GrowlabOrganics/Canadianaccelerator/reviews not attributed. '
        'No patentgrant, capacity, commercialyield or regulatory audit. Old18May2025workshop excluded from recentactivity; LinkedInrelativeages/deadlines not eventdates.')

with (DATA / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(candidates[0]))
    writer.writeheader()
    writer.writerows(candidates)
(DATA / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
manifest.pop('growlab_award')
(DATA / 'source_manifest.json').write_text(json.dumps(list(manifest.values()), ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: s[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for s in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded8 Growlab evidence records including exact official active parent tax.')
