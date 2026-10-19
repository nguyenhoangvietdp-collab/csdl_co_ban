"""Review the ST Software entity associated with AquaX; do not merge related companies."""
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
manifest_path = DATA / 'source_manifest.json'
manifest = {r['id']: r for r in json.loads(manifest_path.read_text(encoding='utf-8'))}
registry = dict(manifest['aquax_danang_registry_202603'])
registry.update(id='aquax_danang_registry_rendered', method='browser_dom', status='fetched_browser',
    snapshot='sources/aquax_danang_registry_rendered_20261019.txt', fetched_at='2026-10-19')
registry['sha256'] = hashlib.sha256((DATA / registry['snapshot']).read_text(encoding='utf-8').encode()).hexdigest()
manifest[registry['id']] = registry
tax_snapshot = 'sources/stsoftware_tax_0402112987.txt'
tax_text = (DATA / tax_snapshot).read_text(encoding='utf-8')
manifest['aquax_stsoftware_tax'] = dict(id='aquax_stsoftware_tax', source_type='government',
    url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp', publisher_owner='Cục Thuế',
    status='fetched_browser', method='browser_dom', fetched_at='2026-10-19', snapshot=tax_snapshot,
    sha256=hashlib.sha256(tax_text.encode()).hexdigest())
evidence = [json.loads(line) for line in (DATA / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]
with (DATA / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
company = next(c for c in candidates if c['id'] == 'S048')
company.update(brand='AquaX', website='https://aquax.vn/', physical='hybrid',
    legal_name='CÔNG TY CỔ PHẦN ST SOFTWARE', tax_id='0402112987', country='VN')
company['notes'] = ('Alias AquaX / ST Software from DAVAS2025. Danang registry dated16Mar2026 links ST Software to AquaX; '
    'This dossier reviews ST Software0402112987, official parent tax row active19Oct2026, not all AquaX-related companies. '
    'Current contracting/IP ownership unresolved across STSoftware, STUnited, newly listed AquaXTechnology and DIGIEYE AppStoreprovider; '
    '0402356422 remains a secondary lead, no transfer/merger inferred. Hybrid buoy/sensors/remote controller plus software; '
    'no sensor accuracy, self-cleaning, AI performance, savings or paid deployments verified. '
    'Current subscription offer observed19Oct2026 is one self-published activity, not dated sale. '
    'DAVAS2026 listing not attendance or funding proof. Registry publication not exact recognition date. '
    'Union exhibition article4Jun2026 names Công ty Cổ phần AQUAX, not STSoftware; kept as context, not attributed STSoftware activity. '
    'App provider/copyright differ; no transfer or ownership inferred. No signup, app installation, contact or payment.')

def add(kind, source, quote, **extra):
    source_row = manifest[source]
    record = dict(id=f'E_{source}_{kind}_S048', company_id='S048', kind=kind, quote=quote,
        url=source_row['url'], snapshot=source_row['snapshot'], sha256=source_row['sha256'],
        publisher_owner=source_row['publisher_owner'], retrieved_at=source_row['fetched_at'], reviewed=True,
        reviewer='Codex: opened source and exact scope read; legal operator deliberately unresolved', **extra)
    if source_row.get('method'):
        record['method'] = source_row['method']
    assert normal(quote) in normal((DATA / record['snapshot']).read_text(encoding='utf-8'))
    assert not validate_evidence(record, date(2026, 10, 19), DATA)
    old = next((e for e in evidence if e['id'] == record['id']), None)
    if old:
        evidence[evidence.index(old)] = record
    else:
        evidence.append(record)

row = 'Công ty Cổ Phần ST Software - Dự án: AQUAX Hồ Tôm Thông Minh'
add('discovery', registry['id'], row, source_type='government', published_at='2026-03-16',
    caveat='Article date printed16Mar2026; recognition decision/date not inspected. Registry combines innovation and support activities, not a product certification.')
add('startup', registry['id'], row,
    caveat='Public innovation/startup-program context for the AquaX project, not proof every listed entity is a newly incorporated startup.')
add('identity', registry['id'], row,
    caveat='Registry documents project-to-ST Software association. Official tax separately verifies STSoftware0402112987; not proof of transfer to AquaXTechnology, current contracting/IP ownership or STUnited merger.')
tax_lines = tax_text.splitlines()
tax_start = next(i for i, line in enumerate(tax_lines) if line.split('\t') == ['1', '0402112987', ''])
tax_quote = '\n'.join(tax_lines[tax_start:tax_start + 3])
assert tax_quote.count('0402112987') == 1
add('tax', 'aquax_stsoftware_tax', tax_quote, tax_id='0402112987', legal_name=company['legal_name'],
    status='NNT đang hoạt động', checked_at='2026-10-19', row_scope='parent_company',
    caveat='Exact single parent row for STSoftware; no status inferred for STUnited, DIGIEYE or AquaXTechnology0402356422, and no current IP/contract ownership verified.')
add('product', 'aquax_company', 'Phao quan trắc make-in-Vietnam có chức năng tự động vệ sinh các cảm biến duy trì độ chính xác đo đạc',
    caveat='Company describes physical buoy integrated with software; self-cleaning and measurement accuracy untested, manufacturing ownership unverified.')
add('technology', 'aquax_company', 'Hệ thống IoT còn có khả năng điều khiển từ xa 5 thiết bị 3 pha nhằm tự động hóa và tối ưu hóa quá trình quản lý ao nuôi.',
    caveat='Self-described remote IoT control; not an electrical safety test or verification of AI prediction accuracy.')
add('activity', 'aquax_company', 'Với phương án thuê bao theo tháng chỉ từ 2,000,000 đồng hoặc theo vụ, AquaX mang công nghệ đến gần với người dân hơn, để “con tôm không còn ăn sổ đỏ”',
    event_date='2026-10-19', origin_id='aquax_subscription_offer_observed_20261019',
    event_date_basis='Live offer observed19Oct2026, not a publication, contract, payment or deployment date.',
    caveat='One owner/activity only; price is an advertised offer, not a quote accepted or verified customer transaction.')
add('counter_review', 'aquax_company', 'Backed by:\nST United',
    search_queries=['AquaX ST Software giải thể closed', 'AquaX 2026 tôm công ty'],
    review_note='No verified closure of exact operator found in opened sources. AquaX WaterUS, AquaExchangeIndia, AQUAXRoboticsFrance and clinicalAQUAx excluded. '
        'STSoftware official tax now active; separate AquaXTechnology lead and differing representatives not resolved. Website zeros are counters, not deployment evidence. '
        '40/20/90percent benefits and nationalaward self-claims not validated. No device, environmental outcome or customer testing.')
add('identity', 'aquax_appstore', 'DIGIEYE ARTIFICIAL INTELLIGENCE TECHNOLOGY JOINT STOCK COMPANY',
    caveat='Apple provider name; copyright says2026STUnited. This does not establish current AquaX contracting entity, project IP ownership or transfer from STSoftware. No new company is created from an app publisher.')
add('product', 'aquax_appstore', 'AquaX là ứng dụng hỗ trợ quản lý trại nuôi tôm trên thiết bị di động, giúp chủ trại, quản lý và kỹ thuật viên theo dõi hoạt động vận hành hằng ngày một cách thuận tiện hơn.',
    caveat='Developer-authored app description corroborates software layer; no installation, user count, paid operation or independently dated activity inferred.')
add('product', 'aquax_davas_2026', 'AquaX - Giải pháp nuôi tôm thông minh ứng dụng AIoT',
    caveat='Listed on organiser website with event program25–27May2026; listing alone does not prove attendance, investment, dated field deployment or independently tested savings.')
union_quote = 'Sản phẩm AquaX - Giải pháp AioT - ứng dụng nuôi tôm thông minh của Công đoàn Công ty Cổ phần AQUAX.'
add('product', 'aquax_union_exhibition_202606', union_quote, published_at='2026-06-04',
    caveat='Union portal reprints TườngMinh/LaoĐộng report about exhibition3–5Jun2026; one origin/owner. Names Công ty Cổ phần AQUAX, not STSoftware; product context only, not dated operating activity attributed to this tax entity.')
add('counter_review', 'aquax_union_exhibition_202606', union_quote, published_at='2026-06-04',
    search_queries=['AquaX 2026 triển lãm tôm', 'AquaX 2026 ST United'],
    review_note='Current legal relationship unresolved: this source names Công ty Cổ phần AQUAX, Danangregistry names STSoftware, store providerDIGIEYE/copyrightSTUnited. '
        'Do not infer transfer, merge or tax identity from same product name or address. This exhibition report is not counted as STSoftware activity. '
        'Secondary AquaXTechnology lead datedSeptember cannot establish identity of entity named in June; chronology unresolved.')

with (DATA / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(candidates[0]))
    writer.writeheader()
    writer.writerows(candidates)
(DATA / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
manifest_path.write_text(json.dumps(list(manifest.values()), ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: r[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for r in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Reviewed AquaX/STSoftware and official tax; related-entity ownership and independent activity remain open.')
