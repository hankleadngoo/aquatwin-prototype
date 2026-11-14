# AquaTwin – Prototype Observation Twin cho chất lượng nước (WQI)

> File này ghi **trạng thái hiện tại** của prototype: đang làm gì, đã chốt gì, phần nào để sau.
> Cập nhật file này mỗi khi xong một bước hoặc đổi quyết định.
> Quy tắc bắt buộc của dự án nằm trong `rule.md` (trích dẫn dạng R3.2, R8.3…).

Cập nhật lần cuối: 2026-11-14 (các mục chi tiết sắp theo 9 khối của sơ đồ; khối chưa làm ghi "Hệ thống đề xuất")

![Kiến trúc đề xuất: mọi bản ghi qua QC trước khi vào twin, dự báo ghi riêng](images/kien-truc-digital-shadow.png)

*Sơ đồ kiến trúc đề xuất, lấy từ `de-xuat-digital-shadow-wqi.md`.*

---

## 1. Mục tiêu và các quyết định đã chốt

### 1.1. Mục tiêu và phạm vi

- **Mục tiêu**: dựng một Observation Digital Twin / digital shadow cho chất lượng nước, tương ứng **phase P1** trong `rule.md` §14.
- **Phạm vi hiện tại**: chỉ dữ liệu WQI (temperature, conductivity – khoá gốc `salinity`, pH, DO, turbidity). Chưa làm feeding event, video, hydrophone.
- **Chưa làm**: dự báo WQI. Theo R6.10, chỉ được đưa dự báo vào sau khi đã kiểm định độc lập.
- **Luồng dữ liệu đích**:
  thư mục dữ liệu trên máy → đọc → **chuẩn hoá** → **QC gắn cờ** → (lưu trữ) → (twin Eclipse Ditto) → (dashboard)
  Phần trong ngoặc là phần để sau.

### 1.2. Quyết định đã chốt

1. **File JSON gốc là kho dữ liệu chính.** Không sửa, không xoá file gốc. Mọi kết quả đều tạo lại được bằng cách chạy lại từ file gốc.
2. **Nạp toàn bộ một lần ở giai đoạn này.** Code vẫn phải viết theo dạng xử lý từng bản ghi theo thứ tự thời gian, để sau này chuyển sang nạp liên tục mà không phải viết lại (§4.3).
3. **Mô hình twin (khi làm Ditto):** một Thing cho mỗi trạm đo WQI, ví dụ `aquatwin:nuoibien-2`. Mỗi chỉ số là một feature, thêm một feature `health`. Mỗi feature giữ giá trị mới nhất, `ts`, cờ QC và `last_good`.
4. **Ditto chỉ giữ trạng thái hiện tại.** Dữ liệu lịch sử và kết quả QC lưu ở file hoặc cơ sở dữ liệu riêng.
5. **Cờ QC không phải ngưỡng cảnh báo.** Ngưỡng QC chỉ đánh giá chất lượng dữ liệu. Ngưỡng cảnh báo DO, nhiệt độ, độ mặn phải do trại duyệt (R8.3). Prototype không phát cảnh báo cho cá.
6. **Không tự suy ra đơn vị, độ sâu hay hiệu chuẩn (R3.5).** Mọi giả định đều phải ghi trong file cấu hình có phiên bản, kèm nguồn; cái gì không có nguồn thì đánh dấu `unconfirmed`.
7. **Khoá `salinity` trong dữ liệu là độ dẫn điện, đơn vị mS/cm** (người dùng xác nhận 13/11/2026 22:31). Trong pipeline: tham số chuẩn là `conductivity` (`unit: mS/cm`, `unit_status: confirmed`, giữ `raw_key: salinity` để truy vết). Độ mặn thực tế (PSU) nếu cần thì là **giá trị dẫn xuất** tính từ độ dẫn điện + nhiệt độ theo PSS-78, ghi rõ công thức, phiên bản và nhiệt độ dùng để tính (R3.6). Trên ThingsBoard giữ nguyên khoá `salinity` và các dashboard.
8. **Ngưỡng cảnh báo ThingsBoard (`greenxAlertPolicy`) tách biệt với ngưỡng QC** và không đưa vào pipeline QC (xem `session_chat.md` §1).
9. **Đơn vị các chỉ số còn lại lấy theo cấu hình GREEN-X trên ThingsBoard** (dashboard GREEN-X Nuôi Biển v6.0 và policy cảnh báo `greenxAlertPolicy`; người dùng đồng ý 13/11/2026 23:25): temperature **°C**, pH **không đơn vị**, DO **mg/L**, turbidity **NTU**, pdo (HonMun_1) **% bão hoà**; `salinity` = độ dẫn điện **mS/cm** (đã xác nhận). Trạng thái trong config: `unit_status: documented`, `unit_source: "ThingsBoard GREEN-X v6.0 + greenxAlertPolicy (quét 2026-11-13)"`. Lưu ý: ThingsBoard **không lưu đơn vị trong telemetry**, đơn vị chỉ nằm ở cấu hình widget/policy và các dashboard cũ ghi không thống nhất (vd DEMO 2 ghi DO "%") – chỉ dùng GREEN-X làm nguồn. Kiểm tra datasheet cảm biến là việc phụ, không chặn prototype.

## 2. Trạng thái các khối

