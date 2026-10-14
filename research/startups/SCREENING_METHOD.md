# Phương pháp duyệt startup

## Mục tiêu giữ nguyên

Xây công cụ thu thập và duyệt đủ 50 startup có pháp nhân Việt Nam, đang hoạt động, có sản phẩm công nghệ cao hoặc đổi mới sáng tạo. Ưu tiên sản phẩm vật lý. Danh sách nguồn gồm quỹ đầu tư, chính phủ và cuộc thi; dữ liệu thuế và hoạt động phải được kiểm tra riêng.

## Các cửa kiểm tra

1. **Định danh:** thương hiệu, tên pháp nhân và MST công ty mẹ 10 chữ số phải được nối bằng nguồn đã đọc. Không đếm chi nhánh hoặc hai thương hiệu của cùng một pháp nhân thành hai công ty.
2. **Thuế:** kết quả trực tiếp trên miền gdt.gov.vn, đúng MST và pháp nhân, kiểm tra trong 30 ngày. Chỉ nhận nhãn chính xác `NNT đang hoạt động` hoặc `NNT đang hoạt động (đã được cấp GCN ĐKT)`. Nhãn khác, mất địa chỉ, ngừng hoặc mâu thuẫn đều chờ xử lý.
3. **Nguồn phát hiện:** ít nhất một công bố có ngày từ quỹ, chính phủ hoặc ban tổ chức cuộc thi trong 730 ngày. Website portfolio không có ngày không tự chứng minh tính gần đây.
4. **Startup:** nguồn thể hiện giai đoạn khởi nghiệp hoặc scale-up, không tự coi mọi công ty công nghệ hay công ty con tập đoàn là startup.
5. **Công nghệ và sản phẩm:** có sản phẩm hoặc prototype chức năng cùng cơ chế đổi mới/R&D cụ thể. Danh xưng AI hoặc bài PR chưa đủ. Chứng nhận doanh nghiệp công nghệ cao là trường riêng; chưa có chứng nhận không được ghi là đã được Nhà nước chứng nhận.
6. **Hoạt động:** ít nhất hai tín hiệu trong 365 ngày, khác đơn vị xuất bản và khác nguồn gốc sự kiện. Ưu tiên triển khai/sản xuất/bán hàng/khách hàng xác nhận; các tín hiệu tuyển dụng, gọi vốn, chứng nhận chỉ có giá trị hỗ trợ. Bài đăng lại một thông cáo không phải hai bằng chứng độc lập.
7. **Phản chứng:** tìm ngừng kinh doanh, giải thể, website đóng cửa, sản phẩm bị rút hoặc pháp nhân đổi tên. Bằng chứng phản đối chưa được giải quyết giữ công ty ở trạng thái pending.

Cờ chất lượng nguồn (`source_integrity_flag`) chưa có giải trình đối chiếu (`resolution`) cũng giữ hồ sơ chờ. Nội dung không liên quan trên website không tự chứng minh doanh nghiệp ngừng hoạt động. Bằng chứng PDF giữ cả hash văn bản lẫn hash tệp gốc; số trang giúp người duyệt đối chiếu. Ngày chỉ có năm được xét bằng toàn khoảng 01/01–31/12, không gán ngày chính xác giả.

Khi bảng Thuế có nhiều chi nhánh, trích đúng hàng MST mẹ 10 chữ số. MST xuất hiện ở dạng tiền tố của `MST-001` không đủ. Tên pháp nhân, MST và nhãn trạng thái phải nằm trong trích đoạn được duyệt, ngoài kiểm tra snapshot gốc. Chi nhánh chấm dứt MST không tự làm công ty mẹ bị loại.

Tín hiệu hoạt động phải ghi rõ loại: triển khai tự công bố, công bố thương mại, ưu đãi đối tác đang hiển thị, chương trình tài trợ có trạng thái active, hoặc mốc R&D/hành chính. Ngày quan sát trạng thái hiện tại không được trình bày thành ngày bắt đầu chương trình. Trúng thầu không chứng minh đã ký hợp đồng, bàn giao hoặc nghiệm thu. Ngày công bố bản mô tả sáng chế không được đổi thành ngày cấp bằng hoặc ngày triển khai sản phẩm.

Các ngưỡng 30/365/730 ngày là chính sách sàng lọc của dự án, không phải quy định pháp luật. Trạng thái thuế tại thời điểm tra cứu không bảo đảm công ty hoạt động liên tục trong tương lai.

## Ưu tiên physical

