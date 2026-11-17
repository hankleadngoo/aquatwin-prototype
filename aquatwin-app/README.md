# AquaTwin — Observation Digital Twin

## Cập nhật 1.3 — dự báo mô phỏng 1–2 ngày

Thêm trang #forecast, truy cập từ tổng quan và từng vấn đề. Mô hình thống kê chu kỳ ngày + residual AR(1), bootstrap 120 quỹ đạo, so cơ sở/kịch bản 24 hoặc 48 giờ; có kiểm tra rolling-origin và persistence. Không là mô hình sinh học, chưa kiểm định độc lập. Xem FORECAST_SIMULATION.md; chạy `node forecast-tests.cjs` để tái tạo kiểm chứng số học và báo cáo sai số.

## Cập nhật 1.2 — không gian người nuôi

Menu chính chỉ còn Tổng quan khu nuôi và 5 mục: biến động nhiệt (temperature), nguy cơ thiếu oxy (DO), biến động axit–kiềm (pH), biến động tính chất nước (conductivity mS/cm), giảm độ trong (turbidity NTU). Công cụ QC, Ditto, dữ liệu, nhật ký và phòng thử vẫn truy cập được qua “Công cụ & kết nối”.

Mỗi mục có quan sát/QC, lịch sử phát lại, thử giá trị giả định, baseline giữ giá trị cuối khi QC đạt, gợi ý kiểm tra và ghi quyết định. Baseline chưa kiểm định độc lập và không dùng kích hoạt cảnh báo. Khi QC không đạt không tạo dự đoán. Giả lập là giá trị do người dùng đặt, không phải mô hình tác động của hành động; không sửa observed hay snapshot Ditto.

Khoảng tham chiếu mặc định trống. Người dùng có thể nhập/xóa khoảng thử nghiệm, lưu cục bộ theo từng chỉ số; đây không phải giới hạn sinh học được trại duyệt. Không kết luận bệnh, ô nhiễm hay an toàn từ một chỉ số. Trạng thái khu nuôi phản ánh dữ liệu đang có, không giả tạo sức khỏe đàn cá. Last_good và kỹ thuật đồng bộ không đổi.

Prototype tiếng Việt cho Nuôi Biển 2. 1.333 bản ghi thật, QC provisional, phát lại lịch sử, twin theo trạm đo, last_good, sự kiện xác minh, thống kê, backtest persistence, giả lập sự cố và nhật ký cục bộ.

## Chạy trên máy

Windows: nhấp đúp `Mo_AquaTwin.cmd`. Trình khởi chạy mở ứng dụng ở cổng 8765, server chỉ bind 127.0.0.1 và chạy ẩn. Dừng server đã được trình khởi chạy tạo bằng `powershell -File stop-app.ps1`. Không cần nhập tài khoản hoặc thông tin VPN.

Trong thư mục `aquatwin-app`, chạy:

    python server.py

Mở http://127.0.0.1:8765. Không mở index.html bằng file:// vì ứng dụng cần fetch data.json. Không cần npm install hay build. Có thể chạy `npm start` nếu có Node.

## Kiểm thử

    node --check dist/app.js
    node tests.cjs

Tái tạo dữ liệu bằng `python prepare_data.py`; script đọc CSV gốc ở `../Data/aquaculture_indices_clean.csv`, không sửa nguồn. Giá trị legacy salinity ánh xạ thành conductivity (mS/cm) theo xác nhận trong `C:/Users/ACER/Downloads/prototype.md`. Metadata khác theo GREEN-X được ghi trong prototype.md. Độ sâu, lồng và hiệu chuẩn chưa biết. Timestamp là giờ nguồn UTC+7 theo mục câu hỏi mở đã được xác nhận.

## Những phần chạy thật

- QC missing/gross_range/site_plausible/spike/rate_of_change/flat_line. Cấu hình theo prototype.md; phiên bản app riêng qc-ui-0.2-provisional. Chưa đối chiếu bit-for-bit với pipeline Downloads, không tuyên bố kết quả test cũ áp dụng cho app này.
- Replay: spike ở điểm con trỏ không đọc mẫu tương lai. last_good chỉ dùng dữ liệu tới con trỏ.
- Xuất CSV đã đổi tên conductivity; xuất Thing JSON và sự kiện QC.
- Nhật ký qua localStorage; không đồng bộ nhiều thiết bị. Export để sao lưu.
- Backtest baseline 30% cuối snapshot, target là mẫu kế tiếp theo lịch không đều; chưa kiểm định độc lập.
- Fault sandbox tách riêng simulated; không sửa lịch sử thật, không gửi lệnh.

