#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_report.py — LỚP 3: đổ nội dung Markdown vào khuôn Word, render MỘT LẦN.

    python render_report.py \
        --khuon   20-Khuon/KhuonMau_NamQuoc.dotx \
        --noidung 10_content/ \
        --info    _info.yaml \
        --facts   _facts.yaml \
        --hinh    00_input/Anh-HienTruong/ \
        --ra      20_output/BaoCao.docx

NGUYÊN TẮC
  • Word là KHUÔN ĐÚC, không phải sản phẩm của AI. Định dạng nằm trong .dotx,
    script chỉ gọi tên style — không tự đặt font, cỡ chữ, màu, lề.
  • KHÔNG ghép file .docx. Chỉ render một lần từ nhiều file .md.
  • Bìa, mục lục, header, footer, số trang, số thứ tự hình/bảng: khuôn lo,
    Word tự cập nhật. File .md tuyệt đối không chứa những thứ đó.
  • Con số chỉ tồn tại ở _facts.yaml. Bản thảo viết {{fact:ten_chi_tieu}}.

CÚ PHÁP TRONG FILE .md
    # ## ### #### ##### ######   → Heading1..6 (numbering của khuôn tự chạy)
    đoạn văn thường              → style thân bài của khuôn
    - mục · * mục                → List Bullet
    1. mục                       → List Number
    | a | b |  (bảng markdown)   → bảng style TableGrid + TableHead/TableContent
    Bảng: <chú thích>            → caption bảng, đặt TRÊN bảng (dòng ngay trước bảng)
    ![chú thích](ten-file.jpg)   → hình + caption đặt DƯỚI hình
    {{fact:ten_chi_tieu}}        → giá trị từ _facts.yaml (chỉ verified)
    {{TODO: việc cần làm}}       → tô vàng để nhìn thấy ngay khi mở file
    {{KEY}} trong bìa/footer     → tra _info.yaml theo đúng tên khoá

THỨ TỰ FILE: theo tên. Đặt tên C1_..., C2_..., C10_... thì dùng --thu-tu
để chỉ định, hoặc đánh số hai chữ số: C01_, C02_.

BẢN NÀY ĐÃ VÁ LỖI L1 (22/08/2026): bat_update_fields() chèn <w:updateFields>
đúng vị trí trong sequence CT_Settings, không chèn làm con đầu tiên của
<w:settings> nữa. Chèn sai chỗ làm file .docx hỏng XSD, và lỗi chỉ lộ ra khi
dùng khuôn CHƯA có sẵn thẻ updateFields — tức chính KhuonMau_NamQuoc.dotx.
Sau mọi thay đổi cấu trúc XML: chạy validate trước khi kết luận là xong.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
import zipfile

try:
    import docx
    from docx.shared import Cm, Pt
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    sys.exit("Cần: pip install python-docx")

STYLE = {
    "than_bai":      "Normal",
    "heading":       ["Heading 1", "Heading 2", "Heading 3",
                      "Heading 4", "Heading 5", "Heading 6"],
    "bullet":        "List Bullet",
    "so_thu_tu":     "List Number",
    "bang":          "Table Grid",
    "o_tieu_de":     "Table Head",
    "o_noi_dung":    "Table Content",
    "caption_bang":  "Caption",
    "doan_chua_anh": "Picture",
    "caption_hinh":  "Pics Caption",
}

VANG = "yellow"
RSTYLE_MAC_DINH = "DefaultParagraphFont"


def mo_khuon(path: str):
    """python-docx không mở .dotx — đổi content-type trong bộ nhớ rồi mở."""
    if path.lower().endswith(".docx"):
        return docx.Document(path)
    buf = io.BytesIO()
    with zipfile.ZipFile(path) as zin, \
         zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == "[Content_Types].xml":
                data = data.replace(b"wordprocessingml.template.main+xml",
                                    b"wordprocessingml.document.main+xml")
            zout.writestr(it, data)
    buf.seek(0)
    return docx.Document(buf)


