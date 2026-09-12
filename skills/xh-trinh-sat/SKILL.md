---
name: xh-trinh-sat
description: "Tìm nguồn công khai, cào trang web và lưu evidence tiết kiệm context; hỗ trợ Exa hoặc công cụ tìm kiếm khả dụng."
---

# xh-trinh-sat

Xác định câu hỏi còn thiếu theo dự án, không ép năm nhóm ngành thủy lợi. Search trả URL/snippet; chỉ scrape trang phù hợp. Dùng scripts/mcp_project_scraper.py để lưu raw HTML và MD dưới research, trả ID/size thay toàn văn. Dùng retrieve chọn đoạn rồi giao model đủ capability trích structured evidence.

Không đưa trang web vào drafts/10_content. Cache theo nguồn/revision, lưu ngày truy cập và URL; đọc lại khi cần xác minh thay đổi. Chất lượng extraction phải kiểm coverage; không nén mất bảng/đơn vị/câu trích. Pháp lý dùng mcp_perplexity_search.py nếu sẵn key/quyền phí, không mặc định recency year; kiểm văn bản gốc, sửa đổi/bãi bỏ/phạm vi trước duyệt. Nếu search lỗi dùng adapter khác có search, không dùng trí nhớ model như kết quả tìm kiếm. Ghi usage của cả scraper-worker-reviewer, không chỉ nhạc trưởng.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
