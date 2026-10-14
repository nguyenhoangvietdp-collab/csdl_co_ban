# CSDL CƠ BẢN — cấu trúc và cách hoạt động

Ngày mô tả: 06/10/2026.

Sheet đích được cấu hình qua biến môi trường `GOOGLE_SHEET_ID`. Sơ đồ dưới đây mô tả lần triển khai ngày 06/10/2026.

## Sơ đồ cây dữ liệu hiện có

```text
CSDL CƠ BẢN (Google Sheet)
├── Doanh_nghiep — 457 bản ghi, 27 cột
│   ├── Khóa: ID doanh nghiệp từ nguồn
│   ├── Nhận diện: tên, mã số thuế, tên tiếng Anh, loại hình
│   ├── Hoạt động: địa chỉ, mã địa phương, ngành, vốn, lao động
│   ├── Liên hệ: điện thoại, email, website, người đại diện
│   └── Truy vết: nguồn v1/B2B, URL hồ sơ, cập nhật nguồn, lúc thu thập
├── San_pham_dich_vu — 20 bản ghi, 11 cột
│   ├── Khóa: ID sản phẩm/dịch vụ từ nguồn
│   ├── Nội dung: tên, nhu cầu mua/bán, mô tả, thẻ tìm kiếm
│   ├── Phạm vi: thị trường, từ ngày, đến ngày
│   └── Truy vết: URL nguồn, cập nhật nguồn, lúc thu thập
├── Tai_lieu — 2.031 bản ghi, 10 cột
│   ├── Khóa: ID tài liệu
│   ├── Chủ thể: loại chủ thể + ID doanh nghiệp/sản phẩm
│   ├── Tệp: tên, URL nguồn, dung lượng, loại file
│   ├── Xử lý: trạng thái đọc, lúc thu thập
│   └── URL Drive: cột dự phòng; dừng tải lên Drive
├── PDF_Tom_tat — 16 bản ghi, 7 cột
│   ├── Liên kết: ID tài liệu + ID doanh nghiệp
│   ├── Nội dung: trường thông tin + giá trị đọc từ PDF
│   └── Bằng chứng: trang PDF, phương pháp, URL nguồn
├── Nhat_ky — 5 bản ghi, 5 cột
│   └── Thời điểm, nguồn, số bản ghi, tổng tại nguồn, trạng thái
└── Trang tính1 — tab gốc được giữ lại
```

Số lượng trên không tính dòng tiêu đề. Trong Tai_lieu có 371 liên kết PDF. PDF_Tom_tat hiện chỉ chứa kết quả đọc một PDF mẫu, gồm cả trạng thái xử lý.

## Quan hệ giữa các tab

- Một doanh nghiệp có nhiều tài liệu: Tai_lieu loại chủ thể `Doanh nghiệp`, ID chủ thể bằng Doanh_nghiep.ID.
- Một sản phẩm có nhiều tài liệu: Tai_lieu loại chủ thể `Sản phẩm`, ID chủ thể bằng San_pham_dich_vu.ID.
- Một tài liệu có nhiều thông tin trích xuất: PDF_Tom_tat.ID tài liệu bằng Tai_lieu.ID tài liệu.
- Doanh_nghiep.ID liên kết với PDF_Tom_tat.ID doanh nghiệp.
- San_pham_dich_vu chưa có cột ID doanh nghiệp. Chưa thể nối sản phẩm với doanh nghiệp bằng khóa đã lưu.
- Sheet không tự cưỡng chế khóa chính hoặc khóa ngoại. Các khóa trên là quy ước của dữ liệu.

## Sơ đồ cây hoạt động

```text
Chu kỳ cập nhật thủ công
├── 1. Thu thập: crawl.ps1
│   ├── Danh sách doanh nghiệp v1, doanh nghiệp B2B, sản phẩm
│   └── Đọc đủ phân trang; kiểm tra số lượng và ID
├── 2. Chuẩn hóa: prepare_sheet.py
│   ├── Hợp nhất doanh nghiệp v1/B2B theo ID
│   ├── Làm sạch mô tả; giữ mã số thuế và ID dạng chuỗi
│   └── Lập chỉ mục tài liệu; khử trùng lặp theo ID tài liệu
├── 3. Đọc PDF được chọn
│   ├── PDF có chữ: trích xuất văn bản
│   ├── PDF scan: đọc ảnh trang; OCR cần cấu hình thêm
│   └── Ghi thông tin quan trọng kèm trang và phương pháp vào PDF_Tom_tat
├── 4. Ghi dữ liệu vào các tab quản lý
│   ├── Đã thực hiện bằng connector Google Sheets
│   └── sync_sheet.py là phương án chạy lại, cần cấu hình quyền truy cập
├── 5. Đọc lại và đối chiếu dữ liệu
│   └── Lần hiện tại: bốn tab dữ liệu không có ô sai lệch
└── 6. Người dùng khai thác Sheet
    ├── Lọc doanh nghiệp theo ngành, địa phương, nguồn
    ├── Tra tài liệu theo loại chủ thể và ID
    ├── Lọc PDF, trạng thái đọc; mở URL nguồn
    └── Đọc tóm tắt và kiểm tra trang PDF dẫn chứng
```

