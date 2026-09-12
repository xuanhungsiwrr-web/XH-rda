#!/usr/bin/env python3
"""
learn-from-edits.py — HOC VAN PHONG TU CHINH BAN SUA CUA NGUOI DUNG.

Day la nguon tin hieu manh nhat va RE NHAT. Moi lan anh sua ban thao cua AI
la mot lan anh "day" no — nhung neu khong ghi lai thi tin hieu do mat.

Script so sanh cap file (ban AI viet, ban anh da sua) o muc CAU va muc TU,
roi tong hop thanh QUY TAC:
  - cum tu bi xoa nhieu lan   -> "khong bao gio dung"
  - cum tu duoc them nhieu lan-> "uu tien dung"
  - cap thay the co he thong  -> "A -> B"
  - bullet bi doi thanh van xuoi (hoac nguoc lai)
  - cau bi cat ngan / noi dai
  - so lieu bi sua            -> KHONG phai loi van phong, tach rieng

Dung:
  # mot cap
  python learn-from-edits.py --pair C2-1_claude.md C2-1_dasua.md

  # ca thu muc: tu ghep cap theo hau to _claude / _dasua
  python learn-from-edits.py --dir lich-su-sua/ --out quy-tac.json --md quy-tac.md
"""
from __future__ import annotations
import argparse, collections, difflib, glob, json, os, re, sys

