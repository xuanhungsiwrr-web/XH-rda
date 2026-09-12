# Hồ sơ văn phong — Nam Quốc

**Đo ngày:** 21/08/2026 · **Nguồn:** 4 báo cáo đã được phê duyệt · **3.214 câu · 2.283 đoạn văn xuôi**
**Cách đo:** `mine-style.py` + `do-muc-h.py`, thống kê tất định, không dùng AI. Con số không thể bịa.

> Đây là file **duy nhất** về văn phong được nạp vào ngữ cảnh mỗi lần viết.
> Khi viết một đề mục: nạp Mục A–G (cố định) + **đúng một dòng** của Mục H + **đúng một** exemplar.
> Không nạp cả kho exemplar — vừa tốn token vừa làm loãng tín hiệu.

---

## A. Danh tính người viết

| | |
|---|---|
| Người viết | Đơn vị tư vấn thiết kế — Công ty Cổ phần Tư vấn và Đầu tư Nam Quốc |
| Xưng hô trong văn | **"Đơn vị tư vấn"** (9 lần) · "Tư vấn thiết kế" (3 lần) |
| Không dùng | **"Chúng tôi"** — chỉ xuất hiện 1 lần trong toàn bộ 4 báo cáo, coi như không dùng |
| Người đọc | Hội đồng thẩm định, Sở NN&PTNT / Sở Xây dựng, chủ đầu tư — người sẽ chất vấn từng con số |
| Thái độ | Trình bày để được duyệt, không phải để thuyết phục bằng cảm xúc |

---

## B. Chỉ số định lượng — ngưỡng đỏ

| Chỉ số | Đo được | Ràng buộc khi viết |
|---|---|---|
| Độ dài câu trung bình | **20,4 từ** (trung vị 15) | viết câu **8–35 từ**; câu trên 43 từ là ngoại lệ |
| Câu dài hơn 40 từ | 11,9% | không vượt 12% |
| Số câu mỗi đoạn | **1,4** (trung vị **1**) | xem cảnh báo dưới |
| Đoạn dưới 3 câu | **92,8%** | **bình thường — không phải lỗi** |
| Tỉ lệ bullet toàn báo cáo | **19,5%** | không vượt 20%; theo từng nhóm xem Mục H |
| Câu bị động (*được / bị*) | 15,6% | không vượt 18% |

### Cảnh báo quan trọng — đừng ép đoạn dài

Gần **93% đoạn trong báo cáo đã duyệt chỉ có 1–2 câu**, trung vị đúng **một câu**. Đây không phải viết hời hợt mà là đặc trưng của hồ sơ tư vấn: mỗi đoạn nêu một thông số, một kết cấu, một căn cứ.

**Sai lầm đã mắc một lần:** từng đặt luật "đoạn phân tích tối thiểu 3 câu". Luật đó trái với chính kho báo cáo đã được thẩm định. Đã bỏ.

Đoạn 3 câu trở lên **chỉ dùng ở nhóm "Sự cần thiết đầu tư"** (2,06 câu/đoạn, 56 từ/đoạn — dài gấp đôi mọi nhóm khác), nơi phải lập luận chứ không chỉ liệt kê thông số.

---

## C. Quy ước số và đơn vị

| Quy ước | Đúng | Sai |
|---|---|---|
| Dấu thập phân | **phẩy** — `4,50` (224 lần dùng phẩy / 26 lần dùng chấm) | `4.50` |
| Dấu hàng nghìn | **chấm** — `1.875` | `1,875` · `1875` |
| Khoảng trắng trước đơn vị | **không có** — `188m`, `-0,50m`, `12cm` (447 dính / 156 rời) | `188 m` |
| Cao trình | luôn kèm dấu — `+1,30m`, `-0,50m` | `1,30m` |
| Nhiệt độ | `27,8°C` | `27.8oC` · `27,8 oC` |
| Đơn vị hay dùng | `m` (360) · `%` (88) · `cm` (62) · `mm` (44) · `km` (25) · `ha` (21) | |
| Diện tích | `m²` chữ số trên | `m2` |
| Hệ quy chiếu | nêu rõ khi lần đầu xuất hiện — `+4,50m (hệ VN2000)` | bỏ trống |

Con số trong bản thảo **không bao giờ gõ trực tiếp** — viết `{{fact:ten_chi_tieu}}`, script thay số khi render. Con số chỉ tồn tại ở `_facts.yaml`.

---

## D. Cấu trúc đoạn điển hình

