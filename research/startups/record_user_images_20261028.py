"""Preserve user images; accept two parent tax tables and hold other observations."""
import csv
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from startup_tool import validate_evidence

D = ROOT / 'data/startups'
DAY = '2026-10-28'
# Names are transcribed only where visible; no missing Vietnamese names are invented.
IMAGES = [
    (1,'2dc3e617-3ce4-4e3a-9fb6-187116d9a446','S055','0313231485','CÔNG TY CỔ PHẦN VERITAS VIỆT NAM','NNT đang hoạt động','tax'),
    (2,'d3f656f7-6934-4f48-ab42-1180b49475b6','S006','0317428355','CÔNG TY TNHH FORTE BIOTECH VIỆT NAM','NNT đang hoạt động','tax'),
    (3,'0c2bdadd-8755-4338-9532-fb9281f1d571','S007','0109206584','','Không tìm thấy người nộp thuế nào phù hợp.','wrong_form'),
    (4,'3432dcf1-6d00-44de-b7cb-22920dcf41c5','S005','1200874529','','Active','secondary'),
    (5,'af2c36a5-6d5a-4fdf-bce8-e95e49ccb6c7','S017','0110830839','AIZ JOINT STOCK COMPANY','Đang hoạt động','secondary'),
    (6,'47e94a14-0bd3-4cc0-a801-6792ddd5d63e','S007','0109206584','N2TP TECHNOLOGY SOLUTIONS','Đang hoạt động','secondary'),
    (7,'05725f91-9669-4a2d-8ec4-4dabd5579d3f','S019','0318400345','','Đang hoạt động','duplicate'),
    (8,'3ad17578-91b7-470a-9234-e2bb29653ccb','S019','0318400345','CÔNG TY CỔ PHẦN CÔNG NGHỆ BRAIN-LIFE LINK','Đang hoạt động','secondary'),
    (9,'d1c4528e-d747-4437-84cd-b25b77aa17dc','S032','0317812963','VIOT ENERGY EFFICIENCY PLATFORM JOINT STOCK COMPANY','Đang hoạt động','secondary'),
    (10,'8c959717-0e58-4ea4-b96c-0dd2db0adb96','S034','0111314178','CÔNG TY CỔ PHẦN CÔNG NGHỆ NĂNG LƯỢNG VOLNEXUS','Đang hoạt động','secondary'),
    (11,'41786c74-9a8c-4803-a94c-344ae71871b3','S030','0319525040','HBC NEXUS JOINT STOCK COMPANY','Đang hoạt động','secondary'),
    (12,'0b89591b-02ee-4d4e-956d-24b44805415d','S022','0319317523','CÔNG TY CỔ PHẦN FIZIBOX','Đang hoạt động','secondary'),
    (13,'07731aba-c691-4c0f-b512-339140e0061a','S029','0316563337','CÔNG TY TNHH OLOGN TECHNOLOGY','Đang hoạt động','secondary'),
    (14,'1594c29f-1930-4121-8150-50b0e9da4dd4','S029','0316563337','','Đang hoạt động','duplicate'),
    (15,'11988f58-dca7-4b70-bc7d-e48919e0d516','S028','4201292624','CÔNG TY TNHH MỘT THÀNH VIÊN CÔNG NGHỆ CAO NHA TRANG','Đang hoạt động','secondary'),
    (16,'5ea8421b-e163-4ce5-b980-4f99808df438','S039','0401799975','FASTDO DIGITAL MANAGEMENT COMPANY LIMITED','Đang hoạt động','secondary'),
    (17,'641021a2-6fb5-4678-83d8-ce18dd6d4892','S014','0108919688','CÔNG TY CỔ PHẦN CÔNG NGHỆ GIÁO DỤC KIRO VIỆT NAM','Đang hoạt động','secondary'),
    (18,'e92f2d9f-9c5d-4346-8704-5de36ccd5735','S018','0110515925','CÔNG TY TNHH ANTAJA','Đang hoạt động','secondary'),
    (19,'96646bf1-e5cc-4373-8661-8d71e2fd3f52','S020','0111030296','FILLSONIC JOINT STOCK COMPANY','Đang hoạt động','secondary'),
    (20,'37177d32-f1f9-465c-afdb-4b743562ebe6','S023','0316051120','CÔNG TY CỔ PHẦN CÔNG NGHỆ KHÔNG GIAN TƯƠNG LAI','Đang hoạt động','secondary'),
    (21,'79b34ee9-dde2-41ac-9109-52e677728782','S024','0319276080','CÔNG TY TNHH HEALTHBRIDGE VIỆT NAM','Đang hoạt động','secondary'),
    (22,'20e4f8e1-a3ce-459e-a22c-88d4ef0d2f5c','S054','0319205202','CÔNG TY TNHH PLANTNER','Đang hoạt động','secondary'),
    (23,'873d8729-9a7a-43a4-88af-e950d015af6c','S002','0316841954','STRIDE MTV COMPANY LIMITED','Đang hoạt động','secondary'),
    (24,'2d0a3fc9-1889-4ebc-9a7d-c96eb6dd47e9','S002','0316839754','CÔNG TY TNHH STRIDE SOLAR','Đang hoạt động','secondary'),
    (25,'5f7aa27c-ce1c-4c30-987f-6dc10dd83842','S002','0319337720','CÔNG TY TNHH STRIDE SOLAR SOLUTIONS','Đang hoạt động','secondary'),
    (26,'5abf6cfb-c1fa-45c4-83f1-96a51ad88157','S031','0110848057','UDATA JOINT STOCK COMPANY','Đang hoạt động','secondary'),
]
with (D / 'candidates.csv').open(encoding='utf-8-sig', newline='') as f:
    companies = list(csv.DictReader(f))
