from pathlib import Path
import csv, statistics
from datetime import datetime
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent
with (ROOT/'Data/aquaculture_indices_clean.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
dates=[datetime.fromisoformat(r['ts']) for r in rows]
out=ROOT/'Bao_cao_DT_Aquaculture/Bao_cao_de_xuat_trien_khai_DT_tu_du_lieu_hien_co.docx'
out.parent.mkdir(exist_ok=True)
d=Document();s=d.sections[0]
s.page_width=Cm(21);s.page_height=Cm(29.7)
s.top_margin=s.bottom_margin=Cm(2);s.left_margin=Cm(2.5);s.right_margin=Cm(2)
for style in d.styles:
    if style.type in (1,2):
        style.font.name='Times New Roman';style.font.size=Pt(13)
        style.font.color.rgb=RGBColor(0,0,0)
d.styles['Normal'].paragraph_format.line_spacing=1.15
d.styles['Normal'].paragraph_format.space_after=Pt(6)

def p(t):d.add_paragraph(t)
def h(t):
    pp=d.add_paragraph();pp.add_run(t).bold=True
    pp.paragraph_format.space_before=Pt(12);pp.paragraph_format.keep_with_next=True
def steps(items):
    for i,t in enumerate(items,1):p(f'Bước {i}. {t}')
def proposal(title,problem,data,method,tools,items,outputs,validation,limits):
    h(title)
    p('Vấn đề cần xử lý: '+problem)
    p('Dữ liệu sử dụng và liên hệ DT: '+data)
    p('Phương pháp đề xuất: '+method)
    p('Công cụ: '+tools)
    steps(items)
    p('Đầu ra: '+outputs)
    p('Kiểm chứng: '+validation)
    p('Điều kiện và giới hạn: '+limits)

h('BÁO CÁO ĐỀ XUẤT TRIỂN KHAI DIGITAL TWIN TỪ DỮ LIỆU TRẠI NUÔI CÁ HIỆN CÓ')
p('Phiên bản 1.0 — 13/11/2026. Định hướng nghiên cứu ứng dụng và thiết kế kỹ thuật.')
p('Bản báo cáo trình bày bằng văn bản, Times New Roman cỡ 13; mục đánh số đơn giản, không sử dụng bảng hoặc hình. Cơ sở: dữ liệu thực tế trong Data, ghi chú dự án, Digital Twin Platform Design chương 2–3–5, hai bài tổng quan 2024/2025 và tài liệu GREEN-X. Các thuật toán dưới đây là đề xuất, chưa được huấn luyện hoặc đánh giá hiệu quả trong báo cáo này.')
h('1. Mục tiêu và phạm vi triển khai')
p('Mục tiêu là xây dựng Water Quality Digital Twin đại diện cho trạng thái nước của nguồn quan trắc NuoiBien_2, liên kết dữ liệu với đối tượng thực, giữ lịch sử và chất lượng quan sát, phát hiện bất thường, thử dự báo và hỗ trợ người vận hành kiểm tra. Chỉ được khẳng định đại diện cho một ao/lồng cụ thể sau khi xác nhận vị trí, độ sâu và mã đơn vị nuôi. Dữ liệu hiện có không đủ để đại diện toàn bộ trại hoặc tất cả cá trong trại.')
p('Digital Twin được hiểu theo năng lực: một biểu diễn số có định danh, liên kết dữ liệu và mô hình phục vụ mục đích xác định. Trong giai đoạn đầu, vòng phản hồi được khép qua người vận hành: cảnh báo, kiểm tra thực tế, ghi hành động và kết quả. Chưa triển khai tự động điều khiển, chẩn đoán bệnh hoặc khẳng định mô phỏng sinh học đã được kiểm chứng. [S1, §3.2, §5.3 và §5.17; S2, §2]')
p('Báo cáo đề xuất tám phương án. Phương án 1–6 có thể triển khai phần mềm và kiểm chứng bước đầu từ dữ liệu hiện có. Phương án 7 thực hiện ở chế độ nghiên cứu, phát lại hoặc giả lập sự cố; phương án 8 xây được workflow nhưng cần dữ liệu vận hành thực tế để đánh giá hiệu quả. Không coi mọi phương án là đã đủ dữ liệu để vận hành sản xuất.')
h('2. Những vấn đề của việc nuôi cá cần giải quyết')
h('2.1. Chất lượng nước suy giảm và nguy cơ thiếu oxy')
p('Người vận hành cần biết nước đang ở trạng thái nào, thay đổi nhanh hay chậm và có cần kiểm tra hay không. Một giá trị đo tại một điểm có thể không phản ánh toàn bộ thể tích ao/lồng. Với dữ liệu đang có, có thể theo dõi DO, nhiệt độ, pH, độ mặn và độ đục; phát hiện diễn biến bất thường và thử dự báo ngắn hạn. Chưa thể quy kết thiếu oxy do mật độ cao, thức ăn dư hay trao đổi nước nếu không có dữ liệu liên quan. [S1, §5.6–5.8; S2, §4.1]')
h('2.2. Chất thải và độ đục tăng')
p('Thức ăn, hoạt động nuôi và môi trường có thể liên quan đến diễn biến nước; bài toán vận hành là nhận biết sự kiện, kiểm tra nguyên nhân và ghi nhận biện pháp xử lý. Độ đục là tín hiệu hỗ trợ, không phải phép đo trực tiếp phân cá, lượng thức ăn dư hoặc nồng độ chất rắn lơ lửng. Muốn định lượng chất thải cần lấy mẫu đối chiếu và dữ liệu thức ăn, sinh khối, đáy hoặc dòng chảy phù hợp. Báo cáo không suy từ một spike độ đục thành kết luận ô nhiễm.')
h('2.3. Điều kiện bất lợi cho sức khỏe và nguy cơ dịch bệnh')
p('Bài toán từ dữ liệu hiện có là phát hiện biến động môi trường cần kiểm tra cá. Không có nhãn bệnh, quan sát sức khỏe, hao hụt hoặc kết quả chuyên môn nên chưa thể xây bộ chẩn đoán bệnh có căn cứ. Hệ thống cần tạo phiếu kiểm tra khi xảy ra sự kiện môi trường; người có trách nhiệm ghi nhận phản ứng ăn, hành vi và kết quả kiểm tra. [S1, §5.17.8.4]')
h('2.4. Biến động thời tiết, thủy triều và môi trường bên ngoài')
p('Dữ liệu nước ghi nhận diễn biến nhưng chưa xác định tác nhân. Không có dữ liệu mưa, gió, bức xạ, thủy triều hay dòng chảy đồng bộ nên chỉ phân tích được biến động và thời điểm xuất hiện, chưa gán nguyên nhân hoặc dự báo theo thời tiết. Khi bổ sung nguồn ngoài phải giữ riêng quan sát thực tế và bản dự báo có sẵn tại thời điểm ra quyết định.')
h('2.5. Sai số quan trắc và gián đoạn thiết bị')
p('Thiết bị có thể ngừng gửi hoặc tạo giá trị nghi vấn. Nếu hệ thống coi dữ liệu cũ là hiện tại, cảnh báo và quyết định sẽ sai. Cần quản lý độ mới, lỗi thu thập, hiệu chuẩn, sự kiện đến muộn và thiếu dữ liệu như các trạng thái chính thức của twin, thay vì chỉ bỏ các dòng lỗi.')
h('2.6. Thiếu bằng chứng để chọn hành động và đánh giá hiệu quả')
p('Trại cần biết hành động nào được thực hiện, bởi ai, khi nào và kết quả ra sao. Hiện chưa có lịch cho ăn, thiết bị, điện năng, sinh khối, tăng trưởng hay chi phí. Vì vậy, có thể xây quy trình ghi nhận và đối chiếu, nhưng chưa tính được lợi ích thực tế về năng suất, FCR, chi phí điện hoặc tỷ lệ sống. [S1, §5.12–5.13]')
h('3. Kiểm kê dữ liệu và giới hạn thực tế')
p(f'Dữ liệu đầu vào hiện có là Data/aquaculture_indices_clean.csv: {len(rows):,} dòng, {len(rows[0])} cột; từ {dates[0].isoformat()} đến {dates[-1].isoformat()}. Có 1.333 JSON trong thư mục Data. CSV gồm một device nuoibienvien3 và một site NuoiBien_2, chưa có mã ao/lồng riêng.')
p('Chín cột gốc gồm device, site, ts, temperature, salinity, pH, DO, turbidity và sensor_error. Tám cột dẫn xuất gồm DO bão hòa, phần trăm bão hòa, thiếu hụt oxy và tốc độ thay đổi mỗi giờ của năm thông số. Những cột dẫn xuất không phải phép đo độc lập; không được dùng kết quả cùng thời điểm của chúng để rò rỉ nhãn dự báo tương lai.')
p('Có 1.330 dòng chứa số đo và 3 dòng lỗi mở cổng serial thiếu cả năm thông số. Không phát hiện timestamp trùng trong bộ CSV này. Khoảng lấy mẫu trung vị khoảng 905,55 giây, không phải chính xác 15 phút. Gián đoạn lớn nhất khoảng 66 phút ngày 06/11. Cần giữ nguyên thời gian thực khi tính tốc độ và định nghĩa nhãn dự báo.')
for key in ['temperature','salinity','pH','DO','turbidity']:
    vals=[float(r[key]) for r in rows if r[key]]
    p(f'{key}: {len(vals):,} số đo, khoảng {min(vals):g}–{max(vals):g}. Đơn vị chưa được xác nhận trong bản ghi nguồn.')
p('Các sự kiện cần xác minh: độ đục 964,4 → 207,7 → 497,9 ngày 02/11; độ mặn 48,2 → 35,7 giữa hai mẫu ngày 02/11. Chúng được gắn cờ nghi vấn, không tự động xóa hoặc kết luận lỗi cảm biến. Nhiều giá trị độ đục tập trung ở một số mức rời rạc, cần kiểm tra độ phân giải và cách chuyển đổi thiết bị.')
p('Ba cột oxy được tính theo Benson–Krause với áp suất 101,325 kPa; giả định nhiệt độ °C, độ mặn phần nghìn, DO mg/L. Trong 1.330 dòng có số đo, 1.290 dòng có salinity >40 và là ngoại suy ngoài miền DOTABLES công bố. CSV gọn đã gộp các kết quả này; khi lập mô hình cần tái tạo cờ ngoài miền từ salinity, không mặc định mọi giá trị là hợp lệ. Chỉ ưu tiên DO gốc cho phiên bản đầu sau khi xác nhận đơn vị. [W1]')
p('Thiếu metadata: timezone; thời điểm nhận dữ liệu; sensorId riêng; tọa độ/độ sâu; hiệu chuẩn; QC; loài/giai đoạn/đàn; cấu hình đơn vị nuôi. Video tại MinIO chưa được đưa vào bộ dữ liệu đã phân tích. Các mẫu JSON ở thư mục gốc khác thời kỳ/nguồn không được tự nối thành cùng một chuỗi.')
h('4. Kiến trúc Digital Twin và bộ công cụ tối thiểu')
p('Kiến trúc kế thừa sáu lớp của S1: ứng dụng FarmOS; dịch vụ phân tích/dự báo/mô phỏng; lõi quản lý twin; dữ liệu; tích hợp; hạ tầng. Quản trị, bảo mật, truy vết và kiểm chứng xuyên suốt. Các lớp là phân chia trách nhiệm, không bắt buộc triển khai thành nhiều microservice.')
p('Đề xuất MVP: Python và pandas/NumPy cho xử lý; SQLite cho lịch sử và sự kiện thí điểm; Eclipse Ditto cho trạng thái twin khi kiểm thử tích hợp; FastAPI làm giao diện dịch vụ; Streamlit và Plotly làm giao diện người vận hành. Khi nhiều người dùng hoặc dữ liệu tăng, đánh giá PostgreSQL và object storage. Docker Compose có thể đóng gói các thành phần sau khi xác nhận môi trường máy. Các công cụ này là lựa chọn kiến trúc đề xuất, chưa được cài hay chạy trong báo cáo.')
p('Ditto: Thing đại diện đối tượng; attributes chứa định danh và mô tả; features chứa nhóm trạng thái. Đề xuất các nhóm waterQuality, dataHealth, anomalies và forecast có sourceTime, validity, QC, modelVersion và inputSnapshotId. Giữ observed, estimated, predicted, simulated và desired tách riêng trong schema dự án. Hệ thống phải kiểm tra liên kết đối tượng và quyền; Ditto không tự cung cấp mô hình sinh học hoặc bộ tối ưu. [W2; S1, §5.4]')
p('Luồng chung: nguồn JSON/CSV → chuẩn hóa và QC → lưu lịch sử bất biến → cập nhật trạng thái twin → phát hiện bất thường/dự báo → giao diện và phiếu kiểm tra → người vận hành ghi hành động → thu kết quả. Với dữ liệu lịch sử phải hiển thị replayTime, không trình bày timestamp năm 2026 trong tập như quan sát live hiện tại.')

proposal('5. Phương án 1: Twin trạng thái nước và phát lại lịch sử',
 'Thông tin phân tán, khó xem trạng thái nước cùng độ mới, khó truy lại diễn biến trước sự kiện.',
 'Năm số đo gốc, device/site/ts và sensor_error; liên kết từng mẫu với đối tượng nguồn. Các thuộc tính không xác nhận phải để unknown.',
 'Xây state projector: từ sự kiện theo thời gian dựng trạng thái hiện hành có nguồn và QC; cung cấp replay theo tốc độ tùy chọn.',
 'Python, pandas, SQLite; Eclipse Ditto HTTP API cho Thing/Feature; FastAPI; Streamlit/Plotly cho trình diễn. [W2]',
 ['Đóng băng snapshot CSV, ghi checksum và phiên bản; nhập ts thành datetime nhưng chưa tự gán múi giờ nếu chưa xác nhận.',
 'Lập data dictionary cho 17 cột. Ánh xạ site/device; dùng mã đơn vị quan trắc tạm thời và ghi rõ chưa xác nhận ao/lồng.',
 'Lưu observation gốc; tạo eventId ổn định từ nguồn, thời gian và nội dung. Nếu cùng khóa khác giá trị, lưu conflict để xem xét.',
 'Định nghĩa projection: observed gồm số đo, measurementTime và QC; derived nằm riêng. Dòng lỗi cập nhật dataHealth, không ghi số 0 vào chất lượng nước.',
 'Tạo Thing và API cập nhật Feature sau bước xác thực. Lưu mọi lịch sử ở kho ngoài; không chỉ giữ giá trị cuối.',
 'Xây màn hình trạng thái, đường thời gian và nút replay. Khi tới khoảng mất dữ liệu, hiển thị stale/unknown và tuổi dữ liệu thay vì nối như không có gián đoạn.',
 'Kiểm tra replay từ đầu và khôi phục từ checkpoint cho cùng kết quả; tách clock mô phỏng và clock hiện tại.'],
 'Danh mục twin, snapshot trạng thái, biểu đồ lịch sử, API đọc trạng thái và log đồng bộ.',
 'Đối chiếu số dòng nhập với 1.333 dòng nguồn; kiểm tra giá trị tại mốc đầu/cuối; inject duplicate, record đến muộn và lỗi; so hash projection sau replay.',
 'Đây là bản sao quan trắc tại nguồn, chưa phải mô hình không gian toàn trại. Chưa gọi là live twin nếu chưa kết nối dòng đo thực tế.')

proposal('6. Phương án 2: Giám sát chất lượng dữ liệu và sức khỏe cảm biến',
 'Mất kết nối hoặc dữ liệu nghi vấn có thể gây cảnh báo sai và che mất rủi ro vận hành.',
 'ts, sensor_error và năm chuỗi đo; dataHealth là trạng thái twin riêng, được các mô hình khác kiểm tra trước khi chạy.',
 'Luật kiểm tra schema/thiếu dữ liệu/độ mới kết hợp kiểm tra đứng giá trị, bước nhảy và MAD của sai phân. Phân biệt unknown, suspect và invalid.',
 'pandas/NumPy, logging Python, pytest cho replay và inject lỗi; lưu QC dạng bảng hoặc JSON sidecar để CSV trình bày không rối.',
 ['Kiểm tra kiểu dữ liệu, giá trị hữu hạn và tính tăng của timestamp theo nguồn; không áp ngưỡng sinh học khi chưa có loài và đơn vị.',
 'Ước lượng khoảng gửi điển hình từ dữ liệu huấn luyện. Chọn giới hạn stale thử nghiệm có giải thích và thử độ nhạy; không coi đó là SLA đã chấp thuận.',
 'Đánh dấu ba dòng serial_error là sự cố thu thập; xác định khoảng không quan sát và các đoạn liên tục trước/sau.',
 'Phát hiện chuỗi đứng giá trị theo độ phân giải cảm biến; dùng cờ nghi vấn vì giá trị không đổi có thể là hiện tượng thật.',
 'Tính bước nhảy trên thời gian thực, so trung vị và MAD quá khứ; khi MAD=0 dùng phương án sàn theo độ phân giải đã xác nhận hoặc đánh dấu chưa đủ điều kiện.',
 'Ghi QC theo từng thông số, lý do, phiên bản luật và người xác minh. Không sửa raw; nếu nội suy, ghi estimated và lưu phương pháp.',
 'Cung cấp API dataHealth; mô hình dự báo/tư vấn đọc cờ này và từ chối đầu vào không đạt.'],
 'Báo cáo chất lượng, danh sách sự cố, chỉ số tuổi dữ liệu và trạng thái cảm biến cần kiểm tra.',
 'Bắt đúng ba lỗi có sẵn; tạo bản sao dữ liệu thử với dropout, duplicate, đổi timestamp và stuck-value; kiểm tra phát hiện và phục hồi. Báo riêng kiểm thử tổng hợp và xác minh thực địa.',
 'Không phát hiện được toàn bộ calibration drift chỉ từ chuỗi đo. Cần mẫu đối chiếu độc lập, số serial và lịch hiệu chuẩn.')

proposal('7. Phương án 3: Phát hiện bất thường môi trường đa thông số',
 'Theo dõi từng số riêng lẻ có thể bỏ sót diễn biến phối hợp và gây quá nhiều cảnh báo.',
 'Các số đo có QC, độ dốc và đặc trưng quá khứ; cập nhật danh sách sự kiện liên kết nguồn quan trắc trong DT.',
 'Hai tầng: quy tắc dễ giải thích và residual/robust statistics; so sánh Isolation Forest như mô hình ứng viên khi có tập tham chiếu phù hợp. [W3]',
 'pandas rolling theo thời gian; NumPy; scikit-learn IsolationForest/Pipeline; SQLite và giao diện gán nhãn Streamlit.',
 ['Chia dữ liệu theo thời gian, dành đoạn cuối để đánh giá. Không học ngưỡng từ toàn bộ dữ liệu rồi báo kết quả trên chính tập đó.',
 'Tính slope, mức lệch trung vị, độ biến động và missingness từ cửa sổ quá khứ; không dùng rolling centered vì lấy thông tin tương lai.',
 'Tạo luật sự kiện: DO giảm liên tiếp, độ đục spike, nhiều thông số cùng biến động. Số mẫu xác nhận/cooldown là tham số thử nghiệm theo thời gian phản ứng.',
 'Chạy detector robust và Isolation Forest trên tập có chất lượng được xem xét; không ép contamination thành tỷ lệ sự cố thực tế.',
 'Gộp các điểm gần nhau thành sự kiện có start/end, nguồn, đặc trưng gây cảnh báo và QC; tách sensor event với environmental suspicion.',
 'Cho người vận hành xem chuỗi trước/sau, ảnh/video nếu sau này có và nhật ký; gán nhãn confirmed/sensor_issue/unknown.',
 'Đo hiệu quả theo sự kiện; điều chỉnh quy tắc trên tập phát triển, đóng băng trước đánh giá cuối.'],
 'Sổ sự kiện bất thường, bằng chứng, thời gian kéo dài và phiếu xác minh; không xuất kết luận ô nhiễm/bệnh tự động.',
 'Precision/recall cần nhãn xác nhận; trước khi có nhãn chỉ báo số cảnh báo và thời gian review. Kiểm tra thủ công các spike đã ghi nhận và mẫu ngẫu nhiên không cảnh báo để tìm bỏ sót.',
 'Một sự kiện thống kê không chứng minh nguy hiểm sinh học. Sự thay đổi ngưỡng giữa trại/loài cần đánh giá lại.')

proposal('8. Phương án 4: Phân tích quy luật ngày–đêm và thời gian phơi nhiễm',
 'Người vận hành chưa biết thời điểm thường biến động, mức biến động nền và thời gian kéo dài của điều kiện cần kiểm tra.',
 'ts, năm số đo đã QC; xây hồ sơ tham chiếu theo giờ và liên kết vào Twin Services.',
 'Tổng hợp theo giờ, đường trung vị/phân vị; tính thời gian ngoài ngưỡng khi ngưỡng đã được chuyên gia trại xác nhận. Trước đó chỉ báo độ lệch thống kê.',
 'pandas groupby/resample, NumPy, Plotly; file cấu hình có species/stage/unit/thresholdOwner khi có ngưỡng.',
 ['Xác nhận timezone và quy ước ngày; nếu chưa có, ghi kết quả là giờ nguồn, không diễn giải thành giờ địa phương.',
 'Phân đoạn theo ngày; thống kê số mẫu và tỷ lệ có quan sát. Không coi 96 mẫu/ngày là số bắt buộc vì lịch thực khoảng 905 giây.',
 'Tính trung vị, khoảng phân vị, min/max theo giờ cùng số ngày đóng góp; nêu chỉ có khoảng 14 lần lặp chu kỳ ngày.',
 'Vẽ riêng từng ngày và hồ sơ tổng hợp để tránh che các đợt thay đổi giữa ngày; phân tích pH/độ mặn cần đối chiếu hiệu chuẩn.',
 'Khi ngưỡng được duyệt, tính exposure bằng thời gian thực giữa mẫu với giả định rõ; không tích lũy thời gian qua khoảng mất dữ liệu dài.',
 'Báo observed coverage và unknown duration bên cạnh exposure; đề xuất tăng kiểm tra vào cửa sổ hay biến động, chờ xác minh tại trại.'],
 'Hồ sơ giờ nguồn/ngày, danh sách khung giờ cần quan sát thêm, báo cáo độ bao phủ và exposure nếu đủ điều kiện.',
 'Kiểm tra công thức thời gian bằng chuỗi tổng hợp; so hồ sơ giữa hai tuần theo cách thăm dò, không suy kết luận mùa vụ. Đối chiếu ngưỡng và độ bao phủ trước mọi báo cáo vận hành.',
 'Chưa chứng minh sáng sớm luôn rủi ro tại địa điểm này; không gán biến động cho thời tiết nếu chưa có dữ liệu tác nhân.')

proposal('9. Phương án 5: Dự báo DO ngắn hạn có khoảng bất định',
 'Cần biết khả năng diễn biến tiếp theo trước khi số đo thay đổi, đồng thời tránh dự báo gây tự tin quá mức.',
 'DO, nhiệt độ/pH/độ mặn đã QC, độ trễ và thời gian; forecast là predicted state có issueTime, validTime, horizon và modelVersion.',
 'Baseline giữ giá trị cuối; so Ridge hoặc HistGradientBoostingRegressor với lag features. Ưu tiên đơn giản vì chuỗi ngắn; đánh giá rolling-origin. [W4]',
 'pandas, scikit-learn Pipeline/Ridge/HistGradientBoostingRegressor, TimeSeriesSplit sau khi xử lý lịch đo; joblib cho artifact; FastAPI để suy luận.',
 ['Chọn mục tiêu là mẫu kế tiếp với elapsed time kèm theo hoặc mốc thời gian cố định. Hai cách không được trộn; nếu dùng lưới 15 phút, mô tả phép aggregate và không tự lấp nhãn thiếu.',
 'Tạo lag và rolling chỉ từ dữ liệu có sẵn tại issueTime. DO_percent cùng thời điểm tương lai không được làm đầu vào cho DO tương lai.',
 'Chọn split theo thời gian; ví dụ train ban đầu khoảng một tuần, validation mở rộng, giữ vài ngày cuối test. Lịch cụ thể phải điều chỉnh theo số cửa sổ hợp lệ.',
 'Dùng gap tối thiểu đủ để nhãn train không vượt mốc validation; TimeSeriesSplit giả định mẫu cách đều cho so thời lượng, nên lưới không đều phải được xử lý hoặc chia theo timestamp.',
 'Fit scaler/imputer và chọn siêu tham số trên train/validation. Baseline persistence luôn có trong so sánh; không tự coi mô hình ML tốt hơn.',
 'Tạo khoảng dự báo bằng residual trên đoạn calibration trước test hoặc quantile model; kiểm tra coverage thực tế. Chuỗi ngắn và phụ thuộc thời gian có thể làm khoảng không ổn định.',
 'Khi dữ liệu stale hoặc ngoài miền, ngừng dự báo/đánh dấu low-confidence. Lưu mọi forecast trước khi quan sát nhãn để backtest công bằng.'],
 'API và lịch sử dự báo DO, khoảng bất định, báo cáo so baseline theo từng chân trời.',
 'MAE/RMSE/bias và coverage/width; số dự báo đủ đầu vào; báo lỗi theo ngày và theo sự kiện. Nếu không vượt baseline thì giữ baseline hoặc chỉ dùng giám sát.',
 'Với DO gốc quan sát 5,39–6,57 và chưa có nhãn loài, không tuyên bố đã phát hiện hypoxia hay chứng minh cảnh báo ngưỡng thấp chưa từng xảy ra. Cần kéo dài theo dõi qua điều kiện đa dạng.')

proposal('10. Phương án 6: Giám sát thay đổi chế độ và suy giảm mô hình',
 'Phân bố chỉ số có thể đổi theo điều kiện nuôi hoặc đầu đo, làm mô hình/luật cũ không còn phù hợp.',
 'Năm chuỗi QC, các phân vị, tỷ lệ thiếu và residual dự báo khi có; ghi modelHealth riêng trong twin.',
 'So cửa sổ tham chiếu và cửa sổ gần đây bằng mức thay đổi trung vị/phân vị; EWMA/CUSUM như ứng viên; theo dõi sai số dự báo có nhãn đến sau.',
 'pandas, NumPy, SciPy stats nếu dùng kiểm định thăm dò; cấu hình baseline có phiên bản và registry artifact.',
 ['Định nghĩa giai đoạn tham chiếu đã được review; lưu thống kê, tỷ lệ missing và cấu hình đo.',
 'Tính thống kê cửa sổ giờ/ngày. So cùng giờ hoặc hiệu chỉnh quy luật ngày để tránh báo drift chỉ vì đổi thời điểm.',
 'Tạo cờ khi lệch kéo dài và đủ dữ liệu; hiệu chỉnh tham số trên replay, không đặt p-value mặc định thành bằng chứng nguyên nhân.',
 'Đối chiếu với lịch bảo trì, hiệu chuẩn và vận hành khi thu thập được; giữ unknown khi chưa xác minh.',
 'Theo dõi sai số dự báo sau khi có quan sát; nếu suy giảm, hạ trạng thái mô hình và quay về baseline/giám sát.',
 'Chỉ huấn luyện lại sau review dữ liệu; lưu model version cũ, mới và đánh giá giữ riêng trước phát hành.'],
 'Cảnh báo đổi chế độ, sổ điều tra nguyên nhân và quy trình rollback mô hình.',
 'Inject offset/drift có biên độ khác nhau trên bản sao dữ liệu; đo độ trễ và báo giả. Kiểm tra trên chuỗi gốc nhưng không xem cờ drift là nhãn đúng.',
 '14 ngày chỉ đủ minh họa pipeline, chưa đủ chứng minh drift dài hạn hoặc mùa vụ; dữ liệu thay đổi thật và cảm biến trôi có thể giống nhau.')

proposal('11. Phương án 7: Môi trường mô phỏng sự cố và phân tích kịch bản nghiên cứu',
 'Cần kiểm thử độ tin cậy trước khi dùng cảnh báo và đề xuất trong vận hành; đồng thời chuẩn bị cấu trúc mô phỏng can thiệp.',
 'Snapshot lịch sử, QC và mô hình đã lưu; đầu ra chỉ thuộc simulated, tách khỏi observed.',
 'Giai đoạn A: replay và fault injection dựa trên dữ liệu thật. Giai đoạn B: mô hình cân bằng oxy giản lược chỉ dùng nghiên cứu sau khi có tham số bổ sung.',
 'Python, NumPy, pytest, runner replay; SciPy solve_ivp cho ODE khi có mô hình; artifact JSON cho scenario/model/input versions. [W5]',
 ['Chọn một đoạn bình thường và một đoạn có sự kiện; đóng băng snapshot với checksum.',
 'Tạo các kịch bản lỗi: mất 1–n mẫu, gửi chậm, lặp sự kiện, offset đầu đo và mất kết nối. Gắn injected flag trong bản sao, không sửa nguồn.',
 'Chạy cùng pipeline DT, phát hiện và dự báo; kiểm tra stale, chặn đầu vào và khả năng khôi phục.',
 'So kịch bản bằng số cảnh báo, số lần dự báo bị chặn, sai số và mất/trùng trạng thái; lưu giả định và seed để lặp lại.',
 'Đối với cân bằng oxy, xác định dC/dt = kLa(Csat−C) + (Q/V)(Cin−C) + P − R, các hạng cùng đơn vị nồng độ/thời gian. Cần V, Q, Cin, kLa và nhu cầu/nguồn oxy; không suy được riêng các tham số đó từ DO hiện tại.',
 'Chỉ hiệu chỉnh mô hình tác động sau khi có trạng thái thiết bị, sinh khối, trao đổi nước và thử nghiệm phù hợp. Với lồng biển cần mô hình vận chuyển/không gian thích hợp thay vì mặc định ao trộn đều.',
 'Dùng dữ liệu can thiệp giữ riêng để kiểm tra đáp ứng; trước đó chỉ trình bày độ nhạy giả định, không gửi lệnh hay công bố lợi ích sinh học.'],
 'Bộ kiểm thử lỗi tái lập được ngay; cấu trúc scenario runner; mô hình can thiệp chỉ là đầu ra có điều kiện dữ liệu.',
 'Qua các phép thử không mất trạng thái âm thầm, không trộn simulated/observed và không thực thi khi thiếu quyền; ODE cần kiểm tra đơn vị, giới hạn và so quan sát độc lập.',
 'Csat còn có vấn đề độ mặn ngoài miền trong bộ hiện tại. Không hiệu chỉnh mọi tham số trên 14 ngày rồi xem mô phỏng như bằng chứng nhân quả. [S1, §5.17.9; S2, §4.1]')

proposal('12. Phương án 8: Hỗ trợ quyết định và nhật ký sức khỏe/vận hành',
 'Thiếu chuỗi bằng chứng từ cảnh báo đến kiểm tra, hành động và kết quả; chưa có dữ liệu để học tác động điều chỉnh.',
 'Sự kiện từ các phương án trước; bổ sung ghi tay có cấu trúc về quan sát cá, cho ăn, thiết bị và kiểm tra tại chỗ. Workflow là phần FarmOS của DT.',
 'Rule-based triage và phiếu công việc; ưu tiên khuyến nghị kiểm tra, sau đó mới mở rộng khuyến nghị vận hành có mô hình đã kiểm chứng.',
 'Streamlit forms, FastAPI, SQLite/PostgreSQL; phân quyền người xem/người xác minh/người duyệt; audit log append-only.',
 ['Định nghĩa phiếu gồm eventId, target, thời gian, bằng chứng, QC và người phụ trách.',
 'Khi sensor_issue, đề xuất kiểm tra kết nối hoặc phép đo; khi environmental_suspicion, yêu cầu quan sát cá và đo đối chứng theo quy trình trại.',
 'Tạo biểu mẫu cho ăn, trạng thái thiết bị, hao hụt, phản ứng ăn và kết quả kiểm tra. Dùng unit/cohort ID và thời gian để nối.',
 'Ghi quyết định approve/reject/defer và lý do; phiên bản đầu không có kết nối điều khiển.',
 'Nếu sau này có thực thi, tách proposalId/commandId, người duyệt, hạn hiệu lực, liên động và phản hồi thiết bị. Nhận lệnh không đồng nghĩa đã thực thi.',
 'Theo dõi chuỗi nước sau hành động nhưng không tự gọi chênh lệch trước–sau là hiệu quả nhân quả; ghi cả thời tiết và các can thiệp đồng thời.',
 'Tổng hợp thời gian phản ứng, phiếu chưa xử lý và mức đầy đủ nhật ký; dùng kết quả để thiết kế thử nghiệm tiếp theo.'],
 'Giao diện cảnh báo có trách nhiệm, sổ kiểm tra và dữ liệu hành động–kết quả cho vòng phát triển sau.',
 'Test quyền, thay đổi trạng thái, lịch sử không mất và thao tác đồng thời; review phiếu với người vận hành. Khi chưa có người dùng thực, chỉ báo kiểm thử workflow.',
 'Không chẩn đoán bệnh hoặc đề xuất thuốc. Không tính mức tiết kiệm hay FCR nếu thiếu nhật ký thức ăn/sinh khối và đối chứng. [S1, §5.17.8.4, §5.17.10]')

h('13. Kế hoạch thực hiện theo thứ tự và tiêu chí nghiệm thu')
p('Giai đoạn 1 — Xác nhận nguồn: chốt đơn vị, múi giờ, đối tượng đo, vị trí/độ sâu và quyền; kiểm tra các spike với người vận hành. Đầu ra là data dictionary, source manifest và danh sách điều kiện chưa biết. Nếu không xác nhận được, giữ unknown và hạn chế diễn giải.')
p('Giai đoạn 2 — Observation DT: thực hiện phương án 1–2, phát lại đủ 1.333 dòng, kiểm tra lỗi và trạng thái. Tiêu chí: đối chiếu được số lượng/giá trị gốc, không ghi 0 thay missing, không dùng số đo cũ như live và có truy vết.')
p('Giai đoạn 3 — Phân tích/cảnh báo: thực hiện phương án 3–4 và workflow phương án 8. Tiêu chí: sự kiện có bằng chứng, quyền xác nhận, unknown và số liệu bao phủ; không đánh giá accuracy sinh học khi chưa có nhãn.')
p('Giai đoạn 4 — Dự báo và ModelOps: thực hiện phương án 5–6. Tiêu chí: split theo thời gian, không rò rỉ, báo đối chứng và bất định; chỉ chọn model khi có lợi ích trên dữ liệu giữ riêng. Không đặt số MAE kỳ vọng khi chưa thử.')
p('Giai đoạn 5 — Kiểm thử kịch bản: thực hiện phần A phương án 7. Tiêu chí: kết quả replay có thể tái tạo, lỗi được nhận diện và nhánh giả lập không tác động dữ liệu thực.')
p('Giai đoạn 6 — Mở rộng có điều kiện: thu video, sinh khối, trạng thái thiết bị, thời tiết và nhật ký. Chọn mô hình can thiệp sau khi có phép đo/kiểm chứng; thử shadow mode rồi mới đề nghị pilot có duyệt. Không gán thời hạn cố định vì phụ thuộc dữ liệu, mùa vụ và quyền truy cập.')
h('14. Đánh giá hiệu quả và thiết kế thí nghiệm')
p('Theo S1, §5.13, so A — vận hành hiện tại; B — giám sát bằng thiết bị; C — hỗ trợ dự báo; D — tối ưu phối hợp. Với tập đang có chỉ đánh giá được các chức năng offline và baseline, chưa có bằng chứng A/B/C/D tại trại. Phải tách lợi ích do thêm cảm biến khỏi lợi ích mô hình.')
p('Chỉ số kỹ thuật: độ trễ ingest/state theo đồng hồ giả lập hoặc đồng hồ thật được phân biệt; tỷ lệ missing/duplicate; replay consistency; số sự kiện nghi vấn; cảnh báo giả theo sự kiện; MAE/RMSE/bias và coverage dự báo. p95/p99 của test tổng hợp không được gọi là SLA thực địa.')
p('Chỉ số vận hành sau khi có triển khai: thời gian kiểm tra, tỷ lệ cảnh báo được xác minh, tỷ lệ can thiệp thực hiện và thời gian môi trường ngoài giới hạn đã duyệt. Chỉ số kinh tế cần đủ điện, thức ăn, nhân công, bảo trì, hiệu chuẩn, tích hợp và vận hành phần mềm. Báo cả chi phí toàn bộ vòng đời và bất định.')
p('Mỗi thí nghiệm lưu dataset version, hash đầu vào, giai đoạn train/test, cấu hình, seed, phiên bản thư viện, model artifact và báo cáo lỗi. Chưa có nhãn thì không báo precision/recall; không có đối chứng thì không khẳng định mô hình làm tăng năng suất hoặc giảm bệnh.')
h('15. Hồ sơ triển khai và phân công công việc')
p('Đề xuất cấu trúc: raw/ giữ bản nguồn; curated/ giữ QC và chuẩn hóa; features/ giữ cửa sổ trễ; models/ giữ artifact/model card; events/ giữ sự kiện xác minh; scenarios/ giữ snapshot và giả lập; reports/ giữ kết quả. Dữ liệu vận hành trong database, media lớn trong object storage khi có. Khóa phiên bản môi trường trước thử nghiệm; không tự chọn bản development của tài liệu thành bản production.')
p('Người phụ trách trại xác nhận đối tượng, giới hạn và nhật ký; kỹ sư dữ liệu quản lý nguồn/QC; kỹ sư nền tảng quản lý Ditto/API/kho; nhà nghiên cứu mô hình quản lý split, đánh giá và miền hiệu lực; người kiểm thử xác minh replay/phân quyền/sự cố. Một nhóm nhỏ có thể kiêm nhiệm nhưng trách nhiệm phê duyệt vẫn cần rõ.')
p('Đầu ra bàn giao: báo cáo khảo sát; schema và ánh xạ đối tượng; source/QC manifest; mã replay và test; cấu hình Ditto; ứng dụng dashboard; detector/baseline dự báo; báo cáo đánh giá; model card; workflow xác minh; runbook xử lý mất dữ liệu và rollback. Báo cáo này là đặc tả đề xuất cho các đầu ra đó, không phải bằng chứng mã đã được triển khai.')
h('16. Các dữ liệu cần bổ sung theo mức ưu tiên')
p('Ưu tiên 1: xác nhận đơn vị và thang độ mặn; timezone; unitId; sensorId; vị trí/độ sâu; model đầu đo; lịch hiệu chuẩn và mẫu đối chiếu. Đây là điều kiện để diễn giải đúng các chỉ số và trạng thái.')
p('Ưu tiên 2: loài/giai đoạn, cohortId, ngày thả/số lượng, cân mẫu và hao hụt; thời gian/lượng cho ăn; trạng thái và thao tác thiết bị; quan sát sức khỏe. Đây là nền để kết nối nước–cá–vận hành.')
p('Ưu tiên 3: video/âm học đồng bộ, nhãn, chất lượng ảnh, thời tiết/dòng chảy/thủy triều; với ao/RAS có thể thêm thể tích, trao đổi nước và thiết bị oxy/tuần hoàn. Thu theo bài toán và ngân sách, không bắt buộc lắp mọi loại cảm biến.')
p('Ưu tiên 4: chi phí, năng suất, thu hoạch và chuỗi lô; dữ liệu trại/mùa giữ riêng. Chỉ số TSS, NH3, CO2 hay điểm phù hợp loài chưa được suy ra từ bộ năm thông số nếu thiếu hiệu chuẩn, TAN, carbonate hoặc quy chuẩn thích hợp.')
h('17. Tài liệu tham khảo và nguồn đối chiếu')
p('S1. Digital Twin Platform Design (EN).pdf và bản DOCX cùng tên trong thư mục. Chương 2: bằng chứng; chương 3: kiến trúc; chương 5, nhất là §5.3–5.8, §5.12–5.17: AquaTwin/FarmOS. Thiết kế đề xuất, không phải chứng nhận hay báo cáo hiệu quả sản xuất.')
p('S2. Føre, M. và cộng sự (2024). Digital Twins in intensive aquaculture — Challenges, opportunities and future prospects. Computers and Electronics in Agriculture 218, 108676. DOI: 10.1016/j.compag.2024.108676. Bản PDF trong thư mục; §2 về thành phần/năng lực, §4 về các concept oxy/tăng trưởng/robotics.')
p('S3. Iranshahi, K. và cộng sự (2025). Digital twins: Recent advances and future directions in engineering fields. Intelligent Systems with Applications 26, 200516. DOI: 10.1016/j.iswa.2025.200516. Khái niệm, digital thread và các hạn chế liên ngành; không gán đánh giá trưởng thành liên ngành cho dự án này.')
p('S4. VinUni_GREEN-X_Digital_Twin_Ecosystem.pdf. Kiến trúc tham chiếu, ứng dụng AquaTwin, tái sử dụng nền tảng và kiểm chứng; không chuyển roadmap chiến lược thành tiến độ cam kết.')
p('Dữ liệu: Data/aquaculture_indices_clean.csv; 1.333 JSON dưới Data; derived_indices_README.md và aquaculture_indices_clean_README.txt. Các con số mô tả dữ liệu trong báo cáo được kiểm tra trực tiếp ngày 13/11/2026.')
p('W1. USGS DOTABLES và OWQ Technical Memorandum 2011.03: https://water.usgs.gov/water-resources/software/DOTABLES/ ; https://water.usgs.gov/admin/memo/QW/qw11.03.pdf . Công thức và miền sử dụng của chỉ số oxy.')
p('W2. Eclipse Ditto, Things: https://eclipse.dev/ditto/basic-thing.html . Đối chiếu mô hình đối tượng. Chọn phiên bản phát hành khi triển khai.')
p('W3. scikit-learn, IsolationForest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html . Công cụ ứng viên phát hiện điểm bất thường; không cung cấp nhãn nguyên nhân sinh học.')
p('W4. scikit-learn, TimeSeriesSplit: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html . Chia dữ liệu theo thời gian; cần lưu ý lịch lấy mẫu và khoảng gap.')
p('W5. SciPy, solve_ivp: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html . Bộ giải bài toán giá trị đầu ODE, không phải mô hình thủy sản có sẵn.')
p('Các liên kết công cụ W2–W5 được đối chiếu ngày 13/11/2026. Bản báo cáo tổng hợp diễn giải và đề xuất triển khai; không sao chép dài nguyên văn, không dùng tuyên bố phần mềm như bằng chứng hiệu quả tại trại.')

for para in d.paragraphs:
    for run in para.runs:
        run.font.name='Times New Roman';run.font.size=Pt(13);run.font.color.rgb=RGBColor(0,0,0)
        fonts=run._element.get_or_add_rPr().rFonts
        if fonts is not None:
            for attr in ['ascii','hAnsi','eastAsia','cs']:fonts.set(qn('w:'+attr),'Times New Roman')
footer=s.footer.paragraphs[0]
footer.add_run('Trang ').font.name='Times New Roman'
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
d.save(out)
check=Document(out)
assert not check.tables and not check.inline_shapes
assert all(r.font.name=='Times New Roman' for pp in check.paragraphs for r in pp.runs)
assert sum(bool('Phương án ' in pp.text and pp.runs and pp.runs[0].bold) for pp in check.paragraphs)==8
print(out)
print('Paragraphs:',len(check.paragraphs),'Words:',sum(len(pp.text.split()) for pp in check.paragraphs))
