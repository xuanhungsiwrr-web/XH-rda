---
name: xh-trich-hinh
description: "Trích hình từ PDF, xử lý ảnh hiện trường và chuẩn bị media có nguồn; không xuất báo cáo hoàn chỉnh."
---

# xh-trich-hinh

pdf-trich-hinh.py cần docling; detect-figures.py dò vùng hình PDF (không quét spec Markdown); geo-index-photos.py dùng EXIF/KMZ. Kiểm --help và dependency trước chạy. Không cài model OCR nặng nếu chưa cần.

Lưu hình dưới sources/media hoặc calculations cùng source ID, page/bbox, caption candidate. Xem lại caption, số và đơn vị; hỏi chọn khi nhiều mặt cắt không phân biệt được. Register artifact và deps để thay nguồn làm phần liên quan stale. Markdown dùng đường dẫn tương đối từ project root; renderer giữ numbering thống nhất.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
