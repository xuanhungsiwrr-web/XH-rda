#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qc-check.py — Tầng 1: kiểm tra TẤT ĐỊNH hồ sơ tư vấn thiết kế.

Chạy trước khi gọi agent xh-qc. Không dùng AI, không tốn token, không quên.
Đọc trực tiếp .docx (không cần python-docx) hoặc .md.

    python qc-check.py BaoCao.docx
    python qc-check.py BaoCao.docx --rules qc-rules.yaml --facts _facts.yaml
    python qc-check.py 10_content/ --json ketqua.json

SÁU LUẬT (rút từ 28 điểm không khớp của BCKTKT Kè Khánh Hưng):
  L1 SO_LECH          mọi số của cùng một chỉ tiêu, xuất hiện ≥2 lần, phải bằng nhau
  L2 VAN_LECH_BANG    số trong văn phải khớp ô tương ứng trong bảng
  L3 BANG_SAI_TEN     tiêu đề bảng phải khớp đại lượng nằm trong bảng
  L4 NGHI_MAT_PHAY    hai lần nêu cùng chỉ tiêu chênh đúng 10 lần → nghi mất dấu phẩy
  L5 RANG_BUOC        ràng buộc vật lý (lan can − vỉa hè ≥ 1,10m; đỉnh kè > MNTK; tổng đoạn = tuyến)
  L6 CHO_TRONG        còn dấu lửng, {{TODO}}, {{fact:}}, ký tự vùng dùng riêng U+E000–U+F8FF

  Phụ: L7 QUY_UOC     dấu thập phân lẫn lộn chấm/phẩy, "oC" thay cho "°C"
       L8 CHUA_DUYET  bản thảo dùng số đang ở trạng thái unverified trong _facts.yaml
       L10 SO_MUON    số mượn dự án khác thiếu dẫn nguồn / thiếu khuyến cáo khảo sát bổ sung
       L9 LOGIC_VAN   đếm tháng sai · "gần/khoảng" đi với số lẻ đến hàng đơn vị
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# ════════════════════════════════════════════════════════════════════════════
# 1. DANH MỤC CHỈ TIÊU MẶC ĐỊNH — công trình kè / đê / lộ GTNT
#    Ghi đè bằng --rules qc-rules.yaml khi làm loại công trình khác.
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_RULES = {
    "chi_tieu": {
        "chieu_dai_ke": {
            "ten": "Chiều dài kè",
            "nhan": ["chiều dài kè", "tổng chiều dài kè", "chiều dài tuyến kè",
                     "chiều dài toàn tuyến kè", "kè có chiều dài", "kè dài"],
            "mau": [r"tuyến kè[^.;]{0,90}?tổng chiều dài(?:\s*khoảng)?\s*([\d.,]+)\s*m",
                    r"kè[^.;]{0,40}?tổng chiều dài(?:\s*khoảng)?\s*([\d.,]+)\s*m"],
            "don_vi": "m", "hop_ly": [5, 20000], "dung_sai": 0.005,
        },
        "chieu_dai_lo": {
            "ten": "Chiều dài lộ giao thông nông thôn",
            "nhan": ["chiều dài lộ", "chiều dài tuyến lộ", "chiều dài đường",
                     "lộ giao thông nông thôn dài", "tổng chiều dài lộ"],
            "mau": [r"tuyến lộ[^.;]{0,90}?tổng chiều dài(?:\s*khoảng)?\s*([\d.,]+)\s*m",
                    r"nâng cấp[^.;]{0,60}?lộ[^.;]{0,60}?tổng chiều dài[:\s]*([\d.,]+)\s*m"],
            "don_vi": "m", "hop_ly": [5, 20000], "dung_sai": 0.005,
        },
        "muc_nuoc_thiet_ke": {
            "ten": "Mực nước thiết kế P=2%",
            "nhan": ["mực nước thiết kế", "mntk", "mực nước p=2%", "mực nước ứng với p=2%"],
            "don_vi": "m", "hop_ly": [-5, 20], "dung_sai": 0.005,
        },
        "cao_trinh_dinh_ke": {
            "ten": "Cao trình đỉnh kè",
            "nhan": ["cao trình đỉnh kè", "đỉnh kè ở cao trình", "cao độ đỉnh kè"],
            "don_vi": "m", "hop_ly": [-5, 20], "dung_sai": 0.005,
        },
        "cao_trinh_via_he": {
            "ten": "Cao trình vỉa hè",
            "nhan": ["cao trình vỉa hè", "vỉa hè cao trình", "cao độ vỉa hè",
                     "vỉa hè ở cao trình"],
            "don_vi": "m", "hop_ly": [-5, 20], "dung_sai": 0.005,
        },
        "cao_trinh_lan_can": {
            "ten": "Cao trình đỉnh lan can",
            "nhan": ["cao trình đỉnh lan can", "cao trình đỉnh tay vịn",
                     "đỉnh lan can ở cao trình"],
            # KHÔNG suy từ "cao trình đỉnh" nằm gần chữ "lan can": trong hồ sơ thật
            # đó thường là cao độ đỉnh kè, tức CHÂN lan can. Chỉ nhận khi văn bản
            # nói thẳng "cao trình đỉnh lan can".
            "don_vi": "m", "hop_ly": [-5, 20], "dung_sai": 0.005,
        },
        "van_toc_gio_max": {
            "ten": "Vận tốc gió cực đại",
            "nhan": ["vận tốc gió cực đại", "vận tốc gió lớn nhất", "gió cực đại",
                     "vmax", "tốc độ gió lớn nhất"],
            "don_vi": "m/s", "hop_ly": [0.5, 80], "dung_sai": 0.01,
        },
        "boc_hoi_nam": {
            "ten": "Lượng bốc hơi năm",
            "nhan": ["bốc hơi năm", "lượng bốc hơi", "bốc hơi trung bình năm",
                     "tổng lượng bốc hơi"],
            "don_vi": "mm", "hop_ly": [100, 4000], "dung_sai": 0.01,
        },
        "luong_mua_nam": {
            "ten": "Lượng mưa năm",
            "nhan": ["lượng mưa năm", "lượng mưa trung bình năm", "mưa bình quân năm",
                     "tổng lượng mưa năm"],
            "mau": [r"lượng mưa trung bình(?:\s*khoảng)?\s*([\d.,]+)\s*(?:-|–|÷)?\s*[\d.,]*\s*mm"],
            "don_vi": "mm", "hop_ly": [100, 6000], "dung_sai": 0.01,
        },
        "nhiet_do_tb_nam": {
            "ten": "Nhiệt độ trung bình năm",
            "nhan": ["nhiệt độ trung bình năm", "nhiệt độ bình quân năm",
                     "nhiệt độ trung bình hàng năm"],
            "mau": [r"nhiệt độ[^.]{0,45}?trung bình\s*([\d.,]+)\s*(?:°|o)?\s*C"],
            "don_vi": "°C", "hop_ly": [10, 40], "dung_sai": 0.01,
        },
        "do_am_max": {
            "ten": "Độ ẩm lớn nhất",
            "nhan": ["độ ẩm lớn nhất", "độ ẩm cao nhất", "độ ẩm max"],
            "don_vi": "%", "hop_ly": [30, 100], "dung_sai": 0.01,
        },
        "do_am_min": {
            "ten": "Độ ẩm nhỏ nhất",
            "nhan": ["độ ẩm nhỏ nhất", "độ ẩm thấp nhất", "độ ẩm min"],
            "don_vi": "%", "hop_ly": [10, 100], "dung_sai": 0.01,
        },
        "mac_bt_ban_chan": {
            "ten": "Mác bê tông bản chắn đất",
            "nhan": ["bản chắn đất", "bản chắn bê tông", "mác bê tông bản chắn"],
            "don_vi": "M", "hop_ly": [100, 600], "dung_sai": 0.0,
        },
        "be_rong_via_he": {
            "ten": "Bề rộng vỉa hè",
            "nhan": ["bề rộng vỉa hè", "vỉa hè rộng", "chiều rộng vỉa hè"],
            "don_vi": "m", "hop_ly": [0.5, 20], "dung_sai": 0.005,
        },
    },

    # Ràng buộc vật lý — biểu thức chỉ dùng tên chỉ tiêu ở trên và số.
    "rang_buoc": [
        {
            "bieu_thuc": "cao_trinh_lan_can - cao_trinh_via_he >= 1.10",
            "thong_diep": ("Lan can phải cao ≥ 1,10m so với mặt vỉa hè. "
                           "Kiểm lại: cao trình nêu có đúng là ĐỈNH lan can không, "
                           "hay là đỉnh kè tức chân lan can"),
            "muc": "canh_bao",
        },
        {
            "bieu_thuc": "cao_trinh_dinh_ke > muc_nuoc_thiet_ke",
            "thong_diep": "Cao trình đỉnh kè phải cao hơn mực nước thiết kế",
            "muc": "nghiem_trong",
        },
        {
            "bieu_thuc": "do_am_max > do_am_min",
            "thong_diep": "Độ ẩm lớn nhất phải lớn hơn độ ẩm nhỏ nhất",
            "muc": "canh_bao",
        },
    ],

    # Bảng phải chứa đại lượng đúng với tên bảng.
    "bang_dai_luong": {
        "độ ẩm":     {"phai_co": ["%"],            "khong_duoc_chi_co": ["oc", "°c", "toc", "tbq"]},
        "nhiệt độ":  {"phai_co": ["oc", "°c", "t"], "khong_duoc_chi_co": []},
        "lượng mưa": {"phai_co": ["mm", "x"],       "khong_duoc_chi_co": []},
        "bốc hơi":   {"phai_co": ["mm", "z"],       "khong_duoc_chi_co": []},
        "gió":       {"phai_co": ["m/s", "v"],      "khong_duoc_chi_co": []},
    },

    # Chuỗi không được còn trong bản nộp.
    "cho_trong": [
        {"regex": r"\{\{\s*TODO", "ma": "CON_TODO", "muc": "nghiem_trong",
         "thong_diep": "Còn placeholder {{TODO:...}} chưa xử lý"},
        {"regex": r"\{\{\s*fact\s*:", "ma": "CON_FACT", "muc": "nghiem_trong",
         "thong_diep": "Còn {{fact:...}} chưa được render thay số"},
        {"regex": r"\{\{[A-Z_]+\}\}", "ma": "CON_PLACEHOLDER", "muc": "nghiem_trong",
         "thong_diep": "Còn placeholder bìa/header chưa thay"},
        {"regex": r"(số|Số|ngày|Ngày)\s*:?\s*[.…]{2,}", "ma": "SO_DE_TRONG", "muc": "nghiem_trong",
         "thong_diep": "Số hiệu / ngày tháng để trống bằng dấu lửng — phải dùng {{TODO:...}}"},
        {"regex": r"[.…]{3,}\s*/\s*\S", "ma": "SO_DE_TRONG", "muc": "nghiem_trong",
         "thong_diep": "Số hiệu / ngày tháng để trống bằng dấu lửng — phải dùng {{TODO:...}}"},
    ],
}