| Khối (theo sơ đồ) | Trạng thái | Ghi chú |
|---|---|---|
| MinIO (nguồn hiện có) | ✅ Có (bản tải về máy) | Chi tiết §3. `Data MinIO/Nuoi-bien-2-data-WQI/YYYY-MM-DD/*.json`, 1.333 file, 30/10–12/11/2026 |
| Connector đọc dữ liệu | ✅ Xong (batch) · ⏸ kết nối trực tiếp MinIO tạm hoãn · ⏸ nạp liên tục để sau | Chi tiết §4. `aquatwin-prototype/src/aquatwin/reader.py`: chỉ đọc, sha256 từng file, iterator theo event time, nhiều site. Kết nối trực tiếp MinIO: đổi phần đọc dữ liệu, các khối sau giữ nguyên |
| Chuẩn hoá | ✅ Xong (obs-1.1) | Chi tiết §5. Long format, `event_id` UUIDv5, quarantine (R3.4), khử trùng (R4.4). Khoá `salinity` → tham số `conductivity` (mS/cm, **confirmed**, giữ `raw_key`, quy tắc `map-salinity-to-conductivity-1.0`). Thêm `practical_salinity` (PSU, `state_kind = estimated`, PSS-78 qua `gsw`, p = 0 dbar giả định, có `derived_from` + `transform`). 1.333 file → 6.665 observation đo + 1.330 dẫn xuất, 0 quarantine. Đơn vị (params-1.2): conductivity **confirmed**; temperature °C, pH, DO mg/L, turbidity NTU **documented** theo GREEN-X kèm `unit_source` (§1.2 mục 9) |
| QC gắn cờ | ✅ Xong (qc-0.2-provisional) | Chi tiết §6. Ngưỡng `conductivity` (mS/cm): gross [0, 80], site_plausible [30, 60], spike 5/10, ROC 7,5/h. Suspect+fail của độ dẫn điện: 97,7% → **4,6%**. `practical_salinity` không chạy QC riêng, kế thừa cờ xấu nhất của 2 đầu vào. 50 test pytest pass. Ngưỡng vẫn **provisional** |
| Twin – Eclipse Ditto | ⏸ Tạm hoãn | Chi tiết §7 (hệ thống đề xuất). Đã chốt mô hình (xem §1.2 mục 3–4) nhưng chưa dựng |
| Kho chuỗi thời gian (lưu trữ) | ⏸ Tạm hoãn | Chi tiết §8. Trước mắt chỉ xuất file kết quả (Parquet/CSV). TimescaleDB để sau |
| Cảnh báo | ⏸ Chưa làm | Chi tiết §9 (hệ thống đề xuất). Prototype không phát cảnh báo (§1.2 mục 5) |
| Dashboard | ⏸ Để sau | Chi tiết §10 (hệ thống đề xuất) |
| Dự báo WQI | ⛔ Chưa làm | Chi tiết §11 (hệ thống đề xuất). R6.10 |

> Các mục §3–§11 tương ứng 9 khối trong sơ đồ ở đầu file. Mỗi mục có phần **Hiện tại** (đã làm) và/hoặc **Hệ thống đề xuất** (chưa thực hiện, lấy từ sơ đồ và `de-xuat-digital-shadow-wqi.md`). Phần "Hiện tại" của §4–§6 và §8 mô tả **cách pipeline `aquatwin-prototype/` đang chạy** (phiên bản hiện tại: schema `obs-1.1`, `params-1.2`, `qc-0.2-provisional`). Khi đổi code hoặc config của khâu nào thì sửa mục của khâu đó. Mọi ngưỡng, đường dẫn, múi giờ nằm trong `aquatwin-prototype/config/`, không viết cứng trong code.

## 3. Khối MinIO (nguồn hiện có)

### 3.1. Hiện tại – dữ liệu đã tải về máy (nuôi-biển-2), kết quả kiểm tra nhanh

- Thiết bị `nuoibienvien3`, site `NuoiBien_2`. Mỗi file là một lần đo, gồm cả 5 chỉ số và một `ts`.
- `ts` dạng ISO không có múi giờ, ví dụ `2026-10-30T00:08:16.144817`. Giả định là giờ địa phương GMT+7 (cần xác nhận).
- Nhịp gửi khoảng 15 phút (trung vị 905 s). Có 1 khoảng trống lớn hơn 30 phút, dài nhất khoảng 66 phút.
- 1.330 file đủ 5 chỉ số. 3 file ngày 06/11 là bản ghi lỗi `sensor_error` ("cannot open serial port …"), không có giá trị đo.
- Thông tin về các nguồn dữ liệu khác (MinIO đầy đủ, ThingsBoard) xem `data.md`.
- Khoảng giá trị (min / trung vị / max):
  - temperature: 27.9 / 28.9 / 29.7
  - salinity (thực chất là **độ dẫn điện, mS/cm**): 31.5 / 49.4 / 51.5. Quy đổi sang độ mặn ở ~28–29°C tương ứng khoảng 20 / 31,5 / 33 PSU → **bình thường** cho nước biển (kết luận cũ "cao bất thường" là sai do hiểu nhầm đơn vị). Các lần tụt xuống 31,5–34 mS/cm (~20–22 PSU) là bất thường cần kiểm tra
  - pH: 7.48 / 8.13 / 8.39
  - DO: 5.39 / 6.0 / 6.57
  - turbidity: 4.3 / 5.0 / 964.4. Có các giá trị vọt lên rất cao

### 3.2. Hệ thống đề xuất (chưa thực hiện: đọc trực tiếp từ MinIO)

