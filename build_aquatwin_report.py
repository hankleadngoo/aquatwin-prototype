from pathlib import Path
import json, re
import fitz
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).parent
OUT=ROOT/'Bao_cao_DT_Aquaculture'
OUT.mkdir(exist_ok=True)
note=Path(r'C:\Users\ACER\.codex\attachments\104d28bc-4530-4fcd-a481-2b91f06ce969\Pasted text.txt').read_text(encoding='utf-8-sig')
sources=[]
for p in ROOT.glob('*.pdf'):
    pdf=fitz.open(p)
    pages=[page.get_text() for page in pdf]
    (OUT/(p.stem+'.txt')).write_text('\n\n'.join(f'--- Trang PDF {i+1} ---\n{t}' for i,t in enumerate(pages)),encoding='utf-8')
    sources.append({'file':p.name,'pages':len(pages),'text_characters':sum(map(len,pages))})
(OUT/'source_manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')

def figure(name, labels, subtitle):
    fig,ax=plt.subplots(figsize=(10,6.7));ax.set_xlim(0,10);ax.set_ylim(0,10);ax.axis('off')
    for i,(title,desc) in enumerate(labels):
        y=8.8-i*1.35
        ax.add_patch(FancyBboxPatch((.6,y-.67),8.8,1.05,boxstyle='round,pad=0.08',facecolor='#edf5f7',edgecolor='#167d8d',linewidth=1.2))
        ax.text(5,y+.04,title,ha='center',va='center',fontsize=12,fontweight='bold',color='#123a53')
        ax.text(5,y-.32,desc,ha='center',va='center',fontsize=9,color='#334955')
        if i<len(labels)-1:ax.annotate('',xy=(5,y-1.02),xytext=(5,y-.77),arrowprops={'arrowstyle':'->','color':'#167d8d','lw':1.5})
    ax.text(5,.35,subtitle,ha='center',fontsize=9,color='#536575',wrap=True)
    fig.savefig(OUT/name,dpi=180,bbox_inches='tight');plt.close(fig)

figure('kien_truc.png',[
 ('Ứng dụng và giải pháp — FarmOS','Dashboard • cảnh báo • kịch bản • phê duyệt • nhật ký kết quả'),
 ('Dịch vụ Digital Twin','Ước lượng • phát hiện bất thường • dự báo • mô phỏng • tối ưu'),
 ('Lõi Digital Twin','Định danh • quan hệ • trạng thái • đồng bộ • vòng đời'),
 ('Dữ liệu','Chuỗi thời gian • ảnh/video/âm thanh • tham số • nguồn gốc'),
 ('Tích hợp và tương tác','Adapter • API • sự kiện • chuẩn hóa • kết nối đối tác'),
 ('Hạ tầng','Edge tại trại • máy chủ/cloud • mạng • lưu trữ')],
 'Nguồn thực tế nằm ngoài lõi; bảo mật, quản trị, kiểm chứng và vận hành xuyên suốt sáu lớp.')
figure('luong_van_hanh.png',[
 ('1. Quan sát và tiếp nhận','Cảm biến • máy đo • camera • nhật ký • trạng thái thiết bị'),
 ('2. Kiểm tra và đồng bộ','Schema • đơn vị • thời gian • hiệu chuẩn • chất lượng • định danh'),
 ('3. Ước lượng và dự báo','Chốt snapshot đầu vào • chạy phiên bản mô hình • lượng hóa bất định'),
 ('4. Mô phỏng và so sánh','Giữ nguyên vận hành / phương án thay đổi • ràng buộc • chi phí'),
 ('5. Đề xuất và phê duyệt','Lý do • thời hạn • người duyệt • kiểm tra điều kiện tại edge'),
 ('6. Thực thi và kiểm chứng','Phản hồi thiết bị • đo kết quả • đối chiếu dự báo • lưu bằng chứng')],
 'Kết quả thực tế quay lại bước 1–3; mất dữ liệu hoặc thiếu quyền phải chặn hành động liên quan.')

doc=Document(); sec=doc.sections[0]
sec.top_margin=Cm(2);sec.bottom_margin=Cm(2);sec.left_margin=Cm(2.2);sec.right_margin=Cm(2)
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
normal=doc.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(11)
normal.paragraph_format.space_after=Pt(6);normal.paragraph_format.line_spacing=1.12
for name in ['Title','Subtitle','Heading 1','Heading 2','Heading 3']:
    doc.styles[name].font.name='Calibri'
    doc.styles[name].font.color.rgb=RGBColor.from_string('123A53')
for name,size in [('Heading 1',17),('Heading 2',13),('Heading 3',11)]:doc.styles[name].font.size=Pt(size)
header=sec.header.paragraphs[0];header.text='NGHIÊN CỨU ỨNG DỤNG  |  DIGITAL TWIN TRONG NUÔI TRỒNG THỦY SẢN';header.style='Caption'
footer=sec.footer.paragraphs[0];footer.alignment=2
footer.add_run('Bản tổng hợp 1.0 • 12/11/2026  |  Trang ')
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)

def p(text,style=None):return doc.add_paragraph(text,style)
def h(text,level=1):doc.add_heading(text,level)
def bullets(items):
    for t in items:p(t,'List Bullet')
def table(headers,rows):
    t=doc.add_table(rows=1, cols=len(headers));t.style='Light Shading Accent 1'
    for c,s in zip(t.rows[0].cells,headers):c.text=s
    for row in rows:
        for c,s in zip(t.add_row().cells,row):c.text=str(s)
    for row in t.rows:
        for c in row.cells:
            for pp in c.paragraphs:
                pp.paragraph_format.space_after=Pt(3)
                for r in pp.runs:r.font.size=Pt(9)
    trPr=t.rows[0]._tr.get_or_add_trPr();repeat=OxmlElement('w:tblHeader');trPr.append(repeat)
    p('')
