# xh-tuvan — v0.6.0

Bộ skill viết hồ sơ tư vấn thiết kế xây dựng Việt Nam — thuỷ lợi, đê điều, kè bờ sông, giao thông, hạ tầng.

## Quick Start (Bắt đầu nhanh)

Để gọi hệ thống và bắt đầu quy trình làm việc, gõ vào khung chat:
`"Bắt đầu điều phối dự án tư vấn thiết kế"` hoặc gọi skill `@xh-tuvan`.
Hệ thống sẽ tự động phân tích và lần lượt kích hoạt các skill tương ứng như xếp lại thư mục, dựng kho số liệu, viết báo cáo, soát lỗi và xuất bản Word.

## Vì sao có plugin này

Cách làm cũ cho AI sinh từng file `.docx` rồi ghép lại. Ghép `.docx` là thao tác mất mát về bản chất — mỗi file mang `styles.xml`, `numbering.xml`, `sectPr` riêng — nên ghép xong thì mục lục không build được, đánh số đề mục nhảy loạn, header đổi giữa chừng. Đó chính là danh sách việc phải sửa tay sau mỗi báo cáo.

Plugin này thay bằng **kiến trúc ba lớp**: dữ liệu (`_facts.yaml`) → nội dung (Markdown) → trình bày (render một lần vào khuôn `.dotx`). Định dạng khi đó là hằng số, không phụ thuộc vào việc mô hình hôm nay viết thế nào.

## Mười skill

**Luồng chính — viết báo cáo**

| Skill | Việc |
|---|---|
| `xh-tuvan` | điều phối — xác định đang ở bước nào, gọi skill con |
| `xh-outline` | sinh và khoá bản đặc tả đề mục, tách exemplar từ báo cáo đã duyệt |
| `xh-viet` | viết nội dung ra Markdown theo spec và hồ sơ văn phong |
| `xh-qc` | rà soát ba tầng: luật cứng · agent năm lăng kính · bỏ phiếu — không cần API trả phí |
| `xh-docx` | render vào khuôn Word, kiểm định dạng |

**Phục vụ — gọi khi cần**

| Skill | Việc |
|---|---|
| `xh-proj-org` | tổ chức thư mục hồ sơ dự án **trên ổ đĩa** theo hệ `10.PhapLy/ 20.DauThau/ 30.KhaoSat/…`, đặt tên file, lập danh mục Excel có hyperlink |
| `xh-drive` | làm việc thẳng với hồ sơ **trên Google Drive** — quét, phân loại, tạo folder, di chuyển file, đọc nội dung. Không cần chép về máy |
| `xh-evidence` | dựng kho số `_facts.yaml` có nguồn và câu trích; sinh phiếu duyệt; hồ sơ khảo sát quá nặng thì sinh phiếu yêu cầu cho NotebookLM (thao tác thủ công, ngoài Claude) thay vì gọi API |
| `xh-trich-hinh` | trích hình, sơ đồ, mặt cắt từ bản vẽ PDF; lập danh mục hình; đọc nhanh hồ sơ scan |
| `xh-trinh-sat` | tự tìm thông tin công khai liên quan dự án (quy hoạch, sạt lở, mực nước BĐ3, dự án lân cận) qua MCP **Exa**, ghi có nguồn/URL vào `00_input/90.TrinhSat-Exa/` — cần kết nối connector Exa trước |

Cộng một agent độc lập `xh-qc` — rà bằng ngữ cảnh sạch, vì agent tự kiểm bài của chính mình luôn dễ dãi.

## Script dùng chung

