---
name: xh-caotrinh-ke
description: "Tính cao trình đỉnh kè, đỉnh đê, đỉnh tường chắn sóng từ mực nước thiết kế, gió, đà sóng, bề rộng sông và thông số tàu — theo TCVN 9902:2023, TCVN 8421:2010, TCVN 8419:2022, QCVN 02:2022/BXD, QCVN 04-05:2022. Xuất chuỗi tính đã thế số kèm nguồn từng thông số và khối YAML cho _facts.yaml. Kích hoạt khi người dùng nhắc: cao trình đỉnh kè, cao trình đỉnh đê, cao trình đỉnh tường chắn sóng, tính nước dềnh do gió, sóng leo, chọn cao độ đỉnh kè, kiểm tra cao trình kè, Zđ. Không dùng để thiết kế mặt cắt hay tính ổn định kè — chỉ xác định cao trình đỉnh."
---

# Tính cao trình đỉnh kè

## 1. Phạm vi và nguyên tắc chọn căn cứ

Trước khi tính, xác định kè thuộc loại nào — điều này quyết định cấp công trình và tần suất:

| Loại kè | Cấp công trình lấy theo | Ghi chú |
|---|---|---|
| Kè bảo vệ đê / thuộc tuyến đê | Cấp đê theo pháp luật đê điều | QCVN 04-05:2022 mục 1.2 **loại trừ** công trình đê điều khỏi phạm vi |
| Kè, bờ bao thuỷ lợi độc lập | QCVN 04-05:2022 Bảng 1 | Mục 1.3 liệt kê "kè, bờ bao thuỷ lợi" là công trình thuỷ lợi |
| Kè bờ sông đô thị | QCVN 03:2022/BXD | |

**Viện dẫn đúng cách:** TCVN 8419:2022 (tiêu chuẩn chuyên cho kè bảo vệ đê, bờ sông) mục 9.3.5.2 chỉ cho *nguyên tắc*, không có công thức gia cao. Khi kè kết hợp chống lũ/triều cường thì mượn công thức của TCVN 9902:2023 (đê sông). **Thuyết minh phải viện dẫn cả hai**: 8419:2022 cho phạm vi/nguyên tắc, 9902:2023 cho công thức.

Không viết câu "chưa có tiêu chuẩn cụ thể áp dụng cho công trình kè" — TCVN 8419:2022 đã có.

## 2. Công thức

```
Zđ = Htk + ΔH + Hsl + a + b + s          (TCVN 9902:2023, mục 10.2.1.1, CT 1)
```

| | Tên | Nguồn |
|---|---|---|
| Htk | Mực nước thiết kế | Tính toán thuỷ văn dự án hoặc quy định của cơ quan có thẩm quyền |
| ΔH | Nước dềnh do gió | TCVN 8421:2010 CT (A.1) |
| Hsl | Sóng leo **do tàu thuyền** | TCVN 8421:2010 CT (84)(85)(86) |
| a | Độ vượt cao an toàn | TCVN 9902:2023 Bảng 6 |
| b | Nước biển dâng | Kịch bản BĐKH-NBD Bộ TN&MT, bản cập nhật 2020 |
| s | Tổng độ lún | TCVN 9902:2023 CT (4); mục 10.2.1.4 cho phép bỏ s với kết cấu BT/BTCT/gạch đá xây |

## 3. Chạy công cụ

```bash
python3 scripts/caotrinh_ke.py --mau > input.json     # sinh file mẫu
# sửa input.json theo hồ sơ dự án
python3 scripts/caotrinh_ke.py input.json -o 30_BanThao/PL_CaoTrinhDinhKe.md
python3 scripts/caotrinh_ke.py input.json --json      # lấy kết quả dạng máy đọc
```

Script tự tra mọi hệ số **tra bảng**; các hệ số **tra đồ thị** phải nhập tay (mục 5).

## 4. Chuỗi tính và nguồn từng thông số

### 4.1. Gió tính toán Vw

```
T (chu kỳ lặp) ← cấp đê:  ĐB → 1% (100 năm) | I,II → 2% (50 năm) | III,IV,V → 4% (25 năm)
                                                       (TCVN 9902:2023, 10.2.1.2)
Vl = Km,T × V10m,50        (QCVN 02:2022/BXD Bảng 5.1 cột V10m,50; Bảng 5.3 hệ số Km,T)
Vw = kfl × kl × Vl         (TCVN 8421:2010, A.3.3)
     kfl = 0,675 + 4,5/Vl  ≤ 1,0
     kl  tra Bảng A.3 — QCVN 02:2022 chuẩn hoá theo **địa hình B** nên dùng cột B
```

**Giữ cả kfl và kl.** Hai hệ số này gần như bù nhau (ví dụ Vl ≈ 29,8 m/s: kfl = 0,826; kl = 1,240; tích = 1,025). Bỏ kfl mà giữ kl thì thừa ~24%; bỏ cả hai thì thiếu ~2%.