def bat_update_fields(path: str) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(path) as zin:
        names = zin.namelist()
        s = zin.read("word/settings.xml").decode("utf-8")
        if "<w:updateFields" in s:
            # đã có sẵn — ép về "true" (khuôn gốc hay để "false", Word sẽ không cập nhật mục lục)
            s = re.sub(r'<w:updateFields\b[^>]*/>', '<w:updateFields w:val="true"/>', s)
        else:
            # CT_Settings là một SEQUENCE có thứ tự — chèn sai chỗ là hỏng XSD.
            # updateFields đứng ngay trước hdrShapeDefaults / footnotePr / endnotePr / compat.
            chen = '<w:updateFields w:val="true"/>'
            for sau in ("<w:hdrShapeDefaults", "<w:footnotePr", "<w:endnotePr",
                        "<w:compat", "<w:rsids", "</w:settings>"):
                k = s.find(sau)
                if k != -1:
                    s = s[:k] + chen + s[k:]
                    break
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                zout.writestr(zin.getinfo(n),
                              s.encode("utf-8") if n == "word/settings.xml"
                              else zin.read(n))
    buf.seek(0)
    with open(path, "wb") as f:
        f.write(buf.read())


def nap_yaml(path: str | None) -> dict:
    if not path:
        return {}
    if not os.path.exists(path):
        print(f"  ! không thấy {path} — bỏ qua", file=sys.stderr)
        return {}
    try:
        import yaml
    except ImportError:
        sys.exit("Cần: pip install pyyaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def so_viet(x) -> str:
    if isinstance(x, bool) or x is None:
        return str(x)
    if isinstance(x, int):
        return f"{x:,}".replace(",", ".")
    if isinstance(x, float):
        if x == int(x) and abs(x) >= 100:
            return f"{int(x):,}".replace(",", ".")
        return f"{x:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
    return str(x)


class KhoFact:
    def __init__(self, facts: dict):
        self.f = facts or {}
        self.canh_bao: list[str] = []

    def tra(self, key: str) -> tuple[str, bool]:
        rec = self.f.get(key)
        if rec is None:
            self.canh_bao.append(f"khoá '{key}' không có trong _facts.yaml")
            return f"[THIẾU FACT: {key}]", True
        if not isinstance(rec, dict):
            return so_viet(rec), False
        gt, dv = rec.get("value"), rec.get("unit") or ""
        tt = rec.get("status", "unverified")
        if gt is None:
            self.canh_bao.append(f"khoá '{key}' chưa có giá trị (status: {tt})")
            return f"[CHƯA CHỐT: {key}]", True
        txt = so_viet(gt) + (dv if dv in ("m", "mm", "cm", "km", "%", "m/s") else
                             (" " + dv if dv else ""))
        if tt != "verified":
            self.canh_bao.append(f"khoá '{key}' đang '{tt}' — chưa được duyệt")
            return txt, True
        return txt, False


def _run(p, text: str, to_vang: bool = False, dam: bool = False, nghieng: bool = False):
    r = p.add_run(text)
    rPr = r._element.get_or_add_rPr()
    rs = OxmlElement("w:rStyle")
    rs.set(qn("w:val"), RSTYLE_MAC_DINH)
    rPr.insert(0, rs)
    if dam:
        r.bold = True
    if nghieng:
        r.italic = True
    if to_vang:
        hl = OxmlElement("w:highlight")
        hl.set(qn("w:val"), VANG)
        rPr.append(hl)
    return r


def _field(p, instr: str):
    for tag, extra in (("begin", None), ("instrText", instr),
                       ("separate", None), ("text", "1"), ("end", None)):
        if tag == "instrText":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = instr
            r = OxmlElement("w:r")
            rPr = OxmlElement("w:rPr")
            rs = OxmlElement("w:rStyle"); rs.set(qn("w:val"), RSTYLE_MAC_DINH)
            rPr.append(rs); r.append(rPr); r.append(el)
            p._p.append(r)
        elif tag == "text":
            r = OxmlElement("w:r")
            t = OxmlElement("w:t"); t.text = extra
            r.append(t); p._p.append(r)
        else:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), tag)
            r = OxmlElement("w:r"); r.append(fc)
            p._p.append(r)


