"""Review Fastdo software and own legal identity; keep tax/activity gaps explicit."""
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from startup_tool import validate_evidence

D = ROOT / 'data/startups'
manifest = {s['id']: s for s in json.loads((D / 'source_manifest.json').read_text(encoding='utf-8'))}
es = [json.loads(s) for s in (D / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if s]
def add(kind, source, quote, **extra):
    s = manifest[source]
    e = dict(id=f'E_{source}_{kind}_S039', company_id='S039', kind=kind, quote=quote, url=s['url'],
        publisher_owner=s['publisher_owner'], snapshot=s['snapshot'], sha256=s['sha256'], retrieved_at='2026-10-20',
        reviewed=True, reviewer='Codex: own legal footer, software output and dates read', **extra)
    errors = validate_evidence(e, date(2026, 10, 20), D)
    assert not errors, (e['id'], errors)
    old = next((x for x in es if x['id'] == e['id']), None)
    if old:
        es[es.index(old)] = e
    else:
        es.append(e)

add('identity', 'fastdo_company', 'Công ty TNHH Quản trị số Fastdo',
    caveat='Own legal footer, not direct registration/tax verification. Separate branch0401799975-001 and FastdoAI entity not merged.')
add('discovery', 'fastdo_danang_202506', 'Fastdo: Phá vỡ rào cản chuyển đổi số cho SMEs bằng giải pháp quản lý công việc tích hợp AI giá tốt, dễ dùng',
    source_type='government', published_at='2025-06-10', caveat='Within730day discovery, DAVAS30May2025 outside365day activity. No funding receipt inferred.')
add('startup', 'fastdo_danang_202506', 'Con đường của một startup công nghệ luôn đầy rẫy thử thách, từ việc hoàn thiện sản phẩm, xây dựng đội ngũ, thu hút người dùng cho đến việc cạnh tranh trên thị trường. Fastdo không là ngoại lệ.',
    caveat='Government startup context; origin at DOCORP/Workdo not corporate incorporation or IP transfer proof.')
add('product', 'fastdo_danang_202506', 'giải pháp quản lý công việc toàn diện',
    caveat='Software/task management, nonphysical classification. HRM integrations do not establish hardware manufacturing.')
add('technology', 'fastdo_danang_202506', 'tích hợp Trợ lý trí tuệ nhân tạo (AI) thông minh',
    caveat='Reported AI integration; no model, source code, benchmark or privacy/security audit examined.')
add('activity', 'fastdo_company', 'Đặt lịch 1:1 với chuyên gia', event_date='2026-10-20',
    origin_id='fastdo_consulting_offer_observed_20261020', event_date_basis='Current consulting/software offer read20Oct2026, not signed contract or delivery date.',
    caveat='One company-owned signal only; no form submission, payment, verified customer counts or consulting completion.')
add('counter_review', 'fastdo_company', 'Mã số thuế: 0401799975',
    search_queries=['Fastdo 2026 ký kết', 'Fastdo giải thể 0401799975'],
    review_note='No verified closure of exact entity in opened relevant sources. OwnMSTnot officialtax. TopCVapplication deadlines/relativeages are not eventdates or secondowner; sameemployer onjobplatform not independentpublisher. '
        'Logos/testimonials/3000customers/98percent satisfaction/revenueuplift not audited. No signup/form sent, no staff or HR data collected.')
with (D / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    cs = list(csv.DictReader(handle))
c = next(x for x in cs if x['id'] == 'S039')
c.update(legal_name='CÔNG TY TNHH QUẢN TRỊ SỐ FASTDO', tax_id='0401799975', country='VN', physical='no', website='https://fastdo.vn/')
c['notes'] = ('Ownwebsitelegalfooter/MST0401799975, not officialtax. Softwaremanagementsuite nonphysical; AIreported not benchmarked. '
    'Government10Jun2025DAVASarticle within730daydiscovery;30May2025event outside365dayactivity. '
    'Onlycurrentownconsultingoffer20Oct2026 acceptedrecentactivity; secondowner/origin missing. '
    'DOCORP/Workdo producthistory not registeredcompanyage/IPtransfer. FastdoAI andbranch001 keptseparate. '
    'Recruitmentdeadlines/relativeages not eventdates; platformoperator not secondowner. No customer/satisfaction/revenue/privacy audit.')
with (D / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    w = csv.DictWriter(handle, fieldnames=list(cs[0]))
    w.writeheader()
    w.writerows(cs)
(D / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in es) + '\n', encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: s[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for s in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded7 FASTDO records; tax and second recent activity owner/origin remain open.')
