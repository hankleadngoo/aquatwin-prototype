# AquaTwin – Prototype Observation Twin cho chất lượng nước (WQI)

> File này ghi **trạng thái hiện tại** của prototype: đang làm gì, đã chốt gì, phần nào để sau.
> Cập nhật file này mỗi khi xong một bước hoặc đổi quyết định.
> Quy tắc bắt buộc của dự án nằm trong `rule.md` (trích dẫn dạng R3.2, R8.3…).

Cập nhật lần cuối: 2026-11-14 (khối Dashboard chuyển sang giao diện web riêng: FastAPI chỉ đọc + HTML/CSS/JS, 4 màn)

![Kiến trúc đề xuất: mọi bản ghi qua QC trước khi vào twin, dự báo ghi riêng](images/kien-truc-digital-shadow.png)

*Sơ đồ kiến trúc đề xuất, lấy từ `de-xuat-digital-shadow-wqi.md`.*

---

## 1. Mục tiêu và các quyết định đã chốt

### 1.1. Mục tiêu và phạm vi

- **Mục tiêu**: dựng một Observation Digital Twin / digital shadow cho chất lượng nước, tương ứng **phase P1** trong `rule.md` §14.
- **Phạm vi hiện tại**: chỉ dữ liệu WQI (temperature, conductivity – khoá gốc `salinity`, pH, DO, turbidity). Chưa làm feeding event, video, hydrophone.
- **Chưa làm**: dự báo WQI. Theo R6.10, chỉ được đưa dự báo vào sau khi đã kiểm định độc lập.
- **Luồng dữ liệu đích**:
  thư mục dữ liệu trên máy → đọc → **chuẩn hoá** → **QC gắn cờ** → **lưu trữ** (TimescaleDB) → **twin Eclipse Ditto** → **giao diện web** (FastAPI + HTML, thay Grafana)
  Đã có bản batch cho cả chuỗi (14/11); chưa có nạp liên tục, cảnh báo, dự báo.

### 1.2. Quyết định đã chốt

1. **File JSON gốc là kho dữ liệu chính.** Không sửa, không xoá file gốc. Mọi kết quả đều tạo lại được bằng cách chạy lại từ file gốc.
2. **Nạp toàn bộ một lần ở giai đoạn này.** Code vẫn phải viết theo dạng xử lý từng bản ghi theo thứ tự thời gian, để sau này chuyển sang nạp liên tục mà không phải viết lại (§4.3).
3. **Mô hình twin (khi làm Ditto):** một Thing cho mỗi trạm đo WQI, ví dụ `aquatwin:nuoibien-2`. Mỗi chỉ số là một feature, thêm một feature `health`. Mỗi feature giữ giá trị mới nhất, `ts`, cờ QC và `last_good`.
4. **Ditto chỉ giữ trạng thái hiện tại.** Dữ liệu lịch sử và kết quả QC lưu ở file và kho chuỗi thời gian TimescaleDB (§8, chọn 14/11/2026).
5. **Cờ QC không phải ngưỡng cảnh báo.** Ngưỡng QC chỉ đánh giá chất lượng dữ liệu. Ngưỡng cảnh báo DO, nhiệt độ, độ mặn phải do trại duyệt (R8.3). Prototype không phát cảnh báo cho cá.
6. **Không tự suy ra đơn vị, độ sâu hay hiệu chuẩn (R3.5).** Mọi giả định đều phải ghi trong file cấu hình có phiên bản, kèm nguồn; cái gì không có nguồn thì đánh dấu `unconfirmed`.
7. **Khoá `salinity` trong dữ liệu là độ dẫn điện, đơn vị mS/cm** (người dùng xác nhận 13/11/2026 22:31). Trong pipeline: tham số chuẩn là `conductivity` (`unit: mS/cm`, `unit_status: confirmed`, giữ `raw_key: salinity` để truy vết). Độ mặn thực tế (PSU) nếu cần thì là **giá trị dẫn xuất** tính từ độ dẫn điện + nhiệt độ theo PSS-78, ghi rõ công thức, phiên bản và nhiệt độ dùng để tính (R3.6). Trên ThingsBoard giữ nguyên khoá `salinity` và các dashboard.
8. **Ngưỡng cảnh báo ThingsBoard (`greenxAlertPolicy`) tách biệt với ngưỡng QC** và không đưa vào pipeline QC (xem `session_chat.md` §1).
9. **Đơn vị các chỉ số còn lại lấy theo cấu hình GREEN-X trên ThingsBoard** (dashboard GREEN-X Nuôi Biển v6.0 và policy cảnh báo `greenxAlertPolicy`; người dùng đồng ý 13/11/2026 23:25): temperature **°C**, pH **không đơn vị**, DO **mg/L**, turbidity **NTU**, pdo (HonMun_1) **% bão hoà**; `salinity` = độ dẫn điện **mS/cm** (đã xác nhận). Trạng thái trong config: `unit_status: documented`, `unit_source: "ThingsBoard GREEN-X v6.0 + greenxAlertPolicy (quét 2026-11-13)"`. Lưu ý: ThingsBoard **không lưu đơn vị trong telemetry**, đơn vị chỉ nằm ở cấu hình widget/policy và các dashboard cũ ghi không thống nhất (vd DEMO 2 ghi DO "%") – chỉ dùng GREEN-X làm nguồn. Kiểm tra datasheet cảm biến là việc phụ, không chặn prototype.
10. **`estimated` theo *Digital Twin Platform Design (EN)*** (người dùng yêu cầu 14/11/2026): estimated là trạng thái **suy ra từ số đo + mô hình** ("State inferred from measurements and models", bảng loại trạng thái Ch. 3). Mỗi giá trị estimated phải kèm mô hình có phiên bản và đầu vào (Bảng 5.21, R2.4), độ bất định và nguồn gốc hiệu chuẩn (Bảng 5.6 "Associate uncertainty and calibration provenance"). Chuỗi lấy mẫu lại theo lưới 15 phút chỉ được coi là estimated khi có mô hình nội suy có phiên bản và độ bất định đi kèm (`de-xuat-digital-shadow-wqi.md` đã sửa theo định nghĩa này).

## 2. Trạng thái các khối

