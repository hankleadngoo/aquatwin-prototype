# AquaTwin 1.1 — cập nhật theo ditto-examples

## 1. Chức năng mới

Màn hình **Kết nối Eclipse Ditto** có: kiểm tra gateway/credentials, tạo Policy và Thing còn thiếu, đồng bộ snapshot đang chọn, đọc Thing từ Ditto, xuất Policy/MQTT connection/Ditto Protocol. Không cung cấp live message hoặc actuator commands.

Gateway Python chuẩn thư viện chạy cùng origin với UI; không lưu tài khoản vào browser. Cho phép Ditto loopback (localhost/127.0.0.1/::1), không tự xuất dữ liệu ra server ngoài. Raw data và lịch sử vẫn ở file, không bị sửa.

## 2. Chạy ngay khi chưa có Ditto

Nhấp `Mo_AquaTwin.cmd`, mở http://127.0.0.1:8765/#ditto, bấm Kiểm tra kết nối. Nếu chưa cấu hình, phải hiện “Chưa cấu hình”, nút đồng bộ bị vô hiệu hóa. Những phần quan trắc, QC, replay và nhật ký vẫn chạy.

Máy chưa có Docker ở lần kiểm tra. Bản cập nhật KHÔNG cài Docker hoặc giả lập dịch vụ Ditto thành thật.

## 3. Khi đã có máy chủ Ditto tại máy này

1. Chọn bản phát hành Ditto phù hợp và chạy theo hướng dẫn chính thức. Không dùng ví dụ cũ làm cam kết tương thích mọi phiên bản: https://eclipse.dev/ditto/installation-running.html . Nhóm tự cấu hình xác thực/Policy; không đưa máy chủ ra Internet bằng mật khẩu mẫu.
2. Dừng AquaTwin bằng `powershell -File stop-app.ps1` trong cửa sổ có quyền với process đã khởi tạo.
3. Cấu hình môi trường của phiên chạy: DITTO_URL (ví dụ http://127.0.0.1:8080), DITTO_TOKEN hoặc cặp DITTO_USER/DITTO_PASSWORD. DITTO_SUBJECT phải là subject mà Ditto đã xác thực, ví dụ nginx:tên_người_dùng khi triển khai nginx basic auth. Không đưa credential vào Git, file ghi chú hoặc giao diện.
4. Chạy `python server.py` hoặc `Mo_AquaTwin.cmd` từ phiên có môi trường trên. Nếu server cũ vẫn chạy, phải dừng rồi mở lại để đọc cấu hình mới.
5. Vào #ditto, Kiểm tra kết nối. Thing chưa tồn tại thì dùng Khởi tạo phần chưa có; gateway dùng If-None-Match để tránh ghi đè. Policy hiện hữu không bị sửa.
6. Chọn timestamp bằng màn hình Tổng quan; vào #ditto và Đồng bộ snapshot sau QC. Gateway dựng snapshot từ dataset được đóng gói, không chấp nhận payload tùy ý từ browser.
7. Gateway GET trước, so sourceTime, dùng ETag/If-Match rồi GET xác minh; không cho đồng bộ snapshot cũ hơn. Snapshot giống nhau được bỏ qua. Ditto không trả ETag thì từ chối cập nhật để tránh ghi đè cạnh tranh.
8. Đọc Thing trực tiếp để đối chiếu observed, last_good và health. Đây là trạng thái replay, chưa phải live sensor data.

Quyền owner đọc/ghi Thing và Policy; ingest chỉ WRITE /features; observer chỉ READ Thing. Không cấp message permission. Tài khoản phải có quyền khởi tạo tương ứng. Chính sách là mẫu review được, không tự nhận sẵn sàng production.

## 4. MQTT — cấu hình mẫu, chưa có broker đang chạy

Tệp trong ditto-config/ hoặc nút xuất trên UI:

- policy-template.json: thay subject placeholder trước khi dùng.
- thing-example.json: snapshot thật tại mốc cuối; dữ liệu historical-replay.
- mqtt-connection-template.json: closed mặc định. URI host.docker.internal:1883 chỉ phù hợp một số cấu hình Docker Desktop; đổi theo môi trường thực. Cần TLS/xác thực và quyền broker phù hợp khi triển khai; không tự kích hoạt broker anonymous.
- mqtt-protocol-example.json: Ditto Protocol modify /features. Publish trên topic nguồn aquatwin/wqi/normalized sau QC, không gửi JSON sensor thô trực tiếp.

Nguồn có authorizationContext aquatwin:ingest; target twin events dùng observer. Connection mẫu không có payload mapper vì payload đã là Ditto Protocol. Không tự tạo connection qua DevOps API trong bản này; quyền quản trị và credential DevOps là riêng. Bản ghi duplicate/đến muộn phải được connector chặn trước publish; MQTT QoS1 tự nó không bảo đảm event-time monotonic hay exactly-once.

Tham khảo chính thức:

- https://github.com/eclipse-ditto/ditto-examples/tree/master/mqtt-quick-introduction
- https://github.com/eclipse-ditto/ditto-examples/tree/master/mqtt-bidirectional
- https://eclipse.dev/ditto/basic-policy.html
- https://eclipse.dev/ditto/httpapi-sse.html

Không sao chép nguyên ví dụ bật LED sang điều khiển trang trại. SSE được xem xét nhưng chưa implement: UI mới đọc trạng thái qua GET, không giả vờ nhận live events.

## 5. Kiểm chứng và giới hạn

`python -m unittest test_bridge.py`: 11 test trên mock HTTP Ditto tại loopback. Bao gồm mapping, missing, last_good, con trỏ, Policy không cấp message, chỉ local endpoint, provision create-only, đồng bộ/get-verify/dedupe, chống lùi thời gian, giữ thuộc tính/feature khác, thiếu ETag, xung đột phiên bản, chặn redirect và Origin/Host.

`node tests.cjs`: kiểm tra lõi QC/replay trước đó. Browser test bao gồm trang mới và trạng thái chưa cấu hình. Mock pass không chứng minh tích hợp bản phát hành Ditto thực đã thành công; cần thực hiện mục 3 trên môi trường có server.

Đây là phần cập nhật trạng thái cho app ở workspace. prototype.md trong Downloads nhắc rule.md và pipeline khác không có tại workspace; không sửa đè hoặc tự nhận thay thế pipeline đó.