# ---------------------------------------------------------------- doc file
def load_blocks(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            import docx
        except ImportError:
            sys.exit("Can: pip install python-docx")
        return [p.text.strip() for p in docx.Document(path).paragraphs if p.text.strip()]
    return [b.strip() for b in
            re.split(r"\n\s*\n", open(path, encoding="utf-8").read()) if b.strip()]


ABBR = ["TS", "ThS", "KS", "GS", "PGS", "TT", "NĐ", "QĐ", "VD", "v.v", "TCVN", "QCVN"]
_ABBR_RE = re.compile(r"\b(" + "|".join(map(re.escape, ABBR)) + r")\.")
BULLET_RE = re.compile(r"^\s*([-*+•]|\d+[.)])\s+")
NUM_RE = re.compile(r"[+-]?\d[\d.,]*")


def split_sentences(text):
    t = _ABBR_RE.sub(lambda m: m.group(1) + "<D>", text)
    t = re.sub(r"(\d)([.,])(\d)", r"\1<\2>\3", t)
    parts = re.split(r"(?<=[.!?;])\s+", t)
    out = []
    for s in parts:
        s = s.replace("<D>", ".").replace("<.>", ".").replace("<,>", ",").strip()
        if len(s) > 8:
            out.append(s)
    return out


def _sub(g, counter, minv):
    """True neu g la con cua mot ngram dai hon cung tan suat -> bo di cho gon."""
    for other, c in counter.items():
        if other != g and g in other and c >= minv and len(other) > len(g):
            return True
    return False


def norm(s):
    return re.sub(r"\s+", " ", s.lower().strip(" .,;:"))


def toks(s):
    return re.findall(r"[0-9A-Za-zÀ-ỹ]+|[^\sA-Za-zÀ-ỹ0-9]", s)


# ---------------------------------------------------------------- so sanh
def ngrams(text, lo=2, hi=4):
    """N-gram chuc nang (khong chua so) de so sanh o muc TOAN VAN BAN."""
    c = collections.Counter()
    for sent in split_sentences(text):
        w = [x.lower() for x in re.findall(r"[A-Za-zÀ-ỹ]+", sent) if len(x) > 1]
        for n in range(lo, hi + 1):
            for i in range(len(w) - n + 1):
                c[" ".join(w[i:i + n])] += 1
    return c


def compare_pair(fa, fb, acc):
    A, B = load_blocks(fa), load_blocks(fb)
    acc["so_cap"] += 1

    # --- lop 0: so sanh CUM TU o muc toan van ban.
    #     Ben bi (chiu duoc viet lai han) van rut duoc thoi quen tu day.
    ga, gb = ngrams("\n".join(A)), ngrams("\n".join(B))
    for g in set(ga) | set(gb):
        d = gb[g] - ga[g]
        if d < 0:
            acc["cum_bien_mat"][g] += -d
        elif d > 0:
            acc["cum_xuat_hien"][g] += d

    # --- cau truc: bullet <-> van xuoi
    ba = sum(1 for x in A if BULLET_RE.match(x))
    bb = sum(1 for x in B if BULLET_RE.match(x))
    if bb < ba:
        acc["cau_truc"]["bullet_thanh_van_xuoi"] += (ba - bb)
    elif bb > ba:
        acc["cau_truc"]["van_xuoi_thanh_bullet"] += (bb - ba)
    if len(B) > len(A):
        acc["cau_truc"]["doan_bi_tach_nho"] += (len(B) - len(A))
    elif len(B) < len(A):
        acc["cau_truc"]["doan_bi_gop_lai"] += (len(A) - len(B))

    # --- muc cau
    SA = [s for blk in A for s in split_sentences(blk)]
    SB = [s for blk in B for s in split_sentences(blk)]
    acc["so_cau_truoc"] += len(SA)
    acc["so_cau_sau"] += len(SB)
    nA = [norm(s) for s in SA]
    nB = [norm(s) for s in SB]

    sm = difflib.SequenceMatcher(a=nA, b=nB, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            acc["cau_giu_nguyen"] += (i2 - i1)
            continue
        if tag == "delete":
            for s in SA[i1:i2]:
                acc["cau_bi_xoa"].append(s[:200])
            continue
        if tag == "insert":
            for s in SB[j1:j2]:
                acc["cau_them_moi"].append(s[:200])
            continue
        # replace: ghep 1-1 theo do tuong dong
        for k in range(max(i2 - i1, j2 - j1)):
            a = SA[i1 + k] if i1 + k < i2 else None
            b = SB[j1 + k] if j1 + k < j2 else None
            if a is None:
                acc["cau_them_moi"].append(b[:200]); continue
            if b is None:
                acc["cau_bi_xoa"].append(a[:200]); continue
            ratio = difflib.SequenceMatcher(a=norm(a), b=norm(b)).ratio()
            if ratio < 0.45:
                acc["cau_viet_lai_han"].append({"truoc": a[:200], "sau": b[:200]})
                continue
            acc["cau_sua_nhe"] += 1
            diff_words(a, b, acc)
            la, lb = len(toks(a)), len(toks(b))
            if lb < la * 0.75:
                acc["cau_truc"]["cau_bi_cat_ngan"] += 1
            elif lb > la * 1.3:
                acc["cau_truc"]["cau_duoc_viet_dai_them"] += 1


def diff_words(a, b, acc):
    wa, wb = toks(a), toks(b)
    sm = difflib.SequenceMatcher(a=[w.lower() for w in wa],
                                 b=[w.lower() for w in wb], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        old = " ".join(wa[i1:i2]).strip()
        new = " ".join(wb[j1:j2]).strip()
        # so lieu bi sua -> khong phai van phong
        if (NUM_RE.fullmatch(old.replace(" ", "")) or
                NUM_RE.fullmatch(new.replace(" ", ""))):
            if old and new:
                acc["so_lieu_bi_sua"].append(f"{old} → {new}")
            continue
        if tag == "delete" and old:
            acc["cum_bi_xoa"][old.lower()] += 1
        elif tag == "insert" and new:
            acc["cum_duoc_them"][new.lower()] += 1
        elif tag == "replace" and old and new:
            if len(old) <= 60 and len(new) <= 60:
                acc["cap_thay_the"][f"{old.lower()} → {new.lower()}"] += 1
            acc["cum_bi_xoa"][old.lower()] += 1
            acc["cum_duoc_them"][new.lower()] += 1


# ---------------------------------------------------------------- chay
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", nargs=2, metavar=("BAN_AI", "BAN_DA_SUA"))
    ap.add_argument("--dir", help="thu muc chua cac cap *_claude.* va *_dasua.*")
    ap.add_argument("--out", default="quy-tac-tu-ban-sua.json")
    ap.add_argument("--md", default="")
    ap.add_argument("--min", type=int, default=2,
                    help="mot thay doi phai lap >= N lan moi thanh QUY TAC")
    args = ap.parse_args()

    acc = {
        "so_cap": 0, "so_cau_truoc": 0, "so_cau_sau": 0,
        "cau_giu_nguyen": 0, "cau_sua_nhe": 0,
        "cau_bi_xoa": [], "cau_them_moi": [], "cau_viet_lai_han": [],
        "cum_bi_xoa": collections.Counter(),
        "cum_duoc_them": collections.Counter(),
        "cap_thay_the": collections.Counter(),
        "so_lieu_bi_sua": [],
        "cau_truc": collections.Counter(),
        "cum_bien_mat": collections.Counter(),
        "cum_xuat_hien": collections.Counter(),
    }

    pairs = []
    if args.pair:
        pairs = [tuple(args.pair)]
    elif args.dir:
        for f in sorted(glob.glob(os.path.join(args.dir, "*_claude.*"))):
            stem = f.rsplit("_claude.", 1)[0]
            ext = f.rsplit(".", 1)[1]
            for cand in (f"{stem}_dasua.{ext}", f"{stem}_dasua.docx", f"{stem}_dasua.md"):
                if os.path.exists(cand):
                    pairs.append((f, cand)); break
    if not pairs:
        sys.exit("Khong co cap file nao. Dat ten: <ma-muc>_claude.md va <ma-muc>_dasua.md")

    for a, b in pairs:
        print(f"So sanh: {os.path.basename(a)}  ↔  {os.path.basename(b)}")
        compare_pair(a, b, acc)

    tong = acc["cau_giu_nguyen"] + acc["cau_sua_nhe"] + len(acc["cau_bi_xoa"]) \
        + len(acc["cau_viet_lai_han"])
    ty_le_giu = round(100 * acc["cau_giu_nguyen"] / tong, 1) if tong else 0

    result = {
        "so_cap_file": acc["so_cap"],
        "TY_LE_CAU_GIU_NGUYEN_PCT": ty_le_giu,
        "thong_ke": {
            "cau_truoc_sua": acc["so_cau_truoc"], "cau_sau_sua": acc["so_cau_sau"],
            "giu_nguyen": acc["cau_giu_nguyen"], "sua_nhe": acc["cau_sua_nhe"],
            "viet_lai_han": len(acc["cau_viet_lai_han"]),
            "bi_xoa": len(acc["cau_bi_xoa"]), "them_moi": len(acc["cau_them_moi"]),
        },
        "thay_doi_cau_truc": dict(acc["cau_truc"]),
        "QUY_TAC_khong_dung": [{"cum": k, "so_lan": v}
                               for k, v in acc["cum_bi_xoa"].most_common(40)
                               if v >= args.min],
        "QUY_TAC_uu_tien_dung": [{"cum": k, "so_lan": v}
                                 for k, v in acc["cum_duoc_them"].most_common(40)
                                 if v >= args.min],
        "QUY_TAC_thay_the": [{"quy_tac": k, "so_lan": v}
                             for k, v in acc["cap_thay_the"].most_common(30)
                             if v >= args.min],
        "THOI_QUEN_bi_loai_bo": [{"cum": k, "so_lan": v}
                                 for k, v in acc["cum_bien_mat"].most_common(200)
                                 if v >= args.min and not _sub(k, acc["cum_bien_mat"], args.min)][:25],
        "THOI_QUEN_duoc_them_vao": [{"cum": k, "so_lan": v}
                                    for k, v in acc["cum_xuat_hien"].most_common(200)
                                    if v >= args.min and not _sub(k, acc["cum_xuat_hien"], args.min)][:25],
        "so_lieu_bi_sua_KHONG_phai_van_phong": acc["so_lieu_bi_sua"][:40],
        "cau_bi_xoa_han": acc["cau_bi_xoa"][:20],
        "cau_viet_lai_han": acc["cau_viet_lai_han"][:20],
    }
    json.dump(result, open(args.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"\n{'='*62}")
    print(f"TỈ LỆ CÂU GIỮ NGUYÊN: {ty_le_giu}%   ← chỉ số theo dõi qua từng báo cáo")
    print(f"{'='*62}")
    st = result["thong_ke"]
    print(f"  giữ nguyên {st['giu_nguyen']} · sửa nhẹ {st['sua_nhe']} · "
          f"viết lại hẳn {st['viet_lai_han']} · xoá {st['bi_xoa']} · thêm {st['them_moi']}")
    if result["thay_doi_cau_truc"]:
        print("\nThay đổi cấu trúc:")
        for k, v in result["thay_doi_cau_truc"].items():
            print(f"  - {k.replace('_',' ')}: {v}")
    for title, key in (("QUY TẮC — KHÔNG dùng", "QUY_TAC_khong_dung"),
                       ("QUY TẮC — ƯU TIÊN dùng", "QUY_TAC_uu_tien_dung"),
                       ("QUY TẮC — THAY THẾ", "QUY_TAC_thay_the"),
                       ("THÓI QUEN bị loại bỏ (toàn văn bản)", "THOI_QUEN_bi_loai_bo"),
                       ("THÓI QUEN được thêm vào (toàn văn bản)", "THOI_QUEN_duoc_them_vao")):
        items = result[key]
        if items:
            print(f"\n{title}:")
            for it in items[:12]:
                lbl = it.get("cum") or it.get("quy_tac")
                print(f"  {it['so_lan']}x  “{lbl}”")
    if result["so_lieu_bi_sua_KHONG_phai_van_phong"]:
        print("\n⚠️ Số liệu bị sửa (KHÔNG phải lỗi văn phong — kiểm lại _facts.yaml):")
        for s in result["so_lieu_bi_sua_KHONG_phai_van_phong"][:10]:
            print(f"  {s}")
    print(f"\n→ {args.out}")

    if args.md:
        L = ["# Quy tắc văn phong rút ra từ bản sửa\n",
             f"Nguồn: {acc['so_cap']} cặp bản thảo. "
             f"**Tỉ lệ câu giữ nguyên: {ty_le_giu}%**\n"]
        if result["QUY_TAC_khong_dung"]:
            L.append("## Không dùng\n")
            L += [f"- “{i['cum']}” (bị xoá {i['so_lan']} lần)"
                  for i in result["QUY_TAC_khong_dung"]]
        if result["QUY_TAC_uu_tien_dung"]:
            L.append("\n## Ưu tiên dùng\n")
            L += [f"- “{i['cum']}” (được thêm {i['so_lan']} lần)"
                  for i in result["QUY_TAC_uu_tien_dung"]]
        if result["THOI_QUEN_bi_loai_bo"]:
            L.append("\n## Thói quen bị loại bỏ\n")
            L += [f"- “{i['cum']}” ({i['so_lan']} lần)" for i in result["THOI_QUEN_bi_loai_bo"]]
        if result["THOI_QUEN_duoc_them_vao"]:
            L.append("\n## Thói quen được thêm vào\n")
            L += [f"- “{i['cum']}” ({i['so_lan']} lần)" for i in result["THOI_QUEN_duoc_them_vao"]]
        if result["QUY_TAC_thay_the"]:
            L.append("\n## Thay thế có hệ thống\n")
            L += [f"- {i['quy_tac']} ({i['so_lan']} lần)"
                  for i in result["QUY_TAC_thay_the"]]
        if result["thay_doi_cau_truc"]:
            L.append("\n## Cấu trúc\n")
            L += [f"- {k.replace('_',' ')}: {v} lần"
                  for k, v in result["thay_doi_cau_truc"].items()]
        open(args.md, "w", encoding="utf-8").write("\n".join(L))
        print(f"→ {args.md}")


if __name__ == "__main__":
    main()
