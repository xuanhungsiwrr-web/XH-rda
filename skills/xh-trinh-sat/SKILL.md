---
name: xh-trinh-sat
description: |
  Trinh sát tự động — tự tìm và tải về thông tin công khai liên quan đến dự án (quy hoạch liên quan, cảnh báo sạt lở, mực nước báo động BĐ3, dự án lân cận, điều kiện tự nhiên–xã hội khu vực) bằng công cụ MCP Exa, lưu có trích dẫn nguồn/URL vào 00_input/90.TrinhSat-Exa/. Kích hoạt khi người dùng nhắc: trinh sát tự động, tìm thông tin công khai cho dự án, tra cứu quy hoạch liên quan, tìm cảnh báo sạt lở, tìm mực nước báo động, tìm dự án lân cận, Exa search, trinh sát dự án. Cần công cụ MCP của connector "Exa" (web_search_exa) đã kết nối cho phiên — nếu chưa có, dừng lại và báo người dùng kết nối trước, không tự bịa kết quả tìm kiếm bằng kiến thức có sẵn.
---

# XH_TrinhSat — trinh sát tự động bằng Exa

Skill này thay cho việc `xh-viet-bao-cao` (plugin `xh-tuvan-v2`) tự tra cứu internet ngầm bên trong lúc viết — tách thành một bước trinh sát riêng, có sổ ghi, chạy **trước** khi viết, để `xh-viet` sau này trích dẫn lại có nguồn rõ ràng thay vì tự nhớ đã đọc ở đâu.

## Kiểm tra trước khi làm gì cả

Trước khi tìm bất cứ thứ gì, xác nhận công cụ `web_search_exa` (connector **Exa**) có trong danh sách công cụ khả dụng của phiên này không.

- **Có** → làm tiếp theo hướng dẫn dưới.
- **Không có** → dừng ngay, nói với người dùng: *"Chưa có công cụ tìm kiếm Exa trong phiên này — cần kết nối connector 'Exa' trên claude.ai trước."* Không tự trả lời bằng kiến thức có sẵn của mô hình rồi giả vờ đó là kết quả tìm kiếm — người dùng sẽ không phân biệt được đâu là trinh sát thật, đâu là bịa.

## Việc cần làm — theo đúng thứ tự

1. **Khởi tạo sổ ghi** (một lần, đầu dự án):
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/ghi-ket-qua-trinh-sat.py khoi-tao \
       --thu-muc-du-an 10-DangViet/<MaDuAn>/00_input/
   ```

2. **Xác định các nhóm cần tìm** — tối thiểu năm nhóm, đúng loại thông tin `xh-viet-bao-cao` từng tự tra cứu:
   - Quy hoạch liên quan đến khu vực dự án (quy hoạch xây dựng, quy hoạch sử dụng đất, quy hoạch phòng chống thiên tai)
   - Cảnh báo sạt lở nguy hiểm tại hoặc gần khu vực dự án
   - Mực nước báo động (BĐ1/BĐ2/BĐ3) của trạm gần nhất
   - Dự án liên quan / lân cận đang hoặc đã triển khai
   - Điều kiện tự nhiên — xã hội khu vực (dân số, kinh tế, hạ tầng hiện có)

   Thêm nhóm khác nếu người dùng yêu cầu cụ thể; không tự bớt nhóm nào trong năm nhóm trên nếu người dùng chỉ nói "trinh sát tự động" chung chung.

3. **Gọi `web_search_exa` cho từng nhóm**, dùng từ khoá có tên địa danh/công trình cụ thể của dự án (không dùng từ khoá chung chung như chỉ "sạt lở" — phải kèm tên sông/xã/tỉnh).

4. **Ghi từng kết quả thật sự liên quan** (không ghi mọi kết quả trả về — lọc lấy cái đúng chủ đề) vào sổ:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/ghi-ket-qua-trinh-sat.py ghi \
       --thu-muc-du-an 10-DangViet/<MaDuAn>/00_input/ \
       --tu-khoa "<từ khoá đã dùng để tìm>" \
       --tieu-de "<tiêu đề trang/tài liệu>" \
       --url "<URL nguồn>" \
       --trich-doan "<câu/đoạn ngắn liên quan trực tiếp>"
   ```

5. Khi xong, báo cho người dùng số kết quả ghi được theo từng nhóm, và đường dẫn `00_input/90.TrinhSat-Exa/_DanhMuc-TrinhSat.md`.

## Ranh giới — không làm

- **Không tự viết nội dung báo cáo từ kết quả tìm được.** Đây chỉ là bước thu thập tham khảo, đưa vào `00_input/` để `xh-viet` đọc và trích dẫn sau — giống hệt vai trò của hồ sơ khảo sát giấy.
- **Không đưa số liệu tìm được thẳng vào `_facts.yaml`.** Số liệu công khai tìm qua Exa (ví dụ mực nước báo động) vẫn phải qua `xh-evidence` để vào kho số đúng khuôn sáu trường, có `status: unverified` chờ người dùng duyệt — không lấy thẳng từ danh mục trinh sát.
- **Không ghi kết quả không liên quan chỉ để cho có số lượng.** Sổ ghi càng nhiều rác thì càng khó lọc lúc viết.
- **Không tìm kiếm nếu công cụ Exa chưa kết nối** — xem mục "Kiểm tra trước khi làm gì cả" ở trên.
