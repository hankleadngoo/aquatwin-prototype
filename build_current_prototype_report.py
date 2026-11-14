"""Generate an as-built report from the actual prototype snapshot, not the roadmap."""
from pathlib import Path
from datetime import datetime
import json,subprocess,statistics,hashlib,zipfile
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent
APP=ROOT/'aquatwin-app'
DATA=json.loads((APP/'dist/data.json').read_text(encoding='utf-8'))
DEPLOY=json.loads((ROOT/'aquatwin-deployment.json').read_text(encoding='utf-8'))
script="const C=require('./dist/core.js'),d=require('./dist/data.json');console.log(JSON.stringify({qc:C.summary(d,d.rows.length-1),eventPoints:C.events(d,d.rows.length-1).length,latest:C.currentTwin(d,d.rows.length-1),backtests:Object.fromEntries(C.keys.map(k=>{const b=C.backtest(d,k);delete b.pairs;return [k,b]}))}));"
METRICS=json.loads(subprocess.check_output(['node','-e',script],cwd=APP,text=True,encoding='utf-8'))
DOC=Document();section=DOC.sections[0]
section.page_width=Cm(21);section.page_height=Cm(29.7)
section.top_margin=section.bottom_margin=Cm(2)
section.left_margin=Cm(2.5);section.right_margin=Cm(2)
style=DOC.styles['Normal'];style.font.name='Times New Roman';style.font.size=Pt(13)
style.paragraph_format.line_spacing=1.15;style.paragraph_format.space_after=Pt(6)
TEXT=[]
def p(t):
 DOC.add_paragraph(t);TEXT.append(t)
def h(t):
 pp=DOC.add_paragraph();pp.add_run(t).bold=True
 pp.paragraph_format.space_before=Pt(12);pp.paragraph_format.keep_with_next=True
 TEXT.append('\n'+t)
def num(x):return f'{x:.5f}'.replace('.',',')

h('BÁO CÁO CHI TIẾT PROTOTYPE AQUATWIN HIỆN CÓ')
p('Hồ sơ hiện trạng sản phẩm, kiến trúc, dữ liệu, giả lập, công nghệ, tích hợp, kiểm thử và giới hạn.')
p('Ngày lập: 14/11/2026. Phiên bản ứng dụng: 1.2.0. Đây là báo cáo as-built, mô tả những gì đã có trong mã nguồn và bản triển khai, tách riêng chức năng chưa thực hiện.')
p('Địa chỉ công khai: '+DEPLOY['url'])
p('Hình thức trình bày: văn bản Times New Roman cỡ 13, mục đánh số; không dùng bảng hoặc hình. Những con số kỹ thuật được tái tính từ snapshot dist/data.json bằng chính hàm của ứng dụng.')

h('1. Tóm tắt điều hành')
p('AquaTwin hiện là prototype theo dõi chất lượng nước tại nguồn quan trắc Nuôi Biển 2. Ứng dụng sử dụng dữ liệu lịch sử thật, tổ chức một bản sao trạng thái theo trạm đo và năm nhóm vấn đề cho người nuôi: biến động nhiệt; nguy cơ thiếu oxy; biến động axit–kiềm; biến động tính chất nước qua độ dẫn điện; giảm độ trong của nước. Menu chính gồm trang tổng quan và năm trang vấn đề, còn công cụ kỹ thuật nằm trong mục Công cụ & kết nối.')
p('Các phần chạy được gồm xem số đo và QC; phát lại lịch sử; tính trạng thái observed và last_good; thống kê theo ngày; xem dấu hiệu cần xác minh; đặt giá trị giả định và khoảng tham chiếu thử nghiệm; hiển thị baseline dự đoán khi dữ liệu đủ điều kiện; backtest đối chứng; giả lập ba tình huống lỗi dữ liệu; ghi nhật ký và xuất các tệp dữ liệu/cấu hình.')
p('Digital Twin trong phiên bản hiện tại chủ yếu là Observation Twin/digital shadow: dữ liệu đi vào biểu diễn số và được dùng hỗ trợ kiểm tra. Chưa phải bản sao sinh học toàn trại, chưa có mô hình tăng trưởng, bệnh, thức ăn, dòng chảy hay điều khiển tự động. Phần phản hồi vận hành là biểu mẫu ghi nhận bởi con người, chưa nối vòng điều khiển với thiết bị thực.')
p('Bản online đã deploy thành công, mở public theo xác nhận của người dùng và chứa 1.333 bản ghi thật. Nó là website tĩnh; trạng thái và phân tích chạy trên trình duyệt. Bản cục bộ có thêm gateway Python để tích hợp Ditto tại localhost, nhưng chưa có bằng chứng kết nối bản phát hành Ditto thật trong môi trường này. Các kiểm thử tích hợp sử dụng mock HTTP có kiểm soát.')

h('2. Căn cứ và phương pháp lập báo cáo')
p('Căn cứ chính: package.json; prepare_data.py; dist/data.json; dist/core.js; dist/app.js; dist/ditto.js; dist/workspace.js; dist/hosting.js; server.py; tests.cjs; test_bridge.py; browser_test.cjs; các cấu hình ditto-config; hosting manifest và biên nhận deploy. Ngữ cảnh nghiệp vụ tham khảo prototype.md trong Downloads, Digital Twin Platform Design chương 3 và 5, các tài liệu tổng quan đã khảo sát.')
p('Mã nguồn tại commit '+DEPLOY['commit_sha']+' là nguồn được đẩy để xuất bản version 1 trên Sites. Ngày lập báo cáo, HEAD của checkout trùng commit này. Trạng thái dịch vụ Sites được kiểm tra lại: URL đang có bản live, quyền public, version_number 1.')
p('Khi mô tả README cũ khác mã đang chạy, báo cáo ưu tiên mã nguồn, manifest và trạng thái dịch vụ. README còn chứa một số đoạn từ giai đoạn chưa deploy và phần cập nhật lỗi dấu; các đoạn đó không được dùng để kết luận prototype hiện vẫn chưa xuất bản. Báo cáo không sửa hoặc redeploy app trong lần lập hồ sơ này.')

