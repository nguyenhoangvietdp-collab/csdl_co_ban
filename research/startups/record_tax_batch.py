"""Record exact reviewed parent rows from captured official tax tables."""
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from startup_tool import validate_evidence
DATA = ROOT/'data/startups'
with (DATA/'candidates.csv').open(encoding='utf-8-sig',newline='') as handle:
    candidates=list(csv.DictReader(handle))
evidence=[json.loads(line) for line in (DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines() if line]
for company_id,key,tax_id,legal_name in [
    ('S036','datbike','0401942142','CÔNG TY TNHH MTV DAT BIKE VIETNAM'),
    ('S008','alpha','0109810355','CÔNG TY TNHH ALPHA ASIMOV ROBOTICS'),
    ('S004','enfarm','0317604360','CÔNG TY TNHH CÔNG NGHỆ NÔNG NGHIỆP ENFARM'),
    ('S016','vulcan','0315155575','CÔNG TY TNHH DOANH NGHIỆP XÃ HỘI VULCAN')]:
    snapshot=f'sources/{key}_tax_{tax_id}.txt'
    text=(DATA/snapshot).read_text(encoding='utf-8')
    # Select the exact parent row, not a branch whose identifier begins with the same digits.
    lines=text.splitlines()
    i=next(i for i,line in enumerate(lines) if line.split('\t')[-1]==tax_id)
    quote='\n'.join(lines[i:i+3])
    r=dict(id=f'E_TAX_{key.upper()}',company_id=company_id,kind='tax',tax_id=tax_id,
        legal_name=legal_name,status='NNT đang hoạt động',quote=quote,snapshot=snapshot,
        sha256=hashlib.sha256(text.encode()).hexdigest(),url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp',
        publisher_owner='Cục Thuế',retrieved_at='2026-10-13',checked_at='2026-10-13',
        reviewed=True,reviewer='Codex: visible official table, exact parent row selected',row_scope='parent_company')
    assert not validate_evidence(r,date(2026,10,13),DATA)
    old=next((e for e in evidence if e['id']==r['id']),None)
    if old: evidence[evidence.index(old)]=r
    else: evidence.append(r)
    company=next(c for c in candidates if c['id']==company_id)
    company.update(tax_id=tax_id,legal_name=legal_name,country='VN')
    company['notes']='Official parent tax row active on 2026-10-13. Product and alternative activity gates remain separate. '+(
        'See source integrity resolution and client corroboration in evidence records.' if key=='enfarm' else
        'Two branches closed; parent and remaining listed branches active.' if key=='datbike' else
        'Global website names Singapore parent; VN operating role requires separate review.' if key=='vulcan' else
        'User report retained separately; direct official capture now available.')
with (DATA/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(candidates[0])); writer.writeheader(); writer.writerows(candidates)
(DATA/'evidence.jsonl').write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in evidence)+'\n',encoding='utf-8')
print('Recorded 4 exact parent tax rows; branch closures not applied to parents.')
