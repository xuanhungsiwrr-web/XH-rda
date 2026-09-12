---
name: xh-docx
description: "Render Markdown thành Word theo template được chọn; preview từng phần hoặc xuất toàn báo cáo thống nhất."
---

# xh-docx

Đọc template manifest trước. Chọn theo tổ chức, loại báo cáo, bước thiết kế, ngôn ngữ; không chọn chỉ theo tên file. Snapshot template + style contract trong project/templates. Mọi style bắt buộc phải tồn tại. Dùng `render` qua runtime hoặc render_report.py --template-map.

Preview một section để rà nhanh được phép. Bản giao cuối luôn render một lần từ các MD hiện hành theo thứ tự outline, không ghép các DOCX đã render riêng. Dùng MD đã có, không gọi AI viết lại chỉ để render. Heading/numbering/caption/TOC do cùng template quản lý. File tính toán Excel/Word lưu riêng; đưa bảng/kết quả hoặc summary Markdown đã duyệt vào report.

Sau render cập nhật fields bằng Word, kiểm mục lục/caption/layout thực tế. Runtime chỉ ghi needs-word-layout-check; chưa có Word thì nói rõ chưa xác minh dàn trang. Để lại TODO/thiếu facts có thể tạo draft, không chứng nhận final.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
