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

for brand,source in [('AirX Carbon','airx_startupwheel_2025'),('BUYO','buyo_antler')]:
    if not any(normal(c['brand'])==normal(brand) for c in candidates):
        c=dict.fromkeys(candidates[0],'')
        c.update(id=f'S{max(int(c["id"][1:]) for c in candidates)+1:03}',brand=brand,
            physical='yes',discovery_url=manifest[source]['url'])
        candidates.append(c)
airx=next(c for c in candidates if c['brand']=='AirX Carbon')
airx.update(website='https://airxcarbon.com/',notes='NetZero Pallet is a product, not a second company. AirX Coffee identifies operator Veritas Vietnam JSC, candidate MST0313231485; legal-brand chain and official tax not yet fully checked. P4G partnership Completed does not establish company closure. No independently checked carbon-negative LCA, certifications or current capacity.')
add(airx['id'],'discovery','airx_startupwheel_2025','AirX Carbon là một startup',source_type='competition',published_at='2025-02-05',
    date_basis='Vietnamese profile displays Published on 05/02/2025; DD/MM/YYYY interpretation.',
    caveat='Company-style first-person profile on organizer site; not independent verification of first-in-world or environmental claims.')
add(airx['id'],'discovery','airx_bpp_2026','AirX Carbon transforms biomaterials',source_type='government',published_at='2026-02-19',
    caveat='Government-funded programme publication; carbon-negative characterization not an independently checked LCA.')
add(airx['id'],'startup','airx_startupwheel_2025','AirX Carbon là một startup',caveat='Brand/startup characterization; older legal operator may require stage clarification.')
add(airx['id'],'product','airx_p4g','NetZero Pallet®, an eco-efficient pallet solution manufactured from agricultural byproducts')
add(airx['id'],'technology','airx_startupwheel_2025','phế phẩm nông nghiệp và chất dẻo',
    caveat='Bio-composite processing, not proof of 100% plant content or full biodegradation.')
add(airx['id'],'activity','airx_bpp_2026','AirX Carbon operates as a hybrid circular model spanning direct sales, pallet leasing and technology licensing.',event_date='2026-02-19',origin_id='airx_bpp_business_model_asof_20260219',
    event_date_basis='Present operations reported at publication date; no transaction-level audit.',
    caveat='USD1.2 million for 2025 is explicitly a projection. Programme concluded November 2025, not company closure.')
add(airx['id'],'counter_review','airx_p4g','Status\nCompleted\nCountries of Operation\nVietnam',
    search_queries=['AirX Carbon giải thể ngừng hoạt động','AirX Carbon closed ceased operations'],
    review_note='No verified company closure in opened relevant material. Programme completion kept distinct from tax/legal closure. AirX Coffee/Veritas operator lead needs legal mapping; not counted as another startup.')

buyo=next(c for c in candidates if c['brand']=='BUYO')
buyo.update(legal_name='Công ty TNHH Giải pháp công nghệ Buyo',country='VN',website='https://buyosolutions.com/',
    notes='Primary Techport profile states candidate tax ID0110114634; official tax still pending. Buyoplastic is a portfolio alias, not another company. Antler portfolio undated; 2022 is company year, not publication date. Factory 30 tonnes/month and 100-tonne target are undated/self-authored; not verified current output. Safety/biodegradation and patent claims not independently checked.')
add(buyo['id'],'identity','buyo_techport','Công ty TNHH Giải pháp công nghệ Buyo',caveat='Provider profile on government-hosted platform; business tax status not established by this page.')
add(buyo['id'],'discovery','buyo_antler','Buyo\nWe upcycle discarded biowaste',source_type='fund',published_at='',
    caveat='Undated investor portfolio; not sufficient for recent-publication gate. Environmental assertions are investee claims.')
add(buyo['id'],'startup','buyo_antler','Hanh Do\nCo-Founder\nBUYO',caveat='Early-stage Antler-backed venture; founder testimonial, not independent operational verification.')
add(buyo['id'],'product','buyo_techport','vật liệu composite sinh học dùng làm bao bì')
add(buyo['id'],'technology','buyo_company','The treated bio-residues will then be compounded with bio-polymers to create biodegradable bio-resins with high performance.',
    caveat='Company describes material processing. No independent biodegradation/safety verification or grant-validity check.')
add(buyo['id'],'counter_review','buyo_techport','Mã số thuế\n0110114634',
    search_queries=['CÔNG TY TNHH GIẢI PHÁP CÔNG NGHỆ BUYO giải thể','BUYO bioplastics closed ceased operations'],
    review_note='No verified legal closure in opened relevant sources. Similar furniture/fuel names excluded. Old forecasts and undated capacities withheld from current-activity evidence; official tax required.')

sunbot=next(c for c in candidates if c['id']=='S014')
sunbot.update(legal_name='CÔNG TY CỔ PHẦN CÔNG NGHỆ GIÁO DỤC KIRO VIỆT NAM',country='VN',physical='hybrid',website='https://sunbot.vn/',
    notes='Sunbot is a KIRO educational programme combining robots and teaching services. Government report links KIRO to the brand; 2026 government event confirms product use, not a sale or current KIRO delivery. Candidate MST0108919688 is a secondary procurement lead, not official tax evidence. Hardware originality/manufacture and second recent activity origin remain unverified. Vendor claims of VNIES appraisal/300 schools/45000 children not independently checked.')
