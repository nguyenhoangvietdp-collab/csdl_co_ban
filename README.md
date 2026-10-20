# CSDL CƠ BẢN

Thu thập API công khai business.gov.vn, chuẩn hóa và ghi Google Sheets. Sheet là đầu ra chính. Không tiếp tục upload Google Drive.

## Nguồn

- https://business.gov.vn/doanh-nghiep-nho-va-vua/tim-kiem/v1
- https://business.gov.vn/doanh-nghiep-nho-va-vua/tim-kiem?tab=1

Phân trang mặc định 50 bản ghi, retry tối đa 4 lần; kiểm tra số ID duy nhất bằng tổng tại nguồn. Không dùng cookie đăng nhập.

## Cài đặt

Yêu cầu Python 3.10+, PowerShell 5.1 hoặc 7. PDF scan cần Poppler `pdftoppm` trên PATH. OCR tùy chọn cần Tesseract cùng ngôn ngữ `vie` và `eng`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Thu thập

Chạy trong thư mục repo:

```powershell
.\crawl.ps1
.\.venv\Scripts\python.exe prepare_sheet.py
```

`data/` chứa snapshot, bảng chuẩn hóa, manifest và batch ghi. Thư mục này bị loại khỏi Git. Hợp nhất doanh nghiệp v1/B2B theo ID nguồn. ID, mã số thuế, điện thoại giữ dạng chuỗi. Mã địa phương giữ nguyên theo nguồn.

## Ghi Google Sheet

Lấy ID từ URL Sheet `/spreadsheets/d/ID/edit`. Với service account: bật Google Sheets API và chia sẻ Sheet cho email service account với quyền chỉnh sửa. Giữ khóa ngoài repo.

```powershell
$env:GOOGLE_SHEET_ID = 'YOUR_SPREADSHEET_ID'
$env:GOOGLE_APPLICATION_CREDENTIALS = 'C:\secure\service-account.json'
.\.venv\Scripts\python.exe sync_sheet.py
```

Hoặc dùng OAuth token còn hiệu lực, scope `https://www.googleapis.com/auth/spreadsheets`, tài khoản có quyền chỉnh sửa:

```powershell
$env:GOOGLE_SHEET_ID = 'YOUR_SPREADSHEET_ID'
$env:GOOGLE_SHEETS_ACCESS_TOKEN = 'YOUR_SHORT_LIVED_OAUTH_TOKEN'
.\.venv\Scripts\python.exe sync_sheet.py
```

Nếu cấu hình cả hai, script ưu tiên token. `.env.example` là mẫu; script không tự đọc `.env`. Không lưu token thật vào file hoặc commit.

Trong Codex có thể gửi batch qua connector Google Sheets; cần ánh xạ sheetId theo metadata Sheet đích.

| Tab quản lý | Nội dung |
|---|---|
| Doanh_nghiep | Thông tin kinh doanh, nguồn và thời điểm |
| San_pham_dich_vu | Sản phẩm, nhu cầu và thị trường |
| Tai_lieu | Chỉ mục liên kết, loại file và trạng thái đọc |
| Nhat_ky | Tổng hợp lần chạy |
| PDF_Tom_tat | Thông tin PDF nếu có dữ liệu trích xuất |

**Đồng bộ ghi đè các tab quản lý và xóa dòng dư trong phạm vi cột quản lý.** Đặt ghi chú thủ công ở tab khác. Ghi theo nhiều batch, chưa có giao dịch nguyên tử hoặc rollback; lỗi giữa chừng có thể để lại dữ liệu ghi một phần. Các tab khác được giữ lại.

Script độc lập đọc lại số dòng cột A. Chưa tự đối chiếu toàn bộ ô. Nhật ký chưa tích lũy nhiều lần chạy. Chưa có khóa nối sản phẩm với doanh nghiệp.

## PDF

Đặt file đã tải trong `output/`:

```powershell
.\.venv\Scripts\python.exe process_pdf.py output\document.pdf
# OCR tùy chọn
.\.venv\Scripts\python.exe process_pdf.py output\document.pdf --ocr
```

Kết quả gồm `pages.json` và ảnh scan trong thư mục cùng tên PDF, bỏ phần mở rộng. Đoạn khớp từ khóa là ứng viên, cần kiểm tra nội dung và trang dẫn chứng.

