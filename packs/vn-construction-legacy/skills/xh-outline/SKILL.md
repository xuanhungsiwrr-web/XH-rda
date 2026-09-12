<!-- HISTORICAL ONLY: Do not activate this legacy skill or its provider policy. Use root skills and references/domain-workflow.md. -->
---
name: xh-outline
description: |
  Sinh và khoá bản đặc tả đề mục cho từng loại báo cáo tư vấn thiết kế — mục tiêu của mục, câu hỏi thẩm định, nguồn dữ liệu, độ dài, hình/bảng bắt buộc, cấm kỵ, exemplar. Tách đề mục và đoạn văn mẫu từ báo cáo đã được phê duyệt. Kích hoạt khi người dùng nhắc: bản đặc tả đề mục, spec đề mục, outline báo cáo, khung đề mục, tách exemplar, sinh spec, đặc tả BCKTKT, đặc tả BCNCKT. Chỉ sinh khung/đặc tả và đoạn văn mẫu ngắn để tham chiếu — không viết nội dung hoàn chỉnh của đề mục; nội dung đầy đủ từng đề mục là việc của xh-viet.
---

# XH_Outline — bản đặc tả đề mục

Khung đề mục chỉ cho biết **tên mục**. Nó không nói cho mô hình biết năm điều quyết định chất lượng, nên mô hình phải tự suy đoán — đúng khoảng 60–70%, và phần 30–40% còn lại chính là chỗ người dùng phải sửa.

Bản đặc tả lấp đúng khoảng trống đó.

## Schema một đề mục

```yaml
ma: "C2.1"
ten: "Điều kiện địa hình"
muc_tieu: "Chứng minh địa hình khu vực phù hợp/không phù hợp với phương án tuyến đề xuất"
cau_hoi_tham_dinh:
  - "Cao độ tự nhiên bình quân bao nhiêu, so với mực nước thiết kế thế nào?"
  - "Có vị trí xung yếu nào không?"
nguon_du_lieu: ["00_input/KhaoSat-DiaHinh/", "_facts.yaml: cao_trinh_*"]
khoa_facts_bat_buoc: ["cao_trinh_tu_nhien", "muc_nuoc_thiet_ke_p2"]
do_dai: "2–3 trang, 5–7 đoạn"        # ĐO từ báo cáo đã duyệt, không đặt theo cảm tính
hinh_bat_buoc: ["sơ đồ vị trí", "mặt cắt ngang đại diện"]
bang_bat_buoc: ["bảng cao độ đặc trưng theo lý trình"]
can_cu: ["TCVN 8419:2022"]
nhom_van_phong: "Điều kiện tự nhiên"  # một trong 6 nhóm ở Mục H hồ sơ văn phong
exemplar: "exemplars/<LoaiBC>/C2-1_DieuKienDiaHinh.md"
cam_ky: "Không mô tả chung chung 'địa hình tương đối bằng phẳng' mà câu sau không có số"
loi_da_xay_ra_that: "…"               # trỏ về điểm cụ thể trong danh sách mâu thuẫn
trang_thai: "cho_ra"                  # cho_ra | da_duyet
nguoi_duyet: ""
```

## Phân công: script làm gì, mô hình làm gì

**Script trích chính xác 100%, không cần AI:**

| Trích | Bằng cách nào |
|---|---|
| cây đề mục theo cấp | `python-docx` đọc `paragraph.style.name` |
| độ dài thực tế mỗi mục | đếm từ, đếm đoạn giữa hai heading |
| số hình, số bảng mỗi mục | đếm caption và `InlineShape` |
| văn bản pháp lý được trích | regex `TCVN|QCVN|Nghị định|Thông tư|Quyết định` |
| tỉ lệ bullet, giọng theo nhóm | `scripts/do-muc-h.py` |

**Mô hình suy luận:** `muc_tieu`, `cau_hoi_tham_dinh` (suy ngược từ nội dung đã viết — người thẩm định sẽ hỏi gì), `nguon_du_lieu`, `cam_ky` (rút từ chỗ báo cáo mẫu làm ĐÚNG mà báo cáo kém hay làm sai).

## Ba luật để spec không bị "học vẹt" một dự án

**Chạy trên ít nhất ba báo cáo cùng loại rồi hợp nhất.** Một báo cáo thì spec bám chặt vào đặc thù dự án đó — ép mọi dự án phải có mục "xử lý nền đất yếu" trong khi dự án khác không cần.

- khối có ở **cả ba** → `bat_buoc`
- khối có ở **một hoặc hai** → `tuy_chon`, ghi rõ điều kiện áp dụng
- **số liệu cụ thể không bao giờ đưa vào spec**, chỉ đưa *loại* số liệu

**Spec phải có người duyệt.** Spec do AI sinh mà chưa ai rà thì **không được dùng để viết báo cáo trình duyệt**. Rà một lượt mất khoảng hai giờ cho một loại báo cáo, sau đó dùng được nhiều năm. Đổi `trang_thai: da_duyet` và điền `nguoi_duyet`.

**Exemplar phải là bản ĐÃ ĐƯỢC DUYỆT, không phải bản đã nộp.** Bản qua thẩm định là bản chịu được chất vấn.

## Bộ hạt giống có sẵn trong plugin

`references/spec-goc-BCDXCTDT.yaml` — spec gốc cho BCĐXCTĐT, exemplar kèm theo ở
`references/exemplars/BCDXCTDT/`. Không phải spec của dự án nào: chỉ có *loại* số liệu.

Quy trình: chép sang `specs/BCDXCTDT.yaml` trong thư mục dự án → điền `nguon_du_lieu`,
`khoa_facts_bat_buoc` theo hồ sơ thực tế → người dùng rà → `trang_thai: da_duyet`.

Bổ sung đề mục mới vào bộ hạt giống chỉ khi đã thấy khối đó ở **ít nhất ba** báo cáo cùng
loại (luật ba báo cáo ở trên), và mọi trường `cam_ky` phải rút từ lỗi đã xảy ra thật —
ghi rõ ở `loi_da_xay_ra_that`.

## Tách exemplar

Với mỗi đề mục, tách đoạn văn tương ứng ra `exemplars/<LoaiBC>/<ma-muc>.md`, và **viết kèm 3–5 dòng ghi chú giải thích**:

```markdown
<!-- Vì sao đoạn này tốt:
     - Mở bằng nguồn khảo sát + thời điểm + tỉ lệ, chưa vội đưa nhận định
     - Số liệu luôn đi kèm hệ quy chiếu (hệ VN2000)
     - Câu cuối mới là kết luận, và kết luận dẫn thẳng sang yêu cầu thiết kế
     - Không có một tính từ cảm tính nào
-->
```

Ghi chú này biến một *ví dụ* thành một *bài học*, và làm exemplar hiệu quả hơn nhiều lần.

> **Ghi chú về khối lượng thực tế:** Một BCKTKT có khoảng 40–60 đề mục cấp 2 (bản đặc tả đầy đủ của BCKTKT Nam Quốc là 117 đề mục). Xử lý theo lô, mỗi lô một chương: khoảng 2–3 giờ máy cho một báo cáo, cộng 1–2 giờ người dùng rà lại.
