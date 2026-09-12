#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phan-loai-ho-so.py — phân loại file hồ sơ dự án vào đúng nhóm thư mục 00_input/.

Luật tất định, không gọi mô hình. Dùng cho cả file trên ổ đĩa lẫn danh sách
file lấy từ Google Drive (search_files trả JSON).

VÀO:  JSON là list các object có ít nhất khoá "title" (hoặc "name"),
      tuỳ chọn "fileSize", "mimeType", "id".
      Hoặc: một thư mục trên đĩa (dùng --thu-muc).
RA:   JSON bảng mapping — mỗi dòng: file → nhóm đề xuất → độ tin cậy → lý do.

    python3 phan-loai-ho-so.py --json ds-file.json --ra mapping.json
    python3 phan-loai-ho-so.py --thu-muc 00_input/ --ra mapping.json

BA MỨC TIN CẬY:
    chac      khớp nhiều dấu hiệu, hoặc dấu hiệu rất riêng  → tự xếp được
    doan      khớp một dấu hiệu yếu                          → nên hỏi người dùng
    khong_ro  không khớp gì                                  → BẮT BUỘC hỏi

Nguyên tắc: thà để "khong_ro" còn hơn đoán bừa rồi chôn file vào sai nhóm.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ────────────────────────────────────────────────────────────────────────────
# Danh mục nhóm — khớp cây 00_input/ của kiến trúc ba lớp
# ────────────────────────────────────────────────────────────────────────────
NHOM = {
    "10.PhapLy": {
        "manh": [r"\bQD[-_ ]?\d", r"quyet[- ]?dinh", r"quyết[- ]?định", r"\bQĐ[-_ ]?\d",
                 r"chu[- ]?truong", r"chủ[- ]?trương", r"phe[- ]?duyet", r"phê[- ]?duyệt",
                 r"\bTT[-_ ]?\d+/\d{4}", r"\bND[-_ ]?\d+/\d{4}", r"nghi[- ]?dinh",
                 r"cong[- ]?van", r"công[- ]?văn", r"\bCV[-_ ]?\d", r"giao[- ]?nhiem[- ]?vu"],
        "yeu": [r"phap[- ]?ly", r"pháp[- ]?lý", r"UBND", r"\bSo[- ]?Xay[- ]?dung"],
        "duoi": [".pdf", ".doc", ".docx"],
    },
    "20.KhaoSat-DiaHinh": {
        "manh": [r"dia[- ]?hinh", r"địa[- ]?hình", r"binh[- ]?do", r"bình[- ]?đồ",
                 r"trac[- ]?doc", r"trắc[- ]?dọc", r"trac[- ]?ngang", r"mat[- ]?cat[- ]?ngang",
                 r"toa[- ]?do", r"tọa[- ]?độ", r"\bTOPO\b"],
        "yeu": [r"khao[- ]?sat", r"khảo[- ]?sát", r"\bKS[-_ ]"],
        "duoi": [".pdf", ".doc", ".docx", ".dwg", ".kmz", ".kml", ".xls", ".xlsx"],
    },
    "30.KhaoSat-DiaChat": {
        "manh": [r"dia[- ]?chat", r"địa[- ]?chất", r"\bKSDC\b", r"\bKSĐC\b",
                 r"ho[- ]?khoan", r"hố[- ]?khoan", r"tru[- ]?ho[- ]?khoan",
                 r"\bSPT\b", r"\bCPT\b", r"co[- ]?ly", r"cơ[- ]?lý", r"\bVST\b"],
        "yeu": [r"thi[- ]?nghiem", r"thí[- ]?nghiệm"],
        "duoi": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
    },
    "ThuyVan": {
        "manh": [r"thuy[- ]?van", r"thủy[- ]?văn", r"thuỷ[- ]?văn", r"muc[- ]?nuoc",
                 r"mực[- ]?nước", r"trieu", r"triều", r"tan[- ]?suat", r"tần[- ]?suất",
                 r"khi[- ]?tuong", r"khí[- ]?tượng", r"hai[- ]?van", r"hải[- ]?văn",
                 r"\bBD3\b", r"\bBĐ3\b", r"song[- ]?gio", r"sóng[- ]?gió"],
        "yeu": [r"luu[- ]?luong", r"lưu[- ]?lượng", r"\bmua\b", r"mưa"],
        "duoi": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
    },
    "BanVe-PDF": {
        "manh": [r"ban[- ]?ve", r"bản[- ]?vẽ", r"\bBV[-_ ]?\d", r"\bA[0-3][-_ ]",
                 r"chi[- ]?tiet[- ]?ket[- ]?cau", r"mat[- ]?bang[- ]?tong[- ]?the"],
        "yeu": [r"\bTK\b", r"thiet[- ]?ke", r"thiết[- ]?kế"],
        "duoi": [".pdf", ".dwg", ".dxf"],
    },
    "AnhHienTruong": {
        "manh": [r"^IMG[-_ ]?\d", r"^DSC[-_ ]?\d", r"^\d{8}[-_ ]?\d{6}",
                 r"^Screenshot", r"hien[- ]?truong", r"hiện[- ]?trường",
                 r"anh[- ]?chup", r"ảnh[- ]?chụp"],
        "yeu": [r"\banh\b", r"\bảnh\b", r"photo"],
        "duoi": [".jpg", ".jpeg", ".png", ".heic", ".mp4", ".mov"],
    },
    "HoSo-Giai-Doan-Truoc": {
        "manh": [r"DXCTDT", r"ĐXCTĐT", r"DeXuatCTDT", r"\bDXCT\b", r"de[- ]?xuat[- ]?chu[- ]?truong",
                 r"đề[- ]?xuất[- ]?chủ[- ]?trương", r"\bBCNCKT\b", r"\bBCKTKT\b",
                 r"\bNCKT\b", r"\bTKKT\b", r"\bTKBVTC\b", r"bao[- ]?cao[- ]?chinh",
                 r"báo[- ]?cáo[- ]?chính", r"thuyet[- ]?minh", r"thuyết[- ]?minh"],
        "yeu": [r"giai[- ]?doan[- ]?truoc", r"\bTM\b"],
        "duoi": [".doc", ".docx", ".pdf"],
    },
    "DuToan-KhoiLuong": {
        "manh": [r"du[- ]?toan", r"dự[- ]?toán", r"khoi[- ]?luong", r"khối[- ]?lượng",
                 r"khai[- ]?toan", r"khái[- ]?toán", r"\bTMDT\b", r"\bTMĐT\b",
                 r"don[- ]?gia", r"đơn[- ]?giá", r"tien[- ]?luong", r"tiên[- ]?lượng"],
        "yeu": [r"\bDT\b", r"bang[- ]?tinh", r"bảng[- ]?tính"],
        "duoi": [".xls", ".xlsx", ".xlsm", ".pdf"],
    },
    "QuyHoach": {
        "manh": [r"quy[- ]?hoach", r"quy[- ]?hoạch", r"\bQHPK\b", r"\bQHCT\b",
                 r"1[-_/]500", r"1[-_/]2000"],
        "yeu": [],
        "duoi": [".pdf", ".doc", ".docx", ".dwg"],
    },
}

