"""Capture updated OpenMind product claims; retain the unresolved tax gate."""
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from startup_tool import validate_evidence

DATA = ROOT / 'data/startups'
manifest = {s['id']: s for s in json.loads((DATA / 'source_manifest.json').read_text(encoding='utf-8'))}
evidence = [json.loads(s) for s in (DATA / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if s]
for kind, source, quote, caveat in [
    ('technology', 'openmind_company_20261020', 'Three tightly integrated layers (perception, simulation and control)',
     'Supplier describes OM-Eye/OM-Twin/OM-Brain. ISO23247/OPCUA mention is architecture claim, not certification, interoperability or safety verification.'),
    ('product', 'openmind_company_20261020', 'Mobile Unloading & Palletizing',
     'Robot application offering; retain hybrid integration classification, not proof manufacturing complete robot arms or production throughput.'),
    ('counter_review', 'openmind_kuka_202610', 'Partnership · October 2026',
     'Own news reports technical exchange with KUKA, month only; not signed partnership, purchase order, KUKA endorsement or independent second owner. No exact day inferred.')]:
    s = manifest[source]
    e = dict(id=f'E_{source}_{kind}_S057', company_id='S057', kind=kind, quote=quote,
        url=s['url'], snapshot=s['snapshot'], sha256=s['sha256'], publisher_owner=s['publisher_owner'],
        retrieved_at='2026-10-20', reviewed=True, reviewer='Codex: refreshed vendor claims, legal/date/safety scope retained', caveat=caveat)
    if kind == 'counter_review':
        e.update(search_queries=['OpenMind Robotics mã số thuế'],
            review_note='No current official tax result from three CAPTCHA submissions; not evidence of shutdown or nonexistent MST. '+caveat)
    assert not validate_evidence(e, date(2026, 10, 20), DATA)
    old = next((x for x in evidence if x['id'] == e['id']), None)
    if old:
        evidence[evidence.index(old)] = e
    else:
        evidence.append(e)
with (DATA / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    candidates = list(csv.DictReader(handle))
c = next(c for c in candidates if c['id'] == 'S057')
addition = (' Refresh20Oct2026: OM-Eye/OM-Twin/OM-Brain vendor architecture and robot application offer; no ISO23247 certification/safety validation inferred. '
    'OwnKUKAtechnicalexchangeOctober2026 monthonly, not signedcontract/endorsement or independent publisher. '
    'Three CAPTCHA submissions for candidate3703462444 rejected, no officialtable; user handoff pending. Tax gate remains open, no shutdown inference.')
if addition not in c['notes']:
    c['notes'] += addition
with (DATA / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(candidates[0]))
    writer.writeheader()
    writer.writerows(candidates)
(DATA / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
(ROOT / 'startup_sources.json').write_text(json.dumps([{k: s[k] for k in ('id', 'source_type', 'publisher_owner', 'url')} for s in manifest.values()], ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded3 updated OpenMind claims; no official tax result.')