- Nguồn: MinIO nội bộ (`10.7.0.27:9090`), bucket `nuoi-bien-1-data`, `nuoi-bien-2-data`: `WQI/*.json` và `WQI-prediction` (chi tiết bucket trong `data.md`).
- **Chỉ đọc, không ghi ngược** về MinIO; luồng một chiều từ MinIO vào twin (sơ đồ, `de-xuat-digital-shadow-wqi.md`).
- Đề xuất dùng site 2 trước vì dữ liệu đều và còn đang ghi (`de-xuat-digital-shadow-wqi.md`, lộ trình).

## 4. Khối Connector đọc dữ liệu

### 4.1. Hiện tại (đã làm – batch, đọc thư mục trên máy)

- **Code / config:** `src/aquatwin/reader.py`; `config/source.yaml` (`sources`, `layout`).
- **Đầu vào:** thư mục `<nguồn>/YYYY-MM-DD/YYYYMMDD-HH-MM-SS.json`. Mặc định `Data MinIO/Nuoi-bien-2-data-WQI`; thêm site khác bằng `--source` (lặp lại được) hoặc thêm vào `sources`.
- **Chỉ đọc**, không sửa/xoá/di chuyển file gốc. Mỗi file được tính `sha256` và đường dẫn tương đối (`source_file`) để truy vết.
- File JSON lỗi cú pháp vẫn được đọc vào (kèm lý do lỗi) để khâu chuẩn hoá đưa vào quarantine, không bỏ im lặng.
- Sắp xếp theo **thời gian sự kiện** (`ts`; nếu `ts` hỏng thì dùng thời gian trong tên file), hoà thì theo đường dẫn → thứ tự tất định.
- Trả về một **iterator** bản ghi thô. Khi chuyển sang nạp liên tục chỉ cần thay iterator này (§4.3).

### 4.2. Hệ thống đề xuất (theo sơ đồ)

| Chức năng trong sơ đồ | Tình trạng |
|---|---|
| Phát lại lịch sử theo `ts` | ✅ Đã làm ở chế độ batch (sắp theo thời gian sự kiện, kiểm tra replay lưu/nạp state) |
| Đọc file mới mỗi 15 phút | ⏸ Chưa làm (§4.3) |
| Khoá chống trùng | ✅ Đã làm: `event_id` UUIDv5 từ (site_id, sensor_id, phenomenon_time, parameter), bản trùng ghi vào `duplicates.csv` (§5) |
| Hàng lỗi | Một phần: bản ghi sai schema vào `output/quarantine.csv` (§5). Chưa có hàng lỗi (dead-letter) cho chạy liên tục |
| Đọc trực tiếp từ MinIO | ⏸ Tạm hoãn: đổi phần đọc dữ liệu, các khối sau giữ nguyên |

- Đề xuất trong `de-xuat-digital-shadow-wqi.md`: khi chạy thời gian thực cho site 2, đọc file mới mỗi 15 phút và đo độ trễ từ lúc đo đến lúc twin cập nhật; nếu quá 30 phút (gấp đôi chu kỳ 15 phút) không có số đo mới thì trạng thái chuyển sang *stale*.

### 4.3. Nạp liên tục / thời gian thực – ghi chú để sau

Hiện tại nạp toàn bộ một lần. **Sau này sẽ sửa để nạp liên tục khi có dữ liệu mới** (theo dõi thư mục hoặc MinIO bucket notification, rồi đến MQTT). Code giai đoạn này phải chuẩn bị sẵn cho việc đó:

- Phần đọc dữ liệu trả về một **iterator** các bản ghi thô theo thứ tự thời gian. Khi chạy liên tục chỉ cần thay bằng iterator đọc dữ liệu mới đến.
- Hàm chuẩn hoá là hàm thuần (pure): cùng đầu vào thì luôn cho cùng đầu ra, không phụ thuộc trạng thái bên ngoài.
- Engine QC giữ **trạng thái cửa sổ** cho từng cặp (sensor, parameter): giá trị trước đó, độ dài đoạn giá trị đứng yên… Trạng thái này phải lưu ra file và nạp lại được (serializable), để khi chạy liên tục có thể tiếp tục từ chỗ dừng.
- Mỗi bản ghi có **khoá idempotency** (`event_id` tất định). Nạp trùng không sinh bản ghi trùng (R4.2, R4.3).
- Việc cần thiết kế khi chuyển sang chạy liên tục:
  - watermark và cách xử lý dữ liệu đến trễ (R4.4: sửa lịch sử nhưng không kéo trạng thái hiện tại lùi lại)
  - spike test cần giá trị kế tiếp, nên cờ của mỗi giá trị sẽ có độ trễ một nhịp
  - phát hiện `stale` theo đồng hồ thật
- Các thông số theo R4.1 cần khai báo cho nguồn dữ liệu: `phenomenonTime`, `ingestTime`, watermark, chất lượng đồng hồ, độ trễ tối đa chấp nhận được.

## 5. Khối Chuẩn hoá

### 5.1. Hiện tại (đã làm)

- **Code / config:** `src/aquatwin/normalize.py` (hàm thuần `normalize_record`), `src/aquatwin/pipeline.py` (khử trùng, kiểm tra thời gian); `config/source.yaml`, `config/parameters.yaml`.
- **Long format:** mỗi bản ghi thô → 5 observation đo trực tiếp (`state_kind = observed`), mỗi chỉ số một dòng, cộng 1 observation dẫn xuất `practical_salinity` nếu đủ đầu vào.