| Khối (theo sơ đồ) | Trạng thái | Ghi chú |
|---|---|---|
| MinIO (nguồn hiện có) | ✅ Đọc trực tiếp qua S3 API (15/11) | Chi tiết §3. Bucket `nuoi-bien-2-data`, mirror `aquatwin-prototype/data/minio/` 1.368 file 30/10–13/11/2026; MinIO không có file WQI mới sau 13/11 08:42. Bản tải tay `Data MinIO/` (1.333 file) giữ nguyên |
| Connector đọc dữ liệu | ✅ Xong (batch) · ✅ kết nối trực tiếp MinIO (15/11) · ✅ chạy định kỳ 15 phút (`--loop`, 15/11) · ⏸ nạp theo sự kiện / dịch vụ nền để sau | Chi tiết §4. `run_connector.py` + `src/aquatwin/minio_source.py` (`config/minio.yaml` `connector-1.0`): key chỉ đọc, tải object mới theo tên key về mirror, `--pipeline` chạy tiếp batch → kho → twin. `reader.py`: chỉ đọc, sha256 từng file, iterator theo event time, nhiều site |
| Chuẩn hoá | ✅ Xong (obs-1.2) | Chi tiết §5. Long format, `event_id` UUIDv5, quarantine (R3.4), khử trùng (R4.4). Khoá `salinity` → tham số `conductivity` (mS/cm, **confirmed**, giữ `raw_key`, quy tắc `map-salinity-to-conductivity-1.0`). Thêm `practical_salinity` (PSU, `state_kind = estimated`, PSS-78 qua `gsw`, p = 0 dbar giả định, có `derived_from` + `transform`; từ obs-1.2 kèm `uncertainty`, `model_validity`, `calibration_provenance` theo Platform Design – §1.2 mục 10). 1.333 file → 6.665 observation đo + 1.330 dẫn xuất, 0 quarantine. Đơn vị (params-1.3, đơn vị như params-1.2): conductivity **confirmed**; temperature °C, pH, DO mg/L, turbidity NTU **documented** theo GREEN-X kèm `unit_source` (§1.2 mục 9) |
| QC gắn cờ | ✅ Xong (qc-0.3-provisional) | Chi tiết §6. Ngưỡng `conductivity` (mS/cm): gross [0, 80], site_plausible [30, 60], spike 5/10, ROC 7,5/h. Suspect+fail của độ dẫn điện: 97,7% → **4,6%**. `practical_salinity` không chạy test chuỗi riêng, kế thừa cờ xấu nhất của 2 đầu vào; từ qc-0.3 ngoài phạm vi hợp lệ PSS-78 → hạ cờ 3. 50 test pytest pass. Ngưỡng vẫn **provisional** |
| Twin – Eclipse Ditto | 🔨 Đang làm (đã có dữ liệu) | Chi tiết §7. Ditto 3.9.8 chạy bằng Docker trên localhost; Thing `aquatwin:nuoibien-2` đã nhận dữ liệu 30/10–12/11 qua projector (`twin-proj-1.1`): replay 1.333 bản ghi, trạng thái khớp observations, chạy lại không đổi (412). Kiểm thử R4.4 (trùng, đến muộn, mất kết nối rồi phát lại) pass trên Ditto giả lập và Ditto thật. Chưa chạy liên tục, `stale` chỉ tính lúc chiếu. Mô hình theo §1.2 mục 3–4 |
| Kho chuỗi thời gian (lưu trữ) | ✅ Xong (batch, `tsdb-1.0`) | Chi tiết §8. TimescaleDB 2.31.0 / PostgreSQL 18 chạy Docker trên localhost (người dùng chọn 14/11). Hypertable `aquatwin.observation` giữ toàn bộ lịch sử có revision (nạp lại không trùng, nội dung khác → revision mới, bản cũ giữ lại), bản ghi đến muộn vào đúng chỗ trong lịch sử; view hiện hành, `observation_as_of` cho backtest, lưới 15 phút. Nạp 7.995 observation, đối chiếu khớp. File Parquet/CSV vẫn xuất như cũ |
| Cảnh báo | ⏸ Chưa làm | Chi tiết §9 (hệ thống đề xuất). Prototype không phát cảnh báo (§1.2 mục 5) |
| Dashboard | ✅ Xong (batch, giao diện web riêng `web-1.0`; Grafana `dashboard-1.0` không phát triển tiếp) | Chi tiết §10. **Từ 14/11 (tối): giao diện web riêng** – FastAPI chỉ đọc + HTML/CSS/JS, `127.0.0.1:8090`, 4 màn (Tổng quan, Chỉ số, Chất lượng dữ liệu, Truy vết & cảnh báo), thế giới hình ảnh "bảng phấn chợ cá", số cũ hiện mờ + dải vàng, cờ bằng hình nét + chữ; 103 test pass. Trước đó: Grafana OSS 13.2.6 + plugin Infinity 4.1.4 chạy Docker trên localhost, chỉ đọc. Trạng thái hiện tại + cờ QC đọc từ twin Ditto (observed và estimated tách riêng, `health`); lịch sử theo cờ, khoảng trống, phân bố cờ, bài QC, cách ly, các lần nạp đọc từ kho TimescaleDB (role chỉ SELECT). Nhật ký cảnh báo: chưa có (khối Cảnh báo chưa làm). Không có ngưỡng cảnh báo. 22 panel chạy qua API: 0 lỗi |
| Dự báo WQI | ⛔ Chưa làm | Chi tiết §11 (hệ thống đề xuất). R6.10 |

> Các mục §3–§11 tương ứng 9 khối trong sơ đồ ở đầu file. Mỗi mục có phần **Hiện tại** (đã làm) và/hoặc **Hệ thống đề xuất** (chưa thực hiện, lấy từ sơ đồ và `de-xuat-digital-shadow-wqi.md`). Phần "Hiện tại" của §4–§6 và §8 mô tả **cách pipeline `aquatwin-prototype/` đang chạy** (phiên bản hiện tại: schema `obs-1.2`, `params-1.3`, `qc-0.3-provisional`). Khi đổi code hoặc config của khâu nào thì sửa mục của khâu đó. Mọi ngưỡng, đường dẫn, múi giờ nằm trong `aquatwin-prototype/config/`, không viết cứng trong code.

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

### 3.2. Đọc trực tiếp từ MinIO (đã làm 15/11)

- **Truy cập:** cần VPN 10.7.x.x. S3 API `10.7.0.27:9000` (console `:9090` chỉ để xem). Không cho đọc ẩn danh. Console trên máy chủ là bản cộng đồng rút gọn (chỉ Object Browser) → access key tạo bằng `mc` (`minio-mc` từ Homebrew core; bản `minio/stable` lỗi 410).
- **Key `aquatwin-connector`:** chỉ `s3:ListBucket`, `s3:GetBucketLocation`, `s3:GetObject` trên `nuoi-bien-2-data` (`aquatwin-prototype/connector/minio-readonly-policy.json`), cha là tài khoản admin `icclab`, không hết hạn. Lưu ở `connector/.env` (chmod 600, gitignore). Đã thử: đọc được bucket này, bucket khác và lệnh admin bị từ chối.
- **Trạng thái dữ liệu (15/11):** NB2 có 165 thư mục ngày (27/05 → 13/11), file WQI cuối `2026-11-13/WQI/20261113-08-42-59.json`; NB1 dừng 02/11. Giờ upload (`last_modified`) không tăng theo thứ tự tên file.

Phần còn đề xuất:

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

### 4.1b. Connector MinIO (đã làm 15/11)

- **Code / config:** `run_connector.py`, `src/aquatwin/minio_source.py`, `config/minio.yaml` (`connector-1.0`: endpoint, bucket, prefix `{day}/WQI/`, regex key, `start_date` 2026-10-30, `lookback_days` 2). Key đọc từ biến môi trường hoặc `connector/.env`, không nằm trong code / config.
- **Cách chạy:** `--check` (kết nối + quyền), `--dry-run` (liệt kê, không tải), mặc định tăng dần (ngày mới + `lookback_days` ngày cuối đã đồng bộ), `--full` (liệt kê lại từ `start_date`), `--pipeline` (có file mới → `run_batch.py` → `run_tsdb.py` → `run_twin.py`).
- **Quy tắc:** chỉ gọi `list_objects` / `get_object`. So **theo tên key**; key mới → tải, kiểm tra kích thước, ghi nguyên byte vào `data/minio/<bucket>/<key>` (ghi tạm rồi đổi tên, chế độ chỉ đọc). Key đã có, etag khác → `conflicts`, không ghi đè. Key có trong trạng thái nhưng mất trên MinIO → `missing_upstream`, không xoá bản đã tải. Key không đúng mẫu → `unexpected_keys`.
- **Trạng thái / báo cáo:** `data/minio/_state/<bucket>.state.json` (etag, sha256, last_modified, fetched_at từng object), `data/minio/_state/sync_log.jsonl`, `output/minio_sync_report.json`.
- **Reader:** mỗi nguồn trong `source.yaml` có thể có `file_glob` riêng (mirror: `*/WQI/*.json`); thư mục ngày = cấp đầu tiên dưới thư mục nguồn. Nguồn mặc định (`source-1.1`) là mirror; `source_file` giờ chứa nguyên bucket/key.
- **Lần chạy đầu (15/11):** 1.368 object (1.333 trùng byte với `Data MinIO/` + 35 file 13/11 00:09–08:42), ~29 s, 0 lỗi. Chạy lại: 0 mới. Batch 8.205 observation (thêm 210), 0 time anomaly. Kho: 210 mới + 7.995 revision mới (chỉ đổi `source_file`; 5 dòng lúc 12/11 23:54 đổi `spike` 2 → 1 vì nay có điểm kế tiếp), khớp. Twin áp dụng 35 bản ghi, khớp. 11 test mới (2 test `minio` dùng MinIO thật), tổng 113 pass.
- **Chạy định kỳ (15/11):** `run_connector.py --loop` mỗi `schedule.interval_s` = 900 s, có file mới thì chạy batch → kho → twin; lỗi một lần chạy không dừng vòng lặp; khoá file chặn chạy chồng. Đang chạy trong tab terminal của app (bắt đầu 15/11 12:52) → dừng khi đóng tab / tắt máy. Chưa thành dịch vụ nền (launchd): tiến trình nền đọc thư mục Desktop cần cấp quyền macOS riêng.
- **Chưa làm:** `received_at` từ `last_modified` (§5.2); nạp theo sự kiện (bucket notification) và chạy pipeline tăng dần thay vì batch lại toàn bộ (§4.3); NB1.

