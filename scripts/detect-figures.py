#!/usr/bin/env python3
"""
detect-figures.py — Tu dong PHAT HIEN cac vung hinh / ban ve trong file PDF.

Khac voi crop-pdf-figure.py (phai biet truoc bbox), script nay TU TIM ra
co bao nhieu hinh, moi hinh o dau, caption la gi.

Nguyen ly:
  1. Lay toan bo net ve vector (page.get_drawings) + anh raster (page.get_images)
  2. Do bbox cua chung vao mot mask nhi phan  ->  morphological closing
     -> cac net gan nhau dinh lai thanh MOT vung  -> connected components
  3. Loai bo: khung vien trang, khung ten ban ve, vun rac qua nho
  4. Bat caption: khoi text bat dau bang "Hinh/Hình/Bang/Bảng/Figure/Table"
     nam ngay duoi (hoac tren) vung hinh
  5. Xuat JSON danh muc ung vien + (tuy chon) render thumbnail de model
     vision xem va phan loai

Dung:
  python detect-figures.py ban-ve.pdf --out catalog.json --render thumbs/
  python detect-figures.py ban-ve.pdf --pages 1-10 --min-area 0.03
"""
from __future__ import annotations
import argparse, json, os, re, sys, zipfile
from dataclasses import dataclass, asdict, field

import numpy as np
import cv2
import pymupdf as fitz

# ---------------------------------------------------------------- tham so
SCALE = 2.0          # px tren 1 point khi dung mask
GAP_PT = 10.0        # net cach nhau duoi nguong nay coi la cung 1 hinh (point)
MIN_AREA_RATIO = 0.02   # vung nho hon 2% dien tich trang -> bo
MAX_AREA_RATIO = 0.92   # vung lon hon 92% -> nghi la khung vien trang
CAPTION_GAP_PT = 60.0   # caption phai nam trong 60pt duoi/tren vung hinh

CAPTION_RE = re.compile(
    r"^\s*(hình|hinh|bảng|bang|figure|fig\.|table|biểu\s*đồ|bieu\s*do|sơ\s*đồ|so\s*do)"
    r"\s*[\dIVXivx]+[\.\-–:\s]", re.IGNORECASE)

TITLEBLOCK_KEYWORDS = [
    "chủ đầu tư", "chu dau tu", "tên bản vẽ", "ten ban ve", "thiết kế", "thiet ke",
    "chủ trì", "chu tri", "kiểm tra", "kiem tra", "tỷ lệ", "ty le", "bản vẽ số",
    "ban ve so", "ký hiệu", "ky hieu", "giai đoạn", "giai doan", "chủ nhiệm",
]


@dataclass
class FigureCandidate:
    id: str
    page: int                      # 1-based
    bbox: list                     # [x0, y0, x1, y1] point PDF
    bbox_rounded: str
    area_ratio: float
    n_vector: int
    n_raster: int
    kind: str                      # vector | raster | mixed
    caption: str = ""
    caption_pos: str = ""          # below | above | none
    text_inside: list = field(default_factory=list)   # nhan / kich thuoc doc duoc
    flags: list = field(default_factory=list)         # titleblock, page_border, ...
    thumb: str = ""


# ---------------------------------------------------------------- tien ich
def rect_to_mask(mask, r, page_rect, scale=SCALE):
    x0 = int(max(0, (r[0] - page_rect.x0) * scale))
    y0 = int(max(0, (r[1] - page_rect.y0) * scale))
    x1 = int(min(mask.shape[1] - 1, (r[2] - page_rect.x0) * scale))
    y1 = int(min(mask.shape[0] - 1, (r[3] - page_rect.y0) * scale))
    if x1 > x0 and y1 > y0:
        mask[y0:y1 + 1, x0:x1 + 1] = 255


def parse_pages(spec, npages):
    if not spec:
        return list(range(npages))
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a) - 1, int(b)))
        else:
            out.append(int(part) - 1)
    return [p for p in out if 0 <= p < npages]


def looks_like_titleblock(text: str) -> bool:
    t = text.lower()
    hits = sum(1 for k in TITLEBLOCK_KEYWORDS if k in t)
    return hits >= 2


