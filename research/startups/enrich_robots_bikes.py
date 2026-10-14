"""Review physical-product evidence; distinguish announcements from completed deployments."""
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from startup_tool import normal,validate_evidence
DATA=ROOT/'data/startups'
mp=DATA/'source_manifest.json'
manifest={r['id']:r for r in json.loads(mp.read_text(encoding='utf-8'))}
evidence=[json.loads(line) for line in (DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]
with (DATA/'candidates.csv').open(encoding='utf-8-sig',newline='') as handle:
    candidates=list(csv.DictReader(handle))

for key,url in [
    ('alpha_patent_51180','https://www.ipvietnam.gov.vn/documents/20182/2142281/51180.pdf/8bf5d9f4-5256-4d55-955c-d8d83a3df1c9'),
    ('alpha_patent_52312','https://www.ipvietnam.gov.vn/documents/20182/2168816/52312.pdf/29f0a42b-0a75-42fd-9f2d-d68ba4ce2956'),
    ('forte_design_gazette_202401','https://ipvietnam.gov.vn/documents/20182/1598756/CB430A2.pdf/fd08e407-a705-49b6-9562-4e54b32d5876')]:
    snapshot=f'sources/{key}.txt'
    manifest[key]=dict(id=key,url=url,source_type='government',publisher_owner='Cục Sở hữu trí tuệ',
        status='fetched_pdf',fetched_at='2026-10-14' if key.startswith('forte') else '2026-10-13',snapshot=snapshot,
        sha256=hashlib.sha256((DATA/snapshot).read_text(encoding='utf-8').encode()).hexdigest(),
        pdf_file=f'sources/{key}.pdf',pdf_sha256=hashlib.sha256((DATA/f'sources/{key}.pdf').read_bytes()).hexdigest())

def add(company,kind,source,quote,**extra):
    r=manifest[source]
    record=dict(id=f'E_{source}_{kind}_{company}',company_id=company,kind=kind,quote=quote,
        url=r['url'],snapshot=r['snapshot'],sha256=r['sha256'],publisher_owner=r['publisher_owner'],
        retrieved_at=r['fetched_at'],reviewed=True,reviewer='Codex: primary text, dates and publication responsibility read',**extra)
    if r.get('pdf_file'):
        record.update(method='pdf_embedded_text',pdf_file=r['pdf_file'],pdf_sha256=r['pdf_sha256'])
    assert normal(quote) in normal((DATA/r['snapshot']).read_text(encoding='utf-8'))
    assert not validate_evidence(record,date(2026,10,14),DATA)
    old=next((e for e in evidence if e['id']==record['id']),None)
    if old: evidence[evidence.index(old)]=record
    else: evidence.append(record)

alpha=next(c for c in candidates if c['id']=='S008')
alpha.update(physical='yes',website='https://alphaasimov.com/')
add('S008','identity','alpha_patent_52312','Công ty TNHH ALPHA ASIMOV ROBOTICS (VN)',page=1,
    caveat='IPO legal name and brand match; tax ID separately corroborated by company footer and official tax lookup.')
add('S008','startup','alpha_jetro_2026','This startup develops autonomous robotic solutions powered by AI and advanced sensor technologies,',
    platform_operator='JETRO',caveat='JETRO disclaimer says companies authored profiles; publisher owner remains Alpha Asimov.')
add('S008','product','alpha_facts','Sản phẩm chính của Alpha Asimov là phương tiện giao hàng tự hành cỡ nhỏ phục vụ giao thực phẩm, hàng tạp hóa và giao hàng chặng cuối.')
add('S008','technology','alpha_facts','Robot sử dụng camera và phần mềm trên thiết bị để nhận biết môi trường xung quanh, xác định khu vực có thể di chuyển, đi theo tuyến đường, điều khiển tốc độ và hướng di chuyển, đồng thời phản ứng với chướng ngại vật và người tham gia giao thông.',
    caveat='Company mechanism description, not an independent safety or autonomy performance test.')
add('S008','technology','alpha_patent_52312','HỆ THỐNG KIỂM SOÁT AN TOÀN KHI ĐI TRONG ĐƯỜNG HẸP CHO XE GIAO HÀNG TỰ LÁI',page=1,
    caveat='Grant-description publication establishes protected subject matter; current validity/maintenance fees not checked.')
add('S008','activity','alpha_patent_52312','(45) 27/10/2025   451',event_date='2025-10-27',page=1,
    origin_id='alpha_52312_grant_description_publication_20251027',activity_role='supporting_rd_milestone',
    event_date_basis='Publication date printed as field (45); not the grant date or an operating deployment date.')
add('S008','activity','alpha_facts','Robot đang được pilot tại một trạm biến áp ở Việt Nam.',event_date='2026-08-23',
    origin_id='alpha_security_substation_pilot_2026',event_date_basis='Present pilot statement on company facts page last updated 23/08/2026; exact commissioning day unknown.',
    caveat='Self-reported pilot; client and substation withheld, no customer-side completion check.')
add('S008','counter_review','alpha_facts','Các pilot giúp công ty kiểm tra hành vi trên đường, dẫn đường, an toàn, hỗ trợ từ xa, quy trình khách hàng và vận hành triển khai thực tế.',
    search_queries=['Alpha Asimov giải thể','Alpha Asimov closed ceased operations'],
    review_note='No verified closure in opened relevant sources; official tax active. UAE/Singapore opportunities are prospective, not completed operations. JETRO profile is company authored.')
alpha['notes']='Official tax active. Current pilot self-report plus distinct IPO patent-publication milestone; neither is an independently audited deployment count. Grant dates claimed by company differ from publication dates printed in patent descriptions. JETRO profile company-authored; not independent activity confirmation.'

bike=next(c for c in candidates if c['id']=='S036')
bike.update(physical='yes',website='https://dat.bike/')
add('S036','identity','datbike_company','CÔNG TY TNHH MTV DAT BIKE VIETNAM\nMST/MSDN: 0401942142')
add('S036','startup','datbike_seriesb','Dat Bike vừa gọi vốn thành công thêm 22 triệu USD ở vòng Series B',
    caveat='Venture-backed Series B scale-up; closing date and funding amount not independently audited here.')
add('S036','product','datbike_era','Motor truyền động bên hông xe (Side Motor) giúp ERA vận hành mượt mà, gần như không tiếng động.',
    caveat='Electric motorbike output; performance adjectives are vendor claims.')
add('S036','technology','datbike_era','Bằng cách chia sẻ 70% linh kiện giữa bộ sạc & bộ điều khiển động cơ trong cùng hệ thống, ERA là kiến trúc xe tối ưu nhất từ Dat Bike: vừa vận hành mạnh mẽ, vừa sạc siêu nhanh.',
    caveat='Vendor describes integrated charger/controller architecture; 70% figure not independently tested.')
add('S036','activity','datbike_store_2026','Thời gian khai trương: 9:00 sáng, Thứ 7 – 28/02/2026',event_date='2026-02-23',
    origin_id='datbike_hanoi_store_launch_announcement_20260223',activity_role='commercial_announcement',
    event_date_basis='Article publication 23/02/2026 announcing scheduled opening on 28/02/2026, not a verified completion date.',
    caveat='Opening announcement, not independent proof that the opening occurred. Article modified 09/10/2026.')
add('S036','activity','datbike_ahamove_2026','Đa dạng xe điện Dat Bike, VinFast, Selex — bảo hiểm TNDS miễn phí',event_date='2026-10-13',
    origin_id='ahamove_datbike_current_rental_offer_20261013',activity_role='observed_partner_commercial_offer',
    event_date_basis='Live partner offer observed on capture date; page displays update month 10/2026, exact update day unknown.',
    caveat='Partner offer observed, not completed rental transactions; cached web search version had different prices/update month, raw live snapshot retained.')
add('S036','counter_review','datbike_company','CÔNG TY TNHH MTV DAT BIKE VIETNAM\nMST/MSDN: 0401942142',
    search_queries=['Dat Bike phá sản 2026','Dat Bike closed ceased operations'],
    review_note='Rumor video located, not evidence of legal closure. Official parent tax active; two branch MSTs closed, four listed units including parent active. Multiple similar names/MSTs excluded. Funding publication dates differ; no exact closing date inferred.')
bike['notes']='Parent 0401942142 official tax active; two closed branches not treated as parent closure. Commercial launch announcement and observed live Ahamove offer are distinct sources/origins, not audited sales. 100,000 annual factory capacity stated for end-2026 is future target, not current verified capacity.'

forte=next(c for c in candidates if c['id']=='S006')
forte.update(legal_name='CÔNG TY TNHH FORTE BIOTECH VIỆT NAM',country='VN',physical='yes',website='https://www.fortebio.tech/')
add('S006','identity','forte_design_gazette_202401','CÔNG TY TNHH FORTE BIOTECH VIỆT NAM (VN)',page=121,
    caveat='Historical IPO entry identifies Vietnam company. Do not interpret it as an invention patent or independently checked current grant validity.')
add('S006','startup','forte_p4g','the startup reduces the use of antibiotics and chemicals in aquaculture',
    caveat='Startup characterization by grant programme; environmental outcome not independently measured here.')
add('S006','product','forte_company','Portable, field-deployable. Qualitative detection of WSSV, EHP, AHPND, TPD in under 1 hour. 2 samples per run.',
    caveat='Company specification of physical diagnostic device; time and accuracy not independently tested.')
add('S006','technology','forte_about','a portable, LAMP-based diagnostic platform that delivers molecular-grade results in under 1 hour, on-site, with no lab, no cold chain, and no specialist training.',
    caveat='Company mechanism description. Press uses simplified PCR terminology; lab-concordance claims vary and are not validated here.')
add('S006','activity','forte_p4g','Status\nActive\nCountries of Operation\nVietnam',event_date='2026-10-14',
    origin_id='forte_p4g_vietnam_partnership_active_observed_20261014',activity_role='observed_active_partner_programme',
    event_date_basis='Live fund/partner status observed on retrieval date; not a project commissioning date.',
    caveat='Partnership status, not legal tax status. Target of 600 farms is a goal, not completed deployment count.')
add('S006','activity','forte_enterprisesg_2025','Forte Biotech has 95 customers across South-east Asia, with Vietnam, Thailand and Indonesia being its biggest markets.',event_date='2025-11-06',
    origin_id='forte_customer_operations_business_times_20251106',platform_operator='Enterprise Singapore',
    event_date_basis='Present operations reported at first publication 06/11/2025; not verified customer transaction dates.',
    caveat='Business Times reporting republished by EnterpriseSG; one publication origin, not two. Counts not an independent financial audit.')
add('S006','activity','forte_app','Updated on\nAug 10, 2026',event_date='2026-08-10',origin_id='forte_aotomatic_app_update_20260810',platform_operator='Google Play',
    caveat='Developer app update. Google hosts the listing, not an independent activity publisher.')
add('S006','counter_review','forte_contact','Forte Biotech Vietnam',
    search_queries=['Forte Biotech ngừng hoạt động giải thể','Forte Biotech closed ceased operations'],
    review_note='No verified closure in opened relevant sources. Singapore parent and Vietnam company kept distinct; current tax still requires direct lookup. Fin-fish target launch in Q3/2026 is not proof of completed launch.')
forte['notes']='Vietnam company identified in IPO gazette; candidate MST0317428355 from secondary lead, official lookup pending. Physical RAPID device. P4G active Vietnam partnership, dated Business Times operating report and developer app update. Do not combine grant target with completed farms, or infer entire group manufacturing from VN legal existence.'

with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
mp.write_text(json.dumps(list(manifest.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'startup_sources.json').write_text(json.dumps([{k:r[k] for k in ('id','source_type','publisher_owner','url')} for r in manifest.values()],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'evidence_records':len(evidence),'companies_reviewed':['S008','S036','S006']}))