### 4.2. Hệ thống đề xuất (theo sơ đồ)

| Chức năng trong sơ đồ | Tình trạng |
|---|---|
| Phát lại lịch sử theo `ts` | ✅ Đã làm ở chế độ batch (sắp theo thời gian sự kiện, kiểm tra replay lưu/nạp state) |
| Đọc file mới mỗi 15 phút | ✅ `run_connector.py --loop` (15/11, §4.1b); pipeline vẫn batch lại toàn bộ mỗi khi có file mới |
| Khoá chống trùng | ✅ Đã làm: `event_id` UUIDv5 từ (site_id, sensor_id, phenomenon_time, parameter), bản trùng ghi vào `duplicates.csv` (§5) |
| Hàng lỗi | Một phần: bản ghi sai schema vào `output/quarantine.csv` (§5). Chưa có hàng lỗi (dead-letter) cho chạy liên tục |
| Đọc trực tiếp từ MinIO | ✅ Đã làm 15/11 (§4.1b), chạy định kỳ 15 phút |

- Đề xuất trong `de-xuat-digital-shadow-wqi.md`: khi chạy thời gian thực cho site 2, đọc file mới mỗi 15 phút và đo độ trễ từ lúc đo đến lúc twin cập nhật; nếu quá 30 phút (gấp đôi chu kỳ 15 phút) không có số đo mới thì trạng thái chuyển sang *stale*.

### 4.3. Nạp liên tục / thời gian thực – đã có bản polling 15 phút (15/11), còn phần nâng cấp

**Đang chạy:** `run_connector.py --loop` hỏi MinIO mỗi 900 s (`config/minio.yaml` `schedule`); có file mới thì chạy `run_batch` → `run_tsdb` → `run_twin` (chi tiết §4.1b). Đây là **polling theo lô nhỏ**, chưa phải luồng sự kiện.

| Yêu cầu | Tình trạng |
|---|---|
| Lấy dữ liệu mới định kỳ | ✅ Polling 15 phút, so theo tên key; lỗi một lần (mất VPN…) không dừng vòng lặp; khoá chống chạy chồng |
| Idempotency (R4.2, R4.3) | ✅ `event_id` tất định; kho bỏ qua dòng không đổi; connector không tải lại key đã có |
| Dữ liệu đến trễ (R4.4) | ✅ Một phần: connector liệt kê lại `lookback_days` = 2 ngày cuối; kho ghi **revision mới** khi lịch sử đổi (bản cũ giữ lại); twin bỏ qua bản ghi không mới hơn trạng thái hiện tại → không bị kéo lùi. Chưa có watermark khai báo chính thức |
| Spike cần giá trị kế tiếp | ✅ Xử lý qua revision: điểm cuối mang `spike` = 2 (chưa đánh giá) tới khi có điểm sau, rồi được sửa (đã thấy 15/11: điểm 12/11 23:54 `spike` 2 → 1) |
| `stale` theo đồng hồ thật | ✅ API web tính tuổi dữ liệu theo giờ thật (`age_s`, ngưỡng `stale_after_s` trong `twin.yaml`). Twin Ditto vẫn ghi `stale` tại lúc chiếu |
| Pipeline xử lý tăng dần | ⏸ Chưa: mỗi khi có file mới pipeline vẫn batch lại toàn bộ (vài giây với ~1.400 file; ~35.000 file/năm sẽ chậm). Đã chuẩn bị: iterator, hàm chuẩn hoá thuần, trạng thái QC / `Processor` lưu-nạp được (`to_dict` / `from_dict`) |
| Nạp theo sự kiện | ⏸ Chưa: MinIO bucket notification (cần đổi cấu hình máy chủ – quyền admin) hoặc MQTT |
| Hàng lỗi (dead-letter) | ⏸ Chưa: lỗi tải từng object nằm trong báo cáo connector, ngày có lỗi được liệt kê lại lần sau; chưa có hàng lỗi riêng |
| Chạy không phụ thuộc máy cá nhân | ⏸ Chưa: vòng lặp sống theo tab terminal trên máy người dùng. Hướng đề xuất: đóng gói `docker compose` (connector, web, TimescaleDB, Ditto) và chạy trên máy chủ nội bộ cùng mạng MinIO |
| Thông số nguồn theo R4.1 | Một phần: có `phenomenon_time` (từ `ts`, GMT+7 đã kiểm chứng), `ingest_time`; **chưa có** `received_at` (đề xuất lấy `last_modified` trên MinIO), chất lượng đồng hồ (NTP?), độ trễ tối đa chấp nhận được, watermark |

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
  - công thức PSS-78: `gsw.SP_from_C(conductivity mS/cm, water_temperature °C, p)`, phiên bản `pss78-gsw-1.1` (giá trị tính ra như 1.0, chỉ thêm thông tin đi kèm);
  - giả định p = 0 dbar (chưa biết độ sâu); `temperature_compensated: unknown` → dùng nhiệt độ đo (nếu sau này là `true` thì dùng 25 °C);
  - `derived_from` = event_id của 2 đầu vào, `transform` = tên + phiên bản + giả định;
  - không tạo nếu thiếu/null một đầu vào; bật/tắt bằng `derived.practical_salinity.enabled`;
  - **thông tin estimated theo Platform Design** (obs-1.2, §1.2 mục 10; 4 cột mới, observed để null):
    - `uncertainty` (PSU, k=1) + `uncertainty_status`: lan truyền bậc nhất (GUM) qua đạo hàm số của `gsw.SP_from_C`, từ độ bất định chuẩn của từng đầu vào trong `derived.practical_salinity.uncertainty.inputs` (`unconfirmed`). Hiện chưa có sai số cảm biến nên các giá trị đầu vào là `null` → `uncertainty = null`, `uncertainty_status = "unavailable: thiếu độ bất định đầu vào …"` cho cả 1.330 giá trị; không tự đặt số (R3.5);
    - `model_validity`: phạm vi xác định của PSS-78 (UNESCO 1981, `documented`): SP 2–42, t −2–35 °C, p 0–10000 dbar → `in_range` / `out_of_range: …`; từ qc-0.3 `out_of_range` → hạ cờ 3 (§6.1). Dữ liệu 30/10–12/11: 1.330/1.330 `in_range`;
    - `calibration_provenance` (JSON): `calibration_ref` các đầu vào (hiện chưa có → `inputs_without_calibration_ref`), `temperature_compensated`, `pressure_dbar` + `pressure_status`, `status = unknown`.

