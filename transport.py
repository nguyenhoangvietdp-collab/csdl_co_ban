import json
from pathlib import Path

d=Path(__file__).parent/'data'
manifest=json.loads((d/'sheet_manifest.json').read_text(encoding='utf-8'))
chunks=[]
for name, meta in manifest.items():
    rows=json.loads((d/f'{name}_rows.json').read_text(encoding='utf-8'))
    batch=[]
    start=0
    for row in rows:
        if batch and len(json.dumps(batch+[row],ensure_ascii=False)) > 14000:
            chunks.append({'id':meta['sheetId'],'start':start,'rows':batch})
            start+=len(batch)
            batch=[]
        batch.append(row)
    if batch:
        chunks.append({'id':meta['sheetId'],'start':start,'rows':batch})
for i, chunk in enumerate(chunks):
    (d/f'compact_{i:03}.json').write_text(json.dumps(chunk,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'count':len(chunks),'max_chars':max(len(json.dumps(c,ensure_ascii=False)) for c in chunks)}))