# ---------------------------------------------------------------- lõi
def _cluster(boxes, prect, gap_pt, min_area_ratio):
    """Do bbox vao mask -> closing -> connected components -> tra ve list fitz.Rect."""
    W = int(prect.width * SCALE) + 1
    H = int(prect.height * SCALE) + 1
    mask = np.zeros((H, W), dtype=np.uint8)
    for b in boxes:
        rect_to_mask(mask, b, prect)
    if mask.max() == 0:
        return []
    k = max(3, int(gap_pt * SCALE))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    n, _, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
    page_area = prect.width * prect.height
    rects = []
    for lab in range(1, n):
        x, y, w, h, _ = stats[lab]
        r = fitz.Rect(prect.x0 + x / SCALE, prect.y0 + y / SCALE,
                      prect.x0 + (x + w) / SCALE, prect.y0 + (y + h) / SCALE)
        if (r.width * r.height) / page_area >= min_area_ratio:
            rects.append(r)
    return rects


def detect_page(page, page_index, min_area_ratio, gap_pt,
                strip_frame=True, frame_ratio=0.55) -> list[FigureCandidate]:
    prect = page.rect
    page_area = prect.width * prect.height

    # --- 1. net ve vector
    vec_boxes = []
    try:
        for d in page.get_drawings():
            r = d.get("rect")
            if r is None:
                continue
            if r.width <= 0.3 and r.height <= 0.3:
                continue                      # cham, vun
            vec_boxes.append((r.x0, r.y0, r.x1, r.y1))
    except Exception as e:
        print(f"  ! get_drawings loi trang {page_index+1}: {e}", file=sys.stderr)

    # --- 2. anh raster nhung trong trang
    ras_boxes = []
    for img in page.get_images(full=True):
        xref = img[0]
        try:
            for r in page.get_image_rects(xref):
                ras_boxes.append((r.x0, r.y0, r.x1, r.y1))
        except Exception:
            pass

    # --- 3. khoi text de bat caption / khung ten
    text_blocks = []
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, txt, *_ = b
        txt = (txt or "").strip()
        if txt:
            text_blocks.append((fitz.Rect(x0, y0, x1, y1), txt))

    # --- 4. TACH KHUNG (to ban ve CAD): khung vien trang + khung ten
    #     Neu khong lam buoc nay, khung vien noi tat ca hinh thanh MOT khoi.
    dropped_frame, titleblocks = 0, []
    if strip_frame:
        keep = []
        for b in vec_boxes:
            bw, bh = b[2] - b[0], b[3] - b[1]
            a = (bw * bh) / page_area
            spans_w = bw > 0.88 * prect.width
            spans_h = bh > 0.88 * prect.height
            # hinh chu nhat bao gan het trang -> khung vien
            if a > frame_ratio and spans_w and spans_h:
                dropped_frame += 1
                continue
            # duong ke chay het chieu ngang / doc trang -> net khung
            if (spans_w and bh < 3) or (spans_h and bw < 3):
                dropped_frame += 1
                continue
            keep.append(b)
        vec_boxes = keep

        # khung ten: gom cum tren tap con da bo khung, tim cum chua tu khoa
        for r in _cluster(vec_boxes + ras_boxes, prect, gap_pt, min_area_ratio):
            inside = " ".join(t for (tr, t) in text_blocks
                              if r.contains(tr.tl) and r.contains(tr.br))
            if looks_like_titleblock(inside):
                titleblocks.append(r)
        if titleblocks:
            vec_boxes = [b for b in vec_boxes
                         if not any(tb.contains(fitz.Rect(b)) for tb in titleblocks)]
            ras_boxes = [b for b in ras_boxes
                         if not any(tb.contains(fitz.Rect(b)) for tb in titleblocks)]

    rects = _cluster(vec_boxes + ras_boxes, prect, gap_pt, min_area_ratio)

    out = []
    for rect in rects:
        ratio = (rect.width * rect.height) / page_area

        flags = []
        if ratio > MAX_AREA_RATIO:
            flags.append("nghi_khung_vien_trang")
        if dropped_frame:
            flags.append(f"da_tach_khung({dropped_frame})")

        n_vec = sum(1 for b in vec_boxes if fitz.Rect(b).intersects(rect))
        n_ras = sum(1 for b in ras_boxes if fitz.Rect(b).intersects(rect))
        kind = "mixed" if (n_vec and n_ras) else ("raster" if n_ras else "vector")

        # text nam trong vung -> nhan, kich thuoc, hoac khung ten
        inside = [t for (r, t) in text_blocks if rect.contains(r.tl) and rect.contains(r.br)]
        joined = " ".join(inside)
        if looks_like_titleblock(joined):
            flags.append("khung_ten_ban_ve")

        # caption: khoi text ngay duoi, roi den ngay tren
        caption, cpos = "", "none"
        best = None
        for (r, t) in text_blocks:
            if not CAPTION_RE.match(t):
                continue
            # duoi
            if 0 <= r.y0 - rect.y1 <= CAPTION_GAP_PT and r.x1 > rect.x0 and r.x0 < rect.x1:
                d = r.y0 - rect.y1
                if best is None or d < best[0]:
                    best = (d, t, "below")
            # tren
            elif 0 <= rect.y0 - r.y1 <= CAPTION_GAP_PT and r.x1 > rect.x0 and r.x0 < rect.x1:
                d = rect.y0 - r.y1
                if best is None or d < best[0]:
                    best = (d, t, "above")
        if best:
            caption = " ".join(best[1].split())[:300]
            cpos = best[2]

        out.append(FigureCandidate(
            id="",
            page=page_index + 1,
            bbox=[round(v, 1) for v in (rect.x0, rect.y0, rect.x1, rect.y1)],
            bbox_rounded=f"{rect.x0:.0f},{rect.y0:.0f},{rect.x1:.0f},{rect.y1:.0f}",
            area_ratio=round(ratio, 4),
            n_vector=n_vec, n_raster=n_ras, kind=kind,
            caption=caption, caption_pos=cpos,
            text_inside=[" ".join(t.split())[:80] for t in inside[:12]],
            flags=flags,
        ))

    out.sort(key=lambda c: (-c.area_ratio))
    return out