| Khoá gốc | Tham số chuẩn | Đơn vị | unit_status |
|---|---|---|---|
| `temperature` | `water_temperature` | degC | documented (GREEN-X) |
| `salinity` | `conductivity` | mS/cm | confirmed (quy tắc `map-salinity-to-conductivity-1.0`) |
| `pH` | `ph` | 1 | documented |
| `DO` | `dissolved_oxygen` | mg/L | documented |
| `turbidity` | `turbidity` | NTU | documented |

- **Giá trị không bị quy đổi** (R3.5): `value` = giá trị gốc dạng số, `raw_value` = chuỗi gốc, `raw_key` = tên khoá gốc.
- **Thời gian:** `phenomenon_time_local` = chuỗi `ts` gốc; `phenomenon_time_utc` đổi theo múi giờ giả định trong config (`Etc/GMT-7`, **unconfirmed**); `tz_assumption` ghi giả định. `ingest_time` = thời điểm chạy; `received_at`, `depth_m`, `calibration_ref`, `unit_id` = null (chưa có thông tin).
- **`event_id`** = UUIDv5 từ (site_id, sensor_id, phenomenon_time_utc, parameter) → khoá idempotency (R4.2).
- **Bản ghi `sensor_error`:** vẫn sinh đủ 5 observation, `value = null`, `device_error` = thông điệp lỗi → QC gán cờ 9. Không sinh giá trị dẫn xuất.
- **Quarantine** (`output/quarantine.csv`, kèm lý do – R3.4): JSON lỗi, không phải object, thiếu `device`/`site`/`ts`, `ts` không parse được, có khoá lạ, giá trị không phải số và không phải null (kể cả bool, NaN), thiếu khoá đo mà không có `sensor_error`.
- **Khử trùng** (R4.4): cùng `event_id` chỉ giữ bản đầu tiên, bản sau ghi vào `output/duplicates.csv` (có cột `same_raw_value`).
- **Kiểm tra thời gian** (chỉ ghi nhận, `output/time_anomalies.csv`): `ts` lệch tên file > 2 s, ngày của `ts` khác thư mục ngày, `ts` ở tương lai, `ts` không tăng dần theo thứ tự file.
- **Giá trị dẫn xuất `practical_salinity`** (PSU, `state_kind = estimated`, R2.1, R3.6):
  - công thức PSS-78: `gsw.SP_from_C(conductivity mS/cm, water_temperature °C, p)`, phiên bản `pss78-gsw-1.0`;
  - giả định p = 0 dbar (chưa biết độ sâu); `temperature_compensated: unknown` → dùng nhiệt độ đo (nếu sau này là `true` thì dùng 25 °C);
  - `derived_from` = event_id của 2 đầu vào, `transform` = tên + phiên bản + giả định;
  - không tạo nếu thiếu/null một đầu vào; bật/tắt bằng `derived.practical_salinity.enabled`.

### 5.2. Đối chiếu với sơ đồ

- 1 bản ghi → 5 observation: ✅ (cộng 1 giá trị dẫn xuất `practical_salinity`).
- Gắn đơn vị, sensorId: ✅ (`unit`, `unit_status`, `unit_source`; `sensor_id` từ `device`).
- `ts` + 07:00: ✅ theo múi giờ trong `config/source.yaml` (`Etc/GMT-7`).
- `receivedAt`: ⏸ chưa có – file trên máy không có thông tin này nên đang để null. Đề xuất trong `de-xuat-digital-shadow-wqi.md`: lấy `last_modified` của file trên MinIO.

## 6. Khối QC gắn cờ

### 6.1. Hiện tại (đã làm)

- **Code / config:** `src/aquatwin/qc.py` (`QCEngine`); `config/qc.yaml` (`qc_version: qc-0.2-provisional`). Bản cũ lưu ở `config/history/`.
- **Thang cờ IOOS QARTOD:** 1 pass · 2 not evaluated · 3 suspect · 4 fail · 9 missing.
- **Xử lý tuần tự theo thời gian** cho từng luồng (site, sensor, parameter). Trạng thái (điểm trước, điểm đang chờ, đoạn đứng yên…) lưu/nạp được bằng `to_dict()` / `from_dict()` → `output/qc_state.json`.
- **6 bài kiểm tra cho mỗi giá trị đo** (mỗi bài một cờ):

| Bài | Quy tắc | Cờ |
|---|---|---|
| `missing` | value null hoặc có `sensor_error` | 9 |
| `gross_range` | ngoài giới hạn vật lý/cảm biến | 4 (turbidity ≥ 1000 → 3, nghi chạm trần) |
| `site_plausible` | ngoài khoảng hợp lý theo trại | 3 |
| `spike` | \|v − (v_trước + v_sau)/2\| > ngưỡng | 3 / 4; thiếu điểm lân cận hoặc lân cận cách > 30 phút → 2 |
| `rate_of_change` | \|Δv\| / Δt (theo giờ) so với điểm trước > ngưỡng | 3; Δt > 30 phút → 2 |
| `flat_line` | giá trị không đổi (sai khác ≤ 0) kéo dài | ≥ 4 h → 3, ≥ 12 h → 4 |

- **Ngưỡng (provisional – chưa được trại duyệt):**

| Chỉ số | gross_range | site_plausible | spike 3 / 4 | rate_of_change |
|---|---|---|---|---|
| water_temperature (°C) | −2 – 45 | 20 – 35 | 1 / 2 | 2 /h |
| conductivity (mS/cm) | 0 – 80 | 30 – 60 | 5 / 10 | 7,5 /h |
| ph | 0 – 14 | 7,0 – 9,0 | 0,3 / 0,6 | 0,5 /h |
| dissolved_oxygen (mg/L) | 0 – 25 | 2 – 15 | 1 / 2 | 2 /h |
| turbidity (NTU) | 0 – 1100 | 0 – 100 | 50 / 200 | 100 /h |

