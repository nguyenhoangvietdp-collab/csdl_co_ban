"""Append reviewed source leads; preserve existing evidence and tax results."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/startups'
manifest={r['id']:r for r in json.loads((DATA/'source_manifest.json').read_text())}
with (DATA/'candidates.csv').open(encoding='utf-8-sig',newline='') as handle:
    candidates=list(csv.DictReader(handle))
evidence=[json.loads(line) for line in (DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]


def candidate(brand, url):
    existing=next((c for c in candidates if c['brand']==brand), None)
    if existing:
        return existing
    row=dict.fromkeys(candidates[0], '')
    row.update(id=f'S{max(int(c["id"][1:]) for c in candidates)+1:03}',brand=brand,discovery_url=url,
               notes='Research lead only. Legal entity, tax and current operations still require verification.')
    candidates.append(row)
    return row


def add(record):
    old=next((e for e in evidence if e['id']==record['id']), None)
    if old:
        evidence[evidence.index(old)]=record
    else:
        evidence.append(record)


boards=[
    ('qvic2026_companies_1.jpeg',[
        ('AIZ','Comprehensive AI enterprise platform for unified data, digital workforce, and intelligent process automation'),
        ('ANTAJA','QLINX — A verifiable blockchain-passport platform enabling the low-altitude economy with cm-level RTK and ultra-reliable connectivity'),
        ('BRAIN-LIFE','AI-powered neurotech wearables that enhance focus, cognition, and mental resilience'),
        ('FILLSONIC','Adaptive multi-speaker audio that preserves signal integrity and coordinates roles at the edge'),
        ('FINIZI.AI','An AI-driven financial and accounting platform that automates tax compliance and financial management'),
        ('FIZIBBOX','Proactive visual fire sensors powered by Edge AI & VLM'),
        ('FUTURE SPACE TECHNOLOGY','OmniEye is vision module providing drones with spatial awareness and safe navigation'),
        ('HEALTHBRIDGE AI','Smarter care, less paperwork - built by doctors, for doctors'),
        ('HITEK','Swarm drone technology for diverse use cases')]),
    ('qvic2026_companies_2.jpeg',[
        ('MEDCAT','MedCAT IDUS - A Vietnamese sovereign AI platform using in-house VLM to turn unstructured documents into trusted structured data'),
        ('NAISCORP ROBOTICS','Edge-AI home companion robot for global senior care'),
        ('NHA TRANG HITECH','Intelligent cold chain management - from factory to consumer'),
        ('OLOGN TECHNOLOGY','NAWI - Universal AR intelligence for industrial and emergency safety'),
        ('TENSOR','Powering sustainable poultry with AI in-ovo sexing solution'),
        ('UDATA','AI-driven technical support, troubleshooting and operational intelligence'),
        ('VEEP','A cloud-based AIoT-powered energy management solution to cut down 30% of building energy waste'),
        ('VIZION','AI-powered smart retail solution for stores & warehouses'),
        ('VOLTERRA','Full-stack software-as-a-service solutions for EV charging infrastructure'),
        ('VORIA SOLUTION','A secure & advanced AIoT platform for remote patient monitoring and telehealth')])]

source=manifest['qvic_presswire_2026']
for image_name, entities in boards:
    image=DATA/image_name
    transcript='QVIC 2026 Shortlisted Startups\n'+'\n\n'.join(brand+'\n'+description for brand,description in entities)
    snapshot='sources/'+image.stem+'_transcription.txt'
    (DATA/snapshot).write_text(transcript,encoding='utf-8')
    for brand, description in entities:
        c=candidate(brand,source['url'])
        add(dict(id=f'E_QVIC26_{c["id"]}',company_id=c['id'],kind='discovery',
            quote=brand+'\n'+description,url=source['url'],snapshot=snapshot,
            sha256=hashlib.sha256(transcript.encode()).hexdigest(),publisher_owner=source['publisher_owner'],
            retrieved_at=source['fetched_at'],published_at='2026-04-06',source_type='competition',
            reviewed=True,reviewer='Codex: manually read original shortlist image',method='image_transcription',
            image_file=image_name,image_sha256=hashlib.sha256(image.read_bytes()).hexdigest()))

source=manifest['datbike_jungle_2025']
c=candidate('Dat Bike',source['url'])
quote='The moment Dat Bike built for\nJuly 18, 2025\nJungle Insights'
text=(DATA/source['snapshot']).read_text(encoding='utf-8')
assert quote in text
add(dict(id='E_DATBIKE_DISCOVERY',company_id=c['id'],kind='discovery',quote=quote,url=source['url'],
    snapshot=source['snapshot'],sha256=source['sha256'],publisher_owner=source['publisher_owner'],
    retrieved_at=source['fetched_at'],published_at='2025-07-18',source_type='fund',reviewed=True,reviewer='Codex: opened fund article'))

hachi=next(c for c in candidates if c['brand']=='Hachi')
hachi.update(tax_id='0107578795',legal_name='CÔNG TY CỔ PHẦN CÔNG NGHỆ CAO HACHI VIỆT NAM',country='VN',website='https://hachi.com.vn/')
text=(DATA/'sources/hachi_tax.txt').read_text(encoding='utf-8')
add(dict(id='E_TAX_HACHI',company_id=hachi['id'],kind='tax',quote=text,
    url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp',snapshot='sources/hachi_tax.txt',
    sha256=hashlib.sha256(text.encode()).hexdigest(),publisher_owner='Vietnam Tax Authority',
    retrieved_at='2026-10-13',checked_at='2026-10-13',reviewed=True,reviewer='Codex: live result after user authorized Hachi lookup',
    tax_id=hachi['tax_id'],legal_name=hachi['legal_name'],status='NNT đang hoạt động'))
source=manifest['hachi_identity']
quote='CÔNG TY CỔ PHẦN CÔNG NGHỆ CAO HACHI VIỆT NAM'
assert quote in (DATA/source['snapshot']).read_text(encoding='utf-8')
add(dict(id='E_IDENTITY_HACHI',company_id=hachi['id'],kind='identity',quote=quote,url=source['url'],
    snapshot=source['snapshot'],sha256=source['sha256'],publisher_owner='Hachi',retrieved_at=source['fetched_at'],
    reviewed=True,reviewer='Codex: brand and legal name on company contact page'))

with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0]))
    writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
print(json.dumps({'candidates':len(candidates),'evidence':len(evidence),'official_tax_checks':sum(e['kind']=='tax' for e in evidence)}))
