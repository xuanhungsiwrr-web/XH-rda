---
name: xh-outline
description: "Chọn yêu cầu tối thiểu của loại báo cáo và lập đề cương có đối chiếu; không viết nội dung báo cáo."
---

# xh-outline

Dùng library discovery theo report_type và design_stage. Mặc định đọc thư viện được cấu hình XH_REPORT_LIBRARY; trên máy anh là AI_Workspace/NoiDung_CacBaoCao. Chọn đầy đủ file liên quan, gồm khung nội dung chung và khung ngành khi áp dụng. requirements lưu snapshot và giữ mọi đoạn nguồn.

Lập section IDs ổn định, title, requirements IDs, depends_on, risk. Có thể bổ sung mục con; không bỏ yêu cầu tối thiểu. Nội dung điều kiện áp dụng chưa rõ phải nêu để duyệt, không tự loại. Bảng coverage phải kiểm tra nội dung tối thiểu, không chỉ tên heading. Các file thư viện có thể là bản tổng hợp chưa đủ nguồn: legal verification là bước riêng. Không yêu cầu phải có ba báo cáo mẫu mới lập được loại báo cáo mới. Có thể dùng seed legacy khi phù hợp; không dùng số dự án mẫu.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
