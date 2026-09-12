# Validation 0.9

Kết quả chốt source ngày 2026-09-10:

- `compileall`: PASS cho `scripts/` và `tests/`.
- `unittest discover`: 37/37 PASS bằng Python trong môi trường MCP v1 tương thích của bản 0.8.
- MCP stdio integration: PASS (list tools và gọi project/learning thật qua stdio).
- JSON manifests/config: PASS; inventory 11/11 `SKILL.md`: PASS; `git diff --check`: PASS.

- Toàn bộ unittest cũ phải tiếp tục đạt sau khi fixture dùng layout API.
- Test layout/migration: init v3, open legacy, missing DB fail, dry-run không ghi, apply/verify/retry/rollback, bảo toàn revision/approval/blob/dependency và lineage khi rewrite path.
- Test delivery: SHA-256 output=feedback, partial failure resume, feedback sửa tay không overwrite, release collision fail, R01/R02 ghép đúng, baseline bị đổi fail, import lặp không trùng.
- Test learning adapter: export projection, stage import không chuyển approval, từ chối live SQLite ở Drive sync path.
- Manifest/skills validation, compileall và git diff check phải đạt.

Không được suy từ test local rằng remote MCP, cloud persistence, deployment hoặc visual QA Word đã được xác minh.