| Script | Việc | Trạng thái |
|---|---|---|
| `render_report.py` | đổ Markdown vào khuôn, render một lần | đã chạy thật |
| `qc-check.py` + `qc-rules.yaml` | kiểm tất định, 9 nhóm luật | 15/18 điểm trong phạm vi, 0 báo sai |
| `mine-style.py` | đo văn phong từ kho báo cáo | đã chạy trên 3.214 câu |
| `do-muc-h.py` | đo giọng theo từng nhóm đề mục | đã chạy trên 229 đề mục |
| `learn-from-edits.py` | rút quy tắc từ bản người dùng sửa | prototype |
| `detect-figures.py` | tự dò vùng hình trong PDF, không cần biết bbox | prototype |
| `geo-index-photos.py` | EXIF + KMZ → lý trình từng ảnh | prototype |
| `extract-video-frames.py` | lọc 18.000 khung video xuống ~50 khung dùng được | prototype |
| `pdf-trich-hinh.py` | trích hình từ PDF kỹ thuật bằng `docling` | cần `pip install docling` |
| `phan-loai-ho-so.py` | phân loại file vào nhóm `00_input/` theo luật tất định, ba mức tin cậy | chạy được ngay |
| `sinh-phieu-yeucau-notebooklm.py` | sinh phiếu yêu cầu trích xuất — đưa cho NotebookLM (thủ công) | chạy được ngay, không cần khoá API |
| `doc-ket-qua-notebooklm.py` | bóc bảng kết quả NotebookLM đã điền ngược vào `_facts.yaml` | chạy được ngay |
| `ghi-ket-qua-trinh-sat.py` | sổ ghi tất định cho kết quả trinh sát Exa | chạy được ngay, cần `xh-trinh-sat` gọi kèm connector Exa |
| `evidence-gemini.py` | trích Evidence Pack từ hồ sơ nặng, ra thẳng lược đồ `_facts.yaml` — **đường dự phòng**, không còn mặc định | cần `GEMINI_API_KEY` |

## Cần có trên máy

- `KhuonMau_NamQuoc.dotx` — khuôn công ty, bản chốt
- Thư mục dự án theo cấu trúc ở `references/kien-truc-3-lop.md`

Bìa **không** thuộc quy trình này — làm file riêng.

## Đọc trước

`references/nguyen-tac.md` — tám nguyên tắc không thương lượng và danh sách "không tự động làm".


---

## Nhật ký phiên bản

### v0.3.2 — 26/08/2026

Thêm một tài liệu, không đổi hành vi skill nào.

- **Thêm `references/huong-dan-sua.md`** — hướng dẫn cho người dùng cách tô màu và bật Track
  Changes khi sửa bản `..._dasua.docx` (quy ước R7: 🟡 vàng = sai · 🟢 xanh lá = cần rà lại ·
  🔵 xanh lam = cần viết lại), gộp từ nội dung trước đây chỉ nằm rải rác trong hội thoại.
- **Quy ước mới: xóa cả đoạn thì dùng Comment của Word, không dùng màu.** Lý do: tô vàng trong
  bản render đã có sẵn *tự động* cho mọi `{{fact:}}` chưa `verified` (không phải người dùng tô
  tay) — nên chỉ xóa một đoạn vốn đã vàng sẵn không đủ để Claude phân biệt "chủ động gắn nghĩa
  sai theo R7" với "markup tự động còn sót lại, xóa vì lý do khác". Ba màu R7 cũng chỉ mô tả vấn
  đề của câu còn lại, không có màu riêng cho lý do xóa hẳn (thừa, trùng ý, hết cần). Comment gắn
  trực tiếp lý do vào đúng vị trí, không lẫn với cơ chế tô vàng tự động.
- **`skills/xh-tuvan/SKILL.md`** — mục "Vòng học từ bản người dùng sửa" nay trỏ sang
  `references/huong-dan-sua.md` thay vì chỉ nhắc chung chung "lưu song song hai bản".

**Việc của người cài:** cài đè `xh-tuvan-v0.3.2.plugin`. Không có thay đổi kiến trúc; nếu đã có
quy trình gửi hướng dẫn tô màu riêng cho người dùng ngoài plugin, có thể thay bằng file này.

### v0.3.1 — 25/08/2026

Mười hai điểm sửa nhỏ, gọn ngữ cảnh và bịt vài lỗ hổng — dựa trên bản v0.3.0 vừa duyệt, không đổi kiến trúc.

