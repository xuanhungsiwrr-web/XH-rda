---
name: xh-tuvan
description: "Điều phối báo cáo, chọn môi trường và xử lý yêu cầu nhiều bước; hỗ trợ viết toàn bộ, một phần hoặc cập nhật phần liên quan."
---

# xh-tuvan

Nhạc trưởng là model của phiên hiện tại: ưu tiên Opus khi Claude Desktop, Astra/Sol khi ChatGPT/Codex. Không tự nhận đã đổi model trong UI; không gọi API để mô phỏng lại nhạc trưởng. Khai environment và actual_model theo thông tin host thật.

Khởi tạo project riêng; metadata chưa rõ để null, tiếp tục các phần độc lập. Chọn tài liệu yêu cầu từ thư viện cấu hình, map toàn bộ yêu cầu vào outline hoặc ngoại lệ có lý do, trình người dùng duyệt. Định nghĩa dependency giữa section/fact/source/calculation. Dùng plan theo mode và max_parallel; host giao task cho công cụ/worker thực sự có sẵn. Chốt các giả định/số liệu dùng chung trước khi viết song song.

Sau mỗi task, lưu artifact với deps và revision; dùng QC theo risk. Provider lỗi thì exclude ứng viên đó và phân bổ lại theo capability, modality, budget. Không ép Gemini; không hạ chất lượng để vượt gate. Output thiếu dữ liệu là draft có TODO, không phải final. Việc chưa phụ thuộc dữ liệu thiếu vẫn tiếp tục. Chỉ assemble/render từ các section hiện hành không stale.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