- **Cờ tổng hợp `quality_flag`:** value null → 9; ngược lại lấy cờ nặng nhất trong các bài đã chạy (4 > 3 > 1); không bài nào chạy được → 2.
- **`practical_salinity`:** không chạy QC riêng (tránh đếm trùng), nhận cờ xấu nhất của conductivity và water_temperature theo thứ tự 9 > 4 > 3 > 2 > 1.
- **Gap** (cấp bản ghi): `gap_before_s` cho mỗi bản ghi; gap > 1.800 s (2 × nhịp 900 s) ghi vào `output/gaps.csv`, **không hạ cờ**.
- **Drift:** trung bình ngày và Δ so với ngày trước, chỉ để báo cáo, không gắn cờ.
- **Lưu ý:**
  - spike cần điểm kế tiếp nên cờ của mỗi giá trị trễ một nhịp (~15 phút); điểm cuối chuỗi → spike = 2;
  - điểm ngay cạnh một spike lớn cũng có thể bị gắn cờ (hiệu ứng lân cận của công thức QARTOD);
  - **ngưỡng QC ≠ ngưỡng cảnh báo** (R8.3, §1.2 mục 5 và 8): không dùng `greenxAlertPolicy`, không phát cảnh báo;
  - đổi ngưỡng: sửa `config/qc.yaml` và tăng `qc_version`.

### 6.2. Đối chiếu với sơ đồ

- Khoảng giá trị, tốc độ đổi, đứng yên: ✅ (`gross_range`, `site_plausible`, `rate_of_change`, `flat_line`, `spike`).
- Thiếu dữ liệu, `sensor_error`: ✅ (`missing` → cờ 9; gap ghi vào `gaps.csv`). Trạng thái *stale* theo đồng hồ thật: ⏸ chưa làm (§4.3).
- Trôi cảm biến: một phần – hiện chỉ có bảng drift theo ngày trong báo cáo, **không gắn cờ**. Đề xuất trong `de-xuat-digital-shadow-wqi.md`: phát hiện bằng kiểm tra xu hướng và so chéo với site kia, gắn cờ *suspect*.
- Gắn `qualityFlag`: ✅ (`quality_flag`, thang QARTOD).

## 7. Khối Twin – Eclipse Ditto

### 7.1. Hiện tại

- Chưa dựng (tạm hoãn).

### 7.2. Hệ thống đề xuất (chưa thực hiện)

- Theo sơ đồ: Thing cho site-1, site-2; tách trạng thái `observed` · `estimated` · `predicted` (tách riêng); twin giữ **trạng thái mới nhất**. Nhận dữ liệu đã qua QC; gửi tiếp sang kho chuỗi thời gian, cảnh báo, dashboard; dự báo ghi vào phần `predicted`.
- Mô hình đã chốt: một Thing cho mỗi trạm đo WQI, mỗi chỉ số là một feature, thêm feature `health`; mỗi feature giữ giá trị mới nhất, `ts`, cờ QC và `last_good` (§1.2 mục 3). Ditto chỉ giữ trạng thái hiện tại (§1.2 mục 4).
- Theo `de-xuat-digital-shadow-wqi.md`: mỗi site có một `twinId` chuẩn duy nhất (R1.1); khi có thông tin lồng hoặc độ sâu thì thêm Thing con. Tách loại trạng thái (R2.1, R2.2): `observed` = số đo thô kèm cờ; `estimated` = giá trị lấy mẫu lại theo lưới 15 phút, chỉ tính từ bản ghi đạt QC; `predicted` = dự báo kèm `modelRef`, phiên bản và ảnh chụp dữ liệu đầu vào (R2.4). Chưa dùng `simulated` và `desired`.
- Lưu ý: trong pipeline hiện tại, `state_kind = estimated` đang dùng cho giá trị dẫn xuất `practical_salinity` (§5), khác với nghĩa "lấy mẫu lại lưới 15 phút" trong đề xuất.
- Ditto lưu: trạng thái hiện tại, journal sự kiện + snapshot trên MongoDB, search index; lịch sử giới hạn – chuỗi thời gian phải đẩy ra cơ sở dữ liệu riêng (`session_chat.md`).
- Kiểm thử đề xuất khi dựng (`de-xuat-digital-shadow-wqi.md`, lộ trình bước 3): đăng ký 2 Thing, phát lại lịch sử site 2 rồi site 1; kiểm thử các kịch bản R4.4 (bản ghi trùng, bản ghi đến muộn, mất kết nối rồi nối lại).

## 8. Khối Kho chuỗi thời gian (lưu trữ)

### 8.1. Hiện tại – đầu ra file và báo cáo

- **Code:** `src/aquatwin/pipeline.py` (`write_outputs`), `src/aquatwin/report.py`; chạy bằng `python run_batch.py --source "Data MinIO/Nuoi-bien-2-data-WQI"`.
- **Thư mục `aquatwin-prototype/output/`:**

