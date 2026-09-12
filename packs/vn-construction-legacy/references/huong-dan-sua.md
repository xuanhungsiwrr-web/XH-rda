# Hướng dẫn sửa bản thảo trong Word

Dành cho anh khi review bản `..._dasua.docx` trong `30_review/`. Làm đúng theo đây thì Claude
học được nhiều nhất từ bản anh sửa — xem thêm mục "Vòng học từ bản người dùng sửa" trong
`skills/xh-tuvan/SKILL.md`.

## 1. Trước khi sửa

Mở đúng bản trong `30_review/` (không sửa thẳng vào `20_output/`). Đặt tên bản đã sửa theo quy
ước `<TenCongTrinh>_<LoaiBC>_<TenTaiLieu>_v<n>_dasua.docx` — không ghi đè lên bản gốc, cặp
`v<n>` / `v<n>_dasua` là dữ liệu học, mất là không rút quy tắc lại được.

## 2. Sửa thế nào

**Bật Track Changes.** Word → Review → Track Changes.
Đây là điều quan trọng nhất. Có track changes thì Claude đọc được chính xác anh đổi chữ nào
thành chữ nào. Không có thì Claude chỉ thấy bản mới, không biết anh đã sửa gì, và học được rất ít.

**Tô màu theo loại vấn đề** (quy ước R7 của skill cũ, giữ nguyên):

| Màu | Nghĩa | Claude sẽ làm gì |
|---|---|---|
| 🟡 Vàng | Sai — số sai, dẫn sai văn bản, sai sự thật | Sửa gốc ở `_facts.yaml` rồi render lại |
| 🟢 Xanh lá | Cần rà lại — chưa chắc đúng, cần kiểm chứng | Tra lại nguồn, hỏi anh nếu không tự quyết được |
| 🔵 Xanh lam | Cần viết lại — nội dung đúng nhưng văn phong hoặc lập luận chưa đạt | Viết lại đoạn đó, đây là phần Claude học nhiều nhất |

**Chỗ Claude để `【TODO: ...】` tô vàng sẵn:** nếu anh có số thì điền thẳng vào, Claude sẽ
đưa vào `_facts.yaml`. Nếu chưa có thì để nguyên.

> **Lưu ý:** một phần chỗ tô vàng trong bản Claude render ra là **tự động**, không phải anh tô
> tay — `render_report.py` tô vàng mọi `{{fact:}}` có `status` khác `verified`. Mục dưới đây nói
> vì sao điều này quan trọng khi anh xóa nguyên một đoạn.

## 3. Xóa cả đoạn mà muốn Claude biết vì sao — dùng Comment, không dùng màu

Chọn đoạn định xóa → **Insert Comment** → gõ ngắn gọn lý do ("sai", "thừa, đã nói ở C05 rồi",
"chưa đủ chứng cứ, bỏ") → rồi xóa bình thường. Track Changes vẫn ghi nhận đoạn xóa, comment vẫn
neo đúng vị trí đó dù chữ đã gạch ngang.

Đừng chỉ tô màu rồi xóa để giải thích lý do xóa, vì hai lẽ:

1. Tô vàng trong bản Word render ra đã có sẵn **tự động** cho mọi `{{fact:}}` chưa `verified`
   (xem lưu ý ở Mục 2). Nếu anh chỉ xóa một đoạn vốn đã vàng sẵn mà không tô gì thêm, Claude
   không phân biệt được đó là anh chủ động gắn nghĩa "sai" theo R7, hay chỉ là markup tự động
   còn sót lại mà anh xóa vì lý do khác (thừa, trùng ý, văn phong...).
2. Ba màu R7 ở Mục 2 mô tả vấn đề của câu **còn lại** trong văn bản, không có màu riêng cho lý
   do xóa hẳn (thừa, trùng, hết cần).

Trường hợp đơn giản — đúng nghĩa "sai" như R7 và đoạn đó **chưa từng** bị tô vàng tự động — thì
tô vàng trước rồi xóa vẫn dùng được: Word giữ nguyên định dạng tô màu trên chữ gạch ngang khi
xóa có Track Changes, Claude vẫn đọc ra được cả hai. Nhưng Comment chắc ăn hơn và không phải
nhớ ngoại lệ này — dùng Comment làm mặc định.

## 4. Sau khi sửa xong

Báo cho Claude bản đã sửa xong (không phải sửa một phần rồi để đó) để chạy vòng học đầy đủ:
so bản gốc với bản đã sửa, rút quy tắc vào `references/ho-so-van-phong.md`, cập nhật `_facts.yaml`
với những chỗ anh sửa số, rồi render bản kế tiếp.
