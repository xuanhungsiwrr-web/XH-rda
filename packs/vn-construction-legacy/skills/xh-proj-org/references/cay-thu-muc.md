# Cây Thư Mục Chuẩn — Dự Án Tư Vấn Thiết Kế Thủy Lợi

> Áp dụng cho: BCNCKT (FS), TKKT, TKBVTC, kè bờ sông, đê điều, cầu cống thuỷ lợi

## Cây thư mục đầy đủ

```
YYMM_[TenDuAn]_[GiaiDoan]/
│
├── INFO/                              ← Thông tin dự án, phân công, sổ theo dõi
│   ├── _README.md                     ← Tên CĐT, số HĐ, tiến độ, liên hệ
│   ├── PhanCongCV_Timeline.xlsx       ← Phân công nhân sự + timeline
│   └── SoHieu_TaiLieu.xlsx            ← Sổ theo dõi số hiệu phát hành
│
├── 10.PhapLy/
│   ├── 11.ChuTruongDT/                ← QĐ phê duyệt chủ trương, QĐ phê duyệt BCNCKT
│   ├── 12.HopDong/                    ← Hợp đồng tư vấn ký với CĐT + phụ lục
│   │   └── _Goc/                      ← File Word gốc để chỉnh sửa
│   ├── 13.YKien_CoQuan/               ← Ý kiến GPMB, địa phương, Bộ ngành, thỏa thuận
│   └── 14.QuyetToan/                  ← Hồ sơ thanh quyết toán hợp đồng tư vấn
│
├── 20.DauThau/                        ← Bỏ qua nếu dự án chỉ định thầu
│   ├── 21.HSMT/                       ← Thông báo mời thầu + Hồ sơ mời thầu từ CĐT
│   └── 22.HSDT/
│       ├── _Goc/                      ← File Word/Excel đang làm
│       └── _NopThau/                  ← Hồ sơ PDF đóng dấu đã nộp
│
├── 30.KhaoSat/
│   ├── 31.NV_PAKS/                    ← Nhiệm vụ khảo sát + PAKS
│   ├── 32.DiaHinh/
│   │   └── _Goc_SoLieu/               ← File gốc từ đơn vị KS (DEM, LAS, DWG)
│   ├── 33.DiaChat/
│   │   └── _Goc_SoLieu/               ← File gốc từ đơn vị KS địa chất
│   └── 34.PhatHanh/                   ← Báo cáo khảo sát phát hành chính thức (PDF)
│
├── 40.ThietKe/
│   ├── 41.ThucHien/                   ← FILE LÀM VIỆC NỘI BỘ — không gửi ra ngoài
│   │   ├── ThuyetMinh/                ← File thuyết minh, báo cáo (Word)
│   │   ├── TinhToan/                  ← File tính toán thuỷ lực, kết cấu, ổn định
│   │   ├── BanVe_CAD/                 ← DWG/DXF gốc (không đổi tên)
│   │   └── DuToan/                    ← Excel dự toán (không đổi tên)
│   │
│   ├── 42.PhatHanh/                   ← ★ HỒ SƠ GỬI ĐI — mỗi đợt = 1 subfolder
│   │   ├── ph1_[YYMMDD]/              ← Phát hành lần 1
│   │   │   ├── T1_BaoCaoChinh.pdf
│   │   │   ├── T2_TomTat.pdf
│   │   │   ├── T3_TMTKCS.pdf
│   │   │   ├── T4_BanVe.pdf
│   │   │   └── T5_DuToan.pdf
│   │   └── ph2_[YYMMDD]/              ← Phát hành lần 2 (chỉ tập có thay đổi)
│   │
│   └── 43.ThamTra_ThamDinh/
│       └── KetQua_ThamTra/            ← Báo cáo thẩm tra, giải trình, ý kiến CĐT
│
├── 50.NTTT/                           ← Nghiệm thu & Thanh toán
│   ├── 51.NghiemThu/
│   │   ├── _HoSo_NT/                  ← File Word làm việc
│   │   └── _PhatHanh/                 ← BB nghiệm thu đã ký
│   ├── 52.ThanhToan/
│   │   ├── Dot1_TamUng/
│   │   ├── Dot2_ThanhToan70pct/
│   │   └── Dot3_QuyetToan/
│   └── 53.QuyetToan/                  ← Hồ sơ hoàn công, quyết toán cuối
│
├── 60.VanThu/
│   ├── 61.CongVan_Di/                 ← CV do đơn vị gửi ra
│   ├── 62.CongVan_Den/                ← CV nhận từ CĐT, Sở, Bộ
│   └── 63.LuuTru/                     ← Email quan trọng lưu dạng PDF
│
└── REF/                               ← Tài liệu tham khảo
    ├── TieuChuan/
    ├── DuAnTuongTu/
    └── HuongDan_KyThuat/
```