- **Tách `references/quy-uoc-dat-ten.md`** khỏi `skills/xh-proj-org/SKILL.md` (cây thư mục chuẩn, hệ đánh số, quy ước đặt tên file/folder, script đổi tên) — giảm dung lượng ngữ cảnh nạp mỗi lần kích hoạt skill, chỉ để lại dòng tham chiếu.
- **Vá `render_report.py`** — không còn ép cứng mọi ảnh về `width=Cm(16.0)`. Đọc kích thước thật bằng Pillow: ảnh ngang giữ `width=16cm`, ảnh dọc đổi sang `height=20cm`. Thiếu Pillow hoặc lỗi đọc ảnh thì lùi về hành vi cũ, có cảnh báo ra `stderr`.
- **Thêm bước 1 vào Self-check của `xh-viet`** — quét lại bản thảo tìm số gõ chết chưa bọc `{{fact:...}}` trước khi giao, không chỉ chạy `qc-check.py`.
- **`xh-tuvan` chặn tự viết nội dung** — thêm dòng cảnh cứng ngay dưới mô tả: gặp yêu cầu viết nội dung trực tiếp thì chuyển sang `xh-viet`, không tự viết trong ngữ cảnh điều phối. Bảng skill phục vụ ghi rõ thêm: "sắp xếp hồ sơ" chung chung mặc định hiểu là ổ đĩa (`xh-proj-org`), chỉ dùng `xh-drive` khi người dùng nói rõ "trên Drive".
- **`xh-qc` Tầng 3 ghi rõ điều kiện kích hoạt** — chỉ bỏ phiếu khi Tầng 2 phát hiện lỗi nghiêm trọng về giải pháp kỹ thuật, lập luận thiếu logic, hoặc sai khác lớn so với định mức; nhắc lại không có mô hình ngoài Claude tham gia bỏ phiếu (nhất quán với việc bỏ hẳn Tầng 4 từ v0.3.0).
- **`xh-drive` — cảnh báo cắt file rõ hơn.** Nêu đích danh giới hạn ngầm ~10MB của `read_file_content` và việc API cắt đuôi file mà không báo lỗi; yêu cầu kiểm câu cuối có bị đứt ngang không, không chỉ kiểm mục lục.
- **`xh-evidence` — thêm fallback khi thiếu `GEMINI_API_KEY`.** Ngoài đường mặc định (phiếu yêu cầu → NotebookLM), nêu thêm lối tắt cho vài chỉ tiêu lẻ: tự upload hồ sơ lên giao diện chat bất kỳ (NotebookLM/ChatGPT/Claude.ai), chép câu trả lời vào file tạm đúng khuôn bảng, rồi vẫn phải qua `doc-ket-qua-notebooklm.py` để vào `_facts.yaml` — không tự tay gõ số vào file.
- **`xh-trich-hinh` — cảnh báo dung lượng `docling` cụ thể hơn** (~1.5GB, kéo theo mô hình nhận diện AI), phải báo trước cho người dùng về thời gian tải.
- **`xh-docx` — thêm mẹo Windows** dùng script PowerShell qua COM Object (`word.application`) để ép cập nhật mục lục tự động, thay vì luôn phải mở Word thủ công.
- **`xh-outline` — hạ mục "Khối lượng thực tế" xuống thành ghi chú** (blockquote) thay vì để thành đề mục ngang hàng, tránh gây hiểu nhầm đây là một bước quy trình.
- **`references/kien-truc-3-lop.md` — thêm `schema_version` bắt buộc** ở đầu lược đồ minh hoạ `_facts.yaml`, dọn đường cho việc quản lý phiên bản khuôn dữ liệu sau này.
- **`README.md`** — thêm mục Quick Start ngay đầu trang. **`plugin.json`** — thêm `"license": "MIT"`.

**Việc của người cài:** cài đè `xh-tuvan-v0.3.1.plugin`. Không có thay đổi kiến trúc, không cần làm gì thêm ngoài cài lại.

### v0.3.0 — 25/08/2026

Sau nghiệm thu v0.2.1 (`30-KiemThu/KetQua-Eval-ChonSkill-v0.2.1.md`), anh Hưng quyết định bỏ hẳn hai script gọi API trả phí theo token khỏi luồng mặc định. Đã tra MCP registry trước khi làm: **không có connector NotebookLM, không có connector OpenAI/ChatGPT nào** trong kho hiện tại — vì vậy hướng xử lý là thủ công (NotebookLM) và bỏ hẳn (ChatGPT), không phải "đổi sang MCP" như dự tính ban đầu.

