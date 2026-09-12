# xh-tuvan 0.9.2

Domain Orchestrator cho tư vấn xây dựng: nhận yêu cầu lập NCKT/ĐXCTĐT/KT-KT, tự phân việc nghiệp vụ, giữ nội dung tối thiểu, quản lý MD theo phần và học có kiểm soát.

Chỉ dùng capability MASTER, TECHNICAL_SPECIALIST, EXTRACTOR, REVIEWER, RESEARCHER. Global Control resolve model, ngân sách, fallback và worker. Plugin không gọi API model trực tiếp. Đổi Master giữa Claude và ChatGPT không đổi workflow. Bridge process protocol 1.1 tại `bridge/wrapper.py` hỗ trợ execute tương thích 1.0 và plugin-owned pause/resume handoff; nghiệm thu Hermes/Telegram vẫn thuộc Global Control. Kết nối Global Control thật là tích hợp riêng, chưa thực hiện trong gói này.

MCP stdio qua `scripts/launch_mcp.py`, gồm `xh_project` và `xh_learning`. Cấu hình host dùng filesystem persistence thật cho `XH_PROJECTS_ROOT` và `XH_TUVAN_KNOWLEDGE_ROOT`; folder ID/URL Drive chỉ là định danh nguồn, không phải đường dẫn chạy code hay SQLite. Phê duyệt learning vẫn ở CLI operator. Bản 0.9.2 này bổ sung skill `xh-caotrinh-ke` cho tính cao độ đỉnh kè; bản 0.9.0 này là source phát triển tách biệt; bản 0.8.0 đang chạy không bị thay đổi.

- [Workflow, capability và action contract](references/domain-workflow.md)
- [Cơ chế học và cách anh Hưng sửa](references/shared-learning.md)
- [Sơ đồ kiến trúc và phân ranh](docs/ARCHITECTURE-0.9.md)
- [Bố trí dữ liệu](references/workspace-layout.md)
- [Migration và rollback](docs/MIGRATION-0.9.md)
- [Cloud readiness](docs/CLOUD-READINESS-0.9.md)
- [Kiểm chứng 0.9](docs/VALIDATION-0.9.md)

Tài liệu 0.7/pack legacy là lịch sử hoặc tham khảo chuyên ngành, không phải policy điều phối hiện hành. Không áp số dự án mẫu vào dự án thật. Kho approved ban đầu rỗng; không tạo phê duyệt giả.
