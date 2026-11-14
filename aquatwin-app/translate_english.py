"""One-time English UI migration; preserve identifiers and raw measurements."""
from pathlib import Path
import re,json,unicodedata
ROOT=Path(__file__).resolve().parent
PAIRS='''
Chọn chỉ số	Select parameter
Diễn biến mô phỏng 	Simulation trajectory 
Diễn biến 	Trends: 
Time phát lại	Replay time
Hợp đồng sẵn sàng	Contract available
QC tạm thời	Provisional QC
01 / CHẤT LƯỢNG NƯỚC	01 / WATER QUALITY
Oxy & biến động môi trường	Oxygen & environmental changes
Theo dõi DO, nhiệt độ, pH và độ dẫn điện. Chưa đặt ngưỡng an toàn theo loài.	Track DO, temperature, pH and conductivity. Species-specific safety thresholds are not configured.
Xem dữ liệu	View data
02 / CHẤT THẢI	02 / WASTE
Turbidity & sự kiện needs review	Turbidity & events to review
Spike không chứng minh thức ăn dư. Cần lấy mẫu, nhật ký cho ăn và bối cảnh.	A spike does not establish uneaten feed. Sampling, feeding logs and context are required.
Xem sự kiện	View events
03 / SỨC KHỎE	03 / HEALTH
Observed cá & phản ứng ăn	Fish observations & feeding response
Record an inspection sức khỏe. Chưa chẩn đoán bệnh từ 5 thông số nước.	Record a health inspection. Five water parameters do not provide a disease diagnosis.
Ghi nhận	Record
04 / MÔI TRƯỜNG NGOÀI	04 / EXTERNAL CONDITIONS
Weather & trao đổi nước	Weather & water exchange
Chưa có mưa, gió, dòng chảy. Không gán nguyên nhân cho biến động nước.	Rain, wind and current data are unavailable. Causes of water changes are not inferred.
Bổ sung nhật ký	Add a log entry
05 / HIỆU QUẢ	05 / EFFICIENCY
Feeding & thiết bị	Feeding & equipment
Chưa có lượng ăn, sinh khối và điện. Khởi tạo nhật ký để xây mô hình tiếp theo.	Feed quantities, biomass and power data are unavailable. Start a logbook to support future models.
Ghi vận hành	Record operations
06 / ĐỘ TIN CẬY	06 / RELIABILITY
Mất dữ liệu & đầu đo	Missing data & probes
Tách sự cố đo khỏi điều kiện môi trường. Xác minh các điểm nghi vấn.	Separate measurement faults from environmental conditions. Review suspect points.
Kiểm tra QC	Review QC
Quan trắc & replay	Observations & replay
QC & sự kiện	QC & events
Lọc days	Filter dates
Policy và Thing	Policy and Thing
Kết nối Ditto	Ditto connection
Sự kiện	Events
AquaTwin — Operations workspace trại nuôi	AquaTwin — Farm operations workspace
Con trỏ dữ liệu không hợp lệ.	Invalid data cursor.
Cần DITTO_SUBJECT theo tài khoản đã xác thực của Ditto.	Set DITTO_SUBJECT to the authenticated Ditto account subject.
Gateway chỉ kết nối Ditto loopback; không gửi dữ liệu trại ra máy chủ bên ngoài.	The gateway connects to loopback Ditto only; farm data is not sent to external servers.
Not configured DITTO_TOKEN hoặc DITTO_USER / DITTO_PASSWORD.	Set DITTO_TOKEN or DITTO_USER / DITTO_PASSWORD.
Ditto từ chối quyền; kiểm tra tài khoản và Policy.	Ditto denied access; check credentials and Policy.
Trạng thái Ditto đã đổi; đọc lại trước khi đồng bộ.	The Ditto state has changed; read it again before synchronizing.
Ditto trả lỗi HTTP 	Ditto returned HTTP error 
Không kết nối được Ditto tại loopback; kiểm tra máy chủ và cổng.	Cannot connect to loopback Ditto; check the server and port.
Phản hồi Ditto không phải JSON hợp lệ.	Ditto returned invalid JSON.
Not configured tài khoản Ditto trong môi trường gateway.	Ditto credentials are not configured in the gateway environment.
Authenticated và đọc Thing.	Authenticated and read the Thing successfully.
Ditto truy cập được; Thing chưa tồn tại.	Ditto is reachable; the Thing does not exist yet.
Đã tạo phần chưa có; không ghi đè Policy hoặc Thing hiện hữu.	Created missing resources; existing Policies and Things were preserved.
Thing chưa tồn tại. Khởi tạo trước.	The Thing does not exist. Provision it first.
Thing dùng Policy khác; cần quản trị xác minh.	The Thing uses a different Policy; administrator review is required.
Snapshot cũ hơn trạng thái Ditto; không kéo trạng thái lùi lại.	The snapshot is older than the Ditto state; state rollback is blocked.
Timestamp trên Ditto không hợp lệ; cần kiểm tra.	The Ditto timestamp is invalid; review it before proceeding.
Snapshot đã có; bỏ qua cập nhật trùng.	The snapshot already exists; duplicate update skipped.
Ditto chưa trả ETag; chưa thể đồng bộ có kiểm soát phiên bản.	Ditto did not return an ETag; version-controlled synchronization is blocked.
Chưa xác minh được trạng thái đọc lại.	Unable to verify the readback state.
Đã đồng bộ và GET xác minh.	Synchronized and verified with GET.
Origin / Host không được phép.	Origin / Host not allowed.
Không có API này.	API endpoint not found.
Yêu cầu JSON.	JSON content is required.
Kích thước yêu cầu không hợp lệ.	Invalid request size.
JSON phải là object.	JSON must be an object.
JSON hoặc tham số không hợp lệ.	Invalid JSON or parameters.
Đạt QC	QC passed
Chưa đánh giá	Not evaluated
Nghi vấn	Suspect
Không đạt	Failed
Thiếu dữ liệu	Missing data
Tổng quan khu nuôi	Farm overview
Tổng quan	Overview
Chất lượng dữ liệu	Data quality
Sự kiện cần xác minh	Events to review
Phân tích môi trường	Environmental insights
Phòng thử nghiệm	Research lab
Nhật ký vận hành	Operations log
Dữ liệu & cấu hình	Data & settings
Kết nối Eclipse Ditto	Eclipse Ditto connection
Trạm Nuôi Biển 2	Marine Farm 2 station
Nuôi Biển 2	Marine Farm 2
Quan trắc môi trường	Environmental monitoring
Không gian điều hành	Operations workspace
KHÔNG GIAN VẬN HÀNH	OPERATIONS WORKSPACE
PHÁT LẠI LỊCH SỬ	HISTORICAL REPLAY
Xuất dữ liệu chuẩn hóa	Export normalized data
Xuất dữ liệu	Export data
Mở menu	Open navigation
Phạm vi & nguồn dữ liệu	Scope & data sources
Dữ liệu nguồn được giữ nguyên · Không kết nối điều khiển thiết bị	Source data is preserved · No device actuation connected
Dữ liệu thật. Quyết định có kiểm chứng.	Real observations. Evidence-based review.
Đóng	Close
Nhiệt độ	Temperature
Oxy hòa tan	Dissolved oxygen
Độ dẫn điện	Conductivity
Độ đục	Turbidity
Biến động nhiệt	Temperature changes
Nguy cơ thiếu oxy	Low-oxygen risk
Biến động axit–kiềm	Acid–base changes
Biến động tính chất nước	Water-property changes
Giảm độ trong của nước	Reduced water clarity
Nước có đang thay đổi nhiệt độ?	Is the water temperature changing?
Oxy có đang giảm?	Is dissolved oxygen decreasing?
pH có thay đổi khác thường?	Is pH changing unexpectedly?
Tính chất nước có đang thay đổi?	Are water properties changing?
Nước có xuất hiện biến động độ đục?	Is turbidity changing unexpectedly?
Theo dõi biến động nhiệt để kiểm tra điều kiện nuôi. Chưa kết luận cá bị sốc nhiệt chỉ từ số đo.	Track thermal changes and inspect rearing conditions. A reading alone does not establish thermal shock in fish.
Đo đối chiếu nhiệt độ tại trạm và kiểm tra vị trí đầu đo.	Cross-check temperature at the station and inspect probe placement.
Ghi nhận nắng, mưa, thời điểm thay nước hoặc thay đổi tuần hoàn.	Record sunlight, rain, water exchanges and circulation changes.
Quan sát hành vi cá; thực hiện quy trình điều chỉnh đã được trại duyệt nếu cần.	Observe fish behavior; follow farm-approved adjustment procedures where needed.
Nhiệt độ là tín hiệu theo dõi biến động nhiệt; mức phù hợp phụ thuộc loài và giai đoạn nuôi.	Temperature tracks thermal changes; suitable conditions depend on species and life stage.
Theo dõi DO và mức thay đổi. Chưa xác lập ngưỡng thiếu oxy cho loài cá tại trại.	Track DO and its rate of change. No species-specific low-oxygen threshold has been approved for this farm.
Kiểm tra lại phép đo DO và tình trạng đầu đo.	Verify the DO reading and inspect the probe.
Quan sát cá, kiểm tra thiết bị oxy/tuần hoàn nếu đơn vị nuôi có trang bị.	Observe fish and inspect oxygenation or circulation equipment, if installed.
Báo người phụ trách khi số đo đối chiếu vượt giới hạn đã duyệt; không chờ dự báo thử nghiệm.	Notify the responsible operator if verified readings exceed approved limits; do not wait for an experimental forecast.
DO là nồng độ oxy hòa tan, không phải % bão hòa. App không dùng các phép tính oxy cũ từ conductivity.	DO is dissolved-oxygen concentration, not percent saturation. Legacy oxygen calculations based on conductivity are excluded.
Theo dõi tính axit–kiềm của nước. Chưa xác định nguyên nhân hoặc đưa liều xử lý hóa chất.	Track water acid–base conditions. The app does not determine causes or prescribe chemical dosing.
Đo pH đối chiếu và kiểm tra hiệu chuẩn, vệ sinh đầu đo.	Cross-check pH and inspect probe calibration and cleanliness.
Ghi thời điểm thay nước, mưa và các thao tác xử lý nước.	Record water exchanges, rainfall and water-treatment activities.
Chuyển người có chuyên môn xem xét trước mọi điều chỉnh hóa học.	Request specialist review before any chemical adjustment.
Một số đo pH không đủ xác định độc tính ammonia hay CO₂; cần thông số bổ sung.	A pH reading alone cannot establish ammonia toxicity or CO2 concentration; additional measurements are required.
Theo dõi độ dẫn điện để nhận diện thay đổi cần kiểm tra; không coi đây là số đo độ mặn PSU.	Track conductivity changes that warrant inspection; this is not a salinity measurement in PSU.
Kiểm tra đơn vị mS/cm, đo đối chiếu và xác nhận trạng thái bù nhiệt.	Verify mS/cm units, cross-check the reading and confirm temperature compensation.
Đối chiếu thay nước, mưa và dòng chảy cùng thời điểm.	Compare concurrent water exchanges, rainfall and currents.
Nếu cần đánh giá độ mặn, dùng phép đo hoặc quy đổi PSS-78 có giả định được xác nhận.	For salinity assessment, use a direct measurement or PSS-78 conversion with confirmed assumptions.
Khóa salinity trong nguồn là conductivity mS/cm. Không kết luận sốc mặn hoặc ô nhiễm chỉ từ giá trị này.	The source salinity key represents conductivity in mS/cm. This value alone does not establish salinity shock or pollution.
Theo dõi độ trong và các điểm tăng đột ngột. Không tự quy kết thức ăn dư, chất thải hoặc bệnh.	Track water clarity and sudden spikes. Do not automatically attribute them to uneaten feed, waste or disease.
Kiểm tra ảnh/quan sát thực địa và đo độ đục đối chiếu.	Review images or field observations and cross-check turbidity.
Kiểm tra bám bẩn đầu đo, bọt khí, thao tác cho ăn hoặc xáo trộn nước.	Check probe fouling, bubbles, feeding activities and water disturbance.
Ghi nhận lấy mẫu và chuyển người phụ trách đánh giá trước khi chọn biện pháp xử lý.	Record sampling evidence and request operator review before selecting a response.
Độ đục NTU không tự quy đổi thành lượng chất thải hoặc TSS khi chưa hiệu chuẩn tại trại.	Turbidity in NTU cannot be converted to waste load or TSS without site-specific calibration.
Thiếu số đo	No measurement
Cần kiểm tra luồng đo; không suy ra tình trạng an toàn.	Inspect the measurement stream; missing data does not establish safety.
Chưa đặt khoảng tham chiếu	No reference range set
Chưa có giới hạn theo loài/giai đoạn được xác nhận.	No confirmed species- and life-stage-specific limits are available.
Dưới khoảng thử nghiệm	Below trial range
Trên khoảng thử nghiệm	Above trial range
Trong khoảng thử nghiệm	Within trial range
Cần xác minh với giới hạn trại đã duyệt trước khi quyết định.	Verify against farm-approved limits before making a decision.
Không đồng nghĩa cá an toàn hoặc môi trường đã đạt mọi yêu cầu.	This does not establish fish safety or compliance with all environmental requirements.
5 VẤN ĐỀ CẦN THEO DÕI	5 MONITORING AREAS
Khu nuôi · 5 nhóm theo dõi	Farm · 5 monitoring areas
Trợ lý theo dõi khu nuôi	Farm monitoring assistant
Quan sát → giả lập → xem xét quyết định.	Observe → simulate → review decisions.
Công cụ & kết nối	Tools & connections
Công cụ hỗ trợ	Supporting tools
Các công cụ kỹ thuật vẫn được giữ, tách khỏi không gian theo dõi 5 vấn đề.	Technical tools remain available separately from the five monitoring areas.
QC dữ liệu	Data QC
Kiểm thử	Testing
Nhật ký	Logbook
Nguồn & cấu hình	Sources & settings
Cần xác minh dữ liệu	Data needs review
Đã có số đo để theo dõi	Measurements available for monitoring
KHU NUÔI / NUÔI BIỂN 2	FARM / MARINE FARM 2
Một khu nuôi. Năm vấn đề cần theo dõi.	One farm. Five monitoring areas.
Xem trạng thái chung, chọn một vấn đề và thử kịch bản trước khi cân nhắc hành động.	Review the farm, explore a monitoring area and test a scenario before considering action.
Ghi nhận tại trại	Record a field observation
TRẠNG THÁI TỔNG QUAN KHU NUÔI	FARM OVERVIEW STATUS
/5 luồng đo có cờ QC cần kiểm tra.	/5 measurement streams have QC flags requiring review.
5 luồng đo hiện không có cờ QC suspect/fail/missing.	No measurement streams currently have suspect, fail or missing QC flags.
Chưa đánh giá sức khỏe đàn cá.	Fish-stock health has not been assessed.
Phát lại lịch sử · UTC+7	Historical replay · UTC+7
Vị trí lồng, độ sâu, đàn cá: chưa xác nhận	Cage location, depth and fish stock: unconfirmed
VẤN ĐỀ 0	AREA 0
Theo dõi · giả lập · quyết định	Monitor · simulate · review
Diễn biến chung và thời điểm theo dõi	Water trends and monitoring time
Chọn thời điểm: cả 5 mục cập nhật theo cùng một snapshot.	Choose a time: all five areas use the same snapshot.
Mỗi chỉ số đại diện cho một nhóm theo dõi, không xác định một nguyên nhân duy nhất. Cờ QC đánh giá dữ liệu; khoảng tham chiếu thử nghiệm và gợi ý không thay thế quy trình trại.	Each indicator represents a monitoring area, not a unique cause. QC flags assess data; trial ranges and guidance do not replace farm procedures.
Hiện đang xem	Currently viewing
dữ liệu lịch sử UTC+7.	historical data in UTC+7.
SỐ ĐO QUAN SÁT	OBSERVED MEASUREMENT
ĐÁNH GIÁ THEO KHOẢNG THỬ	TRIAL-RANGE ASSESSMENT
THAY ĐỔI GIỮA HAI MẪU	CHANGE BETWEEN TWO SAMPLES
Hiệu sai phân, không phải nguyên nhân hoặc dự báo.	Finite difference, not a cause or forecast.
Giữ số đo gốc và khoảng mất dữ liệu; điểm QC nghi vấn được đánh dấu.	Original readings and gaps are preserved; suspect QC points are marked.
1. Đánh giá giả lập	1. Scenario assessment
Tự đặt giá trị giả định để xem cách đánh giá thay đổi. Đây không phải mô hình tác động của sục khí, hóa chất hay thay nước.	Enter a hypothetical value to explore the assessment. This does not model the effects of aeration, chemicals or water exchange.
Thời điểm kịch bản	Scenario time
Sau 15 phút (giả định)	After 15 minutes (assumed)
Sau 30 phút (giả định)	After 30 minutes (assumed)
Sau 60 phút (giả định)	After 60 minutes (assumed)
Đánh giá kịch bản	Evaluate scenario
2. Dự đoán tham khảo	2. Reference forecast
ĐỐI CHỨNG: GIỮ NGUYÊN GIÁ TRỊ CUỐI	BENCHMARK: PERSISTENCE
Dự báo thử cho mẫu kế tiếp (~15 phút theo lịch nguồn). Giá trị bằng số đo hiện tại; không phải mô hình học được đáp ứng sinh học.	Experimental next-sample forecast (~15 minutes at the source cadence). It equals the current reading and does not model biological responses.
Chưa kiểm định độc lập, chưa có khoảng bất định được xác nhận. Không dùng dự báo này để kích hoạt cảnh báo hoặc quyết định vận hành.	Not independently validated; no verified uncertainty interval. Do not use this forecast to trigger alerts or operational decisions.
Chưa tạo dự đoán	Forecast not generated
Số đo hiện tại thiếu hoặc QC chưa đạt. Cần xác minh dữ liệu trước; không thay số đo bằng last_good rồi gọi là dự báo.	The current measurement is missing or has not passed QC. Verify it first; last_good is not substituted and called a forecast.
3. Gợi ý quyết định cho người nuôi	3. Operator decision guidance
Hỗ trợ kiểm tra	Inspection guidance
Ưu tiên xác minh phép đo	Verify the measurement first
Chưa gửi lệnh cho thiết bị. Người phụ trách xác nhận trước khi áp dụng quy trình điều chỉnh tại trại.	No commands are sent to equipment. The responsible operator must approve any farm adjustment procedure.
Ghi nhận quyết định / kiểm tra	Record a decision / inspection
Khoảng tham chiếu cho thử nghiệm	Trial reference range
Để trống nếu chưa có thông tin. Nhập khoảng chỉ phục vụ giả lập trên trình duyệt này; không tự trở thành ngưỡng sinh học đã được trại duyệt.	Leave blank if unknown. This range is for browser-local scenarios only; it does not become a farm-approved biological threshold.
Giới hạn dưới	Lower limit
Giới hạn trên	Upper limit
Lưu khoảng thử	Save trial range
Xóa khoảng thử	Clear trial range
GIẢ LẬP	SIMULATED
Giá trị giả định:	Hypothetical value:
phút theo kịch bản.	minutes in this scenario.
Chênh với số đo hiện tại:	Difference from the current reading:
không tính được	unavailable
Đây là đầu vào người dùng đặt, không phải dự báo. Trạng thái observed và snapshot Ditto không bị thay đổi.	This is a user-defined input, not a forecast. Observed states and the Ditto snapshot remain unchanged.
Giá trị giả định không hợp lệ.	Invalid hypothetical value.
Giới hạn dưới phải nhỏ hơn giới hạn trên.	The lower limit must be smaller than the upper limit.
Đã lưu khoảng thử, chưa phải ngưỡng trại duyệt.	Trial range saved; it is not a farm-approved threshold.
Không lưu được cấu hình.	Unable to save settings.
Ghi nhận kiểm tra:	Inspection record:
Người phụ trách	Responsible operator
Quan sát và quyết định thực tế	Actual observations and decisions
Ghi nhận thực tế, tách khỏi đánh giá giả lập. Chỉ lưu trên trình duyệt này.	Record actual observations separately from scenarios. Saved only in this browser.
Lưu vào nhật ký	Save to logbook
Người vận hành ghi nhận	Recorded by operator
Đã lưu ghi nhận.	Record saved.
Quan trắc lịch sử	Historical observations
Cờ QC tạm thời đánh giá dữ liệu, không phải cảnh báo sức khỏe cá. Độ sâu, vị trí lồng và hiệu chuẩn chưa được xác nhận.	Provisional QC flags assess data, not fish health. Depth, cage location and calibration are unconfirmed.
Chọn thêm bản ghi trên thanh phát lại để xem biểu đồ.	Select more records on the replay timeline to view the chart.
Không có số đo trong khoảng này.	No measurements in this interval.
Cuối tập	Latest record
Quan sát	Observed
Xem & xác minh	View & review
Chưa có sự kiện trong phạm vi này.	No events in this interval.
QUAN SÁT ĐẠT QC	QC-PASSED OBSERVATIONS
BẢN GHI ĐÃ PHÁT	REPLAYED RECORDS
5 phép đo / bản ghi. Spike ở thời điểm đang phát chờ mẫu tiếp theo.	5 measurements per record. Spike QC at the replay cursor awaits the next sample.
phép đo	measurements
AQUATWIN / TRẠM QUAN TRẮC	AQUATWIN / MONITORING STATION
Hiểu trạng thái nước. Chủ động kiểm tra.	Understand the water. Inspect proactively.
Theo dõi môi trường, xác minh dữ liệu và ghi nhận hành động tại trạm Nuôi Biển 2.	Monitor water conditions, review data and record actions at Marine Farm 2.
Nguồn dữ liệu	Data sources
Ghi nhận kiểm tra	Record an inspection
Diễn biến chất lượng nước	Water-quality trends
Số đo gốc	Original readings
Điểm cần xác minh QC	QC points to review
Khoảng trống không được nội suy	Gaps are not interpolated
Theo dõi chuỗi đo tại đúng thời điểm phát lại	Measurements at the selected replay time
Trạm quan trắc số	Digital monitoring station
SƠ ĐỒ ĐẠI DIỆN · KHÔNG PHẢI VỊ TRÍ THỰC	ILLUSTRATIVE DIAGRAM · NOT THE ACTUAL LOCATION
Có dữ liệu lịch sử	Historical data available
Định danh Twin	Twin identifier
Nguồn thiết bị	Source device
Độ sâu / hiệu chuẩn	Depth / calibration
Chưa xác nhận	Unconfirmed
Tích hợp Ditto	Ditto integration
Gateway sẵn sàng	Gateway available
Khám phá mô hình twin	Explore the twin model
Dựa trên chất lượng dữ liệu; chưa kết luận nguyên nhân	Data-quality signals; causes are not established
Xem tất cả	View all
Sức khỏe dữ liệu	Data health
MÔ HÌNH ĐỐI TƯỢNG	ENTITY MODEL
Một nguồn thực. Trạng thái có nguồn gốc.	One real source. Traceable states.
Quan sát, quan hệ và last_good được quản lý riêng cho từng thông số.	Observations, relationships and last_good are managed per parameter.
Xuất Thing JSON	Export Thing JSON
Quan hệ đối tượng	Entity relationships
Trạm đo WQI	WQI monitoring station
luồng đo	measurement streams
Lồng/ao, đàn cá, vị trí đầu đo và độ sâu chưa xác nhận. Prototype không tự tạo quan hệ với đàn cá hoặc thiết bị vận hành.	Cage/pond, fish stock, probe position and depth are unconfirmed. The prototype does not invent stock or equipment relationships.
Trạng thái feature	Feature states
Quan sát tại con trỏ	Observation at cursor
QC tổng hợp	Aggregate QC
Thời điểm last good	Last-good time
Giá trị observed luôn giữ nguyên dù QC không đạt. last_good không thay thế số đo hiện tại. Điểm cuối chờ spike; lịch sử được hoàn tất khi phát tới mẫu kế tiếp.	Observed values remain unchanged even when QC fails. last_good does not replace the current reading. Spike QC is finalized when the next sample is available.
Hợp đồng tương thích Eclipse Ditto	Eclipse Ditto-compatible contract
Đây là projection trong trình duyệt, chưa kết nối máy chủ Ditto. Có script gửi snapshot vào Ditto khi nhóm triển khai cấu hình endpoint và quyền truy cập.	This browser projection is not connected to a Ditto server. A snapshot adapter is available once an endpoint and permissions are configured.
Kiểm tra dữ liệu trước khi ra quyết định.	Check data before making decisions.
6 bài kiểm tra theo cấu hình prototype.md. Ngưỡng provisional, không phải giới hạn sinh học.	Six checks from prototype.md. Provisional QC thresholds are not biological limits.
Phân bố cờ chất lượng	Quality-flag distribution
Kiểm tra tại thời điểm phát lại	Checks at replay time
Chỉ số	Parameter
Dải đo	Gross range
Khoảng trại	Site range
Đứng yên	Flat line
Spike dùng mẫu kế tiếp; ở con trỏ luôn chưa đánh giá.	Spike QC requires the next sample and remains pending at the cursor.
Các khoảng gián đoạn	Data interruptions
Không lấy dữ liệu thiếu làm bằng chứng an toàn	Missing data is not evidence of safety
Đơn vị đã được làm rõ	Units clarified
Khóa gốc là độ dẫn điện, đơn vị mS/cm, không phải độ mặn PSU. Theo prototype.md, người dùng đã xác nhận.	The source key represents conductivity in mS/cm, not salinity in PSU, as confirmed in prototype.md.
%DO, DO bão hòa và thiếu hụt oxy cũ bị loại khỏi app vì tính từ giả định độ mặn sai. Không sử dụng chúng để cảnh báo hoặc dự báo.	Legacy percent saturation, oxygen solubility and oxygen deficit were excluded because they used an incorrect salinity assumption. They are not used in alerts or forecasts.
PSS-78: chưa tính trong bản app này; chưa có thư viện và cần xác nhận bù nhiệt thiết bị trước khi sử dụng vận hành.	PSS-78 is not computed in this version; a suitable library and confirmed device temperature compensation are required before operational use.
SỰ KIỆN / XÁC MINH	EVENTS / REVIEW
Từ dấu hiệu dữ liệu đến kiểm tra thực tế.	From data signals to field inspections.
Mỗi sự kiện có bằng chứng; kết luận do người phụ trách ghi nhận.	Each event includes evidence; conclusions are recorded by the responsible operator.
Xuất sự kiện	Export events
Biến động chỉ số	Parameter changes
Thiết bị & gián đoạn	Devices & interruptions
dấu hiệu QC trong phạm vi đã phát	QC signals in the replayed interval
Hiển thị tối đa 70 dấu hiệu mới nhất. Chưa gộp thành sự cố sinh học.	Showing up to 70 recent signals. They are not grouped into biological incidents.
MÔI TRƯỜNG / BÀI TOÁN NUÔI	ENVIRONMENT / FARM CHALLENGES
Biến dữ liệu thành câu hỏi cần kiểm tra.	Turn data into questions worth checking.
Phân tích nước hiện có; các tác nhân, sức khỏe và chất thải cần thêm bằng chứng.	Analyze available water data; drivers, health and waste require additional evidence.
Diễn biến và thống kê theo ngày	Daily trends and statistics
Số đo đạt QC	QC-passed readings
Trung bình	Mean
Thấp nhất	Minimum
Cao nhất	Maximum
Chỉ tổng hợp mẫu đạt QC; không gọi trung bình các mẫu là trung bình toàn bộ thể tích nước.	Only QC-passed samples are summarized; their mean is not a whole-water-volume average.
Thử nghiệm trước. Kiểm chứng trước.	Experiment first. Verify first.
Không phát hành dự báo vận hành hoặc điều khiển từ kết quả thử nghiệm.	Experimental results do not authorize operational forecasts or equipment control.
Phòng thử nghiệm tách biệt.	Isolated research sandbox.
Backtest dùng toàn bộ snapshot lịch sử; không phải dữ liệu live hay dự báo được kiểm định độc lập.	Backtesting uses the full historical snapshot, not live data or an independently validated forecast.
Đối chứng dự báo: giữ giá trị cuối	Forecast benchmark: persistence
Chỉ số thử nghiệm	Test parameter
Thiết kế	Design
Đánh giá 30% cuối · dự báo mẫu kế tiếp	Last 30% evaluation · next-sample forecast
CẶP HỢP LỆ	VALID PAIRS
Đánh giá:	Evaluation:
Dự báo y(t+1) = y(t). Loại cặp lỗi, gián đoạn >30 phút, QC tại thời điểm phát không đạt. Không dùng spike dựa vào tương lai để chọn đầu vào.	Forecast y(t+1) = y(t). Excludes errors, gaps over 30 minutes and failed input QC. Future-dependent spike checks are not used to select inputs.
Đây là baseline mô tả sai số lịch sử, không phải mô hình đã thắng đối chứng. Chân trời là mẫu kế tiếp theo lịch không đều; chưa cung cấp khoảng bất định có kiểm chứng.	This baseline describes historical errors, not an improvement over a benchmark. The horizon is the next irregular sample; no validated uncertainty interval is provided.
Không có đủ cặp hợp lệ.	Not enough valid pairs.
Giả lập sự cố dữ liệu	Data-fault simulation
Tạo sự cố tại thời điểm đang phát để kiểm tra hành vi hệ thống. Snapshot thật không bị sửa.	Inject a fault at replay time to inspect system behavior. The source snapshot is unchanged.
Mất luồng dữ liệu trong 45 phút	Data-stream outage for 45 minutes
Gửi trùng sự kiện hiện tại	Duplicate the current event
Bản ghi cũ đến sau trạng thái hiện tại	Older record arrives after the current state
Chạy kịch bản	Run scenario
Cổng phát hành mô hình	Model-release gates
Quan trắc & QC	Observations & QC
Dữ liệu thật, ngưỡng chất lượng provisional.	Real data; provisional quality thresholds.
Backtest theo thời gian	Time-based backtesting
Baseline có thể tái lập; chưa kiểm định độc lập.	Reproducible baseline; not independently validated.
Đánh giá miền áp dụng	Assess the validity domain
Cần dữ liệu mùa/trại giữ riêng, bất định và review.	Requires held-out seasons/sites, uncertainty assessment and review.
Đưa vào vận hành	Operational release
Chưa mở. Không có dự báo kích hoạt hành động.	Not released. Forecasts do not trigger actions.
Mô phỏng can thiệp vật lý	Physical-intervention simulation
Chờ dữ liệu	Awaiting data
Chưa mô phỏng bật sục khí hay giảm thức ăn. Cần cấu hình ao/lồng, thể tích, sinh khối, dòng chảy, trạng thái thiết bị và dữ liệu can thiệp.	Aeration and feed reductions are not simulated. Pond/cage configuration, volume, biomass, currents, equipment states and intervention data are required.
Không coi biến đổi số giả định là tác động đã được xác nhận trên cá.	A hypothetical numeric change is not a verified effect on fish.
FARMOS / NHẬT KÝ	FARMOS / LOGBOOK
Ghi hành động. Giữ lại bằng chứng.	Record actions. Preserve evidence.
Nhật ký lưu trên trình duyệt này; xuất file để bàn giao. Không tự đồng bộ giữa thiết bị.	Logs are stored in this browser. Export a file to share; devices do not synchronize automatically.
Xuất nhật ký	Export logbook
Ghi nhận tại trại	Field record
Loại ghi nhận	Record type
Kiểm tra môi trường	Environmental inspection
Quan sát sức khỏe cá	Fish-health observation
Cho ăn	Feeding
Thiết bị / bảo trì	Equipment / maintenance
Thời tiết / dòng chảy	Weather / currents
Thời điểm (giờ nguồn UTC+7)	Time (source timezone UTC+7)
Người thực hiện	Operator
Tên người kiểm tra	Inspector name
Đối tượng / vị trí	Target / location
Kết quả xác minh	Review outcome
Chưa xác định nguyên nhân	Cause undetermined
Nghi sự cố thiết bị	Suspected equipment issue
Đã kiểm tra đối chiếu	Cross-check completed
Cần kiểm tra chuyên môn	Specialist review needed
Lượng / đơn vị (nếu có)	Quantity / unit (optional)
Ví dụ: 12 kg thức ăn	Example: 12 kg of feed
Quan sát, hành động và bằng chứng	Observations, actions and evidence
Ghi nhận thực tế; phân biệt điều quan sát với nhận định…	Record facts; distinguish observations from interpretations…
Lưu ghi nhận	Save record
Làm mới	Reset
Từ dữ liệu đến quyết định	From data to decisions
1. Nhận diện sự kiện dữ liệu.	1. Identify a data event.
2. Đo đối chiếu / quan sát tại trại.	2. Cross-check measurements / inspect the farm.
3. Người phụ trách ghi hành động.	3. The responsible operator records actions.
4. Theo dõi kết quả và diễn biến nước.	4. Monitor outcomes and water trends.
Chưa có ngưỡng sinh học được trại phê duyệt, chưa chẩn đoán bệnh, chưa gửi lệnh cho ăn hoặc sục khí.	No farm-approved biological thresholds, disease diagnosis, feeding commands or aeration commands are available.
Dữ liệu nhập mới là quan sát của người dùng, tách biệt CSV gốc. Lưu cục bộ không thay thế hệ thống nhật ký được quản trị.	New entries are user observations, separate from the source CSV. Local storage does not replace a managed logbook system.
Nhật ký đã lưu	Saved records
Thời điểm	Time
Kết quả / nội dung	Outcome / notes
Chưa có nhật ký. Ghi nhận đầu tiên để bắt đầu liên kết hành động với dữ liệu.	No records yet. Add your first observation to connect actions with data.
Kiểm tra nước	Water inspection
Sức khỏe cá	Fish health
Thiết bị	Equipment
Thời tiết	Weather
Xác minh QC	QC review
NGUỒN DỮ LIỆU / CẤU HÌNH	DATA SOURCES / SETTINGS
Dữ liệu rõ nghĩa. Kết quả truy vết được.	Clear data. Traceable results.
1.333 bản ghi · 30/10–12/11/2026 · NuoiBien_2 · CSV không bị sửa.	1,333 records · 30 Oct–12 Nov 2026 · NuoiBien_2 · Source CSV unchanged.
Xuất cấu hình QC	Export QC settings
Xuất CSV chuẩn hóa	Export normalized CSV
Điều chỉnh ý nghĩa dữ liệu:	Data interpretation correction:
khóa nguồn	source key
là độ dẫn điện mS/cm. App loại các chỉ số oxy dẫn xuất cũ. Không coi conductivity là Practical Salinity.	represents conductivity in mS/cm. Legacy derived oxygen indices are excluded. Conductivity is not Practical Salinity.
Hồ sơ nguồn	Source profile
Múi giờ	Timezone
bản ghi /	records /
Độ sâu / lồng / hiệu chuẩn	Depth / cage / calibration
Đơn vị °C, mg/L, NTU: documented theo GREEN-X trong prototype.md. Độ dẫn điện mS/cm: confirmed theo ghi chú dự án. QC tạm thời không dùng làm giới hạn cho cá.	Units °C, mg/L and NTU are documented in GREEN-X via prototype.md. Conductivity mS/cm is confirmed in project notes. Provisional QC limits are not biological limits.
Dải QC tạm thời	Provisional QC ranges
Theo prototype.md: spike dựa hai lân cận, flatline 4h suspect / 12h fail; gap >30 phút ghi sự kiện. Đây là triển khai QC riêng của app, chưa đối chiếu bit-for-bit với pipeline được mô tả trong Downloads.	Per prototype.md: two-neighbor spike check, flatline suspect at 4h / fail at 12h; gaps over 30 minutes generate events. This app implementation has not been verified bit-for-bit against the separate pipeline.
Trạng thái năng lực	Capability status
Đang hoạt động	Available
Lưu trình duyệt	Browser storage
Chưa kết nối	Not connected
Dự báo vận hành	Operational forecasting
Chưa phát hành	Not released
Camera / âm học	Camera / acoustics
Chưa nạp	Not loaded
Điều khiển thiết bị	Device actuation
Chưa triển khai	Not implemented
Bản ghi chuẩn hóa	Normalized records
mẫu trong phạm vi	samples in scope
Thời gian UTC+7	Time UTC+7
Lỗi nguồn	Source error
Lỗi cổng serial	Serial-port error
Hiển thị 100 bản ghi mới nhất của bộ lọc. Xuất CSV để xem toàn bộ dữ liệu.	Showing the 100 latest filtered records. Export the CSV to view all data.
Giữ giá trị gốc; chỉ đổi tên trường conductivity.	Original values are preserved; only the conductivity field name is normalized.
Tất cả ngày	All dates
Không lưu được. Kiểm tra bộ nhớ trình duyệt rồi thử lại.	Unable to save. Check browser storage and try again.
Mã sự kiện:	Event ID:
Đây là dấu hiệu QC, không phải chẩn đoán bệnh hay kết luận ô nhiễm. Xác nhận cần kiểm tra thực tế.	This is a QC signal, not a disease diagnosis or pollution finding. Verification requires a field inspection.
Người xác minh	Reviewer
Nhận xét / bằng chứng	Notes / evidence
Xem tại thời điểm này	View at this time
Đã ghi nhận xem xét	Review recorded
Đã lưu xác minh vào nhật ký cục bộ.	Review saved in the local logbook.
Vui lòng nhập người thực hiện và nội dung.	Enter an operator and notes.
Đã lưu nhật ký trên trình duyệt này.	Log saved in this browser.
Mất dữ liệu 45 phút	45-minute data outage
Dữ liệu quá cũ theo giới hạn thử nghiệm 30 phút; chặn sử dụng như hiện tại. Không suy điều kiện cá từ dữ liệu thiếu.	Data exceeds the 30-minute trial freshness limit and cannot represent the current state. Missing data does not establish fish conditions.
Gửi trùng sự kiện	Duplicate event
Một cập nhật logic, không sinh thêm số đo.	One logical update; no extra measurement is created.
Bản ghi đến muộn	Late-arriving record
Lưu bổ sung lịch sử; không kéo trạng thái hiện tại lùi lại.	Append to history without moving the current state backward.
Đã cập nhật theo thứ tự thời gian.	Updated in event-time order.
Đã chạy trên bản sao	Run completed on a copy
AquaTwin là prototype quan trắc lịch sử từ 1.333 bản ghi WQI. Lõi twin chạy trong trình duyệt; có hợp đồng và adapter cho Eclipse Ditto nhưng chưa kết nối máy chủ.	AquaTwin is a historical-observation prototype with 1,333 WQI records. The browser runs the twin core; Ditto contracts and an adapter are available but no live server is connected.
Đối chiếu prototype.md ngày 14/11/2026: salinity là conductivity mS/cm; giờ nguồn UTC+7; QC provisional không phải ngưỡng sinh học. App không dùng chỉ số oxy dẫn xuất sai giả định trước đó.	Per prototype.md (14 Nov 2026): salinity means conductivity mS/cm; timestamps are UTC+7; provisional QC limits are not biological thresholds. Incorrect legacy oxygen indices are excluded.
Không có telemetry live, chẩn đoán bệnh, dự báo đã kiểm định hoặc điều khiển thiết bị. Nhật ký chỉ lưu trong trình duyệt này.	No live telemetry, disease diagnosis, independently validated operational forecasts or device actuation. Logs remain in this browser.
Nguồn: Digital Twin Platform Design chương 3/5; tài liệu nghiên cứu 2024/2025; prototype.md; CSV địa phương. Không giả tạo thiết bị, đàn cá hay kết quả kinh tế chưa có dữ liệu.	Sources: Digital Twin Platform Design chapters 3/5; 2024/2025 research; prototype.md; local CSV. No equipment, fish stocks or economic outcomes are invented.
Đang nạp dữ liệu quan trắc…	Loading observation data…
Chưa tải được dữ liệu	Unable to load data
Hãy mở ứng dụng qua máy chủ HTTP, không mở index.html trực tiếp.	Open the app through an HTTP server, not index.html directly.
Thử lại	Retry
Gián đoạn luồng quan trắc	Observation-stream interruption
Không có bản ghi trong	No records for
phút. Khoảng này chưa có dữ liệu để kết luận môi trường.	minutes. No environmental conclusion is possible for this gap.
Không đọc được thiết bị	Unable to read device
Cổng serial không khả dụng; thiếu cả 5 thông số.	The serial port is unavailable; all five parameters are missing.
điểm nhảy	spike
tốc độ thay đổi	rate of change
đứng giá trị	flat line
ngoài khoảng QC tạm	outside provisional site range
ngoài dải QC	outside QC range
cần xác minh	needs review
Cờ QC không xác định nguy cơ cho cá.	QC flags do not establish risk to fish.
Đã xác thực	Authenticated
Cần khởi tạo	Setup required
Chưa cấu hình	Not configured
Không khả dụng	Unavailable
Chưa kiểm tra	Not checked
DITTO / TÍCH HỢP LÕI TWIN	DITTO / TWIN-CORE INTEGRATION
Đồng bộ trạng thái với Eclipse Ditto.	Synchronize states with Eclipse Ditto.
Thing, Policy và MQTT theo ditto-examples. Gateway chỉ kết nối máy chủ loopback.	Thing, Policy and MQTT based on ditto-examples. The gateway connects to loopback servers only.
Kiểm tra kết nối	Check connection
Chỉ đồng bộ quan trắc sau QC và last_good. Không có live message hoặc lệnh thiết bị. Snapshot lịch sử không phải telemetry đang đo.	Sync QC-processed observations and last_good only. No live messages or actuator commands. Historical snapshots are not live telemetry.
Trạng thái kết nối thực tế	Actual connection status
Gateway cục bộ	Local gateway
Nhấn kiểm tra để xác nhận gateway và Ditto; chưa kết nối không hiển thị là live.	Check the gateway and Ditto connection. A disconnected state is never shown as live.
Snapshot đang chọn	Selected snapshot
Thời điểm trên Ditto	Ditto source time
Khởi tạo phần chưa có	Create missing resources
Đồng bộ snapshot sau QC	Sync QC-processed snapshot
Đọc Thing	Read Thing
Không ghi đè Policy/Thing khi khởi tạo. Đồng bộ dùng ETag, từ chối snapshot cũ hơn và đọc lại xác minh.	Setup preserves existing Policies/Things. Sync uses ETags, rejects older snapshots and verifies readback.
Cấu hình gateway trên máy	Configure the local gateway
Chạy	Run
hoặc Mo_AquaTwin.cmd. Cấu hình môi trường DITTO_URL (localhost), DITTO_TOKEN hoặc DITTO_USER / DITTO_PASSWORD; DITTO_SUBJECT cho owner.	or Mo_AquaTwin.cmd. Set DITTO_URL (localhost), DITTO_TOKEN or DITTO_USER / DITTO_PASSWORD; DITTO_SUBJECT identifies the owner.
Subject phụ thuộc xác thực, ví dụ nginx:tên_người_dùng. Không đưa mật khẩu vào browser hoặc tệp chia sẻ.	The subject depends on authentication, e.g. nginx:username. Never put passwords in the browser or shared files.
Máy chưa có Docker theo lần kiểm tra. Ditto cần cài riêng; app không giả lập kết nối thành công.	Docker was unavailable at the last environment check. Install Ditto separately; the app does not fake a successful connection.
Snapshot theo hợp đồng Thing	Thing-contract snapshot
Luồng tích hợp	Integration flow
Owner, ingest, observer. Không cấp message permission.	Owner, ingest and observer roles. No message permissions are granted.
Gửi snapshot explicit, GET xác minh. Tài khoản ở máy chủ.	Explicit snapshot submission with GET verification. Credentials stay server-side.
MQTT sau QC	MQTT after QC
Xuất Ditto Protocol và connection mẫu. Chưa có broker.	Export Ditto Protocol and connection templates. No broker is connected.
Thông báo thay đổi	Change notifications
Target MQTT mẫu nhận twin events. SSE chưa kết nối.	Example MQTT target for twin events. SSE is not connected.
Repository tham khảo	Reference repository
Gói cấu hình tích hợp	Integration configuration bundle
Mẫu không chứa mật khẩu. Broker URI và subject cần cấu hình, kiểm thử trong môi trường thật.	Templates contain no passwords. Configure and test the broker URI and subjects in the target environment.
MQTT payload lấy từ snapshot đã QC; lịch sử ở kho riêng. Trước khi publish phải xử lý trùng và bản ghi đến muộn.	MQTT payloads use QC-processed snapshots; history is stored separately. Handle duplicates and late records before publishing.
Đang dùng static server. Khởi động server.py để bật gateway Ditto.	A static server is running. Start server.py to enable the Ditto gateway.
Yêu cầu thất bại.	Request failed.
Đã đọc Thing trực tiếp từ Ditto.	Thing read directly from Ditto.
Bản xem chung không kết nối Ditto trên máy cá nhân. Dùng bản cục bộ để cấu hình gateway; dữ liệu quan trắc và giả lập vẫn xem được.	The shared site cannot connect to Ditto on a personal computer. Use the local app for gateway setup; observations and scenarios remain available here.
Bản xem chung · Nhật ký và khoảng thử chỉ lưu trên trình duyệt của từng người	Shared site · Logs and trial ranges are stored separately in each browser
Thiếu số đo khởi tạo. Chọn mốc có số đo.	The initial measurement is missing. Choose an origin with a reading.
Số đo khởi tạo chưa đạt QC. Chọn mốc đạt QC hoặc chấp nhận nó làm điều kiện giả định.	The initial reading has not passed QC. Choose a QC-passed origin or explicitly accept it as a hypothetical initial condition.
Số đo khởi tạo fail/missing, không dùng làm đầu vào mô phỏng.	Failed or missing initial readings cannot initialize a simulation.
Cần ít nhất 96 mẫu đạt QC trải trên 48 giờ trong 7 ngày quá khứ.	At least 96 QC-passed samples spanning 48 hours within the previous seven days are required.
Chưa đủ dữ liệu để ước lượng chu kỳ ngày.	Insufficient data to estimate the daily cycle.
Cần ít nhất 48 cặp mẫu đủ gần để ước lượng diễn biến.	At least 48 sufficiently close sample pairs are required to estimate dynamics.
Khởi tạo bằng số đo nghi vấn theo chấp nhận giả định của người dùng.	Initialized with a suspect reading explicitly accepted as a user assumption.
Tham số mô phỏng không hợp lệ.	Invalid simulation parameters.
Dải mô phỏng ra ngoài miền QC thử nghiệm; không cắt số để che lỗi.	The simulation band exceeds the trial QC domain; values are not clipped to conceal this.
P10–P90 của các quỹ đạo mô phỏng, chưa được hiệu chuẩn xác suất dự báo.	P10–P90 across simulated trajectories; forecast probabilities have not been calibrated.
Cơ sở theo dữ liệu quá khứ	Historical-data baseline
Kịch bản giả định	Assumed scenario
Dải P10–P90 của quỹ đạo mô phỏng, chưa hiệu chuẩn xác suất	P10–P90 simulation band; not probability-calibrated
Chân trời	Horizon
Mốc kiểm tra	Evaluation origins
MAE mô phỏng	Simulation MAE
MAE giữ giá trị cuối	Persistence MAE
So sánh	Comparison
Chưa đủ dữ liệu	Insufficient data
Sai số thấp hơn trong tập thử	Lower error on this test set
Chưa vượt đối chứng	Does not outperform benchmark
Rolling-origin: fit từ tối đa 7 ngày trước mỗi mốc, không dùng dữ liệu tương lai. Đối chiếu giá trị gần +24/+48h trong 10 phút; chỉ các điểm đích đạt QC. Số mốc ít, có chồng lấn, chưa kiểm định độc lập; không suy ra hiệu quả thực địa.	Rolling-origin: fit only the preceding seven days. Compare QC-passed targets within 10 minutes of +24/+48h. Few, overlapping origins; no independent validation or demonstrated field benefit.
Chọn chỉ số, thời điểm khởi tạo và chạy mô phỏng.	Select a parameter and forecast origin, then run the simulation.
Kết quả nghiên cứu theo giả định.	Research results under assumptions.
Dải quỹ đạo không phải khoảng tin cậy đã được kiểm chứng. Chưa có thời tiết, dòng chảy, sinh khối hoặc tác động thiết bị trong mô hình. 5 chỉ số được mô phỏng riêng, chưa đồng mô phỏng tương tác.	The trajectory band is not a validated prediction interval. Weather, currents, biomass and equipment effects are not modeled. The five parameters are simulated independently, without coupled interactions.
CƠ SỞ SAU	BASELINE AT
Giá trị trung tâm mô hình thống kê	Central statistical-model estimate
KỊCH BẢN SAU	SCENARIO AT
Giả định thay đổi thêm	Assumed additional change
DẢI QUỸ ĐẠO Ở MỐC CUỐI	TRAJECTORY BAND AT THE ENDPOINT
P10–P90, không phải xác suất cá an toàn	P10–P90, not a probability of fish safety
Gợi ý xem xét	Review guidance
Đường kịch bản ra ngoài khoảng thử từ khoảng +	The scenario leaves the trial range at approximately +
giờ. Nên bố trí đo đối chiếu trước mốc giả định này; xác nhận lại với giới hạn trại đã duyệt.	hours. Arrange a cross-check before this hypothetical time and verify against farm-approved limits.
Đường trung tâm chưa ra ngoài khoảng thử trong kịch bản. Điều này không bảo đảm mọi quỹ đạo hoặc điều kiện thực tế nằm trong giới hạn.	The central path stays within the trial range in this scenario. This does not guarantee that every trajectory or real condition remains within limits.
Chưa đặt khoảng tham chiếu: chỉ mô tả diễn biến, chưa phân loại nước đạt/không đạt theo loài.	No reference range is set: results describe trends, not species-specific water suitability.
Nguồn gốc lần chạy	Run provenance
Khởi tạo:	Origin:
Kết thúc:	End:
mẫu đạt QC,	QC-passed samples,
cặp; cửa sổ	pairs; window
quỹ đạo · seed	trajectories · seed
Loại trạng thái: simulated; không ghi đè observed hoặc Thing.	State kind: simulated. Observed states and the Thing are not overwritten.
Xuất lần chạy JSON	Export run JSON
DỰ BÁO MÔ PHỎNG / 24–48 GIỜ	SIMULATION FORECAST / 24–48 HOURS
Nước có thể diễn biến thế nào trong 1–2 ngày?	How might water conditions change over the next 1–2 days?
Khởi tạo từ dữ liệu đang chọn, mô phỏng cơ sở và so với giả định diễn biến bổ sung.	Initialize from the selected snapshot, simulate a baseline and compare an assumed additional trend.
Mốc gốc	Forecast origin
là thời điểm trong dữ liệu lịch sử, không phải số đo live hôm nay. Chân trời 24/48 giờ được tính từ mốc đó. Nếu dữ liệu cũ, không dùng kết quả như dự báo hiện tại.	is a historical observation, not a live reading today. The 24/48-hour horizon starts at that origin. Old inputs must not be presented as a current forecast.
Chọn điều kiện mô phỏng	Choose simulation conditions
24 giờ — 1 ngày	24 hours — 1 day
48 giờ — 2 ngày	48 hours — 2 days
Thay đổi thêm theo kịch bản (	Additional scenario trend (
0 = không bổ sung xu hướng giả định. Đây không phải mức tác động của thiết bị.	0 means no additional assumed trend. This is not an equipment-response estimate.
Khởi tạo và tính nhất quán	Initialization and consistency
Học từ dữ liệu trước mốc, tối đa 7 ngày.	Fit only data before the origin, up to seven days.
Chấp nhận số đo QC nghi vấn làm điều kiện giả định (không áp dụng fail/missing)	Accept a suspect reading as a hypothetical initial condition (not failed/missing readings)
Kiểm tra sai số lịch sử 24/48h	Evaluate historical 24/48h errors
Đổi mốc bằng thanh phát lại. Kết quả cũ sẽ được xóa khi đổi nguồn khởi tạo.	Change the origin with the replay slider. Previous results are cleared when the initial snapshot changes.
Diễn biến tương lai theo kịch bản	Future scenario trajectories
Kiểm tra lịch sử theo đúng chân trời	Horizon-specific historical evaluation
Mô hình và giới hạn	Model and limitations
Mô hình nghiên cứu: chu kỳ sin/cos 24h khớp theo bình phương tối thiểu; phần dư có tính nhớ AR(1). Mỗi 15 phút mô phỏng phần dư mới bằng lấy mẫu lại nhiễu quá khứ, tạo 120 quỹ đạo. Cùng snapshot, seed và giả định cho cùng kết quả. Kịch bản cộng thay đổi giả định theo thời gian, không mô hình hóa nguyên nhân vật lý.	Research model: least-squares 24h sine/cosine cycle with AR(1) residual memory. Historical innovations are resampled every 15 minutes to generate 120 trajectories. The same snapshot, seed and assumptions reproduce the result. Scenario trends are added over time; physical causes are not modeled.
Cần ít nhất 96 mẫu đạt QC trải 48h và 48 cặp đủ gần. Nếu thiếu dữ liệu hoặc khởi tạo không hợp lệ, app không tạo kết quả. Không thay âm thầm số đo nghi vấn bằng last_good; không sử dụng dữ liệu sau con trỏ để fit.	Requires 96 QC-passed samples spanning 48h and 48 sufficiently close pairs. Missing data or invalid origins block simulation. Suspect readings are not silently replaced with last_good; future data is never used for fitting.
Tập nguồn chỉ khoảng 14 ngày; mô phỏng chưa thắng đối chứng ở mọi chỉ số. Không dùng để điều khiển tự động, chẩn đoán bệnh hoặc cam kết nước sẽ đạt chuẩn.	The source spans about 14 days; simulation does not outperform persistence for every parameter. Do not use it for automatic control, disease diagnosis or water-quality guarantees.
Dự báo mô phỏng 1–2 ngày	1–2 day simulation forecast
2. Dự báo 24–48 giờ	2. 24–48 hour forecast
Mô phỏng diễn biến 1–2 ngày từ snapshot và dữ liệu quá khứ; có kịch bản cơ sở, giả định bổ sung và kiểm tra sai số lịch sử.	Simulate 1–2 day trajectories from the snapshot and past data, with a baseline, additional scenario trends and historical error evaluation.
Mở dự báo mô phỏng	Open simulation forecast
Gián đoạn	Interruption
Lịch sử	History
Dữ liệu	Data
Nguồn:	Source:
VẤN ĐỀ	MONITORING AREA
giả định (	hypothetical (
không đơn vị	unitless
/giờ	/hour
/ngày	/day
giờ	hours
GIỜ	HOURS
phút	minutes
ngày	days
Loại	Type
Ngày	Date
đến	to
Tất cả	All
Tạm dừng	Pause
Phát lại	Replay
Mô phỏng	Simulate
chứa	contains
quan sát	observes
'''

