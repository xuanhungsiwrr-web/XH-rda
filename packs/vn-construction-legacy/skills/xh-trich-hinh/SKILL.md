---
name: xh-trich-hinh
description: |
  Trích hình, sơ đồ, mặt cắt từ PDF kỹ thuật và bản vẽ để đưa vào bản thảo báo cáo; lập danh mục hình; đọc nhanh hồ sơ scan nặng. Kích hoạt khi người dùng nhắc: trích hình từ PDF, cắt hình bản vẽ, lấy mặt cắt từ bản vẽ, danh mục hình, chèn hình vào báo cáo, đọc nhanh hồ sơ scan, docling, PDF sang Word để đọc. Không dùng để render báo cáo hoàn chỉnh — việc đó là của xh-docx; skill này chỉ chuẩn bị nguyên liệu hình cho bản thảo Markdown.
---

# XH_TrichHinh — chuẩn bị hình cho bản thảo

Skill này làm **nguyên liệu**, không làm sản phẩm. Đầu ra là ảnh trong thư mục và một danh mục `.md` — bản thảo chèn hình bằng cú pháp Markdown, còn số hiệu `Hình <chương>-<số>` do `render_report.py` sinh bằng trường STYLEREF + SEQ ở bước cuối.

## Ba việc, ba script

| Việc | Script | Ghi chú |
|---|---|---|
| Trích hình từ **PDF kỹ thuật, bản vẽ, hồ sơ scan** | `scripts/pdf-trich-hinh.py` | dùng `docling`, nhận diện được cả sơ đồ và caption |
| Tìm **chỗ nào trong bản thảo cần hình** | `scripts/detect-figures.py` | quét `10_content/*.md`, đối chiếu spec đề mục |
| Gắn **toạ độ ảnh hiện trường** vào lý trình | `scripts/geo-index-photos.py` | đọc EXIF GPS, xếp ảnh theo tuyến |

## Trích hình từ PDF

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/pdf-trich-hinh.py \
       "00_input/BanVe-PDF/CAU SONG DOC.pdf" \
       --ra 00_input/Hinh/ --tien-to CSD
```

Ra: `00_input/Hinh/CSD01.png`, `CSD02.png`… và `_danh-muc-hinh.md` — bảng ba cột, cột cuối là dòng Markdown chép thẳng vào bản thảo.

**Caption do script gợi ý phải sửa lại.** `docling` lấy caption theo vị trí chữ quanh hình, thường bắt nhầm dòng ghi chú của bản vẽ. Đọc hình rồi tự đặt tên.

## Đọc nhanh hồ sơ scan

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/pdf-trich-hinh.py hoso.pdf \
       --che-do word --ra /tmp/doc-nhanh.docx
```

Dùng khi cần nắm nội dung một hồ sơ scan nặng mà không muốn nạp cả file vào ngữ cảnh. **File ra là bản đọc, không phải bản thảo** — nó không đi qua khuôn, không có mục lục, caption gõ cứng. Đọc xong thì xoá.

## Cài đặt

`docling` **không có sẵn** trong môi trường. Thư viện này rất nặng (~1.5GB) vì kéo theo các mô hình nhận diện AI — chỉ cài khi thật sự cần thiết và phải báo trước cho người dùng về thời gian tải/dung lượng:

```bash
pip install docling --break-system-packages
```

Thiếu thư viện thì script thoát mã 3 và báo rõ, không chạy nửa vời.

## Không làm

- **Không dựng `.docx` để giao nộp.** Mọi bản giao đi qua `render_report.py` và khuôn `KhuonMau_NamQuoc.dotx`. Chế độ `word` chỉ để đọc.
- **Không gõ số hiệu hình bằng tay** vào bản thảo. Chèn thêm một hình là sai toàn bộ số phía sau.
- **Không tự chọn hình thay người dùng** khi bản vẽ có nhiều mặt cắt gần giống nhau — liệt kê ra rồi hỏi.
