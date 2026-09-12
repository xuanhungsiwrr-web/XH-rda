---
name: xh-docx
description: |
  Render bản thảo Markdown thành báo cáo Word hoàn chỉnh bằng khuôn KhuonMau_NamQuoc.dotx, và kiểm định dạng bản render ra. Xử lý mục lục, danh mục hình/bảng, caption tự đánh số, header/footer, placeholder bìa. Kích hoạt khi người dùng nhắc: render báo cáo, xuất file Word, đổ nội dung vào khuôn, sửa định dạng báo cáo, mục lục không cập nhật, caption sai số, render_report, khuôn Word, .dotx, template báo cáo. Không dùng để sửa số liệu sai hay nội dung sai — nếu số trong file Word không khớp thực tế/_facts.yaml, đó là việc của xh-qc trước, xh-docx chỉ xử lý trình bày/định dạng/mục lục/caption sau khi nội dung đã đúng.
---

# XH_Docx — lớp trình bày

Đọc `references/template-map.yaml` trước khi làm bất cứ việc gì với Word. Nó là hợp đồng giữa khuôn và script: **chỉ được gọi styleId có trong đó**.

Khi cần thao tác sâu với OOXML (tracked changes, comment, validate XSD, render ra ảnh để soi), đọc skill `docx` của Anthropic — không viết lại phần đó.

## Render

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/render_report.py \
  --khuon   20-Khuon/KhuonMau_NamQuoc.dotx \
  --noidung 10_content/ \
  --info    _info.yaml \
  --facts   _facts.yaml \
  --hinh    00_input/Anh-HienTruong/ \
  --ra      20_output/BaoCao.docx
```

Script tự làm: mở `.dotx` (python-docx từ chối `.dotx` nên script đổi content-type trong bộ nhớ), dọn đoạn trống cuối khuôn, đổ nội dung theo style, thay `{{fact:}}` và `{{KEY}}`, chèn caption bằng trường Word, bật cờ `updateFields`.

Đọc kỹ phần cảnh báo cuối màn hình: placeholder chưa có giá trị, khoá `_facts.yaml` chưa duyệt, hình không tìm thấy. Mọi chỗ đó đều **tô vàng** trong file để nhìn thấy ngay khi mở.

## Cú pháp Markdown mà script hiểu

| Viết trong `.md` | Ra Word |
|---|---|
| `#` … `######` | Heading 1..6, numbering của khuôn tự chạy |
| đoạn văn thường | style thân bài |
| `- mục` · `* mục` | List Bullet |
| `1. mục` | List Number |
| `\| a \| b \|` | bảng TableGrid, hàng đầu TableHead |
| `Bảng: <chú thích>` ngay trên bảng | caption đặt **trên** bảng |
| `![chú thích](ten-file.jpg)` | hình + caption đặt **dưới** hình |
| `{{fact:ten_chi_tieu}}` | giá trị từ `_facts.yaml` |
| `{{TODO: việc}}` | tô vàng |
| `**đậm**` · `*nghiêng*` | đậm · nghiêng |

## Sau khi render — ba việc phải làm

**Mở bằng Word thật, không phải LibreOffice.** Chọn "Có" khi Word hỏi cập nhật trường, hoặc Ctrl+A rồi F9. Mục lục, danh mục hình/bảng và số trang chỉ build ở bước này.

> **Mẹo trên Windows:** Nếu người dùng đang chạy Windows và có cài sẵn MS Word, hãy đề xuất chạy script PowerShell dùng COM Object (`word.application`) để ép update TOC tự động, giúp họ không phải mở file thủ công.

**Kiểm caption.** Trường `STYLEREF 1 \s` cho ra số chương trong Word nhưng ra *tên* chương trong LibreOffice. Nếu Word cũng ra tên chương, chạy lại với `--caption lien-tuc` để đánh "Bảng 1, Bảng 2" liên tục.

**Chạy `qc-check.py` trên bản render** để chắc không còn placeholder sót và không có số chưa duyệt lọt vào.

## Khi khuôn có vấn đề

Kiểm tra khuôn bằng cách mở gói `.dotx` và đối chiếu `template-map.yaml`. Bốn thứ hay sai:

- **Cờ `updateFields` để `false`** → Word không hỏi cập nhật, người dùng phải F9 thủ công. Bật lên trong `word/settings.xml`.
- **Thiếu style** mà `template-map.yaml` khai → script rơi về `Normal`, định dạng sai âm thầm.
- **Run không có `rStyle`** → LibreOffice tự bọc vào "Subtle Reference", chữ hoá cam và gạch chân.
- **`.rels` sinh bằng lxml có tiền tố `ns0:`** → LibreOffice từ chối mở file dù XML hợp lệ. Ép `nsmap={None: PKG}`.

## Cấm kỵ

Không ghép file `.docx`. Không để AI viết trực tiếp XML của Word. Không dùng `docx-js` để tạo mới. Không tạo bìa — bìa là file riêng.
