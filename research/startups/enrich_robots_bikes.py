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

veep=next(c for c in candidates if c['id']=='S032')
veep.update(legal_name='CÔNG TY CỔ PHẦN VIOT ENERGY EFFICIENCY PLATFORM',country='VN',physical='hybrid',website='https://www.veep.vn/',
    notes='Company footer names Vietnam legal entity; candidate parent MST0317812963 from secondary directories not official tax. Do not substitute representative-office0317812963-001 or NTNN0319514793. Hybrid AMIGO/AIoT platform integrates meters, HVAC and lighting with EEaaS investment/rental; own hardware manufacture and completed customer savings unverified. Company self-identifies Climate Tech startup; historical2017 Australian/group activity kept separate from Vietnam incorporation. QVIC award20/08/2026 and May2026 company report of VNG field trip are separate events/owners; exact trip day unknown. JETRO profile is company-authored asof01/04/2026, not independent operating proof.30–35% savings, customer logos,100% CAPEX funding and2030 carbon target not independently audited.')
add('S032','identity','veep_about','Về Veep\n\u200bĐối Tác Chiến Lược\nCÔNG TY CỔ PHẦN VIOT ENERGY EFFICIENCY PLATFORM',
    caveat='Own-page footer connects VEEP with Vietnam legal name. Candidate MST from directories is withheld pending official parent lookup; addresses differ between old introduction and current homepage.')
add('S032','startup','veep_about','VEEP là một startup Climate Tech',
    caveat='Company self-description, supplemented by QVIC shortlist; group/Australian2017 history not treated as Vietnam incorporation or sole proof of startup stage.')
add('S032','product','veep_about','VEEP mang đến giải pháp AMIGO® – nền tảng quản lý năng lượng thông minh ứng dụng AIoT',
    caveat='Platform plus integrated field equipment and energy-service model classified hybrid; not evidence of self-manufactured devices or measured energy savings.')
add('S032','technology','veep_jetro_profile','integrates smart meters, HVAC systems, lighting, indoor environmental monitoring, and real-time analytics',
    platform_operator='JETRO',caveat='JETRO disclaimer identifies company-authored profile; owner remains VEEP. As-of01/04/2026 does not verify revenues, actual customers, safety or savings.')
add('S032','activity','naiscorp_dost_award_202608','đội VEEP giải Ba với 50.000 USD',event_date='2026-08-20',published_at='2026-08-20',
    origin_id='veep_qvic_final_award_20260820',caveat='Government award report and platform demonstration; not receipt of prize funds, customer contract or audited30% savings.')
add('S032','activity','veep_fieldtrip_202606','Tại buổi Company Visit diễn ra tại VNG, đại diện VEEP đã tham gia phiên thảo luận',
    event_date='2026-05',published_at='2026-05',origin_id='veep_qvic_vng_fieldtrip_report_202605',activity_role='self_reported_participation_report',
    event_date_basis='Visible20 thg5 publication label and QVIC2026 body establish May2026 reporting context; stored conservatively at month precision. Exact trip day not verified, and publication is not equated with the visit day.',
    caveat='Company report, not VNG-side confirmation or completed customer deployment. Different event from August QVIC final; both within one programme, not independent customer traction.')
add('S032','counter_review','veep_introduction','VEEP – là doanh nghiệp gốc Úc',
    search_queries=['"VEEP" "giải thể" "năng lượng"','"VEEP" "ceased operations"'],
    review_note='No verified closure found for the exact Vietnam energy company in relevant searched sources. Unrelated TV series, US training programme and fractional-executive marketplace excluded. NTNN and representative-office IDs not parent tax. JETRO company-authored; partner logos, contractual performance, own manufacture,30–35% savings and carbon targets unverified. Historical Australian/group2017 activity not assumed Vietnam entity age. Field-trip date retained at month precision; no exact commissioning/deployment claimed.')

aiz=next(c for c in candidates if c['id']=='S017')
aiz.update(legal_name='CÔNG TY CỔ PHẦN AIZ',country='VN',physical='no',website='https://aizcorp.vn/',
    notes='VAA and Nghe An University name Vietnam AIZ joint stock company and executives; own website maps software AI Data Platform/3C1A/agents. Candidate parent MST0110830839 from BKHUB/directory, not official tax; representative-office0110830839-001 and unrelated AIZ International0314126733 kept separate. Software classification; IoT ingestion, robot integration and smart-glasses ideas do not establish proprietary physical output. Company reports founded2024; early-stage/QVIC company-track context, not registry age certification. Recent VAA membership27/01/2026, QVIC innovation award20/08/2026 and university roundtable10/10/2026 are different source owners/events, not customer revenue. LinkedIn Public Company label not evidence of stock-market listing. Same-name HCMC insurance-debt search result lacks verified parent-ID match; do not attribute debt or closure to Hanoi entity.')
add('S017','identity','aiz_vaa_membership_202601','Công ty Cổ phần AIZ',published_at='2026-01-27',
    caveat='VAA membership report names legal company and data/AI activity in Vietnam; no parent tax ID in this record.')
add('S017','startup','aiz_bkhub_identity','Năm thành lập\n2024',
    caveat='Platform profile reports recent founding, corroborated by company LinkedIn and QVIC company shortlist context. Profile provider not independently verified; not official incorporation certificate, investment proof or listed-company status.')
add('S017','product','aiz_company','AIZ Data Platform\nOrchestrating intelligence across all sources',
    caveat='Software product offer. Linked IoT devices or Qualcomm smart-glasses integration not proof AIZ manufactures hardware or has paid deployments.')
add('S017','technology','aiz_company','3C1A Architecture\nCognition • Collaboration • Conversation • Agent',
    caveat='Company describes data ingestion/validation/transformation/enrichment and agent orchestration. Performance, enterprise logos, data-cleaning reliability and real deployment scale unverified.')
add('S017','activity','aiz_vaa_membership_202601','Ngày 27/1/2026, Hội Tự động hóa Việt Nam (VAA) đã chính thức trao Chứng nhận Kết nạp hội viên',
    event_date='2026-01-27',published_at='2026-01-27',origin_id='aiz_vaa_membership_admission_20260127',
    caveat='Association reports admission with exact AIZ name in same paragraph. Membership, not technology certification, completed sales or legal tax status;2006 founding in article refers to ETEK, not AIZ.')
add('S017','activity','aiz_nau_event_202610','Hội thảo “Trường Đại học Nghệ An với doanh nghiệp” ngày 10/10/2026',
    event_date='2026-10-10',published_at='2026-10-12',origin_id='aiz_nghe_an_university_roundtable_20261010',
    caveat='University reports AIZ director participation/discussion. Separate from VAA/QVIC; not a signed training order, customer contract or research acceptance.')
add('S017','activity','naiscorp_dost_award_202608','trao 2 giải Đổi mới sáng tạo cho 2 đội AIZ và OpenMind Robotics',
    event_date='2026-08-20',published_at='2026-08-20',origin_id='aiz_qvic_innovation_award_20260820',
    caveat='Government event report, distinct source/event from association and university. Shared award with another team not merged as same company or verified payment.')
add('S017','counter_review','aiz_company','AIZ Data Platform',
    search_queries=['"AIZ" "giải thể"','"AIZ" "ceased operations" AI','"0110830839" "BHXH"'],
    review_note='No verified closure of this exact Hanoi AI company in relevant searched sources. Same-name HCMC insurance-debt listing surfaced but parent tax identity/address match not verified; do not attribute debt or infer closure. Unrelated international/agricultural firms, Brazilian Aizcorp and fictional Aiz excluded. BKHUB HUST Verified badge and LinkedIn Public Company category are not registry, tax or listing proof. Customer logos, Qualcomm endorsement quotes, software reliability and physical product manufacture not independently established.')

