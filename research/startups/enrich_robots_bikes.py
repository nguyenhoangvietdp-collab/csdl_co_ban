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
    assert not validate_evidence(record,date(2026,10,15),DATA)
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

vulcan=next(c for c in candidates if c['id']=='S016')
add('S016','activity','vulcan_tgm_fitting_202512','prosthetic hand from Vulcan Augmetics',event_date='2025-12-30',
    origin_id='vulcan_tgm_vietnam_hand_fitting_20251230',activity_role='partner_reported_product_fitting',
    event_date_basis='TGM explicitly states it hosted a Hand Fitting Event at its Vietnam office on December30,2025; first article publication January05,2026, updated June28,2026.',
    caveat='Partner reports a single donated prosthetic fitting; not audited sales or a clinical performance trial. Brand product use in Vietnam, not an invoice independently tying this delivery to the VN tax entity. Singapore group legal entity is kept separate.')
vulcan['notes']='Official VN parent tax active0315155575. Separate activity origins: Vulcan developer app update11/09/2026 and TGM partner-reported prosthetic fitting at Vietnam office30/12/2025. One reported donated fitting is not a sales/customer count audit or clinical validation. Current global site lists Singapore parent; Vietnamese brand/entity bridge retained from earlier primary identity record. Exact contracting entity for the fitting not independently checked.'

buyo['tax_id']='0110114634'
buyo['discovery_url']=manifest['buyo_p4g_grant_202504']['url']
add(buyo['id'],'discovery','buyo_p4g_grant_202504','BUYO – ASSIST',source_type='fund',published_at='2025-04-16',
    caveat='Primary P4G grant announcement; total4.7M is for17 partnerships, not BUYO alone. Announcement does not establish VN tax status.')
add(buyo['id'],'startup','buyo_p4g_active','The startup utilizes innovative technologies',
    caveat='P4G describes BUYO as a startup; no independent certifications or environmental-performance audit here.')
add(buyo['id'],'activity','buyo_p4g_active','Status\nActive\nCountries of Operation\nVietnam',event_date='2026-10-14',
    origin_id='buyo_p4g_active_vietnam_partnership_observed_20261014',activity_role='observed_active_partner_programme',
    event_date_basis='Live P4G partnership status on capture date; not factory commissioning or tax status.',
    caveat='Active grant partnership is external programme evidence. 100ton/month by end2025 is an old target, not verified current capacity. Certification, biodegradation, carbon and sales claims not independently audited.')
add(buyo['id'],'activity','buyo_conference_202606','On June 26th 2026, BUYO collaborated with the Institute of Strategy and Policy on Agriculture and Environment (ISPAE)',event_date='2026-06-26',
    origin_id='buyo_ispae_hanoi_conference_20260626',activity_role='self_reported_technical_policy_conference',
    event_date_basis='Event date explicit in article body; publication17/07/2026 kept separate.',
    caveat='Company account of conference; independent ISPAE attendance confirmation not opened. Different owner and origin from P4G partnership-status signal, not verified production or sales.')
buyo['notes']='MST0110114634 from primary Techport provider profile is a candidate ID, not official tax status. Recent P4G grant release16/04/2025; active Vietnam partnership observed14/10/2026 plus company-reported ISPAE conference26/06/2026. Old capacity targets and certification/carbon claims not independently checked. Current P4G profile mentions corporate identity BUYO Solutions Company Limited; exact current Vietnamese registered name awaits tax lookup. Singapore company202313125C not substituted for Vietnam entity.'

