"""Review Plantner product context without merging Korea and Vietnam entities."""
import csv
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
with (DATA / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
company = next(c for c in candidates if c['id'] == 'S054')
company.update(physical='yes', website='https://en.plantner.kr/')
company['notes'] = ('Physical fertilizer/alginate materials product context, not independently validated efficacy. '
    'MSD organizer reports15Jan2026DemoDay and Plantner PoC;13percent soil-organic-matter change is internal monitoring,1000ha expansion a plan. '
    'Company history says Vietnam corporation establishedOct2025 but no exact legal name/MST. KoreaJan2024 incorporation not VN incorporation. '
    'Secondary candidateMST0319205202 TNHHPlantner not verified; CTU recruitment title says CoPhanPlantner, unresolved scope/date. '
    'Do not assign group funding, patents, sales or awards to exact VN company before identity mapping. '
    'Current partner-seeking offer observed20Oct2026 and MSDDemoDay are distinct owners/origins at brand level; VN legal scope still open. '
    'No fertilizer registration, safety, manufacturing capacity, disbursement or independent crop trial verified.')

def add(kind, source, quote, **extra):
    s = manifest[source]
    record = dict(id=f'E_{source}_{kind}_S054', company_id='S054', kind=kind, quote=quote,
        url=s['url'], publisher_owner=s['publisher_owner'], snapshot=s['snapshot'], sha256=s['sha256'],
        retrieved_at='2026-10-20', reviewed=True, reviewer='Codex: source read; group versus VN legal scope separated', **extra)
    assert not validate_evidence(record, date(2026, 10, 20), DATA)
    old = next((e for e in evidence if e['id'] == record['id']), None)
    if old:
        evidence[evidence.index(old)] = record
    else:
        evidence.append(record)

add('startup', 'plantner_company_history', 'Mar 2026 Selected for Eco Startup Program (Ministry of Environment)',
    caveat='Company-reported startup programme; no ministry confirmation or exact VN legal identity inferred.')
add('technology', 'plantner_company_history', 'Starting from seaweed-based alginate,',
    caveat='Self-described alginate materials platform, not independently verified process, patents or performance.')
add('product', 'plantner_company_agri', 'of eco-friendly organic fertilizers',
    caveat='Physical fertilizer offering; eco-friendly/organic are supplier descriptions, not verified regulatory certification or efficacy.')
add('activity', 'plantner_msd_demo', 'Quý quân – Recycle Ledger (trái) và Plantner (phải)',
    event_date='2026-01-15', origin_id='plantner_msd_demoday_20260115',
    event_date_basis='Organizer article opening explicitly dates DemoDay15Jan2026; award caption identifies Plantner.',
    caveat='Organizer report of award/PoC at brand level; no prize disbursement or exact VN contracting entity verified.')
add('activity', 'plantner_company_agri', 'We are seeking partners to join Plantner in growing a sustainable agricultural industry in Vietnam.',
    event_date='2026-10-20', origin_id='plantner_agri_partner_offer_observed_20261020',
    event_date_basis='Current partner-seeking offer read20Oct2026; observation date, not date of completed contract or deployment.',
    caveat='Company-owned offer, separate owner/origin from MSD; exact VN legal mapping remains pending.')
add('counter_review', 'plantner_company_history', 'Oct 2025 Established Plantner Vietnam Corporation',
    search_queries=['Plantner giải thể Việt Nam', 'Plantner closed Vietnam company'],
    review_note='No verified closure of exact Vietnam entity found in relevant opened sources. Closed weekends is customer-service hours, not closure. '
        'Korean company history does not name exact VN company/MST; never substitute Korean incorporation/funding/awards for VN legal facts.')
add('counter_review', 'plantner_ctu_recruitment', 'Thông tin tuyển dụng: Công ty Cổ phần Plantner',
    search_queries=['Plantner mã số thuế', 'Plantner Việt Nam 2026 phân'],
    review_note='CTU title says CoPhan whereas secondary0319205202 says TNHH. No legal merger or identity match established. '
        'Dates of unrelated sidebar articles are not publication dates for this recruitment item. Do not use as a dated hiring event.')

with (DATA / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(candidates[0]))
    writer.writeheader()
    writer.writerows(candidates)
(DATA / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: s[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for s in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded7 Plantner context records; Vietnam identity and tax remain pending.')
