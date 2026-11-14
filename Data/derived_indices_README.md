# Các chỉ số bổ sung

Nguồn: aquaculture_all_samples_sorted.csv. Tệp gốc không bị sửa.

## Giả định bắt buộc
- temperature được giả định là °C, salinity là phần nghìn (ppt), DO là mg/L; dữ liệu nguồn chưa xác nhận đơn vị. Các kết quả vật lý chỉ có ý nghĩa khi giả định này đúng.
- Áp suất khí quyển giả định 101.325 kPa (1 atm), không phải áp suất thủy tĩnh tại độ sâu cảm biến.
- Thành phần ion nước được giả định tương tự nước biển. Không xác nhận cảm biến đã bù độ mặn đúng.

## Oxy
Theo USGS OWQ Technical Memorandum 2011.03, phương trình 7 và 8:
T = temperature + 273.15
DO0 = exp(-139.34411 + 157570.1/T - 66423080/T² + 12438000000/T³ - 862194900000/T⁴)
Fs = exp[-S(0.017674 - 10.754/T + 2140.7/T²)]
DO_saturation = DO0 × Fs (hệ số áp suất = 1 tại 1 atm).
DO_saturation_percent = 100 × DO / DO_saturation.
DO_deficit = DO_saturation - DO; âm có nghĩa vượt bão hòa, không cắt về 0.

DOTABLES công bố miền 0–40 °C, 0–40 ppt. Các cột chính chỉ được điền trong miền này.
Với salinity > 40, kết quả chỉ nằm ở ba cột có chữ extrapolated, cờ NOT_VALIDATED. Đây là ngoại suy tham khảo, không dùng làm số đo hoặc đầu vào điều khiển chưa kiểm chứng. Không cắt độ mặn về 40 và không âm thầm coi ngoại suy là hợp lệ.
Cả kết quả trong miền vẫn phụ thuộc đơn vị và áp suất giả định, không phải quan sát trực tiếp hay mức phù hợp cho một loài cá.

## Tốc độ biến đổi
Các cột *_change_per_hour = (giá trị hiện tại - giá trị liền trước) / số giờ thực giữa hai mẫu, tính riêng từng site/device. pH là đơn vị pH/giờ, temperature là °C/giờ; đơn vị độ đục chưa xác nhận nên là đơn vị nguồn/giờ. Đây là hiệu sai phân trung bình khoảng đo, không phải tốc độ tức thời hoặc dự báo.
Mẫu đầu, mẫu lỗi, mẫu ngay sau lỗi và khoảng gián đoạn > 30 phút để trống tốc độ. Mốc 30 phút là quy tắc xử lý dữ liệu của script, không phải ngưỡng sinh học. Không nội suy, không làm trơn, không tự loại bỏ spike.

## Chưa tính
- Khối lượng riêng: cần thống nhất thang độ mặn, áp suất/độ sâu và phương pháp phù hợp, đặc biệt với độ mặn cao.
- TSS: thiếu quan hệ hiệu chuẩn địa phương từ độ đục sang mg/L.
- Tỷ lệ NH3: chưa chốt mô hình cân bằng có hiệu chỉnh độ mặn cao; nồng độ NH3 còn cần TAN và quy ước đơn vị nitơ.
- CO2: thiếu thông số carbonate bổ sung như TA và thang pH.
- Điểm phù hợp môi trường: thiếu loài, giai đoạn và ngưỡng được xác nhận.
Không tạo giá trị giả cho các đại lượng trên.

## Nguồn phương pháp
https://water.usgs.gov/water-resources/software/DOTABLES/
https://water.usgs.gov/admin/memo/QW/qw11.03.pdf

Chạy lại: python add_water_indices.py