def pic(file,caption):doc.add_picture(str(OUT/file),width=Cm(16));p(caption,'Caption')

p('BÁO CÁO TỔNG HỢP','Title')
p('DIGITAL TWIN TRONG NUÔI TRỒNG THỦY SẢN','Title')
p('Nền tảng khái niệm • Kiến trúc • Bài toán ứng dụng\nPhương pháp xử lý • Luồng vận hành • Kiểm chứng','Subtitle')
p('Biên soạn theo góc nhìn nghiên cứu ứng dụng\nPhiên bản 1.0 — Ngày 12 tháng 11 năm 2026')
p('Cơ sở: ghi chú người dùng; bốn PDF trong thư mục dự án; đối chiếu chương 2, 3 và 5 của bản DOCX Digital Twin Platform Design (EN).')
p('Phạm vi: thiết kế hệ thống và kế hoạch nghiên cứu. Chưa có bộ dữ liệu telemetry, video hay kết quả thử nghiệm của trại được cung cấp để huấn luyện hoặc đánh giá mô hình.')
doc.add_page_break()
h('Tóm tắt điều hành')
p('Dự án được xác định là xây dựng hệ thống Digital Twin đa nguồn dữ liệu cho một đơn vị nuôi cụ thể: tái hiện trạng thái và quan hệ đối tượng; phát hiện bất thường; dự báo chỉ số; mô phỏng phương án can thiệp; đề xuất điều chỉnh và ghi nhận phản hồi thực tế. Hệ thống phải tiến triển từ dữ liệu đáng tin cậy đến mô hình được kiểm chứng, trước khi đưa khuyến nghị vào vận hành. [N1; S1, §5.1–5.8]')
p('Kiến trúc sử dụng sáu lớp của báo cáo thiết kế: ứng dụng, dịch vụ DT, lõi DT, dữ liệu, tích hợp và hạ tầng. AquaTwin chuyên biệt hóa các lớp cho thủy sản; FarmOS cung cấp quy trình vận hành. Eclipse Ditto là ứng viên triển khai một phần lõi trạng thái và truy cập, kết nối với kho lịch sử và các dịch vụ phân tích bên ngoài. Đây là phương án kỹ thuật cần thử nghiệm, không phải khẳng định đã hoàn thành sản phẩm. [S1, §3.2, §5.3; D1]')
p('Ưu tiên đề xuất: một ao/bể/lồng và một quyết định có thể đo tác động. Nếu có dữ liệu oxy và thiết bị phù hợp, bắt đầu bằng Water Quality Twin kết hợp Equipment Twin; tiếp theo bổ sung mô hình tăng trưởng và hành vi ăn. Bối cảnh ao, RAS và lồng biển cần các cấu hình khác nhau; không mặc định sục khí là hành động khả thi cho mọi hệ thống. [S1, §5.6.1; S2, §4.1; đề xuất tổng hợp]')
h('Cách sử dụng và mức độ bằng chứng',2)
p('Ký hiệu nguồn [S1]–[S4], [N1], [D1] được giải thích cuối báo cáo. “Theo nguồn” chỉ nội dung tài liệu; “Đề xuất” chỉ lựa chọn nghiên cứu/thiết kế cho dự án. Ngưỡng sinh học, độ trễ, độ chính xác và mức tiết kiệm phải được xác lập bằng khảo sát và thử nghiệm; báo cáo không đặt các giá trị đó như kết quả đã đạt.')
table(['Nguồn','Vai trò và giới hạn'],[
 ('S1 — Platform Design','Đặc tả kiến trúc, hợp đồng dữ liệu và kiểm chứng; là thiết kế đề xuất, không phải chứng nhận hay báo cáo hiệu quả triển khai.'),
 ('S2 — Føre và cộng sự, 2024','Cơ sở chuyên ngành: dữ liệu, mô hình, đồng hóa dữ liệu; ba concept lồng biển. Không coi các concept là AquaTwin đã được triển khai.'),
 ('S3 — Iranshahi và cộng sự, 2025','Khái niệm DT/model/shadow, digital thread và các hạn chế liên ngành; không chuyển điểm đánh giá chuyên gia thành độ trưởng thành riêng của dự án.'),
 ('S4 — GREEN-X','Bối cảnh chiến lược và tái sử dụng nền tảng; các địa điểm, lộ trình và kiến trúc tham chiếu không tự chứng minh triển khai.'),
 ('N1 — Ghi chú','Đầu vào về cách hiểu và nhu cầu; được chuẩn hóa chính tả, thuật ngữ và chỉnh những diễn giải chưa chính xác.')])
