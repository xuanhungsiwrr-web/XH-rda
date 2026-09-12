#!/usr/bin/env python3
"""
mine-style.py — DO VAN PHONG tu kho bao cao cu (docx / pdf / md / txt).

Muc dich: bien "vai chuc du an, hang tram file" thanh MOT ho so van phong
gon (~2-3 trang) co the nhet vao ngu canh moi lan viet.

KHONG dung AI. Toan bo la thong ke tat dinh -> mien phi, chay lai bao nhieu
lan cung ra ket qua giong nhau, va con so thi khong the bia.

Do 9 nhom chi so:
  1. Do dai cau (trung binh, trung vi, phan bo)
  2. Do dai doan (so cau / doan)
  3. Ty le bullet
  4. Ty le cau bi dong ("duoc", "bi")
  5. Cum tu chuyen doan / mo cau  -> NGAN HANG CUM TU
  6. Quy uoc so & don vi (dau thap phan, dau nghin, khoang cach truoc don vi)
  7. Cach xung ho don vi lap bao cao
  8. Cach dan nguon / vien dan van ban
  9. Tu ngu ua dung vs tu ngu KHONG bao gio dung

Dung:
  python mine-style.py kho-bao-cao/ --out style-metrics.json --md style-report.md
  python mine-style.py bao-cao.docx --top 40
"""
from __future__ import annotations
import argparse, collections, json, os, re, statistics, subprocess, sys, unicodedata

# ---------------------------------------------------------------- doc file
def read_docx(path):
    try:
        import docx
    except ImportError:
        sys.exit("Can: pip install python-docx")
    d = docx.Document(path)
    out = []
    for p in d.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        style = (p.style.name or "").lower()
        kind = "heading" if "heading" in style or "đề mục" in style else "body"
        if re.match(r"^\s*([-*+•]|\d+[.)])\s+", t) or "list" in style:
            kind = "bullet"
        if re.match(r"^\s*(hình|bảng|figure|table)\s+\d", t, re.I):
            kind = "caption"
        out.append((kind, t))
    return out


def read_pdf(path):
    try:
        import pymupdf as fitz
    except ImportError:
        sys.exit("Can: pip install pymupdf")
    doc = fitz.open(path)
    out = []
    for page in doc:
        for blk in page.get_text("blocks"):
            t = (blk[4] or "").strip()
            if len(t) < 20:
                continue
            kind = "bullet" if re.match(r"^\s*([-*+•]|\d+[.)])\s+", t) else "body"
            if re.match(r"^\s*(hình|bảng)\s+\d", t, re.I):
                kind = "caption"
            out.append((kind, re.sub(r"\s*\n\s*", " ", t)))
    return out


def read_text(path):
    out = []
    for para in re.split(r"\n\s*\n", open(path, encoding="utf-8", errors="ignore").read()):
        t = para.strip()
        if not t:
            continue
        kind = ("heading" if t.startswith("#")
                else "bullet" if re.match(r"^\s*([-*+•]|\d+[.)])\s+", t)
                else "caption" if re.match(r"^\s*(hình|bảng)\s+\d", t, re.I)
                else "body")
        out.append((kind, t))
    return out


READERS = {".docx": read_docx, ".pdf": read_pdf, ".md": read_text, ".txt": read_text}

# ---------------------------------------------------------------- tach cau
ABBR = ["TS", "ThS", "KS", "GS", "PGS", "TT", "NĐ", "QĐ", "VD", "vd", "v.v",
        "TCVN", "QCVN", "St", "Nxb", "TP", "Q", "P"]
_ABBR_RE = re.compile(r"\b(" + "|".join(map(re.escape, ABBR)) + r")\.")


def split_sentences(text):
    t = _ABBR_RE.sub(lambda m: m.group(1) + "<DOT>", text)
    t = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", t)      # 1.875
    t = re.sub(r"(\d),(\d)", r"\1<CMA>\2", t)       # 4,50
    parts = re.split(r"(?<=[.!?;:])\s+(?=[A-ZĐÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ0-9])", t)
    out = []
    for s in parts:
        s = s.replace("<DOT>", ".").replace("<CMA>", ",").strip()
        if len(s) > 8:
            out.append(s)
    return out


def words(s):
    return re.findall(r"[0-9A-Za-zÀ-ỹ]+", s)


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


