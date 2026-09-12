---
name: xh-viet
description: |
  Viết nội dung từng đề mục báo cáo tư vấn thiết kế ra Markdown có cấu trúc, theo bản đặc tả đề mục và hồ sơ văn phong đã đo từ báo cáo đã duyệt. Không xử lý định dạng, không tạo bìa hay mục lục. Kích hoạt khi người dùng nhắc: viết chương, viết đề mục, soạn nội dung báo cáo, viết thuyết minh, viết phần điều kiện tự nhiên, viết giải pháp thiết kế, viết sự cần thiết đầu tư. Chỉ viết khi đã có bản đặc tả đề mục (spec) được khoá; nếu đề mục/spec chưa có hoặc chưa đủ mục tiêu — câu hỏi thẩm định — exemplar, phải chạy xh-outline trước, không tự bịa khung đề mục rồi viết luôn.
---

# XH_Viet — lớp nội dung

Sản phẩm của skill này là **Markdown**, không phải Word. Định dạng là việc của `xh-docx`.

## Nạp gì vào ngữ cảnh trước khi viết

Ngân sách khoảng 2.700 token cho mỗi đề mục:

| Nạp | Nguồn | Token |
|---|---|---|
| Hồ sơ văn phong Mục A–G | `references/ho-so-van-phong.md` | ~1.400 |
| **Đúng một dòng** Mục H — nhóm đề mục đang viết | cùng file | ~80 |
| **Đúng một** exemplar + ghi chú | `exemplars/<LoaiBC>/<ma>.md` | ~900 |
| Spec đề mục | `specs/<LoaiBC>.yaml` | ~350 |

Dự án chưa có `specs/<LoaiBC>.yaml` thì lấy bộ hạt giống trong plugin làm nền:
`references/spec-goc-BCDXCTDT.yaml`, exemplar kèm theo ở `references/exemplars/BCDXCTDT/`.
Bộ hạt giống chỉ chứa *loại* số liệu, không chứa số của dự án nào — chép sang thư mục dự
án rồi mới điền `nguon_du_lieu` và `khoa_facts_bat_buoc` theo hồ sơ thực tế.

**Không nạp cả kho exemplar.** Vừa tốn token vừa làm loãng tín hiệu. Mỗi lần viết chỉ một cái, đúng nhóm.

Viết mục "Xác định sơ bộ hiệu quả đầu tư về kinh tế - xã hội" có nhóm lợi ích liên quan đến đất
(đất mất do sạt lở, đất tăng giá trị do chỉnh trang) thì nạp thêm
`references/don-gia-dat-loi-ich-kinh-te.md` — chuỗi 4 bước quy đổi giá đất từ Bảng giá đất địa
phương, kèm kiểm sàn bắt buộc.

Mục A–G giống hệt nhau ở mọi lần viết — đặt ở **đầu** ngữ cảnh, cố định, để được lưu cache; phần thay đổi đặt sau.

## Quy tắc viết — đo từ báo cáo đã duyệt, không suy đoán

| | Số đo | Áp dụng |
|---|---|---|
| Câu | trung bình 20,4 từ, trung vị 15 | viết câu 8–35 từ |
| Đoạn | **92,8% dưới 3 câu**, trung vị **1 câu** | **không ép đoạn dài** |
| Bullet | 19,5% toàn báo cáo | theo nhóm, xem Mục H |
| Dấu thập phân | phẩy | `4,50` |
| Đơn vị | **viết dính** | `188m`, `-0,50m` |

Giọng khác nhau theo nhóm đề mục — đây là chỗ hay bị bỏ sót nhất:

| Nhóm | Bullet | Từ/đoạn | Đặc điểm |
|---|---|---|---|
| Sự cần thiết đầu tư | 13% | **56** | lập luận, đoạn dài gấp đôi, vẫn phải có số |
| Căn cứ pháp lý | **2%** | 24 | mỗi căn cứ **một đoạn riêng** mở bằng "Căn cứ" — không dùng bullet |
| Điều kiện tự nhiên | 2% | 24 | luôn dẫn nguồn + thời điểm + tỉ lệ khảo sát |
| Giải pháp kỹ thuật | 10% | **21** | khô, đặc số liệu, đoạn ngắn nhất |
| So sánh phương án | **0%** | 25 | dùng **bảng**; kết luận phải khớp chương thiết kế |
| Kết luận – kiến nghị | 4% | **12** | ngắn, dứt khoát, **không đưa số mới** |

## Cấu trúc đoạn có số liệu

```
NGUỒN → SỐ → SO SÁNH VỚI TRỊ CHO PHÉP → Ý NGHĨA THIẾT KẾ
```

Đoạn mô tả thuần thì một câu là đủ: *"Bản chắn đất bằng bê tông cốt thép M300, dày 12cm, đặt trên nền cọc tràm."*

Câu định tính **được phép** mở đoạn — nhưng câu ngay sau phải có số.

## Con số: không bao giờ gõ trực tiếp

Viết `{{fact:ten_chi_tieu}}`. Script thay số khi render. Con số chỉ tồn tại ở `_facts.yaml`.

Khoá chưa có trong `_facts.yaml` → dừng lại, báo người dùng bổ sung. Không tự điền số từ trí nhớ, không lấy số của dự án khác (Nguyên tắc 1 và 6).

Chỗ còn thiếu dữ liệu → `{{TODO: mô tả cụ thể cần bổ sung gì}}`. Tuyệt đối không dùng `…` hay `.../`: báo cáo đã nộp từng để lọt *"Công văn số …../UBND-NNXD"* vào bản in.

## Trong file `.md` tuyệt đối không có

Bìa · mục lục · danh mục hình/bảng · header · footer · số trang · số thứ tự hình/bảng gõ tay. Đó không phải việc của skill này.