## Quy tắc vận hành

- Các tab dữ liệu do crawler quản lý là bản chụp nguồn của lần chạy. Chạy lại có thể ghi đè nội dung đã sửa tay và xóa các dòng dư trong phạm vi cột quản lý.
- Ghi chú người dùng nên đặt trong một tab riêng. Tab ghi chú này chưa được tạo.
- Nhật ký hiện là bản tổng hợp lần chạy, chưa phải lịch sử tích lũy nhiều lần.
- Không suy diễn các mã địa phương thành tên nếu chưa có bảng đối chiếu.
- Thông tin PDF là kết quả đọc tài liệu, không tự thay thế dữ liệu doanh nghiệp tại nguồn.
- Chưa bật lịch tự động; chưa đọc toàn bộ PDF; chưa cấu hình OCR tự động.
- Google Sheet là đầu ra chính. Drive chỉ giữ định hướng lưu trữ, không tiếp tục tải tệp lên.

## Bộ startup đã triển khai — 14/10/2026

```text
CSDL CƠ BẢN
├── Startup_Danh_sach — 56 hồ sơ, 13 cột
│   ├── Khóa: Mã hồ sơ S001…; thương hiệu và pháp nhân giữ riêng
│   ├── MST mẹ: chữ, không bỏ số 0 đầu; không thay bằng MST chi nhánh
│   ├── Sàng lọc: đầu ra vật lý, kết quả, điều kiện còn thiếu
│   └── Truy vết: ngày bộ lọc, ngày/trạng thái Thuế, nguồn và giới hạn
├── Startup_Dat — công thức lọc từ Startup_Danh_sach
│   ├── Hiện có 6 hồ sơ đạt; mục tiêu 50 chưa hoàn tất
│   └── Tự phản ánh bảng nguồn; không tự tra Thuế hoặc duyệt chứng cứ
└── Startup_Bang_chung — 170 bản ghi, 13 cột
    ├── Khóa: Mã bằng chứng; khóa nối: Mã hồ sơ → Startup_Danh_sach
    ├── Nội dung: loại bằng chứng, chủ nội dung, URL nguồn
    ├── Ngày: sự kiện, công bố, thu thập, kiểm tra Thuế giữ riêng
    └── Đánh giá: giữ ngoài duyệt hoặc hợp lệ theo kiểm tra; xem giới hạn
```

`prepare_startup_sheet.py` xuất các yêu cầu ghi ô; connector gửi vào workbook đã đọc metadata. ID hiện tại: danh sách 1006, đạt 1007, bằng chứng 1008. Không dùng ID này cho workbook khác khi chưa ánh xạ. Không ghi đè chỉnh sửa thủ công khi chưa đối chiếu dữ liệu.

`Startup_Dat!A2` dùng FILTER theo nhãn “Đạt”, phủ tới dòng 1000. Các điều kiện Thuế, ngày và bằng chứng được xét ở bộ lọc trước khi ghi bảng nguồn; đổi nhãn thủ công không thay thế xác minh. Nguồn thuộc cùng chủ nội dung hoặc cùng sự kiện không được tính thành hai nguồn hoạt động khác nhau. “Hợp lệ theo kiểm tra” chỉ nói bản ghi qua cửa kỹ thuật và review, không chứng minh mọi tuyên bố của nguồn đúng.

## Mở rộng đề xuất — chưa triển khai

```text
CSDL CƠ BẢN
├── Ghi_chu_nguoi_dung
│   └── Loại chủ thể, ID chủ thể, ghi chú, người cập nhật, thời điểm
├── Danh_muc
│   └── Bảng đối chiếu mã địa phương, ngành, trạng thái đọc
└── Lich_su_chay
    └── ID lần chạy, thời điểm, nguồn, số lượng, lỗi
```
