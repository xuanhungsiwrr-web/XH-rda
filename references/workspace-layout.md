# Tách source và hồ sơ

Plugin source ở AI_Config/PLUGINS; source gồm skills, scripts, references và packs chuyên ngành. Mỗi project/report ở AI_Workspace/Projects có sources, research, specs, drafts, reviews, edits, calculations, templates, outputs. Facts, metadata, decisions, workflow state, KB snapshot, postmortem ở project/.ai/. Project.json còn bản metadata tương thích renderer; không có API budget. .xh chỉ lưu revisions/blobs nội bộ của hồ sơ.

Shared knowledge đặt qua XH_TUVAN_KNOWLEDGE_ROOT; mặc định plugin root. Cần bốn thư mục knowledge/approved,candidates,rejected,deprecated và learning/ với ledger JSONL, changelog, evaluation_cases, metrics, change_requests, registry.sqlite. Hai host dùng cùng shared root; sao lưu toàn bộ, không chỉ approved/. Không sửa projection JSON bằng tay. Không chạy hai bản SQLite đồng thời qua Drive sync; đồng bộ nhiều máy thuộc hạ tầng.

Xem [kiến trúc 0.8](../docs/ARCHITECTURE-0.8.md) và [quy trình học](shared-learning.md). Project schema 1 có migrate-domain giữ lịch sử; current facts chuyển .ai cần duyệt lại. Chỉ export file đã register. Không tự di chuyển dữ liệu cũ của người dùng.
