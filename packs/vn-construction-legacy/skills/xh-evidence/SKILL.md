---
name: xh-evidence
description: |
  Dựng kho số _facts.yaml cho một dự án — quét hồ sơ đầu vào theo danh mục chỉ tiêu, ghi mỗi khoá kèm nguồn, câu trích, trạng thái duyệt và loại xuất xứ; sinh phiếu duyệt cho người dùng chốt. Khi hồ sơ khảo sát quá nặng để đọc thẳng, sinh phiếu yêu cầu trích xuất để người dùng đưa cho NotebookLM (thao tác thủ công, ngoài Claude), rồi bóc kết quả NotebookLM trả về ngược vào _facts.yaml. Kích hoạt khi người dùng nhắc: dựng _facts.yaml, kho số dự án, trích số liệu từ hồ sơ, Evidence Pack, phiếu duyệt số liệu, bóc chỉ tiêu địa chất, số liệu thuỷ văn từ hồ sơ khảo sát, phiếu yêu cầu trích xuất, NotebookLM, đọc kết quả NotebookLM. Không viết nội dung báo cáo — chỉ dựng lớp dữ liệu; viết là việc của xh-viet.
---

# XH_Evidence — Lớp 1 của kiến trúc ba lớp

Con số chỉ tồn tại ở một nơi: `_facts.yaml`. Skill này dựng nó ra và đưa cho người dùng duyệt. Bản thảo về sau chỉ viết `{{fact:ten_chi_tieu}}`.

## Nguyên tắc cốt lõi

**Quét theo danh mục, không quét tự do.** Bảo mô hình "trích mọi số liệu trong hồ sơ" sẽ trả về hàng nghìn con số vô dụng — số trang, số hiệu bản vẽ, năm ban hành, số thứ tự bảng. Lấy danh mục chỉ tiêu từ `scripts/qc-rules.yaml` rồi đi tìm đúng những chỉ tiêu đó.

**Sáu trường cho mỗi khoá:**

```yaml
cao_do_dinh_ke:
  value: 2.50
  unit: m
  source: "1.TMTK_ke AFD 21.2.2025.docx#tr.45"
  quote: "cao trình đỉnh kè thiết kế +2,50m (hệ Hòn Dấu)"
  status: unverified          # unverified | verified | conflict
  data_type: REFERENCE        # PROJECT | REFERENCE | LEGAL | MISSING
  nguon_du_an: "kè AfD Đê biển Tây"   # bắt buộc khi REFERENCE
```

Trường `quote` quyết định tốc độ duyệt: người dùng đọc câu trích là biết ngay có hiểu đúng ngữ cảnh không, khỏi mở lại PDF gốc. Duyệt 80 chỉ tiêu mất khoảng 30–40 phút.

Trường `data_type` chặn đúng cái bẫy hay gặp nhất: số mượn của dự án lân cận bị trình bày như số của chính dự án. `qc-check.py` luật L10 bắt lỗi này.

## Hai đường lấy số — chọn theo độ nặng của hồ sơ

| Hồ sơ | Đường đi | Ghi chú |
|---|---|---|
| File vừa phải, nằm trên Drive | connector Drive, `read_file_content` | rẻ nhất, không tốn khoá API. Xem skill `xh-drive` |
| File vừa phải, nằm trên ổ đĩa hoặc thư mục đã kết nối | đọc thẳng | |
| **Hồ sơ khảo sát scan hàng trăm trang · nhiều file quét cùng lúc · file lớn bị connector cắt** | phiếu yêu cầu → NotebookLM (thủ công) → bóc kết quả | xem quy trình dưới đây — **đường mặc định**, không cần khoá API nào |

### Đường mặc định cho hồ sơ nặng — qua NotebookLM (thủ công)

NotebookLM không có API công khai, không tự động hoá được từ trong Claude. Quy trình ba bước:

**Bước 1 — sinh phiếu yêu cầu.** Quét `_facts.yaml` hiện có (khoá thiếu / `unverified` / `conflict` / `data_type: MISSING`) đối chiếu danh mục chỉ tiêu, sinh ra một file liệt kê rõ cần hỏi gì, kèm bảng mẫu để dán câu trả lời:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/sinh-phieu-yeucau-notebooklm.py \
       --facts 00_input/../_facts.yaml \
       --chi-tieu ${CLAUDE_PLUGIN_ROOT}/scripts/qc-rules.yaml \
       --ten-du-an "<tên dự án>" \
       --ra _YeuCau-TrichXuat-NotebookLM.md
```

Đưa file này cho người dùng. **Việc của người dùng, ngoài Claude:** tải hồ sơ khảo sát lên NotebookLM, hỏi theo từng dòng trong phiếu, dán câu trả lời của NotebookLM vào bảng mẫu ở cuối file (hoặc lưu thành file riêng theo cùng khuôn bảng), rồi đưa file đã điền lại cho Claude.

**Bước 2 — nhận lại và bóc vào `_facts.yaml`.** Khi người dùng đưa file đã điền:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/doc-ket-qua-notebooklm.py \
       --ket-qua <file đã điền> \
       --facts _facts.yaml \
       --ra _facts.yaml
```

