# Dự báo qua mô phỏng 24–48 giờ — phiên bản nghiên cứu 1.0

## Sử dụng

Từ tổng quan chọn **Dự báo mô phỏng 1–2 ngày**, hoặc từ mục của từng chỉ số chọn **Mở dự báo mô phỏng**. Chọn mốc lịch sử, chỉ số và 24/48 giờ; nhập xu hướng bổ sung mỗi ngày (0 là cơ sở), chạy mô phỏng. Có biểu đồ, đường cơ sở/kịch bản, dải quỹ đạo, thời điểm theo khoảng thử nếu đã đặt và xuất JSON.

Mọi thời điểm tương lai được tính từ timestamp nguồn, không từ ngày xem trang. Snapshot 12/11 không phải số đo hiện tại vào một ngày khác. Dữ liệu thiếu/QC fail không được khởi tạo; QC suspect chỉ được dùng nếu người xem chủ động chấp nhận đó là điều kiện giả định. Không thay bằng last_good âm thầm.

## Mô hình cụ thể

- Tại một cursor, chỉ đọc tối đa 7 ngày dữ liệu quá khứ và cờ QC có sẵn tới cursor. Spike của chính cursor chưa được đánh giá. Cần 96 mẫu đạt QC trải ít nhất 48 giờ và 48 cặp cách nhau tối đa 30 phút.
- Fit bình phương tối thiểu có ridge 1e-8 cho mu(t) = beta0 + beta1 sin(2πh/24) + beta2 cos(2πh/24), h là giờ địa phương nguồn.
- Residual r(t) = y(t) − mu(t). Fit hệ số nhớ phi từ các cặp, ràng buộc 0 <= phi <= 0.995 để mô hình nghiên cứu ổn định. Đây là lựa chọn mô hình, không phải tham số sinh học.
- Cặp quan sát không đều được dùng để xấp xỉ phi theo một nhịp 15 phút; khi tạo innovation có hiệu chỉnh theo elapsed time. Đây là xấp xỉ thống kê, không là ước lượng continuous-time tối ưu.
- Mô phỏng bước 15 phút: r[k+1] = phi*r[k] + e[k], lấy mẫu lại innovation đã trừ trung bình từ tập fit. x[k] = mu(t[k]) + r[k]. 120 quỹ đạo, seed mặc định 20261114; cùng đầu vào cho cùng kết quả.
- Đường trung tâm cơ sở = mu(t0+h) + phi^(4h)*(y0 − mu(t0)). Kịch bản cộng ratePerDay*h/24, một xu hướng do người xem giả định. Không diễn giải rate thành lượng thay đổi do sục khí/thay nước/cho ăn.
- Dải P10–P90 là phân vị ensemble, KHÔNG phải khoảng dự báo đã được hiệu chuẩn coverage. Không tính xác suất an toàn cho cá. Không cắt/quy đổi các giá trị vượt miền QC để làm kết quả có vẻ hợp lý; có cảnh báo khi dải vượt gross range.
- Năm chỉ số được fit riêng, chưa có coupling, cân bằng oxy, sinh khối, thiết bị, thời tiết, thủy triều hay dòng chảy. Đây là simulator thống kê, không mô hình cơ chế đã kiểm chứng.

## Kiểm tra sai số lịch sử

Nút kiểm tra sử dụng toàn snapshot để rolling-origin đánh giá hồi cứu. Origin đầu sau 3 ngày; origin kế tiếp ít nhất 23,5h, mỗi lần fit chỉ dữ liệu trước origin. Tìm quan sát gần +24/+48h (tối đa lệch 10 phút), lọc QC đích sau khi bỏ test spike. So MAE trung tâm mô phỏng với persistence dùng cùng origin và đích. Không chọn mô hình hoặc ngưỡng bằng tập đánh giá, không gọi đây là validation độc lập.

forecast-evaluation.json lưu kết quả tái tính bằng forecast-tests.cjs, gồm chi tiết origin và target. Tập khoảng 14 ngày chỉ cho khoảng 6–11 endpoint hợp lệ tùy chỉ số/chân trời; các chân trời có thể chồng lấn. Mô phỏng chưa tốt hơn persistence ở mọi chỉ số. Với DO, kết quả hồi cứu ban đầu tốt hơn đối chứng trên các mốc hợp lệ, nhưng chưa đủ công bố hiệu quả vận hành. Nhiệt độ/pH/độ đục có các kết quả kém hơn đối chứng, hiển thị rõ trong giao diện.

## Trạng thái và quyền quyết định

Đầu ra có stateKind=simulated, inputSnapshotId, modelVersion, thông tin QC đầu vào, training window, beta/phi, horizon, seed, assumptions cảnh báo và toàn bộ points. Không ghi đè observed, data.json hay Thing trên Ditto. Giới hạn trại chưa được cung cấp; chỉ đối chiếu khoảng thử cục bộ khi người xem đã nhập. Không gửi cảnh báo tự động hoặc lệnh thiết bị từ mô phỏng.

## Kiểm thử

`node forecast-tests.cjs`: đúng bước/mốc 24/48h, tái lập cùng seed, không đọc tương lai (full dataset so truncated dataset tại cùng cursor), độ dịch kịch bản, guard missing/suspect/fail, kiểm tra tham số, không sửa dữ liệu gốc và split rolling-origin. Browser suite thử form 24/48h, rate, bảng sai số, giữ nguyên observed và layout mobile.

Tài liệu phương pháp tham khảo: Hyndman & Athanasopoulos, Forecasting: Principles and Practice, các phần benchmark, bootstrap và time-series cross-validation: https://otexts.com/fpp3/toolbox.html . Implementation ở đây là mô hình thử riêng của prototype, không tuyên bố là phương pháp đã xác nhận cho aquaculture.
