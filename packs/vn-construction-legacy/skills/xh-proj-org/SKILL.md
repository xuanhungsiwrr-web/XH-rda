<!-- HISTORICAL ONLY: Do not activate this legacy skill or its provider policy. Use root skills and references/domain-workflow.md. -->
---
name: "xh-proj-org"
description: "Sap xep, to chuc va don dep thu muc ho so du an tu van thiet ke (thuy loi, de dieu, ke bo song, giao thong, ha tang) theo he thong chuan 10./20./30./40./50./60. Kich hoat ngay khi nguoi dung de cap den bat ky noi dung nao sau: \"sap xep du an\", \"to chuc thu muc\", \"don dep ho so\", \"cay thu muc du an\", \"tao folder du an moi\", \"doi ten file ho so\", \"XH_ProjOrg\", \"organize project\", \"cau truc thu muc\", \"folder du an\", \"dat ten file\", \"ho so thiet ke\", \"dọn dẹp archive\", \"HSPheDuyet\". Cung kich hoat khi nhac den du an BCNCKT / TKKT / TKBVTC ket hop voi tu \"thu muc\", \"ho so\", \"sap xep\". Day la skill chinh cho toan bo cong tac quan ly ho so du an cua to chuc."
---

# XH_ProjOrg -- To Chuc Thu Muc & Ho So Du An

Skill nay giup phan tich cau truc thu muc du an hien tai, de xuat va thuc thi viec to chuc lai theo he thong chuan. Ap dung cho moi du an tu van thiet ke: BCNCKT, TKKT, TKBVTC, ke, de dieu, cau, duong, ha tang. Cung ap dung cho viec don dep kho luu tru nhieu du an da hoan thanh (Archive/Completed).

---

## Nguyen tac bat buoc (luon ap dung)

**1. Hoi nguoi dung truoc khi gap van de khong ro.** Bat cu khi nao gap tinh huong khong the tu suy doan an toan -- vi du: khong chac file nao la "ban cuoi/da phe duyet", khong ro tieu chi chon giu ban nao khi co nhieu file trung ten nhung noi dung khac nhau, khong ro dinh dang doi ten cho mot nhom folder dac biet, khong chac mot folder co phai la 1 du an rieng le hay khong -- PHAI dung lai va hoi nguoi dung (dung AskUserQuestion hoac trinh bay bang de xuat) TRUOC khi thuc thi, dac biet neu thao tac la MOVE hoac XOA (kho hoan tac). Chi tu quyet dinh voi cac thao tac an toan, ro rang, co the hoan tac de dang (vi du: xoa file rac .bak/.tmp, gop 2 ban giong het 100% qua so sanh hash).

Khi gap nhieu von de khong ro cung luc, gom lai thanh 1 bang/danh sach de hoi mot lan, kem vi du cu the tu du lieu thuc te da quet duoc (khong hoi chung chung).

**2. Sau khi sap xep xong, lap danh muc tra cuu bang Excel co link truc tiep.** Sau khi hoan tat to chuc lai thu muc (xong Buoc 4), luon thuc hien Buoc 6 ben duoi: xuat 1 file Excel liet ke toan bo cay thu muc (toi thieu cap 1, nen co ca cap 2) kem hyperlink mo thang den tung folder, luu vao chinh thu muc goc da sap xep, de nguoi dung tra cuu / tim kiem nhanh ma khong can dao qua nhieu cap thu muc.

---

## Quy trinh lam viec

### Buoc 1 -- Thu thap thong tin

Truoc khi lam bat cu viec gi, xac nhan voi nguoi dung:

1. **Duong dan thu muc goc** can sap xep (hoac ten du an moi can tao)
2. **Giai doan du an**: BCNCKT/FS, TKKT, TKBVTC, hay ket hop -- hoac neu la kho Archive nhieu du an: pham vi don dep (xoa rac, gop trung lap, tao HSPheDuyet, doi ten folder cap 1...)
3. **Nhiem vu cu the**: don dep folder cu, tao folder moi, hay doi ten file
4. **Du an co dau thau khong?** -- neu khong thi bo `20.DauThau/`

### Buoc 2 -- Doc va phan tich cau truc hien tai

