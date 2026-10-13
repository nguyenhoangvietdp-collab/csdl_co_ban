"""Append reviewed dossier evidence; preserve unverified tax IDs and source caveats."""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from startup_tool import normal, validate_evidence
from datetime import date

DATA = ROOT / 'data/startups'
manifest_path = DATA / 'source_manifest.json'
manifest = {r['id']: r for r in json.loads(manifest_path.read_text(encoding='utf-8'))}
evidence = [json.loads(line) for line in (DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]
with (DATA/'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))

for key, url, owner, source_type in [
    ('p4g_jan2026', 'https://p4gpartnerships.org/sites/default/files/2026-01/P4G_Startup_Portfolio_Jan26.pdf', 'P4G / WRI', 'fund'),
    ('vulcan_vista_2025', 'https://vista.gov.vn/vn-uploads/startup/2025/44-2025/startup-44.2025.pdf', 'Cục Thông tin, Thống kê / Bộ KH&CN', 'government')]:
    snapshot = f'sources/{key}.txt'
    manifest[key] = dict(id=key,url=url,publisher_owner=owner,source_type=source_type,
        status='fetched_pdf',snapshot=snapshot,sha256=hashlib.sha256((DATA/snapshot).read_text(encoding='utf-8').encode()).hexdigest(),
        fetched_at='2026-10-13',pdf_file=f'sources/{key}.pdf',
        pdf_sha256=hashlib.sha256((DATA/f'sources/{key}.pdf').read_bytes()).hexdigest())

def add(company, kind, source, quote, **extra):
    r = manifest[source]
    record = dict(id=f'E_{source}_{kind}_{company}',company_id=company,kind=kind,quote=quote,
        url=r['url'],snapshot=r['snapshot'],sha256=r['sha256'],publisher_owner=r['publisher_owner'],
        retrieved_at=r['fetched_at'],reviewed=True,reviewer='Codex: read primary text and relevant PDF pages',**extra)
    if r.get('pdf_file'):
        record.update(method='pdf_embedded_text',pdf_file=r['pdf_file'],pdf_sha256=r['pdf_sha256'])
    assert normal(quote) in normal((DATA/r['snapshot']).read_text(encoding='utf-8'))
    assert not validate_evidence(record,date(2026,10,13),DATA)
    old = next((e for e in evidence if e['id']==record['id']),None)
    if old: evidence[evidence.index(old)] = record
    else: evidence.append(record)

enfarm = next(c for c in candidates if c['id']=='S004')
enfarm.update(legal_name='Công ty TNHH Công nghệ nông nghiệp enfarm',country='VN',physical='yes',website='https://enfarm.com/')
add('S004','identity','enfarm_company','Công ty TNHH Công nghệ nông nghiệp enfarm')
add('S004','startup','p4g_jan2026','The startup’s AI-powered device provides real-time, lab-precision soil nutrient analysis and actionable recommendations,',page=20,
    caveat='Portfolio describes the company as a startup; no independent accuracy certification reviewed.')
add('S004','product','enfarm_dpm_2025','Enfarm cung cấp cho Phú Mỹ thiết bị đo dinh dưỡng đất thông minh Enfarm F cùng API tích hợp công nghệ Enfarm vào App Phú Mỹ')
add('S004','technology','enfarm_dpm_2025','Thiết bị Enfarm F ứng dụng công nghệ IoT tiên tiến, có khả năng đo nhanh 7 chỉ tiêu dinh dưỡng và môi trường đất gồm: Nitơ (N), Lân (P), Kali (K), pH, EC, độ ẩm và nhiệt độ.',
    caveat='Partner-described technical capability; performance percentages and ISO equivalence not independently verified.')
add('S004','activity','enfarm_dpm_2025','Giai đoạn đầu, hai bên đã bàn giao 50 bộ thiết bị đo dinh dưỡng đất thông minh Enfarm F, nằm trong tổng số 100 thiết bị của chương trình hợp tác.',
    event_date='2025-10-27',origin_id='enfarm_phumy_50_devices_handover_20251027',
    event_date_basis='DPM states 27/10; matching Enfarm event article explicitly states 27/10/2025.',
    date_source_url=manifest['enfarm_phumy_date']['url'],date_source_snapshot=manifest['enfarm_phumy_date']['snapshot'],
    caveat='Partner-authored handover report, not an independent deployment audit.')
add('S004','activity','enfarm_deployment_2026','Hệ thống được triển khai tại các vùng trồng vải thuộc xã Phúc Hòa và phường Phượng Sơn, gồm 80 cảm biến đất, 80 trạm cảm biến enfarm F+, 50 cổng dữ liệu enfarm F+, hệ thống điều khiển và truyền dữ liệu.',
    event_date='2026-06-30',origin_id='enfarm_bacninh_lychee_iot_project_2026',
    event_date_basis='Publication date of completed/present deployment claim, exact commissioning day not given.',
    caveat='Company report. Unrelated gambling posts present on the same website; project needs client-side corroboration.')
add('S004','technology','enfarm_hardware_2026','Để Type-C có thể đảm nhiệm đồng thời chức năng cấp nguồn và giao tiếp với cảm biến, phần cứng bên trong thiết bị cũng được điều chỉnh phù hợp với thiết kế mới.',
    caveat='Company-described hardware redesign; not proof that every sensor component was developed in-house.')
add('S004','source_integrity_flag','enfarm_company','1win App for Android Bonus Guide',
    review_note='Unrelated gambling articles observed. Cause unknown; do not infer closure or compromise. Client corroboration needed before relying on deployment claims.')
add('S004','counter_review','enfarm_dpm_2025','Giai đoạn đầu, hai bên đã bàn giao 50 bộ thiết bị đo dinh dưỡng đất thông minh Enfarm F',
    search_queries=['Enfarm ngừng hoạt động giải thể','Enfarm closed ceased operations 2026'],
    review_note='No verified closure found in opened relevant primary sources. Site integrity anomaly flagged separately. Tax CAPTCHA failure is not inactivity evidence.')
enfarm['notes']='User confirms active. Candidate MST 0317604360 remains unverified officially. Physical soil sensing hardware supported by DPM handover; company deployment needs client corroboration because unrelated gambling articles are present. No independently checked lab accuracy or revenue.'

vulcan = next(c for c in candidates if c['id']=='S016')
vulcan.update(legal_name='Công ty TNHH Doanh Nghiệp Xã Hội Vulcan',country='VN',physical='yes',website='https://www.wearevulcan.com/')
text = (DATA/manifest['vulcan_identity']['snapshot']).read_text(encoding='utf-8')
start = text.rfind('Vulcan Augmetics là doanh nghiệp')
end = text.find('Công ty TNHH Doanh Nghiệp Xã Hội Vulcan',start)+len('Công ty TNHH Doanh Nghiệp Xã Hội Vulcan')
assert start>=0 and end>start
add('S016','identity','vulcan_identity',text[start:end],caveat='Vietnamese footer names VN company; newer English site names Singapore Pte. VN operational responsibility must be checked separately.')
add('S016','discovery','vulcan_vista_2025','Vulcan Augmetics - một startup công nghệ y - sinh',
    source_type='government',published_at='2025',date_precision='year',page=10,
    caveat='2025 issue cover; exact publication day unknown. Article recounts historical events and must not date them to 2025.')
add('S016','startup','vulcan_vista_2025','Vulcan Augmetics - một startup công nghệ y - sinh',page=10)
add('S016','product','vulcan_vista_2025','phát triển các chi giả thông minh điều khiển bằng tín hiệu cơ (myoelectric).',page=10)
add('S016','technology','vulcan_vista_2025','phần điện, chip là nhóm tự thiết kế nhưng 70% là outsource từ đối tác gia công bên ngoài, sau đó Vulcan lắp ráp và QC, đóng gói thành phẩm.',page=13,
    caveat='Historical interview reproduced in 2025 issue. Outsourced fabrication; not evidence of current own manufacturing capacity.')
add('S016','activity','vulcan_app','Updated on\nSep 11, 2026',event_date='2026-09-11',origin_id='vulcan_mobile_app_update_20260911',platform_operator='Google Play',
    caveat='Developer-published update, not independent proof of clinical deployment or active tax status.')
add('S016','counter_review','vulcan_about','VULCAN AUGMETICS PTE. LTD (202133119C)',
    search_queries=['Vulcan Augmetics ngừng hoạt động giải thể','Vulcan Augmetics closed ceased operations'],
    review_note='No verified closure located in opened relevant sources; other Vulcan brands are unrelated. Current site uses Singapore parent; VN legal and operating roles need separate confirmation.')
vulcan['notes']='Candidate MST0315155575 from secondary lead only; official portal rejected CAPTCHA attempts, no tax result saved. Vietnam footer maps legal company; global claims often name Singapore parent. One dated recent app update; need another publisher/activity origin. Historical government profile not current operational proof.'

with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
manifest_path.write_text(json.dumps(list(manifest.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'startup_sources.json').write_text(json.dumps([{k:r[k] for k in ('id','source_type','publisher_owner','url')} for r in manifest.values()],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'evidence_records':len(evidence),'official_tax_added':0}))
