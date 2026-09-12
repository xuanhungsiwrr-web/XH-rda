---
name: xh-tuvan
description: |
  Điều phối viết hồ sơ tư vấn thiết kế xây dựng Việt Nam — thuỷ lợi, đê điều, kè bờ sông, giao thông, hạ tầng. Nhận yêu cầu viết báo cáo, xác định loại báo cáo và giai đoạn, rồi gọi lần lượt các skill con xh-outline, xh-viet, xh-qc, xh-docx; điều phối cả xh-proj-org (tổ chức thư mục hồ sơ), xh-drive (hồ sơ nằm trên Google Drive), xh-evidence (dựng kho số _facts.yaml), xh-trich-hinh (chuẩn bị hình từ PDF) và xh-trinh-sat (tự tìm thông tin công khai liên quan dự án qua Exa). Kích hoạt khi người dùng nhắc: XH_TuVan, viết báo cáo, BCĐXCTĐT, BCNCKT, FS, BCKTKT, thuyết minh thiết kế, TKKT, TKBVTC, kè bờ sông, đê điều, cầu cống, công trình thuỷ lợi, hoặc khi mở thư mục XuongBaoCao. Khi một câu lệnh gộp từ hai bước trở lên (vừa ra đề mục vừa viết nội dung, hoặc vừa kiểm vừa render), xh-tuvan nhận yêu cầu này để điều phối tuần tự đúng skill con, tránh một skill con tự ý làm luôn việc của skill khác.
---

# XH_TuVan — điều phối

Skill này **không viết nội dung**. Nó xác định đang ở bước nào rồi giao cho skill con.
**Nếu người dùng yêu cầu viết nội dung trực tiếp: chuyển sang `xh-viet`, KHÔNG tự viết trong ngữ cảnh này.**

Đọc `references/nguyen-tac.md` và `references/kien-truc-3-lop.md` ngay khi kích hoạt. Chín nguyên tắc ở đó áp dụng cho mọi bước. Khi đụng đến căn cứ pháp lý, đọc thêm `references/phap-ly-2026-07-01.md`.

## Xác định bước đang ở

Kiểm tra thư mục dự án theo thứ tự, dừng ở bước đầu tiên chưa xong:

| Kiểm tra | Chưa có thì | Skill phụ trách |
|---|---|---|
| `_info.yaml` và cây thư mục dự án | khởi tạo dự án, hỏi tên dự án / địa điểm / giai đoạn | (làm trực tiếp, xem dưới) |
| `_facts.yaml` có khoá `status: verified` | dựng `_facts.yaml` từ `00_input/`, sinh phiếu duyệt cho người dùng | **xh-evidence** |
| `specs/<LoaiBC>.yaml` có `trang_thai: da_duyet` | sinh bản đặc tả đề mục | **xh-outline** |
| `10_content/*.md` | viết nội dung từng đề mục | **xh-viet** |
| bản thảo đã rà | rà soát trước khi render | **xh-qc** |
| `20_output/*.docx` | render vào khuôn | **xh-docx** |

## Năm skill phục vụ, gọi khi cần — không nằm trong luồng chính

| Khi nào | Skill | Việc |
|---|---|---|
| Thư mục hồ sơ dự án lộn xộn, cần sắp xếp; cần tạo cây thư mục dự án mới cho cả công ty. *(Nếu người dùng nói "sắp xếp hồ sơ" chung chung, mặc định là ổ đĩa — dùng skill này)* | **xh-proj-org** | tổ chức theo hệ `10.PhapLy/ 20.DauThau/ 30.KhaoSat/…`, đặt tên file, lập danh mục Excel có hyperlink |
| **Hồ sơ nằm trên Google Drive, không có trên ổ đĩa** — chỉ dùng khi người dùng nói rõ "trên Drive" | **xh-drive** | quét, phân loại, tạo folder và di chuyển file ngay trên Drive; đọc nội dung để dựng kho số. Không phải chép về xưởng nữa |
| Cần dựng hoặc bổ sung `_facts.yaml`; hồ sơ khảo sát quá nặng để đọc thẳng | **xh-evidence** | quét theo danh mục chỉ tiêu, sáu trường mỗi khoá, sinh phiếu duyệt; hồ sơ nặng thì sinh phiếu yêu cầu cho NotebookLM (thủ công) thay vì gọi API |
| Cần hình, sơ đồ, mặt cắt từ bản vẽ PDF để chèn vào bản thảo | **xh-trich-hinh** | trích ảnh + danh mục hình; đọc nhanh hồ sơ scan nặng |
| Cần thông tin công khai liên quan dự án trước khi viết (quy hoạch, sạt lở, mực nước BĐ3, dự án lân cận) | **xh-trinh-sat** | tìm qua Exa (MCP), ghi có nguồn/URL vào `00_input/90.TrinhSat-Exa/`; cần connector Exa đã kết nối |

