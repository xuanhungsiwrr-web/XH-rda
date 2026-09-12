---
name: xh-viet
description: "Viết hoặc sửa Markdown của một phần báo cáo theo đề cương đã duyệt, giữ nguyên phần độc lập."
---

# xh-viet

Nhận TaskPacket: section spec, đúng nguồn/facts/attachments, style profile và tiêu chí. Chỉ viết section được giao. Kết quả dùng {{fact:key}} cho chỉ tiêu dự án và {{TODO: mô tả}} khi thiếu; không suy ra số từ dự án tham khảo. Gắn mọi source/fact/calculation đã dùng vào deps, kể cả số liệu được diễn giải bằng lời.

Chế độ sửa: đọc bản hiện hành, giữ phần người dùng đã sửa, lưu với expected revision để tránh đè bản mới. Không tự cập nhật các section khác; trả impact cho nhạc trưởng. Không tự điều phối Gemini hay lặp vô hạn. Humanizer chỉ chạy sau nội dung, giữ số/căn cứ/cấu trúc. Mỗi model ghi file riêng, không cùng sửa facts hay report.md. Outline ổn định cho phép nhiều section độc lập viết song song.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
