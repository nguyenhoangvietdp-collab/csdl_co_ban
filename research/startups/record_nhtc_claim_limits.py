"""Retain company disclosure limits from web-reader excerpts, not a full HTTP snapshot."""
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
snapshot = 'sources/nhtc_linkedin_web_excerpts_20261020.txt'
text = ('Excerpts returned by web reader20Oct2026 from company LinkedIn profile; HTTP fetch failed and browser connection refused. Not a complete profile snapshot.\n'
    'Founded\n2011\n'
    'Some demo scenes use AI-generated visuals to illustrate system capabilities and future Physical AI concepts. Autonomous UAV/robot deployments are subject to applicable regulations.\n'
    'SELF-CALIBRATING INDOOR POSITIONING SYSTEM AND METHOD (Patent Application No. 1-2026-06996)\n')
(D / snapshot).write_text(text, encoding='utf-8')
es = [json.loads(l) for l in (D / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if l]
for key, quote, caveat in [
    ('demo', 'Some demo scenes use AI-generated visuals',
     'Own disclosure: some demo visuals are AI-generated concepts. Not evidence installed robot/UAV/palm-payment system or customer deployment. Existing hardware documents remain separate evidence.'),
    ('patent', 'Patent Application No. 1-2026-06996',
     'Company-reported application, not granted patent, validated applicant/ownership or enforceable scope. Exact-number search found own company/person posts; no official grant record opened.'),
    ('stage', 'Founded\n2011',
     'Self-described founding2011; QVICshortlist alone not proof startup/scaleup stage. No age cutoff invented; stage remains unresolved. Relative1w/2w/3w post ages not converted to event dates.')]:
    e = dict(id=f'E_NHTC_{key.upper()}_LIMIT_20261020', company_id='S028', kind='counter_review', quote=quote,
        url='https://www.linkedin.com/company/nhatrang-hitech-company-ltd', publisher_owner='Nha Trang Hitech',
        snapshot=snapshot, sha256=hashlib.sha256(text.encode()).hexdigest(), method='web_text_excerpt', retrieved_at='2026-10-20',
        reviewed=True, reviewer='Codex: source opened in web reader; exact excerpt and limitations retained',
        search_queries=['Nha Trang Hitech 2026', '1-2026-06996', 'Nha Trang Hitech startup 2026'],
        review_note=caveat, caveat='Partial web-reader excerpt only; not a fresh complete HTTP or browser capture. '+caveat)
    assert not validate_evidence(e, date(2026, 10, 20), D)
    old = next((x for x in es if x['id'] == e['id']), None)
    if old:
        es[es.index(old)] = e
    else:
        es.append(e)
(D / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in es) + '\n', encoding='utf-8')
with (D / 'candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
    cs = list(csv.DictReader(handle))
c = next(x for x in cs if x['id'] == 'S028')
addition = (' Review20Oct2026: ownLinkedIn discloses some AI-generated demo visuals, not actualdeploymentproof. '
    'Selfreportedpatentapplication1-2026-06996 notgrant/ownershipverified. ProfileFounded2011notstartupstage; noagecutoffinvented. '
    'Relativepostagesnotdatedactivity; partialwebreaderexcerpts stored becauseHTTP/browserfailed. Existinghardwaredocs separate, tax/stage/secondowner remainpending.')
if addition not in c['notes']:
    c['notes'] += addition
with (D / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    w = csv.DictWriter(handle, fieldnames=list(cs[0]))
    w.writeheader()
    w.writerows(cs)
print('Recorded3 NHTC claim limits, no new activity or tax approval.')
