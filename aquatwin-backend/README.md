# AquaTwin backend — standalone package

Thư mục này gom toàn bộ backend Python hiện có của prototype thành một gói độc lập. Không di chuyển hoặc sửa ứng dụng gốc `aquatwin-app` và không thay đổi site đã deploy.

## 1. Thành phần

- `server.py`: API gateway Ditto chạy tại loopback; dựng snapshot sau QC; quản lý provision/sync/readback.
- `prepare_data.py`: đọc CSV, chuẩn hóa conductivity và tính QC provisional.
- `ditto_adapter.py`: CLI gửi Thing snapshot hoặc chạy dry-run.
- `test_bridge.py`: 11 kiểm thử gateway với mock Ditto.
- `data/source.csv`: bản sao CSV 1.333 mẫu, dùng để tái tạo đầu ra.
- `data/observations.json`: dữ liệu chuẩn hóa/QC, được server sử dụng.
- `ditto-config/`: các mẫu Policy, Thing và MQTT/Ditto Protocol.
- `source_manifest.json`: nguồn gốc mã và điều chỉnh đóng gói.

Không chứa frontend, tài khoản thật, VPN, browser profile, log hoặc môi trường ảo. Có dữ liệu trại thật giống prototype đã được cho phép chia sẻ.

## 2. Yêu cầu

Python 3.10 trở lên. Mã dùng thư viện chuẩn; không cần cài FastAPI, Flask, pandas hoặc package pip. Node.js không cần để chạy backend này.

## 3. Chạy độc lập

Mở terminal trong thư mục này:

    python server.py --port 8770

Hoặc nhấp `Run_Backend.cmd` trên Windows. Mở http://127.0.0.1:8770/api/health để kiểm tra. Nhấn Ctrl+C ở terminal để dừng.

Port 8770 khác port 8765 của app hiện tại để tránh xung đột. Gói chỉ có backend; đường dẫn gốc trả mô tả API, không mở dashboard. Frontend cũ vẫn dùng backend cũ trên port 8765; gói này không tự chuyển kết nối của frontend sang 8770.

## 4. Chuẩn bị lại dữ liệu

    python prepare_data.py

Script đọc `data/source.csv`, không sửa CSV, rồi ghi lại `data/observations.json`. Giữ cấu trúc cột nguồn hiện tại; khóa `salinity` là conductivity mS/cm. Các cột oxy dẫn xuất cũ bị loại. Ngưỡng QC là provisional, không phải ngưỡng sinh học.

Server đọc snapshot khi khởi động; sau khi tạo lại dữ liệu cần khởi động lại server. Pipeline hiện dành cho bộ một trạm đo; chưa phải ingest streaming nhiều site.

## 5. API

- `GET /`: thông tin gói backend và danh sách endpoint.
- `GET /api/health`: thông tin gateway và số bản ghi.
- `GET /api/ditto/status`: trạng thái cấu hình/kết nối.
- `GET /api/ditto/thing`: đọc Thing từ Ditto.
- `POST /api/ditto/provision`: body JSON `{}`; tạo phần Policy/Thing chưa có.
- `POST /api/ditto/sync`: body JSON `{"cursor":1332}`; dựng và đồng bộ snapshot cuối bộ dữ liệu.

Khởi tạo yêu cầu `DITTO_SUBJECT`; kết nối yêu cầu `DITTO_TOKEN` hoặc `DITTO_USER` và `DITTO_PASSWORD`. Dùng biến môi trường; `.env.example` chỉ mô tả tên biến, server KHÔNG tự đọc `.env`. Không điền mật khẩu vào mã hoặc file chia sẻ.

Gateway chỉ kết nối Ditto localhost/127.0.0.1/::1. Không có Ditto server, Docker hoặc MQTT broker được cài sẵn trong gói. Xem DITTO_INTEGRATION.md để tham khảo thiết kế tích hợp; các đường dẫn UI trong tài liệu đó thuộc ứng dụng gốc.

## 6. Kiểm thử

    python -m unittest test_bridge.py

    python ditto_adapter.py --snapshot ditto-config/thing-example.json --dry-run

Mock test không chứng minh đã kết nối thành công máy chủ Ditto thật.

## 7. Giới hạn

Đây là local prototype server, không phải backend đã harden để mở trực tiếp ra Internet. Không có database nhật ký, đăng nhập người dùng, telemetry live hoặc lệnh thiết bị. Cơ chế QC/snapshot và chống lùi trạng thái/ETag được giữ từ app.

Mô phỏng dự báo 24–48 giờ hiện chạy bằng JavaScript trong trình duyệt (`aquatwin-app/dist/forecast-core.js`), không phải backend Python, nên không được gán nhầm thành API dự báo của gói này. Nếu cần forecast API, phải triển khai thành một bước tiếp theo.
