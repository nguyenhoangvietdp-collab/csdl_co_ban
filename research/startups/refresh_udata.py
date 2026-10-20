"""Record Udata product evidence without choosing between unverified tax IDs."""
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
quote = 'Nền tảng thu thập, giám sát và phân tích dữ liệu - Uboard\ncủa Công ty Cổ phần Udata'
snapshot = D / 'sources/udata_certificate_browser_20261020.txt'
snapshot.write_text(quote + '\nSao Khuê 2025\nTranscribed from certificate image hosted on Udata website. No tax identifier visible.\n', encoding='utf-8')
image = D / 'sources/udata_certificate_browser_20261020.png'
evidence = [json.loads(s) for s in (D / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if s]
certificate = dict(id='E_UDATA_CERTIFICATE_20261020', company_id='S031', kind='identity', quote=quote,
    url='https://udata.ai/image/about_us/award-cert.webp', publisher_owner='UDATA hosting VINASA certificate image',
    snapshot=str(snapshot.relative_to(D)).replace('\\', '/'), sha256=hashlib.sha256(snapshot.read_text(encoding='utf-8').encode()).hexdigest(),
    method='image_transcription', image_file=str(image.relative_to(D)).replace('\\', '/'), image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
    retrieved_at='2026-10-20', reviewed=True, reviewer='Codex: certificate image visually read from company website',
    caveat='Browser screenshot of company-hosted certificate image, not independently checked with VINASA. Uboard/company name supported; no MST visible, no tax-ID selection or recent-event date inferred from2025.')
new = [certificate]
s = manifest['udata_home_20261020']
for kind, quote, caveat in [
    ('product', 'Central AI layer connecting and analyzing enterprise operational data',
     'Current Ugate software description. Does not establish gateway hardware manufacturing, finance returns, secure processing or independent benchmark.'),
    ('counter_review', 'Enterprise standards for\nsecure data, financial visibility',
     'ISO27001/50001, TCFD/COP28 and customer logos are webpage claims/icons, not audited certificates, compliance or deployments. Zero-initialized counters not actual zero customers, savings or uptime.')]:
    e = dict(id=f'E_udata_home_20261020_{kind}_S031', company_id='S031', kind=kind, quote=quote,
        url=s['url'], publisher_owner=s['publisher_owner'], snapshot=s['snapshot'], sha256=s['sha256'],
        retrieved_at='2026-10-20', reviewed=True, reviewer='Codex: current product and claim scope read', caveat=caveat)
    if kind == 'counter_review':
        e.update(search_queries=['UDATA mã số thuế Đà Nẵng', '0110902473', 'site:udata.ai 0110848057 OR 0110902473'],
            review_note='Two identifiers remain unverified: TVPLlead0110848057 and VNBIS/CVWork0110902473. Own homepage/about and saved19pagecredential text lack taxID. Same name/address not proof of rename or valid current ID. VNBIS HTTPfailed; web page read as lead only. '+caveat)
    new.append(e)
for e in new:
    errors = validate_evidence(e, date(2026, 10, 20), D)
    assert not errors, (e['id'], errors)
    old = next((x for x in evidence if x['id'] == e['id']), None)
    if old:
        evidence[evidence.index(old)] = e
    else:
        evidence.append(e)
with (D / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    cs = list(csv.DictReader(handle))
c = next(x for x in cs if x['id'] == 'S031')
addition = (' Review20Oct2026: company-hosted SaoKhuecertificate names Uboard/CongtyCophanUdata but noMST. '
    'Both0110848057TVPLlead and0110902473VNBIS/CVWork remain unverified; ownhomepage/about/credentialtext noID. '
    'CurrentUgateAIsoftware context doesnotreplace priorgatewaycatalogue; ISO/TCFD/COP28icons and zero-initializedcounters notverifiedcertification/performance. '
    'GDT0110848057 prepared, CAPTCHApermission pending; no submission/result yet.')
if addition not in c['notes']:
    c['notes'] += addition
with (D / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    w = csv.DictWriter(handle, fieldnames=list(cs[0]))
    w.writeheader()
    w.writerows(cs)
(D / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: s[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for s in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded3 UDATA records; tax identifier remains unresolved.')
