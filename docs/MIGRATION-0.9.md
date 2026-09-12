# Migration workspace layout 2 → 3

Không chạy trực tiếp trên dữ liệu thật trước khi có backup ngoài hệ thống và cửa sổ dừng writer. Các lệnh dưới đây dùng `scripts/xh_migration.py`; `dry-run` và `preflight` không ghi.

```powershell
python scripts/xh_migration.py dry-run --project <workspace>
python scripts/xh_migration.py apply --project <workspace>
python scripts/xh_migration.py verify --project <workspace>
python scripts/xh_migration.py rollback --project <workspace>
```

Preflight yêu cầu `project.json`, `.xh/state.sqlite`, đủ revisions/heads/approvals và blobs/head files đúng hash. Thiếu DB hoặc external edit làm fail rõ ràng. Dry-run trả toàn bộ mapping; `sources` không có provenance vào legacy-unclassified, `calculations` vào legacy-out-of-scope.

Apply tạo snapshot ở thư mục sibling `.xh-migration-snapshots`, journal có migration ID, rồi sao chép dữ liệu sang layout 3. Không xóa nguồn. DB v3 giữ revision IDs, approvals, dependency revision IDs và blobs. JSON hiện hành có path cũ nhận revision mới với `lineage_revision`; approval không tự đi theo revision mới. `project.json` được đổi cuối cùng sau khi DB/files đã durable.

Apply/resume chạy lại là idempotent khi layout 3 đã verify. Xung đột destination khác hash bị từ chối. Rollback yêu cầu snapshot và DB legacy còn nguyên; nó phục hồi `project.json` layout 2 và giữ expansion v3 để điều tra, không xóa dữ liệu.

Sau migration cần kiểm report representative, renderer, source refs, manifests, stale descendants và approvals cần duyệt lại. Contract/xóa cây legacy không thuộc release này.