- **`xh-evidence` — đổi đường mặc định cho hồ sơ nặng.** Không còn tự gọi Gemini. Đường mới: sinh **phiếu yêu cầu trích xuất** (`scripts/sinh-phieu-yeucau-notebooklm.py`, quét `_facts.yaml` + danh mục chỉ tiêu, liệt kê đúng khoá còn thiếu/`unverified`/`conflict`) → người dùng tự đưa cho NotebookLM (thao tác tay, ngoài Claude, không có API để tự động hoá) → đưa kết quả về, bóc ngược vào `_facts.yaml` bằng `scripts/doc-ket-qua-notebooklm.py` (luôn ghi `status: unverified`, không tự ý ghi đè khoá đã `verified`). `evidence-gemini.py` (`GEMINI_API_KEY`) hạ xuống thành đường dự phòng, chỉ dùng khi người dùng chủ động yêu cầu.
- **Thêm `xh-trinh-sat`** — trinh sát tự động bằng MCP **Exa** (`web_search_exa`): quy hoạch liên quan, cảnh báo sạt lở, mực nước báo động BĐ3, dự án lân cận, điều kiện tự nhiên–xã hội. Ghi có nguồn/URL vào `00_input/90.TrinhSat-Exa/` qua sổ ghi tất định `scripts/ghi-ket-qua-trinh-sat.py`. **Chưa chạy thử được** — tổ chức chưa kết nối connector Exa lúc đóng gói bản này; skill tự kiểm tra công cụ có sẵn không trước khi làm, không tự bịa kết quả tìm kiếm.
- **Bỏ hẳn QC Tầng 4** (`qc-tang4-ngoai.py`, dùng `OPENAI_API_KEY`) khỏi luồng chính — đã xoá khỏi `scripts/`. QC dừng lại ở ba tầng: luật cứng tất định (`qc-check.py`) → agent `xh-qc` năm lăng kính → bỏ phiếu nhiều agent. Không đổi sang MCP nào khác vì không tìm thấy connector ChatGPT/OpenAI trong registry — quyết định của người dùng là bỏ hẳn lớp này, không phải thay thế.

**Việc của người cài:** cài đè `xh-tuvan-v0.3.0.plugin`. Muốn dùng `xh-trinh-sat` thì kết nối connector **Exa** trên claude.ai trước — chưa kết nối thì skill sẽ báo và dừng, không tự tìm bằng cách khác.

### v0.2.0 — 25/08/2026

Hợp nhất phần dùng được của plugin `xh-tuvan-v2` vào đây, thay vì chuyển hẳn sang v2 — v2 dựng theo kiến trúc ghép `.docx` mà plugin này đã bỏ, và chỉ phủ được BCĐXCTĐT.

- **Thêm `xh-proj-org`** (bê từ v2). Sửa tool xin quyền xoá cho phiên chạy trên cloud qua cầu nối thiết bị; thêm ghi chú phân biệt hai hệ đánh số thư mục.
- **Thêm `xh-trich-hinh`** — `docling` trích hình từ PDF. Đổi mặc định thành trích ảnh + danh mục `.md` cho đúng kiến trúc ba lớp; chế độ dựng `.docx` chỉ để đọc nhanh, có cảnh báo không dùng giao nộp.
- **Thêm `references/phap-ly-2026-07-01.md`** — danh mục văn bản mốc 01/7/2026 và bảng thay thế văn bản đã hết hiệu lực.
- **Thêm Mục K vào `ho-so-van-phong.md`** — Stop Slop, đánh dấu rõ là quy tắc nhập từ ngoài, **chưa đo trên kho**; mâu thuẫn với Mục G thì Mục G thắng.
- **Thêm nguyên tắc 9** — chuỗi lập luận năm mắt xích.
- **Tương thích ngược `status: muon_du_an_khac`** — `_facts.yaml` của Cầu Sông Đốc dùng giá trị này để đánh dấu số mượn (32/70 khoá) trước khi có trường `data_type`. Luật L10 nhận nó như `data_type: REFERENCE`; luật L8 thôi báo trùng `SO_CHUA_DUYET` cho những khoá đó. **Việc nên làm dần:** chuyển sang hai trục tách bạch — `status` cho trạng thái duyệt, `data_type` + `nguon_du_an` cho xuất xứ. Trộn hai trục vào một trường thì không diễn đạt được "số mượn nhưng đã được duyệt dùng".
- **Thêm `data_type` vào `_facts.yaml`** (`PROJECT` / `REFERENCE` / `LEGAL` / `MISSING`) và **luật L10 trong `qc-check.py`**: số mượn từ dự án khác phải dẫn tên nguồn và kèm khuyến cáo khảo sát bổ sung; khoá `MISSING` cấm dùng trong bản thảo.
- **Thêm QC Tầng 4** `qc-tang4-ngoai.py`. Khác bản gốc của v2: thiếu khoá API thì **thoát mã 2**, không trả về câu chữ trông như đã thẩm tra xong.
- **Vá L1 vào `render_report.py`** — `updateFields` chèn đúng vị trí trong sequence `CT_Settings`. Đã render thử bằng `KhuonMau_NamQuoc.dotx` và kiểm lại thứ tự phần tử: `characterSpacingControl → updateFields → hdrShapeDefaults`.

