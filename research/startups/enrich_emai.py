"""Record EM&AI primary sources and the exact active parent tax row."""
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
es = [json.loads(s) for s in (D / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if s]

def add(kind, source, quote, **extra):
    s = manifest[source]
    e = dict(id=f'E_{source}_{kind}_S037', company_id='S037', kind=kind, quote=quote,
        url=s['url'], publisher_owner=s['publisher_owner'], snapshot=s['snapshot'], sha256=s['sha256'],
        retrieved_at='2026-10-20', reviewed=True,
        reviewer='Codex: primary legal definition, funding scope and university activity read', **extra)
    errors = validate_evidence(e, date(2026, 10, 20), D)
    assert not errors, (e['id'], errors)
    old = next((x for x in es if x['id'] == e['id']), None)
    if old:
        es[es.index(old)] = e
    else:
        es.append(e)

add('identity', 'emai_privacy_identity', '“\nEM&AI\n”\n: là Công ty Cổ phần Em And Ai.',
    caveat='Own privacy-policy legal definition, not tax confirmation. Own footer MST0401856849 and179TranHungDao address agree with government parent-name/address; branch0401856849-001 and USoffice kept separate. Terms spell Emandai; no name-change history inferred.')
add('discovery', 'emai_surf_funding_202608',
    'Công ty Cổ phần EM AND AI, địa chỉ tại Tầng 4, Tòa nhà SPT, số 179 Trần Hưng Đạo, phường An Hải, thành phố Đà Nẵng, được hỗ trợ thực hiện dự án “Nghiên cứu và phát triển công nghệ chuyển đổi giọng nói thành văn bản cho tiếng Việt trong môi trường tổng đài”.\nDự án được hỗ trợ 700 triệu đồng, trong đó nội dung hỗ trợ là chi phí nghiên cứu giải mã công nghệ phục vụ đổi mới công nghệ cho Công ty Cổ phần EM AND AI.',
    source_type='government', published_at='2026-08-19',
    caveat='700millionVND for EMAND AI;893million total for two companies, not EMAND AI alone. Ceremony report, no bank-transfer evidence reviewed. Funding is innovation support, not equity investment.')
add('startup', 'emai_shinhan_recap',
    'The eight selected startups were paired with Shinhan business units as follows:\n•\nShinhan Bank Vietnam (5 projects):\nFundiin, Insider One, Quickwork, EM&AI, and OrderNow',
    caveat='2026InnoBoost cohort reported by TheInventionLab; supports current startup-program context. Page has no reliable exact publication date; not used as dated activity/discovery. Program ceiling200million not proof EM&AI received it; PoC not production contract.')
add('technology', 'emai_surf_funding_202608',
    'Dự án thuộc lĩnh vực trí tuệ nhân tạo (AI) – công nghệ cao được ưu tiên phát triển. Doanh nghiệp đã làm chủ công nghệ chuyển đổi giọng nói thành văn bản tiếng Việt với đặc thù dữ liệu có độ nhiễu cao, đa dạng giọng điệu vùng miền; tích hợp vào hệ thống tổng đài ảo và đánh giá chất lượng cuộc gọi.',
    published_at='2026-08-19', caveat='Government description of speech-to-text technology; no independent benchmark, model/IP ownership or audit of production deployments examined.')
add('product', 'emai_chatbot', 'AI Chatbot Agent - Trợ lý khách hàng chuyên nghiệp',
    caveat='Chatbot/voicebot/call-quality software, classified nonphysical. Use in healthcare/finance or device support does not establish hardware manufacturing or sector approval.')
add('activity', 'emai_surf_funding_202608',
    'Lễ trao kinh phí hỗ trợ được tổ chức trong khuôn khổ Lễ Khai mạc Ngày hội Khởi nghiệp đổi mới sáng tạo thành phố Đà Nẵng – SURF 2026 tại Cung Hội nghị Quốc tế Furama vào ngày 19/8/2026, qua đó góp phần lan tỏa chính sách hỗ trợ doanh nghiệp đổi mới công nghệ đến cộng đồng doanh nghiệp.',
    published_at='2026-08-19', event_date='2026-08-19', origin_id='emai_surf_support_20260819',
    caveat='Ceremony involving named EMAND AI in same article; no separate bank receipt. English translation/overallSURF recap remain same owner/event.')
add('activity', 'emai_udn_group_202609',
    'Trong các buổi sinh hoạt chuyên môn, nhóm chú trọng khuyến khích các thành viên đến từ doanh nghiệp như mới đây, chuyên gia Lê Ngọc Trí - Giám đốc Công ty Cổ phần EM & AI đã  đề xuất cơ hội kết nối tri thức công nghệ ứng dụng AI và dữ liệu công nghệ số, từ đó xác định các bài toán từ thực tiễn doanh nghiệp có thể là đầu vào cho nghiên cứu khoa học.',
    published_at='2026-09-14', event_date='2026-09-14', origin_id='emai_ai4art_participation_report_20260914',
    event_date_basis='University report14Sep2026 describes recent specialist contribution and current group participation; exact meeting/formation day not supplied. Date is reporting/observation date, not inferred meeting day.',
    caveat='Independent university report, distinct from city funding ceremony. Proposed research links/future work do not establish delivered project, grant, patent or signed commercial contract.')
add('activity', 'emai_chatbot', 'Thuê ngay trợ lý AI khách hàng chuyên nghiệp với chi phí tối ưu nhất!',
    event_date='2026-10-20', origin_id='emai_chatbot_offer_observed_20261020',
    event_date_basis='Current public software offer observed20Oct2026, no exact page-update or transaction date.',
    caveat='Company-owned offer only. No signup, data upload, consultation request, purchase or customer contact performed.')
add('counter_review', 'emai_chatbot', 'Mã số thuế: 0401856849',
    search_queries=['"EM AND AI" "giải thể"', '"0401856849" "ngừng hoạt động"'],
    review_note='No verified closure of exact parent in opened relevant sources. Initial capture failures resolved; authorized GDTquery returned parent0401856849 active20Oct2026 and branch0401856849-001 temporarily suspended. Branch suspension is not parent closure. TVPLparent search browser blocked byCloudflare; no TVPLstatus used. '
        'Own>90percent NLU claim lacks benchmark/dataset/independent audit; security commitment/privacy policy not compliance certification. Topdev/LinkedIn employer content not independent secondowner, oldaddress/relativeages not current registration/date evidence. Program recap chronology/demoday dates not relied on; independently dated funding/university reports used.')

snapshot = 'sources/emai_tax_20261020.txt'
text = (D / snapshot).read_text(encoding='utf-8')
lines = text.splitlines()
start = next(i for i, line in enumerate(lines) if line.split('\t') == ['2', '0401856849', ''])
quote = '\n'.join(lines[start:start + 3])
assert 'CÔNG TY CỔ PHẦN EM AND AI' in quote and 'NNT đang hoạt động' in quote
assert '0401856849-001' not in quote and 'tạm ngừng' not in quote
tax = dict(id='E_EMAI_TAX_20261020', company_id='S037', kind='tax', tax_id='0401856849',
    legal_name='CÔNG TY CỔ PHẦN EM AND AI', status='NNT đang hoạt động', quote=quote,
    snapshot=snapshot, sha256=hashlib.sha256(text.encode()).hexdigest(),
    url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp', publisher_owner='Cục Thuế',
    retrieved_at='2026-10-20', checked_at='2026-10-20', row_scope='parent_company',
    reviewed=True, reviewer='Codex: authorized CAPTCHA lookup, exact parent row and branch distinction read',
    image_file='sources/emai_tax_20261020.png', image_sha256=hashlib.sha256((D / 'sources/emai_tax_20261020.png').read_bytes()).hexdigest(),
    caveat='Parent0401856849 active. Branch0401856849-001 separately shown NNTtạmngừngKDcóthờihạn, excluded from parent-only quote. Screenshot and visibleDOM preserved; source URL alone does not replay session result. No product-performance or funding-disbursement audit.')
assert not validate_evidence(tax, date(2026, 10, 20), D)
old = next((e for e in es if e['id'] == tax['id']), None)
if old:
    es[es.index(old)] = tax
else:
    es.append(tax)

with (D / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    cs = list(csv.DictReader(handle))
c = next(x for x in cs if x['id'] == 'S037')
c.update(legal_name='CÔNG TY CỔ PHẦN EM AND AI', tax_id='0401856849', country='VN', physical='no',
    website='https://emandai.net/', discovery_url=manifest['emai_surf_funding_202608']['url'])
c['notes'] = ('Ownprivacydefinition mapsEM&AI toEMAND AI; ownMST0401856849/address corroborate government name/address, not tax confirmation. '
    'Chatbot/voicebot/STT software nonphysical;2026InnoBoost cohort startupcontext. City19Aug2026fundingceremony anduniversity14Sep2026researchparticipation report aredistinctowners/origins; universitydateisreportnotexactmeeting. '
    '700millionVNDforEMAI,893milliontotalboth; no bankreceipt orindependentbenchmark/securitycertification. Branch001/USoffice separate. '
    'GDT20Oct2026parent0401856849active; branch001temporarilysuspended, not parentclosure. Initialcapturefailure resolved; TVPLblocked/notused. Screeningpass is not procurement/investment or technical certification.')
with (D / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    w = csv.DictWriter(handle, fieldnames=list(cs[0]))
    w.writeheader()
    w.writerows(cs)
(D / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in es) + '\n', encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: s[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for s in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded10 EM&AI records including exact active parent tax row; branch suspension kept separate.')
