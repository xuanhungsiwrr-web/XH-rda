---
name: xh-drive
description: "Lấy hồ sơ dự án từ thư mục Google Drive, lập danh mục và nhập bổ sung theo phiên bản."
---

# xh-drive

Nhận folder URL/ID một lần, lưu source_roots trong project.json. Dùng connector thật có trong phiên; không giả định tên tool hoặc schema cũ. Nếu chưa có connector nhưng folder đã đồng bộ local thì dùng nguồn local. Thiếu cả hai thì ghi việc cần kết nối, tiếp tục phần không phụ thuộc.

Lần đầu listing metadata trước, phân nhóm nguồn dự án/đối chứng/pháp lý. Đọc chọn lọc file cần cho spec; không đọc cả kho. Ghi file ID, revision/modifiedTime/hash nếu có, URL, local snapshot, conversion status. Lần sau chỉ nhập mới/đổi; invalidation chạy theo source deps. Không tự di chuyển/xóa/đổi tên kho nguồn. File tham khảo luôn mang REFERENCE; không chuyển số tham khảo thành số dự án.

Đọc `references/portable-workflow.md` khi bắt đầu dự án hoặc resume. Mọi path bên dưới tương đối với plugin root; dùng đường dẫn plugin mà host cung cấp, không giả định ổ đĩa. Không đọc toàn bộ pack legacy. Dùng CLI `scripts/xh.py` hoặc MCP `xh_project` nếu có. Luôn gọi status trước thay đổi để phát hiện bản sửa ngoài hệ thống.