Năm skill này **không sinh nội dung báo cáo**. Đừng để chúng thay `xh-viet`.


Không nhảy bước. Spec chưa được người dùng duyệt thì **không viết**; số chưa `verified` thì **không dùng cho số high-stakes**.

## Khởi tạo dự án mới

Tạo cây thư mục:

```
<YYMM>_<DiaDanh>_<TenNgan>_<GiaiDoan>/
├── _info.yaml  _facts.yaml  _references-scope.md
├── 00_input/  10_content/  20_output/
```

`_info.yaml` chứa các khoá viết HOA khớp đúng placeholder `{{KEY}}` trong khuôn: `TEN_DU_AN`, `DIA_DIEM`, `LOAI_BAO_CAO`, `GIAI_DOAN`, `LIEN_DANH`, `DIA_DANH_THANG_NAM`. Chỗ chưa biết ghi `{{TODO: ...}}`, tuyệt đối không dùng dấu `…` hay `.../`.

Địa danh Cà Mau đã bỏ cấp huyện — ghi "xã …, tỉnh Cà Mau".

## Dựng `_facts.yaml` — giao cho `xh-evidence`

Tóm tắt để biết đường điều phối; chi tiết ở `skills/xh-evidence/SKILL.md`.

**Quét theo danh mục, không quét tự do.** Bảo mô hình "trích mọi số liệu" sẽ trả về hàng nghìn con số vô dụng. Lấy danh mục chỉ tiêu từ `scripts/qc-rules.yaml` (14 chỉ tiêu cho kè/đê, mở rộng theo loại công trình) rồi đi tìm đúng những chỉ tiêu đó.