h('3. Bài toán nghiệp vụ và phạm vi giải quyết')
h('3.1. Nhiệt độ — theo dõi biến động nhiệt')
p('Mục đích là giúp người nuôi nhận biết diễn biến nhiệt, kiểm tra phép đo và ghi nhận bối cảnh như nắng, mưa, thay nước hoặc tuần hoàn. Ứng dụng không khẳng định một số đo gây sốc nhiệt hoặc dùng một dải nhiệt an toàn chung cho mọi loài.')
h('3.2. DO — theo dõi nguy cơ thiếu oxy')
p('App hiển thị nồng độ oxy hòa tan và tốc độ thay đổi, hỗ trợ kiểm tra đầu đo, quan sát cá và tình trạng thiết bị oxy/tuần hoàn nếu có. Chưa có giới hạn DO theo loài/giai đoạn được phê duyệt. Tên mục là nhóm nguy cơ cần theo dõi, không chứng minh dữ liệu đã có sự kiện cá thiếu oxy.')
h('3.3. pH — theo dõi biến động axit–kiềm')
p('App hiển thị pH, diễn biến và cờ QC; gợi ý đo đối chiếu, kiểm tra hiệu chuẩn và ghi thao tác nước. Không tính độc tính ammonia, CO₂ hoặc liều hóa chất từ riêng pH. Chưa có TAN, độ kiềm và mô hình cân bằng cần thiết.')
h('3.4. Độ dẫn điện — theo dõi biến động tính chất nước')
p('Trường salinity trong dữ liệu cũ đã được xác nhận là độ dẫn điện mS/cm. App đổi nghĩa trường sang conductivity mà không thay giá trị số. Nó hỗ trợ phát hiện thay đổi cần đối chiếu, nhưng chưa tính độ mặn PSU và không kết luận sốc mặn hoặc ô nhiễm chỉ từ conductivity.')
h('3.5. Độ đục — theo dõi giảm độ trong')
p('App hiển thị độ đục NTU và những điểm biến động để người dùng kiểm tra thực địa. Không tự suy ra lượng thức ăn dư, phân cá, chất rắn lơ lửng hoặc mầm bệnh. Cần dữ liệu bổ sung và hiệu chuẩn địa phương để mở rộng những kết luận đó.')
p('Quy tắc chung: một chỉ số tương ứng một mục theo dõi để giao diện dễ dùng; quan hệ này không đồng nghĩa một chỉ số có duy nhất một nguyên nhân. Các điều kiện môi trường, sinh học và vận hành vẫn có thể tương tác.')

h('4. Dữ liệu hiện tại và chuẩn hóa ý nghĩa')
rows=DATA['rows'];times=[datetime.fromisoformat(r['ts']) for r in rows]
gaps=[(b-a).total_seconds() for a,b in zip(times,times[1:])]
p(f'Nguồn đóng gói là {DATA["meta"]["source"]}; {len(rows):,} bản ghi, từ {rows[0]["ts"]} đến {rows[-1]["ts"]}. Múi giờ nguồn UTC+07:00 được ghi theo xác nhận so khớp ThingsBoard trong prototype.md. Một site NuoiBien_2 và một device nuoibienvien3. Có 1.330 dòng có phép đo, 3 dòng lỗi cổng serial.')
p(f'Khoảng lấy mẫu trung vị {statistics.median(gaps):.2f} giây, xấp xỉ 15 phút 5,5 giây; khoảng gián đoạn dài nhất {max(gaps)/60:.2f} phút. Lịch lấy mẫu không chính xác 15 phút; mục dự báo hiển thị ~15 phút chỉ là xấp xỉ một mẫu kế tiếp.')
for key,config in DATA['params'].items():
 vals=[r['values'][key] for r in rows if r['values'][key] is not None]
 p(f'{config["label"]}: {len(vals):,} giá trị, min {min(vals):g}, max {max(vals):g}; đơn vị {config["unit"] or "pH không đơn vị"}.')
p('Nhiệt độ °C, DO mg/L, độ đục NTU và pH được documented theo GREEN-X trong prototype.md; conductivity mS/cm được ghi confirmed. Độ sâu, vị trí lồng/ao, mã đàn và tham chiếu hiệu chuẩn chưa được xác nhận. Metadata tương ứng để null; không tự sinh vị trí hoặc thông tin cá.')
p('CSV dùng làm nguồn có các cột oxy dẫn xuất từ bước xử lý cũ. Tuy nhiên, ứng dụng chỉ lấy năm chỉ số gốc, ánh xạ conductivity và không đưa DO bão hòa, %DO hoặc thiếu hụt oxy cũ vào data.json vì chúng được tính theo giả định salinity sai. App hiện cũng chưa tính Practical Salinity bằng PSS-78.')
p('Mỗi record trong data.json có ts, site, device, values, error, gapMinutes, id và qc. Mã id được tạo bằng 24 ký tự đầu của SHA-256 từ site + device + ts; metadata giữ SHA-256 toàn bộ CSV nguồn. Đây là định danh ổn định trong snapshot này, chưa phải cơ chế chống xung đột bản ghi hoàn chỉnh cho ingest liên tục.')
p('Công cụ chuẩn bị dữ liệu đọc CSV, sắp theo ts, giữ nguyên giá trị, tính QC và ghi asset JSON. Nó không trực tiếp theo dõi thư mục JSON gốc, không đọc MinIO và không nghe MQTT. Vì vậy, muốn cập nhật nguồn phải chạy lại bước chuẩn bị và xuất bản snapshot mới.')

