# Tiến độ

Cập nhật 06/10/2026, giờ Việt Nam.

## Hoàn thành

- [x] Xác định API và bộ lọc của hai giao diện công khai.
- [x] Chạy crawler: 457 doanh nghiệp v1, 220 doanh nghiệp B2B, 20 sản phẩm.
- [x] Hợp nhất 457 doanh nghiệp; lập chỉ mục 2.031 tài liệu, gồm 371 PDF.
- [x] Ghi năm tab Sheet qua connector; đối chiếu bốn tab dữ liệu, 0 ô sai lệch.
- [x] Đọc một PDF mẫu gồm 8 trang scan, trang cuối trống; ghi 16 mục có dẫn chứng.
- [x] Viết công cụ chuẩn hóa, đồng bộ và xử lý PDF.
- [x] Mô tả sơ đồ cây, quan hệ và quy tắc cập nhật.
- [x] Chuẩn bị cấu hình, dependency, mẫu dữ liệu và template GitHub.

## Phạm vi

Google Sheet là đầu ra chính. Dừng upload Drive theo yêu cầu người dùng. Các folder đã tạo chỉ là định hướng. Upload PDF trước đó thất bại do hết dung lượng; không có PDF upload thành công.

## Việc còn lại

- [ ] Chạy sync_sheet.py bằng credential ngoài Codex.
- [ ] Cấu hình Tesseract và kiểm tra OCR tiếng Việt.
- [ ] Đọc và kiểm tra toàn bộ PDF.
- [ ] Bổ sung khóa nối sản phẩm với doanh nghiệp nếu nguồn cung cấp.
- [ ] Tạo tab ghi chú và danh mục.
- [ ] Lưu lịch sử chạy, checkpoint và phục hồi lỗi.
- [ ] Bật lịch định kỳ nếu được yêu cầu.

Chưa có lịch tự động hoặc CI chạy crawler.

## Bộ startup — 14/10/2026

- [x] Thu thập snapshot và thiết lập cửa sàng lọc Thuế/bằng chứng hoạt động.
- [x] Ghi 56 hồ sơ, 181 bằng chứng và 6 hồ sơ đạt vào ba tab startup của Sheet.
- [x] Đối chiếu toàn bộ vùng đã ghi và xem cách hiển thị trên Google Sheets.
- [ ] Hoàn tất duyệt 50 startup theo đủ điều kiện; hiện đạt 6.
- [ ] Audit đầy đủ danh sách 50 trước khi bàn giao hoàn chỉnh.