## Danh sách cấm

| Không viết | Thay bằng |
|---|---|
| "chúng tôi" | "đơn vị tư vấn" |
| "bước lập dự án đầu tư" (nói về bước sau chủ trương đầu tư) | "bước lập Báo cáo nghiên cứu khả thi" — hoặc "lập Báo cáo kinh tế – kỹ thuật" với dự án được phép |
| viện dẫn cả hành lang luồng hàng hải **và** hành lang luồng đường thuỷ nội địa cho cùng một vị trí | xác định vị trí thuộc hệ nào rồi chỉ viện dẫn hệ đó — một vị trí trên sông chỉ thuộc một hệ quản lý luồng |
| chép lại trị số đã nêu ở đề mục khác (cao trình, tần suất, cấp công trình) | dẫn chiếu số đề mục; trị số chỉ xuất hiện ở đúng một đề mục |
| "tối ưu nhất", "rất tốt", "thuận lợi" | nêu trị số và trị số cho phép |
| "đây là", "bao gồm:" + bullet | mở bằng chủ thể; liệt kê bằng câu hoặc bảng |
| "gần/khoảng" + số lẻ đến hàng đơn vị | làm tròn, hoặc bỏ từ ước lượng và dẫn nguồn |
| "Báo cáo này trình bày...", "Nội dung này được thực hiện tại Chương..." | bỏ hẳn — xem Mục L hồ sơ văn phong |
| "Số liệu ... được tổng hợp từ ba nguồn..." | bỏ hẳn — truy nguồn sống trong `_facts.yaml` |
| "cần bổ sung", "chưa xác định được", "đề nghị anh chốt" | viết ở thể khẳng định hoặc chuyển thành Kiến nghị ở chương cuối |
| "Đơn vị tư vấn lập báo cáo là..." trong phần mở đầu | bỏ — đã có ở bìa và khung tên bản vẽ |

**Nhóm bốn dòng cuối là lỗi "lệch vai"** — nhóm lỗi anh Hưng bắt nhiều nhất ở bản v2. Đọc
Mục L của `references/ho-so-van-phong.md` trước khi viết bất kỳ chương nào.

## Viết từng chương một — không viết gộp

**Viết xong MỘT chương thì dừng, chạy hết ba bước kiểm dưới đây, nhận phản hồi ĐẠT rồi mới
viết chương tiếp theo.** Không viết liền mạch nhiều chương rồi mới kiểm.

Lý do: bản v2 Cầu Sông Đốc viết một mạch 10 chương. Một lỗi kết cấu ở Chương I (mô tả sai
quan hệ cầu–kè) lan sang bốn chương và kéo đổ cả lập luận so sánh phương án ở Chương IV.
Kiểm ngay sau Chương I thì lỗi đã dừng ở một chương.

**Bước 1 — quét số gõ chết.** Tự đọc lại chương vừa viết. Con số kỹ thuật nào gõ trực tiếp mà
KHÔNG bọc trong `{{fact:...}}` thì thay ngay bằng `{{fact:key}}` (nếu biết key) hoặc
`{{TODO: bổ sung key cho số ...}}`.

Áp dụng cho cả **số dẫn xuất** — số tính ra từ số khác: diện tích mặt cầu, số nhịp, số trụ,
suất đầu tư, tổng phân kỳ. Bản v2 gõ cứng hơn 20 số dẫn xuất, và khi chiều dài cầu đổi thì
không có cách nào bảo đảm đã sửa hết. Kết quả: phân kỳ vốn ba năm cộng lại thiếu 11,8 tỷ so
với tổng mức đầu tư, ngay bên dưới câu tự khẳng định là đã bằng nhau.

**Bước 2 — chạy luật cứng.** `scripts/qc-check.py 10_content/ --facts _facts.yaml`. Sửa hết
lỗi nghiêm trọng.

**Bước 3 — CỔNG GEMINI_QC (bắt buộc).** Gọi
`mcp__remote-devices__gemini_qc__gemini_quality_control` trên chương vừa viết.

Dán vào `report_text`: toàn văn chương, **kèm khối số liệu neo** ở đầu (chiều dài, cấp công
trình, tổng mức đầu tư, các cao độ và trị số chính lấy từ `_facts.yaml`). Gemini không thấy
các chương khác — không có khối neo này thì nó không bắt được mâu thuẫn chéo chương.

Trong `criteria`, yêu cầu Gemini đóng vai chuyên gia thẩm định độc lập khó tính, chỉ ra lỗi
cụ thể kèm trích dẫn, không khen chung chung, và rà đủ sáu nhóm: vai viết và văn phong · mâu
thuẫn số liệu · logic kỹ thuật · thiếu nội dung bắt buộc · tiêu chuẩn áp dụng · rủi ro bị
thẩm định trả hồ sơ.

**ĐẠT** = không còn lỗi nhóm nghiêm trọng và không còn lỗi vai viết. Lỗi cảnh báo thì ghi
nhận, đi tiếp, và liệt kê lại ở bước `xh-qc` cuối.

**Chưa ĐẠT** thì sửa chương đó rồi chạy lại Gemini_QC. Lặp tới khi đạt. Không bỏ qua để
viết tiếp.

**Gemini_QC không gọi được** (chưa cài, hết quota, lỗi API) → dừng, báo người dùng. Không tự
bỏ qua cổng. Trong lúc chờ, chạy tạm agent `xh-qc` cho riêng chương đó và ghi rõ đã dùng
phương án thay thế.

Chỉ khi cả 10 chương đều qua cổng mới gọi `xh-qc` chạy trên toàn bộ bản thảo để bắt mâu thuẫn
chéo chương, rồi mới `xh-docx`.