| File | Nội dung |
|---|---|
| `observations.parquet` / `.csv` | mọi observation + `quality_flag`, `qc_tests` (JSON 6 cờ), 6 cột `qc_<bài>`, `qc_version` |
| `quarantine.csv` | bản ghi sai schema + lý do |
| `duplicates.csv` | observation trùng `event_id` đã bỏ |
| `gaps.csv` | khoảng trống > 30 phút |
| `time_anomalies.csv` | bất thường thời gian |
| `qc_state.json` | trạng thái QC trước khi chốt điểm cuối, để nạp tiếp |
| `qc_summary.md` | báo cáo QC (xem dưới) |
| `run_manifest.json` | thời điểm chạy, sha256 mã nguồn, hash config, version, danh sách file đầu vào + sha256, số dòng mỗi file đầu ra (R6.6, R12.5) |

- **`qc_summary.md` gồm:** tổng quan và kiểm tra không mất dữ liệu; bảng cờ theo chỉ số (đo trực tiếp và dẫn xuất tách riêng); so sánh cờ trước/sau sửa đơn vị (chạy lại engine với `config/history/qc-0.1-provisional.yaml`); bảng theo ngày; bài kiểm tra gắn cờ nhiều nhất; bất thường lớn (top turbidity, các đợt conductivity < 40 mS/cm kèm PSU); gap, quarantine, trùng lặp, lỗi thiết bị; drift; giả định đang dùng.
- **Kiểm thử:** `pytest` (51 test) gồm từng bài QC trên dữ liệu tổng hợp, chuẩn hoá/quarantine/timezone, ánh xạ conductivity và giá trị dẫn xuất, bất biến trên dữ liệu thật (1.333 file → 6.665 observation đo + 1.330 dẫn xuất), idempotency (chạy 2 lần giống nhau) và replay (cắt đôi, lưu/nạp state = chạy một lần).

### 8.2. Hệ thống đề xuất (chưa thực hiện)

- Theo sơ đồ: lưu **toàn bộ lịch sử + cờ QC**, **sửa dữ liệu đến muộn**, là **nguồn cho backtest** (kiểm định dự báo).
- Bản ghi đến muộn được dùng để sửa lịch sử, nhưng không kéo trạng thái hiện tại lùi lại (R4.4).
- Công nghệ: TimescaleDB khi chạy thời gian thực (`session_chat.md` §1); `de-xuat-digital-shadow-wqi.md` gợi ý TimescaleDB hoặc InfluxDB. Prototype nhỏ: file gốc + Ditto + file kết quả QC (CSV/Parquet) là đủ.

## 9. Khối Cảnh báo

### 9.1. Hiện tại

- Chưa làm. Prototype không phát cảnh báo cho cá (§1.2 mục 5). Ngưỡng cảnh báo ThingsBoard (`greenxAlertPolicy`) tách biệt, không đưa vào pipeline (§1.2 mục 8).

### 9.2. Hệ thống đề xuất (chưa thực hiện)

- Theo sơ đồ: cảnh báo **chất lượng dữ liệu**; cảnh báo theo **ngưỡng tạm, chờ trại duyệt**; **mất dữ liệu → báo ngay**. Nhận đầu vào từ QC và twin.
- Cảnh báo chất lượng dữ liệu gồm thiếu dữ liệu, đứng yên, lỗi cảm biến (`de-xuat-digital-shadow-wqi.md`, lộ trình bước 5).
- Không im lặng khi thiếu dữ liệu (R4.5): thiếu dữ liệu bắt buộc thì báo cho người vận hành, không coi là an toàn.
- Cảnh báo chỉ chạy trên dữ liệu đạt QC; dữ liệu cờ 3/4/stale → cảnh báo "thiếu dữ liệu tin cậy" (R4.5, R7.6 G1) (`session_chat.md` §1).
- Ngưỡng DO, nhiệt độ, độ mặn để trống cho tới khi trại phê duyệt (R8.3). Chưa dùng dự báo để kích hoạt cảnh báo.

## 10. Khối Dashboard

### 10.1. Hiện tại

- Chưa làm (để sau). Báo cáo QC tạm thời ở `aquatwin-prototype/output/qc_summary.md` (§8.1).

### 10.2. Hệ thống đề xuất (chưa thực hiện)

- Theo sơ đồ: hiển thị **trạng thái + cờ chất lượng**, **lịch sử, khoảng trống**, **nhật ký cảnh báo**. Lấy dữ liệu từ twin.
- Công nghệ gợi ý: Grafana (`de-xuat-digital-shadow-wqi.md`).

## 11. Khối Dự báo

### 11.1. Hiện tại

- Chưa làm (R6.10: chỉ được đưa dự báo vào sau khi đã kiểm định độc lập). Pipeline hiện tại không dùng dữ liệu WQI-prediction.

### 11.2. Hệ thống đề xuất (chưa thực hiện)

- Theo sơ đồ: mốc **giữ giá trị cuối**; **RG-MoE: chưa kiểm định**; **chỉ ghi vào `predicted`** của twin. Lấy dữ liệu từ kho chuỗi thời gian.
- Đánh giá trong `de-xuat-digital-shadow-wqi.md`: với 93 lần chạy ngày 16/10/2026 (chỉ site 1), RG-MoE sai nhiều hơn mốc giữ giá trị cuối ở cả 3 chỉ số tự dự báo (nhiệt độ, DO, độ đục); độ mặn và pH chỉ lặp lại giá trị cuối. Chỉ có một ngày nên chưa đủ để kết luận.
- Hiển thị RG-MoE như trạng thái *predicted* gắn nhãn "chưa kiểm định", luôn kèm mốc giữ giá trị cuối. Kiểm định lại trên nhiều tuần dữ liệu đã qua QC; chỉ đưa vào cảnh báo khi thắng mốc này ổn định (lộ trình bước 7).
- ThingsBoard: rule chain profile Nuôi Biển có nhánh gọi `/predict` (HTTP, không xác thực) nhưng không có khoá dự báo nào được lưu (`session_chat.md`).