def render_thumb(page, cand: FigureCandidate, outdir: str, dpi=110, pad=6):
    r = fitz.Rect(*cand.bbox)
    r = fitz.Rect(r.x0 - pad, r.y0 - pad, r.x1 + pad, r.y1 + pad) & page.rect
    pix = page.get_pixmap(clip=r, dpi=dpi)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{cand.id}.png")
    pix.save(path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", default="figure-candidates.json")
    ap.add_argument("--pages", default="", help='vd "1-10" hoac "3,5,7"')
    ap.add_argument("--render", default="", help="thu muc xuat thumbnail PNG")
    ap.add_argument("--min-area", type=float, default=MIN_AREA_RATIO)
    ap.add_argument("--gap", type=float, default=GAP_PT)
    ap.add_argument("--drop-titleblock", action="store_true",
                    help="bo cac vung nhan dien la khung ten ban ve")
    ap.add_argument("--no-strip-frame", action="store_true",
                    help="KHONG tach khung vien / khung ten to ban ve")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    pages = parse_pages(args.pages, doc.page_count)
    all_c: list[FigureCandidate] = []
    for pi in pages:
        page = doc[pi]
        cands = detect_page(page, pi, args.min_area, args.gap,
                            strip_frame=not args.no_strip_frame)
        for j, c in enumerate(cands, 1):
            c.id = f"P{pi+1:03d}F{j:02d}"
        if args.drop_titleblock:
            cands = [c for c in cands if "khung_ten_ban_ve" not in c.flags]
        if args.render:
            for c in cands:
                c.thumb = render_thumb(page, c, args.render)
        all_c += cands
        print(f"Trang {pi+1}: {len(cands)} ung vien")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"pdf": os.path.basename(args.pdf),
                   "n_pages_scanned": len(pages),
                   "candidates": [asdict(c) for c in all_c]},
                  f, ensure_ascii=False, indent=2)
    print(f"\nTong: {len(all_c)} ung vien -> {args.out}")
    if args.render:
        print(f"Thumbnail -> {args.render}/  (dua cho model vision phan loai)")


if __name__ == "__main__":
    main()