**Việc của người cài:** sau khi cài đè v0.2.0, **tắt plugin `xh-tuvan-v2` và skill `xh-dxct`** — ba skill đang tranh nhau cùng loại báo cáo BCĐXCTĐT.


### v0.2.1 — 25/08/2026

Trả lời hai câu hỏi: *"sao rút từ 17 skill xuống còn 7?"* và *"đọc thẳng hồ sơ trên Drive được không?"*

**Về số skill.** Không có skill nào bị bỏ. Plugin `xh-tuvan-v2` có 17 skill, trong đó **11 skill vốn đã bật sẵn ở cấp tài khoản** (`docx` · `xlsx` · `pptx` · `pdf` · `skill-creator` · `morning` · `schedule` · `setup-cowork` · `import-memory` · `consolidate-memory` · `explain-usage`) — v2 chỉ đóng gói lại chúng. Tắt v2 **không** làm mất chúng. Sáu skill nghiệp vụ còn lại đã được xử lý hết:

| Skill của v2 | Về đâu trong v0.2.1 |
|---|---|
| `xh-proj-org` | giữ nguyên là skill, sửa tool xin quyền xoá + ghi chú hai hệ đánh số |
| `pdf-to-word-engineering` | thành `xh-trich-hinh`, đổi mặc định sang trích ảnh + danh mục `.md` |
| `chatgpt-reviewer` | thành `scripts/qc-tang4-ngoai.py`, gọi từ `xh-qc` Tầng 4 |
| `engineering-writing-master` | nhập nội dung vào `ho-so-van-phong.md` Mục K + `nguyen-tac.md` nguyên tắc 9 |
| `gemini-retriever` | thành `xh-evidence` + `scripts/evidence-gemini.py` |
| `xh-viet-bao-cao` | nội dung chưng thành `20-Khuon/specs-BCDXCTDT.yaml`; việc viết do `xh-viet` làm |

**Thêm `xh-drive`.** Connector Google Drive đọc được `.docx` `.pdf` `.xlsx` ra Markdown đã bóc chữ — kiểm chứng thật trên `1.CauSD_DeXuatCTDT_V4R1.docx`. Tạo folder, di chuyển, đổi tên file trên Drive đều làm được. Hai việc **không** làm được qua connector: ghi `.docx` thành phẩm lên Drive (phải base64, file 456KB thành 608.000 ký tự) và trích hình từ bản vẽ PDF — hai việc đó vẫn đi đường ổ đĩa.

**Thêm `phan-loai-ho-so.py`.** Luật tất định, ba mức tin cậy `chac` / `doan` / `khong_ro`. Kiểm thử trên 19 file thật của Cầu Sông Đốc: 15 chắc, 2 đoán, 2 không rõ — hai file "không rõ" đúng là hai file mơ hồ thật. Chỉ file `chac` mới được tự xếp; còn lại gom một bảng hỏi người dùng một lần.

**Việc của người cài:** sau khi cài v0.2.1, **tắt hai skill tài khoản `xh-proj-org` và `pdf-to-word-engineering`** — bản trong plugin đã được sửa, để cả hai sẽ tranh nhau.

---

## v0.4.0 — Cổng Gemini_QC theo từng chương (26/08/2026)

