#!/usr/bin/env python3
"""
geo-index-photos.py — Gan ANH HIEN TRUONG vao LY TRINH cua tuyen cong trinh.

Doc GPS trong EXIF cua tung anh -> chieu len tuyen (LineString lay tu file
KMZ/KML) -> tra ve ly trinh dang K0+245 va khoang cach vuong goc toi tuyen.

Hoan toan TAT DINH (khong dung AI). Chinh xac bang chinh chinh xac cua GPS.

Dung:
  python geo-index-photos.py anh/ tuyen.kmz --out anh-ly-trinh.csv --kml-out diem-anh.kml
  python geo-index-photos.py anh/ tuyen.kmz --epsg 32648 --max-offset 200

Ghi chu quan trong:
  * Anh gui qua Zalo / Messenger BI XOA EXIF -> phai lay file goc tu the nho.
  * Phai bat dinh vi khi chup. Sai so GPS dien thoai 3-10 m (duoi tan cay 20-50 m).
  * --epsg: he toa do phang de tinh khoang cach. Mac dinh tu chon UTM theo kinh do.
    VN: UTM 48N = EPSG:32648 (tay VN), UTM 49N = EPSG:32649 (dong VN).
"""
from __future__ import annotations
import argparse, csv, io, math, os, re, sys, zipfile, xml.etree.ElementTree as ET
from datetime import datetime

from PIL import Image, ExifTags
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points
from pyproj import Transformer, CRS

IMG_EXT = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff", ".webp"}
GPSTAGS = {v: k for k, v in ExifTags.GPSTAGS.items()}


# ------------------------------------------------------------------ EXIF
def _rat(x):
    try:
        return float(x)
    except Exception:
        try:
            return x[0] / x[1]
        except Exception:
            return None


def dms_to_deg(dms, ref):
    if not dms:
        return None
    d, m, s = (_rat(v) for v in dms)
    if d is None:
        return None
    val = d + (m or 0) / 60.0 + (s or 0) / 3600.0
    if ref in ("S", "W"):
        val = -val
    return val


def read_exif(path):
    """Tra ve dict: lat, lon, alt, dt, direction (huong ong kinh), make, model."""
    out = {"lat": None, "lon": None, "alt": None, "dt": None,
           "direction": None, "make": "", "model": ""}
    try:
        im = Image.open(path)
        exif = im.getexif()
        if not exif:
            return out
        out["make"] = str(exif.get(271, "") or "")
        out["model"] = str(exif.get(272, "") or "")
        dt = exif.get(306) or exif.get(36867)
        if dt:
            out["dt"] = str(dt)
        gps = exif.get_ifd(0x8825) or {}
        if gps:
            out["lat"] = dms_to_deg(gps.get(GPSTAGS["GPSLatitude"]),
                                    gps.get(GPSTAGS["GPSLatitudeRef"]))
            out["lon"] = dms_to_deg(gps.get(GPSTAGS["GPSLongitude"]),
                                    gps.get(GPSTAGS["GPSLongitudeRef"]))
            alt = gps.get(GPSTAGS["GPSAltitude"])
            if alt is not None:
                a = _rat(alt)
                if a is not None:
                    if gps.get(GPSTAGS["GPSAltitudeRef"]) in (1, b"\x01"):
                        a = -a
                    out["alt"] = round(a, 1)
            d = gps.get(GPSTAGS["GPSImgDirection"])
            if d is not None:
                dd = _rat(d)
                if dd is not None:
                    out["direction"] = round(dd, 1)
    except Exception as e:
        print(f"  ! EXIF loi {os.path.basename(path)}: {e}", file=sys.stderr)
    return out


# ------------------------------------------------------------------ KMZ / KML
def read_kml_lines(path):
    """Tra ve list (ten, [(lon,lat), ...]) cho moi LineString trong KMZ/KML."""
    if path.lower().endswith(".kmz"):
        with zipfile.ZipFile(path) as z:
            name = next((n for n in z.namelist() if n.lower().endswith(".kml")), None)
            if not name:
                raise SystemExit("KMZ khong chua file .kml")
            data = z.read(name)
    else:
        data = open(path, "rb").read()

    root = ET.fromstring(data)
    ns = {"k": "http://www.opengis.net/kml/2.2"}

    def findall(tag):
        r = root.findall(f".//k:{tag}", ns)
        return r if r else root.findall(f".//{tag}")

    lines = []
    for pm in (findall("Placemark") or [root]):
        nm = pm.find("k:name", ns)
        nm = nm.text if nm is not None else (pm.findtext("name") or "")
        for ls in (pm.findall(".//k:LineString", ns) or pm.findall(".//LineString")):
            c = ls.find("k:coordinates", ns)
            if c is None:
                c = ls.find("coordinates")
            if c is None or not c.text:
                continue
            pts = []
            for tok in c.text.replace("\n", " ").split():
                parts = tok.split(",")
                if len(parts) >= 2:
                    pts.append((float(parts[0]), float(parts[1])))
            if len(pts) >= 2:
                lines.append((nm or f"tuyen-{len(lines)+1}", pts))
    return lines