def _style_an_toan(doc, ten: str, du_phong: str = "Normal"):
    try:
        doc.styles[ten]
        return ten
    except KeyError:
        return du_phong


INLINE_RE = re.compile(r"(\{\{[^}]*\}\}|\*\*[^*]+\*\*|\*[^*]+\*)")


def _do_noi_dung(p, text: str, kho: KhoFact):
    for phan in INLINE_RE.split(text):
        if not phan:
            continue
        if phan.startswith("{{"):
            noi = phan[2:-2].strip()
            if noi.lower().startswith("fact:"):
                txt, vang = kho.tra(noi.split(":", 1)[1].strip())
                _run(p, txt, to_vang=vang)
            elif noi.lower().startswith("todo"):
                _run(p, "【" + noi + "】", to_vang=True)
            else:
                _run(p, phan, to_vang=True)
        elif phan.startswith("**") and phan.endswith("**"):
            _run(p, phan[2:-2], dam=True)
        elif phan.startswith("*") and phan.endswith("*"):
            _run(p, phan[1:-1], nghieng=True)
        else:
            _run(p, phan)


KIEU_CAPTION = "theo-chuong"


def them_caption(doc, text: str, loai: str, kho: KhoFact):
    style = STYLE["caption_bang"] if loai == "Bảng" else STYLE["caption_hinh"]
    p = doc.add_paragraph(style=_style_an_toan(doc, style, "Caption"))
    _run(p, loai + " ")
    if KIEU_CAPTION == "theo-chuong":
        _field(p, r'STYLEREF 1 \s')
        _run(p, "-")
        _field(p, f'SEQ {loai} \\* ARABIC \\s 1')
    else:
        _field(p, f'SEQ {loai} \\* ARABIC')
    if text:
        _run(p, ": " + text if not text.startswith(":") else text)
    return p


BULLET_RE = re.compile(r"^\s*[-*•]\s+(.*)$")
SO_TT_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
HINH_RE = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*$")
CAPTION_BANG_RE = re.compile(r"^(?:Bảng|Biểu)\s*:\s*(.*)$", re.I)
HANG_BANG_RE = re.compile(r"^\s*\|(.+)\|\s*$")
NGAN_CACH_RE = re.compile(r"^[\s|:-]+$")


