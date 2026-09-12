# Quy ước đặt tên — xh-proj-org

Tách từ `skills/xh-proj-org/SKILL.md` ngày 25/08/2026 để giảm dung lượng ngữ cảnh nạp mỗi lần kích hoạt skill. Đọc file này khi cần: cây thư mục chuẩn, hệ đánh số, quy ước đặt tên thư mục gốc, đặt tên file làm việc/phát hành, đặt tên folder `42.PhatHanh/`, và script đổi tên.

## Cau truc thu muc chuan (tom tat)

```
[TenDuAn]/
|-- INFO/                      <- Thong tin du an, phan cong, so theo doi
|-- 10.PhapLy/
|   |-- 11.ChuTruongDT/        <- QD chu truong, QD phe duyet
|   |-- 12.HopDong/            <- HD tu van, phu luc, HD thau phu
|   |-- 13.YKien_CoQuan/       <- Y kien GPMB, thoa thuan vi tri, co quan
|   +-- 14.QuyetToan/          <- Ho so thanh quyet toan HD tu van
|-- 20.DauThau/                <- Bo neu chi dinh thau
|   |-- 21.HSMT/               <- TBMT + HSMT tu CDT
|   +-- 22.HSDT/
|       |-- _Goc/
|       +-- _NopThau/
|-- 30.KhaoSat/
|   |-- 31.NV_PAKS/            <- Nhiem vu khao sat + PAKS
|   |-- 32.DiaHinh/
|   |-- 33.DiaChat/
|   |   +-- _Goc_SoLieu/
|   +-- 34.PhatHanh/           <- Bao cao khao sat phat hanh (PDF)
|-- 40.ThietKe/
|   |-- 41.ThucHien/           <- File lam viec noi bo
|   |   |-- ThuyetMinh/
|   |   |-- TinhToan/
|   |   |-- BanVe_CAD/
|   |   +-- DuToan/
|   |-- 42.PhatHanh/           <- Ho so phat hanh chinh thuc
|   |   +-- ph1_[YYMMDD]/      <- Moi dot phat hanh = 1 subfolder
|   +-- 43.ThamTra_ThamDinh/
|       +-- KetQua_ThamTra/
|-- 50.NTTT/                   <- Nghiem thu & Thanh toan
|   |-- 51.NghiemThu/
|   |   |-- _HoSo_NT/
|   |   +-- _PhatHanh/
|   |-- 52.ThanhToan/
|   |   |-- Dot1_TamUng/
|   |   |-- Dot2_ThanhToan70pct/
|   |   +-- Dot3_QuyetToan/
|   +-- 53.QuyetToan/
|-- 60.VanThu/
|   |-- 61.CongVan_Di/
|   |-- 62.CongVan_Den/
|   +-- 63.LuuTru/             <- Email, tai lieu luu tru dang PDF
+-- REF/                       <- Tai lieu tham khao
    |-- TieuChuan/
    |-- DuAnTuongTu/
    +-- HuongDan_KyThuat/
```

**Trong kho Archive nhieu du an da hoan thanh**, moi folder du an cap 1 ngoai ra con co the co them:
```
HSPheDuyet/                    <- Ho so thiet ke SAU CUNG (thuong la PDF) da duoc phe duyet/phat hanh
                                   chi tao khi xac dinh RO RANG nguon file (folder ten "PheDuyet",
                                   "Phat Hanh", "XuatBan", "RevF...Sau tham dinh" co PDF ben trong).
                                   Neu khong ro -> hoi nguoi dung, KHONG doan.
```

---

## Quy uoc dat ten thu muc goc du an

```
YYMM_[MaHieuDuAn]_[GiaiDoan]
```

| Thanh phan | Quy uoc | Vi du |
|-----------|---------|-------|
| `YYMM` | Nam-thang ky hop dong | `2508` = thang 8/2025 |
| `MaHieuDuAn` | Ten ngan, khong dau cach | `CM_KeG6`, `DeDieuCaMau` |
| `GiaiDoan` | Giai doan thiet ke | `NCKT`, `TKKT`, `TKBVTC`, `FULL` |

**Vi du:** `2508_CM_KeG6_NCKT`, `2601_DeDieuCaMau_TKKT`

**Rieng khi doi ten hang loat folder cap 1 trong kho Archive nhieu du an** (theo yeu cau cu the cua nguoi dung), co the dung thu tu khac:

```
[DiaDanh]_[YY.MM]_[NoiDungConLai]
```

Vi du: `23.02_CM_KiemDinhNNSC_KeTanThuanL3` -> `CM_23.02_KiemDinhNNSC_KeTanThuanL3`. Luon xac nhan dinh dang cu the voi nguoi dung truoc (Nguyen tac 1) vi co 2 quy uoc khac nhau (dia danh truoc vs thoi gian truoc) tuy boi canh du an moi hay don dep archive cu.

---

## Hệ thống đánh số thư mục con

> **Nguyên tắc:** Chữ số đầu (hàng chục) = nhóm cấp 1 → Chữ số sau (hàng đơn vị) = mục con cấp 2