MUC_NANG = {"nghiem_trong": 2, "canh_bao": 1}


# ════════════════════════════════════════════════════════════════════════════
# 2. ĐỌC FILE
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class Khoi:
    """Một khối văn bản: đoạn văn hoặc bảng."""
    loai: str                       # 'p' | 'tbl'
    text: str = ""
    hang: list = field(default_factory=list)   # với bảng: list[list[str]]
    stt: int = 0
    de_muc: str = ""                # đề mục gần nhất phía trên
    la_heading: bool = False


def _text_cua_p(p) -> str:
    ra = []
    for node in p.iter():
        if node.tag == W + "t" and node.text:
            ra.append(node.text)
        elif node.tag == W + "tab":
            ra.append(" ")
        elif node.tag in (W + "br", W + "cr"):
            ra.append(" ")
        elif node.tag == W + "sym":
            # ÷ ± … font Symbol nằm trong w:sym, không phải w:t.
            ch = node.get(W + "char")
            if ch:
                try:
                    ra.append(chr(int(ch, 16)))
                except ValueError:
                    pass
    return "".join(ra)


def doc_docx(path: str) -> list[Khoi]:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find(W + "body")
    khoi, stt, de_muc = [], 0, ""
    if body is None:
        return khoi
    for el in body:
        if el.tag == W + "p":
            txt = _text_cua_p(el).strip()
            pstyle = el.find(f"{W}pPr/{W}pStyle")
            style = pstyle.get(W + "val", "") if pstyle is not None else ""
            heading = style.lower().startswith("heading") or bool(
                re.match(r"^\d+(\.\d+)*\.?\s+\S", txt)) and len(txt) < 120
            if not txt:
                continue
            stt += 1
            if heading:
                de_muc = txt[:70]
            khoi.append(Khoi("p", txt, stt=stt, de_muc=de_muc, la_heading=heading))
        elif el.tag == W + "tbl":
            hang = []
            for tr in el.findall(W + "tr"):
                o = []
                for tc in tr.findall(W + "tc"):
                    o.append(" ".join(_text_cua_p(p) for p in tc.findall(W + "p")).strip())
                hang.append(o)
            stt += 1
            khoi.append(Khoi("tbl", "", hang=hang, stt=stt, de_muc=de_muc))
    return khoi


