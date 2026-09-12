# Workspace layout 3

Layout có version riêng với plugin: `layout_version=3`, plugin `0.9.0`. Mọi caller dùng `scripts/xh_layout.py`; không tự ghép chuỗi đường dẫn. Root Google Drive chính được định danh bằng folder ID `1kO9wbjTqSxB-NDLSZqfGuRHwc-Eqkmee`. ID/URL không được suy thành ổ đĩa cục bộ.

```text
AI_Space/
├─ 00_Registry/{repositories,deployments,storage}
├─ 01_Development/{incoming,projects,releases}
├─ 02_Workspace/{projects,tasks}
├─ 03_Knowledge/xh-tuvan/{inbox,evidence,review,published}
├─ 03_Knowledge/global-control/operational
├─ 04_Library/{templates,references,tools,artifacts}
├─ 05_Docs/{architecture,guides,prompts,decisions}
├─ 06_Platforms/{claude,chatgpt}/{instructions,config-examples,handoffs}
└─ 90_Archive
```

Mỗi báo cáo/giai đoạn có workspace riêng:

```text
02_Workspace/projects/<project-code>/<report-or-stage>/
├─ README.md
├─ project.json
├─ 10_Sources/10_User_Input
├─ 10_Sources/20_Source_Snapshots
├─ 20_Templates
├─ 30_Working/10_Research
├─ 30_Working/20_Evidence
├─ 30_Working/30_Specs
├─ 30_Working/40_Drafts
├─ 30_Working/50_Reviews
├─ 30_Working/60_Edit_Analysis
├─ 30_Working/70_Learning_Candidates
├─ 30_Working/.ai
├─ 30_Working/.xh
├─ 40_Outputs
└─ 50_Feedback
```

`README.md` chỉ là chỉ mục, không là state thứ hai. `project.json` giữ identity/metadata/source references. SQLite, blobs và journal ở `30_Working/.xh`; facts/decisions/workflow state ở `30_Working/.ai`. Không tạo `calculations` cho workspace mới. Kết quả tính toán có sẵn được snapshot như input; migration giữ `calculations` cũ dưới nhánh `30_Working/.xh/legacy-out-of-scope`.

Nguồn ngoài workspace mặc định chỉ đọc. Chỉ snapshot file cần dùng, ghi ID/URL/revision hoặc modifiedTime/hash. `sources` legacy thiếu provenance không được đoán là user input hay snapshot; migration giữ dưới `30_Working/.xh/legacy-unclassified/sources` và ghi mapping.

Mỗi report release ở `40_Outputs` có bản sao byte-identical `_XHedited.docx` ở `50_Feedback`. Baseline không đổi; feedback không bị overwrite. Pair được quản lý bằng ID, revision, SHA-256, thời gian và plugin version. Preview/ảnh/log/file kỹ thuật không tạo feedback pair.

`XH_TUVAN_KNOWLEDGE_ROOT` tiếp tục chỉ tới operational store cục bộ có persistence và một writer SQLite. Không đổi biến này sang `inbox` hoặc `published` trên Drive. Dùng `xh_knowledge_transfer.py` để xuất projection hoặc stage import; staging không chuyển approval và không ghi DB. Published Drive là projection do quy trình phát hành bên ngoài kiểm soát.

Xem `docs/MIGRATION-0.9.md` trước khi chuyển workspace thật. Không tự di chuyển dữ liệu cũ.