h('Mục lục nội dung')
for s in ['1. Định nghĩa và phạm vi Digital Twin','2. Thuật ngữ và quy ước dữ liệu','3. Kiến trúc hệ thống','4. Xác định bài toán aquaculture','5. Phương pháp giải quyết đề xuất','6. Luồng vận hành và kịch bản minh họa','7. Thiết kế kiểm chứng và chỉ số đánh giá','8. Lộ trình triển khai và đầu ra','9. Giới hạn và quyết định cần chốt','10. Nguồn và đối chiếu ghi chú']:p(s)
doc.add_page_break()
h('1. Định nghĩa và phạm vi Digital Twin')
p('Digital Twin (DT, bản sao số) là biểu diễn số gắn với một đối tượng/hệ thống xác định, được cập nhật bằng dữ liệu từ đối tượng đó, kết hợp mô hình để mô tả trạng thái, ước lượng những gì khó quan sát, dự báo và hỗ trợ quyết định. Phạm vi mô hình và tần suất cập nhật phụ thuộc mục đích sử dụng. [S1, §3.1; S2, §2; S3, §1]')
p('Trong aquaculture, đối tượng có thể là ao/bể/lồng, đàn vật nuôi, thiết bị hoặc quá trình cho ăn. Một đối tượng có thể có nhiều twin theo mục đích; mỗi twin có các thuộc tính/trạng thái và mô hình tương ứng. Vì vậy, câu “một twin là một thuộc tính” trong ghi chú cần được sửa: oxy là một đại lượng trạng thái, còn Water Quality Twin là biểu diễn có cấu trúc cho mục đích theo dõi và phân tích nước. [N1; S1, §5.3.3–5.4]')
h('1.1. Phân biệt các khái niệm gần nhau',2)
table(['Khái niệm','Đặc trưng','Hàm ý'],[
 ('Digital Model','Mô hình số không có liên kết cập nhật tự động với đối tượng.','Vẫn có thể chạy mô phỏng; mô phỏng đơn thuần chưa chứng minh twinning.'),
 ('Digital Shadow','Theo phân loại luồng dữ liệu: cập nhật tự động từ thực sang số.','Theo dõi trạng thái; mức độ mô hình hóa phải được công bố riêng.'),
 ('Digital Twin','Có định danh, liên kết dữ liệu, mô hình và dịch vụ theo mục đích. Một số tác giả dùng tiêu chí trao đổi tự động hai chiều.','Báo cáo dùng cách mô tả theo năng lực; công bố rõ vòng phản hồi là khuyến nghị có người duyệt hay tự động.'),
 ('Dashboard / mô hình 3D','Giao diện trình bày số đo hoặc không gian.','Là thành phần tùy chọn; không tự chứng minh năng lực dự báo, mô phỏng hay điều khiển.')])
p('Khác biệt định nghĩa cần giữ rõ: S3, §3.1 nhấn mạnh luồng dữ liệu tự động hai chiều; S2, §2.2 phân biệt DT mô tả, dự báo, khuyến nghị và tự chủ; S1 cho phép DT giám sát hoặc có điều khiển. Do đó, không khẳng định tự động điều khiển là điều kiện duy nhất trong mọi tài liệu, cũng không gán mọi dashboard là DT hoàn chỉnh.')
h('1.2. Các mức năng lực',2)
p('S2 phân biệt: 0 — standalone (tiền thân mô hình chưa nối thực); 1 — descriptive (mô tả); 2 — diagnostic (phát hiện/đánh giá sự cố); 3 — predictive (dự báo); 4 — prescriptive (khuyến nghị); 5 — autonomous (tự chủ). Đề xuất dự án đi từ mức mô tả đến dự báo và khuyến nghị có giám sát, không đặt tự chủ là đầu ra ban đầu. [S2, tr. PDF 6]')
h('1.3. Giá trị và đánh đổi',2)
p('DT tạo khả năng kết hợp quan sát rời rạc với hiểu biết cơ chế, thử kịch bản trước khi can thiệp, phối hợp quyết định và truy vết kết quả. Giá trị chỉ được chứng minh khi tốt hơn quy trình hiện tại hoặc giải pháp đơn giản với chi phí hợp lý. Bất lợi gồm chất lượng cảm biến, khó quan sát sinh học dưới nước, sai lệch mô hình theo loài/mùa/trại, chi phí xử lý media, tích hợp và quyền dữ liệu. [S1, §5.12–5.18; S2, §5; S3, §5]')
h('2. Thuật ngữ và quy ước dữ liệu')
table(['Thuật ngữ','Diễn giải dùng trong dự án'],[
 ('Target entity / Instance / Template','Đối tượng được đại diện / một twin cụ thể / cấu trúc mẫu tái sử dụng. Mẫu dùng chung không làm các tham số sinh học tự động chuyển được.'),
 ('State / State projection','Trạng thái theo thời gian / cách dựng trạng thái hiện hành từ các sự kiện hợp lệ.'),
 ('Observed / Estimated','Giá trị đo, ghi nhận thực tế / giá trị suy ra từ dữ liệu và mô hình, có bất định.'),
 ('Predicted / Simulated / Desired','Dự báo tương lai / kết quả kịch bản giả định / trạng thái mục tiêu được quản lý quyền thực hiện.'),
 ('Event time / Ingestion time','Thời điểm hiện tượng xảy ra / thời điểm hệ thống nhận dữ liệu; phải lưu riêng.'),
 ('Freshness / Stale','Độ mới / dữ liệu đã quá cũ đối với mục đích cụ thể; giá trị cuối không mặc nhiên là trạng thái hiện tại.'),
 ('Schema / Ontology / Semantics','Cấu trúc dữ liệu / khái niệm và quan hệ / ý nghĩa gồm đại lượng, đơn vị, ngữ cảnh.'),
 ('Provenance / Digital thread','Nguồn gốc và các bước tạo kết quả / chuỗi liên kết dữ liệu xuyên suốt vòng đời.'),
 ('Data assimilation','Đồng hóa dữ liệu: dùng phép đo hiệu chỉnh trạng thái/tham số mô hình có xét sai số; khác việc ghi số đo vào cơ sở dữ liệu.'),
 ('Snapshot / Model Registry / ModelOps','Bộ đầu vào được chốt / danh mục phiên bản mô hình / quản lý phát hành, giám sát, thu hồi mô hình.'),
 ('VVUQ','Verification: kiểm tra triển khai đúng; Validation: phù hợp thực tế và mục đích; Uncertainty Quantification: lượng hóa bất định.'),
 ('Co-simulation / Federation','Phối hợp các mô hình có trao đổi đại lượng / liên kết các bên nhưng giữ quyền dữ liệu và vận hành.'),
 ('DO / Biomass / FCR','Oxy hòa tan / sinh khối / hệ số chuyển đổi thức ăn; phải nêu kỳ tính, biến động đàn và cách đo lượng thức ăn.'),
 ('Edge / Gateway / Interlock','Xử lý tại trại / cầu nối nguồn dữ liệu / điều kiện liên động tại bộ điều khiển.'),
 ('MAE / RMSE / TCO','Sai số tuyệt đối trung bình / căn sai số bình phương trung bình / tổng chi phí sở hữu.')])