def doc_markdown(path: str) -> list[Khoi]:
    khoi, de_muc, stt = [], "", 0
    with open(path, encoding="utf-8") as f:
        buf, trong_bang, hang = [], False, []
        for line in f:
            raw = line.rstrip("\n")
            if raw.strip().startswith("|"):
                trong_bang = True
                o = [c.strip() for c in raw.strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in o if c):
                    hang.append(o)
                continue
            if trong_bang and hang:
                stt += 1
                khoi.append(Khoi("tbl", hang=hang, stt=stt, de_muc=de_muc))
                hang, trong_bang = [], False
            if raw.startswith("#"):
                de_muc = raw.lstrip("# ").strip()[:70]
                stt += 1
                khoi.append(Khoi("p", de_muc, stt=stt, de_muc=de_muc, la_heading=True))
            elif raw.strip():
                buf.append(raw)
            elif buf:
                stt += 1
                khoi.append(Khoi("p", " ".join(buf), stt=stt, de_muc=de_muc))
                buf = []
        if buf:
            stt += 1
            khoi.append(Khoi("p", " ".join(buf), stt=stt, de_muc=de_muc))
        if hang:
            stt += 1
            khoi.append(Khoi("tbl", hang=hang, stt=stt, de_muc=de_muc))
    return khoi


def doc_nguon(path: str) -> tuple[list[Khoi], str]:
    if os.path.isdir(path):
        gop, dem = [], 0
        for ten in sorted(os.listdir(path)):
            if ten.endswith(".md"):
                for k in doc_markdown(os.path.join(path, ten)):
                    k.stt += dem
                    k.de_muc = f"{ten} · {k.de_muc}"
                    gop.append(k)
                dem = gop[-1].stt if gop else dem
        return gop, "thư mục .md"
    if path.lower().endswith(".docx"):
        return doc_docx(path), ".docx"
    return doc_markdown(path), ".md"


# ════════════════════════════════════════════════════════════════════════════
# 3. SỐ HỌC — đọc số theo quy ước Việt Nam
# ════════════════════════════════════════════════════════════════════════════

SO_RE = re.compile(r"[+\-−]?\d{1,3}(?:\.\d{3})+(?:,\d+)?|[+\-−]?\d+(?:[.,]\d+)?")


def doc_so(s: str) -> float | None:
    """'1.875' → 1875 ·  '4,50' → 4.5 ·  '27.8' → 27.8 ·  '+1,30' → 1.3"""
    s = s.strip().replace("−", "-").replace(" ", "")
    if not s or not re.search(r"\d", s):
        return None
    try:
        if "," in s:                       # phẩy = thập phân, chấm = hàng nghìn
            return float(s.replace(".", "").replace(",", "."))
        if s.count(".") == 1:
            nguyen, le = s.split(".")
            # '1.875' → hàng nghìn ; '27.8' → thập phân
            if len(le) == 3 and len(nguyen.lstrip("+-")) <= 3:
                return float(nguyen + le)
            return float(s)
        return float(s.replace(".", ""))
    except ValueError:
        return None


def viet_so(x: float) -> str:
    if x == int(x):
        if abs(x) < 100:
            return f"{int(x)},00"
        return f"{int(x):,}".replace(",", ".")
    return f"{x:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


# ════════════════════════════════════════════════════════════════════════════
# 4. TRÍCH GIÁ TRỊ CHỈ TIÊU
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class Diem:
    chi_tieu: str
    gia_tri: float
    nguon: str        # 'van' | 'bang'
    stt: int
    de_muc: str
    trich: str