# ------------------------------------------------------------------ chieu
def pick_epsg(lon):
    zone = int((lon + 180) // 6) + 1
    return 32600 + zone          # UTM bac ban cau


def fmt_chainage(m):
    km = int(m // 1000)
    return f"K{km}+{m - km*1000:06.1f}".replace("+0", "+", 1) if False else f"K{km}+{int(round(m - km*1000)):03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo_dir")
    ap.add_argument("kmz")
    ap.add_argument("--out", default="anh-ly-trinh.csv")
    ap.add_argument("--kml-out", default="", help="xuat KML diem anh de mo Google Earth")
    ap.add_argument("--epsg", type=int, default=0, help="EPSG he phang; 0 = tu chon UTM")
    ap.add_argument("--max-offset", type=float, default=200.0,
                    help="anh cach tuyen qua nguong nay -> danh dau CAN XEM LAI (m)")
    ap.add_argument("--segments", default="",
                    help='phan doan, vd "D1:0-500,D2:500-1200,D3:1200-2000" (met)')
    args = ap.parse_args()

    lines = read_kml_lines(args.kmz)
    if not lines:
        raise SystemExit("Khong tim thay LineString nao trong KMZ. "
                         "Tuyen cong trinh phai duoc ve dang duong (path), khong phai diem.")
    name, coords = max(lines, key=lambda t: len(t[1]))
    print(f"Tuyen: '{name}' — {len(coords)} dinh")

    epsg = args.epsg or pick_epsg(coords[0][0])
    tr = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(epsg), always_xy=True)
    inv = Transformer.from_crs(CRS.from_epsg(epsg), CRS.from_epsg(4326), always_xy=True)
    line = LineString([tr.transform(lon, lat) for lon, lat in coords])
    print(f"He phang EPSG:{epsg} — chieu dai tuyen {line.length:,.1f} m")

    segs = []
    for s in filter(None, args.segments.split(",")):
        nm, rng = s.split(":")
        a, b = rng.split("-")
        segs.append((nm.strip(), float(a), float(b)))

    rows, no_gps = [], []
    for root, _, files in os.walk(args.photo_dir):
        for fn in sorted(files):
            if os.path.splitext(fn)[1].lower() not in IMG_EXT:
                continue
            p = os.path.join(root, fn)
            e = read_exif(p)
            if e["lat"] is None or e["lon"] is None:
                no_gps.append(os.path.relpath(p, args.photo_dir))
                continue
            x, y = tr.transform(e["lon"], e["lat"])
            pt = Point(x, y)
            chain = line.project(pt)                 # ly trinh doc tuyen (m)
            near = line.interpolate(chain)
            offset = pt.distance(near)               # khoang cach vuong goc (m)
            seg = next((nm for nm, a, b in segs if a <= chain < b), "")
            note = ""
            if offset > args.max_offset:
                note = f"CAN XEM LAI — cach tuyen {offset:.0f} m"
            elif chain <= 0.5 or chain >= line.length - 0.5:
                note = "Ngoai pham vi tuyen (dau/cuoi)"
            rows.append({
                "file": os.path.relpath(p, args.photo_dir),
                "ly_trinh": fmt_chainage(chain),
                "chainage_m": round(chain, 1),
                "offset_m": round(offset, 1),
                "doan": seg,
                "lat": round(e["lat"], 7), "lon": round(e["lon"], 7),
                "cao_do_gps": e["alt"] if e["alt"] is not None else "",
                "huong_chup": e["direction"] if e["direction"] is not None else "",
                "thoi_gian": e["dt"] or "",
                "thiet_bi": (e["make"] + " " + e["model"]).strip(),
                "ghi_chu": note,
            })

    rows.sort(key=lambda r: r["chainage_m"])
    if rows:
        with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    print(f"\n{len(rows)} anh co GPS -> {args.out}")
    if no_gps:
        print(f"{len(no_gps)} anh KHONG co GPS trong EXIF (thuong do gui qua Zalo/"
              f"Messenger hoac tat dinh vi):")
        for n in no_gps[:10]:
            print("   -", n)

    if args.kml_out and rows:
        parts = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
                 f'<name>Diem chup anh — {name}</name>']
        for r in rows:
            desc = (f"{r['ly_trinh']} · cach tuyen {r['offset_m']} m · "
                    f"{r['thoi_gian']} · {r['ghi_chu']}")
            parts.append(f"<Placemark><name>{r['ly_trinh']} {os.path.basename(r['file'])}</name>"
                         f"<description><![CDATA[{desc}]]></description>"
                         f"<Point><coordinates>{r['lon']},{r['lat']},0</coordinates></Point>"
                         f"</Placemark>")
        parts.append("</Document></kml>")
        open(args.kml_out, "w", encoding="utf-8").write("\n".join(parts))
        print(f"KML diem anh -> {args.kml_out} (mo bang Google Earth de kiem tra bang mat)")

    # tom tat theo doan
    if segs and rows:
        print("\nPhan bo anh theo doan:")
        for nm, a, b in segs:
            n = sum(1 for r in rows if a <= r["chainage_m"] < b)
            flag = "  <-- THIEU ANH" if n == 0 else ""
            print(f"  {nm} (K{int(a//1000)}+{int(a%1000):03d} - K{int(b//1000)}+{int(b%1000):03d}): {n} anh{flag}")


if __name__ == "__main__":
    main()