`yes`: thiết bị, robot, cảm biến, vật liệu, kit sinh học, năng lượng hoặc sản phẩm vật lý do startup phát triển. `hybrid`: phần mềm có phần cứng/sản phẩm vật lý tích hợp. `no`: đầu ra phần mềm thuần túy. Chỉ xếp hạng sau khi qua mọi cửa; không dùng ưu tiên physical để bỏ qua kiểm tra thuế.

## Evidence ledger

`data/startups/candidates.csv`: id, brand, legal_name, tax_id, country, physical, website, discovery_url, notes.

`data/startups/evidence.jsonl`: mỗi dòng một bằng chứng, có id, company_id, kind, quote, url, snapshot, sha256, publisher_owner, retrieved_at, reviewed, reviewer. Thêm published_at/source_type cho discovery; event_date/origin_id cho activity; tax_id/legal_name/status/checked_at cho tax.

Các kind: discovery, identity, startup, technology, product, activity, tax, negative_activity. `reviewed=true` chỉ sau khi đọc và đối chiếu ngữ nghĩa. Hash chỉ chứng minh snapshot không đổi; không chứng minh nguồn nói thật. URL và quote cũng không thay thế review.

`counter_review` lưu xác nhận review phản chứng: search_queries (ít nhất hai truy vấn), review_note và bằng chứng đã đọc. Đây là bản ghi phán đoán của reviewer; snapshot tham chiếu không tự chứng minh rằng không có tin đóng cửa. Thiếu review này thì chưa duyệt.

## Sharpness Ledger áp dụng cho tiêu chí

Đây là tác vụ sàng lọc doanh nghiệp, không phải đề cương kiểm định giả thuyết. Không tạo giả thuyết khoa học hoặc chạy schema G/H/C giả.

| Tiêu chí | Nhận định | Quyết định |
|---|---|---|
| Nối thương hiệu với MST | Accuracy fix: tránh kiểm tra nhầm pháp nhân | Bắt buộc |
| Thuế chính thức và hoạt động thực tế | Sharper theo mục tiêu tác vụ: tách trạng thái pháp lý khỏi hoạt động sản phẩm | Giữ cả hai |
| Physical | Depends: ưu tiên xếp hạng phù hợp; lọc tuyệt đối sẽ thu hẹp yêu cầu chưa được xác nhận | Ưu tiên, không bắt buộc |
| Follower và website còn mở | Broader: không chứng minh sản phẩm hoặc doanh nghiệp đang vận hành | Chỉ là đầu mối |
| Chứng nhận công nghệ cao | Depends: có giá trị xác nhận riêng; bắt buộc sẽ thay đổi phạm vi startup đổi mới | Ghi riêng khi có nguồn |

Không kiểm tra novelty của phương pháp hoặc chạy checker dành cho giả thuyết nghiên cứu. Không tuyên bố phương pháp mới.

## Epistemic Guard

Review một lượt theo từng công ty: supported / contradicted / unverified. Không tự nâng lead lên approved khi thiếu thuế. Chưa có 50 công ty qua toàn bộ cửa thì mục tiêu chưa hoàn thành. Danh sách pending là hàng đợi nghiên cứu, không phải khuyến nghị đầu tư.

## Chạy

```powershell
python startup_tool.py fetch --sources startup_sources.json
python startup_tool.py screen --as-of YYYY-MM-DD
python -m unittest discover -s tests -p test_startup_tool.py
```

Kết quả gồm screening.csv, approved_50.csv, screening_summary.json trong data/startups. Không ghi Sheet hoặc tải Drive từ script này. Giai đoạn tích hợp Sheet dùng tab riêng sau khi có dữ liệu được kiểm tra.

`approved`: đủ cửa theo chính sách. `pending`: thiếu hoặc chưa rõ bằng chứng. `excluded_tax_entity`: pháp nhân/MST đã kiểm tra không có trạng thái thuế hoạt động, hoặc kết quả thuế mâu thuẫn. Trạng thái loại chỉ áp dụng cho pháp nhân/MST trong dòng; không kết luận toàn bộ thương hiệu hay pháp nhân khác đóng cửa.

Nguồn chỉ có tháng dùng `YYYY-MM`; bộ lọc yêu cầu toàn bộ tháng nằm trong cửa sổ thời gian. Không tự gán ngày chính xác. Snapshot HTML mới lưu kèm hash nội dung trong tên để tránh ghi đè bằng chứng cũ.

Collector HTML không chạy JavaScript, không đọc ảnh/PDF, không giải CAPTCHA và không tự hiểu tiêu chí sản phẩm. Nội dung ảnh cần đọc riêng; lỗi TLS không được bỏ qua. Nguồn timeout cần đọc bằng trình duyệt hoặc chờ truy cập lại.