# ---------------------------------------------------------------- tu dien do
PASSIVE = [r"\bđược\b", r"\bbị\b"]
SELF_REF = ["đơn vị tư vấn", "tư vấn thiết kế", "chúng tôi", "đơn vị lập báo cáo",
            "nhà thầu tư vấn", "liên danh tư vấn", "tư vấn kiến nghị", "báo cáo này"]
HEDGE = ["khoảng", "tương đối", "cơ bản", "nhìn chung", "phần lớn", "hầu hết",
         "có thể", "dự kiến", "ước tính", "tạm tính"]
PUFF = ["tuyệt vời", "ấn tượng", "vô cùng", "hoàn hảo", "xuất sắc", "rất tốt",
        "đáng kinh ngạc", "tối ưu nhất", "hiện đại bậc nhất", "vượt trội hoàn toàn"]
CITE_PATTERNS = {
    "theo_X": r"\b[Tt]heo\s+(TCVN|QCVN|Nghị định|Thông tư|Quyết định|Luật)",
    "can_cu_X": r"\b[CC]ăn\s*cứ\s+(TCVN|QCVN|Nghị định|Thông tư|Quyết định|Luật)",
    "tuan_thu_X": r"\b(tuân thủ|phù hợp với|đáp ứng)\s+(TCVN|QCVN|quy định)",
    "ngoac_don": r"\((TCVN|QCVN|NĐ|TT|QĐ)[^)]{0,40}\)",
    "nguon_duoi_bang": r"\[?[Nn]guồn\s*:",
}
LEGAL_RE = re.compile(r"\b(TCVN|QCVN)\s*[\d\-]+\s*[:\-]\s*\d{4}"
                      r"|\b(?:Nghị định|NĐ)\s*\d+/\d{4}"
                      r"|\b(?:Thông tư|TT)\s*\d+/\d{4}", re.I)