def _chuan(s: str) -> str:
    s = unicodedata.normalize("NFC", s).lower()
    return re.sub(r"\s+", " ", s)


DON_VI_RE = {
    "m":    r"\s?m(?![a-zà-ỹ/²³])",
    "mm":   r"\s?mm\b",
    "%":    r"\s?%",
    "m/s":  r"\s?m/s",
    "°C":   r"\s?(?:°|o)\s?C\b",
    "M":    None,          # mác bê tông: tiền tố M ngay trước số
}

NHIEU_TU_DEM = re.compile(
    r"(đoạn|hàng|cấp|loại|số|chương|mục|tháng|năm|trạm|hình|bảng|lần|cột|hố|lớp|"
    r"phương án|tuyến số)\s*$", re.I)


def _cham_diem(cua_so: str, m: re.Match, don_vi: str) -> int:
    """Số nào trong cửa sổ là giá trị của chỉ tiêu — không phải số thứ tự."""
    d = 0
    txt = m.group()
    sau = cua_so[m.end(): m.end() + 6]
    truoc = cua_so[max(0, m.start() - 14): m.start()]
    pat = DON_VI_RE.get(don_vi)
    if don_vi == "M":
        d += 4 if truoc.rstrip().endswith(("M", "m")) else -1
    elif pat and re.match(pat, sau):
        d += 4
    if txt[0] in "+-−":
        d += 3
    if "," in txt or "." in txt:
        d += 1
    if NHIEU_TU_DEM.search(truoc):
        d -= 4
    d -= m.start() // 25          # số càng xa nhãn càng ít khả năng
    return d


LY_TRINH_RE = re.compile(r"[KkLl]\s?\d+\s?\+\s?\d+")
TAN_SUAT_RE = re.compile(r"(?:P\s*=\s*|tần suất\s+)\d+(?:[.,]\d+)?\s*%", re.I)
MA_HIEU_RE = re.compile(r"\b(?:M|B|D|PC|K|TCVN|QCVN)\s?\d+(?:[.,]\d+)?", re.I)
NGOAC_KEP_RE = re.compile(r"\{\{[^}]*\}\}")


def _che(s: str) -> str:
    """Che lý trình (K0+120) và placeholder ({{fact:...}}) — không phải giá trị chỉ tiêu."""
    s = LY_TRINH_RE.sub(lambda m: "·" * len(m.group()), s)
    s = TAN_SUAT_RE.sub(lambda m: "·" * len(m.group()), s)
    return NGOAC_KEP_RE.sub(lambda m: "·" * len(m.group()), s)


def _so_tot_nhat(cua_so: str, cfg: dict) -> tuple[float, str] | None:
    cua_so = _che(cua_so)
    ung_vien = []
    lo, hi = cfg.get("hop_ly", [-1e9, 1e9])
    for m in SO_RE.finditer(cua_so):
        v = doc_so(m.group())
        if v is None:
            continue
        if not (lo <= abs(v) <= hi if lo >= 0 else lo <= v <= hi):
            continue
        ung_vien.append((_cham_diem(cua_so, m, cfg.get("don_vi", "")), -m.start(), v, m.group()))
    if not ung_vien:
        return None
    ung_vien.sort(reverse=True)
    return ung_vien[0][2], ung_vien[0][3]


