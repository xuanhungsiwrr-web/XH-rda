---
name: xh-evidence
description: "Nhập và đối chiếu dữ liệu có nguồn, cho phép bổ sung dần; không viết thuyết minh."
---

# xh-evidence

Dùng nguồn theo source ID + hash, giữ bản gốc và bản MD trích xuất có deps. Đọc bảng/trang cần thiết. PDF scan/bản vẽ cần adapter document/vision hoặc OCR trước; DeepSeek text chỉ dùng sau khi đã có văn bản phù hợp. NotebookLM thủ công là lựa chọn, không bắt buộc và không giả định API miễn phí.

Mỗi fact có value, unit, source, quote, data_type PROJECT/REFERENCE/LEGAL/MISSING; REFERENCE thêm nguon_du_an. `fact` chỉ tạo unverified/conflict; người dùng mới resolve-fact. Không ghi đè conflict hoặc tự kế thừa verified từ dự án khác. Thiếu khảo sát cho phép tạo danh sách TODO và viết phần không phụ thuộc; final vẫn bị chặn. Tính toán dùng artifact có version, công thức/giả định/đơn vị/input refs; giá trị dẫn xuất phải đưa qua fact approval.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
