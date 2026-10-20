"""Review Olinno separately from enfue JSC; retain publisher and date boundaries."""
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
mp = DATA / 'source_manifest.json'
manifest = {r['id']: r for r in json.loads(mp.read_text(encoding='utf-8'))}
snapshot = 'sources/olinno_tax_0401950376.txt'
tax_text = (DATA / snapshot).read_text(encoding='utf-8')
manifest['olinno_tax'] = dict(id='olinno_tax', url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp',
    source_type='government', publisher_owner='Cục Thuế', status='fetched_browser', method='browser_dom',
    fetched_at='2026-10-19', snapshot=snapshot, sha256=hashlib.sha256(tax_text.encode()).hexdigest())
evidence = [json.loads(line) for line in (DATA / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]
with (DATA / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
company = next(c for c in candidates if c['id'] == 'S049')
company.update(brand='Olinno', legal_name='CÔNG TY TNHH CÔNG NGHỆ OLINNO', tax_id='0401950376',
    country='VN', physical='no', website='https://olinno.com/')
company['notes'] = ('Alias Olinno Technology. Official parent tax0401950376 active19Oct2026; own footer040-195-0376 is the same digit sequence, not a branch. '
    'SaaS venture builder, no physical-device output established. Own site links Enfue/Xagoe; Chrome store directly names OlinnoTechnologyLtd as EnfueRecruiter developer. '
    'Direct HTTP capture version2.1.10 updated10Sep2026 differs from search-cache2.1.7/23Aug; use captured fields, not globally latest claim. '
    'Store update and current SaaS offer are different origins but same Olinno owner; Google is platform operator, not second activity publisher. '
    'Government SURF article4Aug2025 supports discovery, outside365-day activity window. Since2009/copyright not incorporation date; MVP3Mar2025 and July2025launch also outside window. '
    'Enfue website footer enfueJSC and secondaryMST0402222179 kept separate; developer role does not merge companies or establish IP ownership. '
    'Enfue Tasco15Jan2026 article is advance announcement, not attendance/completed partnership. No extension installation, applicant-data capture, signup or contact.')
company['notes'] += ' Legacy DAVAS discovery snapshot hash mismatch remains held outside approval; old hash not silently replaced.'

def add(kind, source, quote, **extra):
    src = manifest[source]
    record = dict(id=f'E_{source}_{kind}_S049', company_id='S049', kind=kind, quote=quote,
        url=src['url'], snapshot=src['snapshot'], sha256=src['sha256'], publisher_owner=src['publisher_owner'],
        retrieved_at=src['fetched_at'], reviewed=True, reviewer='Codex: source, legal scope, publisher and date read', **extra)
    if src.get('method'):
        record['method'] = src['method']
    assert normal(quote) in normal((DATA / record['snapshot']).read_text(encoding='utf-8'))
    assert not validate_evidence(record, date(2026, 10, 19), DATA)
    old = next((e for e in evidence if e['id'] == record['id']), None)
    if old:
        evidence[evidence.index(old)] = record
    else:
        evidence.append(record)

lines = tax_text.splitlines()
i = next(i for i, line in enumerate(lines) if line.split('\t') == ['1', '0401950376', ''])
tax_quote = '\n'.join(lines[i:i + 3])
assert tax_quote.count('0401950376') == 1
add('tax', 'olinno_tax', tax_quote, tax_id='0401950376', legal_name=company['legal_name'],
    status='NNT đang hoạt động', checked_at='2026-10-19', row_scope='parent_company',
    caveat='Olinno parent only; no tax status inferred for enfue JSC, no representative or product/privacy compliance verified.')
add('identity', 'olinno_tax', tax_quote,
    caveat='Exact Olinno brand contained in official legal name. Own footer corroborates same10digits and address; extension provider corroborates English trade name, not ownership of all Enfue entities.')
add('identity', 'olinno_company', 'Olinno Technology Ltd. Enterprise code: 040-195-0376.',
    caveat='Self-published English name and formatted identifier; remove only display hyphens to compare0401950376, do not treat as a branch suffix.')
add('startup', 'olinno_careers', 'We have a few roles available to help our start-up development.',
    caveat='Self-described venture/startup development context, not a registration date, dated hiring event or independent proof of company age.')
add('product', 'olinno_chrome_enfue', 'Easily capture and add applicants from LinkedIn profiles to your company.',
    caveat='Software extension, developer listed OlinnoTechnologyLtd. Description read only; no installation or personal applicant information collected.')
add('technology', 'olinno_enfue', 'No more status meeting chaos. Get AI-powered summaries, team scorecards, and one-click decisions on every candidate.',
    caveat='Enfue vendor feature claim; Olinno is confirmed extension developer, not necessarily sole owner/operator of platform. No model, hiring accuracy, fairness, privacy or compliance audit.')
add('activity', 'olinno_chrome_enfue', '2.1.10\nUpdated\nSeptember 10, 2026', event_date='2026-09-10',
    origin_id='olinno_enfue_recruiter_store_update_20260910',
    event_date_basis='Exact Version/Updated fields in direct HTTP snapshot captured19Oct2026. Search/browser cached view showed older2.1.7/23Aug; no globally latest-version claim.',
    caveat='Developer-owned release record on Google platform, not Google as an independent activity publisher; ratings/users are not audited paid customers.')
add('activity', 'olinno_company', 'Check out our SaaS\nAvailable Now', event_date='2026-10-19',
    origin_id='olinno_saas_offer_observed_20261019',
    event_date_basis='Current SaaS availability offer observed19Oct2026; not launch, contract or customer deployment date.',
    caveat='Same Olinno owner as Chrome developer; two origins do not satisfy two distinct publisher owners.')
add('discovery', 'olinno_surf_gov_202508', 'Dự án Enfue TalentSpike là nền tảng tuyển dụng thông minh ứng dụng AI.',
    source_type='government', published_at='2025-08-04',
    caveat='Government article lists SURF2025 finalist project. Project association supported by Olinno own links/store developer, not proof all Enfue corporate activity belongs to Olinno. Within730-day discovery, outside365-day activity window.')
add('counter_review', 'olinno_chrome_enfue', 'Olinno Technology Ltd.',
    search_queries=['Olinno giải thể closed', 'Enfue Olinno 2026'],
    review_note='No verified closure found for exact Olinno entity in opened relevant sources; official tax active. '
        'Privacy disclosures are developer declarations, not verified collection/encryption/safety or permission to scrape applicant data. '
        'Chrome publisher badges/Non-trader do not prove VN tax/product compliance or operating shutdown. No extension installed.')
add('counter_review', 'olinno_enfue', 'enfue JSC. © 2026. All Rights Reserved.',
    search_queries=['Enfue Olinno 2026', 'Olinno 2026 innovation'],
    review_note='Keep Enfue operator distinct from Olinno extension developer; no legal merger/transfer inferred from links, shared people or branding. '
        '1000+companies/ROI/time-saving claims and testimonials are unverified; no user/customer counts adopted. '
        'Tasco article says heading/aims/lookforward, not attendance; Since2009 and copyright are not incorporation dates. '
        'Older Sep2025press/Mar2025MVP/Jul2025launch do not establish recent activity asof19Oct2026.')

with (DATA / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(candidates[0]))
    writer.writeheader()
    writer.writerows(candidates)
(DATA / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
mp.write_text(json.dumps(list(manifest.values()), ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: r[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for r in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded Olinno tax and SaaS evidence; independent recent publisher remains open.')
