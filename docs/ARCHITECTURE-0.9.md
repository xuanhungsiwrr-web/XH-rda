# xh-tuvan 0.9.0 — workspace lifecycle

xh-tuvan vẫn là Domain Orchestrator. Global Control sở hữu model/provider/routing/budget/session/worker và state mechanics toàn cục. Hermes là hạ tầng. Plugin chỉ sở hữu nghiệp vụ báo cáo, nguồn, QA, render, delivery pair và controlled learning.

`xh_layout.py` là nguồn duy nhất của path semantics và `layout_version=3`. `Project` nhận dạng layout 2/3, mở đúng SQLite hiện hữu và từ chối tạo DB rỗng khi `project.json` đã có nhưng state DB mất. CLI, MCP, domain, renderer, delivery, migration và learning cùng gọi lớp này.

Migration dùng expand–migrate–verify: snapshot DB/config; sao chép blobs/current heads; tạo DB v3; cập nhật revision paths; tạo revision mới có lineage khi JSON hiện hành chứa path cũ; chuyển `project.json` cuối cùng. DB/file legacy không bị xóa, nên rollback chỉ kích hoạt lại layout 2. Contract/cleanup phá hủy là giai đoạn khác, không nằm trong 0.9.0.

Renderer tạo preview dưới `30_Working/.xh/render`. Final render yêu cầu `release_id`, sau đó delivery service tạo hai file độc quyền trong Outputs/Feedback và ghi pair transaction state. Retry sau partial failure dùng immutable baseline. Feedback import kiểm baseline trước, khóa đúng pair/revision/hash, phân tích DOCX theo paragraph/table và không coi XML thô là bài học.

Learning giữ chuỗi candidate → validation → operator approval → change request → regression → release authorization. Operational SQLite không chạy trên Drive sync. `xh_knowledge_transfer.py` chỉ xuất projection hoặc stage import; nó không chuyển approval hoặc tự sửa skill.

Cloud executor cần checkout source từ GitHub khi có registry, filesystem persistence thật cho workspace/operational DB, và backend HTTPS MCP riêng nếu dùng ChatGPT Work. Stdio chỉ là local transport. Plugin không tự triển khai endpoint hoặc Global Control.