h('5. Kiến trúc tổng thể')
h('5.1. Ánh xạ với kiến trúc DT sáu lớp')
p('Lớp ứng dụng: giao diện HTML/CSS/JavaScript, trang tổng quan và năm nhóm vấn đề; biểu mẫu nhật ký và công cụ kỹ thuật. Lớp dịch vụ DT: QC, events, phân tích ngày, baseline/backtest, kiểm thử giả lập. Lõi DT: currentTwin dựng observed, last_good và health theo con trỏ phát lại. Lớp dữ liệu: CSV nguồn, data.json và localStorage. Lớp tích hợp: gateway REST Python, adapter CLI và mẫu cấu hình MQTT. Lớp hạ tầng: trình duyệt và hosting tĩnh Sites; thêm tiến trình Python khi chạy cục bộ.')
p('Đây là ánh xạ trách nhiệm logic theo tài liệu, không có sáu máy chủ hoặc sáu microservice độc lập. Phần lớn chức năng nằm trong một static frontend; gateway là thành phần tùy chọn của bản local.')
h('5.2. Kiến trúc bản online')
p('CSV tại máy phát triển → prepare_data.py → dist/data.json + các asset frontend → archive gắn commit → Sites → trình duyệt người xem. Khi mở trang, browser tải toàn bộ snapshot rồi tính projection, sự kiện, thống kê, baseline và giao diện. Không có backend Python trên bản hosting static.')
p('Nhật ký và khoảng thử nằm ở localStorage của từng browser/origin. Hai thành viên xem cùng URL không tự thấy ghi chú hoặc khoảng thử của nhau. Dữ liệu quan trắc chung là bản tĩnh đã phát hành; chưa có cập nhật realtime hay database dùng chung.')
h('5.3. Kiến trúc bản cục bộ')
p('Browser → server.py tại 127.0.0.1:8765 → asset frontend và API /api/ditto/*. Gateway đọc data.json, dựng snapshot từ cursor, dùng tài khoản trong biến môi trường để gửi request tới Ditto loopback nếu đã cấu hình. Máy chủ Ditto không nằm trong gói đã cài của prototype; Docker không khả dụng ở lần kiểm tra môi trường trước.')
p('server.py dùng ThreadingHTTPServer của thư viện chuẩn để phục vụ prototype. Nó chưa phải application server được harden để công khai. Không cần React, Vue, FastAPI, pandas, Plotly, TimescaleDB, MongoDB hoặc broker MQTT để chạy phần demo hiện tại. MongoDB chỉ là phụ thuộc có thể cần khi nhóm triển khai Ditto riêng; chưa được dựng cho prototype này.')

h('6. Công nghệ và vai trò từng thành phần')
p('Frontend: HTML5, CSS responsive và JavaScript thuần; hash routing bằng location.hash; DOM rendering bằng template strings; Fetch API tải data.json và gọi gateway local; Web Storage API lưu nhật ký/khoảng thử. Biểu đồ là SVG được dựng bằng mã, không dùng thư viện chart bên ngoài.')
p('Giao diện: màu nền sáng và thanh điều hướng tối, font Be Vietnam Pro tải qua Google Fonts, có system font fallback. Font của giao diện web khác Times New Roman được dùng cho báo cáo này. Không có engine 3D hay hình học mô phỏng thật của lồng/ao.')
p('Data preparation: Python chuẩn thư viện với csv, json, datetime và hashlib. Kiểm soát chất lượng là quy tắc viết trong prepare_data.py; ngưỡng được xuất kèm data.json. Chưa có trình cấu hình QC trên giao diện; nút xuất QC tải cấu hình hiện hành.')
p('Gateway và CLI: Python chuẩn thư viện http.server và urllib. Định dạng tích hợp: JSON Thing, Policy và Ditto Protocol. Xác thực gateway→Ditto dùng Bearer token hoặc Basic auth trong môi trường; browser không có ô nhập mật khẩu Ditto.')
p('Kiểm thử: Node.js với assert cho core; Python unittest và mock HTTP server cho gateway; Chrome headless với DevTools Protocol/WebSocket cho kiểm tra giao diện. Không dùng Jest, pytest hoặc Playwright trong bộ kiểm thử riêng của app này. Các kiểm thử pytest được prototype.md nhắc thuộc pipeline khác.')
p('Đóng gói và hosting: Git commit, tar archive, .openai/hosting.json với static.directory = dist, Sites quản lý version và quyền truy cập. Không có bước npm install/build framework; package.json cung cấp lệnh start/test và version sản phẩm.')

h('7. Danh mục giao diện và tính năng')
h('7.1. Tổng quan khu nuôi')
p('Hiển thị thời điểm nguồn đang phát, trạng thái dữ liệu chung, năm thẻ vấn đề, số đo hiện tại, cờ QC và đánh giá theo khoảng thử. Có biểu đồ chọn chỉ số, thanh trượt phát lại, nút phát/tạm dừng và đi tới cuối tập. Mỗi thẻ đưa đến trang vấn đề tương ứng.')
p('Trạng thái chung đếm số chỉ số có QC 3, 4 hoặc 9 tại cursor. Nếu có ít nhất một, hiển thị Cần xác minh dữ liệu; nếu không, hiển thị Đã có số đo để theo dõi. Nó không tổng hợp sức khỏe cá, năng suất hay trạng thái thiết bị thật. Việc người dùng nhập khoảng thử không tự sửa thuật toán trạng thái chung này.')
h('7.2. Năm trang vấn đề')
p('Các route là #problem-temperature, #problem-DO, #problem-pH, #problem-conductivity và #problem-turbidity. Mỗi trang có số đo, QC, đánh giá theo khoảng thử, tốc độ thay đổi giữa hai mẫu, biểu đồ lịch sử, khối giả lập, dự đoán tham khảo, danh sách gợi ý kiểm tra và nút ghi quyết định.')
p('Tốc độ thay đổi = (giá trị hiện tại − giá trị trước)/(thời gian thực tính theo giờ). Chỉ tính khi hai giá trị có mặt, khoảng cách dương và không quá 30 phút. Tốc độ trên màn hình chưa tự loại mọi cặp QC nghi vấn; cần đọc cùng cờ dữ liệu. Đây là hiệu sai phân khoảng đo, không phải tốc độ tức thời hoặc chứng minh nguyên nhân.')
h('7.3. Công cụ Digital Twin')
p('Route #twin hiển thị sơ đồ quan hệ mang tính khái niệm giữa site, trạm đo và nguồn; bảng observed/last_good của từng feature; JSON hợp đồng Thing để xuất. Quan hệ là cấu trúc định sẵn cho một trạm, chưa có graph database hay ontology reasoning. Không đại diện bố trí lồng ngoài thực tế.')
h('7.4. Chất lượng dữ liệu và sự kiện')
p('Route #quality hiển thị phân bố cờ, QC từng bài tại cursor, lỗi thiết bị, gap và lưu ý đơn vị. Route #events lọc nhóm biến động chỉ số hoặc thiết bị/gián đoạn; mỗi dấu hiệu có thời gian, lý do QC và nút xác minh. Danh sách hiển thị tối đa 70 dấu hiệu mới nhất; có xuất JSON.')
p('Sự kiện ở đây chủ yếu là record–parameter bị gắn cờ, không được gộp thành những sự cố môi trường độc lập. Một đợt đứng giá trị kéo dài có thể tạo nhiều dấu hiệu. Nhãn xác minh lưu nhật ký nhưng chưa có vòng cập nhật bộ nhãn detector hoặc trạng thái resolved cho từng sự kiện.')
h('7.5. Phân tích môi trường')
p('Route #insights giữ các thẻ định hướng bài toán nước, chất thải, sức khỏe, tác nhân ngoài, thiết bị và độ tin cậy. Có chuỗi toàn giai đoạn đã phát và thống kê theo ngày: số mẫu đạt QC, trung bình, min/max. Trung bình là trung bình các mẫu được chọn, không phải trung bình trọng số theo thời gian hoặc thể tích toàn khu nuôi.')
h('7.6. Phòng thử nghiệm')
p('Route #lab tính baseline persistence và sai số trên đoạn 30% cuối snapshot, chọn từng chỉ số. Có fault sandbox cho mất dữ liệu 45 phút, bản ghi trùng và bản ghi đến muộn. Đây là khối nghiên cứu riêng, sử dụng toàn snapshot ngay cả khi cursor đang ở mốc sớm; giao diện ghi rõ phạm vi backtest.')
h('7.7. Nhật ký vận hành')
p('Route #journal có loại ghi nhận kiểm tra môi trường, sức khỏe cá, cho ăn, thiết bị/bảo trì và thời tiết; có thời gian, người thực hiện, đối tượng, trạng thái xác minh, lượng/đơn vị và nội dung. Mỗi trang vấn đề còn có biểu mẫu quyết định nhanh; sự kiện QC có biểu mẫu xác minh. Có xuất JSON nhật ký.')
p('Bản ghi được tạo bởi người dùng và gắn createdAt, snapshot hoặc eventId khi phù hợp. Đây là dữ liệu nhập tay, không phải phản hồi thiết bị đã được đo xác nhận. Lưu localStorage không tạo chứng cứ bất biến: người dùng có thể xóa/chỉnh qua công cụ browser; chưa có audit server, phân quyền cá nhân hay cộng tác nhiều người.')
h('7.8. Dữ liệu và cấu hình')
p('Route #data có hồ sơ nguồn, hash CSV, trạng thái năng lực, dải QC và bảng số đo theo ngày. Bảng hiển thị tối đa 100 bản ghi mới nhất trong bộ lọc/phạm vi đã phát. Nút xuất CSV chuẩn hóa xuất toàn bộ snapshot nguồn, không chỉ 100 dòng đang nhìn. Xuất cấu hình QC ở JSON; không sửa ngưỡng QC trực tiếp trên UI.')
h('7.9. Kết nối Eclipse Ditto')
p('Route #ditto có kiểm tra kết nối, khởi tạo phần còn thiếu, đồng bộ snapshot sau QC, đọc Thing và xuất Policy/MQTT connection/Ditto Protocol. Chỉ bản local có gateway thực. Bản online bị hosting.js chặn gọi gateway, giải thích cần dùng môi trường cục bộ; không phát request tới localhost người xem.')

