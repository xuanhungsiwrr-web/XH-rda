# Cloud readiness 0.9

Đã hỗ trợ ở code:

- Path semantics độc lập host, layout versioned và project-relative.
- Workspace mới/legacy, migration/rollback và checkpoint ZIP có SQLite backup.
- Source identity có thể lưu Drive ID/URL/revision/hash mà không coi Drive là filesystem.
- Stdio MCP cho executor/local host; capability packets không chứa provider/model/budget.
- Operational knowledge tách projection export/import; từ chối live SQLite ở đường dẫn Drive sync phổ biến.

Cần hạ tầng bên ngoài plugin:

- Registry xác nhận GitHub repository, release và deployment; hiện source này chưa có Git remote.
- Cloud executor checkout một canonical source, không sửa song song hai bản.
- Persistent filesystem/database service với one-writer/locking và backup; không dùng Drive sync cho live SQLite.
- Public HTTPS MCP hoặc Secure MCP Tunnel, authentication và in-product installation test cho ChatGPT Work. Local stdio không chứng minh remote integration.
- Controlled publisher để đưa approved versioned knowledge sang `03_Knowledge/xh-tuvan/published`.

Không triển khai trong 0.9.0: Global Control, Hermes, remote endpoint, credentials, deployment, source/data move trên Drive hoặc quản lý tính toán/dự toán/hồ sơ nộp chủ đầu tư.