Trật tự bốn nhịp, dùng cho mọi đoạn có số liệu:

```
NGUỒN  →  SỐ  →  SO SÁNH VỚI TRỊ CHO PHÉP  →  Ý NGHĨA THIẾT KẾ
```

> *Theo kết quả khảo sát địa hình tháng 3/2025 tỉ lệ 1/500, cao trình tự nhiên bờ kênh
> biến thiên từ +0,60m đến +1,10m, thấp hơn mực nước thiết kế P=2% là {{fact:muc_nuoc_thiet_ke_p2}},
> nên toàn tuyến phải đắp tôn cao trước khi thi công kết cấu kè.*

Bốn nhịp trong một câu 45 từ — dài hơn trung bình, nhưng đây là kiểu câu được phép dài.

**Đoạn mô tả thuần** (chiếm đa số) thì ngắn hơn nhiều, một câu là đủ:

> *Bản chắn đất bằng bê tông cốt thép M300, dày 12cm, đặt trên nền cọc tràm.*

---

## E. Cách mở đoạn — theo thứ tự ưu tiên

Đo trên 2.283 đoạn:

| Kiểu mở đoạn | Số lần | Khi nào dùng |
|---|---|---|
| Bằng **chủ thể** (tên hạng mục, tên kết cấu) | 2.001 | mặc định — *"Bản chắn đất bằng…"*, *"Mái kè được gia cố…"* |
| Bằng **số** | 90 | khi con số là điểm chính của đoạn |
| Bằng **nguồn / căn cứ** | 69 | *"Theo kết quả khảo sát…"*, *"Căn cứ Quyết định số…"* |
| Bằng **liên từ** | 61 | nối tiếp ý đoạn trước — dùng thưa |
| Bằng **kết quả tính toán** | 42 | *"Kết quả tính toán cho thấy…"* |

**Câu định tính được phép mở đoạn** — nhưng câu ngay sau phải có số. Ví dụ nằm trong báo cáo đã duyệt: *"Địa hình khu vực tương đối bằng phẳng."* + câu tiếp theo nêu dải cao độ. Từng bị coi nhầm là lỗi.

---

## F. Ngân hàng cụm từ — dùng lại được

Rút từ 4 báo cáo, **đã lọc bỏ địa danh và tên dự án** để không rò sang hồ sơ khác.

**Chuyển ý và dẫn dắt**
`trên cơ sở` · `theo kết quả` · `căn cứ vào` · `trong quá trình` · `phù hợp với` · `sau khi hoàn thành` · `tác động của` · `ảnh hưởng đến`

**Thuật ngữ hạng mục** (dùng đúng dạng này, không biến thể)
`mặt cắt ngang điển hình` · `cao trình đỉnh` · `vải địa kỹ thuật` · `cấp công trình` · `đường tần suất` · `lượng bốc hơi` · `lượng mưa trung bình` · `bản đồ vị trí` · `khu vực dự án` · `biện pháp thi công` · `an toàn lao động` · `quản lý vận hành` · `phòng chống sạt lở` · `tổng mức đầu tư` · `biến đổi khí hậu`

**Dẫn văn bản** — bốn dạng, theo tần suất thật:

| Dạng | Số lần | Mẫu |
|---|---|---|
| `Căn cứ + <văn bản>` | 22 | *Căn cứ Nghị định số 06/2021/NĐ-CP ngày … của Chính phủ…* |
| `Theo + <văn bản>` | 19 | *Theo TCVN 9844:2013,…* |
| Nguồn đặt dưới bảng | 12 | *Nguồn: Đài Khí tượng Thủy văn tỉnh …* |
| `Tuân thủ + <văn bản>` | 4 | |

Dạng đầy đủ của văn bản: **`<Loại> số <số hiệu> ngày <ngày> của <cơ quan ban hành>`** — không rút gọn ở lần nhắc đầu tiên.

---

## G. Danh sách cấm — kèm cột thay bằng