openmind=next((c for c in candidates if c['id']=='S057'),None)
if openmind is None:
    assert not any(normal(c['brand'])==normal('OpenMind Robotics') for c in candidates)
    openmind={key:'' for key in candidates[0]}
    openmind.update(id='S057',brand='OpenMind Robotics')
    candidates.append(openmind)
assert openmind['brand']=='OpenMind Robotics'
openmind.update(legal_name='CÔNG TY TNHH OPENMIND ROBOTICS',country='VN',physical='hybrid',website='https://www.openmindrobotics.com/',
    discovery_url=manifest['naiscorp_dost_award_202608']['url'],
    notes='Vietnam company identified by HASI exhibitor listing; candidate parent MST3703462444 only from secondary directories, not official tax. Distinct from US OpenMind/OM1/Pantera-funded entity and Chinese Openmind robotics firms; no20-million-dollar funding attributed to VN company. Hybrid vision/robotics integration including OM-Eye/OnRobots and third-party robot hardware; not proof of own complete robot manufacture. Gradion reports live ACE integration28/07/2026; government QVIC innovation award20/08/2026 is separate event/owner. Prototype/reference implementation not customer production acceptance or audited deployment count. Company LinkedIn founded2026; website copyright2024 is not incorporation evidence. HASI scheduled booth not attendance proof; full masked tax value not inferred from site.')
add('S057','discovery','naiscorp_dost_award_202608','trao 2 giải Đổi mới sáng tạo cho 2 đội AIZ và OpenMind Robotics',
    published_at='2026-08-20',source_type='government',caveat='Government QVIC winner report adds a distinct VN robotics lead; not same company as AIZ or foreign OpenMind firms.')
add('S057','identity','openmind_hasi_exhibitor_202607','Công ty TNHH Openmind robotics',
    caveat='Vietnam association exhibitor listing names company; tax masked as3703**** and not reconstructed. Candidate3703462444 remains secondary, no official tax lookup.')
add('S057','startup','openmind_company_linkedin','Founded\n2026',platform_operator='LinkedIn',
    caveat='Company self-reported founding/early-stage team plus QVIC company context; not verified incorporation certificate. Website copyright2024 kept separate.')
add('S057','product','openmind_company','Autonomous Cobot Picking and Placing',
    caveat='Physical robotic manipulation solution combined with software, classified hybrid. Third-party robot-brand support does not establish own robot manufacture, endorsement or completed customer deployments.')
add('S057','technology','openmind_company','Develops cutting-edge computer vision algorithms that allow robots to perceive and understand their surroundings',
    caveat='Vendor mechanism description, not independently validated accuracy, speed, collision safety or ROI. Digital twins described elsewhere on same page.')
add('S057','technology','openmind_gradion_ace_recap',"connect Openmind's OnRobots to Gradion's Fleet Management and MES on live ACE hardware",
    caveat='Counterparty integration-session account; supports platform/hardware integration, not broad production-readiness or proof every future issue is solved.')
add('S057','activity','openmind_gradion_ace_recap','On 28 July 2026, Openmind Robotics joined Gradion at the ACE floor in Ho Chi Minh City',
    event_date='2026-07-28',origin_id='openmind_gradion_ace_live_integration_20260728',activity_role='counterparty_reported_live_integration',
    caveat='Gradion reports OnRobots running on live hardware and a reference implementation. No customer acceptance, invoice, commercial contract or independent performance replication checked.')
add('S057','activity','naiscorp_dost_award_202608','trao 2 giải Đổi mới sáng tạo cho 2 đội AIZ và OpenMind Robotics',
    event_date='2026-08-20',published_at='2026-08-20',origin_id='openmind_qvic_innovation_award_20260820',
    caveat='Government QVIC award report, distinct from Gradion July integration. Prize publication is not proof of funds received or mass deployment.')
add('S057','counter_review','openmind_company','OpenMind Robotics',
    search_queries=['"OpenMind Robotics" "giải thể"','"OpenMind Robotics" Vietnam "closed"'],
    review_note='No verified closure of this exact Vietnam company found in relevant sources. US OpenMind/OM1/Pantera/PiNetwork funding and Chinese companies excluded. No20-million-dollar or RMB funding attributed. HASI booth schedule and pre-event LinkedIn announcements not attendance proof. Copyright2024 not incorporated date. Third-party logos, ROI, safety, accuracy and production/customer counts unverified; official parent tax still pending.')

antaja=next(c for c in candidates if c['id']=='S018')
antaja.update(legal_name='',country='VN',website='https://www.antaja.com/',
    notes='Website legal terms self-declare incorporation in Vietnam and footer uses Antaja Co., Ltd.; exact registered name/MST mapping remains unverified. Vietnamese name CÔNG TY TNHH ANTAJA / candidate MST0110515925 from secondary directories, not official tax. Cached GitHub web result names Antaja Company Limited, while current raw capture says ant & aja Lab without same website mapping; not used as current legal identity. QLINX post explicitly describes R&D and future finalist meeting. RTK/control and compliance-module pages Coming Soon/currently under development. Product completion, physical prototype/output, startup stage, independent recent activity and regulatory permission unverified. Homepage lists intended thermal/UAV/RTK/cloud features; fleet counts are simulation. GitHub forks not own IP or customer delivery.')
add('S018','identity','antaja_company','Copyright © 2026 Antaja Co., Ltd.',
    caveat='Own footer names company in abbreviated English; exact registered Vietnamese name/MST not corroborated. Do not treat cached GitHub company name as current identity: raw capture has a different display name.')
add('S018','identity','antaja_terms','a technology research and development company incorporated in Vietnam.',
    caveat='Company own legal terms self-declare Vietnam incorporation; reviewed as page content without registration, order or acceptance. Does not verify tax or specific approvals.')
add('S018','technology','antaja_qlinx_linkedin','Tại Antaja, chúng tôi đang nghiên cứu và phát triển QLINX™',platform_operator='LinkedIn',
    caveat='Company describes R&D for identity/verification/trust of autonomous systems; not completed production, registered IP, cm-level positioning test or permission for autonomous flight.')
add('S018','product','antaja_qlinx_module','This solution is currently under development.',
    caveat='Withheld from product gate: detail page is Coming Soon, not a verified functional product, manufactured module or customer deployment.')
next(e for e in evidence if e['id']=='E_antaja_qlinx_module_product_S018')['reviewed']=False
add('S018','counter_review','antaja_rtk','This solution is currently under development.',
    search_queries=['"ANTAJA" "giải thể"','"Antaja" "ceased operations"'],
    review_note='No verified closure found for exact Vietnam company in relevant results; Finnish/Indonesian homonyms excluded. Homepage features and simulation fleet counts not installed assets. RTK/control and compliance-module detail pages Coming Soon, so product gate remains pending. LinkedIn invitation to August finale not attendance proof. Forked GitHub projects not own inventions or independent activity. Secondary tax active status not official tax; planned2030 scale not current results.')

fillsonic=next(c for c in candidates if c['id']=='S020')
fillsonic['notes']='QVIC shortlist describes adaptive multi-speaker edge audio, but no verified functional product, primary legal identity, startup stage or current operations found in scoped searches. Candidate CÔNG TY CỔ PHẦN FILLSONIC / MST0111030296 only from secondary directories; not entered as verified legal/tax. One obvious domain attempt fillsonic.com returns Fill Sonic Coming Soon, without legal ID or link proving relation to QVIC company; official website field remains empty. Sparse indexed results do not mean company closed. Do not infer hardware manufacture from registered industry or confuse clothing Fillsonic650 branding.'
base=next(e for e in evidence if e['id']=='E_QVIC26_S020')
for kind,reviewed in [('counter_review',True),('product',False)]:
    record=dict(base,id=f'E_FILLSONIC_SHORTLIST_{kind.upper()}',kind=kind,reviewed=reviewed)
    if kind=='counter_review':
        record.update(search_queries=['"Fillsonic" "giải thể"','"Fillsonic" "closed"','"Fillsonic" "speaker"','"Fillsonic" "loa"'],
            review_note='No verified closure found, but primary legal/company/product/activity sources remain insufficient after scoped searches. Secondary candidate MST0111030296 and guessed Coming Soon domain not verified as QVIC company. No company contact sent, signup, order or identity inferred from missing web presence.')
    else:
        record['caveat']='Withheld from product gate: original organiser image states a concept/solution, without functional product, prototype or producer evidence; physical classification left unreviewed.'
    old=next((e for e in evidence if e['id']==record['id']),None)
    if old: evidence[evidence.index(old)]=record
    else: evidence.append(record)
    assert not validate_evidence(dict(record,reviewed=True),date(2026,10,15),DATA)