Mỗi khoá ghi năm trường: `value` · `unit` · `source` (file#trang) · `quote` (câu trích nguyên văn) · `status`.

Trường `quote` quyết định tốc độ duyệt: người dùng đọc câu trích là biết ngay có hiểu đúng ngữ cảnh không, khỏi mở lại PDF gốc.

Cùng một khoá mà hai nguồn cho hai giá trị → `status: conflict`, liệt kê `ung_vien` kèm nguồn, **không tự chọn** (Nguyên tắc 7).

Sau khi quét xong, sinh **phiếu duyệt** dạng bảng (Excel hoặc Markdown) mỗi dòng một chỉ tiêu, cột ứng viên và nguồn điền sẵn, chừa cột cho người dùng chốt. Duyệt 80 chỉ tiêu mất khoảng 30–40 phút.

## Luồng đầy đủ khi viết một chương

```
xh-trinh-sat  → thông tin công khai liên quan dự án (nếu cần, trước khi viết)
xh-outline    → spec đề mục (người dùng duyệt)
xh-trich-hinh → hình + danh mục hình (nếu chương có hình bắt buộc)
   ┌─────────── LẶP CHO TỪNG CHƯƠNG, KHÔNG VIẾT GỘP ───────────┐
   │ xh-viet   → 10_content/C0x.md  (MỘT chương)               │
   │ qc-check.py → Tầng 1, luật cứng                           │
   │ Gemini_QC → Tầng 2 ngoài Claude   ← CỔNG BẮT BUỘC         │
   │ xh-viet   → sửa theo phản hồi, chạy lại Gemini_QC         │
   │            ↺ lặp tới khi Gemini trả OK                    │
   └───────────────────────────────────────────────────────────┘
xh-qc         → Tầng 3, agent năm lăng kính, chạy trên TOÀN BỘ bản thảo
xh-viet       → sửa theo danh sách
xh-docx       → render vào khuôn
```

## ⛔ CỔNG GEMINI_QC — quy tắc bắt buộc từ v0.4.0

**Viết xong một chương thì phải chạy `Gemini_QC` trên chương đó. Chưa nhận phản hồi ĐẠT thì
KHÔNG được viết chương tiếp theo.**

Đây là quy tắc anh Hưng chốt ngày 26/08/2026, sau khi bản v2 viết một mạch 10 chương rồi mới
kiểm — kết quả là lỗi kết cấu nghiêm trọng (mô tả sai quan hệ cầu–kè) lan sang bốn chương và
kéo theo cả lập luận so sánh phương án. Nếu kiểm ngay sau Chương I thì lỗi đã dừng ở một chương.

Cách gọi:

```
mcp__remote-devices__gemini_qc__gemini_quality_control(
    report_text = <toàn văn chương vừa viết, kèm các số liệu neo từ _facts.yaml>,
    criteria    = <tiêu chí rà cho đúng nhóm đề mục — xem bảng dưới>
)
```

Tiêu chí gửi kèm phải nêu rõ: *"Đóng vai chuyên gia thẩm định độc lập của Sở Xây dựng, chỉ ra
lỗi cụ thể kèm trích dẫn, không khen chung chung."* Sáu nhóm luôn hỏi: vai viết và văn phong ·
mâu thuẫn số liệu · logic kỹ thuật · thiếu nội dung bắt buộc · tiêu chuẩn áp dụng · rủi ro bị
thẩm định trả hồ sơ.

Vì Gemini không thấy các chương khác, phải **dán kèm số liệu neo** (chiều dài, cấp công trình,
tổng mức đầu tư, các cao độ chính) vào đầu `report_text`, nếu không nó không bắt được mâu thuẫn
chéo chương.

**Coi là ĐẠT khi** Gemini không còn lỗi nhóm "nghiêm trọng" và không còn lỗi vai viết. Lỗi mức
cảnh báo được phép ghi nhận rồi đi tiếp, nhưng phải liệt kê lại ở bước `xh-qc` cuối.

**Khi Gemini_QC không gọi được** (chưa cài, hết quota, lỗi API): dừng lại và báo người dùng —
không tự bỏ qua cổng. Trong lúc chờ, chạy tạm agent `xh-qc` cho riêng chương đó để vẫn có góc
nhìn thứ hai, và ghi rõ trong báo cáo là đã dùng phương án thay thế.

Nếu tool trả lỗi `404 ... model ... no longer available`, đó là tên model trong code đã cũ —
báo người dùng cập nhật, kèm tên model mới mà lỗi gợi ý. Cùng lỗi này có thể xuất hiện ở
`scripts/evidence-gemini.py` (biến `XH_GEMINI_MODEL`).

Gọi `xh-qc` **bằng công cụ Agent**, không tự kiểm bài của chính mình. Agent tự kiểm luôn dễ dãi
vì vẫn giữ nguyên giả định lúc viết. Điều này đúng với cả Gemini: giá trị của nó nằm ở chỗ nó
không biết ta đã nghĩ gì lúc viết.

## Vòng học từ bản người dùng sửa

Mỗi lần người dùng sửa bản thảo là một tín hiệu vàng, và hiện nay nó đang bị vứt đi. Cách anh
cần tô màu, bật Track Changes, và ghi Comment khi xóa cả đoạn — xem `references/huong-dan-sua.md`
(gửi hoặc trỏ người dùng đọc file này trước khi họ mở bản `..._dasua.docx`). Nhắc người dùng lưu song song:

```
60-VanPhong/lich-su-sua/C2-1_claude.md
60-VanPhong/lich-su-sua/C2-1_dasua.md
```

Rồi chạy `scripts/learn-from-edits.py --dir lich-su-sua/` để rút quy tắc, ghi vào Mục F và G của `references/ho-so-van-phong.md`.

Chỉ số theo dõi: **tỉ lệ câu giữ nguyên**. Mục tiêu 40% → 65% → 80% qua năm báo cáo. Không tăng sau ba báo cáo nghĩa là hồ sơ văn phong đang ghi sai thứ — xem lại chứ đừng viết thêm quy tắc.

## Không tự động làm

Xem đầy đủ ở `references/nguyen-tac.md`. Hai điều hay bị vi phạm nhất:

- **Không ghép file `.docx`.** Chỉ render một lần từ nhiều `.md`.
- **Không tạo bìa.** Bìa là file riêng do người dùng làm.
