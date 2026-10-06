# Báo cáo vấn đề bảo mật

Không đăng credential hoặc dữ liệu nhạy cảm trong issue công khai. Nếu repo có bật GitHub Private vulnerability reporting, dùng mục Security để báo riêng. Nếu chưa bật, liên hệ chủ repo qua kênh riêng đã biết.

Nếu token hoặc khóa đã lộ: thu hồi hoặc xoay khóa trước; xóa khỏi Git history nếu cần. `.gitignore` không xóa bí mật đã được commit.

Ứng dụng đọc API công khai và ghi vào Sheet được chỉ định. Chỉ cấp quyền cần thiết cho tài khoản đồng bộ. Dữ liệu nguồn, PDF, ảnh render và thông tin xác thực không thuộc gói mã nguồn.
