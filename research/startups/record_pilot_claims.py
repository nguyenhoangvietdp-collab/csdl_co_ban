"""Use the installed Deep Research ledger; source snapshots stay local."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT/'data/startups'
LEDGER = Path('C:/Users/Admin/.codex/plugins/cache/local-project-tools/deep-research/3.2.0/skills/deep-research/scripts/research_ledger.py')
evidence = {e['id']:e for e in map(json.loads,(DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines())}
selections = [
    ('E001','Q1','Touchstone names Selex Motors, Stride, Alterno, Enfarm, Neorice and Forte Biotech among backed companies.'),
    ('E_TAX_SELEX','Q3','The official tax lookup lists 0108324659, CÔNG TY CỔ PHẦN PHƯƠNG TIỆN ĐIỆN THÔNG MINH SELEX, as NNT đang hoạt động.'),
    ('E016','Q5','VSV describes Vulcan Augmetics as providing electric prosthetics.')
]
rows=[]
for key, subq, claim in selections:
    e=evidence[key]
    destination=subprocess.check_output([sys.executable,str(LEDGER),'source-path',str(HERE),e['url']],text=True).strip()
    shutil.copyfile(DATA/e['snapshot'],destination)
    rows.append(dict(subq=subq,claim=claim,quote=e['quote'],url=e['url'],source_tier=1,
        provider='web + captured primary page',published=e.get('published_at',''),stance='supports'))
input_file=HERE/'rows.jsonl'
input_file.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(LEDGER),'add-batch',str(HERE),str(input_file)],check=True)