| Không viết | Thay bằng | Lý do |
|---|---|---|
| "chúng tôi" | "đơn vị tư vấn" | 1 lần / 4 báo cáo — không phải giọng của hồ sơ |
| "tối ưu nhất", "vô cùng", "ấn tượng" | bỏ hẳn, hoặc thay bằng trị số | 4 lần lọt vào kho — đều là lỗi, không phải chuẩn |
| "rất tốt", "thuận lợi", "hiệu quả cao" | nêu trị số và trị số cho phép | tính từ cảm tính không chịu được chất vấn |
| "khoảng" + số lẻ đến hàng đơn vị | chọn một: hoặc "khoảng 2.400", hoặc "2.404 (nguồn…)" | *"gần 2.404 học sinh"* — mâu thuẫn về mức chắc chắn |
| "đây là", "bao gồm:" + bullet | mở bằng chủ thể; liệt kê bằng câu hoặc bảng | thói quen của AI, không có trong kho |
| dấu `…` hay `.../` cho chỗ trống | `{{TODO: nội dung cần bổ sung}}` | bản đã nộp từng để lọt *"Công văn số …../UBND-NNXD"* |
| ký tự `÷` font Symbol (U+F0B8) | ký tự Unicode `÷` (U+00F7) hoặc chữ "đến" | mất khi trích PDF, hiện thành số vô nghĩa |

**Từ ràm rà — dùng có kiểm soát:** `khoảng` (121 lần), `có thể` (51), `tương đối` (24), `dự kiến` (22), `cơ bản` (19). Chúng có trong kho nên không cấm, nhưng mỗi lần dùng phải tự hỏi: *đã có số chưa?* Nếu có số thì bỏ từ ràm rà đi.

---

## H. Khác biệt giọng theo nhóm đề mục — **đo thật, không suy đoán**

Một hồ sơ văn phong duy nhất cho cả báo cáo là không đủ. Số dưới đây đo trên 229 đề mục của 4 báo cáo đã duyệt:

| Nhóm đề mục | Số mục | Bullet | Câu/đoạn | Từ/đoạn | Đặc điểm |
|---|---|---|---|---|---|
| **Sự cần thiết đầu tư** | 19 | 13,2% | 2,06 | **56** | đoạn dài gấp đôi mọi nhóm — lập luận, được nêu hệ quả xã hội nhưng vẫn phải có số |
| **Căn cứ pháp lý** | 30 | **1,8%** | 1,11 | 24 | mỗi căn cứ **một đoạn riêng**, mở bằng "Căn cứ" — **không dùng bullet** |
| **Điều kiện tự nhiên** | 30 | 2,1% | 1,87 | 24 | mô tả có phân tích; luôn dẫn nguồn + thời điểm + tỉ lệ khảo sát |
| **Giải pháp kỹ thuật** | 115 | 10,2% | 1,22 | **21** | khô, đặc số liệu, đoạn ngắn nhất trong phần nội dung |
| **So sánh phương án** | 10 | **0%** | 1,30 | 25 | dùng **bảng**, không bullet; kết luận phải khớp chương thiết kế |
| **Kết luận – kiến nghị** | 25 | 3,7% | 1,26 | **12** | ngắn, dứt khoát; **không đưa số mới** chưa có ở chương trước |

**Phát hiện đáng chú ý:** "Căn cứ pháp lý" chỉ 1,8% bullet — trái hẳn với giả định thông thường rằng mục này là danh sách gạch đầu dòng. Trong hồ sơ thật, mỗi căn cứ là một đoạn văn hoàn chỉnh. Nếu không đo thì đã viết sai.

---

## I. Exemplar

| Nhóm | File exemplar | Trạng thái |
|---|---|---|
| tất cả 6 nhóm | `50-Spec-Exemplar/BCKTKT/exemplars-BCKTKT.md` (33 đoạn) | ✅ có, chưa gắn nhãn theo 6 nhóm Mục H |

Việc còn lại: gắn mỗi exemplar vào đúng một nhóm ở Mục H, và viết kèm 3–5 dòng **ghi chú giải thích vì sao đoạn này tốt** — điều biến một *ví dụ* thành một *bài học*.

---

## J. Nhật ký và chỉ số theo dõi

| Ngày | Thay đổi |
|---|---|
| 21/08/2026 | Dựng lần đầu. Đo trên 4 báo cáo đã duyệt (3.214 câu). Mục H đo thật theo 229 đề mục. |
| 25/08/2026 | Thêm **Mục K** — danh sách cấm nhập từ `engineering-writing-master` (plugin v2). Đánh dấu chưa kiểm chứng trên kho, chờ `mine-style.py` xác nhận. |

**Chỉ số theo dõi: tỉ lệ câu giữ nguyên** sau khi anh sửa bản thảo — đo bằng `learn-from-edits.py`.

```
BC #1: ~40%   →   BC #3: ~65%   →   BC #5: ~80%
```

Chưa có số lần nào — cần lưu song song `*_claude.md` và `*_dasua.md` vào `60-VanPhong/lich-su-sua/`.

