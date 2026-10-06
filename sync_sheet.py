"""Push the prepared dataset into the user-selected existing Google Sheet.

Authentication: set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON
file shared as editor on the destination, or GOOGLE_SHEETS_ACCESS_TOKEN to an
OAuth token with spreadsheets scope. Credentials are never stored in this repo.
"""
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from prepare_sheet import TARGET, TAB_IDS, main as prepare

ROOT = Path(__file__).parent

def token():
    value=os.environ.get('GOOGLE_SHEETS_ACCESS_TOKEN')
    if value:
        return value
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        raise RuntimeError('Configure OAuth token or a service account; alternatively submit generated batches using the connected Google Drive connector in Codex.')
    import google.auth
    from google.auth.transport.requests import Request
    credentials,_=google.auth.default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
    credentials.refresh(Request())
    return credentials.token

def api(path, payload=None):
    url=f'https://sheets.googleapis.com/v4/spreadsheets/{TARGET}{path}'
    for attempt in range(4):
        request=urllib.request.Request(url,data=None if payload is None else json.dumps(payload).encode(),headers={'Authorization':'Bearer '+token(),'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (429,500,502,503,504) or attempt==3:
                raise
            time.sleep(2**(attempt+1))

def main():
    if not TARGET:
        raise RuntimeError('Set GOOGLE_SHEET_ID to the destination spreadsheet ID before syncing.')
    prepare()
    metadata=api('?fields=sheets.properties')
    existing={s['properties']['title']:s['properties'] for s in metadata['sheets']}
    mapping={}
    requests=[]
    manifest=json.loads((ROOT/'data/sheet_manifest.json').read_text(encoding='utf-8'))
    for name, info in manifest.items():
        if name in existing:
            mapping[info['sheetId']]=existing[name]['sheetId']
            props=existing[name]
            grid=props.get('gridProperties',{})
            requests.append({'updateSheetProperties':{'properties':{'sheetId':props['sheetId'],'gridProperties':{'rowCount':max(grid.get('rowCount',0),info['rows']), 'columnCount':max(grid.get('columnCount',0),info['columns'])}},'fields':'gridProperties.rowCount,gridProperties.columnCount'}})
        else:
            mapping[info['sheetId']]=info['sheetId']
            requests.append({'addSheet':{'properties':{'sheetId':info['sheetId'],'title':name,'gridProperties':{'rowCount':max(1000,info['rows']),'columnCount':info['columns'],'frozenRowCount':1}}}})
    api(':batchUpdate',{'requests':requests})
    for b in json.loads((ROOT/'data/sheet_batches.json').read_text(encoding='utf-8')):
        for request in b['requests']:
            request['updateCells']['range']['sheetId']=mapping[request['updateCells']['range']['sheetId']]
        api(':batchUpdate',{'requests':b['requests']})
        time.sleep(1.1)
    # Clear only obsolete rows in crawler-owned tabs after successful replacement.
    cleanup=[]
    for name,info in manifest.items():
        old=existing.get(name,{}).get('gridProperties',{}).get('rowCount',0)
        if old>info['rows']:
            cleanup.append({'updateCells':{'range':{'sheetId':mapping[info['sheetId']],'startRowIndex':info['rows'],'endRowIndex':old,'startColumnIndex':0,'endColumnIndex':info['columns']},'rows':[],'fields':'userEnteredValue'}})
    if cleanup:
        api(':batchUpdate',{'requests':cleanup})
    for name,info in manifest.items():
        values=api('/values/'+urllib.parse.quote(f"'{name}'!A1:A{info['rows']}",safe=''))['values']
        if len(values)!=info['rows']:
            raise RuntimeError(f'Write verification failed: {name}')
    print('Verified crawler output in https://docs.google.com/spreadsheets/d/'+TARGET+'/edit')

if __name__=='__main__':
    main()
