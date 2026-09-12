# Chín nguyên tắc tuyệt đối — không thương lượng

Áp dụng cho mọi skill trong plugin này.

1. **Không bịa số liệu.** Mọi con số khảo sát / tính toán / cao trình / lưu lượng phải có nguồn trong `00_input/` hoặc hồ sơ giai đoạn trước. Thiếu thì **nói thẳng là thiếu** và để `{{TODO: ...}}` — không sáng tác.

2. **Chỉ trích văn bản còn hiệu lực.** Đối chiếu `_references-scope.md` của dự án. Văn bản đã hết hiệu lực thì không trích; nếu trích để so sánh lịch sử thì ghi rõ "đã hết hiệu lực, dẫn để tham khảo".

3. **Không lệch khỏi khuôn.** Font, lề, header, footer, style đề mục đều nằm trong `KhuonMau_NamQuoc.dotx`. Script chỉ gọi tên style có trong `references/template-map.yaml`, không tự đặt định dạng. Đổi cấu trúc khung đề mục → hỏi người dùng trước.

4. **Dùng hệ SI và ký hiệu theo TCVN.** Đơn vị và ký hiệu tuân theo tiêu chuẩn đã chốt ở `_references-scope.md`.

5. **Văn phong kỹ thuật, không quảng cáo.** Không dùng tính từ cảm tính. Chi tiết đo được ở `references/ho-so-van-phong.md`.

6. **Tái sử dụng có kiểm soát.** Khi lấy nội dung từ báo cáo cũ: chỉ lấy phần được đánh dấu tái sử dụng được; ghi chú nguồn dạng `*(Tham khảo: <mã-dự-án>)*`; **tuyệt đối không sao chép số liệu khảo sát** trừ khi cùng vị trí đo và cùng chuỗi số liệu đã nghiệm thu.

7. **Mâu thuẫn dữ liệu — không tự xử.** Hai nguồn cho hai con số khác nhau thì ghi cả hai vào `_facts.yaml` với `status: conflict` và liệt kê `ung_vien`, chờ người dùng chốt. Không tự chọn cái "hợp lý hơn".

8. **Báo cáo trình duyệt — viết đủ, không tóm tắt.** Viết đủ độ sâu kỹ thuật theo chuẩn hồ sơ trình duyệt. Không rút gọn trừ khi người dùng yêu cầu thẳng.

9. **Lập luận theo chuỗi năm mắt xích — không nhảy cóc.** Mọi đoạn chứng minh sự cần thiết đầu tư, mọi đoạn giải thích vì sao chọn giải pháp này, phải đi đủ năm bước và **theo đúng thứ tự**:

   ```
   (1) Hiện trạng đo đạc      vị trí, lý trình, kích thước, mức độ hư hỏng — có số
   (2) Nguyên nhân kỹ thuật   dòng chảy, triều cường, địa chất yếu, tải trọng
   (3) Hậu quả và rủi ro      mất an toàn đê bao, gián đoạn giao thông, ngập úng
   (4) Sự cần thiết đầu tư    bám quy hoạch được duyệt + văn bản của địa phương
   (5) Giải pháp kiến nghị    kết cấu phù hợp nhất về kỹ thuật - kinh tế
   ```

   Thiếu mắt xích (2) thì đoạn văn thành mô tả, không thành lập luận. Thiếu (3) thì người thẩm định không thấy vì sao phải làm bây giờ. Nhảy thẳng từ (1) sang (5) là lỗi hay gặp nhất.

   *Nhập từ `engineering-writing-master` (plugin v2), 25/08/2026. Chi tiết cách viết và ví dụ ở `ho-so-van-phong.md` Mục K.*

---

## Quy tắc "không làm gì cả"

Dù skill đã kích hoạt, **không** tự động:

- Tạo dự án mới khi người dùng chỉ hỏi thông tin chung.
- Viết nội dung kỹ thuật vượt quá dữ liệu có trong `00_input/`.
- Thay đổi cấu trúc khung đề mục khi chưa xác nhận.
- Bổ sung TCVN ngoài `_references-scope.md`.
- Sao chép số liệu khảo sát từ dự án khác.
- Tự chọn một trong hai giá trị mâu thuẫn.
- Tóm tắt báo cáo trình duyệt cho ngắn gọn.
- **Ghép file `.docx`.** Khái niệm "ghép chương" đã bị loại khỏi kiến trúc.
- **Tự tạo bìa.** Bìa là file riêng, người dùng làm ngoài quy trình này.
- **Trích văn bản pháp lý theo trí nhớ.** Danh mục ở `references/phap-ly-2026-07-01.md` là ảnh chụp 08/08/2026 — phải tra lại hiệu lực trước mỗi dự án.

Khi nghi ngờ → hỏi. Một câu hỏi trước rẻ hơn một báo cáo sai.