by_id = {c['id']: c for c in companies}
evidence = [json.loads(s) for s in (D / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if s]
manifest = []
for number, uid, cid, mst, name, status, category in IMAGES:
    source = Path('C:/Users/Admin/AppData/Local/Temp') / f'codex-clipboard-{uid}.png'
    image_file = f'sources/user_20261028_{number:02d}_{mst}.png'
    destination = D / image_file
    if source.exists():
        shutil.copyfile(source, destination)
    assert destination.is_file(), source
    image_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
    quote = '\n'.join(v for v in (name, mst, status) if v)
    if category == 'wrong_form':
        quote = 'Mã số thuế*\n' + mst + '\nHọ và tên\n' + status
    snapshot = f'sources/user_20261028_{number:02d}_{mst}.txt'
    context = ('Ảnh do người dùng gửi ngày28/10/2026. Chép trực quan các trường nhìn thấy; '
        'ngày tra cứu gốc và thanh địa chỉ không hiển thị. Ngày kiểm tra là ngày đọc ảnh, không phải ngày truy vấn đã xác minh.\n')
    if number == 1:
        context += ('Chi nhánh0313231485-001: CHI NHÁNH - CÔNG TY CỔ PHẦN VERITAS VIỆT NAM; '
            'hiển thị ngừng hoạt động, phần cuối trạng thái bị cắt mép phải. Không áp trạng thái chi nhánh cho công ty mẹ.\n')
    (D / snapshot).write_text(context + quote + '\n', encoding='utf-8')
    entry = dict(image_number=number, company_id=cid, observed_tax_id=mst, observed_legal_name=name,
        observed_status=status, category=category, image_file=image_file, image_sha256=image_hash,
        snapshot=snapshot, original_filename=source.name, received_at=DAY)
    if category == 'duplicate':
        entry['same_entity_as_image'] = 8 if number == 7 else 13
        manifest.append(entry)
        continue
    official = category == 'tax'
    caveat = ('Ảnh bảng Thuế do người dùng cung cấp, không phải lượt đọc trực tiếp của Codex. '
        'URL cổng Thuế được quy chiếu theo ngữ cảnh tra cứu trước đó; thanh địa chỉ và ngày truy vấn gốc không có trong ảnh.' if official else
        'Ảnh người dùng cung cấp; chưa có URL nguồn gốc được xác minh. Giữ ngoài cửa duyệt Thuế; '
        'không mở rộng quy tắc nguồn thay thế TVPL sang các danh bạ khác và không giả URL từ tên doanh nghiệp.')
    if category == 'wrong_form':
        caveat += ' Biểu mẫu có trường Họ và tên, đang tra cá nhân; kết quả không tìm thấy không chứng minh N2TP/doanh nghiệp ngừng hoạt động hoặc MST sai.'
    if cid == 'S034':
        caveat += ' Ảnh ghi VOLNEXUS, chưa chứng minh đồng nhất pháp nhân với thương hiệu VOLTERRA.'
    if cid == 'S002':
        caveat += ' Ba MST Stride giữ riêng; cùng địa chỉ/người đại diện không xác định đơn vị vận hành cần chọn.'
    if cid == 'S031':
        caveat += ' 0110848057 được ghi nhận; chưa tự loại đầu mối0110902473 hoặc chốt quan hệ với thương hiệu từ tên trùng.'
    if cid == 'S029':
        caveat += ' Ảnh ghi OLOGN, chưa xác minh lịch sử đổi tên ORCO trong nguồn TVPL cũ.'
    record = dict(id=f'E_USER_IMAGE_{number:02d}_20261028', company_id=cid,
        kind='tax' if official else 'user_observation', quote=quote,
        url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp' if official else f'attachment://user-20261028/image-{number:02d}',
        publisher_owner='Cục Thuế — ảnh người dùng cung cấp' if official else 'Ảnh người dùng cung cấp — chưa xác minh nguồn gốc',
        snapshot=snapshot, sha256=hashlib.sha256((D / snapshot).read_text(encoding='utf-8').encode()).hexdigest(),
        method='image_transcription', image_file=image_file, image_sha256=image_hash,
        retrieved_at=DAY, reviewed=True, reviewer='Codex: read visible fields in user-supplied image', caveat=caveat,
        observed_tax_id=mst, observed_legal_name=name, observed_status=status)
    if official:
        record.update(tax_id=mst, legal_name=name, status=status, checked_at=DAY,
            row_scope='parent_company', check_date_basis='Review/receipt date; original query date not shown.')
        by_id[cid].update(tax_id=mst, legal_name=name, country='VN')
        if cid == 'S006':
            by_id[cid]['notes'] = by_id[cid]['notes'].replace(
                'candidate MST0317428355 from secondary lead, official lookup pending.',
                'parentMST0317428355 now supported by user-supplied tax-table image received28Oct2026, original query date not shown.')
    errors = validate_evidence(record, date(2026, 10, 28), D)
    assert errors == ([] if official else ['invalid_source_url']), (number, errors)
    old = next((e for e in evidence if e['id'] == record['id']), None)
    if old:
        evidence[evidence.index(old)] = record
    else:
        evidence.append(record)
    entry.update(evidence_id=record['id'], caveat=caveat)
    manifest.append(entry)

for cid in {m['company_id'] for m in manifest}:
    relevant = [m for m in manifest if m['company_id'] == cid and m['category'] != 'duplicate']
    summary = '; '.join(f"ảnh{m['image_number']}: {m['observed_tax_id']} — {m['observed_status']}" for m in relevant)
    note = f' [Ảnh nhận28/10/2026: {summary}. '
    note += ('Ghi Thuế theo ảnh người dùng gửi; ngày tra cứu gốc không hiển thị, không phải đọc trực tiếp. Các cửa khác xét riêng.]' if cid in {'S006','S055'} else
        'Chỉ là quan sát từ ảnh, chưa thay kết quả Thuế hợp lệ hoặc chốt quan hệ thương hiệu/pháp nhân.]')
    if note not in by_id[cid]['notes']:
        by_id[cid]['notes'] += note
    if cid == 'S055':
        by_id[cid]['notes'] += ' Chi nhánh-001 ngừng hoạt động trong ảnh, giữ riêng khỏi công ty mẹ đang hoạt động.' if 'Chi nhánh-001 ngừng hoạt động trong ảnh' not in by_id[cid]['notes'] else ''

with (D / 'candidates.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(companies[0])); w.writeheader(); w.writerows(companies)
(D / 'evidence.jsonl').write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in evidence) + '\n', encoding='utf-8')
(D / 'user_images_20261028.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('Preserved26 originals; recorded24 observations, including2 parent tax images;2 duplicate views not counted twice.')