Script tự ghi `status: unverified` cho mọi khoá mới (không bao giờ tự đặt `verified`), bỏ qua dòng thiếu `value` hoặc `quote`, và không ghi đè khoá nào đã `verified` sẵn — những trường hợp đó in ra riêng để người dùng tự quyết.

**Bước 3 — báo người dùng duyệt** như phiếu duyệt thường (xem mục "Phiếu duyệt" dưới).

### Đường dự phòng — `evidence-gemini.py`

Chỉ dùng khi người dùng **chủ động yêu cầu** dùng Gemini (ví dụ cần quét hàng loạt file tự động, không muốn thao tác tay qua NotebookLM) **và** đã có sẵn `GEMINI_API_KEY`. Không còn là đường mặc định.

```bash
export GEMINI_API_KEY=...
python ${CLAUDE_PLUGIN_ROOT}/scripts/evidence-gemini.py \
       --tai-lieu 00_input/30.KhaoSat-DiaChat/*.pdf \
       --chi-tieu ${CLAUDE_PLUGIN_ROOT}/scripts/qc-rules.yaml \
       --ra 00_input/_evidence-diachat.yaml
```

Không có khoá thì script thoát mã 2 và không trả về gì — chủ ý, để tránh trả về dữ liệu trông giống thật (grep vài dòng chứa từ khoá) mà không có số trang, không ngữ cảnh.

> **Fallback khi thiếu `GEMINI_API_KEY`:** Thấy mã thoát 2 thì quay lại đường mặc định ở trên (phiếu yêu cầu → NotebookLM thủ công → bóc kết quả) — đó chính là đường không cần khoá API. Nếu người dùng muốn nhanh hơn cho một vài chỉ tiêu lẻ, cũng có thể gợi ý họ tự upload hồ sơ lên bất kỳ giao diện chat nào có sẵn (NotebookLM, ChatGPT, Claude.ai), hỏi trực tiếp, rồi chép phần trả lời vào một file tạm theo đúng khuôn bảng của `_YeuCau-TrichXuat-NotebookLM.md`. Dùng file tạm đó làm đầu vào cho `doc-ket-qua-notebooklm.py` để dựng `_facts.yaml` đúng cấu trúc — không tự tay gõ giá trị vào `_facts.yaml`.

## Ba trạng thái, đừng nhầm với xuất xứ

Đây là hai trục khác nhau, hay bị trộn làm một:

```
status     — ĐÃ DUYỆT CHƯA:  unverified → verified (người dùng chốt) · conflict
data_type  — SỐ TỪ ĐÂU RA:   PROJECT · REFERENCE · LEGAL · MISSING
```

Một khoá có thể vừa là `REFERENCE` vừa là `verified` — số mượn của dự án bên cạnh, nhưng người dùng đã xem và đồng ý cho dùng. Nhét cả hai ý vào một trường `status` thì không diễn đạt được tình huống đó.

> Ghi chú tương thích: `_facts.yaml` của Cầu Sông Đốc dựng trước 25/08/2026 dùng `status: muon_du_an_khac` cho 32 khoá. `qc-check.py` hiểu được giá trị đó và coi như `data_type: REFERENCE`. Khi có dịp, tách ra hai trục cho sạch.

## Mâu thuẫn — không tự xử

Cùng một khoá mà hai nguồn cho hai giá trị → `status: conflict`, liệt kê `ung_vien` kèm nguồn từng cái, **không tự chọn cái hợp lý hơn**. Đây là Nguyên tắc 7.

```yaml
sdd_tong_mat_dat_vinh_vien:
  status: conflict
  ung_vien:
    - value: 2774
      unit: m2
      source: "DT SDĐ.xlsx#ô D7"
      quote: "Mất đất vĩnh viễn: 2.774"
    - value: 5063
      unit: m2
      source: "DT SDĐ.xlsx#D8+D9"
      quote: "452,52 × 2,6 = 1.176,552 · phần còn lại 3.886,448"
  ghi_chu: "D7 gõ tay, trùng đúng ô D4 của mục I — nghi là bản sao sót lại"
```

## Phiếu duyệt

Quét xong thì sinh **phiếu duyệt** dạng bảng — mỗi dòng một chỉ tiêu, cột giá trị và nguồn điền sẵn, chừa cột cho người dùng chốt. Xuất Excel (skill `xlsx`) hoặc Markdown.

Sắp xếp theo mức độ quan trọng, không theo thứ tự trong hồ sơ: chỉ tiêu high-stakes lên đầu — cao trình thiết kế, lưu lượng tính toán, khối lượng chính, đơn giá, mã hiệu định mức. Người dùng mệt dần khi duyệt; đừng để những chỉ tiêu quyết định nằm cuối bảng.

## Không làm

- **Không đổi `status` sang `verified` thay người dùng.** Máy trích thì luôn là `unverified`.
- **Không tính toán, nội suy, quy đổi đơn vị** khi trích. Trích nguyên văn, tính toán là việc khác.
- **Không lấy số từ lớp trung gian** — data-sheet, bản tóm tắt, hồ sơ giai đoạn trước — mà không ghi rõ. Mỗi lớp trung gian là một chỗ để số liệu sai lệch mà không ai biết.
- **Không bỏ trường `quote`.** Khoá không có câu trích thì người duyệt phải mở lại PDF, và họ sẽ không mở.
