# Changelog 0.9.0

## Workspace và migration

- Thêm layout v3 tập trung cho Registry, Sources, Templates, Working, Outputs và Feedback.
- Mở workspace 0.8 ở chế độ tương thích; không tự tạo DB rỗng khi state legacy bị thiếu.
- Thêm preflight, dry-run, apply, verify, resume và rollback có snapshot/journal.
- Migration theo expand/copy, giữ nguyên nguồn legacy, blob, revision, dependency và approval; rewrite path tạo lineage revision mới, không sao chép approval sang revision mới.
- Nguồn không đủ provenance và thư mục calculations cũ được giữ ở vùng legacy riêng, không đoán phân loại và không xóa.

## Giao nhận và feedback

- Final release yêu cầu `release_id` và tạo cặp `40_Outputs/*.docx` + `50_Feedback/*_XHedited.docx` byte-identical.
- Baseline không ghi đè; retry tiếp tục từ partial state và giữ nguyên feedback đã sửa.
- Import feedback khóa đúng release/revision/hash, chống nhập trùng, phân tích paragraph/table DOCX và không tự tạo bài học.

## Shared learning và cloud readiness

- Operational SQLite bắt buộc nằm trên filesystem/volume bền vững do host cấu hình, không nằm trong thư mục Drive sync.
- Projection export là read-only; stage import kiểm hash và không chuyển approval.
- Provider/model/budget/retry vẫn thuộc Global Control; plugin không nhận thêm trách nhiệm này.

## Tương thích và kiểm chứng

- Cập nhật Codex/Claude manifests lên 0.9.0, CLI/MCP actions, tài liệu layout/workflow và các skill điều phối/render.
- 37 regression/acceptance tests PASS; xem `VALIDATION-0.9.md`.
- Chưa deploy, publish, migrate dữ liệu thật hoặc xác minh cloud/Word visual layout.