pdf=DATA/'sources/airx_brochure.pdf'
txt=pdf.with_suffix('.txt')
manifest['airx_brochure']=dict(id='airx_brochure',source_type='company',publisher_owner='AirX / Veritas Vietnam',url='https://airxcarbon.com/storage/plant-based-negative-carbon-polypropylene-brochure.pdf',status='fetched_pdf',fetched_at='2026-10-14',snapshot='sources/airx_brochure.txt',sha256=hashlib.sha256(txt.read_text(encoding='utf-8').encode()).hexdigest(),pdf_file='sources/airx_brochure.pdf',pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
airx.update(legal_name='CÔNG TY CỔ PHẦN VERITAS VIỆT NAM',tax_id='0313231485',country='VN',
    notes='Candidate VN operator Veritas Viet Nam and MST0313231485 stated by AirX merchant site. Company brochure links AirX trademark to Veritas Vietnam JSC; JETRO company-authored profile maps AirX Carbon to Veritas Vietnam JSC as of01/04/2026. English/Vietnamese legal-name chain still requires official registration/tax comparison before approval. Current merchant offer plus BPP report19/02/2026 provide distinct activity owners/origins; merchant offering is not completed sales. NetZero Pallet remains product alias. P4G Completed describes programme, not company closure. Carbon-negative LCA, certification validity and current capacity not independently checked.')
add(airx['id'],'identity','airx_brochure','AirX is a trademark of the Veritas Vietnam JSC.',page=1,
    caveat='Historical company brochure, undated. Original PDF/hash and page1 visually checked; not a trademark-register extract or current registered VN name proof.')
add(airx['id'],'identity','airx_jetro_2026','AirX Carbon（Veritas Vietnam JSC）',
    caveat='Company-authored JETRO profile identifies English brand/operator name as of01/04/2026; JETRO disclaimer does not independently certify accuracy. VN tax spelling still pending.')
add(airx['id'],'identity','airx_commercial_live','AirX\nCông Ty Cổ Phần Veritas Việt Nam\nMST: 0313231485',
    caveat='Merchant footer identifies Vietnamese operator and candidate tax ID; cross-brand link retained separately, not an official active-tax result.')
add(airx['id'],'activity','airx_commercial_live','AirX in logo và nhận diện',event_date='2026-10-14',
    origin_id='airx_vietnam_merchant_b2b_offer_observed_20261014',activity_role='observed_company_commercial_offer',
    event_date_basis='Live business-order offer observed at capture; exact launch date unknown.',
    caveat='Public offer for co-branded coffee-residue products, not verified paid orders or production totals. Brand portfolio relation supported by brochure and company-authored JETRO profile; official VN tax still pending.')

stride=next(c for c in candidates if c['id']=='S002')
stride.update(physical='hybrid',website='https://www.stride.vn/',
    notes='Hybrid solar installation/financing/digital monitoring platform, not proof of in-house panel manufacturing. Google Play names STRIDE MTV COMPANY LIMITED; candidate VN entities include MTV0316841954, Solar0316839754 and newer Solar Solutions0319337720 from secondary listings. NTNN IDs and Singapore financing parent must remain separate. Exact Vietnam operating legal entity/tax mapping unresolved. Active P4G partnership observed14/10/2026 and developer app update26/05/2026; programme system/revenue/carbon totals not independently audited or assigned exact commissioning dates.')
add('S002','identity','stride_customer_app','STRIDE MTV COMPANY LIMITED',
    caveat='Developer legal-name lead, not official VN registration/tax identity. Multiple Stride entities require matching before choosing parent MST.')
add('S002','startup','stride_p4g','Stride is a clean tech startup in Vietnam',
    caveat='Fund programme characterization; Vietnam operating market does not alone establish registered legal entity.')
add('S002','product','stride_p4g','affordable solar installations',
    caveat='Hybrid installation/financing service with physical solar output, not proprietary solar panel manufacture.')
add('S002','technology','stride_customer_app','monitor its performance and energy output from our app',
    caveat='Developer describes digital solar monitoring. No independent accuracy, original sensor hardware or energy-savings verification.')
add('S002','activity','stride_p4g','Status\nActive\nCountries of Operation\nVietnam',event_date='2026-10-14',
    origin_id='stride_p4g_active_vietnam_partnership_observed_20261014',activity_role='observed_active_partner_programme',
    event_date_basis='Live status observed at capture, not tax status or a commissioning date.',
    caveat='Programme reports deployment/revenue/carbon totals without exact individual dates or audit documents. Do not date all historical installations to capture day.')
add('S002','activity','stride_customer_app','Updated on\nMay 26, 2026',event_date='2026-05-26',
    origin_id='stride_customer_app_update_20260526',platform_operator='Google Play',
    caveat='Developer maintenance activity; Google hosts the listing and is not an independent publisher. App update does not independently prove completed solar installations.')
add('S002','counter_review','stride_p4g','Stride – ASSIST',
    search_queries=['Stride điện mặt trời giải thể','Stride solar ceased operations'],
    review_note='No verified closure located in relevant searched sources. Similar Stride software/foreign firms excluded. Multiple Vietnam legal names and NTNN IDs remain unresolved; do not infer active tax from fund status, app update or directory listings.')

n2tp=next(c for c in candidates if c['id']=='S007')
n2tp.update(legal_name='CÔNG TY CỔ PHẦN GIẢI PHÁP CÔNG NGHỆ N2TP',country='VN',physical='no',website='https://n2tp.com/',
    notes='Historical government article names VN legal entity; candidate MST0109206584 from secondary listings not official tax evidence. Current output reviewed as software: SmartDoseAI/AI4Science. Biosensor translation and automated-lab equipment integration are not verified deployed physical outputs. Recent fund investment announcement12/08/2026 and ministry event11/12/2025 are distinct owners/origins. VNU study reports SmartDoseAI use, not validation of universal safety or future-data mathematical guarantees. Website hospital counts, speed, reproducibility and patent grant status not independently verified.')
add('S007','identity','n2tp_hhtp_identity','Công ty Cổ phần Giải pháp Công nghệ N2TP',
    caveat='Government event article17/05/2023 identifies company; historical mapping, not current active-tax status.')
add('S007','startup','touchstone_n2tp_2026','Vietnamese startups building technological self-reliance',
    caveat='Investor describes startup investment rationale in N2TP funding announcement; interested party, not audited scale or valuation.')
add('S007','product','n2tp_company','SmartDoseAI',
    caveat='Company offers clinical decision-support software. No treatment recommendation or approval/certification claim established here.')
add('S007','technology','touchstone_n2tp_2026','N2TP’s core technology is the AI4Science platform',
    caveat='AI hypothesis/simulation/experimental-feedback architecture described by investor; productivity and performance claims not independently replicated.')
add('S007','technology','n2tp_smartdose_study_2026','Dose adjustments were performed based on AUC estimation using SmartDoseAI® software',
    caveat='Retrospective hospital study reports software use July2025–March2026. Does not establish general clinical safety, regulatory approval, causal software benefit or total hospital deployments.')
add('S007','activity','touchstone_n2tp_2026','announced that it has received investment from Touchstone Partners.',event_date='2026-08-12',
    origin_id='n2tp_touchstone_seed_announcement_20260812',activity_role='investor_reported_funding',
    event_date_basis='Dateline12/08/2026 in article; not an independently audited transaction closing date.',
    caveat='Investor announcement; no disclosed amount or bank confirmation used. Patent applications not treated as grants.')
add('S007','activity','n2tp_mst_event_202512','N2TP Solutions Technology của Việt Nam đã giới thiệu giải pháp AI',event_date='2025-12-11',
    origin_id='n2tp_vietnam_korea_startup_pitch_20251211',activity_role='government_reported_technical_presentation',
    event_date_basis='Event date11/12/2025 in body; publication13/12/2025 kept separate.',
    caveat='Presentation evidence, not completed hospital sales. Ministry sentence ambiguously joins two startups/solutions; do not attribute used-EV trading platform to N2TP.')
add('S007','counter_review','n2tp_company','N2TP Technology Solutions JSC',
    search_queries=['N2TP giải thể','N2TP closed company'],
    review_note='No verified closure located in relevant searched sources. Website claims universal safety/proof/reproducibility and hospital counts remain unverified, not supported by the opened clinical study. Physical biosensor deployment and current official tax remain unverified.')

volterra=next(c for c in candidates if c['id']=='S034')
volterra.update(physical='hybrid',website='https://volterra.vn/vi',
    notes='Company presents energy-management software with VolSense/VolNexus/VolRemote IoT hardware. Hybrid classification does not establish manufactured/deployed units, autonomous-operation duration or savings. Government report identifies VinUniversity spin-off; registered VN name/tax mapping still pending. Candidate MST0111314178 from secondary listings not official tax evidence. UniVentures award-report publication06/10/2026 and company Better Choice award-report08/10/2026 are different events/owners; exact award ceremony dates not independently checked. Target30000 charging stations by2030 is future, not current deployment.')
add('S034','startup','volterra_vista_202610','Hai startup Selfomy và Volterra',
    caveat='Government compilation calls Volterra a university spin-off/startup; not confirmation of registered company or tax status.')
add('S034','product','volterra_hardware','Thiết bị edge-to-cloud cho hạ tầng sạc ổn định',
    caveat='Vendor offers sensors, industrial gateway and controller alongside software; no independent production or field deployment proof.')
add('S034','technology','volterra_hardware','cảm biến, điều phối và thực thi tại chỗ',
    caveat='Edge-to-cloud sensing/control architecture;14-day offline operation, safety and optimization claims not independently tested.')
add('S034','activity','volterra_vista_202610','giành chiến thắng tại UniVentures',event_date='2026-10-06',
    origin_id='volterra_univentures_award_report_20261006',activity_role='government_reported_startup_award',
    event_date_basis='Publication06/10/2026 of completed-award report. Exact ceremony date unknown; do not equate publication with ceremony or incubation start.',
    caveat='Government compilation. Supports a recent published startup-development signal, not audited operations or completed Singapore incubation.2030 targets withheld from current deployment.')
add('S034','activity','volterra_award_202610','Volterra chính thức được xướng tên',event_date='2026-10-08',
    origin_id='volterra_better_choice_award_report_20261008',activity_role='self_reported_startup_award',
    event_date_basis='Company article publication08/10/2026 reporting Better Choice award; exact gala date not independently checked.',
    caveat='Company report, not independent organiser confirmation or evidence of commercial sales. Different award from UniVentures.')
add('S034','counter_review','volterra_award_202610','Better Choice Awards 2026',
    search_queries=['Volterra giải thể sạc','Volterra Vietnam ceased operations'],
    review_note='No verified closure found for this VN charging startup. US fire-truck/Microsoft developer-kit firms and mathematical Volterra topics excluded. Registered legal entity, official tax and deployment counts remain unverified; partner logos are not independent confirmations.')

pdf=DATA/'sources/nhtc_vtb_report_2026.pdf'
txt=pdf.with_suffix('.txt')
manifest['nhtc_vtb_report_2026']=dict(id='nhtc_vtb_report_2026',source_type='company',publisher_owner='Công ty CP Điện tử Tân Bình / VTB',platform_operator='HOSE',url='https://staticfile.hsx.vn/Uploads/UploadDocuments/2450878/20260403%20-%20VTB%20-%2010.BAO%20CAO%20KET%20QUA%20KINH%20DOANH%202025%20VA%20KE%20HOACH%202026.pdf',status='fetched_pdf',fetched_at='2026-10-14',snapshot='sources/nhtc_vtb_report_2026.txt',sha256=hashlib.sha256(txt.read_text(encoding='utf-8').encode()).hexdigest(),pdf_file='sources/nhtc_vtb_report_2026.pdf',pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
nhtc=next(c for c in candidates if c['id']=='S028')
nhtc.update(legal_name='CÔNG TY TNHH MỘT THÀNH VIÊN CÔNG NGHỆ CAO NHA TRANG',tax_id='4201292624',country='VN',physical='yes',website='https://nhtc.com.vn/',
    notes='Own website identifies VN legal name and candidate tax4201292624, and says15+ years experience. Startup/scale-up stage not established by QVIC participation alone. Physical RTLS/IoT products and UWB/BLE/RFID mechanism described; accuracy, manufacturing volumes, patents and customer totals not independently checked. OnSafe developer app updated16/03/2026. VTB report hosted by HOSE names Nha Trang Hitech for increased IoT cooperation, without dated contract or completed delivery; not counted as independent current activity. Tax and second recent activity owner still required.')
add('S028','identity','nhtc_company','Nha Trang Hitech Company, Ltd.\nCông ty TNHH Một Thành Viên Công Nghệ Cao Nha Trang',
    caveat='Company self-identification; candidate MST in same page, not official active-tax result.')
add('S028','product','nhtc_company','ONTRAK ChainFlow',
    caveat='Physical IoT/RTLS ecosystem described by manufacturer; current output and deployment quantities not audited.')
add('S028','technology','nhtc_company','UWB+BLE+RFID',
    caveat='Real-time location technology stack;10cm accuracy and uptime values are vendor claims, not independently tested.')
add('S028','activity','nhtc_app_2026','Updated on\nMar 16, 2026',event_date='2026-03-16',
    origin_id='nhtc_onsafe_app_update_20260316',platform_operator='Google Play',
    caveat='Developer maintenance activity; Google hosts the app and is not an independent publisher or proof of new hardware sales.')
add('S028','counter_review','nhtc_vtb_report_2026','Nha Trang Hitech',page=3,
    search_queries=['Công Nghệ Cao Nha Trang giải thể','Nha Trang Hitech closed company'],
    review_note='No verified closure found for exact company in relevant searched sources. Historical2020–2021 insurance-debt lists surfaced but were not verified as current status; no closure inferred. VTB increased-cooperation wording lacks dated contract/completed delivery; not counted as a recent independent activity.15+ year company history leaves startup qualification unresolved.')

naiscorp=next(c for c in candidates if c['id']=='S027')
naiscorp.update(legal_name='CÔNG TY CỔ PHẦN CÔNG NGHỆ THÔNG MINH NAISCORP ROBOTICS',country='VN',physical='yes',website='https://www.naiscorp.com/en',
    notes='DISSC and partner SPT map Naiscorp Robotics to the Vietnam smart-technology joint stock company. Official parent tax0402268582 active15/10/2026; legacy IT-services Naiscorp0102003754 is a different entity. Physical Healthmate robot demonstrated at QVIC20/08/2026; integrator/customizer, not proof of entirely in-house manufacture or medical-device approval. QVIC award and SPT cooperation report are distinct owners/events. Company2006 history describes inherited group capabilities, not verified robot-company incorporation. Five patent applications are not granted patents. Official tax, product and distinct recent activity gates reviewed; current manufacture, sales totals and clinical claims not independently audited.')
add('S027','identity','naiscorp_dissc_award_202608','Công ty Cổ phần Công nghệ Thông minh Naiscorp Robotics',
    published_at='2026-08-21',caveat='DISSC names Vietnam legal company and Da Nang registration; candidate tax ID is not stated in this article.')
add('S027','startup','naiscorp_dissc_award_202608','Từ 28 startup xuất sắc được chọn tham gia vòng ươm tạo QVIC 2026, Naiscorp Robotics',
    published_at='2026-08-21',caveat='Government startup-support centre explicitly describes startup incubation participation. Inherited20-year group history is kept separate from the robot company; no verified incorporation date claimed.')
add('S027','product','naiscorp_dost_award_202608','Healthmate – robot đồng hành chăm sóc tại nhà',
    published_at='2026-08-20',caveat='Government report describes a demonstrated physical robot. Not confirmation of medical approval, mass production or commercial sales.')
add('S027','technology','naiscorp_about','Deploying service/assistant robots powered by Generative AI and modeled with Digital Twin technology',
    caveat='Vendor describes AI and digital-twin architecture; autonomy, safety, uptime, customer logos and performance not independently tested.')
add('S027','activity','naiscorp_dost_award_202608','Ngày 20/8/2026, Tập đoàn Qualcomm phối hợp cùng Bộ Khoa học và Công nghệ tổ chức Lễ trao giải',
    event_date='2026-08-20',published_at='2026-08-20',origin_id='naiscorp_qvic_final_award_20260820',
    caveat='Award and Healthmate demonstration, not proof of grant cash receipt or sales. DISSC report of same award is not counted as a second origin.')
add('S027','activity','naiscorp_spt_partnership_202606','Lễ ký kết đánh dấu bước khởi đầu cho quan hệ hợp tác giữa SPT',
    event_date='2026-06-15',published_at='2026-06-15',origin_id='naiscorp_spt_strategic_agreement_report_20260615',
    event_date_basis='Dated15-06-2026 entry for this exact article in SPT news list embedded in captured page. This is the report publication date, not an independently checked signing day.',
    caveat='Counterparty reports signed cooperation; plans through2030 and proposed products are not completed deliveries, revenue or production capacity.')
add('S027','counter_review','naiscorp_dissc_award_202608','Naiscorp Robotics kế thừa nền tảng hơn 20 năm nghiên cứu',
    search_queries=['"NAISCORP ROBOTICS" "giải thể"','"Naiscorp Robotics" "ceased operations"'],
    review_note='No verified closure found for exact robotics entity in relevant searched results. Legacy Naiscorp IT company and2006 group history kept separate. Official parent tax active15/10/2026; five applications not grants; partner logos,99.9% uptime, clinical benefit and own manufacturing unverified.')

tax_text=(DATA/'sources/naiscorp_tax_0402268582.txt').read_text(encoding='utf-8')
manifest['naiscorp_tax_0402268582']=dict(id='naiscorp_tax_0402268582',source_type='government',publisher_owner='Cục Thuế',url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp',status='captured_browser',fetched_at='2026-10-15',snapshot='sources/naiscorp_tax_0402268582.txt',sha256=hashlib.sha256(tax_text.encode()).hexdigest())
add('S027','tax','naiscorp_tax_0402268582',tax_text[tax_text.index('1\t0402268582'):].strip(),
    tax_id='0402268582',legal_name=naiscorp['legal_name'],status='NNT đang hoạt động',checked_at='2026-10-15',row_scope='parent_company',
    caveat='Visible official parent row after user-authorized CAPTCHA lookup; status observed15/10/2026, not a guarantee of future operation.')
naiscorp['tax_id']='0402268582'

tensor=next(c for c in candidates if c['id']=='S030')
tensor.update(legal_name='CÔNG TY CỔ PHẦN HBC NEXUS',country='VN',physical='yes',website='https://tensor.vn/',
    notes='Primary HBC Nexus footer names VN company; affiliated Bavina names HBC Nexus/Tensor and EggVision, but exact brand-to-registered-entity mapping still requires corroboration. Candidate parent MST0319525040 from secondary directories only, not official tax. Physical in-ovo scanning prototype demonstrated at QVIC20/08/2026. Vendor75% initial accuracy is on limited data;85% and90–95% are targets, not validated results. QVIC award and affiliated-group report of ESG event26/06/2026 are distinct owners/origins; ESG activity is company-level, not EggVision delivery. Group relationship is disclosed. Fund the Future listing is a schedule with self-reported profiles, not proof of attendance or investment. HBC website ESG examples labelled synthetic are not customer metrics; no separate startup added for ESGY.')
add('S030','identity','tensor_hbc_website','Công ty Cổ phần HBC Nexus',
    caveat='Company self-identification and VN address. Exact TENSOR brand mapping is not contained in this quote; secondary candidate MST0319525040 remains unverified.')
add('S030','identity','tensor_hbc_qvic_mapping','công ty thành viên HBC Nexus / Tensor',published_at='2026-08-20',
    caveat='Affiliated group maps brand aliases; lacks exact registered legal name/MST in the quoted alias. Do not merge with unrelated Tensor firms or count parent group as independent of Nexus.')
add('S030','startup','tensor_fund_future_schedule_202608','EggVision By request Pre-seed',published_at='2026-08-14',
    platform_operator='The Edge Alliance',caveat='Team self-reports pre-seed stage in organiser schedule; no funding closure, actual attendance or independent verification inferred.')
add('S030','product','naiscorp_dost_award_202608','đội Tensor mang đến giải pháp EggVision',published_at='2026-08-20',
    caveat='Government QVIC report identifies demonstrated physical in-ovo AI system. Commercial sales, mass manufacturing and customer acceptance not established.')
add('S030','technology','tensor_company','solution using Computer Vision AI to non-invasively and non-harmfully determine the sex',
    caveat='Vendor mechanism claim; day4 capability, welfare, throughput and operational accuracy not independently tested.')
add('S030','technology','tensor_eggvision_company','độ chính xác ban đầu là 75% trên dữ liệu hạn chế.',
    caveat='Vendor reports limited-data initial testing, without independently reviewed test protocol/sample size.85% commercialization and90–95% are future targets; not current measured performance.')
add('S030','activity','naiscorp_dost_award_202608','đội Tensor giải Nhì được thưởng 75.000 USD',event_date='2026-08-20',published_at='2026-08-20',
    origin_id='tensor_qvic_final_award_20260820',caveat='Government report of award and demonstration; no bank receipt or commercial delivery verified. Affiliated Bavina report of same final not another activity origin.')
add('S030','activity','tensor_hbc_esg_event_202606','Gia Lai, ngày 26/06/2026',event_date='2026-06-26',published_at='2026-06-29',
    origin_id='hbc_nexus_gia_lai_esg_conference_20260626',activity_role='affiliated_group_reported_company_event',
    caveat='Affiliated Bavina reports HBC Nexus representatives attending ESG event, distinct from QVIC. Supports company-level activity, not EggVision delivery or unrelated-party validation. Formal Tensor-to-entity mapping still pending.')
add('S030','counter_review','tensor_company','initial accuracy of 75% on limited data',
    search_queries=['"Tensor" "EggVision" "giải thể"','"HBC Nexus" "closed"'],
    review_note='No verified closure found for this Vietnam project/entity in relevant searches. Unrelated Tensor robocar/French firms excluded. Vendor accuracy targets, industry statistics and team-level10-million-dollar contract claims not accepted as audited EggVision results. A secondary Chinese article claims80 installed units, but primary site still describes limited-data75% testing; deployment quantity withheld. Formal brand/legal mapping and official tax remain pending. Fund the Future schedule is not proof of completed pitching; HBC ESG demo data expressly synthetic.')

with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
mp.write_text(json.dumps(list(manifest.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'startup_sources.json').write_text(json.dumps([{k:r[k] for k in ('id','source_type','publisher_owner','url')} for r in manifest.values()],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'candidates':len(candidates),'evidence_records':len(evidence),'companies_reviewed':['S008','S036','S006',airx['id'],buyo['id'],'S014','S005','S016','S002','S007','S034','S028','S027','S030']}))
