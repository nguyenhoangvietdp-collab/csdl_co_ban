"""Corroborate ENFARM using the original public award, without claiming contract completion."""
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
snapshot='sources/enfarm_procurement_IB2600287567.txt'
text=(DATA/snapshot).read_text(encoding='utf-8')
url=text.splitlines()[0].removeprefix('Source: ')
evidence=[json.loads(line) for line in (DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]
for kind,quote,extra in [
    ('identity','0317604360\tCÔNG TY TNHH CÔNG NGHỆ NÔNG NGHIỆP ENFARM',{}),
    ('activity','1\tvn0317604360\t0317604360\tCÔNG TY TNHH CÔNG NGHỆ NÔNG NGHIỆP ENFARM',{}),
]:
    if kind=='activity':
        quote='1\tvn0317604360\t0317604360\tCÔNG TY TNHH CÔNG NGHỆ NÔNG NGHIỆP ENFARM\t349.200.000'
        extra=dict(event_date='2026-06-12',origin_id='enfarm_cefd_award_IB2600287567_20260612',
            event_date_basis='Approval date 12/06/2026; published 15/06/2026. Award, not signed contract or acceptance.',
            caveat='Public procurement result confirms awarded supplier and goods; no installation/acceptance certificate reviewed.')
    r=dict(id=f'E_enfarm_procurement_{kind}_S004',company_id='S004',kind=kind,quote=quote,
        url=url,snapshot=snapshot,sha256=hashlib.sha256(text.encode()).hexdigest(),
        publisher_owner='Trung tâm Động lực học Thủy khí Môi trường',platform_operator='Hệ thống mạng đấu thầu quốc gia',
        source_type='government',retrieved_at='2026-10-13',reviewed=True,
        reviewer='Codex: direct visible procurement detail and exact winning tax ID',method='browser_dom_excerpt',**extra)
    assert normal(quote) in normal(text)
    assert not validate_evidence(r,date(2026,10,13),DATA)
    old=next((e for e in evidence if e['id']==r['id']),None)
    if old: evidence[evidence.index(old)]=r
    else: evidence.append(r)
for e in evidence:
    if e['id']=='E_enfarm_deployment_2026_activity_S004':
        e.update(reviewed=False,reviewer='Withheld: company-site integrity anomaly; use original award instead')
    if e['id']=='E_enfarm_company_source_integrity_flag_S004':
        e.update(resolution='Screening claims corroborated using exact-entity official award and independent DPM handover; company deployment claim withheld. Website anomaly cause remains unknown and is not declared repaired.',
            resolution_evidence_ids=['E_enfarm_procurement_activity_S004','E_enfarm_procurement_identity_S004','E_enfarm_dpm_2025_activity_S004'])
with (DATA/'candidates.csv').open(encoding='utf-8-sig',newline='') as handle:
    candidates=list(csv.DictReader(handle))
next(c for c in candidates if c['id']=='S004')['notes']='Official tax active; DPM handover and original CEFD procurement award are distinct external activity evidence. Award does not prove completion. Company deployment claim withheld due website anomaly; no website repair inferred. Official goods list names CWT China for sensor S7 and Dien Quang Vietnam for gateways/nodes; do not claim all hardware manufactured in-house.'
with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
mp=DATA/'source_manifest.json'
manifest={r['id']:r for r in json.loads(mp.read_text(encoding='utf-8'))}
manifest['enfarm_procurement']=dict(id='enfarm_procurement',source_type='government',publisher_owner='Trung tâm Động lực học Thủy khí Môi trường',
    platform_operator='Hệ thống mạng đấu thầu quốc gia',url=url,status='fetched_browser_excerpt',snapshot=snapshot,
    sha256=hashlib.sha256(text.encode()).hexdigest(),fetched_at='2026-10-13',note='Direct browser original record, not the commercial mirror.')
mp.write_text(json.dumps(list(manifest.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'startup_sources.json').write_text(json.dumps([{k:r[k] for k in ('id','source_type','publisher_owner','url')} for r in manifest.values()],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'evidence_records':len(evidence),'enfarm_company_deployment_withheld':True}))
