# Kiến trúc ba lớp

```
LỚP 1 · DỮ LIỆU      _facts.yaml · hinh-anh-catalog.md · _references-scope.md
        ↓ chưng cất một lần, người duyệt
LỚP 2 · NỘI DUNG     10_content/*.md — AI viết, chỉ Markdown
        ↓ AI viết, mang tên khoá chứ không mang con số
LỚP 3 · TRÌNH BÀY    KhuonMau_NamQuoc.dotx + render_report.py → .docx
        ↓ script tất định, chạy ĐÚNG MỘT LẦN ở bước cuối
```

## Vì sao phải tách

Kiến trúc cũ cho AI sinh từng file `.docx` rồi ghép lại. Ghép `.docx` là thao tác **mất mát về bản chất**: mỗi file mang `styles.xml`, `numbering.xml`, `sectPr` riêng, nên ghép xong thì mục lục không build được, style sinh ra bản trùng tên, đánh số đề mục nhảy loạn, header đổi giữa chừng. Đó chính là danh sách việc phải sửa tay sau mỗi báo cáo.

Với kiến trúc ba lớp, định dạng là **hằng số** — nó nằm trong khuôn, không phụ thuộc vào việc mô hình hôm nay viết thế nào.

## Ba luật bất biến

**Con số chỉ tồn tại ở Lớp 1.** Bản thảo `.md` viết `{{fact:cao_trinh_dinh_ke}}`, không gõ số. Sửa một chỗ, cả báo cáo đổi theo — và `qc-check.py` có chỗ để đối chiếu.

**File `.md` tuyệt đối không chứa:** bìa, mục lục, danh mục hình/bảng, header, footer, số trang, số thứ tự hình/bảng gõ tay. Đó không phải việc của AI.

**Hai tầng trạng thái cho mọi con số:**
```
AI trích  → status: unverified → KHÔNG dùng cho số high-stakes
Người duyệt → status: verified → được dùng
```
High-stakes = cao trình thiết kế, lưu lượng tính toán, khối lượng chính, đơn giá, mã hiệu định mức. `render_report.py` tô vàng và `qc-check.py` báo lỗi khi bản thảo dùng số chưa duyệt.

**Bốn loại xuất xứ cho mọi con số.** Trường `data_type` trong `_facts.yaml`:

| `data_type` | Nghĩa | Ràng buộc khi viết |
|---|---|---|
| `PROJECT` | số đo của chính dự án này | dùng tự do. Khoá không khai `data_type` được hiểu là PROJECT |
| `REFERENCE` | số mượn từ dự án lân cận hoặc hồ sơ khác | **bắt buộc** khai thêm `nguon_du_an`; đề mục dùng nó phải **nhắc tên nguồn** và **có câu khuyến cáo khảo sát bổ sung** |
| `LEGAL` | trị số lấy từ văn bản pháp lý, TCVN, QCVN | bắt buộc có `source` ghi số hiệu văn bản |
| `MISSING` | chưa có, đang chờ khảo sát | **cấm dùng trong bản thảo**; để `{{TODO: ...}}` thay vào |

`qc-check.py` luật L10 bắt bốn lỗi tương ứng: `MUON_THIEU_KHAI_NGUON` · `MUON_THIEU_DAN_NGUON` · `MUON_THIEU_KHUYEN_CAO` · `FACT_MISSING` · `LEGAL_THIEU_NGUON`.

Lược đồ đầy đủ một khoá:

```yaml
schema_version: "1.1"  # Bắt buộc có ở đầu file để quản lý version

cao_do_dinh_ke:
  value: 2.50
  unit: m
  source: "1.TMTK_ke AFD 21.2.2025.docx#tr.45"
  quote: "cao trình đỉnh kè thiết kế +2,50m (hệ Hòn Dấu)"
  status: verified            # unverified | verified | conflict
  data_type: REFERENCE        # PROJECT | REFERENCE | LEGAL | MISSING
  nguon_du_an: "kè AfD Đê biển Tây"   # bắt buộc khi REFERENCE
```

> Trường `data_type` chưng từ lược đồ Evidence Pack của skill `gemini-retriever` (plugin v2), thêm 25/08/2026. Nó giải đúng bài toán Cầu Sông Đốc: thiếu khảo sát địa chất và thuỷ văn, phải mượn số của dự án kè AfD kề bên — và **số mượn không bao giờ được trình bày như số của chính dự án**.


## Cấu trúc thư mục dự án

```
<YYMM>_<DiaDanh>_<TenNgan>_<GiaiDoan>/
├── _info.yaml           giá trị cho {{KEY}} ở khuôn (bìa, header, footer)
├── _facts.yaml          mọi con số, có nguồn và trạng thái
├── _references-scope.md văn bản pháp lý được phép trích
├── 00_input/            hồ sơ Claude cần đọc (không phải cả kho dự án)
├── 10_content/          C01_....md · C02_....md — AI viết
└── 20_output/           .docx render ra
```
