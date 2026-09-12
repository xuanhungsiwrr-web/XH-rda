# xh-tuvan 0.7.0 — báo cáo portable

Bản triển khai nền tảng tại chỗ: nhạc trưởng theo host, giữ Markdown từng phần, revision/approval, kiểm coverage, fallback theo capability, nguồn web tách khỏi bản thảo, render Word thống nhất.

- [Tư vấn cho anh Hưng](docs/TU-VAN-TUY-BIEN-0.7.md)
- [Giao diện thao tác và quy trình](references/portable-workflow.md)
- [Cây thư mục và export](references/workspace-layout.md)
- [Audit trước triển khai](docs/ARCHITECTURE-AUDIT-2026-09-07.md)

## Cài vào môi trường mới

Dùng Python 3.11+; tạo môi trường riêng và cài requirements.txt. Bản local đã có .venv để kiểm thử, source ZIP không kèm môi trường này.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Claude Desktop: tham khảo config/claude-desktop.example.json, điều chỉnh đường dẫn máy mới và thêm server theo cách host hỗ trợ. Plugin .mcp.json dùng launcher chọn .venv nếu có. Đặt XH_PROJECTS_ROOT và XH_REPORT_LIBRARY trong host. Không thay toàn bộ cấu hình đang có chỉ để thêm một server.

ChatGPT/Codex local: dùng cùng CLI/MCP nếu host hỗ trợ. ChatGPT web cần cách kết nối remote/authenticated phù hợp; server hiện được đóng gói chỉ chạy stdio local. Chưa triển khai remote và chưa cài vào ứng dụng nào trong tác vụ này.

Provider: copy config/providers.json thành config/providers.local.json, chọn model ID thật, limits, giá/reserve và bật adapter sau khi kiểm tài khoản. API keys chỉ qua biến môi trường. host-session dùng model hiện tại của ứng dụng. Handoff tới Gemini/NotebookLM/xh-llm cần tool thật do host gọi. MintRouter/DeepSeek text adapter chưa bật khi chưa có key/model. Không coi Google AI Pro đồng nghĩa mọi Gemini API miễn phí.

## Dự án

CLI: python scripts/xh.py init --project <đường-dẫn-project-mới> --data <metadata.json>. Payload/gate đầy đủ nằm trong portable-workflow.md. MCP xh_project có cùng actions. 10 entrypoint cũ được giữ, thêm xh-humanize. Nguồn library snapshot gồm 9 file của người dùng; cần kiểm nguồn pháp lý trước sử dụng.

Dữ liệu vận hành nằm ở project, không ở plugin. Không di chuyển dự án cũ tự động. Nếu cần dùng dự án cũ, tạo project workspace mới, nhập các MD/facts có đối chiếu và phê duyệt lại; chưa có converter tự di trú toàn bộ state legacy.

## Phục hồi

ZIP nguyên bản nằm bên cạnh trong Backups/. Giải nén sang một folder riêng và chuyển cấu hình host về folder đó; giữ nguyên project mới cùng lịch sử, không chép dữ liệu cũ đè nó. Khi quay lại 0.7, tiếp tục từ workspace đã lưu. Đường dẫn source vẫn giữ tên xh-tuvan-0.6.0 để không phá tham chiếu; manifest hiện là 0.7.0.

## Giới hạn xác minh

Tests local kiểm state, approvals, conflict, dependency, fallback giả lập, source capture giả lập, MCP stdio thật và DOCX fixture. Không có live provider/Drive test hoặc visual QA bằng Word thật. Bản render luôn cần cập nhật TOC/fields và kiểm layout trước giao. Budget direct API là reservation accounting; host phải cộng phí MCP/Perplexity, dùng cap upstream để hạn chế tiền thật.