def trich_chi_tieu(khoi: list[Khoi], rules: dict) -> list[Diem]:
    diem: list[Diem] = []
    thay: set = set()
    ct = rules["chi_tieu"]

    for k in khoi:
        if k.loai == "p":
            low = _chuan(k.text)
            # (a) mẫu regex riêng — dùng khi nhãn + cửa sổ không đủ chính xác
            for ma, cfg in ct.items():
                for mau in cfg.get("mau", []):
                    for mm in re.finditer(mau, k.text, re.I | re.S):
                        v = doc_so(mm.group(1))
                        if v is None:
                            continue
                        lo, hi = cfg.get("hop_ly", [-1e9, 1e9])
                        if not (lo <= abs(v) <= hi if lo >= 0 else lo <= v <= hi):
                            continue
                        khoa = (ma, k.stt, round(v, 6))
                        if khoa in thay:
                            continue
                        thay.add(khoa)
                        diem.append(Diem(ma, v, "van", k.stt, k.de_muc,
                                         mm.group(0)[:110].strip()))
            # (b) nhãn + cửa sổ
            for ma, cfg in ct.items():
                for nhan in cfg["nhan"]:
                    m = re.search(re.escape(_chuan(nhan)), low)
                    if not m:
                        continue
                    kq = _so_tot_nhat(k.text[m.end(): m.end() + 80], cfg)
                    if not kq:
                        continue
                    v, _ = kq
                    khoa = (ma, k.stt, round(v, 6))
                    if khoa in thay:
                        break
                    thay.add(khoa)
                    trich = k.text[max(0, m.start() - 12): m.end() + 62].strip()
                    diem.append(Diem(ma, v, "van", k.stt, k.de_muc, trich))
                    break
        else:
            # caption bảng (đoạn "Bảng ..." liền trên hoặc liền dưới)
            cap = ""
            i_k = khoi.index(k) if k in khoi else -1
            for j in (i_k - 1, i_k + 1):
                if 0 <= j < len(khoi) and khoi[j].loai == "p":
                    t = khoi[j].text.strip()
                    if re.match(r"^(Bảng|Biểu)\s", t, re.I):
                        cap = t
                        break
            ma_cap = None
            if cap:
                lowc = _chuan(cap)
                for ma_, cfg_ in ct.items():
                    if any(_chuan(n) in lowc for n in cfg_["nhan"]):
                        ma_cap = (ma_, cfg_)
                        break
            if ma_cap:
                ma_, cfg_ = ma_cap
                lo_, hi_ = cfg_.get("hop_ly", [-1e9, 1e9])
                # ô "Năm" / "Tổng" / "TB" trong hàng tiêu đề → lấy đúng cột đó
                cot_nam = None
                for hang in k.hang[:2]:
                    for c_, o_ in enumerate(hang):
                        if re.fullmatch(r"\s*(năm|cả năm|tổng|tb|trung bình)\s*",
                                        _chuan(o_)):
                            cot_nam = c_
                            break
                    if cot_nam is not None:
                        break
                for r_, hang in enumerate(k.hang):
                    o_list = [hang[cot_nam]] if (cot_nam is not None and cot_nam < len(hang)) else []
                    for cell in o_list:
                        mm = SO_RE.search(_che(cell))
                        if not mm:
                            continue
                        v = doc_so(mm.group())
                        if v is None:
                            continue
                        if not (lo_ <= abs(v) <= hi_ if lo_ >= 0 else lo_ <= v <= hi_):
                            continue
                        khoa = (ma_, k.stt, round(v, 6))
                        if khoa in thay:
                            continue
                        thay.add(khoa)
                        diem.append(Diem(ma_, v, "bang", k.stt, k.de_muc,
                                         f"{cap[:50]} · cột 'Năm': " + " | ".join(hang)[:70]))
            for r, hang in enumerate(k.hang):
                nhan_o = None
                for o in hang:
                    lowo = _chuan(o)
                    for ma, cfg in ct.items():
                        if any(_chuan(n) in lowo for n in cfg["nhan"]):
                            nhan_o = (ma, cfg, o)
                            break
                    if nhan_o:
                        break
                if not nhan_o:
                    continue
                ma, cfg, o_nhan = nhan_o
                lo, hi = cfg.get("hop_ly", [-1e9, 1e9])
                for cell in hang:
                    if cell is o_nhan:
                        continue
                    for m in SO_RE.finditer(_che(cell)):
                        v = doc_so(m.group())
                        if v is None:
                            continue
                        if not (lo <= abs(v) <= hi if lo >= 0 else lo <= v <= hi):
                            continue
                        khoa = (ma, k.stt, round(v, 6))
                        if khoa in thay:
                            continue
                        thay.add(khoa)
                        diem.append(Diem(ma, v, "bang", k.stt, k.de_muc,
                                         f"bảng, hàng {r + 1}: " + " | ".join(hang)[:90]))
    return diem


# ════════════════════════════════════════════════════════════════════════════
# 5. CÁC LUẬT
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class Loi:
    ma: str
    muc: str
    de_muc: str
    stt: int
    thong_diep: str
    trich: str = ""

    def dong(self) -> str:
        dau = "[!!]" if self.muc == "nghiem_trong" else "[! ]"
        vt = f"{self.de_muc[:38]:38s}" if self.de_muc else " " * 38
        return f"{dau} {self.ma:16s} {vt} {self.thong_diep}"


def _khac_nhau(vals: list[float], dung_sai: float) -> bool:
    lo, hi = min(vals), max(vals)
    if hi == 0:
        return lo != 0
    return (hi - lo) / abs(hi) > max(dung_sai, 1e-9)


def luat_1_2_4(diem: list[Diem], rules: dict) -> list[Loi]:
    """L1 lệch giữa các mục · L2 văn lệch bảng · L4 nghi mất dấu phẩy."""
    loi, ct = [], rules["chi_tieu"]
    theo_ma: dict[str, list[Diem]] = {}
    for d in diem:
        theo_ma.setdefault(d.chi_tieu, []).append(d)

    for ma, ds in theo_ma.items():
        cfg = ct[ma]
        ds_sai = cfg.get("dung_sai", 0.005)
        van = [d for d in ds if d.nguon == "van"]
        bang = [d for d in ds if d.nguon == "bang"]

        def khop(a: float, b: float) -> bool:
            return not _khac_nhau([a, b], ds_sai)

        # L4 — chênh đúng 10 lần
        da_bao_10 = False
        for i_ in range(len(ds)):
            for j_ in range(i_ + 1, len(ds)):
                a, b = ds[i_].gia_tri, ds[j_].gia_tri
                if a == 0 or b == 0:
                    continue
                ti = max(abs(a), abs(b)) / min(abs(a), abs(b))
                if abs(ti - 10) < 0.02:
                    loi.append(Loi(
                        "NGHI_MAT_PHAY", "nghiem_trong", ds[i_].de_muc, ds[i_].stt,
                        f"{cfg['ten']}: {viet_so(a)} và {viet_so(b)} chênh đúng 10 lần "
                        f"— nhiều khả năng mất dấu phẩy thập phân",
                        f"{ds[i_].trich}  ⟷  {ds[j_].trich}"))
                    da_bao_10 = True
        if da_bao_10:
            continue

        # L2 — mỗi giá trị trong văn phải khớp MỘT giá trị nào đó của bảng
        if van and bang:
            tap_bang = sorted({round(d.gia_tri, 6) for d in bang})
            tong_bang = sum(tap_bang)          # bảng tách theo đoạn — văn nêu tổng
            le = [d for d in van
                  if not any(khop(d.gia_tri, b) for b in tap_bang)
                  and not (len(tap_bang) > 1 and khop(d.gia_tri, tong_bang))]
            if le:
                mo_ta_van = " và ".join(viet_so(d.gia_tri) for d in le[:3])
                mo_ta_bang = " · ".join(viet_so(b) for b in tap_bang[:6])
                loi.append(Loi(
                    "VAN_LECH_BANG", "nghiem_trong", le[0].de_muc, le[0].stt,
                    f"{cfg['ten']}: trong văn ghi {mo_ta_van}, "
                    f"không khớp giá trị nào trong bảng ({mo_ta_bang})",
                    f"{le[0].trich}  ⟷  {bang[0].trich}"))
                continue

        # L1 — nhiều giá trị khác nhau trong văn
        gia_tri_van = sorted({round(d.gia_tri, 6) for d in van})
        if len(gia_tri_van) > 1 and _khac_nhau(gia_tri_van, ds_sai):
            mo_ta = " · ".join(
                f"{viet_so(d.gia_tri)} ({d.de_muc[:24] or 'không rõ mục'})"
                for d in sorted({round(d.gia_tri, 6): d for d in van}.values(),
                                key=lambda x: x.stt)[:5])
            loi.append(Loi(
                "SO_LECH", "nghiem_trong", van[0].de_muc, van[0].stt,
                f"{cfg['ten']} có {len(gia_tri_van)} giá trị khác nhau: {mo_ta}",
                van[0].trich))
    return loi


