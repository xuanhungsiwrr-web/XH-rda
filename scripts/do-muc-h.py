# -*- coding: utf-8 -*-
"""Đo văn phong THEO NHÓM ĐỀ MỤC (Mục H) — thứ mine-style.py chưa làm."""
import re, sys, glob, statistics, unicodedata
import docx

NHOM = [
 ("Sự cần thiết đầu tư",   r"sự cần thiết|mục tiêu đầu tư|hiện trạng.*sạt lở|tính cấp thiết|sự cấp thiết"),
 ("Căn cứ pháp lý",        r"căn cứ|cơ sở pháp lý|tài liệu.*lập|danh mục.*tiêu chuẩn|quy chuẩn.*áp dụng"),
 ("Điều kiện tự nhiên",    r"điều kiện tự nhiên|khí tượng|thu[ỷy] văn|địa hình|địa chất|đặc điểm khu vực|hiện trạng khu vực"),
 ("Giải pháp kỹ thuật",    r"giải pháp|thiết kế|kết cấu|quy mô|biện pháp thi công|vật liệu|tính toán"),
 ("So sánh phương án",     r"so sánh|lựa chọn phương án|phương án.*kiến nghị|đánh giá.*phương án"),
 ("Kết luận – kiến nghị",  r"kết luận|kiến nghị|đề xuất.*thực hiện"),
]
BULLET = re.compile(r"^\s*([-•*▪–]|\d+[.)]|[a-zA-Z][.)]|[+])\s+")
CAU = re.compile(r"[.!?;]+\s+|[.!?]$")

def chuan(s): return unicodedata.normalize("NFC", s).lower()

def phan_nhom(tieu_de):
    t = chuan(tieu_de)
    for ten, pat in NHOM:
        if re.search(pat, t): return ten
    return None

def dem_cau(t):
    return max(1, len([c for c in CAU.split(t) if c and c.strip()]))

kq = {ten: {"doan":0,"bullet":0,"cau":[],"tu_doan":[],"so_luong_muc":0} for ten,_ in NHOM}
for f in sorted(glob.glob(sys.argv[1] + "/*.docx")):
    d = docx.Document(f)
    nhom = None
    for p in d.paragraphs:
        t = p.text.strip()
        if not t: continue
        st = (p.style.name or "").lower()
        la_heading = st.startswith("heading") or bool(re.match(r"^(chương|phần|[IVX]+\.|\d+(\.\d+)*\.?)\s+\S", t)) and len(t) < 120
        if la_heading:
            n = phan_nhom(t)
            if n: nhom = n; kq[n]["so_luong_muc"] += 1
            continue
        if not nhom: continue
        k = kq[nhom]
        if BULLET.match(t): k["bullet"] += 1
        else:
            k["doan"] += 1
            k["cau"].append(dem_cau(t))
            k["tu_doan"].append(len(t.split()))

print(f"{'Nhóm đề mục':24s} {'mục':>4s} {'đoạn':>6s} {'bullet%':>8s} {'câu/đoạn':>9s} {'từ/đoạn':>8s}")
print("-"*66)
for ten,_ in NHOM:
    k = kq[ten]
    tong = k["doan"] + k["bullet"]
    if tong < 10: 
        print(f"{ten:24s} {k['so_luong_muc']:>4d} {k['doan']:>6d}   (mẫu quá nhỏ)")
        continue
    bl = 100*k["bullet"]/tong
    cd = statistics.mean(k["cau"]) if k["cau"] else 0
    td = statistics.median(k["tu_doan"]) if k["tu_doan"] else 0
    print(f"{ten:24s} {k['so_luong_muc']:>4d} {k['doan']:>6d} {bl:>7.1f}% {cd:>9.2f} {td:>8.0f}")
