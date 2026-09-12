# Prompt chuyển phiên

Tiếp tục công việc với anh Hưng bằng tiếng Việt. Phạm vi đang chốt chỉ là xh-tuvan Domain Orchestrator, không xây Global AI Control Plane.

Source: D:/AI_Space/AI_Config/PLUGINS/xh-tuvan-0.6.0, manifest 0.8.0. Kiến trúc gốc: D:/AI_Space/AI_Docs/Kien_truc_AI_Tong_the_va_XH_Tuvan_v1.0.md. Đọc README.md, references/domain-workflow.md, references/shared-learning.md và docs/VALIDATION-0.8.md trước khi sửa tiếp.

Đã thực hiện: gỡ provider router/API adapters khỏi runtime; dùng MASTER/TECHNICAL_SPECIALIST/EXTRACTOR/REVIEWER/RESEARCHER; start từ yêu cầu cấp cao tự chọn bộ nội dung tối thiểu; workflow domain và kiểm input revisions; facts/decisions/PPR trong project/.ai; shared knowledge có candidate/validated/approved/rejected/deprecated, ledger, evaluations và metrics; cổng CR/test/release; cập nhật 11 skills. Giữ Markdown incremental, dependency, QA, attachments, Word renderer.

Kiểm chứng cuối: 30 unittest PASS, 11 skill hợp lệ, 5 baseline cases PASS, MCP stdio thật; chuỗi release thử chạy trong kho tạm. Không có bài học fixture trong kho thật. Kho approved thật rỗng. Chưa kiểm tích hợp Global thật, chưa nhập/cài vào ChatGPT. Không nói rằng chỉ phát capability packet là đã gọi model.

Learning bắt buộc candidate → validation → approval → CR → test → version mới. Không tự phê duyệt thay người dùng. Host phải xác thực quyền CLI; actor/reference không phải cơ chế xác thực. Dữ liệu dự án không đưa vào shared rules; bài học chi phí/model trả Global, không ghi domain.

Backup trước sửa: D:/AI_Space/AI_Config/PLUGINS/Backups/xh-tuvan-before-domain-0.8-20260908.zip. Gói nguồn 0.8 nằm Releases. Công cụ thực hiện và thử cổng phát hành nằm D:/AI_Space/AI_Docs/XH_Tuvan_0.8_Review/tools. Không chạy lại maintenance script trên source đã thay đổi vì chúng kiểm backup trước khi thao tác.

Bước tiếp theo chỉ khi được giao: tích hợp hợp đồng capability với Global Control thực tế hoặc thử hồ sơ đại diện trong project riêng. Không tự mở rộng sang Telegram/Tailscale, thiết bị, thuê bao, ngân sách API hoặc hạ tầng worker. Nếu sửa code/skill sau kiểm, chạy kiểm tra phù hợp và cập nhật bằng chứng trước đóng gói.