def luat_3_bang_sai_ten(khoi: list[Khoi], rules: dict) -> list[Loi]:
    loi, bang_dl = [], rules["bang_dai_luong"]
    for i, k in enumerate(khoi):
        if k.loai != "tbl":
            continue
        caption = ""
        for j in (i - 1, i + 1):
            if 0 <= j < len(khoi) and khoi[j].loai == "p":
                t = khoi[j].text.strip()
                if re.match(r"^(Bảng|Biểu)\s", t, re.I):
                    caption = t
                    break
        if not caption:
            continue
        low_cap = _chuan(caption)
        ruot = _chuan(" ".join(" ".join(h) for h in k.hang))
        for ten, cfg in bang_dl.items():
            if ten not in low_cap:
                continue
            co = any(dv in ruot for dv in cfg["phai_co"])
            cam = [x for x in cfg["khong_duoc_chi_co"] if x in ruot]
            if not co and cam:
                loi.append(Loi(
                    "BANG_SAI_TEN", "nghiem_trong", k.de_muc, k.stt,
                    f"Bảng mang tên '{ten}' nhưng ruột bảng chứa đại lượng khác "
                    f"({', '.join(cam)}) và không có {cfg['phai_co'][0]}",
                    caption[:90]))
            break
    return loi


def luat_5_rang_buoc(diem: list[Diem], rules: dict) -> list[Loi]:
    loi = []
    gia_tri: dict[str, float] = {}
    nguon: dict[str, Diem] = {}
    for d in diem:
        if d.chi_tieu not in gia_tri:
            gia_tri[d.chi_tieu] = d.gia_tri
            nguon[d.chi_tieu] = d
    for rb in rules["rang_buoc"]:
        bt = rb["bieu_thuc"]
        ten = re.findall(r"[a-z_][a-z0-9_]*", bt)
        if not all(t in gia_tri for t in ten):
            continue
        try:
            ok = eval(bt, {"__builtins__": {}}, dict(gia_tri))   # noqa: S307 — biểu thức trong file cấu hình
        except Exception:
            continue
        if not ok:
            d0 = nguon[ten[0]]
            chi_tiet = ", ".join(f"{t} = {viet_so(gia_tri[t])}" for t in ten)
            loi.append(Loi("RANG_BUOC", rb.get("muc", "nghiem_trong"), d0.de_muc, d0.stt,
                           f"{rb['thong_diep']} — hiện: {chi_tiet}", d0.trich))
    return loi


def luat_6_cho_trong(khoi: list[Khoi], rules: dict) -> list[Loi]:
    loi = []
    for k in khoi:
        noi_dung = k.text if k.loai == "p" else " ".join(" ".join(h) for h in k.hang)
        for r in rules["cho_trong"]:
            m = re.search(r["regex"], noi_dung)
            if m:
                loi.append(Loi(r["ma"], r["muc"], k.de_muc, k.stt, r["thong_diep"],
                               noi_dung[max(0, m.start() - 30): m.end() + 30].strip()))
        pua = [c for c in noi_dung if 0xE000 <= ord(c) <= 0xF8FF]
        if pua:
            loi.append(Loi("KY_TU_PUA", "nghiem_trong", k.de_muc, k.stt,
                           f"Có {len(pua)} ký tự vùng dùng riêng (U+{ord(pua[0]):04X}) — "
                           f"mất khi trích PDF hoặc mở bằng LibreOffice; thường là ÷ font Symbol",
                           noi_dung[:80]))
    return loi


SO_DE_MUC_RE = re.compile(r"\b\d+(?:\.\d+){1,}\b")


def luat_7_quy_uoc(khoi: list[Khoi]) -> list[Loi]:
    loi, phay, cham = [], 0, 0
    dau_cham: list[Khoi] = []
    for k in khoi:
        if k.loai != "p" or k.la_heading:
            continue
        # bỏ số đề mục (2.1.4.1), lý trình (K0+120) và mã văn bản trước khi đếm
        sach = SO_DE_MUC_RE.sub(" ", _che(k.text))
        phay += len(re.findall(r"\d,\d", sach))
        c = re.findall(r"\d\.\d(?!\d\d)", sach)          # 27.8 — không phải 1.875
        if c:
            cham += len(c)
            dau_cham.append(k)
        if re.search(r"\d\s*oC\b", k.text):
            loi.append(Loi("QUY_UOC", "canh_bao", k.de_muc, k.stt,
                           "Viết 'oC' (chữ o thường) thay cho '°C'", k.text[:80]))
    if phay and cham and cham <= phay:
        k = dau_cham[0]
        loi.append(Loi("QUY_UOC", "canh_bao", k.de_muc, k.stt,
                       f"Dấu thập phân không nhất quán: {phay} chỗ dùng phẩy, "
                       f"{cham} chỗ dùng chấm", k.text[:80]))
    return loi


