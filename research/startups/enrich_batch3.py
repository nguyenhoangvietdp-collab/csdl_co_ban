"""Append primary-source leads and Hachi evidence without marking missing gates complete."""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from startup_tool import normal

DATA=ROOT/'data/startups'
manifest={r['id']:r for r in json.loads((DATA/'source_manifest.json').read_text())}
with (DATA/'candidates.csv').open(encoding='utf-8-sig',newline='') as handle:
    candidates=list(csv.DictReader(handle))
evidence=[json.loads(line) for line in (DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]


def find_or_add(brand,source):
    c=next((c for c in candidates if normal(c['brand'])==normal(brand)),None)
    if c:
        return c
    c=dict.fromkeys(candidates[0],'')
    c.update(id=f'S{max(int(c["id"][1:]) for c in candidates)+1:03}',brand=brand,
        discovery_url=manifest[source]['url'],notes='Primary-source lead only; not yet approved.')
    candidates.append(c)
    return c


def add(c,kind,source,quote,**extra):
    r=manifest[source]
    text=(DATA/r['snapshot']).read_text(encoding='utf-8')
    assert normal(quote) in normal(text),(c['brand'],source,'quote mismatch')
    record=dict(id=f'E_{source}_{kind}_{c["id"]}',company_id=c['id'],kind=kind,quote=quote,
        url=r['url'],snapshot=r['snapshot'],sha256=r['sha256'],publisher_owner=r['publisher_owner'],
        retrieved_at=r['fetched_at'],reviewed=True,reviewer='Codex: source read and scope checked',**extra)
    old=next((e for e in evidence if e['id']==record['id']),None)
    if old: evidence[evidence.index(old)]=record
    else: evidence.append(record)


# Program date is not silently converted into a publication date.
for brand,title in [
    ('EM&AI','Công ty Cổ phần EM&AI'), ('UCTalent','UCTalent'),
    ('FASTDO','FASTDO: Phần mềm quản lý công việc tích hợp với công nghệ AI (trí tuệ nhân tạo)'),
    ('Augmented Hype','Augmented Hype'),
    ('Run Together','Công Ty Cổ Phần Công Nghệ Thể Thao Run Together'),
    ('DDC Holdings','DDC Holdings'), ('Kaas.finance','Kaas.finance - Stablecoin solution & APIs platform'),
    ('Skoolib','Skoolib'), ('Plen.ai','Plen.ai'), ('PatSense','PatSense, Inc'),
    ('Ohhi.vn','Ohhi.vn'), ('AquaX / ST Software','ST SOFTWARE JOIN STOCK COMPANY'),
    ('Olinno Technology','Olinno Technology Ltd'), ('HanaGold','Trung Tâm Vàng Bạc Đá Quý HanaGold')
]:
    c=find_or_add(brand,'davas_2025')
    add(c,'discovery','davas_2025',title,source_type='government',published_at='',
        event_date='2025-05-29',date_note='Official event date; webpage publication date unverified. Not sufficient for dated publication gate.')

for brand,quote in [
    ('Growlab','Growlab, a biotech startup with patented tissue culture technology, wins the championship prize'),
    ('Biglead','The third prize of $20,000 went to Biglead, a solution by IDO E-commerce'),
    ('Dayladau','Dayladau, selected by investors for growth potential'),
    ('Plantner','Plantner, recognized for converting agricultural waste into organic fertilizer')
]:
    c=find_or_add(brand,'techfest_final_hanoi_2025')
    add(c,'discovery','techfest_final_hanoi_2025',quote,source_type='government',published_at='2025-12-12',
        caveat='Publication includes international contestants; Vietnam tax registration unverified. Award amount/patent grant not independently validated.')

hachi=next(c for c in candidates if c['brand']=='Hachi')
add(hachi,'technology','hachi_research','Nghiên cứu thành công hệ thống IoT kiểm soát và điều khiển tự động, tối ưu hóa quy trình trồng rau thủy canh')
add(hachi,'product','hachi_research','Nghiên cứu thành công hệ thống IoT kiểm soát và điều khiển tự động, tối ưu hóa quy trình trồng rau thủy canh',
    caveat='Historical 2016 R&D result. Current deployment and current physical product availability still require recent corroboration.')
add(hachi,'startup','hachi_startup_2025','Từ góc độ của một doanh nghiệp khởi nghiệp, ông Đặng Xuân Trường, Giám đốc Công ty cổ phần Công nghệ cao Hachi Việt Nam')
add(hachi,'activity','hachi_app','Lần cập nhật gần đây nhất\n18 thg 1, 2026',event_date='2026-01-18',
    origin_id='hachi_one_app_update_2026',publisher_note='Developer-authored listing; Google distribution metadata does not make this an independent editorial confirmation.',
    caveat='App listing states IoT connection is in development; do not present it as a shipped feature.')
tax=next(e for e in evidence if e['id']=='E_TAX_HACHI')
record=dict(tax,id='E_HACHI_COUNTER',kind='counter_review',
    search_queries=['Hachi 2026 giải thể ngừng','Hachi 2025 triển khai trang trại'],
    review_note='Tax status active; searched closure and operations. Multiple unrelated Hachi/Hachi Hachi businesses appeared and were not attached to this legal entity. No verified closure in opened material; coverage limited.')
old=next((e for e in evidence if e['id']==record['id']),None)
if old: evidence[evidence.index(old)]=record
else: evidence.append(record)
hachi['notes']='Official tax active. R&D and app update found; missing recent fund/government/contest publication and a second independent recent activity origin. Physical classification awaits current product evidence.'

with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
print(json.dumps({'candidates':len(candidates),'evidence':len(evidence),'official_tax_checks':sum(e['kind']=='tax' for e in evidence)}))