NUM_UNIT = re.compile(r"([+-]?\d[\d.,]*(?:\s\d{3})*)(\s*)(m3/s|m³/s|km2|km²|m2|m²|kN/m2|kN|MPa|"
                      r"kg/m3|mm|cm|km|m|ha|%|‰)(?![\w])", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file hoac thu muc")
    ap.add_argument("--out", default="style-metrics.json")
    ap.add_argument("--md", default="", help="xuat ban tom tat markdown")
    ap.add_argument("--top", type=int, default=30, help="so cum tu lay vao ngan hang")
    ap.add_argument("--min-files", type=int, default=2,
                    help="cum tu phai xuat hien o >= N file moi tinh la 'thoi quen'")
    ap.add_argument("--min-count", type=int, default=3,
                    help="cum tu phai lap >= N lan")
    args = ap.parse_args()

    files = []
    if os.path.isdir(args.path):
        for root, _, fs in os.walk(args.path):
            for f in sorted(fs):
                if os.path.splitext(f)[1].lower() in READERS and not f.startswith("~$"):
                    files.append(os.path.join(root, f))
    else:
        files = [args.path]
    if not files:
        sys.exit("Khong tim thay file .docx/.pdf/.md/.txt nao")

    sent_lens, para_sents = [], []
    n_body = n_bullet = n_caption = n_head = 0
    passive_hits = total_sents = 0
    opener_counter = collections.Counter()      # cum mo cau
    ngram_files = collections.defaultdict(set)  # ngram -> tap file
    ngram_count = collections.Counter()
    selfref = collections.Counter()
    hedge = collections.Counter()
    puff = collections.Counter()
    cite = collections.Counter()
    dec_comma = dec_dot = 0
    thou_dot = thou_space = thou_none = 0
    unit_space = unit_nospace = 0
    unit_forms = collections.Counter()
    legal_forms = collections.Counter()
    para_open_kind = collections.Counter()

    for fp in files:
        ext = os.path.splitext(fp)[1].lower()
        try:
            blocks = READERS[ext](fp)
        except Exception as e:
            print(f"  ! bo qua {os.path.basename(fp)}: {e}", file=sys.stderr)
            continue
        for kind, text in blocks:
            if kind == "heading":
                n_head += 1
                continue
            if kind == "caption":
                n_caption += 1
                continue
            if kind == "bullet":
                n_bullet += 1
                continue
            n_body += 1

            sents = split_sentences(text)
            if not sents:
                continue
            para_sents.append(len(sents))

            # kieu mo doan
            first = sents[0]
            fw = strip_accents(words(first)[0]) if words(first) else ""
            if re.match(r"^\d", first):
                para_open_kind["bat dau bang so"] += 1
            elif fw in ("theo", "can", "cancu"):
                para_open_kind["bat dau bang nguon/can cu"] += 1
            elif fw in ("ket", "qua"):
                para_open_kind["bat dau bang ket qua"] += 1
            elif fw in ("do", "vi", "nhu", "tuy", "ngoai", "ben", "tren"):
                para_open_kind["bat dau bang lien tu"] += 1
            else:
                para_open_kind["bat dau bang chu the"] += 1

            for s in sents:
                total_sents += 1
                w = words(s)
                sent_lens.append(len(w))
                if any(re.search(p, s) for p in PASSIVE):
                    passive_hits += 1
                # cum mo cau (3 tu dau)
                if len(w) >= 3:
                    opener_counter[" ".join(w[:3]).lower()] += 1
                # ngram chuc nang 3-5 tu, khong chua so
                lw = [x.lower() for x in w if not x.isdigit()]
                for n in (3, 4, 5):
                    for i in range(len(lw) - n + 1):
                        g = " ".join(lw[i:i + n])
                        if any(ch.isdigit() for ch in g):
                            continue
                        ngram_count[g] += 1
                        ngram_files[g].add(fp)

            low = text.lower()
            for k in SELF_REF:
                if k in low:
                    selfref[k] += low.count(k)
            for k in HEDGE:
                hedge[k] += len(re.findall(r"\b" + re.escape(k) + r"\b", low))
            for k in PUFF:
                if k in low:
                    puff[k] += low.count(k)
            for name, pat in CITE_PATTERNS.items():
                cite[name] += len(re.findall(pat, text))
            for m in LEGAL_RE.finditer(text):
                legal_forms[re.sub(r"\s+", " ", m.group(0))] += 1

            # quy uoc so
            for m in NUM_UNIT.finditer(text):
                num, gap, unit = m.group(1).strip(), m.group(2), m.group(3)
                unit_forms[unit.lower()] += 1
                if gap:
                    unit_space += 1
                else:
                    unit_nospace += 1
                if re.search(r",\d", num):
                    dec_comma += 1
                elif re.search(r"\.\d{1,2}$", num):
                    dec_dot += 1
                if re.search(r"\d\.\d{3}\b", num):
                    thou_dot += 1
                elif re.search(r"\d\s\d{3}\b", num):
                    thou_space += 1
                elif len(re.sub(r"\D", "", num)) >= 4:
                    thou_none += 1

    if not sent_lens:
        sys.exit("Khong bóc được câu nào. Kiểm tra lại định dạng file đầu vào.")

    # ngan hang cum tu: phai xuat hien o >= min_files file
    bank = [(g, c, len(ngram_files[g])) for g, c in ngram_count.items()
            if len(ngram_files[g]) >= min(args.min_files, len(files)) and c >= args.min_count]
    # uu tien ngram dai va lap nhieu, bo ngram bi chua trong ngram dai hon
    bank.sort(key=lambda t: (-t[1] * (len(t[0].split()) ** 1.5)))
    chosen, seen = [], []
    for g, c, nf in bank:
        if any(g in s for s in seen):
            continue
        seen.append(g)
        chosen.append({"cum_tu": g, "so_lan": c, "so_file": nf})
        if len(chosen) >= args.top:
            break

    n_content = n_body + n_bullet
    M = {
        "so_file_quet": len(files),
        "cau": {
            "tong_so": total_sents,
            "do_dai_tb": round(statistics.mean(sent_lens), 1),
            "do_dai_trung_vi": statistics.median(sent_lens),
            "p10": sorted(sent_lens)[len(sent_lens) // 10],
            "p90": sorted(sent_lens)[len(sent_lens) * 9 // 10],
            "cau_dai_hon_40_tu_pct": round(
                100 * sum(1 for x in sent_lens if x > 40) / len(sent_lens), 1),
        },
        "doan": {
            "so_cau_tb": round(statistics.mean(para_sents), 1) if para_sents else 0,
            "so_cau_trung_vi": statistics.median(para_sents) if para_sents else 0,
            "doan_duoi_3_cau_pct": round(
                100 * sum(1 for x in para_sents if x < 3) / len(para_sents), 1)
            if para_sents else 0,
        },
        "bo_cuc": {
            "doan_van_xuoi": n_body, "dong_bullet": n_bullet,
            "caption": n_caption, "de_muc": n_head,
            "ty_le_bullet_pct": round(100 * n_bullet / n_content, 1) if n_content else 0,
        },
        "bi_dong": {
            "so_cau_co_duoc_bi": passive_hits,
            "ty_le_pct": round(100 * passive_hits / total_sents, 1),
        },
        "quy_uoc_so": {
            "dau_thap_phan": ("phẩy" if dec_comma >= dec_dot else "chấm"),
            "dem_phay": dec_comma, "dem_cham": dec_dot,
            "dau_hang_nghin": max([("chấm", thou_dot), ("khoảng trắng", thou_space),
                                   ("không dùng", thou_none)], key=lambda t: t[1])[0],
            "khoang_trang_truoc_don_vi": ("có" if unit_space >= unit_nospace else "không"),
            "dem_co_khoang": unit_space, "dem_khong_khoang": unit_nospace,
            "dang_don_vi_hay_dung": unit_forms.most_common(10),
        },
        "xung_ho_don_vi": selfref.most_common(6),
        "tu_ram_ra": hedge.most_common(10),
        "tu_cam_tinh_PHAI_TRANH": puff.most_common(10),
        "cach_dan_nguon": cite.most_common(),
        "dang_trich_van_ban": legal_forms.most_common(8),
        "kieu_mo_doan": para_open_kind.most_common(),
        "cum_mo_cau_hay_dung": opener_counter.most_common(20),
        "ngan_hang_cum_tu": chosen,
    }

    json.dump(M, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Đã quét {len(files)} file · {total_sents} câu · {n_body} đoạn văn xuôi")
    print(f"→ {args.out}")

    if args.md:
        L = []
        a = L.append
        a("# Hồ sơ văn phong — đo từ kho báo cáo\n")
        a(f"Nguồn: **{len(files)} file**, {total_sents} câu, {n_body} đoạn văn xuôi.\n")
        a("## Chỉ số định lượng\n")
        a("| Chỉ số | Giá trị | Áp dụng khi viết |")
        a("|---|---|---|")
        c, d, b = M["cau"], M["doan"], M["bo_cuc"]
        a(f"| Độ dài câu trung bình | **{c['do_dai_tb']} từ** | Viết câu {c['p10']}–{c['p90']} từ |")
        a(f"| Câu dài > 40 từ | {c['cau_dai_hon_40_tu_pct']}% | Giữ dưới ngưỡng này |")
        a(f"| Số câu / đoạn | **{d['so_cau_tb']}** | Đoạn phân tích tối thiểu 3 câu |")
        a(f"| Đoạn dưới 3 câu | {d['doan_duoi_3_cau_pct']}% | |")
        a(f"| Tỉ lệ bullet | **{b['ty_le_bullet_pct']}%** | Không vượt quá |")
        a(f"| Câu bị động (được/bị) | {M['bi_dong']['ty_le_pct']}% | |")
        q = M["quy_uoc_so"]
        a(f"| Dấu thập phân | **{q['dau_thap_phan']}** | 4,50 m |")
        a(f"| Dấu hàng nghìn | {q['dau_hang_nghin']} | |")
        a(f"| Khoảng trắng trước đơn vị | {q['khoang_trang_truoc_don_vi']} | |")
        a("\n## Cách mở đoạn\n")
        for k, v in M["kieu_mo_doan"]:
            a(f"- {k}: {v} lần")
        a("\n## Ngân hàng cụm từ (dùng lại được)\n")
        for it in chosen[:args.top]:
            a(f"- “{it['cum_tu']}” — {it['so_lan']} lần / {it['so_file']} file")
        a("\n## Cách xưng hô đơn vị\n")
        for k, v in M["xung_ho_don_vi"]:
            a(f"- “{k}” — {v} lần")
        a("\n## Cách dẫn nguồn\n")
        for k, v in M["cach_dan_nguon"]:
            a(f"- {k}: {v} lần")
        if M["tu_cam_tinh_PHAI_TRANH"]:
            a("\n## ⚠️ Từ cảm tính xuất hiện trong kho (cần loại bỏ)\n")
            for k, v in M["tu_cam_tinh_PHAI_TRANH"]:
                a(f"- “{k}” — {v} lần")
        open(args.md, "w", encoding="utf-8").write("\n".join(L))
        print(f"→ {args.md}")


if __name__ == "__main__":
    main()