---

## Bảng nhận dạng folder cũ → folder mới (thường gặp)

| Folder/file cũ (tên tự phát) | Folder mới (chuẩn) |
|------------------------------|---------------------|
| `PhapLy/`, `PL/`, `Pha ly/` | `10.PhapLy/` |
| `DeXuatCTDT/`, `ChuTruong/` | `10.PhapLy/11.ChuTruongDT/` |
| `HopDong/`, `HD/`, `Contract/` | `10.PhapLy/12.HopDong/` |
| `YKien/`, `GopY/`, `GPMB/` | `10.PhapLy/13.YKien_CoQuan/` |
| `ThanhToan/`, `QuyetToan/` (HĐ TV) | `10.PhapLy/14.QuyetToan/` |
| `DauThau/`, `HSDT/`, `HoSoDuThau/` | `20.DauThau/` |
| `HSMT/`, `TBMT/` | `20.DauThau/21.HSMT/` |
| `HSDuThau/`, `PPL/` | `20.DauThau/22.HSDT/` |
| `KhaoSat/`, `KS/`, `Survey/` | `30.KhaoSat/` |
| `NhiemVuKS/`, `NVKS/`, `PAKS/` | `30.KhaoSat/31.NV_PAKS/` |
| `DiaHinh/`, `DH/`, `Topography/` | `30.KhaoSat/32.DiaHinh/` |
| `DiaChat/`, `DC/`, `Geology/` | `30.KhaoSat/33.DiaChat/` |
| `ThietKe/`, `Design/`, `HoSo/` | `40.ThietKe/` |
| `LamViec/`, `Working/`, `Draft/` | `40.ThietKe/41.ThucHien/` |
| `ThuyetMinh/`, `BC/`, `Report/` | `40.ThietKe/41.ThucHien/ThuyetMinh/` |
| `BanVe/`, `DWG/`, `CAD/` | `40.ThietKe/41.ThucHien/BanVe_CAD/` |
| `TinhToan/`, `Calc/` | `40.ThietKe/41.ThucHien/TinhToan/` |
| `DuToan/`, `Estimate/`, `TMDT/` | `40.ThietKe/41.ThucHien/DuToan/` |
| `PhatHanh/`, `NopHoSo/`, `Submit/` | `40.ThietKe/42.PhatHanh/` |
| `ThamDinh/`, `ThamTra/`, `Review/` | `40.ThietKe/43.ThamTra_ThamDinh/` |
| `NghiemThu/`, `NT/` | `50.NTTT/51.NghiemThu/` |
| `ThanhToan/` (tiền) | `50.NTTT/52.ThanhToan/` |
| `VanThu/`, `CV/`, `CongVan/` | `60.VanThu/` |
| `Ref/`, `Reference/`, `ThamKhao/` | `REF/` |
| `Info/`, `ThongTin/` | `INFO/` |

---

## Quy tắc tạo folder

**Cấp 1** (10., 20., 30., ...):
- Bỏ hẳn folder nếu dự án không có nội dung
- **Giữ nguyên số thứ tự** của các folder còn lại
- Ví dụ: dự án không có đấu thầu → bỏ `20.DauThau/`, nhưng folder tiếp theo vẫn là `30.KhaoSat/`

**Cấp 2 trở xuống**:
- Chỉ tạo khi có file phù hợp
- Bỏ cả folder lẫn số thứ tự nếu không có nội dung

---

## Ghi chú bổ sung

**Với dự án TKKT hoặc TKBVTC:**
- Folder `42.PhatHanh/` có thể có thêm tập: T6 (Phụ biểu tính toán), T7 (Chỉ dẫn kỹ thuật)

**Với dự án chỉ định thầu** (không qua đấu thầu):
- Bỏ `20.DauThau/`, giữ số thứ tự — folder tiếp theo vẫn là `30.KhaoSat/`

**File CAD và dự toán:**
- CAD `.dwg`, `.dxf`, `.bak` → giữ nguyên tên gốc, chỉ đảm bảo đúng folder `BanVe_CAD/`
- Excel dự toán → giữ nguyên tên gốc, đặt vào `DuToan/`

**File scan tài liệu gốc:**
- Đặt trong `_Goc/` của folder tương ứng
- Không bỏ vào `REF/`