h('8. Mô hình bản sao số và quản lý trạng thái')
p('Thing ID: aquatwin:nuoibien-2. Attributes gồm site, device, timezone và sourceMapping. Năm feature tương ứng temperature, conductivity, pH, DO, turbidity; feature health giữ tình trạng dữ liệu. Một feature không được hiểu là một twin sinh học độc lập.')
p('Mỗi feature đo có properties.observed = {value, ts, unit, qualityFlag}; last_good = {value, ts} hoặc null. Observed giữ giá trị gốc ngay cả khi nghi vấn; missing là null. last_good được tìm lùi từ cursor đến điểm QC 1 gần nhất, không thay thế observed và không được diễn giải là số đo đang còn mới.')
p('Feature health gồm mode = historical-replay, sourceTime, deviceError, depth_m, calibration_ref, unit_id, spikeStatus và qcVersion. Trường chưa biết là null. Ứng dụng chưa tính tuổi dữ liệu realtime so với đồng hồ hiện tại để vận hành live; chỉ thể hiện mốc replay và thử stale trong sandbox.')
p('Thang trạng thái theo tài liệu có observed, estimated, predicted, simulated và desired, nhưng Thing hiện chỉ xuất observed, last_good và health. Giá trị giả lập nằm trong state giao diện; baseline hiển thị không được ghi vào nhánh predicted của Thing; không có desired instruction. Đây là khác biệt quan trọng giữa kiến trúc mục tiêu và implementation hiện tại.')

h('9. Cơ chế QC đang sử dụng')
p('Phiên bản cấu hình: qc-ui-0.2-provisional. Quy ước cờ: 1 đạt; 2 chưa đánh giá; 3 nghi vấn; 4 không đạt; 9 thiếu. Cờ này đánh giá chất lượng dữ liệu, không phải mức nguy hiểm cho cá. Các ngưỡng được chép thành cấu hình trong prepare_data.py theo prototype.md, chưa đối chiếu bit-for-bit với engine QC của pipeline khác.')
p('Missing: value null hoặc sensor_error thì cờ 9. Gross range: ngoài dải cấu hình thì cờ 4; riêng turbidity từ 1.000 đến 1.100 được cờ 3. Site plausible: ngoài khoảng tham chiếu QC thì cờ 3. Rate of change: |Δvalue|/Δgiờ vượt mức cấu hình thì cờ 3; chỉ xét khoảng dương, không quá 30 phút.')
p('Spike: so |value − (previous + next)/2| với hai ngưỡng; cờ 3 hoặc 4 khi vượt. Cần có cả hai lân cận, mỗi khoảng không quá 30 phút. Vì dùng mẫu tiếp theo, tại cursor app buộc spike = 2 và tính lại cờ tổng hợp, tránh sử dụng tương lai khi phát lại. Khi phát sang mẫu sau, QC điểm trước có thể được hoàn tất.')
p('Flat line: chuỗi bằng chính xác giá trị liên tiếp với khoảng đo không quá 30 phút, từ 4 giờ gắn cờ 3, từ 12 giờ cờ 4. Đây là heuristic; đầu đo có độ phân giải thấp hoặc môi trường ổn định có thể bị gắn cờ nhiều. Chưa có tolerance theo từng cảm biến hoặc phép đo đối chiếu để phân biệt chắc chắn.')
for key,conf in DATA['params'].items():
 p(f'QC {conf["label"]} ({conf["unit"] or "không đơn vị"}): gross {conf["gross"][0]}–{conf["gross"][1]}; site plausible {conf["plausible"][0]}–{conf["plausible"][1]}; spike suspect/fail {conf["spike"][0]}/{conf["spike"][1]}; ROC {conf["roc"]}/giờ. Các giá trị đều là cấu hình thử nghiệm dữ liệu, không dùng làm ngưỡng vận hành cho loài cá.')
