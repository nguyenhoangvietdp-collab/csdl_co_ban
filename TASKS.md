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

## Bộ startup — 19/10/2026

- [x] Rà Olinno: Thuế0401950376 đang hoạt động; phân biệt nhà phát triển tiện ích với enfue JSC, dùng ngày10Sep từ snapshot trực tiếp. Thêm11 bản ghi, Sheet169 ô khớp; chờ nguồn hoạt động thứ hai. Tổng329 bằng chứng, vẫn9 đạt.
- [x] Đối chiếu Thuế MEDCAT MST0110578065 đang hoạt động, giữ TPA riêng; thêm1 bản ghi, đồng bộ Sheet dòng27/bằng chứng319. Đọc lại143 ô khớp, FILTER9 mã. Tổng318 bằng chứng, 9 đạt, 47 chờ, 1 loại pháp nhân Thuế.
- [x] Rà AquaX/STSoftware: thêm13 bản ghi; Thuế MST0402112987 đang hoạt động, giữ các pháp nhân khác riêng. Bài triển lãm ghi Công ty Cổ phần AQUAX chưa nối STSoftware, chưa dùng làm hoạt động; hồ sơ chờ. Sheet đọc lại195 ô khớp. Tổng317 bằng chứng, vẫn8 đạt.
- [x] Sau lượt lỗi CAPTCHA VORIA, đọc bảng Thuế do người dùng hoàn thành: MST3604052503, pháp nhân VORIA SOLUTION, NNT đang hoạt động. Thêm2 bản ghi, chạy sàng lọc19/10 và đồng bộ Sheet: 57 hồ sơ, 304 bằng chứng, 8 đạt, 48 chờ, 1 loại pháp nhân Thuế. Đọc lại767 ô khớp và xem ba vùng hiển thị liên quan.
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

- [x] Hoàn thiện BUYO Việt Nam: Thuế mẹ0110114634 đang hoạt động20/10, tách chi nhánh/Singapore; Sheet thêm S056 vào danh sách đạt. Tổng330 bằng chứng,10/50 đạt,46 chờ,1 loại pháp nhân Thuế. Ledger chọn lọc84/84 quote khớp; xem hồ sơ BUYO.

- [x] Rà Plantner: thêm7 bản ghi, xếp Vật lý; giữ riêng tên Cổ phần/TNHH và nhóm Hàn Quốc. Sheet104 ô khớp, tổng337 bằng chứng/10 đạt; còn pháp nhân/MST/Thuế.

- [x] Hoàn thiện Growlab: MST0318576613 Thuế đang hoạt động20/10, cây giống vật lý, thêm8 bằng chứng. Sheet117 ô khớp, FILTER11 mã; tổng345 bằng chứng/11 đạt. Chưa xác minh năng suất hoặc bằng sáng chế.

- [x] Rà bổ sung OpenMind20/10:3 bản ghi công nghệ/ứng dụng/giới hạn tin KUKA. Ba CAPTCHA bị từ chối, chưa có Thuế; Sheet52 ô khớp. Tổng348 bằng chứng/11 đạt, tiếp tục chờ MST mẹ.

- [x] Nhận ảnh OpenMind TVPL và quyền dùng nguồn thay thế20/10; cập nhật tiêu chí/validator/export, ghi riêng tax_secondary. OpenMind đạt với nhãn TVPL;12/50 đạt,349 bằng chứng. Sheet26 ô khớp/12 mã, không gọi đây là kết quả Thuế trực tiếp.

- [x] Đối chiếu OLOGN qua TVPL: đúng MST0316563337 nhưng danh sách ghi ORCO; chi tiết chưa đọc được sau quyền CAPTCHA vì công cụ không nhấp được. Ghi1 phản chứng/Sheet26 ô khớp,350 bằng chứng/12 đạt; không tự gộp tên hoặc suy trạng thái.

- [x] Rà AirX/Veritas20/10: thêm3 bản ghi, nối thương hiệu/pháp nhân, phân biệt chi nhánh-001. GDT hai CAPTCHA từ chối, TVPL chi tiết chưa đọc được trạng thái; Sheet52 ô khớp. Tổng353 bằng chứng/12 đạt; còn cửa trạng thái.

- [x] Bổ sung UDATA20/10: ảnh chứng nhận Uboard/pháp nhân không có MST, ngữ cảnh Ugate/phạm vi logo tiêu chuẩn. Hai MST ứng viên vẫn chưa chọn; quyền CAPTCHA đang chờ, chưa gửi. Sheet52 ô khớp, tổng356 bằng chứng/12 đạt.

- [x] Rà FASTDO20/10:7 bản ghi mới, tên pháp nhân/MST tự công bố0401799975, xếp Phi vật lý. DAVAS2025 ngoài365ngày, một lời chào dịch vụ gần đây; còn Thuế/chủ nguồn thứ hai. Sheet104 ô khớp, tổng363 bằng chứng/12 đạt.

- [x] Đọc PDF Plantner gốc đính kèm CTU:3trang/513588byte, xem trang2. Bên tuyển Hàn Quốc, lập công ty Việt Nam còn dự kiến tại thời điểm tài liệu; không gán tiêu đề Cổ phần thành pháp nhân Việt Nam. Sheet26 ô khớp,364 bằng chứng/12 đạt.

- [x] Rà giới hạn NHTC20/10:3 bản ghi về demo AI/đơn sáng chế/giai đoạn doanh nghiệp. Sheet52 ô API khớp, UI chụp lỗi nên chưa xác nhận trực quan;367 bằng chứng/12 đạt. Còn Thuế/startup/chủ nguồn hoạt động thứ hai.