### 5.2. Đối chiếu với sơ đồ

- 1 bản ghi → 5 observation: ✅ (cộng 1 giá trị dẫn xuất `practical_salinity`).
- Gắn đơn vị, sensorId: ✅ (`unit`, `unit_status`, `unit_source`; `sensor_id` từ `device`).
- `ts` + 07:00: ✅ theo múi giờ trong `config/source.yaml` (`Etc/GMT-7`).
- `receivedAt`: ⏸ chưa có – file trên máy không có thông tin này nên đang để null. Đề xuất trong `de-xuat-digital-shadow-wqi.md`: lấy `last_modified` của file trên MinIO.

## 6. Khối QC gắn cờ

### 6.1. Hiện tại (đã làm)

- **Code / config:** `src/aquatwin/qc.py` (`QCEngine`); `config/qc.yaml` (`qc_version: qc-0.3-provisional`; ngưỡng chỉ số đo như qc-0.2). Bản cũ lưu ở `config/history/`.
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
- **`practical_salinity`:** không chạy các test chuỗi riêng (tránh đếm trùng), nhận cờ xấu nhất của conductivity và water_temperature theo thứ tự 9 > 4 > 3 > 2 > 1. Từ **qc-0.3** (người dùng duyệt 14/11) có thêm test `model_validity`: giá trị ngoài phạm vi hợp lệ PSS-78 (`model_validity = out_of_range`) → cờ 3 (`qc.yaml → estimated.model_validity_out_of_range_flag`), trong phạm vi → 1; cờ cuối = xấu nhất của cờ kế thừa và test này. Hạ cờ không loại bỏ giá trị: vẫn lưu, vẫn chiếu vào twin. Dữ liệu 30/10–12/11: 1.330/1.330 trong phạm vi → cờ không đổi (1.230 cờ 1, 100 cờ 3 kế thừa).
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

- **Ditto 3.9.8 chạy bằng Docker Compose** trong `aquatwin-prototype/ditto/` (bộ `deployment/docker` chính thức, sửa tối thiểu, các chỗ sửa đánh dấu `AQUATWIN:`; bản gốc lưu ở `docker-compose.upstream-3.9.8.yml`). Phiên bản ghim trong `ditto/.env`; tên project Docker `aquatwin-ditto`.
  - 9 container: mongodb, policies, things, things-search, connectivity, gateway, ditto-ui, swagger-ui, nginx. RAM dùng khoảng 2,2 GB.
  - Chỉ mở trên `127.0.0.1` (8080 nginx, 8081 gateway, 27017 MongoDB). Dữ liệu MongoDB lưu trong volume `aquatwin-ditto_aquatwin_mongodb_data`.
  - Đăng nhập: user mẫu `ditto`/`ditto` của bộ docker chính thức (nginx basic auth) – chỉ dùng trên localhost; truy cập không đăng nhập → 401.
  - Trang `/apidoc/` không có file OpenAPI (đã bỏ mount trỏ vào repo Ditto).
- **Policy + Thing khung `aquatwin:nuoibien-2`** tạo bằng `ditto/bootstrap_things.py` (chạy lại được, lần 2 trả 204):
  - attributes: `site_id`, `sensor_id`, `source_authority`, `schema_version`, `params_version`, `qc_version`, `state_kinds`; `unit_id`, `depth_m`, `location` = null (R3.5);
  - feature cho 5 chỉ số đo (`unit`, `unit_status`, `raw_key`, `observed`, `last_good`), feature `practical_salinity` (`estimated`) và `health` – **chưa có dữ liệu**.
- **Projector** (`src/aquatwin/twin.py`, `run_twin.py`, cấu hình `config/twin.yaml`, `projection_version: twin-proj-1.1`):
  - đọc `output/observations.parquet`, gom thành bản ghi (site, sensor, phenomenon_time) theo thứ tự thời gian, mỗi bản ghi → một JSON merge-patch vào Thing;
  - **cập nhật có điều kiện** (RQL): chỉ áp dụng khi `ts` mới hơn `features/health/properties/last_record_ts` → bản ghi trùng / đến muộn bị Ditto trả 412, trạng thái hiện tại không lùi (R4.2, R4.4);
  - feature mỗi chỉ số: `observed` (giá trị, đơn vị, `ts`, `quality_flag`, `qc_tests`, `qc_version`, `event_id`, `source_file`, `device_error`) và `last_good` (chỉ khi cờ ∈ `last_good_flags`, hiện `[1]` – đề xuất 14/11, người dùng đồng ý khi yêu cầu viết projector); `practical_salinity` ghi vào nhóm `estimated` (kèm `derived_from`, `transform`, và từ `twin-proj-1.1`: `uncertainty`, `uncertainty_status`, `model_validity`, `calibration_provenance`); `predicted` chưa dùng (R6.10);
  - feature `health`: `last_record_ts`, `last_record_local`, `last_source_file`, `gap_before_s`, `device_error`, `stale` (= quá 1.800 s so với lúc chiếu), `stale_checked_at`, `projection_version`;
  - merge-patch: `null` = xoá khoá → bản ghi `sensor_error` xoá `observed.value` cũ, `last_good` giữ nguyên.
- **Kết quả replay lại sau obs-1.2 / twin-proj-1.1** (14/11): chạy lại `bootstrap_things.py` (attributes `obs-1.2`, `params-1.3`) rồi replay: 1.333/1.333 áp dụng, đối chiếu **khớp**; chạy lại → 1.333 bỏ qua.
- **Kết quả replay** (14/11, twin-proj-1.0): 1.333 bản ghi (7.995 observation) áp dụng trong ~16 s; đối chiếu trạng thái twin với giá trị cuối trong observations: **khớp**. Chạy lại: 0 áp dụng, 1.333 bỏ qua (412). `stale = true` vì dữ liệu dừng ở 12/11. Báo cáo: `output/twin_replay_report.json`.
- **Kiểm thử** (`tests/test_twin.py`, 13 test): dựng patch; trùng → 1 cập nhật; đến muộn → không lùi; `sensor_error`; trạm chưa khai báo không bị bỏ im lặng; replay dữ liệu thật khớp + idempotent; mất kết nối rồi phát lại (chồng lấn) = chạy liên tục; và `pytest -m ditto` với Ditto thật trên Thing tạm (tự xoá). Toàn bộ 64 test pass (sau obs-1.2: 69 test, thêm 4 test estimated ở `test_normalize.py` và 1 ở `test_twin.py`).
- Chưa làm: chạy liên tục (nhận bản ghi mới thay vì đọc parquet), tính lại `stale` theo đồng hồ thật định kỳ, ghi bản ghi đến muộn vào kho chuỗi thời gian (§8), Thing cho site 1, đổi tài khoản mặc định trước khi mở ra mạng. Cách chạy: `aquatwin-prototype/README.md` mục "Twin – Eclipse Ditto".

### 7.2. Hệ thống đề xuất (chưa thực hiện)