p('Cờ tổng hợp: missing ưu tiên 9; còn lại lấy mức nặng nhất trong bài có cờ 1/3/4, không có thì 2. Do đó cờ tổng hợp 1 không có nghĩa tất cả sáu bài đã hoàn tất: spike tại cursor có thể chưa đánh giá nhưng các bài khác đã đạt. Màn hình kỹ thuật cho xem cờ riêng từng bài.')
counts=METRICS['qc'];total=sum(counts.values())
p(f'Tái tính tại cursor cuối: tổng {total:,} phép đo = 1.333 × 5; đạt {counts["1"]:,}; nghi vấn {counts["3"]:,}; không đạt {counts["4"]:,}; thiếu {counts["9"]:,}; chưa đánh giá tổng hợp {counts["2"]:,}. Tỷ lệ cờ 1 khoảng {counts["1"]/total*100:.2f}%. Đây là kết quả của cấu hình provisional, không phải tỷ lệ môi trường an toàn.')
p(f'Hàm events trả {METRICS["eventPoints"]:,} dấu hiệu record/chỉ số và gap/lỗi trong toàn snapshot. Con số này không phải {METRICS["eventPoints"]:,} lần xảy ra sự cố trại độc lập. Tại mốc cuối, pH và turbidity có cờ nghi vấn do heuristic đứng giá trị; vì vậy tổng quan báo 2/5 luồng cần xác minh.')

h('10. Kiến trúc giả lập và dự đoán')
h('10.1. Giả lập từng chỉ số')
p('Đầu vào gồm giá trị giả định do người dùng nhập và nhãn thời điểm sau 15, 30 hoặc 60 phút. Hàm assessValue so giá trị với low/high của khoảng thử cục bộ: thấp hơn low, cao hơn high hoặc trong khoảng; nếu chưa nhập khoảng thì trả chưa đặt tham chiếu. Hàm renderScenario tính chênh lệch với số đo hiện tại và hiển thị kết quả.')
p('Khoảng thời gian 15/30/60 phút chỉ là nhãn kịch bản; không được dùng trong phương trình tiến hóa trạng thái. Giả lập không tự dự đoán giá trị sau thời gian đó và không suy ra mức oxy do sục khí hoặc pH do hóa chất. scenarioState chỉ nằm trong bộ nhớ phiên; reload mất kịch bản. observed, CSV và Thing không thay đổi.')
p('Khoảng thử lưu từng chỉ số ở localStorage; kiểm tra nhập số hữu hạn và low < high. Khoảng mặc định trống, không có species/stage approval. Trong khoảng thử chỉ có nghĩa so sánh số học đạt khoảng người dùng đặt, không xác nhận tình trạng sinh học.')
h('10.2. Dự đoán tham khảo trên trang vấn đề')
p('Công thức duy nhất hiện tại là persistence: y_hat(t+1) = y(t). Chỉ hiển thị khi số đo khác null và cờ tổng hợp tại cursor là 1. Nếu không, trang nêu chưa tạo dự đoán; không lấy last_good để giả làm quan sát hoặc forecast mới. Chưa có mô hình học máy được train và phát hành.')
p('Không có khoảng bất định, biến thời tiết, trạng thái thiết bị hay mô hình sinh học trong forecast. Một bước là mẫu kế tiếp theo lịch nguồn, khoảng 15 phút nhưng không đều. Baseline không kích hoạt cảnh báo, thay đổi thiết bị hay khẳng định rủi ro cá.')
h('10.3. Backtest trong phòng thử nghiệm')
p('Hàm backtest chọn split floor(1.333 × 0,7) = 933; duyệt những cặp mẫu liên tiếp từ phần sau mốc này. Đầu vào dự báo là giá trị trước; nhãn là giá trị tiếp theo. Loại null, sensor_error, khoảng không dương hoặc trên 30 phút. Cặp cũng bị loại nếu QC của đầu vào hoặc nhãn không đạt khi bỏ test spike để không chọn đầu vào bằng mẫu tương lai.')
p('Dải thời gian đánh giá hiển thị bắt đầu 08/11/2026 19:32:46 đến 12/11/2026 23:54:44. Chưa có huấn luyện, tìm siêu tham số, cross-validation nhiều mùa/trại hoặc kiểm định độc lập; 70% đầu không phải tập train của một mô hình học trong baseline này. Kết quả là lỗi trên phần đuôi đã lọc QC, không đại diện toàn bộ điều kiện hoặc điểm bị loại.')
for key,b in METRICS['backtests'].items():
 p(f'Baseline {DATA["params"][key]["label"]}: {b["count"]} cặp; MAE {num(b["mae"])}; RMSE {num(b["rmse"])}; bias {num(b["bias"])}. Đơn vị theo chỉ số gốc. Bias trong code là trung bình prediction − actual.')
p('Các số sai số trên được tính lại bằng mã app, không phải bằng chứng cải thiện so phương pháp khác. Sai số nhỏ của chuỗi ít biến động hoặc bị lọc không chứng minh khả năng cảnh báo sự cố hiếm. Báo cáo không thêm mô hình nâng cao hoặc hiệu quả sinh học chưa kiểm chứng.')
h('10.4. Giả lập sự cố dữ liệu')
p('Mất luồng 45 phút: sandbox lấy timestamp nguồn cộng 45 phút, tính tuổi dữ liệu, đánh dấu stale vì vượt mốc thử 30 phút và không đủ điều kiện đề xuất. Gửi trùng: dùng Set khóa id cho hai bản sao của record, nhận hai nhưng chấp nhận một cập nhật logic. Đến muộn: dùng một record cũ so với timestamp hiện tại và giữ projection không lùi.')
p('Đây là các đoạn mô phỏng logic trên bản sao dữ liệu trong trình duyệt. Chưa thực hiện ngắt mạng thật, broker replay, viết correction lịch sử vào database, crash recovery hay lưu trạng thái connector. Không gọi các kịch bản này là bằng chứng chịu lỗi toàn hệ thống production.')