| Cấp 1 | Cấp 2 | Ý nghĩa |
|-------|-------|---------|
| `10.` | `11.` `12.` `13.`… | Pháp lý & Hợp đồng |
| `20.` | `21.` `22.` `23.`… | Đấu thầu |
| `30.` | `31.` `32.` `33.`… | Khảo sát |
| `40.` | `41.` `42.` `43.`… | Thiết kế |
| `50.` | `51.` `52.` `53.`… | Nghiệm thu & Thanh toán |
| `60.` | `61.` `62.` `63.`… | Văn thư |
| `INFO` | — | Thông tin dự án (luôn hiện đầu) |
| `REF` | — | Tài liệu tham khảo (hiện cuối) |

---

## Quy uoc dat ten file

### File lam viec noi bo (trong `41.ThucHien/`)

```
Tap[N].[x]_TenFile_R[x]-[TRANGTHAI]-YYYYMMDD.ext
```

| Thanh phan | Y nghia | Vi du |
|-----------|---------|-------|
| `Tap[N].[x]` | So tap + tieu muc | `Tap1.1`, `Tap2.3`, `Tap3.1` |
| `TenFile` | Ten loai ho so, khong ghi ten du an | `BaoCaoChinh`, `TM_ThietKe`, `BanVe_MatBang` |
| `R[x]` | So lan phat hanh | `R1`, `R2`, `R3` |
| `TRANGTHAI` | Trang thai phat hanh | `IFA`, `REV`, `APP` |
| `YYYYMMDD` | Ngay phat hanh | `20251217` |

**Ma trang thai:**
| Ma | Nghia | Dung khi |
|----|-------|---------|
| `IFA` | Issued for Approval -- Trinh tham tra | Nop ho so de tham dinh |
| `REV` | Revision -- Chinh sua sau tham tra | Chinh theo y kien tham dinh |
| `APP` | Approved -- Da phe duyet | Ho so da co quyet dinh phe duyet |

**Phan loai Tap:**
- `Tap1.x` -> Thuyet minh, bao cao (BaoCaoChinh, BaoCaoTomTat, TM_ThietKe, ChiDanThiCong...)
- `Tap2.x` -> Ban ve (BanVe_MatBang, BanVe_MatCat, BanVe_KetCau...)
- `Tap3.x` -> Du toan (DuToan_XayLap, DuToan_ThietBi...)

**Vi du:**
```
Tap1.1_BaoCaoChinh_R1-IFA-20251115.docx    <- Ban trinh tham tra lan 1
Tap1.1_BaoCaoChinh_R1-REV-20251210.docx   <- Sau khi chinh theo tham tra
Tap1.1_BaoCaoChinh_R1-APP-20251228.docx   <- Ban phe duyet
Tap2.3_BanVe_MatCat_R1-IFA-20251115.dwg   <- CAD: giu nguyen ten theo so hieu to
Tap3.1_DuToan_R1-IFA-20251115.xlsx        <- Du toan (khong doi noi dung)
```

### File phat hanh (trong `42.PhatHanh/ph1_YYMMDD/`)

File PDF khi nop ho so -- dat ten ngan gon theo so tap:

```
T[N]_TenTap.pdf
```

Vi du: `T1_BaoCaoChinh.pdf`, `T2_TomTat.pdf`, `T3_TMTKCS.pdf`, `T4_BanVe.pdf`

### File CAD va Excel du toan

**Giu nguyen ten goc** -- chi can dam bao nam dung folder:
- CAD `.dwg`, `.dxf`, `.bak` -> `41.ThucHien/BanVe_CAD/`
- Excel du toan -> `41.ThucHien/DuToan/`

### Van thu, cong van, bien ban

```
YYMMDD_TenVanBan.ext
```
Vi du: `251204_CV_XinTamUng.pdf`, `260103_BB_NghiemThu.pdf`

---

## Dat ten folder `42.PhatHanh/`

```
42.PhatHanh/
|-- ph1_251217/     <- Phat hanh lan 1, ngay 17/12/2025
|   |-- T1_BaoCaoChinh.pdf
|   |-- T2_TomTat.pdf
|   +-- T3_TMTKCS.pdf
+-- ph2_260326/     <- Phat hanh lan 2 (chi tap co thay doi)
    +-- T1_BaoCaoChinh.pdf
```

Ban hien hanh cua T2: van la o `ph1` (vi `ph2` khong co T2 -> khong doi).

---

## Script doi ten file

Dung `scripts/rename_files.py` de doi ten hang loat:

```bash
# Xem truoc (khong thuc thi)
python3 scripts/rename_files.py --root "<DUONG_DAN>" --preview

# Thuc thi
python3 scripts/rename_files.py --root "<DUONG_DAN>"
```

Script tu dong bo qua: `.dwg`, `.dxf`, `.bak`, file trong `DuToan/`, `BanVe_CAD/`, `42.PhatHanh/`, `_NopThau/`, file da co tien to `Tap[N].[x]_`.

