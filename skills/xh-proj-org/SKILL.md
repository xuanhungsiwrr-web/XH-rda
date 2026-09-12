---
name: xh-proj-org
description: "Tổ chức nguồn local, tạo project riêng và danh mục nguồn; giữ tách biệt plugin, thư viện và dự án."
---

# xh-proj-org

Plugin source ở AI_Config/PLUGINS; project work ở AI_Workspace/Projects; dùng references/workspace-layout.md. Chỉ index nguồn được chỉ định, không tự dời/xóa kho cũ. Khi cần sắp xếp, lập mapping và log trước, thực hiện trong phạm vi được duyệt. Giữ bản gốc và ID ổn định, không coi trùng tên là trùng nội dung.

Dùng ingest cho file đã copy/đồng bộ trong project; đăng ký cả nguồn binary và MD đã chuyển đổi. Nhật ký và kết quả nằm trong project, không ghi vào thư mục cài plugin. Quy ước ngành cũ ở pack legacy chỉ nạp nếu người dùng cần tổ chức theo cây đó.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