h('11. Gợi ý quyết định và vòng phản hồi')
p('Gợi ý hiện là danh sách câu hướng dẫn theo từng nhóm vấn đề, không do optimizer hoặc mô hình nhân quả sinh ra. Với QC không đạt, app ưu tiên xác minh phép đo; khi QC đạt vẫn chỉ hỗ trợ kiểm tra. Nội dung gồm đo đối chiếu, kiểm tra đầu đo, ghi bối cảnh, quan sát cá và chuyển người có chuyên môn. Không tự đề xuất liều thuốc, hóa chất hoặc lượng thức ăn.')
p('Quy trình sử dụng hiện tại: chọn mốc → xem số đo/QC → đọc diễn biến → có thể thử giá trị và khoảng tham chiếu → xem baseline nếu đủ điều kiện → kiểm tra thực tế → người vận hành ghi quyết định. Bản ghi có problem key và snapshot để truy vết. Chưa có xác nhận thực thi thiết bị hoặc đo lợi ích sau can thiệp tự động.')
p('Tên “gợi ý quyết định” trong UI cần được hiểu là hỗ trợ quy trình kiểm tra, không phải tối ưu hành động vật lý. Chưa có hàm mục tiêu chi phí, ràng buộc phúc lợi loài, mô hình tác động hoặc so sánh lợi ích kinh tế của nhiều phương án.')

h('12. Tích hợp Eclipse Ditto: phần có mã và phần chưa chạy thật')
p('Gateway có GET /api/health; GET /api/ditto/status; GET /api/ditto/thing; POST /api/ditto/provision; POST /api/ditto/sync. sync nhận cursor, dựng snapshot từ dataset phía Python; không nhận URL hoặc payload Thing tùy ý từ browser. Gateway chỉ bind 127.0.0.1; kiểm tra Host/Origin, JSON và kích thước POST tối đa 2.048 byte.')
p('Cấu hình môi trường: DITTO_URL mặc định http://127.0.0.1:8080; chỉ cho hostname loopback. Xác thực qua DITTO_TOKEN hoặc DITTO_USER/DITTO_PASSWORD; DITTO_SUBJECT xác định chủ thể owner. HTTP redirect bị chặn và proxy môi trường không được dùng cho kết nối loopback. Không có credential được nhúng trong asset online.')
p('Provision đọc Policy/Thing trước; chỉ tạo nếu 404 với If-None-Match: *. Không ghi đè những đối tượng đã tồn tại. Policy owner có quyền đọc/ghi Thing và Policy; ingest chỉ ghi /features; observer đọc Thing. Không có quyền message để điều khiển thiết bị.')
p('Sync đọc Thing, kiểm tra đúng Policy và sourceTime, chặn snapshot cũ hơn; nội dung giống nhau thì bỏ trùng. Nếu cần cập nhật, yêu cầu ETag và dùng If-Match. Thuộc tính/feature khác được giữ lại trong body; sau PUT thực hiện GET và đối chiếu features. Đây là kiểm soát phiên bản cho một snapshot, không thay thế transaction nhiều tài nguyên hoặc kiểm soát mọi writer bên ngoài.')
p('Các tệp cấu hình trong ditto-config gồm Thing snapshot, Policy template, MQTT connection template và Ditto Protocol example. Connection mặc định closed; URI broker cần đổi đúng môi trường, quyền và TLS do nhóm triển khai. Chưa có broker, connector live, payload mapper tùy chỉnh hoặc SSE listener đang hoạt động. UI đọc trạng thái Ditto bằng GET qua gateway khi có server, không giả vờ nhận realtime events.')
p('ditto_adapter.py là CLI nhận snapshot JSON và có dry-run; chỉ gửi PUT Thing với tài khoản môi trường, không gửi lệnh thiết bị. Nó đơn giản hơn gateway và không có toàn bộ bảo vệ sourceTime/ETag của sync trong server.py. Nên ưu tiên gateway cho thử nghiệm đồng bộ có kiểm soát.')
p('Kết quả đã kiểm tra chỉ là mock gateway và schema snapshot; chưa có integration report với Ditto thật. Không coi nút giao diện hoặc tệp connection mẫu là bằng chứng máy chủ đã kết nối.')

h('13. Triển khai, lưu trữ và quyền truy cập')
p('URL: '+DEPLOY['url']+'. Audience: public theo xác nhận của chủ dự án cho phép dùng dữ liệu thật và bất kỳ ai có đường dẫn. Người xem có thể tải asset dữ liệu của bản công khai; đây không phải chế độ dữ liệu riêng tư theo tài khoản.')
p('Mã sản phẩm 1.2.0 khác số version hosting 1 và bridgeVersion 1.1.0: ba giá trị dùng cho ba lớp khác nhau. Saved version ID: '+DEPLOY['version_id']+'. Deployment ID: '+DEPLOY['deployment_id']+'. Trạng thái publish succeeded.')
p('Kho online chỉ phục vụ dist; server.py không được thực thi trên static hosting. hosting.js nhận diện hostname không phải loopback và chặn Ditto action bằng thông báo phù hợp. Không có đường hầm về VPN/MinIO hoặc máy cá nhân của người xem.')
p('LocalStorage sử dụng aquatwin-journal-v1 cho nhật ký và aquatwin-problem-ranges-v1 cho khoảng thử. Đây là lưu trữ theo origin: nội dung ở localhost không tự xuất hiện ở URL online hoặc browser khác. scenarioState, cursor và kết quả đọc Ditto là state bộ nhớ, reload có thể mất. Chưa có đăng nhập, database người dùng, phân quyền nghiệp vụ hoặc chia sẻ nhật ký nhóm.')
p('Gói ZIP và launcher cục bộ cho phép chạy không cần build frontend. Máy cần Python; Node cần cho test và npm scripts. Tệp Mo_AquaTwin.cmd gọi start-app.ps1, mở browser và server local ẩn. stop-app.ps1 kiểm tra PID/command line trước khi dừng server do app tạo; quyền hệ điều hành có thể yêu cầu đúng phiên hoặc quyền chạy phù hợp.')