# Đuôi file rất riêng — tự nó đã đủ để xếp nhóm, không cần dấu hiệu trong tên
DUOI_RIENG = {
    ".kmz": "20.KhaoSat-DiaHinh", ".kml": "20.KhaoSat-DiaHinh",
    ".dwg": "BanVe-PDF", ".dxf": "BanVe-PDF",
    ".heic": "AnhHienTruong", ".mov": "AnhHienTruong", ".mp4": "AnhHienTruong",
}

RAC = re.compile(r"\.(bak|tmp|back|dwl|dwl2|log|db|ini)$|^~\$|Thumbs\.db", re.I)


def phan_loai(ten: str, duoi: str) -> tuple[str, str, str]:
    """Trả (nhom, do_tin_cay, ly_do)."""
    if RAC.search(ten):
        return ("_RAC", "chac", "file rác theo đuôi hoặc tiền tố")

    t = ten.lower()
    diem: dict[str, tuple[int, list[str]]] = {}

    for nhom, luat in NHOM.items():
        sm = [p for p in luat["manh"] if re.search(p, t, re.I)]
        sy = [p for p in luat["yeu"] if re.search(p, t, re.I)]
        khop_duoi = duoi.lower() in luat["duoi"]
        d = len(sm) * 3 + len(sy) * 1 + (1 if khop_duoi and (sm or sy) else 0)
        if d:
            dh = []
            if sm:
                dh.append(f"{len(sm)} dấu hiệu mạnh")
            if sy:
                dh.append(f"{len(sy)} dấu hiệu phụ")
            if khop_duoi:
                dh.append(f"đuôi {duoi}")
            diem[nhom] = (d, dh)

    if not diem:
        rieng = DUOI_RIENG.get(duoi.lower())
        if rieng:
            return (rieng, "chac", f"đuôi {duoi} chỉ dùng cho nhóm này")
        return ("_KHONG_RO", "khong_ro", "tên file không mang dấu hiệu nào nhận ra được")

    xep = sorted(diem.items(), key=lambda kv: -kv[1][0])
    nhat, (d1, dh1) = xep[0]

    # hai nhóm điểm sát nhau → không dám chắc
    if len(xep) > 1 and xep[1][1][0] >= d1 - 1:
        nhi = xep[1][0]
        return (nhat, "doan", f"khớp cả '{nhat}' và '{nhi}' gần ngang nhau — cần hỏi")

    tin = "chac" if d1 >= 3 else "doan"
    return (nhat, tin, ", ".join(dh1))