def doc_khoi_md(path: str):
    khoi, bang, caption_cho = [], [], None
    with open(path, encoding="utf-8") as f:
        dong = [l.rstrip("\n") for l in f]

    i = 0
    while i < len(dong):
        l = dong[i]
        if HANG_BANG_RE.match(l):
            bang.append(l)
            i += 1
            continue
        if bang:
            rows = []
            for b in bang:
                if NGAN_CACH_RE.match(b.strip().strip("|")):
                    continue
                rows.append([c.strip() for c in b.strip().strip("|").split("|")])
            if rows:
                khoi.append(("bang", rows, caption_cho))
            bang, caption_cho = [], None

        if not l.strip():
            i += 1
            continue
        m = HEADING_RE.match(l)
        if m:
            khoi.append(("heading", len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        m = HINH_RE.match(l)
        if m:
            khoi.append(("hinh", m.group(2).strip(), m.group(1).strip()))
            i += 1
            continue
        m = CAPTION_BANG_RE.match(l.strip())
        if m:
            caption_cho = m.group(1).strip()
            i += 1
            continue
        m = BULLET_RE.match(l)
        if m:
            khoi.append(("bullet", m.group(1).strip()))
            i += 1
            continue
        m = SO_TT_RE.match(l)
        if m:
            khoi.append(("so", m.group(1).strip()))
            i += 1
            continue
        buf = [l.strip()]
        i += 1
        while i < len(dong) and dong[i].strip() and not HEADING_RE.match(dong[i]) \
                and not BULLET_RE.match(dong[i]) and not SO_TT_RE.match(dong[i]) \
                and not HANG_BANG_RE.match(dong[i]) and not HINH_RE.match(dong[i]):
            buf.append(dong[i].strip())
            i += 1
        khoi.append(("doan", " ".join(buf)))

    if bang:
        rows = [[c.strip() for c in b.strip().strip("|").split("|")]
                for b in bang if not NGAN_CACH_RE.match(b.strip().strip("|"))]
        if rows:
            khoi.append(("bang", rows, caption_cho))
    return khoi


def don_duoi_khuon(doc) -> int:
    n = 0
    while doc.paragraphs:
        p = doc.paragraphs[-1]
        if p.text.strip() or p._p.findall(qn("w:r")):
            break
        if p._p.find(qn("w:pPr")) is not None and \
           p._p.find(qn("w:pPr")).find(qn("w:sectPr")) is not None:
            break
        p._p.getparent().remove(p._p)
        n += 1
    return n


def do_vao_khuon(doc, khoi, kho: KhoFact, thu_muc_hinh: str | None, nhat_ky: list):
    for k in khoi:
        loai = k[0]

        if loai == "heading":
            cap = min(k[1], 6)
            st = _style_an_toan(doc, STYLE["heading"][cap - 1], "Normal")
            p = doc.add_paragraph(style=st)
            _do_noi_dung(p, k[2], kho)

        elif loai == "doan":
            p = doc.add_paragraph(style=_style_an_toan(doc, STYLE["than_bai"]))
            _do_noi_dung(p, k[1], kho)

        elif loai == "bullet":
            p = doc.add_paragraph(style=_style_an_toan(doc, STYLE["bullet"], "Normal"))
            _do_noi_dung(p, k[1], kho)

        elif loai == "so":
            p = doc.add_paragraph(style=_style_an_toan(doc, STYLE["so_thu_tu"], "Normal"))
            _do_noi_dung(p, k[1], kho)

        elif loai == "bang":
            rows, caption = k[1], k[2]
            if caption is not None:
                them_caption(doc, caption, "Bảng", kho)
            ncot = max(len(r) for r in rows)
            t = doc.add_table(rows=len(rows), cols=ncot)
            try:
                t.style = STYLE["bang"]
            except KeyError:
                nhat_ky.append(f"khuôn không có table style '{STYLE['bang']}'")
            for ri, r in enumerate(rows):
                for ci in range(ncot):
                    o = t.cell(ri, ci)
                    o.text = ""
                    p = o.paragraphs[0]
                    st = STYLE["o_tieu_de"] if ri == 0 else STYLE["o_noi_dung"]
                    p.style = _style_an_toan(doc, st, "Normal")
                    _do_noi_dung(p, r[ci] if ci < len(r) else "", kho)

        elif loai == "hinh":
            duong_dan, caption = k[1], k[2]
            tim = duong_dan
            if thu_muc_hinh and not os.path.isabs(duong_dan):
                ung = os.path.join(thu_muc_hinh, duong_dan)
                if os.path.exists(ung):
                    tim = ung
            p = doc.add_paragraph(style=_style_an_toan(doc, STYLE["doan_chua_anh"], "Normal"))
            if os.path.exists(tim):
                r = p.add_run()
                try:
                    from PIL import Image
                    with Image.open(tim) as img:
                        w, h = img.size
                    if w > h:
                        r.add_picture(tim, width=Cm(16.0))
                    else:
                        r.add_picture(tim, height=Cm(20.0))
                except ImportError:
                    print("  ! Chưa cài Pillow, ảnh sẽ tự giãn rộng 16cm. Gõ: pip install Pillow", file=sys.stderr)
                    r.add_picture(tim, width=Cm(16.0))
                except Exception:
                    r.add_picture(tim, width=Cm(16.0))
            else:
                _run(p, f"【THIẾU HÌNH: {duong_dan}】", to_vang=True)
                nhat_ky.append(f"không thấy file hình: {duong_dan}")
            them_caption(doc, caption, "Hình", kho)


KEY_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def thay_placeholder_paragraph(p, info: dict, con_sot: set) -> None:
    full = "".join(r.text or "" for r in p.runs)
    if "{{" not in full:
        return
    moi = KEY_RE.sub(lambda m: str(info.get(m.group(1), m.group(0))), full)
    for m in KEY_RE.finditer(moi):
        con_sot.add(m.group(1))
    if moi == full:
        return
    for r in p.runs[1:]:
        r._element.getparent().remove(r._element)
    if p.runs:
        p.runs[0].text = moi
        if "{{TODO" in moi or "{{" in moi:
            rPr = p.runs[0]._element.get_or_add_rPr()
            hl = OxmlElement("w:highlight")
            hl.set(qn("w:val"), VANG)
            rPr.append(hl)
    else:
        _run(p, moi, to_vang=("{{" in moi))


def quet_thay_tat_ca(doc, info: dict) -> set:
    con_sot: set = set()

    def quet_bang(tbl):
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    thay_placeholder_paragraph(p, info, con_sot)
                for t in cell.tables:
                    quet_bang(t)

    for p in doc.paragraphs:
        thay_placeholder_paragraph(p, info, con_sot)
    for t in doc.tables:
        quet_bang(t)
    for s in doc.sections:
        for phan in (s.header, s.footer, s.first_page_header, s.first_page_footer,
                     s.even_page_header, s.even_page_footer):
            if phan is None:
                continue
            for p in phan.paragraphs:
                thay_placeholder_paragraph(p, info, con_sot)
            for t in phan.tables:
                quet_bang(t)
    return con_sot


def main() -> int:
    ap = argparse.ArgumentParser(description="Đổ Markdown vào khuôn Word, render một lần")
    ap.add_argument("--khuon", required=True)
    ap.add_argument("--noidung", required=True)
    ap.add_argument("--info")
    ap.add_argument("--facts")
    ap.add_argument("--hinh")
    ap.add_argument("--ra", required=True)
    ap.add_argument("--thu-tu")
    ap.add_argument("--caption", choices=["theo-chuong", "lien-tuc"],
                    default="theo-chuong")
    a = ap.parse_args()

    global KIEU_CAPTION
    KIEU_CAPTION = a.caption

    info = nap_yaml(a.info)
    kho = KhoFact(nap_yaml(a.facts))
    nhat_ky: list[str] = []

    if os.path.isdir(a.noidung):
        if a.thu_tu:
            ds = [os.path.join(a.noidung, x.strip()) for x in a.thu_tu.split(",")]
        else:
            ds = sorted(os.path.join(a.noidung, f)
                        for f in os.listdir(a.noidung) if f.endswith(".md"))
    else:
        ds = [a.noidung]
    ds = [f for f in ds if os.path.exists(f)]
    if not ds:
        print("Không có file .md nào để render.", file=sys.stderr)
        return 2

    doc = mo_khuon(a.khuon)
    da_don = don_duoi_khuon(doc)

    tong_khoi = 0
    for f in ds:
        khoi = doc_khoi_md(f)
        tong_khoi += len(khoi)
        do_vao_khuon(doc, khoi, kho, a.hinh, nhat_ky)

    con_sot = quet_thay_tat_ca(doc, info)

    os.makedirs(os.path.dirname(os.path.abspath(a.ra)), exist_ok=True)
    doc.save(a.ra)
    bat_update_fields(a.ra)

    print(f"\n✓ {a.ra}")
    print(f"  {len(ds)} file .md · {tong_khoi} khối nội dung"
          + (f" · dọn {da_don} đoạn trống cuối khuôn" if da_don else ""))
    for f in ds:
        print(f"    · {os.path.basename(f)}")
    if con_sot:
        print(f"\n  ⚠ {len(con_sot)} placeholder chưa có giá trị trong _info.yaml:")
        for k in sorted(con_sot):
            print(f"      {{{{{k}}}}}")
    if kho.canh_bao:
        print(f"\n  ⚠ {len(kho.canh_bao)} vấn đề về số liệu (đã tô vàng trong file):")
        for c in sorted(set(kho.canh_bao)):
            print(f"      {c}")
    if nhat_ky:
        print(f"\n  ⚠ {len(nhat_ky)} ghi chú:")
        for c in sorted(set(nhat_ky)):
            print(f"      {c}")
    print("\n  Mở bằng Word → chọn 'Có' khi Word hỏi cập nhật trường,"
          "\n  hoặc Ctrl+A rồi F9, để build mục lục và số trang.")
    return 1 if (con_sot or kho.canh_bao) else 0


if __name__ == "__main__":
    sys.exit(main())