```bash
# Doc cay thu muc
find "<DUONG_DAN>" -type d | sort

# Doc danh sach file
find "<DUONG_DAN>" -type f | sort
```

Sau khi doc xong:
- Nhan dang cac nhom file theo noi dung -> lap bang mapping cu -> moi
- File khong ro loai -> **hoi nguoi dung tung file mot**
- Ghi nhan file CAD (.dwg, .dxf, .bak) va Excel du toan -> **khong doi ten**
- Neu don dep kho Archive nhieu du an: quet file trung lap bang **so sanh hash noi dung** (khong chi dua vao ten file giong nhau -- nhieu file cung ten trong nganh nay thuong la cac phuong an/phien ban KHAC NHAU, vd dinh muc theo nhieu quyet dinh khac nhau). Chi coi la trung lap that khi hash giong het.

### Buoc 3 -- Lap ke hoach va xac nhan

Doc cay thu muc chuan: `references/cay-thu-muc.md`

Trinh bay bang mapping va cau truc moi cho nguoi dung **xac nhan truoc** khi thuc thi. Ap dung dung Nguyen tac 1 o tren: neu co nhieu diem khong ro (vi du: nhieu folder co ve la "ban phe duyet cuoi" nhung khong chac chan, hoac ten folder khong ro dia danh/thoi gian), gom thanh bang de nguoi dung chon 1 lan, chi tu thuc hien phan da ro rang, con lai chờ xac nhan.

**Nguyen tac tao folder:**
- **Cap 1** (10., 20., ...): Bo han folder neu du an khong co noi dung, nhung **giu nguyen so thu tu** cua cac folder con lai (vi du: khong co dau thau -> bo `20.DauThau/`, nhung folder tiep theo van la `30.KhaoSat/`)
- **Cap 2 tro xuong**: Chi tao khi co file phu hop; bo ca folder lan so thu tu neu khong can

### Buoc 4 -- Tao va thuc thi script bash

Script phai:
1. Tao cau truc thu muc moi (`mkdir -p`)
2. Di chuyen file vao dung vi tri (`mv`)
3. Doi ten file theo quy uoc (dung `scripts/rename_files.py`)
4. Voi rieng nhiem vu don dep kho Archive: duoc phep xoa file rac (.bak/.tmp/.back/dwl/dwl2/plot.log/hardcopy.log/Thumbs.db...) va xoa ban trung lap that (giu 1 ban theo tieu chi da thong nhat voi nguoi dung, vd ban mtime moi nhat) -- nhung van phai xac nhan truoc voi nguoi dung ve tieu chi giu/xoa (Nguyen tac 1)
5. Neu lenh `rm`/`os.remove` bao loi "Operation not permitted" tren folder da ket noi:
   - Phien Cowork chay tren may nguoi dung: goi `mcp__cowork__allow_cowork_file_delete` voi duong dan thu muc.
   - **Phien chay tren cloud, thao tac qua cau noi thiet bi** (truong hop thuong gap tu 25/08/2026): goi
     `mcp__remote-devices__device_request_delete_permission` voi cac thu muc goc can bat quyen xoa.
     Moi lan goi deu hien hop thoai cho nguoi dung bam. Neu bi tu choi hoac khong ai tra loi:
     **khong xoa** — `mv` file vao `_to_delete/` cung thu muc goc roi bao nguoi dung tu xoa.

Kiem tra sau khi chay:
```bash
# Xac nhan khong con file sot trong folder cu
find "<FOLDER_CU>" -not -type d
```

### Buoc 5 -- Bao cao va huong dan thu cong

- In cay thu muc moi bang `find ... -type d | sort`
- Nhac xoa folder vo rong trong File Explorer (neu `rm -rf` that bai do Google Drive)
- Nhac doi ten folder goc trong File Explorer neu can

### Buoc 6 -- Lap danh muc Excel co link truc tiep (bat buoc, xem Nguyen tac 2)

Sau khi cau truc da on dinh, tao 1 file Excel (dat ten vd `DanhMuc_<TenKhoLuuTru>.xlsx`) luu ngay tai thu muc goc vua sap xep, gom toi thieu:

- **Sheet danh muc cap 1**: STT, ten folder du an, so file, dung luong, cot "Mo folder" la hyperlink mo truc tiep den folder do
- **Sheet cay thu muc cap 2** (neu huu ich): du an + ten thu muc con + hyperlink
- Neu co du lieu can nguoi dung tu xem lai (vd nhom file cung ten khac noi dung chua xu ly): them 1 sheet rieng liet ke day du de tra cuu
- Neu co xoa file (rac/trung lap): them 1 sheet log ghi lai duong dan + kich thuoc file da xoa, de minh bach/audit

**Cach tao hyperlink toi folder tren may Windows cua nguoi dung** (dung openpyxl, xem skill `xlsx`):

```python
import urllib.parse
def to_file_uri(base_windows_path, rel_path):
    full = base_windows_path + "\\" + rel_path.replace('/', '\\')
    parts = full.split('\\')
    # KHONG encode phan "O:\" (o dia) vi dau ":" phai giu nguyen trong file URI
    encoded = [parts[0]] + [urllib.parse.quote(p) for p in parts[1:]]
    return "file:///" + "/".join(encoded)

cell.hyperlink = to_file_uri(r"D:\GDrive\...", "TenDuAn/SubFolder")
```

`base_windows_path` la duong dan Windows that (vd `D:\GDrive\03-Projects_Archive\Completed`) ma nguoi dung nhin thay trong File Explorer -- **khong** dung duong dan `/sessions/.../mnt/...` cua sandbox trong hyperlink, vi day la duong dan chi bash nhin thay, khong ton tai tren may nguoi dung.

---

---

## ⚠️ Hai he danh so — khong duoc lan

Plugin nay dung **hai he thu muc khac nhau, khac vai**:

| He | Dung o dau | Dau hieu | Vi du |
|---|---|---|---|
| **He ho so du an** (skill nay) | Thu muc luu tru ho so cua cong ty, tren o dia du an | dung **dau cham** | `10.PhapLy/` `20.DauThau/` `30.KhaoSat/` `41.ThucHien/` `42.PhatHanh/` |
| **He xuong viet bao cao** (`xh-tuvan`) | Kho `D:\ClaudeAI\XuongBaoCao\` | dung **dau gach ngang** | `10-DangViet/` `20-Khuon/` `40-Script/` `50-Spec-Exemplar/` `60-VanPhong/` |

Trong mot du an dang viet, thu muc `10-DangViet/<MaDuAn>/00_input/` co the chua cac nhom
`10.PhapLy/`, `20.KhaoSat-DiaHinh/`, `30.KhaoSat-DiaChat/` — **do la he ho so du an nam long
trong he xuong viet**, khong phai loi. Khong "chuan hoa" mot he ve he kia.

*Ghi chu them 25/08/2026 khi nhap skill nay tu plugin `xh-tuvan-v2` sang `xh-tuvan`.*


## Cấu trúc thư mục và quy ước đặt tên

**Đọc chi tiết tại `references/quy-uoc-dat-ten.md`** — gồm cây thư mục chuẩn, hệ đánh số, quy ước đặt tên thư mục gốc, đặt tên file làm việc/phát hành, đặt tên folder `42.PhatHanh/`, và script đổi tên.

---

## Luu y Google Drive / Windows

- Bash sandbox doc file qua duong dan mount: `/sessions/.../mnt/TenFolder/`
- `mv` hoat dong binh thuong trong cung mount point
- Neu thu muc duoc ket noi qua Cowork (`request_cowork_directory`), lenh xoa (`rm`, `os.remove`) co the bao loi "Operation not permitted" o lan thu dau -- day la co che bao ve mac dinh. Goi `mcp__cowork__allow_cowork_file_delete` voi duong dan thu muc de xin quyen xoa, sau do thao tac xoa se hoat dong binh thuong.
- `rm -rf` folder rong co the bao loi do Google Drive sync -> nhac user xoa thu cong trong File Explorer
- Doi ten folder goc: co the thuc hien truc tiep bang `os.rename` qua Cowork sau khi da ket noi thu muc; neu that bai moi can nhac lam thu cong trong File Explorer
- Khi tao hyperlink Excel: dung duong dan Windows that (vd `D:\GDrive\...`) ma nguoi dung thay tren may ho, khong dung duong dan sandbox `/sessions/.../mnt/...`

