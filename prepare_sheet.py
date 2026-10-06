"""Normalize crawler outputs and generate native Sheets batch requests.

Run after crawl.ps1. The requests can be submitted through the connected Google
Drive tool, or sync_sheet.py with an explicitly configured Google credential.
"""
import html
import json
import os
import re
from pathlib import Path

DATA = Path(__file__).parent / 'data'
TARGET = os.environ.get('GOOGLE_SHEET_ID', '').strip()
TAB_IDS = {'Doanh_nghiep': 1001, 'San_pham_dich_vu': 1002, 'Tai_lieu': 1003, 'Nhat_ky': 1004}

def read(name):
    return json.loads((DATA / name).read_text(encoding='utf-8-sig'))

def clean(value):
    if value is None:
        return ''
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return html.unescape(re.sub('<[^>]+>', ' ', str(value))).strip()

def media_url(path):
    if not path:
        return ''
    if path.startswith('https://'):
        return path
    return 'https://apiv2.business.gov.vn/medias/' + path.lstrip('/')

def cell(value):
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        return {'userEnteredValue': {'numberValue': value}}
    return {'userEnteredValue': {'stringValue': clean(value)[:49000]}}

def main():
    companies = {}
    sources = {}
    for name, label in [('companies_v1.json','v1'), ('companies_b2b.json','b2b')]:
        for obj in read(name):
            key = str(obj['id'])
            companies.setdefault(key, obj)
            sources.setdefault(key, []).append(label)
    run = read('run.json')
    now = run['scraped_at']
    company_rows = [[
        'ID','Tên doanh nghiệp','Mã số thuế','Nguồn','Tên tiếng Anh','Loại hình',
        'Địa chỉ','Mã tỉnh theo nguồn','Mã huyện theo nguồn','Mã quốc gia theo nguồn',
        'Ngành chính','Các ngành','Điện thoại','Email','Website','Vốn điều lệ (VND)',
        'Số lao động','Người đại diện','Chức vụ','Ngày thành lập','Doanh thu BQ 3 năm',
        'Vốn BQ 3 năm','Lao động BQ 3 năm','URL hồ sơ v1','URL hồ sơ B2B',
        'Cập nhật tại nguồn','Thu thập lúc']]
    document_rows = [['ID tài liệu','ID doanh nghiệp/sản phẩm','Loại chủ thể','Tên tài liệu','URL nguồn','Dung lượng nguồn (byte)','Loại file','URL Drive','Trạng thái đọc','Thu thập lúc']]
    documents_seen = set()
    def documents(obj, kind):
        for f in obj.get('fileVaults') or []:
            key = str(f.get('id') or f.get('filePath'))
            if key in documents_seen:
                continue
            documents_seen.add(key)
            name = f.get('fileName') or ''
            suffix = Path(name).suffix.lower()
            document_rows.append([key,str(obj['id']),kind,name,media_url(f.get('filePath')),
                f.get('fileSize'),suffix,'','Chưa tải/đọc' if suffix=='.pdf' else 'Chỉ mục liên kết',now])
    for key, obj in companies.items():
        websites = obj.get('websites') or ([obj.get('website')] if obj.get('website') else [])
        sectors = '; '.join(f"{x.get('code','')}: {x.get('name','')}" for x in obj.get('nganhNghes') or [])
        company_rows.append([key,obj.get('tenGiaoDich'),str(obj.get('maSoThue') or ''),'; '.join(sources[key]),obj.get('tenTiengAnh'),
            (obj.get('loaiHinhDoanhNghiep') or {}).get('tenLoaiHinh'),obj.get('diaChi'),obj.get('maTinhThanh'),obj.get('maQuanHuyen'),
            obj.get('quocGiaTruSoChinh'),obj.get('nganhNgheChinh'),sectors,obj.get('dienThoai'),obj.get('email'),'; '.join(websites),
            obj.get('vonDieuLe'),obj.get('tongSoLaoDong'),obj.get('nguoiDaiDien'),obj.get('chucVuNguoiDaiDien'),obj.get('ngayThanhLap'),
            obj.get('doanhThuBinhQuan3Nam'),obj.get('tongVonBinhQuan3Nam'),obj.get('laoDongBinhQuan3Nam'),
            f'https://business.gov.vn/doanh-nghiep-nho-va-vua/ho-so/v1/{key}' if 'v1' in sources[key] else '',
            f'https://business.gov.vn/doanh-nghiep-nho-va-vua/ho-so/{key}' if 'b2b' in sources[key] else '',obj.get('lastModificationTime'),now])
        documents(obj, 'Doanh nghiệp')
    product_rows = [['ID','Tên sản phẩm/dịch vụ','Nhu cầu','Mô tả','Thẻ tìm kiếm','Thị trường mục tiêu','Từ ngày','Đến ngày','URL nguồn','Cập nhật tại nguồn','Thu thập lúc']]
    for obj in read('products.json'):
        product_rows.append([str(obj['id']),obj.get('name'),{0:'Chào mua',1:'Chào bán'}.get(obj.get('type'),'Không xác định'),
            clean(obj.get('descriptions')),'; '.join(obj.get('searchTags') or []),obj.get('targetMarketing'),obj.get('timeFrom'),obj.get('timeTo'),
            f"https://business.gov.vn/doanh-nghiep-nho-va-vua/san-pham-dich-vu/{obj['id']}",obj.get('lastModificationTime'),now])
        documents(obj, 'Sản phẩm')
    pdf_summary = DATA/'pdf_summary_rows.json'
    if pdf_summary.exists():
        summary_rows = json.loads(pdf_summary.read_text(encoding='utf-8-sig'))
        summarized_ids = {str(row[0]) for row in summary_rows[1:] if row}
        for row in document_rows[1:]:
            if row[0] in summarized_ids:
                row[8]='Có thông tin trích xuất; xem PDF_Tom_tat'
    logs = [['Thời điểm','Nguồn','Số bản ghi','Tổng tại nguồn','Trạng thái'],
            *[[now,x['source'],x['count'],x['expected'],'Đã kiểm tra đủ phân trang'] for x in run['sources']],
            [now,'Doanh nghiệp hợp nhất',len(companies),'','Khử trùng lặp theo ID'],
            [now,'Tài liệu PDF','','','Có bảng trích xuất PDF; xem phương pháp và trang dẫn chứng' if pdf_summary.exists() else 'Chưa tải/đọc']]
    tabs = {'Doanh_nghiep':company_rows,'San_pham_dich_vu':product_rows,'Tai_lieu':document_rows,'Nhat_ky':logs}
    if pdf_summary.exists():
        TAB_IDS['PDF_Tom_tat']=1005
        tabs['PDF_Tom_tat']=summary_rows
    batches = []
    for name, rows in tabs.items():
        sid=TAB_IDS[name]
        for start in range(0,len(rows),75):
            chunk=rows[start:start+75]
            batches.append({'sheet':name,'start':start,'requests':[{'updateCells':{
                'range':{'sheetId':sid,'startRowIndex':start,'endRowIndex':start+len(chunk),'startColumnIndex':0,'endColumnIndex':len(rows[0])},
                'rows':[{'values':[cell(v) for v in row]} for row in chunk], 'fields':'userEnteredValue'}}]})
    metadata = {name:{'sheetId':TAB_IDS[name],'rows':len(rows),'columns':len(rows[0])} for name,rows in tabs.items()}
    for name, rows in tabs.items():
        (DATA/f'{name}_rows.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
    (DATA/'sheet_batches.json').write_text(json.dumps(batches,ensure_ascii=False),encoding='utf-8')
    (DATA/'sheet_manifest.json').write_text(json.dumps(metadata,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(metadata,ensure_ascii=False))

if __name__=='__main__':
    main()