Nếu sau 3 báo cáo mà tỉ lệ không tăng: hồ sơ này đang ghi sai thứ. Xem lại chứ đừng viết thêm quy tắc.


---

## K. Danh sách cấm **nhập từ ngoài** — chưa đo trên kho Nam Quốc

> **Xuất xứ:** skill `engineering-writing-master` của plugin `xh-tuvan-v2`, nhập ngày 25/08/2026.
> **Trạng thái: CHƯA KIỂM CHỨNG.** Mục G ở trên rút từ 4 báo cáo đã duyệt (3.214 câu) — đó là dữ liệu. Mục K này là **quy tắc do người khác đặt ra**, chưa đếm trên kho. Áp dụng được, nhưng khi mâu thuẫn với Mục G thì **Mục G thắng** — đã sai một lần vì cho "địa hình tương đối bằng phẳng" là lỗi, hoá ra nó nằm trong báo cáo đã phê duyệt.
> **Việc cần làm để nâng Mục K lên ngang Mục G:** chạy `mine-style.py` đếm tần suất từng cụm dưới đây trong 4 báo cáo đã duyệt. Cụm nào xuất hiện ≥ 3 lần thì **gỡ khỏi danh sách cấm** và chuyển sang Mục F.

**a) Cụm sáo rỗng — cắt bỏ, không thay thế**

`đóng vai trò then chốt` · `đóng vai trò quan trọng` · `bức tranh toàn cảnh` · `minh chứng rõ nét` · `như chúng ta đã biết` · `tóm lại là` · `không thể phủ nhận rằng` · `đáng chú ý là`

Cách sửa: xoá cụm, giữ lại mệnh đề mang thông tin. *"Tuyến kè đóng vai trò then chốt trong việc bảo vệ 25 hộ dân"* → *"Tuyến kè bảo vệ 25 hộ dân"*.

**b) Cấu trúc tương phản nhị nguyên giả tạo**

`Không chỉ … mà còn …` · `Dù … nhưng vẫn …` · `Vừa … vừa …` khi hai vế không thực sự đối lập.

Cách sửa: tách thành hai câu, mỗi câu một mệnh đề có số.

**c) Nhận xét định tính không kèm số — quy tắc chuyển hoá**

Đây là mục quan trọng nhất của Mục K, và nó **trùng hướng với Mục G** nên độ tin cậy cao hơn phần a/b.

| Viết như thế này | Là vì thiếu | Viết thành |
|---|---|---|
| *"tình trạng sạt lở diễn ra hết sức nghiêm trọng"* | lý trình, kích thước, đối tượng bị đe doạ | *"đoạn bờ kênh từ K0+000 đến K0+350 sạt lở đứng mép bờ 3,0–5,5m, đe doạ trực tiếp 25 hộ dân và tuyến đường liên ấp"* |
| *"địa chất khu vực rất yếu"* | chỉ tiêu cơ lý, chiều sâu lớp | *"lớp 1 là bùn sét chảy dày 8,5–12,0m, cường độ kháng cắt không thoát nước Su = 8–14 kPa"* |
| *"giao thông đi lại khó khăn"* | hiện trạng đo được | *"mặt đường rộng 2,5m, kết cấu đất, ngập 0,3–0,5m khi triều cường vượt +1,80m"* |

**Ngoại lệ đã xác nhận:** câu định tính **được phép mở đoạn** nếu câu ngay sau có số. Xem Mục E. Đây là cách viết có thật trong báo cáo đã duyệt, không phải lỗi.

---

## Giới hạn của bản đo này

- **File PDF chưa được quét.** `01_TM BAO CAO NCKT.pdf` (4,7MB) nằm ngoài 4 file đã đo — `mine-style.py` cần thêm bước bóc text PDF.
- **4 báo cáo là mẫu đủ cho chỉ số toàn cục, hơi mỏng cho Mục H** ở hai nhóm "So sánh phương án" (10 mục) và "Sự cần thiết đầu tư" (19 mục). Thêm 2–3 báo cáo nữa thì hai dòng đó chắc hơn.
- **Chưa lọc theo người viết.** Nếu trong 4 báo cáo có phần do đồng nghiệp hoặc thầu phụ viết thì chỉ số bị pha. Anh xác nhận giúp: cả 4 có phải đều do anh viết không?

---

## L. Vai người viết — rút từ bản sửa v2 ngày 26/08/2026

