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

## Bộ startup — 15/10/2026

- [x] Ghi nhận lượt tra cứu VORIA ngày19/10: cổng Thuế từ chối hai mã xác nhận; giữ pending, chờ ảnh kết quả chính thức, không tính lỗi CAPTCHA như bằng chứng trạng thái.
- [x] Thu thập snapshot và thiết lập cửa sàng lọc Thuế/bằng chứng hoạt động.
- [x] Ghi 57 hồ sơ, 302 bản ghi bằng chứng (gồm bản giữ ngoài duyệt) và 7 hồ sơ đạt vào ba tab startup của Sheet.
- [x] Rà soát VORIA: tên nhà cung cấp, app/Hub, triển lãm SIHUB và cập nhật ứng dụng; ghi giới hạn ICU/bảo mật, chờ MST mẹ/Thuế.
- [x] Rà soát VIZION: đối chiếu tên người sáng lập với shortlist, Smart3DTour/AIInventory; không tính ngày cập nhật cũ trên bản web store vào hoạt động gần đây.
- [x] Rà soát UDATA: đọc catalogue PDF gốc19 trang/xem trang12 gateway; đối chiếu BK Fund và MOU BKE, chờ MST mẹ/Thuế.
- [x] Rà soát OLOGN/NAWI: mẫu thử còn chuẩn bị thử nghiệm, báo cáo R&D và sự kiện HUTECH khác nguồn/ngày; chờ MST mẹ/Thuế.
- [x] Rà soát HEALTHBRIDGE AI/HITEK: phân loại đầu ra, ghi tên pháp nhân còn mâu thuẫn; không gán MST cùng tên hoặc ngày sự kiện chưa chắc chắn.
- [x] Rà soát MEDCAT: phần mềm IDUS/Nexus, giải Digital Startup và chứng nhận hệ sinh thái Hà Nội; chờ MST mẹ/Thuế, tách MedCAT TPA.
- [x] Rà soát FST: catalogue drone, tên tự công bố và ngữ cảnh nợ phí đấu thầu; giữ Chờ các cửa còn thiếu.
- [x] Rà soát BRAIN-LIFE/FIZIBOX, đọc công báo SHTT và báo cáo meetup; giữ Chờ phần pháp nhân/Thuế còn thiếu.
- [x] Rà soát ANTAJA/Fillsonic; giữ sản phẩm chưa xác minh ngoài duyệt, không suy triển khai từ concept/Coming Soon.
- [x] Bổ sung OpenMind Robotics Việt Nam, phân biệt công ty nước ngoài, xác nhận báo cáo tích hợp Gradion; giữ Chờ MST mẹ/Thuế.
- [x] Bổ sung AIZ: sản phẩm phần mềm và3 hoạt động khác nguồn; giữ Chờ MST mẹ/Thuế, không gán kết quả BHXH cùng tên chưa khớp pháp nhân.
- [x] Bổ sung VEEP, xác định mô hình hybrid, tách MST mẹ ứng viên khỏi văn phòng đại diện/NTNN; giữ Chờ Thuế.
- [x] Bổ sung hồ sơ TENSOR/EggVision, phân biệt75% thử nghiệm ban đầu với mục tiêu thương mại; giữ Chờ khi chưa xác minh Thuế/mapping.
- [x] Hoàn tất hồ sơ NAISCORP Robotics, đối chiếu Thuế chính thức0402268582 và công bố nguồn/giới hạn.
- [x] Đối chiếu giá trị các vùng đã ghi; các lượt xem giao diện và giới hạn được ghi trong PROGRESS.
- [ ] Hoàn tất duyệt 50 startup theo đủ điều kiện; hiện đạt 7.
- [ ] Audit đầy đủ danh sách 50 trước khi bàn giao hoàn chỉnh.