pdf=DATA/'sources/brainlife_ipo_459A1.pdf'
txt=pdf.with_suffix('.txt')
manifest['brainlife_ipo_459A1']=dict(id='brainlife_ipo_459A1',source_type='government',publisher_owner='Cục Sở hữu trí tuệ',url='https://www.ipvietnam.gov.vn/documents/20182/2416858/CB459A1.pdf/60490e29-eca2-425b-8a71-b1d7dc48dc5d',status='fetched_pdf',fetched_at='2026-10-15',snapshot='sources/brainlife_ipo_459A1.txt',sha256=hashlib.sha256(txt.read_text(encoding='utf-8').encode()).hexdigest(),pdf_file='sources/brainlife_ipo_459A1.pdf',pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
brainlife=next(c for c in candidates if c['id']=='S019')
brainlife.update(legal_name='CÔNG TY CỔ PHẦN CÔNG NGHỆ BRAIN-LIFE LINK',country='VN',physical='yes',website='https://brainlife.ai/',
    notes='IPO original gazette459A1 page32 names VN applicant; application1-2024-08724 published15/05/2026, not a granted patent or clinical approval. Candidate parent MST0318400345 only secondary, branches001/002/003 not parent. Focus+ physical BCI/EEG wearable offered for preorder; no verified mass shipment, clinical efficacy or device approvals. Product FAQ calls it consumer technology, not diagnosis/treatment. Company preorder offer observed15/10/2026 and IPO publication are distinct sources/origins; offer is not completed sale. SIHUB profile MVP but founding2014 conflicts with company/secondary2024: date unresolved, not silently corrected. UK contacts/brand not substituted for Vietnam legal entity.10+ patents, partners, founding-age and investment/cloud-credit claims not independently audited.')
add('S019','identity','brainlife_ipo_459A1','CÔNG TY CỔ PHẦN CÔNG NGHỆ BRAIN-LIFE LINK (VN)',page=32,
    caveat='Official applicant identity and VN designation, not current tax status or proof that all related foreign brand entities are the same company.')
add('S019','startup','brainlife_sihub_profile','Giai đoạn Sản phẩm / Dịch vụ Sơ khai (MVP)',
    caveat='Startup platform profile says MVP. Provider submission not independently audited;2014 founding field conflicts with2024 in other sources and is left unresolved. MVP stage not inferred from patents or research team age.')
add('S019','product','brainlife_focus_product','Deliver advanced BCI wearables and software for focus, stress management, and health monitoring.',
    caveat='Physical wearable offered for preorder, not verified mass delivery. Own FAQ says consumer technology not intended for diagnosis/treatment. Testimonials, first-in-Vietnam and European-standard claims not independent efficacy/certification proof.')
add('S019','technology','brainlife_company','Thiết bị của Brain-Life thu thập tín hiệu EEG',
    caveat='Company describes EEG capture and AI/cloud analysis. Cognitive-state accuracy, benefit, biomedical-data protection and clinical claims not independently tested.')
add('S019','technology','brainlife_ipo_459A1','GIAO DIỆN TƯƠNG TÁC MÁY TÍNH NÃO KHÔNG CẦN HIỆU CHUẨN',page=32,
    caveat='Published application subject matter, not granted protection, successful implementation, regulatory authorisation or proof calibration is unnecessary in all uses.')
add('S019','activity','brainlife_ipo_459A1','(43) 15/05/2026',event_date='2026-05-15',published_at='2026-05-15',page=32,
    origin_id='brainlife_application_1_2024_08724_publication_20260515',activity_role='supporting_rd_publication',
    caveat='Application publication milestone, not grant date, manufacturing or clinical deployment.')
add('S019','activity','brainlife_focus_product','Reserve today to receive an exclusive discount for Early Explorers.',event_date='2026-10-15',
    origin_id='brainlife_focus_preorder_offer_observed_20261015',activity_role='observed_live_product_offer',
    event_date_basis='Live preorder offer observed at capture; not product release, order fulfilment or commissioning date.',
    caveat='Self-published commercial offer only. March beta/June delivery roadmap has no verified year/completion; no200 beta units,1000 preorders or delivered volume inferred.')
add('S019','counter_review','brainlife_focus_product','It is not intended for medical diagnosis or treatment.',
    search_queries=['"Brain-Life" "giải thể"','"Brain-Life" "closed" Vietnam'],
    review_note='No verified closure for exact VN entity in relevant sources; US Brain Life LLC litigation, brainlife.io research platform and Japanese Brain Life Imaging excluded. SIHUB2014 versus2024 founding unresolved. UK contacts not VN legal substitute. Patent applications not grants; Google cloud programme credits not equity cash; claimed10-billion-VND investment not independently reconciled. Consumer FAQ excludes diagnosis/treatment. Preorders/roadmap not delivery or clinical validation.')

fizibox=next(c for c in candidates if c['id']=='S022')
fizibox.update(brand='FIZIBOX',tax_id='0319317523',country='VN',physical='hybrid',website='https://fizibox.com/',
    notes='Standardised brand to FIZIBOX from current own site; original shortlist transcript FIZIBBOX retained as historical alias, not separate company. Own footer Fizibox Corp and parent candidate tax0319317523; exact VN legal name CÔNG TY CỔ PHẦN FIZIBOX still secondary, no official tax. Hybrid industrial edge AI nodes/software for existing cameras.99% false-alarm reduction,15s response, patents, airport/TBS cases, fire-safety compliance and customer deployment counts not independently verified. Some product/about links404; zero/blank animated metrics not interpreted as zero deployments. GenAI Fund reports participation/pitch at meetup23/04/2026, distinct from August own product offer. Angel tranche ask indicates early-stage fundraising context, not completed investment or client contract.')
add('S022','identity','fizibox_company','Fizibox Corp',
    caveat='Own footer identifies abbreviated English brand/company and tax0319317523. Exact registered VN legal name unverified; official tax result required. Historical shortlist typo FIZIBBOX not another company.')
add('S022','product','fizibox_company','Industrial-Grade Hardware Nodes',
    caveat='Vendor describes physical edge nodes integrated with software and existing cameras, hence hybrid. Not proof of manufacturing volumes, certified fire alarm function or paid customer deployment.')
add('S022','technology','fizibox_about_post_202608','Fizibox Node có thể được đặt gần nguồn dữ liệu để xử lý hình ảnh ngay tại chỗ.',published_at='2026-08-09',
    caveat='Vendor mechanism of edge processing/selective alerts. Accuracy, false-positive reduction, failover, cyber/data security and safety compliance not independently tested.')
add('S022','activity','fizibox_about_post_202608','Fizibox hỗ trợ từ bước làm rõ nhu cầu, chọn cấu hình Fizibox Node phù hợp',
    event_date='2026-08-09',published_at='2026-08-09',origin_id='fizibox_product_service_offer_report_20260809',activity_role='self_published_product_offer',
    caveat='Dated own product/service offer report, not verified field acceptance or customer contract. Owner distinct from GenAI Fund April meetup report.')
add('S022','counter_review','fizibox_company','Tax code: 0319317523',
    search_queries=['"Fizibox" "giải thể"','"Fizibox" "closed"'],
    review_note='No verified closure for exact VN brand in relevant sources; Hungarian classroom kits and homonyms excluded. Own tax footer not official active-tax evidence.99%/15s, patents, case studies, logo support, compliance and deployment numbers not independently verified; blank rendered counters not zeros. Some product/about links404, not evidence company closed. GenAI Fund meetup report supplies separate source/event; angel fundraising ask is not cash received, signed partnership or independent safety validation.')
add('S022','startup','fizibox_genai_meetup_202604','Ask: $50K angel tranche, industrial, F&B, and retail partnerships, and an Associate Founder in BD and Global Relations',
    caveat='Organiser recap describes fundraising/cofounder needs, supporting early-stage startup context by inference. Not an incorporation date, investment received or investor endorsement of performance.')
add('S022','activity','fizibox_genai_meetup_202604','FIZIBOX: An edge AI operating system built around dual-stage cognitive verification',
    event_date='2026-04-23',origin_id='fizibox_genai_builders_meetup_20260423',activity_role='organiser_reported_meetup_pitch',
    event_date_basis='Event date from recap page title April23,2026; URL date April24 not separately treated as verified publication metadata.',
    caveat='GenAI Fund recap lists representative Tran Le Phuong Duyen and FIZIBOX among builders who pitched in Ho Chi Minh City. Distinct from August own product offer; not proof of investment, customer delivery, hardware certification or legal/tax identity.')

fst=next(c for c in candidates if c['id']=='S023')
fst.update(legal_name='CÔNG TY CỔ PHẦN CÔNG NGHỆ KHÔNG GIAN TƯƠNG LAI',country='VN',physical='yes',website='https://www.fstech.vn/vi',
    notes='Same company website uses full Vietnamese legal name in VI title and Future Space Technology JSC in EN title, with same FS Corp brand/address. Candidate parent MST0316051120 only from secondary directories; not verified official tax. Website offers VS/IVS drones and FS software; own manufacture, performance, licenses and delivery not independently checked. OmniEye in original QVIC shortlist not found on reviewed website pages, so do not identify VS/IVS as OmniEye. No verified startup stage/founding date: copyright2025 not incorporation, secondary2019 not primary. Current product offer observed15/10/2026 supplies one own activity only; independent recent activity still missing. Procurement directory suspension due overdue participation fees is not official tax closure; directory representative/old MITECH names differ and not reconciled. Homepage ACTIVE labels are demo/system text, not live assets or tax status; placeholder social URLs not verified company profiles.')
add('S023','identity','fst_company','Công ty Cổ phần Công Nghệ Không Gian Tương Lai',
    caveat='VI document title gives full company name; EN about page on same domain titles Future Space Technology JSC with same FS Corp/address. Self-identification, not registry/tax proof. No reviewed page maps OmniEye to a VS/IVS model.')
add('S023','product','fst_solutions','IVS-60: Drone cánh quay',
    caveat='Own product catalogue offers physical VS/IVS drones alongside FS software; classified physical by offered output. Manufacture, working prototype, delivered units and performance not independently verified. Do not equate these named drones to QVIC OmniEye vision module.')
add('S023','technology','fst_about','Tích hợp chip AI Qualcomm (Snapdragon), công nghệ 5G và Wifi6.',
    caveat='Vendor describes embedded AI/connectivity plus flight-control/composite manufacture. Qualcomm component reference does not establish endorsement, exact chip, independently measured capability or local content ratio.')
add('S023','activity','fst_solutions','Showcases các công cụ cụ thể mà FSCorp cung cấp',
    event_date='2026-10-15',origin_id='fst_live_drone_software_offer_observed_20261015',activity_role='observed_live_product_offer',
    event_date_basis='Undated catalogue offer observed at capture, not release, commissioning or delivery date; footer2025 not activity date.',
    caveat='One company-owned public offer only; no customer-side completion, paid order, external recent event or second independent publisher established by scoped searches.')
add('S023','counter_review','fst_about','Được Bộ Quốc phòng cấp phép thiết kế, sản xuất và bảo dưỡng tàu bay không người lái.',
    search_queries=['"Future Space Technology" "closed"','"CÔNG TY CỔ PHẦN CÔNG NGHỆ KHÔNG GIAN TƯƠNG LAI" "giải thể"','"OmniEye" "QVIC"','"fstech.vn" -site:fstech.vn'],
    review_note='No verified closure of this exact entity found; evidence remains sparse after scoped searches. Site claims defense/pilot-training permissions without reviewed licence numbers/documents: not verified authority or general flight permission. Percent accuracy/savings, flight durations/ranges, IP67, AES256 and RTK precision not independently tested. Copyright2025 not founding date; ACTIVE/status labels not live telemetry or tax result. Generic GitHub/LinkedIn/Twitter links containing FS Corp placeholder not used as corroboration. Unrelated FSpace/FPT satellites, overseas OmniEye cameras/research/edge satellites, PVcomBank Future Space initiative and Fusan FSCORP excluded.')
add('S023','counter_review','fst_procurement_context','Tạm ngừng do nợ phí quá hạn',
    search_queries=['"0316051120" "tạm ngừng"'],
    review_note='Secondary procurement directory records01/04/2025 fee suspension and explicitly frames nonpayment as stopped transactions on e-procurement system. Not official tax result, proof of legal dissolution or current company closure; do not mark excluded. Representative/name history MITECH differ across directories and are unresolved, not evidence of fraud or another parent entity. No paid report/login consulted.')

medcat=next(c for c in candidates if c['id']=='S026')
medcat.update(legal_name='CÔNG TY CỔ PHẦN MEDCAT',country='VN',physical='no',website='https://medcat.vn/',
    notes='Company own Hanoi launch report explicitly names Công ty Cổ phần MedCAT. Parent candidate MST0110578065 from secondary directories only, not official tax or entered as verified ID. Keep MedCAT TPA candidate0110956983 separate despite linked subdomain. IDUS/Nexus and AIInsurance are software/document-data platforms; no own physical-device output established. Government reports Digital Startup Gold award15/01/2026; own report26/02/2026 Hanoi innovation ecosystem certificate is separate activity/owner, not verified paid strategic data contract or completed deployment. SLM/VLM/OCR mechanism described;99%up-to product claim,97%field-level event report and95%testimonial have different scopes, no independent benchmark/clinical benefit or compliance audit. Unrelated CogStack MedCAT toolkit/archive, foreign MedCat firms, trademarks and medical-school names excluded; no foreign research/IP attributed.')
add('S026','identity','medcat_hanoi_launch_vn','Công ty Cổ phần MedCAT vinh dự nhận chứng nhận Đơn vị đồng hành',
    caveat='Own report explicitly ties company legal name and MedCAT brand to Hanoi event; no parent tax ID on reviewed page, and no merger with separately named MedCAT TPA.')
add('S026','startup','medcat_mst_asean_award_202601','MedCAT Nexus by MedCAT won the Gold Award in the Digital Startup category.',published_at='2026-01-16',
    caveat='Government reports startup-category award, supporting startup context; not incorporation date, official tax status or an investment received.')
add('S026','product','medcat_idus','Nền tảng đọc hiểu và tái cấu trúc dữ liệu thông minh IDUS của MedCAT',
    caveat='Offered software platform for document digitisation/OCR and structured data; classified nonphysical. Healthcare/insurance focus does not establish own medical-device manufacture or validated clinical decision-making.')
add('S026','technology','medcat_mst_asean_award_202601','combining a Small Language Model (SLM) and a Vision-Language Model (VLM)',published_at='2026-01-16',
    caveat='Government award report describes architecture; no independent code/model-origin, privacy, accuracy, medical benefit or production-scale audit. OCR, VLM/SLM and award not regulatory device approval.')
add('S026','activity','medcat_mst_asean_award_202601','MedCAT Nexus by MedCAT won the Gold Award in the Digital Startup category.',
    event_date='2026-01-15',published_at='2026-01-16',origin_id='medcat_asean_digital_award_20260115',
    event_date_basis='Report dated16January2026 explicitly places award ceremony on evening15January.',
    caveat='Award report, not customer acceptance, prize cash received or tax lookup. Vietnamese ministry/company articles covering same award are not additional activity origins.')
add('S026','activity','medcat_hanoi_launch_vn','Ngày 26/02/2026, trong khuôn khổ Lễ công bố thành lập Công ty Cổ phần Trung tâm Đổi mới Sáng tạo Hà Nội, Công ty Cổ phần MedCAT vinh dự nhận chứng nhận Đơn vị đồng hành',
    event_date='2026-02-26',origin_id='medcat_hanoi_innovation_ecosystem_certificate_20260226',activity_role='self_reported_ecosystem_certificate',
    caveat='Company report supports a separate participation/certificate milestone from January award. Strategic-partner language does not prove paid data contract, government procurement, funding or commissioned infrastructure. English/Vietnamese posts same owner and event.')
add('S026','counter_review','medcat_idus','độ chính xác lên tới 99%',
    search_queries=['site:medcat.vn "giải thể"','"MedCAT" "closed" Vietnam'],
    review_note='No verified closure for exact Vietnam entity found in scoped searches. CogStack MedCAT Medical Concept Annotation Toolkit GitHub archive/issues and foreign company acquisitions are unrelated, not VN closure or IP.99%up-to own product claim,97%field-level award report and95%testimonial not interchangeable benchmarks; populations/test methods not independently checked. No diagnostic efficacy, medical-device approval, security/privacy compliance, in-house model provenance, customer volumes or production performance established. MedCAT TPA linked service not automatically same parent legal entity/MST; NIC contact address not registered-office proof. Tax0110578065 still secondary only.')

healthbridge=next(c for c in candidates if c['id']=='S024')
healthbridge.update(legal_name='',tax_id='',country='',physical='no',website='https://www.healthbridgeai.com/',
    notes='JarvisMD software clinical scribe, not own physical device or autonomous clinical decision system. Homepage footer Cyber GBA Limited trading as HealthBridge AI; terms effective04/03/2026 name HealthBridge AI Pte.Ltd. Neither reconciled as Vietnamese registered company. VN staff/presence and company LinkedIn founded2023 do not establish VN legal entity. Secondary HEALTHBRIDGE VIETNAM/MST0319276080 and HealthBridge Consult not mapped; do not adopt namesake tax IDs. Own live service offer observed15/10/2026 only; no second independently dated recent activity established. HSAClassA/SaMD,privacy/compliance claims self-published, registry not checked. Homepage no secondary data use vs terms permitting deidentified/aggregated improvement need reconciliation; no breach inferred. Terms require clinician review, not diagnosis/treatment or authoritative patient record. Separate Canada NGO, SouthAfrican Healthbridge/Nora, MTNfitnessapp and hackathon/GitHub namesakes.')
add('S024','identity','healthbridge_terms_202603','JarvisMD / HealthBridge AI Pte. Ltd.',
    caveat='Foreign-style provider name in own terms, not a verified Vietnamese entity. Homepage separately says Cyber GBA Limited trading as HealthBridge AI; corporate relation/jurisdiction not reconciled. No Vietnam legal-name/MST mapping claimed.')
add('S024','startup','healthbridge_company_linkedin','Founded\n2023',platform_operator='LinkedIn',
    caveat='Company self-reported founding/team profile, supports startup context only. Not incorporation certificate, Vietnam company registration or current official tax result.')
add('S024','product','healthbridge_company','captures your consultation audio and generates draft clinical notes in real time',
    caveat='Vendor offers JarvisMD software transcription/draft notes, classified nonphysical. Not own medical hardware, independent diagnosis, EMR system of record or verified clinical efficacy.')
add('S024','technology','healthbridge_company','Audio is captured securely and processed in real time using medical-grade speech recognition.',
    caveat='Vendor mechanism statement, not security/performance validation or certification. Draft notes require clinician editing/approval before transfer to authoritative EMR/EHR.')
add('S024','activity','healthbridge_company','Real-time audio-to-text transcription',event_date='2026-10-15',
    origin_id='healthbridge_live_jarvismd_offer_observed_20261015',activity_role='observed_live_product_offer',
    event_date_basis='Live offer observed at capture, not product release, paid deployment or treatment date.',
    caveat='One company-owned offer; recruitment posts with relative dates and old BLOCK71 URL now redirecting to generic B71 landing not used as independently dated recent activity.')
add('S024','counter_review','healthbridge_terms_202603','JarvisMD does not provide medical advice, diagnosis, or treatment decisions.',
    search_queries=['"HealthBridge AI" "giải thể"','"HealthBridge AI" "Cyber GBA" "Vietnam"'],
    review_note='No verified exact-entity closure found in scoped searches; company legal mapping remains unresolved. Terms name HealthBridge AI Pte.Ltd while homepage Cyber GBA Limited; not silently merged as VN entity. Vendor HSAClassA/SaMD,GDPR/HIPAA/PDPA,security/clinical benefit claims not independently checked. Homepage says no secondary data use but terms permit deidentified/aggregated improvement: scope unresolved, no illegal use inferred. Medical notes require independent clinician review and EMR remains record. Canada HealthBridge NGO, SouthAfrican company/Nora acquisition, workoutapp and AmazonNova/hackathon/GitHub projects unrelated. Closing job applications not company closure. Secondary0319276080 not mapped to this brand; no namesake MST substituted.')

hitek=next(c for c in candidates if c['id']=='S025')
hitek.update(legal_name='',tax_id='',country='VN',physical='hybrid',website='https://hitekdrone.com/',
    notes='Drone Light Show service with programmed swarm/software and physical drone hardware, classified hybrid, not verified own drone manufacture. Own about page identifies parent CTCP Tập đoàn Công nghệ Hitek; exact contracting/QVIC legal entity remains unresolved. Secondary same-name Hitek Drone candidate MST0109744857/0110423255 not interchangeable or entered. Own TeamHitek StartupWheel2023 account supports startup context, not individual CV/foundingdate proof. Current live offer observed15/10/2026 only. Cup2025/26 project says14/09, not recent just because season spans2026; not counted within365days. Allumee public post linksHitekDrone/HiDrone but date relative/uncorroborated, HTTPcapturefailed: not activity gate. Self safety/flightpermits/fleetcounts/softwareIP not audited; parent/groupsubsites same publisher, not independent events.')
add('S025','identity','hitek_group_company','Công ty Cổ phần Tập đoàn Công nghệ Hitek (Hitek Group JSC)',
    caveat='Own group footer gives parent name, linked by drone site. Not proof parent is contracting/QVIC tax entity; leave exact legal-name/MST fields unset until reconciled with Hitek Drone entities.')
add('S025','startup','hitek_about','Giải Nhì Bảng Việt Nam tại cuộc thi Startup Wheel 2023',
    caveat='Own Team Hitek competition account, not independent award verification or corporate founding date. Founder CV/startup years and parent age kept separate from drone legal entity.')
add('S025','product','hitek_about','Trình diễn ánh sáng nghệ thuật bằng thiết bị bay không người lái – Drone Light Show',
    caveat='Offered service combines physical drone fleet and software, classified hybrid. Not proof of own drone manufacture, delivery volumes, fleet ownership or flight/safety certification.')
add('S025','technology','hitek_drone_service','tự nghiên cứu và viết phần mềm độc quyền',
    caveat='Vendor describes own show-programming software and trials; no code/IP ownership, swarm accuracy, production count or failure/safety performance independently checked.')
add('S025','activity','hitek_drone_service','khả năng cung cấp dịch vụ trọn gói hoàn toàn tự chủ',event_date='2026-10-15',
    origin_id='hitek_live_drone_show_offer_observed_20261015',activity_role='observed_live_product_offer',
    event_date_basis='Live service offer observed at capture, not completed show, release or contract date.',
    caveat='One own service offer. Group/Flycam/Drone websites same publisher; no multiple independent activity owners inferred.')
add('S025','counter_review','hitek_about','Công ty mẹ là CTCP Tập đoàn Công nghệ Hitek',
    search_queries=['"Hitek Drone" "giải thể"','"HITEK" "giải thể" "Drone"'],
    review_note='No verified closure of exact brand found; same-name companies and parent/subsidiary tax relationships unresolved. Candidate0109744857/0110423255 not arbitrarily chosen. Physical show operation not evidence manufacturing hardware. Local permit advice/safety/insurance/fullautonomy claims not verified authorisations or safety test. Allumee post supports HitekDrone/HiDrone alias but relative date insufficient for recent activity; no date inferred from cached age. StartupWheel personalCV not substituted for TeamHitek account; old awards not recent activity. Software-only Hitek firms/overseas Hitek homonyms not merged.')
add('S025','counter_review','hitek_national_cup_project','Tối ngày 14/09 vừa qua',
    search_queries=['"Hitek Drone" "2026" site:allumee.com'],
    review_note='Company project is titled NationalCup2025/26 and gives14/09 without separately verified year. Do not use season2026 as event year or assume within365day window; project omitted from recent activity gate. No customer-side acceptance, invoice, exact event date or counted fleet independently checked.')

ologn=next(c for c in candidates if c['id']=='S029')
ologn.update(legal_name='CÔNG TY TNHH OLOGN TECHNOLOGY',country='VN',physical='yes',website='https://ologn.tech/',
    notes='Original TuoiTre04/10/2026 names Công ty TNHH OLOGN Technology and founders with photographed NAWI prototype. Own site team HuyDuong/LuanLe and LinkedIn same website match brand context. Candidate parentMST0316563337 onlysecondary; old ORCO internship-document mirrors not primary/current tax rename proof, ID left unset. Physical NAWI AR clip-on prototype, preparing real-world trials; no completed firefighter field validation, certified explosive-atmosphere use, sales or deployments established. Earliest2027market plan and1500USD are forecasts, not delivery/transaction. Edge AI/camera/iToF/gas/thermal architecture reported; gas threshold/drift MCU path explicitly not ML, do not call all sensors AI. Oct4prototype-development report and ownOct9HUTECHevent distinct owners/origins; copiesVietnam.vn/inkl sameTuoiTreowner. Homepage SaulGoodman/MattBrandon/JohnLarson testimonials and template success messages/counters not verified clients or sent forms. Separate o-logn.com Solutions and OLogNTechnologiesAG patents/litigation.')
add('S029','identity','ologn_nawi_tuoitre_202610','Công ty TNHH OLOGN Technology',published_at='2026-10-04',
    caveat='Original organiser/interview report names company, founders and NAWI. Matches own website team HuyDuong/LuanLe; no verified parent tax ID, incorporation or old ORCO rename inferred.')
add('S029','startup','ologn_nawi_tuoitre_202610','hoàn thiện mẫu thử',published_at='2026-10-04',
    caveat='Prototype-stage venture described in original TuoiTre Startup Award coverage, supporting startup/product-stage context. Project development from late2025 is not company incorporation date; coverage not award winner or commercial validation.')
add('S029','product','ologn_nawi_tuoitre_202610','thiết bị AR dạng clip-on',published_at='2026-10-04',
    caveat='Article documents physical NAWI prototype/board/HUD and founder description, not merely software service. Field trials still being prepared; no fireground safety certification, explosive-atmosphere approval, mass manufacture, customer delivery or lifesaving performance independently validated.')
add('S029','technology','ologn_company','Customized firmware and embedded software development',
    caveat='Own engineering-services mechanism description. NAWI architecture in original report includes thermal/RGB/iToF/AR and edge processing onQCS8250, but gas threshold/drift MCU path explicitly not ML. No source-code, sensor accuracy/latency, all-condition offline function or safety audit performed.')
add('S029','activity','ologn_nawi_tuoitre_202610','đang chuẩn bị thử nghiệm thực tế',event_date='2026-10-04',published_at='2026-10-04',
    origin_id='ologn_nawi_prototype_development_report_20261004',activity_role='reported_prototype_development_status',
    event_date_basis='Current prototype status reported on publication04Oct2026; exact build/demo date unknown, not field-trial completion.',
    caveat='Original report/interview with board/HUD photos, supporting current R&D activity. Vietnam.vn/inkl syndications same owner and origin; no extra independent publishers/events counted. Forecast market2027/price1500USD not shipment or revenue.')
add('S029','activity','ologn_company_linkedin','Sáng 09/10/2026, O(log n) tham dự chương trình HUTECH Business Connect',event_date='2026-10-09',
    origin_id='ologn_hutech_business_connect_participation_20261009',platform_operator='LinkedIn',activity_role='company_reported_event_participation',
    caveat='Own company post explicitly states event date, distinct from October4 prototype report. Not independently confirmed attendance, signed partnership, hiring volume, grant or commercial contract; relative post age not used as date.')
add('S029','counter_review','ologn_company','Saul Goodman',
    search_queries=['"OLOGN" "giải thể"','"OLOGN" "closed"','"0316563337" "OLOGN" "ORCO"'],
    review_note='No verified closure for exact VN entity found; OLogNTechnologiesAG Liechtenstein patents/Xiaomi litigation and generic algorithm/OLOGN Solutions sites excluded. Own homepage has SaulGoodman/MattBrandon/JohnLarson testimonials/template labels and success messages; not verified customers, counts or evidence form submitted. No message/signup sent. NAWI prototype not finished fieldtrial; explosive-atmosphere certification future condition,2027market/1500USDplan not shipped units. Camera/sensor performance,foundry/manufacturing IP,safety and official tax unverified. ORCO/MST0316563337 olddocument mirrors not primary/current rename proof; copies of TuoiTre not independent activity sources.')

pdf=DATA/'sources/udata_credential.pdf'
txt=pdf.with_suffix('.txt')
manifest['udata_credential_pdf']=dict(id='udata_credential_pdf',source_type='company',publisher_owner='UDATA',url='https://udata.ai/credential.pdf',status='fetched_pdf',fetched_at='2026-10-15',snapshot='sources/udata_credential.txt',sha256=hashlib.sha256(txt.read_text(encoding='utf-8').encode()).hexdigest(),pdf_file='sources/udata_credential.pdf',pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
udata=next(c for c in candidates if c['id']=='S031')
udata.update(legal_name='CÔNG TY CỔ PHẦN UDATA',country='VN',physical='hybrid',website='https://udata.ai/',
    notes='BK Fund original post names Công ty cổ phần Udata and investment agreement09/07/2026, not amount/closed disbursement. OwnJuly30BKE MOU report separateevent, not paid customercontract/commissionedsolarproject. Original19pagePDF18.6MB text extracted, page12visuallyread shows USG/UBG/UOG physicalgatewaycatalogue; Uboardsoftwareplusgatewayintegration classified hybrid, not independently proven own manufacture/delivery. PDFpage10UgateAIgateway is not automatically same physicalproduct. ParentMST0110848057secondaryonly, recruitmentsite0110902473conflicts so no arbitraryIDselection. Company LinkedInFounded2024andPublicCompanyselfcategories not verified incorporation/listing. Fund startupDeepTech context. Currentwebsite animatedcounterszero/0.0notactualno-deploymentoruptime values; efficiency/security/OEE/ESGclaimsnot independently benchmarked or certification. GooglePlayaccountclosurepostUDATATechnologiesidentitynotmapped; opendatateamudata/foreignnamesakesnotattributed.')
add('S031','identity','udata_bkfund_investment_post','Công ty cổ phần Udata',
    caveat='Fund original post identifies legal name and linked UDATA brand/solutions. No parent tax ID in reviewed text; candidate0110848057 and recruitment0110902473 not reconciled by name/address alone.')
add('S031','startup','udata_bkfund_investment_post','startup Deep Tech',
    caveat='Investor explicitly describes startup context. No funding amount, actual disbursement, audited customer acceptance, incorporation date or exchange listing verified; LinkedInPublicCompany is not listing evidence.')
add('S031','product','udata_uboard','Consolidate multi-source data into an intuitive platform',
    caveat='Offered Uboard software for factory/energy/equipment data. Hybrid classification relies additionally on stated EMS/hardware integration, not proof Uboard itself is a physical box or UDATA manufactures all sensors/gateways.')
add('S031','product','udata_company_linkedin','high-quality hardware components',platform_operator='LinkedIn',
    caveat='Company describes integrating EMS with hardware in BKE partnership context, supporting hybrid solution model. Not independent own-hardware production, installed volume, accepted deployment or proof Ugate AI platform equals older MiniUgate gateway.')
add('S031','product','udata_credential_pdf','Udata Gateway',page=12,
    caveat='Original company PDF19pages, page12 rendered/read: physical USG/UBG/UOG units and interface/spec table. Supports hybrid hardware/software catalogue, not independently tested specs, manufacture origin, delivery volumes or safety certification. Page10 Ugate AI Gateway software kept distinct; no publication date inferred from capture or embedded PDF metadata.')
add('S031','technology','udata_uboard','AI Reporting',
    caveat='Vendor describes reporting/AI answers, multisource operational data, alerts and IoT monitoring. No source-code, model-provenance, safety/security/30-dayoffline capability or ROI benchmark audit. Energy/OEE efficiency claims not certification.')
add('S031','activity','udata_bkfund_investment_post','officially signed an investment agreement',event_date='2026-07-09',
    origin_id='udata_bkfund_investment_agreement_20260709',platform_operator='LinkedIn',activity_role='investor_reported_agreement_signing',
    event_date_basis='Fund English/Vietnamese post explicitly gives9July2026; relative post age not used.',
    caveat='Investor reports signed agreement only; no amount, bank transfer, equity registration, governance completion or customer contract verified. Reposts by UDATA/ThinkZone/individuals same originalowner/event.')
add('S031','activity','udata_company_linkedin','Memorandum of Understanding (MOU)',event_date='2026-07-30',
    origin_id='udata_bke_solar_partnership_mou_20260730',platform_operator='LinkedIn',activity_role='company_reported_mou_signing',
    event_date_basis='Company post explicitly states30July2026; no publication date inferred from relative age.',
    caveat='Separate date/partner/event from BK Fund agreement. Self-report MOU with BKE Vietnam, not signed paid supply contract, realised savings, operating solar site or regulatory acceptance.')
add('S031','counter_review','udata_uboard','Platform Uptime SLA',
    search_queries=['"UDATA" "giải thể"','"UDATA" "closed" Vietnam'],
    review_note='No verified exact-company closure found in scoped searches. GooglePlayUDATATechnologiesaccountclosurepost not mapped by entity/developer ID; not attributed. opendatateamudata closed issues and foreign firms not company closure/IP. Website0/0.0 animatedcountertext not interpreted as actual zero customers/deployments/uptime. Safety/privacy/energy/OEE/ESG results, costbenefit, customerlogos and grouprelationshipsnot independently audited. Candidate0110848057 vs recruitment0110902473unresolved; no matchingparentofficialtax. LinkedInPublicCompany not stockexchange listing. BKFundsigning not verified cash received; BKE MOU not commissionedproject. Oldgateway names vsnewUgateAIbrandingnot silently merged.')

txt=DATA/'sources/vizion_googleplay_web_read_20261015.txt'
manifest['vizion_googleplay_web_read']=dict(id='vizion_googleplay_web_read',source_type='company',publisher_owner='Vizion Technology',url='https://play.google.com/store/apps/details?hl=vi&id=global.vizion.tour',status='manual_web_read',fetched_at='2026-10-15',snapshot='sources/vizion_googleplay_web_read_20261015.txt',sha256=hashlib.sha256(txt.read_text(encoding='utf-8').encode()).hexdigest(),method='web_text_transcription',capture_note='Selected literal fields from opened web view; HTTP collector failed, cached view age may differ from current store state. No claim full raw page retained.')
vizion=next(c for c in candidates if c['id']=='S033')
vizion.update(legal_name='CÔNG TY CỔ PHẦN CÔNG NGHỆ VIZION',country='VN',physical='no',website='https://vizion.global/',
    notes='Own VN footer fulllegalname and founderThànhTrần match writtenThanhTran founder/chairman in originalQVICimage (re-read, not faceidentification). Smart3DTour/AIInventory software/platform offers, no ownphysicalhardware established; not infer CCTV/robot/warehousehardware from shortlist. ParentMST0317142483/0319020755/0319657216 secondary namesakes unresolved, allleftunset. LegacyLLC/currentCorporation andmultipleaddresses not assumedrename/branchhistory. OwnLinkedInFounded2022 startupcontext, not registry. One liveAIInventoryofferobserved15/10/2026; no second independentlydatedrecentowner/event established. Opened GooglePlayview lists20Aug2025update, outside365days, cachedviewnotverifiedlateststorestate; no freshactivityinferred from crawl/copyrightdates. WebsiteROI/growthstats attributedtoindustrysources not auditedVizionresults, zerosanimatednotactualmetrics. No foreignVizion14Mfunding/shippinganalytics, VixVizion orSamsungISOCELL claimsattributed.')
add('S033','identity','vizion_about_vn','CÔNG TY CỔ PHẦN CÔNG NGHỆ VIZION',
    caveat='Own footer full legal name and founderThànhTrần in same page, consistent with writtenThanhTran role in originalshortlistimage reread. Parent tax/legacyLLC-toCorporation mapping not independently verified; namesakeMSTs not chosen.')
add('S033','startup','vizion_company_linkedin','Founded\n2022',platform_operator='LinkedIn',
    caveat='Company self-reported founding supports startup context, not incorporation certificate. Website startup/Techfest/SaoKhue claims not independent current award verification; copyright2024 not founding date.')
add('S033','product','vizion_smart3d','là giải pháp số hóa không gian',
    caveat='Own Smart3DTour software/360-degree presentation offer, classified nonphysical; phones/cameras used to capture media are not verified own manufactured products. No installation, upload or customer deployment check performed.')
add('S033','product','vizion_ai_inventory','AI Inventory',
    caveat='Own catalogue describes inventory tracking/forecast/replenishment software for retail/manufacturing/logistics. Supports current retail/warehouse offering context, not independently proven AI model, physical device output, functioning stock-control integration or paid deployment.')
add('S033','technology','vizion_smart3d','Tích hợp trợ lý AI bằng giọng nói',
    caveat='Vendor describes voice assistant/media hotspots/visit analytics within virtualtour. No sourcecode, modelprovenance, latency, accuracy, privacy/security, ROI or conversion uplift independently benchmarked.')
add('S033','activity','vizion_ai_inventory','Tự động bổ sung hàng hóa',event_date='2026-10-15',
    origin_id='vizion_live_ai_inventory_offer_observed_20261015',activity_role='observed_live_product_offer',
    event_date_basis='Live service/product offer observed at capture, not release, production acceptance or sale date.',
    caveat='One company-owned offer only. Own website/LinkedIn/store listings not independent owners; thoughtleadership or generalindustryreports not standalone completed business activity.')
add('S033','counter_review','vizion_company','Nguồn: Gartner',
    search_queries=['"Vizion" "giải thể"','"Vizion" "closed" Vietnam','"Vizion" "2026" "hợp tác"'],
    review_note='No verified closure of exact VN company found in scoped searches; coffee-company dissolutionpage relatedlinks, UKproperties/repairnetwork and foreignfirms not attributed. ForeignVizionInc14Mshippingvisibility funding, VixVizion facialrecognition andSamsungISOCELLproducts excluded. Multiple0317142483/0319020755/0319657216parentMSTleads unresolved; no namesake substituted. HomepageROI/growth/productivity stats citeindustrysources not measuredVizioncustomerresults; animatedzeros not actualzeroresult. LegacyLLC/corporation/contactaddresses not automatically renameorbranchproof. No second independentlydatedrecentactivity after scopedsearches; oldawards/pagecrawl dates not newevents.')
add('S033','counter_review','vizion_googleplay_web_read','20 thg 8, 2025',method='web_text_transcription',platform_operator='Google Play',
    search_queries=['"vizion.global" "2026"'],
    review_note='Opened web view lists lastupdate20Aug2025, outside365daywindow at15Oct2026; not a recentactivity event. HTTPcollector failed, saved only literal selectedfields from openedwebview; cached age may differ from currentregionalstorestate, so not claim globallylatestversiondate or closure. Google hosts developercontent, not independentpublisher; downloads/declarations not activeusers, corporateMST or independentlyauditedprivacy. Storeportalvizion.space vsglobal samebrandcontext not legalregistryhistory.')

voria=next(c for c in candidates if c['id']=='S035')
voria.update(legal_name='VORIA SOLUTION TECHNOLOGY COMPANY LIMITED',country='VN',physical='hybrid',website='https://www.voriacare.com/',
    notes='Appleprovider givesEnglishlegalname, GooglePlaydeveloperaddressDongNaiVietnam; VNregisteredname/MST3604052503 stillsecondary, not verified officialtax/representative (directoriesdiffer). VoriaCareapp+physicalVoriaHub/thirdpartymedicaldevices classifiedhybrid, not ownmanufactureordiagnosticapproval. SelfLinkedInhealthtechstartupFounded2025 notregistrationcertificate; PublicCompanynotlisting. GooglePlayupdate24July2026 andSIHUBorganiserSmartHealthcare8Apr2026(article9Apr) distinctowner/event. Google/Applestoredevelopercontent sameVoriaowner, notindependent. VoriaICUGiaDinhcollaboration self-reportedtrial, no hospital-sideacceptance/dateorclinicaloutcomeverification. Appdisclaimernotmedicaldevice/notdiagnosis appliesapp, notverifiedclassificationallhardware/ICU. GooglePlayDataisntencrypted declarationneedsclarification, notruntimefinding orbreachproof; websitecapturefailed. No patientdataentered/appinstalled/demo/contactsent.')
add('S035','identity','voria_appstore','VORIA SOLUTION TECHNOLOGY COMPANY LIMITED',platform_operator='Apple App Store',
    caveat='Seller/provider self-identification linked to VoriaCare/VoriaSolution; GooglePlay same legal English name/address in DongNaiVietnam. Use sourced English name, not invented registered Vietnamese translation. Officialparenttax/VNregisteredname/representative not yet checked.')
add('S035','startup','voria_company_linkedin','healthcare technology startup',platform_operator='LinkedIn',
    caveat='Company explicitly describes startup and self-reportsFounded2025. Not an incorporation certificate, publicly listed company or currenttaxresult; PublicCompanyprofilecategory not exchange listing.')
add('S035','product','voria_googleplay','official companion app for the Voria Hub',platform_operator='Google Play',
    caveat='Developer describes app plus physical Hub bridging third-party glucose/BP/scale/oximeter devices, hence hybrid. Not proof owndevice manufacture, calibrated clinical accuracy, registereddeviceclassification or medicaloutcomes. App explicitly excludes diagnosis/treatment; no app installed or patientdataentered.')
add('S035','technology','voria_googleplay','The app communicates with the Voria Hub via Bluetooth.',platform_operator='Google Play',
    caveat='Vendor describes Hub-to-cloud aggregation and Bluetooth app/configuration. No interoperability, encryption, dataminimisation, alert/sensoraccuracy or performance verification; AIoTlabel alone not validated clinicalAI.')
add('S035','activity','voria_googleplay','Jul 24, 2026',event_date='2026-07-24',platform_operator='Google Play',
    origin_id='voria_care_android_update_20260724',activity_role='developer_reported_app_update',
    event_date_basis='StoreUpdatedonfield in capturedpage, not medicaldevice launch, customercontract, incorporation or deploymentdate.',
    caveat='Developer/platform update signal, not independentGoogleclinical/securityaudit or proof activeusers. Applelisting sameowner, relativeApple25Jul without independentlyverifiedyear not extra event.')
add('S035','activity','voria_sihub_smarthealth_202604','Voria Solution với giải pháp theo dõi sức khỏe tại nhà',event_date='2026-04-08',published_at='2026-04-09',
    origin_id='voria_smart_healthcare_exhibition_20260408',activity_role='organiser_reported_exhibition',
    event_date_basis='SIHUBreport dated9Apr explicitly places event8Apr2026, with Voria listed among solutions.',
    caveat='Organiser report, distinct from Julyappupdate. Bacsigiadinh/press/company versions sameexhibitionorigin, not multiple events. Showcase not regulatoryapproval, paid procurement, grant, hospitalacceptance or independent clinicalvalidation.')
add('S035','counter_review','voria_googleplay','Data isn’t encrypted',platform_operator='Google Play',
    search_queries=['"Voria" "giải thể"','"Voria Solution" "closed"'],
    review_note='NoverifiedclosureforexactVNcompanyfound; LinuxVoria2004/foreignEVcharging/Greeknamesexcluded. StoreDatasafety saysDataisntencrypted while descriptioncallssecuredashboard; developerdeclarationnotruntimeaudit, scope/versionunresolved, nobreachorillegalprocessinginferred. Appnotmedicaldevice/notdiagnosisdisclaimer not regulatorydecisionforallHub/ICUsystems. Downloads/reviewsnotclinicalbenefit/users. Englishproviderprimary vsVietnameselegalname/MST3604052503secondary; representativeNguyenXuanHieu/BuiTrungKienconflictnotresolved. Websitecapturefailed notclosure. No patientdata, signup, installation or contacts.')
add('S035','counter_review','voria_company_linkedin','trong quá trình thử nghiệm và đánh giá hệ thống Voria ICU',platform_operator='LinkedIn',
    search_queries=['"Voria" site:bvndgiadinh.org.vn','"Voria" "Smart Healthcare 2026"'],
    review_note='CompanyselfreportsGiaDinhICUtrial/evaluation, not finished commercialproduct, acceptedclinicaldeployment, diagnosticapproval or validatedoutcome. No exacttrialdate/hospital-sideacceptancechecked; relativepostage notconvertedtoeventdate. SeparateSmartHealthcareexhibitiondate confirmedorganiser but not hospitalclinicalvalidation. Rawpatientimages/data not collected or analysed.')

with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
mp.write_text(json.dumps(list(manifest.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'startup_sources.json').write_text(json.dumps([{k:r[k] for k in ('id','source_type','publisher_owner','url')} for r in manifest.values()],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'candidates':len(candidates),'evidence_records':len(evidence),'companies_reviewed':['S008','S036','S006',airx['id'],buyo['id'],'S014','S005','S016','S002','S007','S034','S028','S027','S030','S032','S017','S057','S018','S020','S019','S022','S023','S026','S024','S025','S029','S031','S033','S035']}))
