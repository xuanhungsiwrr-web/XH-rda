# Shared Learning 0.9

Hai Master đặt `XH_TUVAN_KNOWLEDGE_ROOT` tới cùng một thư mục bền vững trên filesystem cục bộ/volume được khóa, tuyệt đối không dùng thư mục Google Drive đang sync cho SQLite hoạt động. Đọc snapshot approved + `30_Working/.ai/STATE.md`, `DECISIONS.md`, `PROJECT_FACTS.json` khi vào việc. Snapshot dự án giữ plugin_version, KB ID, rule/hash/evidence/phê duyệt. Kho ban đầu rỗng là hợp lệ; không giả lập bài học đã được anh Hưng duyệt.

Phân loại trước lưu: facts/đơn vị/phương án riêng vào `30_Working/.ai/`; quy tắc viết, extraction, QA, pháp lý/kỹ thuật tái sử dụng thành domain candidate; hiệu năng, token, giá, provider vào Global Control. REVIEWER kiểm scope và thông tin riêng, không chỉ tin nhãn tác giả.

```text
candidate → validation → operator approval → approved knowledge
                                             ↓ nếu cần sửa skill
                                       change request
                                             ↓
                                sửa có kiểm soát → test cũ + mới
                                             ↓
                                  duyệt phát hành → version mới
```

MCP `xh_learning`: candidate, validate, reject, snapshot, change-request, evaluate. Không có approve/release cho model. Candidate cần title, rule, evidence(reference,quote), author, category, risk, cases; scope=domain. Case có input, expected_findings, explanation. technical/legal tự mang high risk.

Validate cần reviewer khác author, evidence_checked=true, reusable=true, conflicts_checked=true và rationale. Reviewer thật sự kiểm nguồn, phạm vi, ngoại lệ, xung đột approved/deprecated. Pháp lý/kỹ thuật cần nguồn chuyên ngành gốc. Kiểm tự động hiện hỗ trợ missing_source, conflicting_fact, unlabelled_assumption, unverified_legal; không chứng minh đầy đủ kết luận kỹ thuật/văn phong. Ca mới có thể FAIL baseline; ghi lỗi đó để sửa qua CR, không đổi expected chỉ để PASS. Release phải PASS toàn bộ ca cũ/mới. Giữ cases của rule deprecated để không mất lịch sử; thay kỳ vọng sai cần CR và lý do.

Operator dùng `scripts/learning_admin.py approve --data approval.json`: lesson_id, actor, approval_reference từ quyết định thật, expected_hash trùng content_hash. Không tự tạo lời duyệt hoặc dùng author/reviewer làm người duyệt. Actor/reference chỉ là audit, **không phải xác thực danh tính**: host phải kiểm quyền chạy CLI/file. Plugin không triển khai hệ quyền toàn cục.

Không sửa approved rule trực tiếp: tạo candidate mới, validate/approve lại; deprecate bản cũ qua operator có reason. Candidate không có quyền sửa source skill.

Sửa skill: tạo change-request với lesson_id approved, paths, actor; thực hiện thay đổi đúng CR và thêm case; operator chạy `scripts/xh_evolution.py test --data cr.json` với cr_id. Lệnh chạy unittest thật + mọi evaluation case, lưu source fingerprint. Operator chạy release với cr_id, version lớn hơn manifest, actor, approval_reference. Source/cases đổi sau test làm gate từ chối. Receipt release-authorized cho phép cập nhật manifest/đóng gói; script không tự sửa skill/cài đặt. Chất lượng quyết định còn cần thử hồ sơ đại diện và reviewer, không suy từ PASS rằng mọi báo cáo đều đúng.

Anh Hưng có thể nói “Giữ các phần còn lại, sửa mục X theo file Y; số liệu này chỉ thuộc dự án”. MASTER nhập bản sửa và giữ diff. Nếu muốn học chung: “Cách sửa này nên dùng cho báo cáo tương tự; đưa thành đề xuất bài học.” Hệ thống trình rule, phạm vi, ngoại lệ, evidence và case để anh duyệt. “Duyệt bài học L-...” chỉ áp dụng đúng nội dung/hash đã trình, không duyệt mọi sửa skill tương lai.

`learning/registry.sqlite` là nguồn giao dịch; JSONL ledger, knowledge JSON, changelog và metrics là projection được phục hồi trong cùng transaction ghi. Sao lưu toàn shared root; không sửa projection bằng tay. Trao đổi đa máy chỉ qua gói projection read-only: export, kiểm hash và stage-import; approval không được chuyển theo gói. Đồng bộ DB đa máy thuộc hạ tầng ngoài plugin. Metrics ở đây chỉ là trạng thái bài học/kiểm thử, không chứa chi phí hay đánh giá model.