def main():
    ap = argparse.ArgumentParser(description="Phân loại file hồ sơ vào nhóm 00_input/")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--json", help="File JSON danh sách file (từ Drive search_files)")
    g.add_argument("--thu-muc", help="Thư mục trên đĩa cần quét")
    ap.add_argument("--ra", help="File JSON kết quả (mặc định in ra màn hình)")
    a = ap.parse_args()

    muc = []
    if a.json:
        raw = json.loads(Path(a.json).read_text(encoding="utf-8"))
        ds = raw.get("files", raw) if isinstance(raw, dict) else raw
        for f in ds:
            ten = f.get("title") or f.get("name") or ""
            if not ten:
                continue
            muc.append({"ten": ten, "id": f.get("id"), "kich_thuoc": f.get("fileSize")})
    else:
        for p in sorted(Path(a.thu_muc).rglob("*")):
            if p.is_file():
                muc.append({"ten": p.name, "id": str(p), "kich_thuoc": p.stat().st_size})

    kq = []
    for m in muc:
        duoi = Path(m["ten"]).suffix
        nhom, tin, ly_do = phan_loai(m["ten"], duoi)
        kq.append({**m, "nhom_de_xuat": nhom, "do_tin_cay": tin, "ly_do": ly_do})

    # phát hiện nghi trùng: cùng tên, hoặc cùng kích thước và tên gần giống
    theo_ten: dict[str, list] = {}
    for r in kq:
        theo_ten.setdefault(r["ten"].lower(), []).append(r)
    for ten, ds in theo_ten.items():
        if len(ds) > 1:
            for r in ds:
                r["nghi_trung"] = f"{len(ds)} file cùng tên"

    tk = {"tong": len(kq)}
    for t in ("chac", "doan", "khong_ro"):
        tk[t] = sum(1 for r in kq if r["do_tin_cay"] == t)
    tk["nghi_trung"] = sum(1 for r in kq if r.get("nghi_trung"))

    ra = {"tong_ket": tk, "mapping": kq}
    txt = json.dumps(ra, ensure_ascii=False, indent=2)
    if a.ra:
        Path(a.ra).write_text(txt, encoding="utf-8")
        print(f"Đã ghi {a.ra}")
    else:
        print(txt)

    print(f"\nTổng {tk['tong']} file — chắc {tk['chac']} · đoán {tk['doan']} · "
          f"không rõ {tk['khong_ro']} · nghi trùng {tk['nghi_trung']}", file=sys.stderr)
    if tk["doan"] or tk["khong_ro"]:
        print("⚠ Có file chưa xếp chắc chắn — PHẢI hỏi người dùng trước khi di chuyển.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