- Theo sơ đồ: Thing cho site-1, site-2; tách trạng thái `observed` · `estimated` · `predicted` (tách riêng); twin giữ **trạng thái mới nhất**. Nhận dữ liệu đã qua QC; gửi tiếp sang kho chuỗi thời gian, cảnh báo, dashboard; dự báo ghi vào phần `predicted`.
- Mô hình đã chốt: một Thing cho mỗi trạm đo WQI, mỗi chỉ số là một feature, thêm feature `health`; mỗi feature giữ giá trị mới nhất, `ts`, cờ QC và `last_good` (§1.2 mục 3). Ditto chỉ giữ trạng thái hiện tại (§1.2 mục 4).
- Theo `de-xuat-digital-shadow-wqi.md`: mỗi site có một `twinId` chuẩn duy nhất (R1.1); khi có thông tin lồng hoặc độ sâu thì thêm Thing con. Tách loại trạng thái (R2.1, R2.2): `observed` = số đo thô kèm cờ; `estimated` = giá trị suy ra từ số đo + mô hình, kèm mô hình, đầu vào, độ bất định và nguồn gốc hiệu chuẩn (theo *Digital Twin Platform Design (EN)*, §1.2 mục 10; đề xuất đã sửa 14/11); `predicted` = dự báo kèm `modelRef`, phiên bản và ảnh chụp dữ liệu đầu vào (R2.4). Chưa dùng `simulated` và `desired`.
- Hiện có: `practical_salinity` (§5). Nếu sau này thêm chuỗi lấy mẫu lại theo lưới 15 phút thì cũng ghi vào nhóm `estimated`, với `transform` là mô hình nội suy có phiên bản và có độ bất định riêng.
- Ditto lưu: trạng thái hiện tại, journal sự kiện + snapshot trên MongoDB, search index; lịch sử giới hạn – chuỗi thời gian phải đẩy ra cơ sở dữ liệu riêng (`session_chat.md`).
- Kiểm thử đề xuất khi dựng (`de-xuat-digital-shadow-wqi.md`, lộ trình bước 3): đăng ký 2 Thing, phát lại lịch sử site 2 rồi site 1; kiểm thử các kịch bản R4.4 (bản ghi trùng, bản ghi đến muộn, mất kết nối rồi nối lại).

## 8. Khối Kho chuỗi thời gian (lưu trữ)

### 8.1. Đầu ra file và báo cáo (pipeline)

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

### 8.2. Kho TimescaleDB (đã làm 14/11, batch)

- **Yêu cầu theo sơ đồ:** lưu **toàn bộ lịch sử + cờ QC**, **sửa dữ liệu đến muộn** (sửa lịch sử nhưng không kéo trạng thái hiện tại lùi lại – R4.4), là **nguồn cho backtest** (kiểm định dự báo). `de-xuat-digital-shadow-wqi.md` gợi ý TimescaleDB hoặc InfluxDB.
- **Lựa chọn:** TimescaleDB thay vì InfluxDB (người dùng chọn 14/11/2026). Lý do chính: cần truy vết, sửa lịch sử không mất bản cũ và nạp lại không trùng – làm được trực tiếp bằng ràng buộc SQL; InfluxDB ghi đè điểm cùng series + thời điểm (mất bản cũ), không có UNIQUE/transaction, khó lưu cột JSON truy vết. Lợi thế tốc độ ghi của InfluxDB không cần ở quy mô này (< 250.000 dòng/năm/trạm).
- **Hạ tầng:** `aquatwin-prototype/timescale/docker-compose.yml`, image `timescale/timescaledb:2.31.0-pg18` (bản đầy đủ, Timescale License), chỉ mở `127.0.0.1:5432`, telemetry tắt, volume `aquatwin_tsdb_data`, project Docker `aquatwin-tsdb`. Mật khẩu sinh ngẫu nhiên trong `timescale/.env` (không commit).
- **Cấu hình:** `config/tsdb.yaml` (`tsdb-1.0`): kết nối, schema `aquatwin`, chunk 7 ngày, lưới 15 phút, cờ tốt `[1]`. Schema SQL: `src/aquatwin/sql/tsdb_schema.sql` (chạy lại an toàn). Code: `src/aquatwin/tsdb.py`, chạy `run_tsdb.py`.
- **Bảng và view (schema `aquatwin`):**
  - `observation` – hypertable theo `phenomenon_time`, đủ cột `obs-1.2` (JSONB cho `qc_tests`, `derived_from`, `calibration_provenance`) + `revision`, `is_current`, `content_sha256`, `ingest_run_id`, `loaded_at`, `superseded_at`; khoá `(event_id, phenomenon_time, revision)`, mỗi `event_id` chỉ một revision hiện hành;
  - `ingest_run` – mỗi lần nạp: nguồn + sha256, manifest pipeline, phiên bản schema/QC, số dòng mới / sửa / giữ nguyên (R6.6, R12.5);
  - `quarantine` – bản ghi bị cách ly kèm nội dung thô (R3.4);
  - `observation_current` – revision hiện hành; `observation_as_of(ts)` – lịch sử như đã biết tại `ts` (backtest không nhìn trước); `observation_grid` – thống kê khung 15 phút UTC chỉ từ giá trị cờ 1 (`n_total`, `n_good`, mean/min/max, số cờ 3/4/9). Lưới là thống kê, **không** phải trạng thái estimated (§1.2 mục 10).
- **Quy tắc nạp** (một transaction, khoá bảng để không có hai loader chạy cùng lúc): `event_id` mới → revision 1; nội dung (mọi cột trừ `ingest_time`, băm sha256) giống revision hiện hành → bỏ qua; khác → revision mới hiện hành, revision cũ giữ lại với `is_current = false`. Bản ghi đến muộn được ghi vào lịch sử ở đúng `phenomenon_time` (khác twin: twin bỏ qua để không lùi trạng thái – R4.4). Kho không đổi giá trị, cờ hay đơn vị.
- **Kết quả (14/11):** nạp 7.995 observation (6.665 observed + 1.330 estimated, 30/10–12/11) trong ~0,6 s, 3 chunk; đối chiếu nội dung với `observations.parquet`: **khớp**. Nạp lại: 0 mới, 7.995 giữ nguyên. Báo cáo: `output/tsdb_load_report.json`.
- **Kiểm thử** (`tests/test_tsdb.py`, 9 test; `pytest -m tsdb` chạy trên schema tạm `aquatwin_test_*` tự xoá): băm nội dung bỏ qua `ingest_time`; JSON chuẩn hoá thứ tự khoá; chặn `event_id` trùng và tên schema/khoảng chunk lạ; nạp lại không trùng (kể cả sau khi chạy lại pipeline); bản ghi đến muộn lấp lịch sử; đổi nội dung → revision 2, bản cũ còn, `observation_as_of` trả bản cũ, đổi lại → revision 3; lưới chỉ đếm cờ 1; quarantine nạp một lần. Tổng 79 test pass.
- **Chưa làm:** nạp liên tục (cùng với connector §4.3); nén chunk cũ và continuous aggregate (dữ liệu còn nhỏ; nén làm việc sửa revision chậm hơn); chính sách lưu giữ / sao lưu; nối backtest dự báo (§11) vào kho. Dashboard (§10) đã đọc kho từ 14/11.

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

### 10.0. Giao diện web riêng (đã làm 14/11 tối – thay Grafana)