h('14. Kiểm thử đã có và bằng chứng')
p('Lần lập báo cáo chạy lại node tests.cjs thành công: số dòng, source mapping, thứ tự thời gian, missing, không đọc tương lai tại cursor, last_good, events, QC counts, split backtest, escape và timezone. Đây là bộ assert core, không gọi số assert là test case riêng nếu chưa có test runner thống kê.')
p('Python unittest test_bridge.py chạy lại 11 test, đều pass. Các nhóm gồm snapshot/missing/last_good; cursor không hợp lệ; Policy không cấp actuator message; chặn endpoint ngoài; chưa cấu hình; provision create-only; sync xác minh/dedupe/chống lùi; giữ feature khác; thiếu ETag/xung đột; không follow redirect; kiểm tra Origin và payload API. Máy chủ đích của bộ test là mock loopback.')
p('browser_test.cjs đã chạy ở phiên cập nhật UI trước: kiểm tra 6 navigation item chính; 5 trang giả lập và khoảng thử; các trang kỹ thuật; trạng thái Ditto chưa cấu hình; desktop 1.440 × 1.080 và mobile 390 × 844 không tràn ngang; replay, sandbox, lưu nhật ký và không có JavaScript runtime exception trong chuỗi thao tác. Báo cáo này đọc lại mã và bằng chứng đó, không khẳng định đã chạy lại browser suite hoặc kiểm tra mọi browser sau deploy.')
p('Chưa có kiểm thử tải đồng thời, endurance dài ngày, độ bền localStorage, kiểm thử bảo mật chuyên sâu, audit accessibility đầy đủ, thử mất điện/mạng tại trại hay xác nhận lợi ích sản xuất. Source test pass không chứng minh tỷ lệ phát hiện bệnh, cảnh báo môi trường hoặc giảm chi phí.')

h('15. Danh mục mã nguồn và đầu ra')
files=[('dist/index.html','Khung trang và thứ tự nạp script/style.'),('dist/styles.css; dist/workspace.css','Giao diện responsive và bố cục theo 5 vấn đề.'),('dist/app.js','Các màn hình kỹ thuật, biểu đồ SVG, form, export, replay và event binding.'),('dist/core.js','QC theo cursor, projection, last_good, events, summary và baseline backtest.'),('dist/workspace.js','Tổng quan mới, 5 trang, khoảng thử, giả lập và quyết định nhanh.'),('dist/ditto.js','Giao diện gateway Ditto và template tích hợp.'),('dist/hosting.js','Hành vi bản xem chung, chặn gateway local trên host công khai.'),('dist/data.json','Snapshot dữ liệu, metadata và QC đã chuẩn bị.'),('prepare_data.py','Đọc CSV, ánh xạ conductivity, tính QC và đóng gói dữ liệu.'),('server.py','Server local và Ditto bridge; snapshot phía Python.'),('ditto_adapter.py; ditto-config/','CLI và cấu hình JSON tham khảo.'),('tests.cjs; test_bridge.py; browser_test.cjs','Kiểm thử core, gateway mock và browser.'),('Mo_AquaTwin.cmd; start-app.ps1; stop-app.ps1','Khởi động/dừng bản local.'),('.openai/hosting.json; package.json','Site identity, static deploy config, lệnh và phiên bản.'),('README.md; DITTO_INTEGRATION.md','Hướng dẫn sử dụng và tích hợp; đọc cùng báo cáo do còn đoạn README cũ.'),('aquatwin-deployment.json ở workspace','Biên nhận URL, version, deployment, quyền public và commit đã triển khai.')]
for name,role in files:p(name+': '+role)
p('Các dữ liệu VPN, tài khoản MinIO, browser profile, .runtime và log không nằm trong asset deploy. Báo cáo không đọc hoặc ghi lại nội dung file credential của workspace.')

h('16. Hướng dẫn thao tác theo tình huống')
h('16.1. Người nuôi kiểm tra một chỉ số')
p('Mở URL; chọn Tổng quan; xem timestamp lịch sử; chọn một trong năm vấn đề; xem số đo và cờ QC; kéo con trỏ nếu cần xem diễn biến; đọc gợi ý kiểm tra. Nếu QC nghi vấn, ưu tiên đo đối chiếu, không diễn giải màu QC thành mức nguy hiểm của cá.')
h('16.2. Thử đánh giá giả lập')
p('Chọn trang vấn đề; nếu có thông tin phù hợp thì nhập low/high để tạo khoảng thử, nếu không giữ trống; nhập giá trị giả định và nhãn thời gian; bấm đánh giá; xem chênh lệch và phân loại so khoảng. Thay đổi giả định không cập nhật số đo thật. Có thể xóa khoảng thử bằng nút riêng.')
h('16.3. Xem dự đoán và kiểm tra độ tin cậy')
p('Khi QC đạt, trang hiện persistence cho mẫu kế tiếp; đọc đúng nhãn baseline. Nếu QC không đạt, app chưa tạo dự đoán. Muốn xem sai số lịch sử, mở Công cụ & kết nối → Kiểm thử; chọn chỉ số và xem số cặp, MAE/RMSE. Không lấy sai số trung bình để cam kết an toàn ở các tình huống ngoài dữ liệu.')
h('16.4. Ghi nhận kiểm tra')
p('Bấm Ghi nhận quyết định/kiểm tra; nhập người phụ trách và quan sát thực tế. Sau lưu, mở Nhật ký để xem và xuất JSON sao lưu. Người khác không tự thấy nội dung đó; nếu cần làm việc nhóm phải trao đổi file hoặc phát triển backend dùng chung.')
h('16.5. Kiểm tra kết nối Ditto')
p('Dùng bản local; cấu hình môi trường và máy chủ Ditto; chọn Công cụ & kết nối → Kết nối Ditto; kiểm tra status; tạo phần thiếu; chọn timestamp và đồng bộ; đọc Thing đối chiếu. Không thao tác trên bản public để kết nối localhost; không đưa mật khẩu vào browser.')