Nguồn: `CauSongDoc_NCKT_BaoCaoChinh_v2_DaSua.docx` — 232 đoạn chèn, 249 đoạn xoá, 20 nhận xét
của anh Hưng. Đây là nhóm lỗi anh gọi là **"lệch vai"**: AI viết như trợ lý đưa bản nháp cho sếp
xem, thay vì như đơn vị tư vấn nộp hồ sơ cho Cơ quan thẩm định.

Mục này ưu tiên cao hơn Mục G khi hai bên va nhau.

### L1. Không viết về chính bản báo cáo

Nhận xét: *"Sai vai trò của người viết báo cáo."*

Thuyết minh trình bày CÔNG TRÌNH, không tự bình luận về bố cục, phạm vi hay chủ ý của chính nó.
Người đọc là cơ quan thẩm định, không cần được hướng dẫn cách đọc.

| Đã bị xoá | Vì sao |
|---|---|
| "Báo cáo nghiên cứu khả thi giữ nguyên mục tiêu này, không đề xuất bổ sung hay điều chỉnh." | tự bình luận về hồ sơ |
| "Nhiệm vụ này được thực hiện tại Chương IV và Chương V của báo cáo, trọng tâm là..." | hướng dẫn cách đọc |
| "Dự án là bước cụ thể hóa quy hoạch chi tiết thành dự án đầu tư xây dựng, không đề xuất nội dung nằm ngoài quy hoạch được duyệt." | tự khai phạm vi |
| "Mục tiêu trên bao gồm ba nội dung gắn với nhau theo quan hệ nhân quả..." | giảng giải cấu trúc |

Bỏ mọi câu mở bằng *"Báo cáo này..."*, *"Nội dung này được trình bày tại..."*, *"Mục tiêu trên bao gồm..."*.

### L2. Không kể lại quá trình làm hồ sơ

Nhận xét: *"Văn phong sai."*

Bị xoá nguyên đoạn: *"Thực hiện yêu cầu nêu trên, Chủ đầu tư đã tổ chức khảo sát, thu thập tài
liệu và lập Báo cáo nghiên cứu khả thi dự án. Đơn vị tư vấn lập báo cáo là Công ty... Hồ sơ mang
mã số... gồm Tập I Thuyết minh, Tập II Phụ lục tính toán và Tập III Bản vẽ thiết kế cơ sở."*

Không tự giới thiệu đơn vị tư vấn, không liệt kê cấu tạo bộ hồ sơ. Đã có ở bìa và khung tên bản vẽ.

### L3. Không giải trình nguồn số liệu trong thân báo cáo

Nhận xét: *"Số liệu lấy chỉ là ngầm hiểu, không được đưa vào báo cáo"*

Bị xoá: *"Số liệu điều kiện tự nhiên trình bày trong chương này được tổng hợp từ ba nguồn...
Các số liệu kế thừa từ công trình lân cận đều được ghi rõ nguồn tại từng vị trí sử dụng."*

**Điều chỉnh quan trọng đối với Nguyên tắc 1 và 6.** Quy ước "số mượn phải ghi rõ nguồn + khuyến
cáo khảo sát bổ sung" vẫn đúng — nhưng nó sống **trong `_facts.yaml`**, không phải viết ra thành
đoạn văn trong thuyết minh. Thuyết minh chỉ NÊU số. Khuyến cáo khảo sát bổ sung thì chuyển thành
**Kiến nghị ở chương cuối**, không rải trong thân bài.

### L4. Không nêu tình trạng chưa hoàn thành, không viết câu phòng thủ

Bị xoá: *"Kết quả tính toán tổng mức đầu tư tại Chương VIII nằm trong trần này. Trường hợp trong
bước thiết kế bản vẽ thi công, kết quả khảo sát địa chất bổ sung dẫn đến phải điều chỉnh..."*

Hai lỗi trong một: viện dẫn kết quả tính toán **không tồn tại** trong hồ sơ, và viết câu phòng
thủ kiểu *"nếu sau này phát sinh thì sẽ..."*.

### L5. Giai đoạn hồ sơ

Nhận xét: *"Sai. Giai đoạn này không còn Để quyết định đầu tư nữa."*

Ở bước NCKT của dự án **đã có chủ trương đầu tư được duyệt**, không viết mục đích hồ sơ là
"để cấp có thẩm quyền xem xét quyết định đầu tư". Chủ trương đã quyết rồi.

### L6. Bố cục — tách thông tin chính khỏi bảng chỉ tiêu kỹ thuật