KHOANG_THANG_RE = re.compile(
    r"(\d+)\s*tháng\s*,?\s*từ\s*tháng\s*(\d+)\s*(?:đến|-|–|tới)\s*tháng\s*(\d+)", re.I)
UOC_LUONG_RE = re.compile(
    r"\b(gần|khoảng|xấp xỉ|chừng)\s+(\d{1,3}(?:\.\d{3})+|\d{4,})\b", re.I)


def luat_9_logic_van(khoi: list[Khoi]) -> list[Loi]:
    """Đếm tháng sai · từ ước lượng đi với con số quá chính xác."""
    loi = []
    for k in khoi:
        if k.loai != "p":
            continue
        for m in KHOANG_THANG_RE.finditer(k.text):
            n, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            that = (b - a + 1) if b >= a else (12 - a + 1 + b)
            if that != n:
                loi.append(Loi("DEM_THANG_SAI", "nghiem_trong", k.de_muc, k.stt,
                               f"Ghi {n} tháng nhưng từ tháng {a} đến tháng {b} là {that} tháng",
                               m.group(0)))
        for m in UOC_LUONG_RE.finditer(k.text):
            so = doc_so(m.group(2))
            if so is None or so % 100 == 0:      # số tròn trăm thì "khoảng" là hợp lý
                continue
            loi.append(Loi("UOC_LUONG_MAU_THUAN", "canh_bao", k.de_muc, k.stt,
                           f"'{m.group(1)}' đi với con số lẻ đến hàng đơn vị "
                           f"({m.group(2)}) — mâu thuẫn về mức chắc chắn; "
                           f"hoặc làm tròn, hoặc bỏ '{m.group(1)}' và dẫn nguồn",
                           m.group(0)))
    return loi


def luat_8_chua_duyet(khoi: list[Khoi], facts: dict) -> list[Loi]:
    """Bản thảo dùng {{fact:x}} mà x đang unverified/conflict trong _facts.yaml."""
    loi = []
    if not facts:
        return loi
    for k in khoi:
        noi_dung = k.text if k.loai == "p" else " ".join(" ".join(h) for h in k.hang)
        for m in re.finditer(r"\{\{\s*fact\s*:\s*([a-z0-9_]+)\s*\}\}", noi_dung):
            key = m.group(1)
            f = facts.get(key)
            if f is None:
                loi.append(Loi("FACT_THIEU", "nghiem_trong", k.de_muc, k.stt,
                               f"Khoá '{key}' không có trong _facts.yaml", m.group(0)))
            elif str(f.get("status", "")).lower() in ("muon_du_an_khac", "muon", "reference"):
                # số mượn có luật riêng L10 xử lý — không báo trùng ở đây
                continue
            elif f.get("status") != "verified":
                loi.append(Loi("SO_CHUA_DUYET", "nghiem_trong", k.de_muc, k.stt,
                               f"Khoá '{key}' đang ở trạng thái '{f.get('status')}' — "
                               f"chưa được duyệt, không dùng cho số high-stakes", m.group(0)))
    return loi


def luat_10_so_muon(khoi: list[Khoi], facts: dict) -> list[Loi]:
    """Số mượn từ dự án khác phải ghi rõ nguồn và kèm khuyến cáo khảo sát bổ sung.

    Trường `data_type` trong _facts.yaml nhận bốn giá trị:
        PROJECT    số đo của chính dự án này              — dùng tự do
        REFERENCE  số mượn từ dự án lân cận / hồ sơ khác  — phải dẫn nguồn + khuyến cáo
        LEGAL      trị số lấy từ văn bản pháp lý, TCVN    — phải dẫn số hiệu văn bản
        MISSING    chưa có, đang chờ khảo sát             — CẤM dùng trong bản thảo

    Khoá không khai `data_type` được coi là PROJECT (tương thích ngược với
    _facts.yaml dựng trước 25/08/2026).
    """
    loi = []
    if not facts:
        return loi

    DAU_HIEU_KHUYEN_CAO = re.compile(
        r"khảo sát bổ sung|khảo sát chi tiết ở bước|cần khảo sát|"
        r"phải được kiểm chứng|xác minh ở bước", re.IGNORECASE)

    # gom theo đề mục để xét ngữ cảnh rộng hơn một đoạn
    theo_de_muc: dict[str, list[Khoi]] = {}
    for k in khoi:
        theo_de_muc.setdefault(k.de_muc or "", []).append(k)

    def text_cua(k: Khoi) -> str:
        return k.text if k.loai == "p" else " ".join(" ".join(h) for h in k.hang)

    for de_muc, ds in theo_de_muc.items():
        van_ban_muc = " ".join(text_cua(k) for k in ds)
        for k in ds:
            for m in re.finditer(r"\{\{\s*fact\s*:\s*([a-z0-9_]+)\s*\}\}", text_cua(k)):
                key = m.group(1)
                f = facts.get(key)
                if not isinstance(f, dict):
                    continue
                dt = str(f.get("data_type", "")).upper()
                # tương thích ngược: _facts.yaml của Cầu Sông Đốc dùng
                # status: muon_du_an_khac để đánh dấu số mượn, trước khi có
                # trường data_type. Coi đó là REFERENCE.
                if not dt:
                    st = str(f.get("status", "")).lower()
                    dt = "REFERENCE" if st in ("muon_du_an_khac", "muon", "reference") else "PROJECT"

                if dt == "MISSING":
                    loi.append(Loi(
                        "FACT_MISSING", "nghiem_trong", k.de_muc, k.stt,
                        f"Khoá '{key}' khai data_type: MISSING — chưa có số liệu, "
                        f"không được dùng trong bản thảo. Để {{{{TODO: ...}}}} thay vào.",
                        m.group(0)))
                    continue

                if dt == "REFERENCE":
                    nguon = str(f.get("nguon_du_an") or "").strip()
                    if not nguon:
                        loi.append(Loi(
                            "MUON_THIEU_KHAI_NGUON", "nghiem_trong", k.de_muc, k.stt,
                            f"Khoá '{key}' khai data_type: REFERENCE nhưng thiếu trường "
                            f"'nguon_du_an' trong _facts.yaml — không biết mượn của dự án nào",
                            m.group(0)))
                    elif nguon.lower() not in van_ban_muc.lower():
                        loi.append(Loi(
                            "MUON_THIEU_DAN_NGUON", "nghiem_trong", k.de_muc, k.stt,
                            f"Khoá '{key}' là số mượn của '{nguon}' nhưng đề mục này "
                            f"không nhắc tên nguồn — đang trình bày như số của chính dự án",
                            m.group(0)))
                    if not DAU_HIEU_KHUYEN_CAO.search(van_ban_muc):
                        loi.append(Loi(
                            "MUON_THIEU_KHUYEN_CAO", "canh_bao", k.de_muc, k.stt,
                            f"Đề mục dùng số mượn ('{key}') nhưng không có câu khuyến cáo "
                            f"khảo sát bổ sung ở bước thiết kế sau",
                            m.group(0)))

                if dt == "LEGAL" and not str(f.get("source") or "").strip():
                    loi.append(Loi(
                        "LEGAL_THIEU_NGUON", "canh_bao", k.de_muc, k.stt,
                        f"Khoá '{key}' khai data_type: LEGAL nhưng không ghi 'source' — "
                        f"trị số pháp lý phải dẫn số hiệu văn bản hoặc TCVN",
                        m.group(0)))
    return loi