**Quy tắc mới, bắt buộc:** viết xong một chương thì chạy `Gemini_QC` trên chương đó; chưa nhận
phản hồi ĐẠT thì không được viết chương tiếp theo.

Lý do: bản v2 Cầu Sông Đốc viết một mạch 10 chương rồi mới kiểm. Một lỗi kết cấu ở Chương I —
mô tả sai quan hệ cầu–kè — lan sang bốn chương và kéo đổ cả lập luận so sánh phương án. Kiểm
ngay sau Chương I thì lỗi đã dừng ở một chương.

Luồng QC nay có ba tầng:

| Tầng | Công cụ | Phạm vi | Thời điểm |
|---|---|---|---|
| 1 | `scripts/qc-check.py` | luật cứng, tất định | sau mỗi chương |
| 2 | `Gemini_QC` (MCP ngoài Claude) | **cổng bắt buộc** | sau mỗi chương |
| 3 | agent `xh-qc` | năm lăng kính, chéo chương | sau khi đủ 10 chương |

Khi gọi Gemini_QC phải dán kèm **khối số liệu neo** từ `_facts.yaml` vào đầu `report_text` —
Gemini không thấy các chương khác nên không có khối này thì không bắt được mâu thuẫn chéo chương.

Gemini_QC không gọi được thì **dừng và báo người dùng**, không tự bỏ qua cổng.

**Hồ sơ văn phong thêm Mục L — vai người viết**, rút từ 249 đoạn anh Hưng xoá trong bản v2:
không viết về chính bản báo cáo · không kể quá trình làm hồ sơ · không giải trình nguồn số liệu
trong thân bài · không viết câu phòng thủ · tách thông tin chính khỏi bảng chỉ tiêu kỹ thuật ·
danh mục tiêu chuẩn phải đúng loại công trình · xác nhận sơ đồ truyền lực trước khi viết "tận
dụng/tựa trên".

---

## v0.5.0 — Bộ đặc tả đề mục hạt giống cho BCĐXCTĐT (01/09/2026)

Trước bản này, spec đề mục chỉ tồn tại trong thư mục từng dự án — mỗi dự án mới lại phải
sinh spec từ đầu, và bài học rút được ở dự án trước không đi theo. Nay plugin mang sẵn một
bộ hạt giống, chép sang dự án rồi mới điền phần riêng của dự án đó.

- **Thêm `references/spec-goc-BCDXCTDT.yaml`** — spec gốc cho Báo cáo đề xuất chủ trương
  đầu tư. Bản đầu tiên có một đề mục đầy đủ: **C3.4 Phạm vi đầu tư**, gồm mục tiêu, bảy câu
  hỏi thẩm định, cấu trúc bắt buộc sáu khối a)–đ), sáu điều cấm kỵ và `loi_da_xay_ra_that`.
  Không chứa số liệu của dự án nào, chỉ chứa *loại* số liệu.
- **Thêm `references/exemplars/BCDXCTDT/C3-4_PhamViDauTu.md`** — exemplar kèm ghi chú bảy
  dòng "vì sao đoạn này tốt", rút từ bản hợp nhất R7 Kè Thủ Thiêm.
- **`xh-outline`** — thêm mục "Bộ hạt giống có sẵn trong plugin": quy trình chép sang
  `specs/<LoaiBC>.yaml`, và điều kiện để được bổ sung đề mục mới vào bộ hạt giống (luật ba
  báo cáo, `cam_ky` phải rút từ lỗi đã xảy ra thật).
- **`xh-viet`** — bảng nạp ngữ cảnh trỏ sang bộ hạt giống khi dự án chưa có spec. Danh sách
  cấm thêm ba dòng:
  - "bước lập dự án đầu tư" → **"bước lập Báo cáo nghiên cứu khả thi"**. Sau chủ trương đầu
    tư, bước kế tiếp có tên pháp lý riêng; gọi sai là lỗi bị thẩm định bắt ngay.
  - **Không viện dẫn cả hai hệ quản lý luồng cho cùng một vị trí.** Đoạn sông đã xác định
    thuộc vùng nước cảng biển thì viện dẫn hành lang luồng hàng hải và Cảng vụ Hàng hải;
    không kèm hành lang luồng đường thuỷ nội địa.
  - Không chép lại trị số đã nêu ở đề mục khác (cao trình, tần suất, cấp công trình) —
    dẫn chiếu số đề mục. Trị số lặp ở hai chỗ là nguồn sai lệch khi thông số được tính lại;
    Kè Thủ Thiêm đổi tần suất từ 5% sang 1,5% là một lần vấp đúng chỗ này.