add('S014','identity','sunbot_yenso_2025','Công ty cổ phần công nghệ giáo dục KIRO Vietnam',
    caveat='Government report names the organiser of a Sunbot school event on 28/03/2025; historical identity bridge, not current tax status.')
add('S014','product','sunbot_company','Sunbot là sản phẩm giáo dục công nghệ của KIRO Việt Nam',
    caveat='Robot-assisted educational programme; hybrid hardware and services. Original hardware manufacture not established.')
add('S014','technology','sunbot_company','Trẻ điều khiển robot bằng thẻ lệnh logic',
    caveat='Describes programming interaction; does not establish proprietary electronics or independent learning outcomes.')
add('S014','discovery','sunbot_phuninh_2026','NGÀY HỘI STEAM – ĐẤU TRƯỜNG SUNBOT 2026',source_type='government',published_at='2026-04-04',
    caveat='Dated government product-use report; not a startup award or certification of original hardware.')
add('S014','activity','sunbot_phuninh_2026','Trường Mầm non Thanh Lâm tổ chức ngày hội STEAM – đấu trường SunBot',event_date='2026-04-04',
    origin_id='sunbot_thanhlam_school_event_20260404',activity_role='customer_product_use',
    caveat='Government event report supports use of the product. It does not identify the supplying legal entity or prove a new sale/current company delivery.')
add('S014','counter_review','sunbot_company','KIRO Việt Nam',
    search_queries=['KIRO Việt Nam giải thể','Sunbot closed company'],
    review_note='No relevant verified closure found in these searches. Similar tanning chatbot and foreign Kiro names excluded. Tax status remains unknown; March2025 event is outside the current activity window.')

neorice=next(c for c in candidates if c['id']=='S005')
neorice.update(legal_name='CÔNG TY CỔ PHẦN HOÁ NÔNG AHA',country='VN',physical='hybrid',website='https://www.camchau.com/',
    notes='NEORICE is described as a cultivation project/solution associated with AHA, not a separately verified incorporated startup. Government text maps the solution to AHA; exact registered spelling and candidate MST1200874529 from secondary listings still need official verification. Hybrid process/service with rice output, not proof of proprietary drone hardware. Recent government sources describe AHA technical work; startup qualification of the operating entity remains unverified. Programme investment and area targets, carbon credit eligibility, USDA certification, emissions and income claims are not independently audited.')
add('S005','identity','neorice_khuyennong_202511','Công ty Cổ phần Hoá nông AHA đẩy mạnh giải pháp NEORICE',
    caveat='Government associates solution and company; registered spelling/tax ID and project legal structure still require official records.')
add('S005','product','neorice_aim','NEORICE sustainable rice cultivation process',
    caveat='Cultivation process with agricultural output and services; not a verified proprietary hardware product.')
add('S005','technology','neorice_aim','Professional Agriculture System (PAS)',
    caveat='Programme describes integrated digital/organic-farming methods; technical performance not independently tested.')
add('S005','technology','neorice_paa_2025','natural minerals combined with drone spraying technology',
    caveat='Speaker biography describes process; no original ministry decision, hardware IP, emissions audit or organic certificate checked.')
add('S005','activity','neorice_khuyennong_202511','đẩy mạnh giải pháp NEORICE',event_date='2025-11-13',
    origin_id='aha_neorice_national_extension_report_20251113',activity_role='reported_current_technical_work',
    event_date_basis='Present activity statement at article update 13/11/2025; exact field-work days not specified.',
    caveat='Government programme report, not audited deployment counts or credited carbon issuance.')
add('S005','activity','aha_vinhthuan_202609','Công ty Cổ phần Hóa Nông AHA thông tin về công tác phối hợp, hỗ trợ kỹ thuật',event_date='2026-09-18',
    origin_id='aha_vinhthuan_technical_project_meeting_20260918',activity_role='reported_technical_support_meeting',
    event_date_basis='Article explicitly dates project launch meeting 18/9/2026.',
    caveat='Supports AHA technical participation. No explicit NEORICE brand in this article; process name matches other primary descriptions. Project budget/area belong to the whole project, not company revenue or completed delivery.')
add('S005','counter_review','neorice_aim','NEORICE - Negative Emission Organic Rice',
    search_queries=['Công ty Hóa nông AHA giải thể','NEORICE closed company'],
    review_note='No verified legal closure found in relevant sources; unrelated comic/forum names excluded. October2026 rice purchase agreement is by Thien Phat, not AHA. Harvest December2026 is future. AHA/project startup status and official tax remain unverified.')

with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
mp.write_text(json.dumps(list(manifest.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'startup_sources.json').write_text(json.dumps([{k:r[k] for k in ('id','source_type','publisher_owner','url')} for r in manifest.values()],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'candidates':len(candidates),'evidence_records':len(evidence),'companies_reviewed':['S008','S036','S006',airx['id'],buyo['id'],'S014','S005']}))