# ════════════════════════════════════════════════════════════════════════════
# 6. CHẠY
# ════════════════════════════════════════════════════════════════════════════

def nap_yaml(path: str | None):
    if not path:
        return None
    try:
        import yaml
    except ImportError:
        print("! Cần PyYAML để đọc file cấu hình:  pip install pyyaml", file=sys.stderr)
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def gop_rules(nguoi_dung: dict | None) -> dict:
    r = json.loads(json.dumps(DEFAULT_RULES))
    if not nguoi_dung:
        return r
    for k, v in nguoi_dung.items():
        if isinstance(v, dict) and isinstance(r.get(k), dict):
            r[k].update(v)
        else:
            r[k] = v
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra tất định hồ sơ tư vấn thiết kế")
    ap.add_argument("nguon", help="file .docx / .md hoặc thư mục 10_content/")
    ap.add_argument("--rules", help="qc-rules.yaml ghi đè danh mục chỉ tiêu mặc định")
    ap.add_argument("--facts", help="_facts.yaml để kiểm số chưa duyệt")
    ap.add_argument("--json", dest="ra_json", help="ghi kết quả ra file JSON")
    ap.add_argument("--im", action="store_true", help="chỉ in tổng kết")
    a = ap.parse_args()

    rules = gop_rules(nap_yaml(a.rules))
    facts = nap_yaml(a.facts) or {}

    khoi, loai = doc_nguon(a.nguon)
    if not khoi:
        print("Không đọc được nội dung nào.", file=sys.stderr)
        return 2

    diem = trich_chi_tieu(khoi, rules)
    loi: list[Loi] = []
    loi += luat_1_2_4(diem, rules)
    loi += luat_3_bang_sai_ten(khoi, rules)
    loi += luat_5_rang_buoc(diem, rules)
    loi += luat_6_cho_trong(khoi, rules)
    loi += luat_7_quy_uoc(khoi)
    loi += luat_9_logic_van(khoi)
    loi += luat_8_chua_duyet(khoi, facts)
    loi += luat_10_so_muon(khoi, facts)

    # bỏ trùng, sắp theo mức rồi theo vị trí
    thay, loc = set(), []
    for l in loi:
        khoa = (l.ma, l.stt, l.thong_diep[:45])
        if khoa not in thay:
            thay.add(khoa)
            loc.append(l)
    loc.sort(key=lambda x: (-MUC_NANG.get(x.muc, 0), x.stt))

    nt = sum(1 for l in loc if l.muc == "nghiem_trong")
    cb = len(loc) - nt

    print(f"\n{a.nguon}  ({loai}, {len(khoi)} khối, "
          f"{sum(1 for k in khoi if k.loai == 'tbl')} bảng, "
          f"{len(diem)} giá trị chỉ tiêu đọc được)")
    print(f"{len(loc)} vấn đề — {nt} nghiêm trọng, {cb} cảnh báo\n")
    if not a.im:
        for l in loc:
            print(l.dong())
            if l.trich:
                print(f"     → {l.trich[:150]}")
        print()

    if a.ra_json:
        with open(a.ra_json, "w", encoding="utf-8") as f:
            json.dump({"nguon": a.nguon,
                       "tong": len(loc), "nghiem_trong": nt, "canh_bao": cb,
                       "loi": [asdict(l) for l in loc],
                       "chi_tieu_doc_duoc": [asdict(d) for d in diem]},
                      f, ensure_ascii=False, indent=2)
        print(f"→ {a.ra_json}")

    return 1 if nt else 0


if __name__ == "__main__":
    sys.exit(main())