p('Nguồn thuật ngữ: [S1, §3.4–3.6, §5.4, §5.8, §5.17; S2, §2; S3, §3]. Các diễn giải được chuẩn hóa cho báo cáo này.')
h('3. Kiến trúc hệ thống')
pic('kien_truc.png','Hình 1. Tổng hợp lại kiến trúc sáu lớp theo S1, §3.2 và §5.3; hình do báo cáo này dựng.')
p('S4 trình bày sáu nhóm theo cách khác, tách AI/analytics khỏi dịch vụ DT và gộp knowledge/data/governance. Đây là cách trình bày chiến lược, không nên đồng nhất số thứ tự lớp giữa hai tài liệu. Báo cáo lấy tên lớp S1 làm chuẩn vì có đặc tả kỹ thuật đi kèm. [S4, tr. PDF 5; S1, §3.2]')
h('3.1. Ranh giới chức năng và triển khai',2)
p('GDT sở hữu định danh chuẩn, State Service, Event Bus, Model Registry/Execution, Decision Authorization, Audit và Federation Gateway. AquaTwin sở hữu ontology thủy sản, adapter, mô hình chuyên ngành và workflow FarmOS. Sáu lớp là tổ chức logic; MVP có thể gộp chức năng để giảm vận hành. [S1, §5.17.2–5.17.3]')
table(['Khối đề xuất','Chức năng / nơi triển khai'],[
 ('Edge và adapter','Đọc thiết bị, gắn thời gian, kiểm tra sơ bộ, lưu đệm; bộ điều khiển địa phương giữ liên động.'),
 ('Chuẩn hóa và dòng sự kiện','Kiểm tra schema, đơn vị, định danh, trùng/lỗi; lưu sự kiện gốc và bản xử lý.'),
 ('Twin state / Eclipse Ditto','Quản lý Thing, thuộc tính, features, quyền và trạng thái gần nhất; bổ sung kiểm tra quan hệ và hợp đồng ngành.'),
 ('Kho lịch sử và media','Chuỗi thời gian cho số đo/đặc trưng; object storage cho video/audio; chỉ lưu tham chiếu trong twin.'),
 ('Các dịch vụ mô hình','Bất thường, dự báo, ước lượng, mô phỏng; chạy trên snapshot có phiên bản.'),
 ('FarmOS và dịch vụ quyết định','Giao diện, kịch bản, đề xuất, phê duyệt, điều phối và đối chiếu kết quả.')])
p('Ditto là middleware quản lý twin và kết nối, không mặc nhiên cung cấp mô hình sinh học, bộ dự báo hoặc tối ưu cho trại. Thing/Feature có thể chứa trạng thái; quan hệ domain cần quy ước và kiểm tra riêng. Lịch sử Ditto không thay thế cơ sở dữ liệu chuỗi thời gian. Twin channel cập nhật bản sao số; live channel chuyển thông điệp tới thiết bị/gateway. Desired state hoặc phản hồi nhận lệnh chưa chứng minh hành động đã hoàn tất. [D1]')
h('3.2. Đối tượng và quan hệ',2)
table(['Thực thể','Quan hệ và dữ liệu quan trọng'],[
 ('FarmSite → ProductionUnit','Trại chứa ao/lồng/RAS; có chủ quản, tọa độ và hồ sơ quyền.'),
 ('ProductionUnit ↔ StockCohort','Đơn vị nuôi chứa đàn theo khoảng thời gian; chuyển đàn/thu hoạch không sửa mất lịch sử.'),
 ('Sensor / Camera / Hydrophone','Quan sát đơn vị hoặc vùng/độ sâu; khai báo vị trí, thời gian, chất lượng, hiệu chuẩn.'),
 ('Feeder / Aerator / Pump','Phục vụ đơn vị nuôi; ghi trạng thái, lệnh, phản hồi, lượng cấp/điện nếu đo được.'),
 ('FeedBatch / FeedingEvent','Lô thức ăn → sự kiện cấp → đàn; phân biệt kế hoạch, lượng cấp và lượng ăn được ước lượng.'),
 ('ModelRun / Decision / Execution','Lần chạy dùng model version và snapshot; đề xuất liên kết phê duyệt, lệnh và kết quả.'),
 ('HarvestLot → ProductLot → Shipment','Duy trì nguồn gốc qua tách/gộp lô, chế biến và bàn giao; mở rộng sau MVP.')])
p('Cấu trúc dựa trên [S1, §5.4 và §5.17.4]. Nếu dùng Ditto cho MVP, ánh xạ Thing theo thực thể và Feature theo nhóm chức năng; không nhất thiết tạo một Thing mới cho mỗi phép đo.')
h('4. Xác định bài toán aquaculture')
h('4.1. Vấn đề nghiên cứu và nhu cầu quyết định',2)
p('Khó khăn trung tâm là trạng thái môi trường, sinh học và thiết bị phân tán, không quan sát đầy đủ và thay đổi theo thời gian. Cảnh báo theo ngưỡng chỉ phản ánh một phần; dữ liệu nước và hình ảnh cần được đặt trong quan hệ với đàn, vị trí và lịch vận hành. [S2, §1–3; S1, §5.6–5.7]')
table(['Bài toán','Đầu vào → đầu ra','Quyết định được hỗ trợ'],[
 ('P1. Tái hiện trạng thái','Số đo, danh mục, quan hệ → trạng thái có nguồn, thời gian, QC.','Đối tượng nào đang hoạt động, dữ liệu nào còn tin cậy?'),
 ('P2. Phát hiện bất thường','Chuỗi đo, thiết bị, media → sự kiện, mức độ, bằng chứng.','Kiểm tra cảm biến hay kiểm tra điều kiện nuôi?'),
 ('P3. Ước lượng và dự báo','Lịch sử, đàn, vận hành → sinh khối/chỉ số tương lai và bất định.','Cần chuẩn bị phản ứng khi nào?'),
 ('P4. Mô phỏng can thiệp','Trạng thái ban đầu, mô hình, hành động → quỹ đạo các phương án.','Thay lịch cho ăn hoặc thiết bị sẽ tác động thế nào?'),
 ('P5. Đề xuất và phản hồi','Kịch bản, chi phí, ràng buộc → phương án được duyệt và kiểm chứng.','Chọn phương án nào, ai chịu trách nhiệm, kết quả thực ra sao?')])