- **`scripts/qc-rules.yaml`** — thêm hai luật cứng vào nhóm `cho_trong`: `SAI_TEN_BUOC`
  (nghiêm trọng) và `TRUNG_HE_LUONG` (cảnh báo). Đã thử trên năm câu mẫu: bắt đúng cả hai
  ca lỗi, không báo sai cho ba ca đúng — kể cả câu hợp lệ nhắc đường thuỷ nội địa cấp II ở
  chương phù hợp quy hoạch.

**Việc của người cài:** cài đè `xh-tuvan-v0.5.0.plugin`. Không đổi kiến trúc. Dự án đang
chạy mà đã có `specs/BCDXCTDT.yaml` riêng thì spec dự án vẫn thắng — bộ hạt giống chỉ dùng
khi dự án chưa có.

---

## v0.6.0 — Hai luật số liệu mới cho xh-qc + đơn giá đất lợi ích kinh tế (01/09/2026)

Rút từ phiên viết Chương IV–X BCĐXCTĐT dự án Kè Thủ Thiêm — hai lỗi tính toán thật lọt qua
ba vòng rà trước khi bị bắt ở vòng thứ ba, cả hai đều là loại lỗi "đúng số riêng lẻ, sai khi
đặt cạnh nhau", đúng loại `xh-qc` lăng kính L1/L5 sinh ra để bắt.

- **`agents/xh-qc.md` — thêm L1a và L1b vào lăng kính L1 (Số liệu):**
  - **L1a — So sánh dự án đối chứng phải cùng cơ sở tính.** So sánh suất đầu tư/suất chi phí
    với dự án đối chứng mà một bên gồm dự phòng/GPMB còn bên kia không, rồi vẫn kết luận
    "cao hơn/thấp hơn X%", là lỗi `nghiem_trong`. Ca thật: bản thảo kết luận "+5,2%" trong
    khi cùng cơ sở tính, chênh lệch thực là +26,3% — sai gần 5 lần độ lớn.
  - **L1b — Annuity phải quy đổi lại theo từng kịch bản độ nhạy.** Một khoản lợi ích quy đổi
    từ giá trị một lần sang dòng đều bằng công thức annuity(i, n) thì mọi kịch bản đổi i hoặc
    n trong bảng độ nhạy phải tính lại đúng khoản đó theo cặp (i,n) của kịch bản — không giữ
    nguyên trị số phương án cơ sở. Ca thật: bảng đổi i=10%/14% và n=30 năm nhưng ban đầu giữ
    nguyên 34,1 tỷ đồng/năm của khoản lợi ích đất; sửa đúng thành 28,5 / 39,7 / 35,1 tỷ
    đồng/năm theo từng kịch bản.
- **Thêm `references/don-gia-dat-loi-ich-kinh-te.md`** — chuỗi 4 bước quy đổi giá đất từ
  Bảng giá đất địa phương (Nghị quyết HĐND) sang đơn giá dùng cho lợi ích kinh tế đất ven
  sông/đê: Vị trí 1 → quy Vị trí theo tiếp cận đường bộ → giảm theo khoảng cách → hệ số theo
  mục đích sử dụng đất công cộng, kèm kiểm sàn bắt buộc (không thấp hơn giá đất nông nghiệp
  cùng vị trí) và ví dụ số thật (Kè Thủ Thiêm: 25.488.000 đ/m²).
- **`xh-viet`** — bảng nạp ngữ cảnh trỏ sang tài liệu trên khi viết mục hiệu quả kinh tế có
  nhóm lợi ích liên quan đến đất.

**Việc của người cài:** cài đè `xh-tuvan-v0.6.0.plugin`. Không đổi kiến trúc, không đổi luồng
làm việc — chỉ thêm hai luật kiểm và một tài liệu tham khảo.
