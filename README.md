# xh-tuvan 0.8.0

Domain Orchestrator cho tư vấn xây dựng: nhận yêu cầu lập NCKT/ĐXCTĐT/KT-KT, tự phân việc nghiệp vụ, giữ nội dung tối thiểu, quản lý MD theo phần và học có kiểm soát.

Chỉ dùng capability MASTER, TECHNICAL_SPECIALIST, EXTRACTOR, REVIEWER, RESEARCHER. Global Control resolve model, ngân sách, fallback và worker. Plugin không gọi API model trực tiếp. Đổi Master giữa Claude và ChatGPT không đổi workflow. Kết nối Global Control thật là tích hợp riêng, chưa thực hiện trong gói này.

MCP stdio qua scripts/launch_mcp.py (ưu tiên .venv), gồm xh_project và xh_learning. Cấu hình host: XH_PROJECTS_ROOT, XH_REPORT_LIBRARY, XH_TUVAN_KNOWLEDGE_ROOT. Python dependencies ở requirements.txt. Phê duyệt learning dùng CLI operator; host kiểm quyền, plugin không cung cấp xác thực/remote server. Thư mục vẫn mang tên xh-tuvan-0.6.0 để giữ đường dẫn; manifest là 0.8.0.

- [Workflow, capability và action contract](references/domain-workflow.md)
- [Cơ chế học và cách anh Hưng sửa](references/shared-learning.md)
- [Sơ đồ kiến trúc và phân ranh](docs/ARCHITECTURE-0.8.md)
- [Bố trí dữ liệu](references/workspace-layout.md)
- [Kiểm chứng 0.8](docs/VALIDATION-0.8.md)

Tài liệu 0.7/pack legacy là lịch sử hoặc tham khảo chuyên ngành, không phải policy điều phối hiện hành. Không áp số dự án mẫu vào dự án thật. Kho approved ban đầu rỗng; không tạo phê duyệt giả.