## Ranh giới triển khai

Đây là static app và lõi twin trong trình duyệt, KHÔNG có Ditto server đang chạy, telemetry live, cảnh báo sinh học, mô hình bệnh, điều khiển hoặc dữ liệu camera được nạp. Feature hợp đồng sẵn cho Ditto, adapter CLI kèm theo nhưng chưa được thử tích hợp vì không có máy chủ.

Sau khi xuất Thing JSON, có thể kiểm tra bằng `python ditto_adapter.py --snapshot ten-file.json --dry-run`. Để gửi snapshot tới Ditto đã triển khai, cấu hình DITTO_URL và DITTO_TOKEN hoặc DITTO_USER/DITTO_PASSWORD trong môi trường; có thể thêm DITTO_POLICY_ID. Không đưa mật khẩu vào giao diện, mã nguồn hay lệnh shell. Adapter chỉ PUT Thing, không gửi lệnh thiết bị. Cần cấu hình policy, backup và quyền trên Ditto của nhóm.

## Đơn vị và chỉ số dẫn xuất

Không dùng DO saturation/%DO/deficit tính cũ vì salinity gốc thực chất là conductivity. App không tính PSU bằng một công thức phỏng đoán. Khi có GSW/PSS-78, cần ghi giả định áp suất và trạng thái bù nhiệt, nguồn đầu vào, phiên bản transform và QC kế thừa. Không dùng conductivity như PSU.

## Dữ liệu và quyền riêng tư

Sites được tạo ở chế độ riêng tư; giữ nguyên audience. Dữ liệu snapshot nằm trong asset riêng của app. Không chứa HA.conf, thông tin VPN, tài khoản MinIO, browser profile hay mật khẩu. Nhật ký ở trình duyệt người dùng không tự đẩy lên server. Font web có fallback system nếu mạng ngoài không truy cập được.

Trạng thái bàn giao: chưa upload source hoặc deploy Sites. Automatic approval review từ chối xuất mã kèm dữ liệu trại thực sang repository bên ngoài khi chưa có chấp thuận rõ ràng. Bản hoàn chỉnh hiện chạy cục bộ; Site đã đăng ký chưa có phiên bản triển khai. Không coi expected_url là URL hoạt động.

## Căn cứ phạm vi

`prototype.md` (14/11/2026), Digital Twin Platform Design chương 3/5, tài liệu Føre và cộng sự 2024, tổng quan 2025 và các báo cáo dự án. `rule.md` được prototype.md nhắc tới nhưng không có ở workspace hoặc cạnh bản ghi chú Downloads; app tuân thủ các quy tắc đã trích dẫn trong ghi chú, không tự nhận đã đọc rule.md đầy đủ.

## C?p nh?t 1.1 ? Ditto

??c DITTO_INTEGRATION.md. C? gateway c?c b? th?c: ki?m tra, create-only Policy/Thing, ??ng b? c? ETag, ??c l?i. Ch?a c? m?y ch? Ditto/Docker th?c ?? ki?m th? t?ch h?p. Nh?ng m? t? phi?n b?n 1.0 ? tr?n v? static-only ?? ???c thay th? b?i server.py khi ch?y b?ng launcher m?i. Ph?m vi quan tr?c/QC v? c?c gi?i h?n sinh h?c kh?ng ??i.


## Architecture update 2026-11-17

See `ARCHITECTURE_ALIGNMENT.md`, `standards-traceability.csv`, `openapi.json` and `schemas/observation.schema.json`. Versioned target profile: `dist/architecture-profile.json`. Research-only alignment with ISO/IEC 30188 and adapted ISO 23247 patterns; no complete conformity claim. New read-only APIs: `/api/architecture`, `/api/observations?cursor=100`, `/api/state/health`. Run `python -m unittest test_bridge.py test_standards.py`. The local web app adds Architecture & evidence under Tools & connections. No hosted deployment has been performed for this update.