Nhận xét: *"Sai văn phong. Đây là những thông tin chính của dự án. Phải để riêng, không để trong
bảng tổng hợp chỉ tiêu kinh tế kỹ thuật."*

**Khối A — danh mục riêng, không phải bảng:** Nhóm dự án · Loại, cấp công trình · Tổng mức đầu tư
· Nguồn vốn · Thời gian thực hiện.

**Khối B — bảng "Tổng hợp chỉ tiêu kinh tế - kỹ thuật của dự án", chỉ chỉ tiêu kỹ thuật:**
Tần suất thiết kế · Mực nước thiết kế · Chiều dài cầu · Cao độ tim mặt cầu ...

Tổng mức đầu tư phải kèm số tiền bằng chữ: *"123.339.000.000 đồng (Một trăm hai mươi ba tỷ ba
trăm ba mươi chín triệu đồng)"*.

### L7. Không đưa chi tiết công tác khảo sát vào thuyết minh

Nhận xét: *"Không cần thiết trong báo cáo đi khảo sát địa hình đã có."* · *"Trong báo cáo, không
đưa chi tiết như thế này"*

Bị xoá: thành phần khảo sát (bình đồ 1/1.000, trắc dọc, trắc ngang), lưới khống chế (05 mốc đường
chuyền cấp 2, hai mốc thuỷ chuẩn hạng IV, sai số khép Wh = -5,00mm).

Nêu **KẾT QUẢ** khảo sát — địa hình thế nào, địa tầng ra sao. Không nêu quy trình và thông số của
bản thân công tác khảo sát.

### L8. Căn cứ pháp lý — chỉ văn bản pháp lý của chính dự án

Nhận xét: *"sai. Dự án mới thì báo cáo địa hình phải khảo sát mới. Báo cáo khảo sát địa hình dự án
cũ chỉ là tham khảo, không nên đưa vào đây."* · *"Không cần thiết đưa vào."*

Hồ sơ khảo sát của dự án khác là NGUỒN THAM KHẢO, không phải CĂN CỨ. Không liệt kê trong mục
"Những căn cứ để lập báo cáo". Quyết định phê duyệt dự toán chi phí chuẩn bị dự án cũng bị loại.

### L9. Danh mục tiêu chuẩn phải đúng loại công trình

Nhận xét: *"Sai, không liên quan."* · *"Không liên quan."* · *"Quá cũ, cần kiểm tra rà soát xem có
mới hơn không."*

Danh mục dài mà lẫn tiêu chuẩn không dùng thì làm giảm độ tin cậy của cả danh mục. Với công trình
cầu, anh đã loại: quy chuẩn quy hoạch xây dựng · tiêu chuẩn kết cấu thép (nếu không dùng thép) ·
tiêu chuẩn thiết kế nền nhà · tiêu chuẩn cọc khoan nhồi (nếu dùng cọc ly tâm đóng) · **toàn bộ
nhóm tiêu chuẩn công trình thuỷ lợi/đê biển** khi hạng mục cầu độc lập kết cấu với kè.

Quy tắc: giữ tiêu chuẩn nào thì phải chỉ ra được nó chi phối nội dung nào trong hồ sơ. Rà tiêu
chuẩn ban hành trước 2000 xem đã có bản thay chưa.

Bỏ câu dự phòng *"Trường hợp xuất hiện tiêu chuẩn mới thay thế..."* — nhận xét: *"Không đưa nội
dung này vào."*

### L10. Mô tả quan hệ giữa công trình đang thiết kế và công trình lân cận

Nhận xét: *"Cầu nằm phía trên và độc lập với tuyến kè."* · *"Sai. Tuyến kè độc lập với tuyến cầu"*
· *"Sai nghiêm trọng về kết cấu. Cần chỉnh lại fact.yaml"*

Trùng tuyến trên mặt bằng **không** đồng nghĩa với liên kết kết cấu. Trước khi viết bất kỳ câu nào
kiểu "tận dụng", "tựa trên", "làm nền đỡ", phải xác nhận sơ đồ truyền lực trên bản vẽ cắt ngang:
kết cấu mới có hệ móng riêng hay truyền tải vào kết cấu cũ?

Viết sai chỗ này kéo theo hàng loạt: lập luận so sánh phương án, khối lượng móng, danh mục tiêu
chuẩn áp dụng, và yêu cầu kiểm toán kết cấu cũ. Ghi kết luận vào `_facts.yaml` thành một khoá
riêng để các chương sau không tự suy diễn lại.