h('4.2. Chọn bài toán thí điểm theo hệ thống nuôi',2)
p('Đề xuất chọn một đơn vị nuôi và một quyết định, không xây toàn bộ chuỗi ngay. Ao/bể có đo oxy và thiết bị điều khiển phù hợp có thể thử oxy–sục khí; RAS cần xét bơm, tuần hoàn, lọc và oxy; lồng biển cần xét oxy theo không gian, dòng chảy và cho ăn. Nghiên cứu S2 về lồng biển cho thấy cần mô hình vận chuyển–tiêu thụ oxy; không nên thay thế bằng giả định “tăng sục khí toàn lồng” áp dụng từ ao. [S1, §5.6.1; S2, §4.1]')
p('Câu hỏi đề xuất: H1 — chuẩn hóa thời gian, nguồn và QC có giảm lỗi trạng thái không? H2 — kết hợp môi trường và vận hành có dự báo tốt hơn mô hình đơn giản không? H3 — mô hình cơ chế kết hợp dữ liệu có mô phỏng đáp ứng can thiệp trong phạm vi kiểm chứng không? H4 — khuyến nghị có làm giảm phơi nhiễm điều kiện bất lợi hoặc chi phí mà vẫn đáp ứng giới hạn không? Đây là giả thuyết cần thử nghiệm, chưa phải kết luận.')
h('4.3. Khảo sát dữ liệu bắt buộc',2)
bullets(['Xác định loài, giai đoạn, loại hình nuôi, số đơn vị, mật độ và các quy trình vận hành hiện có.',
 'Lập danh mục cảm biến/máy đo: đại lượng, đơn vị, vị trí/độ sâu, tần suất, lịch hiệu chuẩn, dữ liệu gốc và thời gian lưu.',
 'Đánh giá camera/âm học: góc nhìn, ánh sáng, độ đục, đồng hồ, chất lượng, video mẫu, nhãn và quyền sử dụng.',
 'Kiểm kê nhật ký thả/di chuyển/hao hụt, cân mẫu, thức ăn, thay nước, thiết bị, sự cố và hành động của người vận hành.',
 'Kiểm tra API/giao thức, quyền đọc/ghi, mạng/điện, khả năng phản hồi thực thi và người chịu trách nhiệm.'])
h('5. Phương pháp giải quyết đề xuất')
h('5.1. Đồng bộ và chất lượng dữ liệu',2)
p('Mỗi phép đo cần: eventId, sourceId, siteId, unitId/targetId, parameter, value, unit, phenomenonTime, receivedAt, qualityFlag và schemaVersion; bổ sung vị trí/độ sâu, calibrationRef, độ bất định khi phù hợp. Dữ liệu mô hình bổ sung modelVersion, inputSnapshotId, stateKind và thời hạn giá trị. [S1, §5.7, §5.17.6–5.17.7]')
table(['Tình huống','Xử lý đề xuất'],[
 ('Trùng sự kiện','Khóa theo nguồn + mã bản ghi; cùng khóa khác payload được báo xung đột.'),
 ('Dữ liệu đến muộn','Lưu lịch sử và correction; không âm thầm kéo trạng thái hiện tại về quá khứ.'),
 ('Thiếu hoặc sai phép đo','Gắn cờ, cách ly khi cần; dữ liệu nội suy phải được đánh dấu, không ghi thành quan sát thực.'),
 ('Quá hạn hiệu chuẩn / dữ liệu cũ','Hạ QC; vô hiệu quyết định phụ thuộc hoặc chuyển người vận hành theo chính sách.'),
 ('Mất mạng','Edge lưu đệm và phát lại; duy trì quy trình địa phương đã được phép.'),
 ('Video/audio khác tốc độ','Trích đặc trưng theo cửa sổ, lưu độ lệch thời gian và luồng bị thiếu; giữ liên kết media gốc.')])