- **Quyết định:** người dùng chọn tự làm giao diện thay Grafana (Grafana chỉ là lớp hiển thị; UI riêng tuỳ biến được cho người vận hành trại). Người dùng chọn: phục vụ **cả** người vận hành trại (điện thoại, ngoài trời) và nhóm kỹ thuật (máy tính); **4 màn**; dữ liệu cũ **vẫn hiện nhưng mờ + thông báo rõ**; công nghệ để Claude chọn; thế giới hình ảnh **"bảng phấn chợ cá"** (chọn trong 3 phương án: bảng phấn, hải đồ, dashboard IoT chuẩn). Ghi trong `aquatwin-prototype/PRODUCT.md` và `.impeccable/surfaces/web-index-html.md`.
- **Công nghệ:** FastAPI chỉ đọc (`src/aquatwin/webapi.py`, `run_web.py`, `config/web.yaml` `web-1.0`) phục vụ cả API JSON và trang tĩnh `web/static/` (HTML/CSS/JS thuần, không Node, không bước build; biểu đồ SVG tự vẽ; chữ Be Vietnam Pro OFL tự host). Chỉ `127.0.0.1:8090`. Kho đọc bằng role `aquatwin_web` (chỉ SELECT, transaction READ ONLY; mật khẩu ngẫu nhiên trong `web/.env`, không commit); twin đọc bằng GET.
- **Không có ngưỡng trong web.yaml:** khoảng trống từ `source.yaml`, dữ liệu cũ từ `twin.yaml`, cờ từ `qc.yaml`, đơn vị từ `parameters.yaml`, schema từ `tsdb.yaml`; JS lấy mọi ngưỡng / múi giờ qua `/api/meta` (có test chặn viết cứng). Không có ngưỡng cảnh báo cho cá (R8.3).
- **4 màn:**
  1. *Tổng quan*: dải tuổi dữ liệu theo đồng hồ thật (vàng khi cũ: "Số đo cách đây 1 ngày 23 giờ – không phải hiện tại"); 5 dòng observed + dòng estimated riêng (độ mặn PSS-78, "suy ra từ độ dẫn điện + nhiệt độ"), mỗi dòng: số lớn, đơn vị, dấu cờ (hình nét + chữ + lý do QC), giờ, "tốt gần nhất" khi cờ không tốt, nét 48 giờ; số cũ hiển thị như phấn lau dở (vẫn đọc được); tình trạng thiết bị / twin (độ sâu, lồng: "chưa biết"); nhật ký cảnh báo "chưa có".
  2. *Chỉ số*: chọn chỉ số + khoảng (24 giờ … toàn bộ, neo ở bản ghi mới nhất); biểu đồ: đường = cờ tốt, ký hiệu theo cờ, khoảng trống tô sọc vàng, điểm hỏng ngoài thang kẹp ở mép kèm giá trị thật; chú giải có số đếm; thông tin đơn vị (trạng thái + nguồn), mô hình và độ bất định (chưa có) cho estimated; bảng điểm không tốt; revision cũ bị gạch.
  3. *Chất lượng dữ liệu*: bản ghi, observation, % cờ tốt (87,3%), khoảng trống (1), lỗi thiết bị (3), cách ly (0); cờ theo ngày (GMT+7); cờ theo chỉ số; bài QC gây cờ xấu; khoảng trống; lỗi thiết bị; cách ly.
  4. *Truy vết & cảnh báo*: nhật ký cảnh báo (chưa có), phiên bản đang chạy, thuộc tính twin, kho (dòng hiện hành / revision cũ), các lần nạp.
- **Kiểm thử** (`tests/test_web.py`, 12 test): meta lấy từ config và không có ngưỡng cảnh báo; tuổi dữ liệu theo đồng hồ thật; observed / estimated tách; 404 / 400 / 503 / 405 (chỉ GET); trang tĩnh phục vụ, `.env` không lộ; JS không viết cứng ngưỡng / múi giờ; `-m tsdb`: số điểm và số cờ mỗi chỉ số, tổng / cờ tốt / theo ngày, khoảng trống khớp `observations.parquet` + `gaps.csv`; role đọc không DELETE / CREATE / UPDATE được. Tổng 103 test pass. Đã xem trên trình duyệt ở 1440 px và 390 px.
- **Review hoàn thiện** (agent review độc lập, theo `impeccable`): lần 1 "fix" 7 điểm (thang biểu đồ bị gai kéo giãn, cờ "thiếu" chỉ khác "tốt" bằng sắc độ, màu xanh dùng sai chỗ, số cũ dùng gradient, nhãn nhóm kiểu eyebrow, dòng chỉ số trên điện thoại bị chèn, nhãn khoảng trống đè dữ liệu) → sửa; lần 2 phát hiện tràn ngang trên điện thoại → sửa; lần 3 **ship**. Hệ thiết kế ghi trong `aquatwin-prototype/DESIGN.md` + `.impeccable/design.json`.
- **Grafana** (`dashboard/`, mục 10.1 dưới) giữ lại nhưng không phát triển tiếp; container **đã dừng** (14/11, theo yêu cầu người dùng), volume còn giữ.
- **Chưa làm:** nhật ký cảnh báo thật (§9), nhóm predicted (§11), tự cập nhật khi có nạp liên tục, đăng nhập / vai trò (hiện chỉ localhost).

### 10.1. Grafana (đã làm 14/11, batch – không phát triển tiếp từ khi có giao diện web riêng)

- **Yêu cầu theo sơ đồ:** hiển thị **trạng thái + cờ chất lượng**, **lịch sử, khoảng trống**, **nhật ký cảnh báo**; lấy dữ liệu từ twin. Công nghệ gợi ý: Grafana (`de-xuat-digital-shadow-wqi.md`).
- **Hạ tầng:** `aquatwin-prototype/dashboard/docker-compose.yml`, image `grafana/grafana:13.2.6` + plugin `yesoreyeram-infinity-datasource` 4.1.4 (Grafana Labs, ghim phiên bản, cài lúc khởi động), chỉ mở `127.0.0.1:3000`, tắt gửi thống kê / kiểm tra cập nhật / tự cập nhật plugin, tắt đăng ký và truy cập ẩn danh. Project Docker `aquatwin-dashboard`, volume `aquatwin_grafana_data`. Grafana nối vào mạng Docker của `timescale/` (host `timescaledb`) và `ditto/` (host `nginx`). Mật khẩu admin và mật khẩu role đọc sinh ngẫu nhiên trong `dashboard/.env` (không commit).
- **Nguồn dữ liệu (chỉ đọc):**
  - twin Ditto qua Infinity (HTTP GET, basic auth từ biến môi trường) → trạng thái hiện tại – đúng sơ đồ "lấy dữ liệu từ twin";
  - kho TimescaleDB qua role `aquatwin_grafana` (chỉ `SELECT` trên schema `aquatwin`, `default_transaction_read_only = on`; đã thử DELETE / CREATE TABLE → bị từ chối) → lịch sử và chất lượng dữ liệu (twin không giữ lịch sử – §1.2 mục 4).
