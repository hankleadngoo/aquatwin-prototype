# Chuẩn bị bản xem chung

Trạng thái: chờ xác nhận quyền tải snapshot thật và danh sách người xem, chưa push hoặc deploy.

- Giữ project_id appgprj_6af7e4ee4af8819192f772c1a2ac5be5, không tạo Site mới.
- Hiện có audience custom; các lựa chọn máy chủ cung cấp là custom và public, không có workspace_all.
- Không thay đổi audience trước khi người dùng xác định người được xem.
- Asset dữ liệu hiện có chứa 1.333 bản ghi trại thực. Chưa được đưa lên vì automatic approval review yêu cầu xác nhận payload rõ ràng.
- Có thể thay bằng dữ liệu synthetic được ghi nhãn rõ nếu người dùng chọn; không gọi synthetic là quan trắc thật.
- Bản hosting là static. Không chạy server.py trên Cloudflare và không kết nối gateway localhost của từng người xem.
- Nhật ký và khoảng thử dùng localStorage riêng cho mỗi người/trình duyệt, không phải nhật ký cộng tác dùng chung.
- Cấu hình browser QA, .runtime, credential và file VPN không được đóng gói.
- Lần cuối kiểm tra: node tests.cjs; python -m unittest test_bridge.py; kiểm tra cú pháp các file JS.
- Sau khi được xác nhận: source helper mở/push đúng repo; package asset từ đúng commit; save/deploy; kiểm tra trạng thái deployment; cấu hình audience đúng danh sách được yêu cầu.