h('5.2. Phát hiện bất thường',2)
p('Đề xuất triển khai ba tầng: (i) luật chất lượng như mất dữ liệu, đứng giá trị, bước nhảy, ảnh bị che; (ii) bất thường chuỗi thời gian so với quy luật giờ/ngày hoặc phần dư dự báo; (iii) bất thường đa nguồn như trạng thái thiết bị không phù hợp phản hồi đo. Bắt đầu bằng luật và thống kê dễ giải thích, sau đó so sánh mô hình học máy khi có dữ liệu đủ. [Đề xuất phát triển từ S1, §5.6 và §5.17.8]')
p('Đầu ra cảnh báo gồm đối tượng, khoảng thời gian, bằng chứng, QC, mức độ, độ tin cậy và bước kiểm tra tiếp. Phải tách nghi lỗi đo khỏi nghi sự cố môi trường. Sai số giữa mô hình và số đo chỉ là dấu hiệu; chưa đủ kết luận nguyên nhân hay chẩn đoán bệnh.')
h('5.3. Camera, âm học và ước lượng sinh khối',2)
p('Đề xuất pipeline: kiểm tra chất lượng hình ảnh → chọn đoạn hợp lệ → phát hiện/theo dõi khi khả thi → trích đặc trưng vận động, phân bố hoặc phản ứng ăn → tổng hợp theo cửa sổ → liên kết với đàn và môi trường. Chỉ số hoạt động cần nhãn để kiểm chứng trước khi diễn giải thành nhu cầu ăn. Camera đơn không mặc nhiên đo được kích thước tuyệt đối; cần hiệu chuẩn hình học/cấu hình đo phù hợp. [S2, §3.2; đề xuất kỹ thuật]')
p('Sinh khối có thể biểu diễn B̂(t) = N̂(t) × w̄̂(t). Sai số số lượng, hao hụt, lấy mẫu và ước lượng khối lượng phải được truyền tới khoảng bất định sinh khối. Cần đối chiếu cân mẫu độc lập và kết quả thu hoạch, không lấy chính đầu ra mô hình làm nhãn đúng. [S1, §5.8.1–5.8.2]')
h('5.4. Mô hình dự báo',2)
p('Đề xuất khởi đầu bằng persistence (giữ giá trị gần nhất), quy luật theo thời gian và hồi quy; sau đó thử mô hình cây tăng cường với đặc trưng trễ, hoặc mạng chuỗi thời gian nếu lượng dữ liệu phù hợp. Không lựa chọn mô hình phức tạp chỉ vì mới. Đầu vào gồm chỉ số nước, trạng thái thiết bị, vận hành và điều kiện ngoài có sẵn tại thời điểm dự báo.')
p('Chia tập theo thời gian, kiểm tra trên vụ/trại giữ riêng; fit bước chuẩn hóa và chọn đặc trưng chỉ trên tập huấn luyện. Tránh rò rỉ do cửa sổ video hoặc chuỗi đo chồng lấn. Đánh giá từng chân trời bằng MAE/RMSE, bias, độ bao phủ khoảng dự báo và khả năng cảnh báo vượt giới hạn. Chân trời cụ thể phải dựa vào thời gian phản ứng vận hành. [S1, §5.8.2, §5.13; đề xuất quy trình]')
h('5.5. Mô phỏng can thiệp và đồng hóa dữ liệu',2)
p('Mô hình đề xuất có dạng x(t+Δt) = f(x(t), u(t), w(t); θ) + ε. Trong đó x là trạng thái, u là hành động, w là điều kiện ngoài, θ là tham số hiệu chỉnh và ε phản ánh sai số. Mô hình dự báo quan sát chưa đủ chứng minh đáp ứng khi thay đổi u; cần mô hình tác động và dữ liệu can thiệp/kiểm chứng phù hợp.')
p('Với ao/RAS, có thể bắt đầu từ cân bằng oxy giản lược: biến thiên oxy = trao đổi/cấp oxy + nguồn sinh học − hô hấp vật nuôi − nhu cầu nền ± trao đổi nước; các hạng phải cùng đơn vị. Với lồng biển cần xét vận chuyển theo dòng chảy, khuếch tán, phân bố cá và điều kiện biên. Đây là cấu trúc nghiên cứu, chưa phải phương trình đã hiệu chỉnh cho địa điểm. [S2, §4.1; đề xuất tổng hợp]')
p('Hướng lai: dùng mô hình cơ chế cho phần có hiểu biết vật lý/sinh học, mô hình dữ liệu cho phần dư; cân nhắc bộ lọc trạng thái khi mô hình, cấu trúc quan sát và sai số phù hợp. S2, §4.1.5 đề xuất Ensemble Kalman Filter như một khả năng cho concept oxy; không xem đó là lựa chọn bắt buộc hoặc đã được xác nhận cho dự án.')
p('Mỗi kịch bản khởi chạy từ cùng snapshot; lưu scenarioId, phiên bản, tham số, hành động, điều kiện biên và bất định. So sánh phương án giữ nguyên với các phương án thay đổi. Kết quả chỉ ghi vào nhánh simulated. Các phương án ngoài miền đã kiểm chứng phải được đánh dấu, không sử dụng như bằng chứng tác động chắc chắn.')
h('5.6. Tối ưu và khuyến nghị',2)
p('Đề xuất bộ tối ưu tạo tập phương án khả thi theo điện, thức ăn, lao động và rủi ro môi trường, với giới hạn vận hành bắt buộc do trại xác lập. Có thể bắt đầu bằng duyệt một tập kịch bản nhỏ để dễ kiểm tra; chỉ tăng độ phức tạp khi lợi ích được chứng minh. Mọi phương án có lý do, snapshot, modelRunId, bất định và hạn hiệu lực. [S1, §5.8.3, §5.12.1, §5.17.10]')
p('Lệnh có commandId và vòng đời riêng: đề xuất → duyệt/từ chối → gửi → tiếp nhận → thực thi/xảy ra lỗi → xác minh. Thiết bị xác nhận tiếp nhận không đồng nghĩa đã hoàn tất. Khi dữ liệu không đủ hoặc quá cũ, chặn hành động liên quan và chuyển quy trình địa phương/người phụ trách.')
h('6. Luồng vận hành và kịch bản minh họa')
pic('luong_van_hanh.png','Hình 2. Luồng đề xuất dựa trên S1, §5.17.13 và §5.17.25; phản hồi phải được gắn với cùng quyết định.')
h('6.1. Kịch bản minh họa: oxy có nguy cơ giảm',2)
p('Bước 1: dữ liệu nước và thiết bị được tiếp nhận. Bước 2: kiểm tra cảm biến, độ mới và đơn vị; dựng trạng thái ao. Bước 3: chạy dự báo có khoảng bất định. Bước 4: nếu có nguy cơ theo giới hạn trại phê duyệt, so sánh giữ nguyên với thay đổi lịch thiết bị/cho ăn trong phạm vi đã kiểm chứng. Bước 5: hiển thị lý do và điều kiện; người vận hành duyệt. Bước 6: edge kiểm tra lại rồi gửi lệnh; thu phản hồi và số đo để đánh giá. Không suy luận rằng tăng oxy luôn làm tăng trưởng tốt hơn ở mọi điều kiện.')
h('6.2. Nhánh lỗi và xử lý',2)
table(['Trường hợp','Hành vi mong đợi'],[
 ('Cảm biến đứng giá trị','Tách cảnh báo lỗi đo; không coi chuỗi ổn định là môi trường an toàn.'),
 ('Dữ liệu tới muộn sau khi dự báo','Giữ snapshot đã dùng, ghi correction; đánh giá lại hiệu lực đề xuất nếu cần.'),
 ('Camera không quan sát được','Đánh dấu đặc trưng thiếu; mô hình thay thế chỉ được dùng nếu đã kiểm chứng.'),
 ('Không có phê duyệt / đề xuất hết hạn','Không thực thi; ghi rõ trạng thái.'),
 ('Thiết bị không xác nhận thực thi','Không cập nhật thành hoàn tất; thông báo và thực hiện quy trình xử lý sự cố.'),
 ('Mất cloud hoặc mô hình suy giảm','Giữ điều khiển/bảo vệ tại trại; ngừng khuyến nghị phụ thuộc và phục hồi có đối chiếu.')])