- **Cấu hình:** `config/dashboard.yaml` (`dashboard-1.0`): datasource, múi giờ hiển thị (`Etc/GMT-7`, khớp giả định GMT+7 của `ts` – vẫn unconfirmed), khoảng thời gian mặc định 16 ngày, nhãn cờ và chỉ số, nội dung panel nhật ký cảnh báo. **Không chứa ngưỡng**: khoảng trống lấy `source.yaml` (gap_factor × nhịp = 1.800 s), dữ liệu cũ lấy `twin.yaml` (`stale_after_s` = 1.800 s), giá trị cờ `qc.yaml`, đơn vị `parameters.yaml`, schema `tsdb.yaml`. Code: `src/aquatwin/dashboard.py`; chạy `run_dashboard.py` sinh `dashboard/provisioning/` + `dashboard/dashboards/aquatwin-wqi.json` (không sửa tay) và tạo role chỉ-đọc; `--check` chạy truy vấn mọi panel qua API Grafana.
- **Dashboard "AquaTwin – Chất lượng nước (Observation Twin)"** (biến **Trạm**: `site_id` ↔ `thing_id` lấy từ `twin.yaml`):
  1. *Trạng thái hiện tại – twin*: bảng **observed** (giá trị, đơn vị + trạng thái đơn vị, cờ QC tô màu, thời điểm, lỗi thiết bị, giá trị tốt gần nhất, phiên bản QC, khoá gốc, file nguồn); bảng **estimated** riêng (giá trị, cờ, phạm vi hợp lệ mô hình, độ bất định + trạng thái, hiệu chuẩn đầu vào, transform) – R2.1, R2.4; bảng `health` (stale lúc chiếu); thuộc tính Thing (giá trị null hiện "(chưa biết)"); **tuổi dữ liệu theo đồng hồ thật** (now − bản ghi mới nhất trong kho, đỏ khi > `stale_after_s`) – bù cho `stale` của twin chỉ tính lúc chiếu.
  2. *Lịch sử theo chỉ số – kho*: 6 biểu đồ (5 observed + `practical_salinity` ghi rõ estimated), đường = cờ 1, chấm = cờ 2/3/4 theo màu; đường đứt ở khoảng trống > 30 phút; khoảng trống tô vùng bằng annotation. Không vẽ ngưỡng cảnh báo (R8.3) hay ngưỡng ThingsBoard.
  3. *Chất lượng dữ liệu*: số bản ghi / observation / % cờ tốt (87,3%), số khoảng trống (1), bản ghi cách ly (0), bản ghi lỗi thiết bị (3); số observation theo cờ mỗi ngày (ngày theo GMT+7); phân bố cờ theo chỉ số; bài QC gây cờ 3/4/9; bảng khoảng trống (06/11 05:59 → 07:05, 66,1 phút – khớp `gaps.csv`).
  4. *Nhật ký cảnh báo và truy vết*: panel nhật ký cảnh báo ghi rõ **chưa có** (khối §9 chưa làm, prototype không phát cảnh báo – §1.2 mục 5); bảng các lần nạp kho (`ingest_run`: phiên bản, số dòng mới / sửa / giữ nguyên, sha256 nguồn).
- **Kết quả (14/11):** 22 truy vấn (21 panel có truy vấn + 1 annotation) chạy qua API Grafana: **0 lỗi, 0 panel rỗng** (`output/dashboard_check_report.json`); đã xem trên trình duyệt: đủ 4 nhóm panel, cờ tô màu đúng.
- **Kiểm thử** (`tests/test_dashboard.py`, 12 test): bố cục hợp lệ; mỗi chỉ số một biểu đồ, estimated ghi nhãn; đổi ngưỡng / cờ / schema / múi giờ trong config → dashboard đổi theo, múi giờ lạ bị chặn; không có threshold / alert rule; truy vấn chỉ đọc (SQL không có lệnh ghi, HTTP chỉ GET); provisioning không chứa mật khẩu; observed và estimated tách bảng; `-m tsdb` chạy SQL mọi panel trong transaction read-only và so số dòng / số cờ tốt / khoảng trống với `observations.parquet` + `gaps.csv`; `-m grafana` chạy mọi panel qua Grafana thật. Tổng 91 test pass.
- **Chưa làm:** nhật ký cảnh báo thật (chờ khối §9); đường predicted (chờ §11, R6.10); dashboard tự cập nhật khi có nạp liên tục (hiện làm mới 5 phút nhưng dữ liệu chỉ đổi khi chạy lại pipeline + `run_tsdb.py` + `run_twin.py`); tài khoản theo vai trò (hiện chỉ admin cục bộ); Thing site 1 (tạm gác).

### 10.2. Hệ thống đề xuất (phần còn lại)

