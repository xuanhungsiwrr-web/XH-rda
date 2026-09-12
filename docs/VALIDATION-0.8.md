# Kiểm chứng xh-tuvan 0.8.0

Ngày kiểm tra: 09/09/2026 (Asia/Saigon). Chỉ kiểm Domain Orchestrator cục bộ, không gọi API trả phí hoặc triển khai Global Control.

Kết quả: **30 unittest PASS**, lần cuối 47,318 giây; **11/11 skill hợp lệ**; **5/5 evaluation baseline PASS**. MCP stdio thật khởi tạo và công bố đúng xh_project, xh_learning; yêu cầu approve qua tool model bị từ chối.

Đã kiểm: nhận dạng ba loại báo cáo và lấy khung nội dung; tự chuyển extraction/pháp lý/kỹ thuật/outline/drafting/QA/output; từ chối kết quả dùng revision cũ; giữ bản sửa người dùng; chỉ vô hiệu hóa phần phụ thuộc; giữ conflicts; approval không theo bản sửa; coverage; render một Word từ nhiều phần và từ chối style thiếu; export artifacts/revisions; di trú schema giữ lịch sử và chạy lại không tạo thay đổi dư.

Learning: candidate không thể bỏ validation/approval; không tự review; approval phải trùng content hash; hai đối tượng dùng cùng store đọc cùng snapshot; scope global không ghi ledger; project facts ở .ai; giữ lịch sử rejected/deprecated; phục hồi ledger bị ghi dở từ registry; xóa/làm yếu case cũ không thể PASS. Post-Project Review bắt buộc theo report revision; gọi lại với danh sách lesson rỗng không làm mất candidate đang chờ duyệt.

Đã chạy **toàn chuỗi phát hành bằng fixture trong thư mục tạm**: candidate → independent validation → simulated operator approval → CR → unittest thực + evaluations → release-authorized. Gọi lại cùng ý định trả receipt cũ; đổi evaluation sau test bị từ chối. Fixture không được đưa vào approved knowledge thật và không tạo version 0.8.1 thật.

Fingerprint scripts/skills/references/workflows/tests của lần kiểm cuối:
`851cd6ba5f6289b06bee034bc451bcdeaf964734c6f6766ba2747b93faa5e061`

Không còn tên model cố định hoặc tham chiếu provider registry trong skills/agents/references hiện hành khi rà soát. Các adapter chọn provider/gọi API của 0.7 đã được sao lưu rồi gỡ; HTML normalizer chỉ xử lý HTML đã nhận. Công cụ nhập bảng legacy giữ tương thích định dạng, không chọn model.

Giới hạn cần giữ rõ: không kiểm end-to-end Claude/ChatGPT/Global Control thật; chưa cài plugin vào ứng dụng. Actor và approval_reference là dữ liệu audit, host phải xác thực quyền thực thi. Test tất định không thay semantic review/pháp lý/kỹ thuật. Word fixture được kiểm cấu trúc bằng python-docx; không phải kiểm dàn trang một báo cáo thực tế. Shared SQLite cần một filesystem cục bộ; đồng bộ đa máy không thuộc gói này.

Kho approved thực tế khởi đầu rỗng. Năm case baseline là dữ liệu tổng hợp, không phải số liệu dự án hoặc bài học giả được phê duyệt.