h('17. Những giới hạn và rủi ro kỹ thuật cần biết')
p('Thứ nhất, quy mô dữ liệu nhỏ: một nguồn, khoảng 14 ngày. Không đánh giá được đại diện mùa vụ, trại khác, nhiều đàn hoặc sự cố hiếm. Không có nhãn xác nhận nguyên nhân môi trường, sức khỏe và tác động hành động.')
p('Thứ hai, engine QC provisional có thể gắn nhiều cờ đứng giá trị do độ phân giải; chưa có hiệu chuẩn/đối chiếu chuyên môn. Sự kiện là dấu hiệu điểm đo, chưa có gộp incident, giảm báo lặp, trạng thái xử lý hoặc phản hồi học detector.')
p('Thứ ba, pipeline chuẩn bị dữ liệu hiện dành cho snapshot một nguồn; so lân cận theo danh sách toàn bộ, chưa phân vùng state nhiều site/device. Định danh dựa site/device/ts chưa giải quyết hai payload khác nhau cùng thời điểm. Không có watermark, ingest timestamp, dead-letter queue hoặc streaming ingest.')
p('Thứ tư, lõi twin trong browser dựng lại từ asset thay vì state service bền vững. Một số hàm quét lịch sử và dùng indexOf; flatline quét ngược nhiều điểm. Chưa benchmark với nhiều trạm hoặc dữ liệu hàng triệu dòng, chưa có virtualization cho bảng và quản lý tải lớn.')
p('Thứ năm, chưa có mô hình vật lý/sinh học, assimilation, solver ODE, ML training hay policy optimizer trong app. Sự hiện diện baseline, slider hoặc MQTT template không chứng minh các năng lực này đã có. Last_good cũng không có chính sách tuổi tối đa được kiểm chứng cho quyết định thực.')
p('Thứ sáu, persistence trên một đoạn cuối và lọc QC có thể tạo đánh giá thuận lợi hơn toàn bộ thời gian; không có so sánh mô hình nâng cao, predictive interval hoặc independent validation. Giả lập cho nhập giá trị số học không kiểm tra đầy đủ miền sinh học hay động học của quá trình.')
p('Thứ bảy, localStorage không phải database/audit nghiệp vụ; có thể mất khi xóa browser và không chia sẻ nhóm. Bản public không yêu cầu tài khoản; không có phân vai người duyệt, chữ ký quyết định hoặc lịch sử bất biến. Nếu cần dữ liệu nhạy cảm phải thay đổi mô hình truy cập theo yêu cầu chủ dự án.')
p('Thứ tám, gateway local mới kiểm thử mock. Nó không phải reverse proxy production; chưa kiểm tra mọi cấu hình xác thực Ditto. Cần xác nhận mapping subject, ETag và Policy trên bản Ditto thực trước khi chạy trại. Không có điều khiển thiết bị, live stream hoặc đảm bảo điều khiển khi mất kết nối.')

h('18. Lộ trình nâng cấp được đề xuất, chưa phải tính năng hiện có')
p('Ưu tiên 1: xác nhận vị trí/độ sâu, thông số đầu đo, hiệu chuẩn và unitId; đối chiếu heuristic QC và dữ liệu nghi vấn với người vận hành. Tách cấu hình QC có phiên bản rõ khỏi mã và sửa hồ sơ README lỗi thời.')
p('Ưu tiên 2: triển khai Ditto thật trên môi trường test; chạy ma trận integration và replay; bổ sung kho lịch sử có quyền truy cập, ingest idempotent, xử lý late/conflict và trạng thái freshness thực.')
p('Ưu tiên 3: database nhật ký nhóm, xác thực/phân quyền, audit và sao lưu; gộp sự kiện theo incident, phản hồi xác minh và thông báo có giới hạn/cooldown.')
p('Ưu tiên 4: dữ liệu dài hơn và nhãn độc lập; xây dự báo có so baseline, đánh giá ngoài thời gian/trại và bất định. Chỉ phát hành khi mục đích và tiêu chí chấp nhận được xác nhận.')
p('Ưu tiên 5: thu trạng thái thiết bị, sinh khối, cho ăn, hình học và trao đổi nước; phát triển mô hình tác động, kiểm chứng can thiệp và mới xem xét điều phối có quyền. Camera/âm học và mô hình sức khỏe là dự án con cần dữ liệu/nhãn và đánh giá riêng.')

h('19. Nguồn kiểm chứng và phiên bản báo cáo')
p('Nguồn triển khai được kiểm tra qua Sites get_site ngày 14/11/2026: public, live URL và version 1. Biên nhận workspace khớp commit nguồn. Báo cáo không thực hiện đổi domain, thay audience, upload dữ liệu mới hoặc redeploy.')
p('Nguồn kỹ thuật trực tiếp là các tệp liệt kê mục 15. Kho ví dụ tham khảo: https://github.com/eclipse-ditto/ditto-examples ; phần mqtt-quick-introduction và mqtt-bidirectional. Tài liệu thiết kế tham chiếu là Digital Twin Platform Design (EN), chương 3 và 5. Những tài liệu này định hướng thiết kế, không thay thế bằng chứng tính năng thực thi.')
p('Ngữ nghĩa dữ liệu dựa prototype.md ngày 14/11/2026. Tệp rule.md được ghi chú nhắc tới nhưng không có sẵn trong checkout đã kiểm tra; không tuyên bố báo cáo đã kiểm toán toàn bộ quy tắc của pipeline khác. Các phiên bản QC, app, bridge và hosting đã được tách rõ ở trên để tránh nhầm lẫn.')

for pp in DOC.paragraphs:
 for run in pp.runs:
  run.font.name='Times New Roman';run.font.size=Pt(13);run.font.color.rgb=RGBColor(0,0,0)
  rf=run._element.get_or_add_rPr().rFonts
  if rf is not None:
   for k in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+k),'Times New Roman')
foot=section.footer.paragraphs[0]
run=foot.add_run('AquaTwin 1.2.0 — Hồ sơ hiện trạng — Trang ');run.font.name='Times New Roman';run.font.size=Pt(10)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
OUT=ROOT/'Bao_cao_DT_Aquaculture';OUT.mkdir(exist_ok=True)
file=OUT/'Bao_cao_chi_tiet_hien_trang_AquaTwin_Prototype.docx'
DOC.save(file)
(OUT/'Bao_cao_chi_tiet_hien_trang_AquaTwin_Prototype.txt').write_text('\n\n'.join(TEXT),encoding='utf-8')
(OUT/'AquaTwin_prototype_report_metrics.json').write_text(json.dumps(METRICS,ensure_ascii=False,indent=2),encoding='utf-8')
check=Document(file)
assert not check.tables and not check.inline_shapes
assert all(r.font.name=='Times New Roman' for pp in check.paragraphs for r in pp.runs)
assert zipfile.ZipFile(file).testzip() is None
print(file)
print('Paragraphs:',len(check.paragraphs),'Words:',sum(len(pp.text.split()) for pp in check.paragraphs),'Bytes:',file.stat().st_size)
