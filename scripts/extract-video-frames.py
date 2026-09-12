#!/usr/bin/env python3
"""
extract-video-frames.py — Trich KHUNG HINH DUNG DUOC tu video hien truong / flycam.

Video 10 phut @30fps = 18.000 khung. Khong the dua het cho model vision xem.
Script nay loc con ~40-80 khung dang xem, theo 3 tang loc TAT DINH:

  Tang 1 — ffmpeg scene-detect: chi lay khung khi CANH DOI (khong lay deu theo giay)
  Tang 2 — do net (variance of Laplacian): bo khung rung / mo / lia may
  Tang 3 — perceptual hash: bo khung trung lap gan giong nhau

Sau do khung con lai moi dua cho model vision cham diem noi dung.
Neu video co GPS (DJI xuat file .SRT di kem), script doc luon toa do tung khung.

Dung:
  python extract-video-frames.py video.mp4 --out khung/ --scene 0.30 --max 80
  python extract-video-frames.py video.mp4 --out khung/ --srt video.SRT
"""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, sys

import cv2
import numpy as np


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def sharpness(path):
    """Variance of Laplacian — cang cao cang net. < 60 thuong la mo/rung."""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0
    if max(img.shape) > 900:
        s = 900 / max(img.shape)
        img = cv2.resize(img, None, fx=s, fy=s)
    return float(cv2.Laplacian(img, cv2.CV_64F).var())


def dhash(path, size=8):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = cv2.resize(img, (size + 1, size))
    diff = img[:, 1:] > img[:, :-1]
    return int("".join("1" if b else "0" for b in diff.flatten()), 2)


def hamming(a, b):
    return bin(a ^ b).count("1")


def parse_dji_srt(path):
    """DJI xuat .SRT chua toa do tung giay. Tra ve list (giay, lat, lon, alt)."""
    if not path or not os.path.exists(path):
        return []
    txt = open(path, encoding="utf-8", errors="ignore").read()
    out = []
    for blk in txt.split("\n\n"):
        t = re.search(r"(\d\d):(\d\d):(\d\d),(\d+)\s*-->", blk)
        la = re.search(r"\[?latitude\s*[:=]\s*(-?\d+\.\d+)", blk, re.I)
        lo = re.search(r"\[?long?itude\s*[:=]\s*(-?\d+\.\d+)", blk, re.I)
        al = re.search(r"(?:abs_)?alt\w*\s*[:=]\s*(-?\d+\.?\d*)", blk, re.I)
        if t and la and lo:
            sec = int(t.group(1)) * 3600 + int(t.group(2)) * 60 + int(t.group(3))
            out.append((sec, float(la.group(1)), float(lo.group(1)),
                        float(al.group(1)) if al else None))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default="khung/")
    ap.add_argument("--scene", type=float, default=0.30,
                    help="nguong doi canh 0..1 (thap = lay nhieu khung hon)")
    ap.add_argument("--fallback-every", type=float, default=3.0,
                    help="neu scene-detect ra qua it khung, lay deu moi N giay")
    ap.add_argument("--min-sharp", type=float, default=60.0)
    ap.add_argument("--hash-dist", type=int, default=6,
                    help="hai khung khac nhau duoi nguong nay coi la trung")
    ap.add_argument("--max", type=int, default=80)
    ap.add_argument("--srt", default="", help="file .SRT cua DJI (neu co)")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        raise SystemExit("Chua co ffmpeg. Cai: apt install ffmpeg / choco install ffmpeg")

    raw = os.path.join(args.out, "_raw")
    os.makedirs(raw, exist_ok=True)
    for f in os.listdir(raw):
        os.remove(os.path.join(raw, f))

    # --- Tang 1: scene detect
    r = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", args.video,
             "-vf", f"select='gt(scene,{args.scene})',showinfo", "-vsync", "vfr",
             "-frame_pts", "1", "-q:v", "3", os.path.join(raw, "s_%05d.jpg")])
    n1 = len(os.listdir(raw))
    print(f"Tang 1 (doi canh, nguong {args.scene}): {n1} khung")

    if n1 < 8:
        print(f"  -> qua it, chuyen sang lay deu moi {args.fallback_every}s")
        for f in os.listdir(raw):
            os.remove(os.path.join(raw, f))
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", args.video,
             "-vf", f"fps=1/{args.fallback_every}", "-q:v", "3",
             os.path.join(raw, "t_%05d.jpg")])
        n1 = len(os.listdir(raw))
        print(f"  -> {n1} khung")

    files = sorted(os.path.join(raw, f) for f in os.listdir(raw))

    # --- Tang 2: do net
    scored = [(f, sharpness(f)) for f in files]
    keep = [(f, s) for f, s in scored if s >= args.min_sharp]
    print(f"Tang 2 (do net >= {args.min_sharp}): {len(keep)}/{len(scored)} khung "
          f"(bo {len(scored)-len(keep)} khung mo/rung)")
    if not keep:
        keep = sorted(scored, key=lambda t: -t[1])[:args.max]

    # --- Tang 3: bo trung lap
    final, hashes = [], []
    for f, s in keep:
        h = dhash(f)
        if h is None:
            continue
        if any(hamming(h, hh) <= args.hash_dist for hh in hashes):
            continue
        hashes.append(h)
        final.append((f, s))
    print(f"Tang 3 (bo trung lap): {len(final)} khung")

    final = sorted(final, key=lambda t: -t[1])[:args.max]
    final = sorted(final, key=lambda t: t[0])

    # --- xuat
    srt = parse_dji_srt(args.srt)
    fps_probe = run(["ffprobe", "-v", "0", "-of", "csv=p=0", "-select_streams", "v:0",
                     "-show_entries", "stream=r_frame_rate", args.video])
    try:
        num, den = fps_probe.stdout.strip().split("/")
        fps = float(num) / float(den)
    except Exception:
        fps = 30.0

    meta = []
    for i, (f, s) in enumerate(final, 1):
        m = re.search(r"_(\d+)\.jpg$", f)
        pts = int(m.group(1)) if m else 0
        sec = pts / fps if f.split("/")[-1].startswith("s_") else pts * args.fallback_every
        name = f"F{i:03d}_t{int(sec):05d}s.jpg"
        dst = os.path.join(args.out, name)
        shutil.copy(f, dst)
        rec = {"file": name, "giay": round(sec, 1), "do_net": round(s, 1)}
        if srt:
            near = min(srt, key=lambda r: abs(r[0] - sec))
            if abs(near[0] - sec) <= 3:
                rec.update(lat=near[1], lon=near[2], alt=near[3])
        meta.append(rec)

    with open(os.path.join(args.out, "khung.json"), "w", encoding="utf-8") as fh:
        json.dump({"video": os.path.basename(args.video), "fps": round(fps, 2),
                   "frames": meta}, fh, ensure_ascii=False, indent=2)
    shutil.rmtree(raw, ignore_errors=True)
    print(f"\n-> {len(meta)} khung trong {args.out}  (kem khung.json)")
    print("   Buoc tiep: dua thu muc nay cho model vision cham diem noi dung.")
    if srt:
        print("   Da gan toa do GPS tung khung tu file SRT -> chay tiep geo-index-photos.py")


if __name__ == "__main__":
    main()