Để ghi thông tin đã kiểm tra: sao chép `examples/pdf_summary_rows.example.json` thành `data/pdf_summary_rows.json`, thay bằng ID thật, giá trị, trang và phương pháp đọc; đồng bộ lại. Chưa tự tạo tóm tắt nghiệp vụ hoặc tải toàn bộ PDF.

## Tệp và tài liệu

- `crawl.ps1`: thu thập ba danh sách API.
- `prepare_sheet.py`: chuẩn hóa và tạo batch.
- `sync_sheet.py`: ghi Sheet theo biến môi trường.
- `process_pdf.py`: đọc văn bản, render scan, OCR tùy chọn.
- `transport.py`: chia chunk để sử dụng connector Codex.
- [Sơ đồ CSDL](CSDL_SHEET_MAP.md).
- [Tiến độ](TASKS.md), [changelog](CHANGELOG.md).
- [Đóng góp](CONTRIBUTING.md), [bảo mật](SECURITY.md).

## Sàng lọc startup từ nguồn đầu tư và công bố

`startup_tool.py` thu thập snapshot HTML và duyệt bằng chứng đã được đọc. Xem [phương pháp và các cửa kiểm tra](research/startups/SCREENING_METHOD.md).

Nguồn mẫu nằm trong `startup_sources.json`. Kết quả ở `data/startups/`: bảng ứng viên, bằng chứng, screening.csv và approved_50.csv. Danh sách approved chỉ nhận công ty qua đủ các cửa; thiếu 50 thì báo complete=false. Không tự suy ra trạng thái thuế từ website tổng hợp hoặc portfolio.

```powershell
python startup_tool.py fetch --sources startup_sources.json
python startup_tool.py screen --as-of YYYY-MM-DD
python prepare_startup_sheet.py
```

Trích thông tin từ ảnh/PDF và CAPTCHA cần bước đọc hoặc tra cứu được cho phép. Đầu ra startup đã ghi vào ba tab `Startup_Danh_sach`, `Startup_Dat`, `Startup_Bang_chung` trong Sheet CSDL CƠ BẢN. `prepare_startup_sheet.py` chuẩn bị `data/startups/sheet_startup_payload.json` để gửi qua connector; không tự ghi hoặc xác thực tài khoản. Đọc metadata Sheet đích và ánh xạ lại sheetId trước mỗi lần gửi. Các ID 1006–1008 và công thức dấu chấm phẩy đang dành cho workbook tiếng Việt này. Không dùng file payload để ghi đè tab có chỉnh sửa thủ công khi chưa đối chiếu.

`Startup_Dat` tự lọc các dòng “Đạt” từ danh sách; không tự tra Thuế hoặc duyệt bằng chứng mới. Bộ lọc ghi nhận trạng thái tại thời điểm kiểm tra, không bảo đảm hoạt động liên tục trong tương lai. Khi cập nhật danh sách dài hơn 1.000 dòng cần mở rộng vùng công thức và grid. Xem [sơ đồ Sheet](CSDL_SHEET_MAP.md).

Tiến độ startup: [nhật ký bằng chứng và giới hạn](research/startups/PROGRESS.md), [bảng trạng thái hiện tại](research/startups/current_screening.csv). Bảng này chứa cả hồ sơ chờ và hồ sơ loại; không phải danh sách 50 công ty đã đạt. Các script `enrich_*` là ghi nhận hồ sơ nghiên cứu cụ thể, cần snapshot cục bộ đã đọc; không phải bộ trích xuất tự động cho mọi website. `build_pilot.py` chỉ khởi tạo khi chưa có dữ liệu, để tránh ghi đè hồ sơ đã bổ sung.

Hồ sơ cập nhật20/10/2026: [Growlab — có Thuế, cây giống vật lý, đạt sàng lọc](research/startups/GROWLAB.md), [Plantner — sản phẩm vật lý, chờ pháp nhân/Thuế](research/startups/PLANTNER.md), [BUYO Việt Nam — đã đối chiếu Thuế, đạt cửa sàng lọc](research/startups/BUYO.md), [Olinno — có Thuế, chờ chủ nguồn hoạt động thứ hai](research/startups/OLINNO.md), [MEDCAT — đã đối chiếu Thuế, đạt cửa sàng lọc](research/startups/MEDCAT.md), [AquaX / ST Software — có Thuế, chờ hoạt động đúng pháp nhân](research/startups/AQUAX.md), [VORIA SOLUTION — Thuế đang hoạt động và giới hạn sản phẩm](research/startups/VORIA_SOLUTION.md), [NAISCORP Robotics — nguồn, Thuế và giới hạn](research/startups/NAISCORP_ROBOTICS.md), [TENSOR/EggVision — đang chờ Thuế và mapping](research/startups/TENSOR_EGGVISION.md). Hiện12/50 đạt (11 có Thuế trực tiếp, 1 dùng TVPL thay thế theo quyền người dùng20/10), 356 bản ghi bằng chứng; toàn bộ57 ứng viên có trong bảng sàng lọc, không gọi tất cả là đã duyệt.

