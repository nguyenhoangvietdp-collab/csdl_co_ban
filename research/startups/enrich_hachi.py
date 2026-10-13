"""Complete the Hachi dossier with browser-read government and dated project evidence."""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from startup_tool import normal
DATA=ROOT/'data/startups'
mp=DATA/'source_manifest.json'
manifest={r['id']:r for r in json.loads(mp.read_text())}
with (DATA/'candidates.csv').open(encoding='utf-8-sig',newline='') as handle:
    candidates=list(csv.DictReader(handle))
hachi=next(c for c in candidates if c['brand']=='Hachi')
evidence=[json.loads(line) for line in (DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]

snapshot='sources/hachi_natif_browser.txt'
text=(DATA/snapshot).read_text(encoding='utf-8')
manifest['hachi_natif_2026'].update(status='fetched_browser_excerpt',snapshot=snapshot,
    sha256=hashlib.sha256(text.encode()).hexdigest(),fetched_at='2026-10-13',
    note='HTTP fetch failed, then visible browser DOM excerpt and article date were read directly.')
manifest['hachi_app']['publisher_owner']='Hachi'
manifest['hachi_app']['platform_operator']='Google Play'
for e in evidence:
    if e.get('company_id')==hachi['id'] and e.get('kind')=='activity' and 'play.google.com' in e.get('url',''):
        e['publisher_owner']='Hachi'
        e['platform_operator']='Google Play'


def add(kind, source, quote, **extra):
    r=manifest[source]
    assert normal(quote) in normal((DATA/r['snapshot']).read_text(encoding='utf-8'))
    record=dict(id=f'E_{source}_{kind}_{hachi["id"]}',company_id=hachi['id'],kind=kind,quote=quote,
        url=r['url'],snapshot=r['snapshot'],sha256=r['sha256'],publisher_owner=r['publisher_owner'],
        retrieved_at=r['fetched_at'],reviewed=True,reviewer='Codex: read source, dates and ownership',**extra)
    old=next((e for e in evidence if e['id']==record['id']),None)
    if old: evidence[evidence.index(old)]=record
    else: evidence.append(record)

add('discovery','hachi_natif_2026','Ở lĩnh vực nông nghiệp đô thị, Hachi là ví dụ tiêu biểu cho sức mạnh của khoa học công nghệ trong đời sống.',
    source_type='government',published_at='2026-01-13',method='browser_dom_excerpt')
add('startup','hachi_natif_2026','Startup này nghiên cứu ra dung dịch dinh dưỡng thay đất để trồng rau bằng nước',method='browser_dom_excerpt')
add('product','hachi_natif_2026','tạo ra thiết bị trồng rau thông minh phù hợp với hộ gia đình.',method='browser_dom_excerpt')
add('activity','hachi_natif_2026','Đổi mới mô hình kinh doanh, Hachi “bán công nghệ, không bán rau”, cho thuê hệ thống, cung cấp giống và dinh dưỡng cho hàng chục nghìn hộ gia đình.',
    event_date='2026-01-13',origin_id='hachi_rental_service_model_natif_2026',method='browser_dom_excerpt',
    event_date_basis='Publication date of present-tense service model; not a field inspection date.',
    caveat='Government communication describes the model; customer count is not independently audited.')
add('activity','hachi_project_2026','hoàn thiện vào tháng 6/2026',event_date='2026-06',date_precision='month',
    origin_id='hachi_toan_hung_yen_1000m2_project_2026',
    caveat='Company-authored project completion report. Exact completion day and customer-side confirmation not established.')
hachi.update(physical='yes',notes='Tax active; government recognition and described smart hydroponic product; current project and app update. Recent activity includes party-authored project and government-described service model; no independently audited customer count.')
with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
mp.write_text(json.dumps(list(manifest.values()),ensure_ascii=False,indent=2),encoding='utf-8')
portable=[{k:r[k] for k in ('id','source_type','publisher_owner','url')} for r in manifest.values()]
(ROOT/'startup_sources.json').write_text(json.dumps(portable,ensure_ascii=False,indent=2),encoding='utf-8')
print('Hachi evidence appended; developer app content attributed to Hachi, not Google.')