h('7. Thiết kế kiểm chứng và chỉ số đánh giá')
p('Theo S1, §5.13, cần so sánh A — vận hành hiện tại; B — giám sát có cảm biến; C — hỗ trợ dự báo; D — tối ưu phối hợp. Các nhóm phải nêu khác biệt về dữ liệu và thiết bị; không gán toàn bộ cải thiện từ B sang C/D cho DT nếu điều kiện nuôi cũng thay đổi.')
table(['Nhóm','Chỉ số / bằng chứng'],[
 ('Dữ liệu và đồng bộ','Uptime, bias đo, thiếu/trùng, độ trễ p50/p95/p99, trạng thái cũ; thử dữ liệu sai, đổi đơn vị, phát lại.'),
 ('Bất thường','Precision, recall theo sự kiện, số cảnh báo giả/đơn vị/ngày, thời gian báo sớm; nhãn do người có chuyên môn xác nhận.'),
 ('Dự báo','MAE/RMSE/bias theo chân trời, độ bao phủ và độ rộng khoảng dự báo; đối chứng đơn giản; tập thời gian/địa điểm giữ riêng.'),
 ('Mô phỏng','So phản ứng dự báo và quan sát sau can thiệp; kiểm tra cân bằng, độ nhạy tham số và miền giá trị.'),
 ('Quyết định','Tính khả thi, vi phạm giới hạn, tỷ lệ duyệt/thực hiện, dữ liệu đầu vào đủ mới, truy vết kết quả.'),
 ('Kinh tế và sinh học','FCR, tăng trưởng, sống/hao hụt, giờ phơi nhiễm ngoài giới hạn, điện/chi phí và TCO; nêu sai số đo và biến động đàn.'),
 ('Khả năng mở rộng','Công sức tích hợp/hiệu chỉnh trại thứ hai, lỗi ngữ nghĩa, quyền dữ liệu và phục hồi mạng.')])
p('Đề xuất tiền đăng ký mục tiêu chính và mức cải thiện tối thiểu có ích sau khảo sát baseline; lặp thử nghiệm và báo khoảng tin cậy. Khi không ngẫu nhiên hóa được, dùng thời kỳ/đơn vị đối sánh và phân tích độ nhạy; vẫn nêu giới hạn suy luận nhân quả. Kiểm chứng ngoài trại/mùa huấn luyện là điều kiện cho tuyên bố chuyển giao. [S1, §5.13.1]')
p('Thang E0–E4 của S1, §2.2.2 mô tả bằng chứng: E0 chưa xác minh; E1 đặc tả/API; E2 triển khai/demo tái lập; E3 so sánh độc lập; E4 thực địa có kết quả và đối chứng. Bài review, sơ đồ kiến trúc hoặc API mẫu không tự tạo bằng chứng E4 cho sản phẩm. Mức bằng chứng cần gắn từng tuyên bố.')
h('8. Lộ trình triển khai và đầu ra')
table(['Giai đoạn','Sản phẩm bàn giao','Điều kiện chuyển bước'],[
 ('P0 — Khảo sát','Inventory nguồn/thiết bị; mục tiêu, đối tượng, quyền, baseline và người phụ trách.','Có dữ liệu mẫu và phạm vi thí điểm thống nhất.'),
 ('P1 — Observation DT','Ontology/schema; adapter; state; lịch sử; dashboard; replay; edge buffering.','Đúng nguồn, đơn vị, thời gian; không mất/trùng âm thầm; qua thử lỗi.'),
 ('P2 — Model-based DT','Mô hình đối chứng/dự báo; registry; snapshot; bất định; mô hình mô phỏng giới hạn.','Báo cáo VVUQ độc lập; miền sử dụng được chấp nhận.'),
 ('P3 — Decision support','Kịch bản; đề xuất; duyệt; nhật ký lệnh; phản hồi và đối chiếu.','Qua kiểm thử thiếu quyền/dữ liệu cũ; có chủ sở hữu quyết định.'),
 ('P4 — Integrated FarmOS','Phối hợp nước, sinh học, thiết bị, vận hành; sổ chi phí.','Có kết quả đo và phân tích lợi ích–chi phí.'),
 ('P5 — Mở rộng','Trại/loài tiếp theo; chuỗi đầu vào/thu hoạch; federation.','Tái kiểm chứng, đo công sức chuyển giao và quyền chia sẻ.')])
