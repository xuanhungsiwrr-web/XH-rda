# Nơi lưu và cách mang toàn bộ công việc đi

```text
AI_Config/PLUGINS/
  xh-tuvan-0.6.0/          source đang nâng lên 0.7.0, giữ path cũ để không đứt liên kết
    skills/ scripts/ config/ references/ tests/
    packs/                legacy nghiệp vụ + humanizer upstream và license
    docs/                 audit, hướng dẫn, kết quả kiểm thử
  Backups/                ZIP nguyên bản trước chuyển đổi
  Releases/               source ZIP portable, không kèm .venv hoặc API key

AI_Workspace/
  NoiDung_CacBaoCao/       thư viện yêu cầu tối thiểu, không phải dữ liệu dự án
  Library/                vị trí khuyến nghị cho templates, profiles, exemplar đã khử số
  Tools/                  scripts gốc tham khảo; bản tích hợp được đóng gói trong plugin
  Skills/                 ZIP upstream gốc
  Projects/<ma-du-an>/
    project.json          metadata, nguồn Drive, execution và budget
    sources/              input gốc + converted MD có source hash
    research/             web HTML/MD, nguồn pháp lý, evidence chưa duyệt
    evidence/             facts theo revision, metadata fields
    specs/                snapshot yêu cầu + outline + coverage mapping
    calculations/         Excel/Word/artifact tính toán và summary MD
    drafts/               MD hiện hành từng section
    edits/ reviews/       bản sửa người dùng và phiếu QC
    templates/            khuôn và contract chính xác dùng cho dự án
    outputs/              report MD, Word, preview
    feedback/             nhận xét, dữ liệu đề xuất cải tiến plugin
    .xh/                  SQLite, snapshots theo hash và file render tạm
```

Chưa di chuyển các thư mục dữ liệu đang có. Chỉ tạo cây project mới khi có yêu cầu làm dự án; bản demo kiểm thử tách riêng. Source plugin và artifacts làm báo cáo không trộn nhau. Runtime không sửa source plugin từ feedback: người dùng xem diff rồi mới chấp nhận quy tắc mới.

Tái sử dụng cùng dự án: giữ MD/conversion và source hashes; chỉ viết lại section stale. Tái sử dụng dự án khác: lấy exemplar đã loại số/names, công thức và phương pháp có phạm vi áp dụng; nguồn mang REFERENCE, facts nhập lại unverified, không mang approval của dự án trước.

Export project qua CLI export: database snapshot nhất quán và mọi file đã register cùng revision lịch sử. Để lấy toàn bộ file đầu vào, ingest/register chúng trước. Source ZIP là gói riêng; mang cả source release + project export + thư viện/template cần thiết. Không copy .venv sang máy khác, cài dependencies từ requirements. Nếu có secrets trong tài liệu do người dùng cung cấp, archive vẫn chứa tài liệu đó; đây không phải công cụ dò/xóa secrets trong nội dung.