## 12. Câu hỏi mở (cần trại / nhóm thiết bị trả lời)

- [x] ~~Đơn vị chính thức của từng chỉ số~~ → `salinity` = độ dẫn điện mS/cm (xác nhận); các chỉ số còn lại theo cấu hình GREEN-X: °C, pH, DO mg/L, NTU (§1.2 mục 9). Việc phụ (không chặn): đối chiếu datasheet cảm biến khi có.
- [x] ~~`ts` là giờ địa phương GMT+7 hay UTC?~~ → **GMT+7**: so khớp NB2 ngày 12/11 với ThingsBoard, 96/96 bản ghi chỉ khớp thời điểm khi hiểu `ts` là +07:00 (lệch 0,4–3,5 s). Còn mở: đồng hồ thiết bị có đồng bộ NTP không?
- [ ] Vị trí và độ sâu đặt đầu đo, thuộc bè (unit) nào
- [ ] Giới hạn đo theo thông số kỹ thuật (spec) của từng đầu đo. Turbidity có giá trị trần (ví dụ 1100) không?
- [ ] Lịch vệ sinh và hiệu chuẩn đầu đo
- [x] ~~Độ mặn khoảng 49 là đúng thực tế hay do lỗi đơn vị?~~ **Đã trả lời 13/11 22:31:** khoá `salinity` là độ dẫn điện mS/cm. Độ mặn thực khoảng 27–33 PSU (bình thường). Đã sửa `config/parameters.yaml` và `config/qc.yaml` (obs-1.1, qc-0.2).
- [ ] Cảm biến có tự bù nhiệt cho độ dẫn điện không (giá trị là độ dẫn điện thực tế hay đã quy về 25°C – "specific conductance")? Ảnh hưởng tới công thức quy đổi sang độ mặn. Hiện để `temperature_compensated: unknown` (dùng nhiệt độ đo); nếu là có thì phải dùng t = 25°C.
- [ ] GREEN-X quy đổi độ mặn bằng hệ số tuyến tính ≈ 0,65 × mS/cm, cho kết quả **cao hơn PSS-78 khoảng 8%** ở 28–29°C (50,9 mS/cm: GREEN-X 33,1 ppt, PSS-78 31,1 PSU). Nếu cảm biến đã bù nhiệt về 25°C thì PSS-78 sẽ gần GREEN-X hơn. Cần thống nhất công thức nào là chuẩn cho dashboard và cảnh báo.
- [ ] Độ dẫn điện tụt dưới 40 mS/cm: **8 đợt / 38 lần đo** (30/10, 01/11, 02/11, 03/11, 04/11, 09/11, 10/11, 11/11), thấp nhất 31,5 mS/cm (~17,8 PSU), mỗi đợt 30–90 phút, phần lớn bắt đầu khoảng **10:40–11:35 sáng** (01/11 và 10/11 lúc ~14:20–15:30). Có phải thay nước / bổ sung nước ngọt / vệ sinh định kỳ không? Trại có lịch thao tác không?
- [ ] Ai duyệt ngưỡng QC và ngưỡng cảnh báo (R8.3)
- [ ] pH đứng yên rất lâu (dài nhất 17,4 h ở 8.22, 17 đoạn ≥ 4 h) dù độ phân giải 0.01: đầu đo pH có cập nhật theo bước / bị treo giá trị không? Đồng thời pH tăng dần 7,5 → 8,2 trong 2 tuần: thực tế hay trôi hiệu chuẩn?
- [ ] Turbidity đứng yên ở 5.0 / 4.6 kéo dài tới 17 h (25 đoạn ≥ 4 h): đây có phải giá trị sàn / mặc định của cảm biến không?
- [ ] Sự kiện turbidity 02/11 17:42–18:13 (964 → 208 → 498) và 06/11 16:08 (316): thực tế (khuấy bùn, vệ sinh, thay lưới…) hay nhiễu? Trại có nhật ký thao tác không?
- [ ] Ngày 06/11: mất dữ liệu 66 phút (05:59 → 07:05) rồi 3 lỗi "cannot open serial port" (07:05, 17:41, 17:44). Có ai can thiệp thiết bị / mất điện không?
- [ ] DO thực tế có 2 chữ số thập phân (không phải độ phân giải thấp như dự đoán) – xác nhận độ phân giải và độ chính xác của đầu đo DO

## 13. Nhật ký