Đây là chỗ hồ sơ cũ hay sai: lấy vận tốc gió **3 giây** (V3s hoặc W0 của QCVN 02:2009) làm Vl, trong khi TCVN 8421 định nghĩa Vl là gió **trung bình 10 phút** ở cao độ 10 m.

### 4.2. Nước dềnh ΔH

```
ΔH = kw · Vw² · L / [ g · (d + 0,5·ΔH) ] · cos αw        (TCVN 8421:2010, CT A.1)
```

Công thức **ẩn** → giải lặp (script tự làm, thường hội tụ sau 3–5 vòng).

- `kw` — Bảng A.2, nội suy theo Vw (20→2,1e-6; 30→3,0e-6; 40→3,9e-6; 50→4,8e-6)
- `L` — đà sóng (m): bề rộng mặt nước theo hướng gió bất lợi, đo trên bình đồ khảo sát địa hình
- `d` — độ sâu nước ứng với Htk, lấy từ mặt cắt ngang khảo sát
- `αw` — góc giữa trục dọc khu nước và hướng gió; **mặc định lấy 0° (bất lợi nhất)**

**Ngưỡng nghi ngờ:** ΔH > 0,10 m trên sông là bất thường — thường do nhầm nước dềnh với chiều cao sóng.

### 4.3. Sóng leo do tàu Hsl

```
v_adm = 0,9·√( [6·cos((π + arccos(1−ka))/3) − 2(1−ka)] · g·A/b )    (CT 85)
hsh   = 2·(v²/g)·√(δ·ds/lu)                                          (CT 84)
hrsh  = βsl·[0,5·hsh + 0,05·ctgφ·v²/g] / (1 − 0,05·ctgφ)             (CT 86)
```

- `ka` — tỷ số diện tích mặt cắt ngang phần ngập của tàu / diện tích mặt cắt ướt sông A
- `A` (m²), `b` (m) — mặt cắt ướt và bề rộng sông theo mép nước
- `δ` — hệ số đầy mớn tàu; `ds` — mớn nước; `lu` — chiều dài tàu (lấy theo **tàu thiết kế** của tuyến luồng)
- `βsl` — 1,4 bản liền khối · 1,0 đá lát · 0,8 đá đổ
- `ctgφ` — hệ số mái dốc. CT(86) đòi hỏi ctgφ < 20.

⚠ **v_adm theo CT(85) là tốc độ GIỚI HẠN (cận trên).** Nếu luồng có quy định tốc độ chạy tàu thấp hơn, nhập vào `v_khong_che` — nếu không, hsh có thể thiên lớn 2–3 lần.

### 4.4. Sóng leo do gió — kiểm tra bổ sung, mặc định TẮT

TCVN 9902:2023 mục 10.2.1.1 định nghĩa **Hsl là sóng leo do tàu thuyền**; ảnh hưởng của gió trên đê sông đã được kể qua ΔH. Chú thích Bảng 6 chỉ cho phép "xem xét cho phù hợp" tuỳ giải pháp.

Chỉ bật `tinh_song_gio` khi có lý do rõ ràng (sông rất rộng, cửa sông thoáng, đà sóng vài km) và **phải luận chứng riêng trong thuyết minh**. Khi bật:

```
h1% = 0,0208 · Wg^1,25 · Dg^(1/3)               (TCVN 8419:2022, CT 7 — Dg tính bằng km)
hrun1% = kr · kp · ksp · krun · h1%             (TCVN 8421:2010, CT 25)
```

⚠ CT(7) có dạng `Dg^(1/3)`, **thiên lớn rõ rệt khi đà gió < 1 km**. Với sông hẹp, nhập trực tiếp `h1_nhap` tra từ Hình A.1/A.2 TCVN 8421 thay vì để script dùng CT(7).

Nếu Hsl bị quyết định bởi sóng gió, script sẽ cảnh báo — đừng bỏ qua cảnh báo đó.

### 4.5. a, b, s

- **a** — TCVN 9902:2023 Bảng 6: ĐB 0,80 · I 0,60 · II 0,50 · III 0,40 · IV 0,30 · V 0,20 (m)
- **b** — kịch bản BĐKH-NBD Bộ TN&MT bản 2020. **Ghi rõ kịch bản (RCP4.5/RCP8.5), mốc năm, tỉnh.** Mặc định dự án ĐBSCL: RCP8.5, mốc 2050. TCVN 9902:2023 yêu cầu b ≥ 0 và **phải được CĐT hoặc cơ quan có thẩm quyền chấp thuận** — nhắc người dùng gắn văn bản hoặc ghi căn cứ.
- **s** — tách `s = s_công trình + s_nền khu vực`. Vùng ĐBSCL có lún nền do khai thác nước ngầm, nên vẫn cộng s cho kè BTCT/cừ dù mục 10.2.1.4 cho phép bỏ; nếu bỏ thì phải luận chứng.

