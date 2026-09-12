---
name: xh-qc
description: "Kiểm số liệu, nguồn, logic, coverage và mâu thuẫn trước duyệt; QC nội dung đi trước render."
---

# xh-qc

Chạy luật tất định trước; chỉ dùng rules pack phù hợp (bộ qc-check legacy còn default ngành thủy lợi, không dùng để chứng nhận loại báo cáo khác). Kiểm mọi fact có source/quote, trạng thái/approval và revision. Review coverage đối chiếu cả yêu cầu tối thiểu, điều kiện áp dụng và nội dung đã trả lời.

Task rủi ro cao cần reviewer độc lập qua adapter khả dụng; model nào đạt capability đều dùng được. Review chéo section theo dependency và claim index, mở rộng toàn văn khi cần. Trả findings severity critical/warning, quote, vấn đề, việc cần làm. Không báo lỗi nếu không có căn cứ; không buộc phải tìm ra lỗi. `review` lưu findings theo revision và coverage_checked. Review không đồng nghĩa user approve. Hết budget/lần sửa thì checkpoint, không bỏ gate.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