- 2026-11-12: Khảo sát MinIO (3 bucket). Đánh giá WQI và WQI-prediction. Viết đề xuất digital shadow (`de-xuat-digital-shadow-wqi.md`).
- 2026-11-13: Tải WQI nuôi-biển-2 từ 30/10 đến 12/11 (1.333 file). Chốt hướng: thư mục trên máy → chuẩn hoá → QC → Ditto. Chốt mô hình 1 Thing / trạm. Tạm hoãn Ditto và lưu trữ, làm chuẩn hoá và QC trước.
- 2026-11-13 23:10: Người dùng xác nhận khoá `salinity` là **độ dẫn điện mS/cm** (phát hiện từ quét ThingsBoard: dashboard GREEN-X quy đổi ra ppt ≈ 0,65 × giá trị thô). Kết luận cũ "độ mặn ~49 bất thường" bị huỷ. Khối Chuẩn hoá và QC chuyển sang trạng thái "cần sửa"; thêm quyết định §3.7–3.8. Dữ liệu MinIO/ThingsBoard đầy đủ ghi ở `data.md`.
- 2026-11-13: Viết xong pipeline batch `aquatwin-prototype/` (đọc → chuẩn hoá → QC, qc-0.1-provisional, obs-1.0). Chạy trên dữ liệu thật: 1.333 file → 6.665 observation (15 missing do sensor_error), 0 quarantine, 0 trùng, 1 gap 66 phút, 0 bất thường thời gian. Cờ suspect+fail: salinity 97,7% (chủ yếu site_plausible, mong muốn), pH 31,4% và turbidity 28,2% (chủ yếu flat_line), nhiệt độ 3,2%, DO 0,2%. 41 test pytest pass (gồm idempotency và replay lưu/nạp state). Kết quả: `aquatwin-prototype/output/qc_summary.md`.
- 2026-11-13 23:30: Chốt đơn vị các chỉ số còn lại theo cấu hình GREEN-X trên ThingsBoard (°C, pH, DO mg/L, NTU) – quyết định §3.9. Việc còn lại: đổi `unit_status` trong `config/parameters.yaml` từ `unconfirmed` sang `documented` (kèm `unit_source`) rồi chạy lại pipeline.
- 2026-11-13: Sửa pipeline theo đơn vị độ dẫn điện (obs-1.0 → **obs-1.1**, qc-0.1 → **qc-0.2-provisional**). `salinity` → `conductivity` (mS/cm, confirmed); thêm `practical_salinity` (PSU, estimated, PSS-78 qua `gsw` 3.6.23, p = 0 dbar, nhiệt độ đo cùng bản ghi). Kết quả: 6.665 observation đo + 1.330 dẫn xuất; suspect+fail độ dẫn điện 97,7% → 4,6% (còn lại do ROC 34, flat_line 25, spike 4); practical_salinity 17,8 / 29,8 / 31,4 PSU (min/trung vị/max), 100 giá trị kế thừa cờ 3. 8 đợt độ dẫn điện < 40 mS/cm, đa số khoảng 11h sáng. PSS-78 thấp hơn quy đổi GREEN-X (0,65×) khoảng 8%. 50 test pytest pass. Cấu hình cũ lưu ở `config/history/`.
- 2026-11-13 23:35: Xoá toàn bộ các prompt Claude Code (§8 Bước 1, §9 Bước 1b, §10 Bước 1c) khỏi file theo yêu cầu người dùng. File chỉ còn trạng thái, quyết định, câu hỏi mở, ghi chú và nhật ký.
- 2026-11-13 23:29 (giờ máy): Cập nhật `aquatwin-prototype/config/parameters.yaml` lên **params-1.2**: temperature (degC), pH (1), DO (mg/L), turbidity (NTU) chuyển `unit_status` từ `unconfirmed` sang `documented`, thêm `unit_source` ("ThingsBoard GREEN-X v6.0 + greenxAlertPolicy (quét 2026-11-13)…"); conductivity giữ `confirmed`. Chạy lại pipeline: số observation và cờ QC không đổi (6.665 đo + 1.330 dẫn xuất), chỉ đổi `unit_status`. 51 test pytest pass. Bản cũ lưu ở `config/history/params-1.1.yaml`.
- 2026-11-14: Thêm §8–§11 mô tả cách từng khâu của pipeline đang chạy (đọc, chuẩn hoá, QC gắn cờ, đầu ra/báo cáo), gồm bảng 6 bài kiểm tra QC, ngưỡng qc-0.2-provisional và cách tính cờ tổng hợp. §2 trỏ tới các mục này.
- 2026-11-14: Sắp xếp lại bố cục file theo yêu cầu người dùng, không thêm/bớt nội dung: §1 Mục tiêu (1.1) + Quyết định đã chốt (1.2, giữ số mục 1–9) · §2 Trạng thái các khối · §3–§8 chi tiết từng khối (§3 Dữ liệu nguồn ← §4 cũ, §4 Đọc ← §8 cũ, §5 Chuẩn hoá ← §9 cũ, §6 QC ← §10 cũ, §7 Lưu trữ/đầu ra ← §11 cũ, §8 Nạp liên tục ← §6 cũ) · §9 Câu hỏi mở ← §5 cũ · §10 Nhật ký ← §7 cũ. Các tham chiếu § trong phần nội dung đã đổi theo số mới; các mục nhật ký cũ giữ nguyên số § cũ.
- 2026-11-14: Thêm sơ đồ kiến trúc `images/kien-truc-digital-shadow.png` (từ `de-xuat-digital-shadow-wqi.md`) vào đầu file.
- 2026-11-14: Sắp các mục chi tiết theo 9 khối của sơ đồ kiến trúc: §3 MinIO · §4 Connector đọc dữ liệu (gộp "Đọc dữ liệu", "Kết nối trực tiếp MinIO" và "Nạp liên tục" – §4.3) · §5 Chuẩn hoá · §6 QC · §7 Twin – Eclipse Ditto · §8 Kho chuỗi thời gian (gồm đầu ra file hiện tại) · §9 Cảnh báo · §10 Dashboard · §11 Dự báo · §12 Câu hỏi mở · §13 Nhật ký. Khối chưa làm ghi "Hệ thống đề xuất" lấy từ sơ đồ, `de-xuat-digital-shadow-wqi.md` và `session_chat.md`; khối đã làm thêm phần đối chiếu với sơ đồ. Bảng §2 đổi theo 9 khối (thêm dòng Cảnh báo).