Rà soát tiếp: [VEEP — mô hình AIoT/EEaaS, chờ MST mẹ và Thuế](research/startups/VEEP.md).

[AIZ — phần mềm dữ liệu/AI Agent và các nguồn hoạt động](research/startups/AIZ.md), vẫn chờ MST mẹ và Thuế chính thức.

[OpenMind Robotics Việt Nam — tích hợp robotics và báo cáo đối tác](research/startups/OPENMIND_ROBOTICS.md), ứng viên mới, chờ MST mẹ/Thuế.

[ANTAJA và Fillsonic — các điểm chưa xác minh](research/startups/ANTAJA_FILLSONIC.md): concept/R&D và trang Coming Soon chưa đủ vượt cửa sản phẩm.

[BRAIN-LIFE và FIZIBOX — thiết bị, công báo SHTT và hoạt động meetup](research/startups/BRAINLIFE_FIZIBOX.md), còn thiếu đối chiếu pháp nhân/Thuế.

[FUTURE SPACE TECHNOLOGY — catalogue drone và các điểm còn thiếu](research/startups/FUTURE_SPACE_TECHNOLOGY.md), chưa xác minh MST/Thuế, startup và hoạt động độc lập.

[MEDCAT — phần mềm AI tài liệu, giải thưởng và hoạt động hệ sinh thái](research/startups/MEDCAT.md), chờ MST mẹ/Thuế; chưa gộp pháp nhân TPA.

[HEALTHBRIDGE AI và HITEK — sản phẩm và các quan hệ pháp nhân chưa đối chiếu](research/startups/HEALTHBRIDGE_HITEK.md), tiếp tục chờ Thuế và hoạt động độc lập đủ ngày.

[OLOGN / NAWI — mẫu thử và hoạt động gần đây](research/startups/OLOGN.md), chờ MST mẹ/Thuế; chưa xác minh triển khai cứu hỏa hoặc chứng nhận an toàn.

[UDATA — nền tảng AIoT, PDF gateway và các thỏa thuận](research/startups/UDATA.md), chờ MST mẹ/Thuế; chưa xác nhận giải ngân hoặc nghiệm thu.

[VIZION — phần mềm 3D/AI Inventory và các mốc chưa đủ](research/startups/VIZION.md), chờ MST mẹ/Thuế và hoạt động độc lập đủ ngày.

[VORIA SOLUTION — VoriaCare/Hub, triển lãm và giới hạn ICU](research/startups/VORIA_SOLUTION.md), chờ MST mẹ/Thuế; chưa kiểm nghiệm bảo mật hoặc hiệu quả lâm sàng.

## Trạng thái thực tế

Ngày 06/10/2026: 457 doanh nghiệp v1, 220 doanh nghiệp B2B, hợp nhất 457 doanh nghiệp; 20 sản phẩm; 2.031 liên kết tài liệu, gồm 371 PDF. Số lượng có thể thay đổi theo nguồn.

Đã ghi Sheet qua connector và đối chiếu bốn tab dữ liệu: 0 ô sai lệch. Đã đọc một PDF mẫu qua ảnh scan. Chưa chạy sync độc lập với credential, chưa cấu hình OCR, chưa đọc toàn bộ PDF hoặc bật lịch tự động.

Repo chưa khai báo giấy phép sử dụng. Snapshot, PDF và credential không thuộc gói mã nguồn. Dữ liệu nguồn tuân theo điều kiện của đơn vị cung cấp.

Nguồn trạng thái doanh nghiệp: ưu tiên cổng Thuế; khi tra cứu thất bại, người dùng cho phép Thư Viện Pháp Luật thay thế từ20/10/2026. Loại tax_secondary lưu riêng, bắt buộc lý do fallback; Sheet đánh dấu TVPL nguồn thay thế. Không áp dụng tự động cho FiinGate hoặc danh bạ khác.

[AirX Carbon / Veritas Việt Nam](research/startups/AIRX.md): đã nối thương hiệu/pháp nhân, chờ kết quả trạng thái doanh nghiệp.