### 4.6. Bước chọn cao trình

```
Zc = làm tròn lên [ max(Zđ ; cao trình kè hiện hữu lân cận ; yêu cầu kết nối hạ tầng ; MNTK kè) ]
```

Bội số làm tròn 0,05 m (mặc định) hoặc 0,10 m. **Bắt buộc viết một câu lý do chọn** trong thuyết minh — ví dụ "phù hợp điều kiện địa hình tự nhiên, đồng bộ với các đoạn kè hiện hữu, dự phòng lún do khai thác nước ngầm".

TCVN 8419:2022 mục 9.3.5.1g: cao trình đỉnh kè **tối thiểu** bằng mực nước thiết kế kè.

## 5. Thông số phải tra đồ thị hoặc tự quyết định

Script **không** đoán thay các giá trị này.

| Thông số | Nguồn | Bắt buộc? |
|---|---|---|
| `krun` | **Đồ thị Hình 11 TCVN 8421** — trục ngang ctgφ (1÷30), họ đường cong λ̄d/h̄d1% = 7, 10, 15, 20, 25, 30, 40, 50; krun ≈ 0,1÷2,6 | Chỉ khi bật sóng gió |
| `h1_nhap` (thay CT7) | **Đồ thị Hình A.1 + A.2 TCVN 8421** qua gL/Vw², gt/Vw | Khi đà gió < 1 km |
| `kt`, `λ` nước nông | Hình A.4, A.5 TCVN 8421 | Chỉ khi d/λ < 0,5 — sông ĐBSCL thường không cần |
| `L` (đà sóng), `αw` | Đo trên bình đồ / ảnh vệ tinh | Có |
| Tàu thiết kế: `ds`, `lu`, `δ`, `ka`, `v_khong_che` | Cấp kỹ thuật tuyến luồng, quy định tốc độ chạy tàu | Có |
| `ket_cau_mai` → kr, kp | Giải pháp kết cấu đã chọn | Có |
| `b`, kịch bản NBD, mốc năm | Quyết định của người thiết kế + chấp thuận của CĐT | Có |
| `s` | Kết quả tính lún + số liệu lún nền khu vực | Có |

Các hệ số **tra bảng** — kw (A.2), kl (A.3), kfl, kr/kp (Bảng 6), ksp (Bảng 7), ki (Bảng 8), kβ (Bảng 9), βsl, a (Bảng 6 TCVN 9902), Km,T (Bảng 5.3), tần suất (Bảng 4 QCVN 04-05) — script tự tra và tự nội suy, có in nguồn.

## 6. Quy trình làm việc

1. Hỏi/xác định: loại kè → cấp công trình → tần suất.
2. Lấy Htk từ hồ sơ thuỷ văn (hoặc `_facts.yaml` nếu đã có).
3. Lấy V10m,50 từ QCVN 02:2022/BXD Bảng 5.1 theo địa danh. *Lưu ý sáp nhập đơn vị hành chính 2025 — bảng dùng tên huyện/tỉnh cũ.*
4. Đo L, d, b, A trên bình đồ và mặt cắt.
5. Sinh `input.json`, điền, chạy script.
6. **Đọc hết phần cảnh báo** — xử lý từng cái trước khi dùng kết quả.
7. Dán khối YAML vào `_facts.yaml` (trạng thái `cho_duyet`), dán bản Markdown vào phụ lục tính toán.
8. Gọi `xh-viet` để viết đoạn thuyết minh; `xh-qc` để soát chéo.

## 7. Kiểm chứng

Script đã được kiểm ngược với hồ sơ đã duyệt:

- **Kè G6 (Bạc Liêu, cấp III):** Zđ = 3,381 m, chọn +3,50 m — hồ sơ gốc 3,39 m / +3,50 m.
- **Kè sông Đồng Nai:** với Vw = 22,32 m/s, L = 800 m, d = 4 m → kw = 2,3088e-6 (hồ sơ ghi 2,31e-6), ΔH = 0,0234 m (hồ sơ ghi 0,024 m).

## 8. Lỗi thường gặp cần chặn

1. Định nghĩa `s` một đằng, dùng số một nẻo trong cùng phụ lục.
2. Ghi `b = 0,26 cm` trong khi số dùng là 0,26 **m**.
3. Lấy `a` từ Bảng 6 **TCVN 9901** (đê biển) trong khi công thức là của TCVN 9902.
4. Gọi ΔH là "chiều cao sóng Hs" — nước dềnh và chiều cao sóng là hai đại lượng khác nhau.
5. Gộp "nước dềnh do gió và tàu" thành một con số không tách được.
6. Dùng gió 3 giây làm Vl (TCVN 8421 cần gió trung bình 10 phút).
7. Dùng nguồn gió QCVN 02:**2009** (đã bị QCVN 02:**2022** thay thế).
8. Không ghi tần suất gió gắn với cấp đê.