- Nhật ký cảnh báo lấy từ khối Cảnh báo (cảnh báo chất lượng dữ liệu, mất dữ liệu, ngưỡng tạm chờ trại duyệt) khi khối đó có.
- Thêm nhóm *predicted* (gắn nhãn "chưa kiểm định", luôn kèm mốc giữ giá trị cuối) khi khối Dự báo có (§11).
- Khi mở ra ngoài localhost: tài khoản theo vai trò, đổi tài khoản Ditto mặc định, HTTPS.

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
- [ ] **Sai số (độ chính xác) của đầu đo độ dẫn điện và nhiệt độ**, và độ sâu đặt đầu đo: cần để tính độ bất định của `practical_salinity` (estimated phải kèm độ bất định – Platform Design Bảng 5.6). Khi có, điền vào `derived.practical_salinity.uncertainty.inputs` trong `config/parameters.yaml` kèm nguồn; hiện `uncertainty = null`.
- [x] ~~Độ mặn khoảng 49 là đúng thực tế hay do lỗi đơn vị?~~ **Đã trả lời 13/11 22:31:** khoá `salinity` là độ dẫn điện mS/cm. Độ mặn thực khoảng 27–33 PSU (bình thường). Đã sửa `config/parameters.yaml` và `config/qc.yaml` (obs-1.1, qc-0.2).
- [ ] Cảm biến có tự bù nhiệt cho độ dẫn điện không (giá trị là độ dẫn điện thực tế hay đã quy về 25°C – "specific conductance")? Ảnh hưởng tới công thức quy đổi sang độ mặn. Hiện để `temperature_compensated: unknown` (dùng nhiệt độ đo); nếu là có thì phải dùng t = 25°C.
- [ ] GREEN-X quy đổi độ mặn bằng hệ số tuyến tính ≈ 0,65 × mS/cm, cho kết quả **cao hơn PSS-78 khoảng 8%** ở 28–29°C (50,9 mS/cm: GREEN-X 33,1 ppt, PSS-78 31,1 PSU). Nếu cảm biến đã bù nhiệt về 25°C thì PSS-78 sẽ gần GREEN-X hơn. Cần thống nhất công thức nào là chuẩn cho dashboard và cảnh báo.
- [ ] Độ dẫn điện tụt dưới 40 mS/cm: **8 đợt / 38 lần đo** (30/10, 01/11, 02/11, 03/11, 04/11, 09/11, 10/11, 11/11), thấp nhất 31,5 mS/cm (~17,8 PSU), mỗi đợt 30–90 phút, phần lớn bắt đầu khoảng **10:40–11:35 sáng** (01/11 và 10/11 lúc ~14:20–15:30). Có phải thay nước / bổ sung nước ngọt / vệ sinh định kỳ không? Trại có lịch thao tác không?
- [ ] Ai duyệt ngưỡng QC và ngưỡng cảnh báo (R8.3)
- [ ] pH đứng yên rất lâu (dài nhất 17,4 h ở 8.22, 17 đoạn ≥ 4 h) dù độ phân giải 0.01: đầu đo pH có cập nhật theo bước / bị treo giá trị không? Đồng thời pH tăng dần 7,5 → 8,2 trong 2 tuần: thực tế hay trôi hiệu chuẩn?
- [ ] Turbidity đứng yên ở 5.0 / 4.6 kéo dài tới 17 h (25 đoạn ≥ 4 h): đây có phải giá trị sàn / mặc định của cảm biến không?
- [ ] Sự kiện turbidity 02/11 17:42–18:13 (964 → 208 → 498) và 06/11 16:08 (316): thực tế (khuấy bùn, vệ sinh, thay lưới…) hay nhiễu? Trại có nhật ký thao tác không?
- [ ] Ngày 06/11: mất dữ liệu 66 phút (05:59 → 07:05) rồi 3 lỗi "cannot open serial port" (07:05, 17:41, 17:44). Có ai can thiệp thiết bị / mất điện không?
- [ ] Dashboard (§10): ai sẽ xem (người vận hành trại, nhóm dữ liệu…), cần những vai trò / quyền nào, và có cần mở ra ngoài máy chạy prototype không (hiện chỉ localhost, một tài khoản admin)?
- [ ] Vì sao MinIO không có file WQI mới của NB2 sau 13/11 08:42 (NB1 sau 02/11) trong khi ThingsBoard vẫn nhận? Luồng ghi lên MinIO có bị dừng không, có dự định chạy lại không?
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
- 2026-11-14: Dựng Eclipse Ditto **3.9.8** bằng Docker Compose (`aquatwin-prototype/ditto/`, bộ chính thức sửa tối thiểu: port chỉ localhost, volume MongoDB, bỏ mount trỏ vào repo Ditto). `/health` = UP, 9 container chạy. Tạo Policy + Thing khung `aquatwin:nuoibien-2` bằng `ditto/bootstrap_things.py` (chưa có dữ liệu). Khối Twin chuyển sang 🔨 Đang làm.
- 2026-11-14: Viết projector twin (`src/aquatwin/twin.py`, `run_twin.py`, `config/twin.yaml`, `twin-proj-1.0`): mỗi bản ghi → merge-patch có điều kiện "mới hơn `last_record_ts`". Replay 1.333 bản ghi vào `aquatwin:nuoibien-2`, đối chiếu khớp, chạy lại không đổi. Thêm 13 test (R4.4 trên Ditto giả lập + Ditto thật), tổng 64 test pass. `last_good` = chỉ cờ 1; `estimated` = giá trị dẫn xuất.
- 2026-11-14: Sửa `estimated` theo *Digital Twin Platform Design (EN)* (estimated = suy ra từ số đo + mô hình; Bảng 5.6, 5.21): schema **obs-1.2** thêm `uncertainty`, `uncertainty_status`, `model_validity`, `calibration_provenance` cho giá trị estimated; **params-1.3** thêm `model_validity` (PSS-78: SP 2–42, t −2–35 °C, p 0–10000 dbar) và `uncertainty` (đầu vào `null`, `unconfirmed`); transform `pss78-gsw-1.1`; projector **twin-proj-1.1**. Chạy lại: số observation và cờ không đổi (6.665 đo + 1.330 estimated); 1.330 `in_range`; độ bất định `unavailable` (chưa có sai số cảm biến). Bootstrap lại Thing + replay: khớp. 69 test pass. Bản cũ: `config/history/params-1.2.yaml`.
- 2026-11-14: Sửa định nghĩa `estimated` trong `de-xuat-digital-shadow-wqi.md` (mục quyết định thiết kế + bảng chất lượng dữ liệu) và §7.2 cho khớp *Digital Twin Platform Design*: estimated = suy ra từ số đo + mô hình; lấy mẫu lại 15 phút chỉ là estimated khi có mô hình nội suy có phiên bản + độ bất định.
- 2026-11-14: **qc-0.3-provisional** (người dùng duyệt hạ cờ): estimated ngoài phạm vi hợp lệ của mô hình (`model_validity = out_of_range`) → test `model_validity` = 3, cờ cuối = xấu nhất của cờ kế thừa và test này; giá trị vẫn lưu và chiếu vào twin. Ngưỡng chỉ số đo giữ như qc-0.2 (bản cũ: `config/history/qc-0.2-provisional.yaml`). Dữ liệu hiện tại không có giá trị ngoài phạm vi → cờ không đổi. Bootstrap + replay Ditto: khớp. 70 test pass. Tạm gác: độ bất định, Thing site 1.
- 2026-11-14: Làm khối **kho chuỗi thời gian** bằng TimescaleDB (người dùng chọn sau khi so sánh với InfluxDB): Docker `timescale/timescaledb:2.31.0-pg18` trên localhost; `config/tsdb.yaml` (`tsdb-1.0`), `src/aquatwin/tsdb.py`, `run_tsdb.py`; hypertable `aquatwin.observation` có revision (nạp lại không trùng, nội dung khác → revision mới, bản cũ giữ), `ingest_run`, `quarantine`, view hiện hành, `observation_as_of`, lưới 15 phút. Nạp 7.995 observation, khớp; nạp lại 0 mới. 9 test mới, tổng 79 pass.
- 2026-11-14: Làm khối **Dashboard** bằng Grafana OSS 13.2.6 + plugin Infinity 4.1.4 (Docker, localhost, chỉ đọc): `config/dashboard.yaml` (`dashboard-1.0`), `src/aquatwin/dashboard.py`, `run_dashboard.py` sinh provisioning + dashboard từ config (ngưỡng khoảng trống / dữ liệu cũ / cờ / đơn vị lấy từ source, twin, qc, parameters.yaml); role TimescaleDB `aquatwin_grafana` chỉ SELECT. 4 nhóm panel: trạng thái hiện tại từ twin (observed, estimated tách riêng, health, thuộc tính, tuổi dữ liệu), lịch sử theo cờ + khoảng trống từ kho, chất lượng dữ liệu, nhật ký cảnh báo (ghi rõ chưa có) + các lần nạp. 22 truy vấn qua API: 0 lỗi; 12 test mới, tổng 91 pass.
- 2026-11-14 (tối): Khối **Dashboard chuyển sang giao diện web riêng** theo yêu cầu người dùng: FastAPI chỉ đọc + HTML/CSS/JS thuần (`config/web.yaml` `web-1.0`, `src/aquatwin/webapi.py`, `run_web.py`, `web/static/`), role kho `aquatwin_web` chỉ SELECT, 4 màn (Tổng quan, Chỉ số, Chất lượng dữ liệu, Truy vết & cảnh báo), thế giới hình ảnh "bảng phấn chợ cá" (người dùng chọn), số cũ hiện mờ + dải vàng (người dùng chọn), cờ bằng hình nét + chữ. 12 test mới, tổng 103 pass. Grafana giữ lại, không phát triển tiếp. Thêm `aquatwin-prototype/PRODUCT.md`.
- 2026-11-15: Làm **connector đọc trực tiếp MinIO** (S3 API, key chỉ đọc `aquatwin-connector` do người dùng tạo bằng `mc`): `config/minio.yaml` `connector-1.0`, `src/aquatwin/minio_source.py`, `run_connector.py`; mirror thô `aquatwin-prototype/data/minio/` giữ nguyên key; reader thêm `file_glob` theo nguồn; `source.yaml` → `source-1.1`, nguồn mặc định là mirror. Lần đầu tải 1.368 file (35 file mới ngày 13/11), batch 8.205 observation, kho + twin khớp. Phát hiện MinIO không có dữ liệu mới sau 13/11 08:42. 11 test mới, tổng 113 pass.
- 2026-11-15: Connector **chạy định kỳ**: `run_connector.py --loop` (`schedule` trong `config/minio.yaml`: 900 s, pipeline bật, khoá file), bắt đầu 12:52 trong tab terminal của app. 2 test mới, tổng 115 pass.
- 2026-11-16: Viết lại §4.3 theo trạng thái thật (trước đó còn ghi "để sau" dù đã có polling 15 phút): bảng đã làm / chưa làm cho nạp liên tục.


## B? sung 17/11/2026 ? b? m? c?c b? v? ?nh x? ti?u chu?n

?? s?a tr?c ti?p `aquatwin-app`/`aquatwin-backend`: profile tr?m c? phi?n b?n, h?p ??ng observation/provenance, API freshness, guard m? h?nh nghi?n c?u v? m?n Architecture & evidence. Xem `cap_nhat_trien_khai_tieu_chuan_1711.md`. ??y l? b? prototype hi?n c? trong workspace Windows, kh?c b? `aquatwin-prototype` ???c m? t? ? c?c m?c tr??c; kh?ng x?c nh?n thay ??i FastAPI/TimescaleDB/connector ? m?i tr??ng kh?c. Ch?a tuy?n b? tu?n th? ISO ??y ?? ho?c ??t P1.