p('Lộ trình được chuyển thể từ S1, §5.16. Chưa gán số tuần vì chưa biết quy mô nguồn dữ liệu, thời gian mùa vụ và quyền truy cập. Các mốc 2026–2030 trong S4 là kịch bản chiến lược, không phải cam kết tiến độ dự án.')
h('9. Giới hạn và quyết định cần chốt')
p('Chưa có dữ liệu thực tế để xác nhận mức độ đầy đủ, tỷ lệ lỗi, năng lực camera, mô hình tốt nhất hay hiệu quả kinh tế. Các thử nghiệm trong báo cáo là kế hoạch đề xuất; chưa chạy huấn luyện, mô phỏng thực địa hoặc điều khiển thiết bị. Các mốc dự án trong S1, §5.11 là thông tin được dự án báo cáo, không được chuyển thành kết quả kiểm chứng độc lập.')
bullets(['Chọn ao, RAS hay lồng biển; loài và giai đoạn; xác định đơn vị thí điểm.',
 'Chọn quyết định chính: giám sát/cảnh báo, cho ăn, sục khí hay vận hành tuần hoàn.',
 'Xác nhận dữ liệu đo, lịch sử can thiệp, nhãn video và bộ đo độc lập để đánh giá.',
 'Chốt miền hiệu lực mô hình, ngưỡng do chuyên gia trại phê duyệt và cơ chế phản hồi thiết bị.',
 'Chốt hạ tầng tại trại/cloud, lưu media, quyền chia sẻ và chi phí sở hữu.',
 'Chốt baseline, tiêu chí nghiệm thu, người chịu trách nhiệm dữ liệu, mô hình và quyết định.'])
h('10. Nguồn và đối chiếu ghi chú')
p('Số trang dưới đây là thứ tự trang PDF, bắt đầu từ 1. Đối với S1, ưu tiên tra theo số mục vì tài liệu có một số tham chiếu chéo bị lỗi. Các nguồn được diễn giải, không sao chép nguyên văn dài.')
table(['Mã','Tài liệu / vị trí sử dụng'],[
 ('N1','Pasted text.txt do người dùng cung cấp. Tổng hợp nhu cầu, ghi chú chương 2/3/5 và câu hỏi nghiên cứu.'),
 ('S1','Digital Twin Platform Design (EN).pdf; đối chiếu bản DOCX cùng tên. Chương 2: bằng chứng; chương 3: kiến trúc; chương 5: AquaTwin/FarmOS, đặc biệt §5.3–5.8, §5.12–5.17; tr. PDF 121–145 cho nội dung chính chương 5.'),
 ('S2','Føre, M. và cộng sự (2024). Digital Twins in intensive aquaculture — Challenges, opportunities and future prospects. Computers and Electronics in Agriculture 218, 108676. DOI: 10.1016/j.compag.2024.108676. Tr. 4–6: thành phần/mức năng lực; 11–13: oxy và tăng trưởng; 14–15: robotics; 16–17: giới hạn/định hướng.'),
 ('S3','Iranshahi, K., Brun, J., Arnold, T., Sergi, T. và Müller, U.C. (2025). Digital twins: Recent advances and future directions in engineering fields. Intelligent Systems with Applications 26, 200516. DOI: 10.1016/j.iswa.2025.200516. Tr. 1–3: khái niệm; tr. 10–11: giới hạn, digital thread và triển khai.'),
 ('S4','VinUni_GREEN-X_Digital_Twin_Ecosystem.pdf. Tr. PDF 2, 5–6, 15–20: nền tảng dùng chung, AquaTwin, federation, validation, lộ trình. Một số slide là hình; ưu tiên diễn giải nội dung chữ có thể đối chiếu.'),
 ('D1','Tài liệu Eclipse Ditto chính thức đã đối chiếu trong trao đổi dự án: https://eclipse.dev/ditto/ ; basic-thing.html ; basic-feature.html ; basic-history.html ; protocol-twinlive.html. Vai trò: tham khảo triển khai; cần khóa phiên bản khi làm thử nghiệm.')])
h('10.1. Các điểm ghi chú đã được chuẩn hóa',2)
table(['Ghi chú ban đầu / khả năng hiểu nhầm','Cách diễn đạt trong bản tổng hợp'],[
 ('Một twin là một thuộc tính.','Một twin là biểu diễn theo mục đích, gồm trạng thái, quan hệ, mô hình; thuộc tính là thành phần của biểu diễn.'),
 ('Tăng oxy thì dự báo cá phát triển tốt hơn.','Đó là giả thuyết can thiệp; phải có mô hình và kiểm chứng theo loài/địa điểm, không khẳng định quan hệ đơn điệu.'),
 ('Phân chia tác vụ để chúng không ảnh hưởng nhau.','Tách trách nhiệm và giao diện để bảo trì, nhưng các mô hình vẫn có phụ thuộc và cần phối hợp.'),
 ('Dự báo tốt có thể dùng để mô phỏng thay đổi vận hành.','Chất lượng dự báo quan sát và chất lượng dự đoán can thiệp cần đánh giá riêng.'),
 ('Chỉ số lợi ích là vốn/lãi dự kiến.','Đánh giá lợi ích so đối chứng và TCO thực tế, có bất định và kiểm soát yếu tố mùa vụ.'),
 ('Mô hình ảo giác / một cấu hình dùng mọi nơi.','Dùng thuật ngữ sai lệch, suy giảm hoặc ngoài miền; cấu hình phải được tái kiểm chứng theo trại/loài.')])
h('10.2. Kết quả nghiên cứu cần bàn giao',2)
p('Bộ tài liệu yêu cầu và ontology; hợp đồng dữ liệu có phiên bản; cấu hình twin/adapter; dữ liệu thí nghiệm được phép sử dụng; baseline và mô hình có model card; báo cáo VVUQ; bộ kịch bản; luồng phê duyệt–phản hồi; mã kiểm thử/replay; báo cáo vận hành và lợi ích–chi phí. Đây là các đầu ra có thể kiểm tra được để chuyển từ ý tưởng DT sang hệ thống nghiên cứu ứng dụng.')

path=OUT/'Tong_hop_Digital_Twin_Aquaculture.docx'
doc.save(path)
print(path)
print('Paragraphs:',len(doc.paragraphs),'Tables:',len(doc.tables),'Inline figures:',len(doc.inline_shapes))