def main():
 mapping={}
 for line in PAIRS.strip().splitlines():
  if '\t' in line:
   a,b=line.split('\t',1);mapping[a]=b
 # Replace longest phrases first to preserve natural sentence translations.
 targets=list((ROOT/'dist').glob('*.js'))+[ROOT/'dist/index.html',ROOT/'server.py',ROOT/'prepare_data.py',ROOT/'ditto_adapter.py']
 for path in targets:
  s=path.read_text(encoding='utf-8')
  for a,b in sorted(mapping.items(),key=lambda x:-len(x[0])):s=s.replace(a,b)
  s=s.replace("'vi-VN'","'en-US'").replace('lang="vi"','lang="en"')
  path.write_text(s,encoding='utf-8')
 data_path=ROOT/'dist/data.json';data=json.loads(data_path.read_text(encoding='utf-8'))
 for conf in data['params'].values():
  for a,b in sorted(mapping.items(),key=lambda x:-len(x[0])):conf['label']=conf['label'].replace(a,b)
 data['meta']['timezoneSource']='prototype.md section 12: confirmed against ThingsBoard'
 data['meta']['mapping']='salinity -> conductivity (mS/cm), per prototype.md section 1.2'
 data_path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('English migration applied to UI, model messages, gateway and metadata; raw values preserved.')

if __name__=='__main__':main()
