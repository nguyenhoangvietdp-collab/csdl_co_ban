"""Prepare startup-only Sheets writes; submit through the connected Drive tool.

Existing business crawler tabs are outside this export. Tax IDs stay text.
"""
import csv
import json
from datetime import date
from pathlib import Path
from prepare_sheet import cell
from startup_tool import DATA, validate_evidence

HEADERS = ['Mã hồ sơ','Thương hiệu','Pháp nhân','MST mẹ','Đầu ra vật lý','Kết quả','Còn thiếu','Bằng chứng hợp lệ','Ngày bộ lọc','Ngày kiểm tra Thuế','Trạng thái Thuế','Nguồn phát hiện','Giới hạn / ghi chú']
REASONS = dict(missing_parent_company_tax_id='Chưa xác minh MST mẹ',no_matching_official_tax_evidence='Thiếu kết quả Thuế chính thức',tax_inactive_or_conflicting_status='Thuế ngừng hoạt động hoặc xung đột',counter_evidence_review_missing='Chưa rà soát phản chứng',brand_legal_entity_mapping_unverified='Chưa nối thương hiệu với pháp nhân',no_recent_fund_government_contest_publication='Thiếu công bố gần đây từ quỹ/chính phủ/cuộc thi',startup_unverified='Chưa xác minh tiêu chí startup',technology_unverified='Chưa xác minh công nghệ',product_unverified='Chưa xác minh sản phẩm',vietnam_legal_entity_unverified='Chưa xác minh pháp nhân Việt Nam',need_two_independent_recent_activity_publishers='Thiếu hai chủ nguồn hoạt động gần đây',need_two_distinct_activity_origins='Thiếu hai sự kiện hoạt động khác nhau',product_classification_unreviewed='Chưa phân loại đầu ra vật lý',source_integrity_requires_resolution='Cờ chất lượng nguồn chưa xử lý',negative_activity_requires_resolution='Bằng chứng hoạt động tiêu cực chưa xử lý')
KINDS = dict(tax='Thuế',tax_secondary='Thuế — TVPL thay thế',identity='Thương hiệu / pháp nhân',discovery='Nguồn phát hiện',startup='Tiêu chí startup',product='Sản phẩm',technology='Công nghệ',activity='Hoạt động',counter_review='Rà soát phản chứng',source_integrity_flag='Chất lượng nguồn',negative_activity='Hoạt động tiêu cực')

def main():
    with (DATA/'screening.csv').open(encoding='utf-8-sig',newline='') as f:
        companies=list(csv.DictReader(f))
    evidence=[json.loads(l) for l in (DATA/'evidence.jsonl').read_text(encoding='utf-8').splitlines() if l]
    today=date.fromisoformat(companies[0]['as_of'])
    by_id={c['id']:c for c in companies}
    rows=[HEADERS]
    for c in companies:
        taxes=[e for e in evidence if e['company_id']==c['id'] and e['kind'] in {'tax','tax_secondary'} and e.get('tax_id')==c['tax_id'] and not validate_evidence(e,today,DATA)]
        tax=max(taxes,key=lambda e:(e['kind']=='tax',e.get('checked_at','')),default={})
        tax=dict(tax)
        if tax.get('kind')=='tax_secondary':
            tax['status'] += ' [TVPL — nguồn thay thế]'
        rows.append([c['id'],c['brand'],c['legal_name'],c['tax_id'],{'yes':'Vật lý','hybrid':'Kết hợp','no':'Phi vật lý'}.get(c['physical'],'Chưa phân loại'),{'approved':'Đạt','pending':'Chờ','excluded_tax_entity':'Loại pháp nhân Thuế'}[c['decision']],'; '.join(REASONS.get(r,r) for r in c['reasons'].split('; ') if r),int(c['valid_evidence']),c['as_of'],tax.get('checked_at',''),tax.get('status',''),c['discovery_url'],c['notes']])
    proof=[['Mã bằng chứng','Mã hồ sơ','Thương hiệu','Loại bằng chứng','Chủ nội dung','Ngày sự kiện','Ngày công bố','Ngày thu thập','Ngày kiểm tra Thuế','Trạng thái Thuế','Đánh giá sử dụng','URL nguồn','Giới hạn / bối cảnh (ghi chú nghiên cứu)']]
    for e in evidence:
        errors=validate_evidence(e,today,DATA)
        note=' | '.join(str(e[k]) for k in ('caveat','event_date_basis','review_note','resolution') if e.get(k))
        proof.append([e['id'],e['company_id'],by_id[e['company_id']]['brand'],KINDS.get(e['kind'],e['kind']),e['publisher_owner'],e.get('event_date',''),e.get('published_at',''),e.get('retrieved_at','')[:10],e.get('checked_at',''),e.get('status',''),'Giữ ngoài duyệt: '+', '.join(errors) if errors else 'Hợp lệ theo kiểm tra; xem giới hạn',e['url'],note])
    approved=[HEADERS,[None]*13]
    # shortcut: FILTER covers 1000 rows; expand the grid and range before a larger queue.
    formula='=IFERROR(FILTER(Startup_Danh_sach!A2:M1000;Startup_Danh_sach!F2:F1000="Đạt");"Chưa có hồ sơ đạt")'
    tabs=[('Startup_Danh_sach',1006,rows),('Startup_Dat',1007,approved),('Startup_Bang_chung',1008,proof)]
    requests=[]
    for title,sid,values in tabs:
        assert all(len(row)==13 for row in values)
        cells=[{'values':[cell(v) for v in row]} for row in values]
        if title=='Startup_Dat':
            cells[1]['values']=[{} for _ in HEADERS]
            cells[1]['values'][0]={'userEnteredValue':{'formulaValue':formula}}
        requests.append({'updateCells':{'range':{'sheetId':sid,'startRowIndex':0,'endRowIndex':len(cells),'startColumnIndex':0,'endColumnIndex':13},'rows':cells,'fields':'userEnteredValue'}})
    payload={'tabs':[{'title':t,'sheetId':sid,'rows':len(values),'columns':13} for t,sid,values in tabs],'requests':requests,'approved_count':sum(c['decision']=='approved' for c in companies),'as_of':today.isoformat()}
    (DATA/'sheet_startup_payload.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k!='requests'},ensure_ascii=False))

if __name__=='__main__':
    main()
