"""Record researched leads, without inferring unverified tax or product facts."""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DATA = ROOT/'data/startups'
if (DATA/'candidates.csv').exists() or (DATA/'evidence.jsonl').exists():
    raise FileExistsError('Pilot initialization requires an empty dataset; preserve enriched dossiers.')
manifest = {r['id']:r for r in json.loads((DATA/'source_manifest.json').read_text(encoding='utf-8'))}
candidates = []
evidence = []


def lead(brand, source, quote, published='', physical='', country='', tax_id='', legal_name=''):
    candidate_id = f'S{len(candidates)+1:03}'
    candidates.append(dict(id=candidate_id, brand=brand, legal_name=legal_name, tax_id=tax_id,
        country=country, physical=physical, website='', discovery_url=manifest[source]['url'],
        notes='Lead from opened primary source. Missing facts remain unverified.'))
    row = manifest[source]
    text = (DATA/row['snapshot']).read_text(encoding='utf-8')
    assert quote in text, (brand, 'quote not in fetched source')
    evidence.append(dict(id=f'E{len(evidence)+1:03}', company_id=candidate_id, kind='discovery',
        quote=quote, url=row['url'], snapshot=row['snapshot'], sha256=row['sha256'],
        publisher_owner=row['publisher_owner'], retrieved_at=row['fetched_at'],
        source_type=row['source_type'], published_at=published, reviewed=True, reviewer='Codex: opened primary publication'))
    return candidate_id


quote = 'backing leading companies such as Selex Motors, Stride, Alterno, Enfarm, Neorice, and Forte Biotech.'
for brand in ['Selex Motors', 'Stride', 'Alterno', 'Enfarm', 'Neorice', 'Forte Biotech']:
    lead(brand, 'touchstone_green_2025', quote, '2025-11-20')
lead('N2TP', 'touchstone_n2tp_2026', 'N2TP Technology Solutions JSC was founded in 2020 in Hanoi', '2026-08-12')
for brand in ['Alpha Asimov', 'Eureka Robotics']:
    lead(brand, 'touchstone_n2tp_2026', 'Touchstone has backed notable AI and deep tech names such as Alpha Asimov, Eureka Robotics, Forte, and Prep.', '2026-08-12')
for brand, quote in [
    ('Geninus Vietnam', "Samsung Genome Institute's spinoff that offers genetic testing services to provide insights into your health."),
    ('Hachi', 'Smart hydroponic farming system using IoT technology to provide higher quality agricultural products and productivity.'),
    ('MN Audio', 'High-end audio system with sound chip engineered in Vietnam, transmitting the most high-fidelity sound to listeners.'),
    ('Modmo', 'E-mobility company creating zero-emission urban transportation vehicles with a focus on design and versatility.'),
    ('Sunbot', 'Comprehensive preschool program for kids based on early education methods, STEAM thinking, and robotic technology.'),
    ('ThingsTwin', 'Smart home management system with intuitive 3D interface, customizable for homeowners, easy-to-use for families.'),
    ('Vulcan Augmetics', 'Affordable, life-improving and highly functional electric prosthetics, designed to be upgradable and customizable.'),
]:
    lead(brand, 'vsv_portfolio', brand+'\n'+quote)

selex = candidates[0]
selex.update(tax_id='0108324659', legal_name='CÔNG TY CỔ PHẦN PHƯƠNG TIỆN ĐIỆN THÔNG MINH SELEX',country='VN')
text = (DATA/'sources/selex_tax.txt').read_text(encoding='utf-8')
evidence.append(dict(id='E_TAX_SELEX',company_id='S001',kind='tax',quote=text,
    url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp',snapshot='sources/selex_tax.txt',
    sha256=hashlib.sha256(text.encode()).hexdigest(),publisher_owner='Vietnam Tax Authority',
    retrieved_at='2026-10-13',checked_at='2026-10-13',reviewed=True,reviewer='Codex: live tax table after user-authorized lookup',
    tax_id=selex['tax_id'], legal_name=selex['legal_name'],status='NNT đang hoạt động'))

source = manifest['selex_company']
source_text = (DATA/source['snapshot']).read_text(encoding='utf-8')
for kind, quote in [
    ('identity', 'Công ty Cổ phần\nPhương tiện điện thông minh Selex\nSelex Motors được thành lập vào năm 2018'),
    ('technology', 'Sở hữu đội ngũ nhân lực công nghệ cao, Selex làm chủ toàn bộ quá trình nghiên cứu, phát triển sản phẩm'),
    ('product', 'Với nhà máy riêng, Selex làm chủ sản xuất hàng loạt xe máy điện, pin, trạm đổi pin,')
]:
    from startup_tool import normal
    if normal(quote) not in normal(source_text):
        raise ValueError(f'Selex {kind} quote requires source review')
    evidence.append(dict(id=f'E_SELEX_{kind}',company_id='S001',kind=kind,quote=quote,
        url=source['url'],snapshot=source['snapshot'],sha256=source['sha256'],publisher_owner='Selex',
        retrieved_at=source['fetched_at'],reviewed=True,reviewer='Codex: company R&D and manufacturing page'))
selex['physical']='yes'

def selex_fact(kind, source_id, quote, **extra):
    row = manifest[source_id]
    from startup_tool import normal
    text = (DATA/row['snapshot']).read_text(encoding='utf-8')
    assert normal(quote) in normal(text), (kind, source_id)
    evidence.append(dict(id=f'E_SELEX_{kind}_{source_id}',company_id='S001',kind=kind,quote=quote,
        url=row['url'],snapshot=row['snapshot'],sha256=row['sha256'],publisher_owner=row['publisher_owner'],
        retrieved_at=row['fetched_at'],reviewed=True,reviewer='Codex: primary source and date review',**extra))

selex_fact('startup','selex_milestone','Doanh nghiệp startup Việt đạt được công nhận về năng lực trí tuệ')
selex_fact('activity','selex_milestone','Đến nay Selex đã phủ sóng 120 trạm đổi pin, chạm mốc 1 triệu lượt đổi pin phục vụ khách hàng',
    event_date='2025-11-13',origin_id='selex_network_operating_2025',event_date_basis='publication date of present-tense operation claim')
selex_fact('activity','petrolimex_selex_2026','Tập đoàn Xăng dầu Việt Nam (Petrolimex) phối hợp cùng Xuân Cầu Holdings và Selex Motors tổ chức Lễ công bố thành lập Công ty Cổ phần (CTCP) Hạ tầng Năng lượng Xanh Việt Nam.',
    event_date='2026-05-06',origin_id='vgx_joint_venture_launch_2026')
tax = next(e for e in evidence if e['id']=='E_TAX_SELEX')
evidence.append(dict(tax,id='E_SELEX_COUNTER',kind='counter_review',
    search_queries=['Selex Motors 2026 ngừng giải thể','Selex Motors 2026 startup'],
    review_note='Reviewed search results and recent tax table; no verified closure report found in opened material. Search coverage is limited; absence of a result does not prove absence of closure.'))

with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer = csv.DictWriter(handle,fieldnames=list(candidates[0]))
    writer.writeheader()
    writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
print(json.dumps({'candidates':len(candidates),'evidence':len(evidence),'official_tax_checks':1}))
