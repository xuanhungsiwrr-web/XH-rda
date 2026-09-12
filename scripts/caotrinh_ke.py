#!/usr/bin/env python3
"""Tính cao trình đỉnh kè / đỉnh đê / đỉnh tường chắn sóng.

Zd = Htk + dH + Hsl + a + b + s   (TCVN 9902:2023, muc 10.2.1.1, CT 1)

Nguon cong thuc: TCVN 9902:2023, TCVN 8421:2010, TCVN 8419:2022,
QCVN 02:2022/BXD, QCVN 04-05:2022. Xem SKILL.md cung thu muc de biet
day du nguyen tac chon can cu, cac bang tra va canh bao.

Cach dung:
    python3 caotrinh_ke.py --mau > input.json
    python3 caotrinh_ke.py input.json -o PL_CaoTrinhDinhKe.md
    python3 caotrinh_ke.py input.json --json
"""
import argparse
import copy
import json
import math
import sys

G = 9.81

A_VC = {"DB": 0.80, "I": 0.60, "II": 0.50, "III": 0.40, "IV": 0.30, "V": 0.20}
TS_GIO = {"DB": (1, 100), "I": (2, 50), "II": (2, 50), "III": (4, 25), "IV": (4, 25), "V": (4, 25)}
TS_MN = {"DB": 0.20, "I": 0.50, "II": 1.00, "III": 1.50, "IV": 2.00}

KM_X = [1, 5, 10, 20, 30, 40, 50, 100]
KM_Y = [.75, .85, .90, .95, .97, .99, 1.00, 1.04]
KW_X = [20, 30, 40, 50]
KW_Y = [2.1e-6, 3.0e-6, 3.9e-6, 4.8e-6]
KL_X = [10, 15, 20, 25, 30, 35, 40]
KL_Y = {
    "A": [1.10, 1.10, 1.09, 1.09, 1.09, 1.09, 1.08],
    "B": [1.30, 1.28, 1.26, 1.25, 1.24, 1.22, 1.21],
    "C": [1.47, 1.44, 1.42, 1.39, 1.38, 1.36, 1.34],
    "MAT_NUOC": [1, 1, 1, 1, 1, 1, 1],
}
KRKP = {
    "ban_btct": (1.00, .90, "Ban BT/BTCT"),
    "da_khoi_001": (.95, .85, "Da/khoi BT r/h1%~0,01"),
    "da_khoi_002": (.90, .80, "Da/khoi BT r/h1%~0,02"),
    "da_khoi_005": (.80, .70, "Da/khoi BT r/h1%~0,05"),
    "da_khoi_010": (.75, .60, "Da/khoi BT r/h1%~0,10"),
    "da_khoi_020": (.70, .50, "Da/khoi BT r/h1%>0,20"),
}
KI = {"0.1": 1.10, "1": 1.00, "2": .96, "5": .91, "10": .86, "30": .76, "50": .68}
BSL = {"ban_lien_khoi": 1.4, "da_lat": 1.0, "da_do": 0.8}
BSL_TEN = {"ban_lien_khoi": "ban lien khoi", "da_lat": "da lat", "da_do": "da do"}

# Thong so tham khao theo loai ghe/tau thong dung - chi de goi y, van phai
# doi chieu ho so phuong tien/luong thuc te truoc khi dung.
TAU_PRESET = {
    "ghe_nho": dict(ka=.030, Auot=2, bmep=5, delta=.70, ds=.5, lu=8, vkc=1.5),
    "tau_5_10": dict(ka=.035, Auot=12, bmep=15, delta=.75, ds=1.0, lu=15, vkc=2.0),
    "tau_100_200": dict(ka=.040, Auot=60, bmep=40, delta=.80, ds=1.6, lu=25, vkc=2.5),
    "salan_500": dict(ka=.045, Auot=400, bmep=100, delta=.80, ds=2.5, lu=40, vkc=2.5),
    "salan_1000": dict(ka=.050, Auot=700, bmep=150, delta=.85, ds=3.2, lu=70, vkc=3.0),
    "tau_khach": dict(ka=.040, Auot=35, bmep=50, delta=.70, ds=1.2, lu=30, vkc=3.0),
}

DEFAULT_INPUT = {
    "dia_danh": "",
    "cap": "III",
    "Htk": 2.33,
    "V50": 31,
    "diahinh": "B",
    "kfl": True,
    "kl_on": True,
    "L": 800,
    "d": 4,
    "alpha": 0,
    "m_mai": 2,
    "giaco": "ban_lien_khoi",
    "tau_on": True,
    "loai_tau": "",
    "ka": 0.045,
    "Auot": 400,
    "bmep": 100,
    "delta": 0.8,
    "ds": 2.5,
    "lu": 40,
    "vkc": 2.5,
    "gio_on": False,
    "Dg": 0.8,
    "h1_nhap": None,
    "krun": 1.8,
    "ketcau": "ban_btct",
    "tsleo": "1",
    "b": 0,
    "sct": 0,
    "snen": 0,
    "zhh": None,
    "mntk": None,
}

SAMPLE_COMMENT = """\
// File mau input.json cho caotrinh_ke.py. Xoa cac dong // truoc khi dung
// neu trinh doc JSON cua ban khong chap nhan comment (script nay tu bo qua).
//
// cap        - cap cong trinh: DB, I, II, III, IV, V (quyet dinh a, tan suat gio/MNTK)
// Htk        - muc nuoc thiet ke (m), lay tu thuy van du an hoac co quan co tham quyen
// V50        - V10m,50 tra Bang 5.1 QCVN 02:2022/BXD theo dia danh (m/s)
// diahinh    - A | B | C | MAT_NUOC (Bang A.3 TCVN 8421) - dung B neu chua ro
// kfl, kl_on - bat/tat he so kfl (A.3.3) va kl (Bang A.3); giu ca hai (mac dinh true)
// L, d, alpha- da song (m), do sau nuoc ung Htk (m), goc gio toi (do, 0 = bat loi nhat)
// m_mai      - he so mai m = ctg(phi), dung m:1
// giaco      - gia co mai: ban_lien_khoi | da_lat | da_do (quyet dinh beta_sl CT 86)
// tau_on     - bat tinh song leo do tau (mac dinh cua TCVN 9902:2023)
// loai_tau   - (tuy chon) ghi chu loai tau da chon preset, khong anh huong tinh toan
// ka, Auot, bmep, delta, ds, lu, vkc - thong so tau/luong (xem muc 4.3 SKILL.md)
// gio_on     - bat kiem tra bo sung song leo do gio (mac dinh TAT - can luan chung rieng)
// Dg, h1_nhap, krun, ketcau, tsleo  - chi dung khi gio_on = true (xem muc 4.4, 5 SKILL.md)
// b          - nuoc bien dang (m), ghi ro kich ban/moc nam trong thuyet minh
// sct, snen  - do lun cong trinh, do lun nen khu vuc (m)
// zhh, mntk  - (tuy chon) cao trinh ke hien huu lan can, MNTK ke - de chon Zc
"""


def interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


def ksp_lookup(Vw, ctg):
    if ctg <= 2:
        ys = [1.0, 1.1, 1.4]
    elif ctg <= 5:
        ys = [0.8, 1.1, 1.5]
    else:
        ys = [0.6, 1.2, 1.6]
    return interp(Vw, [5, 10, 20], ys)


def fm(x, n=3):
    if x is None or not math.isfinite(x):
        return "—"
    s = f"{x:.{n}f}"
    return s.replace(".", ",")


def apply_tau_preset(inp):
    """Neu loai_tau khop mot preset va nguoi dung chua tu doi, dien so lieu goi y."""
    preset = TAU_PRESET.get(inp.get("loai_tau"))
    if not preset:
        return inp
    out = dict(inp)
    for k, v in preset.items():
        out.setdefault(k, v)
        if out.get(k) is None:
            out[k] = v
    return out


def tinh(inp):
    """Loi tinh - port truc tiep tu ham tinh() trong artifact JS 'Cao trinh dinh ke'."""
    inp = apply_tau_preset(inp)
    w = []
    cap = inp.get("cap", "III")
    if cap not in TS_GIO:
        raise ValueError(f"Cap cong trinh khong hop le: {cap!r} (DB, I, II, III, IV, V)")
    pGio, T = TS_GIO[cap]
    Km = interp(T, KM_X, KM_Y)
    V50 = inp.get("V50") or 0
    Vl = Km * V50

    kfl = 1.0
    if inp.get("kfl", True) and Vl:
        kfl = min(1.0, 0.675 + 4.5 / Vl)
    dh = inp.get("diahinh", "B")
    if dh not in KL_Y:
        raise ValueError(f"Dia hinh khong hop le: {dh!r} (A, B, C, MAT_NUOC)")
    kl = interp(Vl, KL_X, KL_Y[dh]) if inp.get("kl_on", True) else 1.0
    Vw = kfl * kl * Vl
    if Vw < 20:
        w.append(("kw", f"Vw = {fm(Vw,2)} m/s < 20 m/s — ngoai dai Bang A.2, kw da kep ve 2,1.10^-6."))
    if Vw > 50:
        w.append(("kw", f"Vw = {fm(Vw,2)} m/s > 50 m/s — ngoai dai Bang A.2, kw kep ve 4,8.10^-6."))

    kw = interp(Vw, KW_X, KW_Y)
    L = inp.get("L") or 0
    d = inp.get("d") or 1
    ca = math.cos(math.radians(inp.get("alpha") or 0))
    dH, it = 0.0, 0
    for it in range(1, 101):
        m = kw * Vw * Vw * L / (G * (d + 0.5 * dH)) * ca
        if abs(m - dH) < 1e-7:
            dH = m
            break
        dH = m
    if dH > 0.10:
        w.append(("dH", f"dH = {fm(dH)} m > 0,10 m — bat thuong voi song. Kiem tra lai L va d; de nham nuoc denh voi chieu cao song."))

    ctg = inp.get("m_mai") or 2
    cand, det = {}, {}

    if inp.get("tau_on", True):
        ka = inp.get("ka") or 0
        A = inp.get("Auot") or 1
        bm = inp.get("bmep") or 1
        de = inp.get("delta") or .8
        dsv = inp.get("ds") or 1
        lu = inp.get("lu") or 1
        vkc = inp.get("vkc")
        if 0 < ka < 1 and (1 - 0.05 * ctg) > 0:
            ng = 6 * math.cos((math.pi + math.acos(1 - ka)) / 3) - 2 * (1 - ka)
            if ng > 0:
                v85 = 0.9 * math.sqrt(ng * G * A / bm)
                v = min(v85, vkc) if vkc else v85
                hsh = 2 * (v * v / G) * math.sqrt(de * dsv / lu)
                bsl = BSL[inp.get("giaco", "ban_lien_khoi")]
                hrsh = bsl * (0.5 * hsh + 0.05 * ctg * v * v / G) / (1 - 0.05 * ctg)
                det["tau"] = dict(v85=v85, vkc=vkc, v=v, hsh=hsh, hrsh=hrsh, bsl=bsl)
                cand["tau"] = hrsh
                if not vkc:
                    w.append(("v tau", f"Toc do lay theo CT(85) = {fm(v85,2)} m/s — day la toc do gioi han (can tren). Nhap toc do khong che cua luong de tranh thien lon."))
            else:
                w.append(("CT85", "Bieu thuc trong can CT(85) <= 0 — kiem tra ka."))
        else:
            w.append(("Tau", "ka phai trong (0;1) va ctg(phi) < 20. Chua tinh duoc song tau."))

    if inp.get("gio_on", False):
        Dg = inp.get("Dg") or 0
        h1in = inp.get("h1_nhap")
        if h1in is not None:
            h1 = h1in
        elif Dg > 0:
            h1 = 0.0208 * (Vw ** 1.25) * (Dg ** (1 / 3))
        else:
            h1 = 0.0
        ketcau = inp.get("ketcau", "ban_btct")
        if ketcau not in KRKP:
            raise ValueError(f"ketcau khong hop le: {ketcau!r}")
        kr, kp, mo = KRKP[ketcau]
        kspv = ksp_lookup(Vw, ctg)
        kr_ = inp.get("krun") or 0
        tsleo = str(inp.get("tsleo", "1"))
        if tsleo not in KI:
            raise ValueError(f"tsleo khong hop le: {tsleo!r} ({', '.join(KI)})")
        ki = KI[tsleo]
        hrun = kr * kp * kspv * kr_ * h1 * ki
        det["gio"] = dict(h1=h1, tuCT7=h1in is None, kr=kr, kp=kp, mo=mo, ksp=kspv, krun=kr_, ki=ki, hrun=hrun, Dg=Dg)
        cand["gio"] = hrun
        if kr_ < 0.1 or kr_ > 2.6:
            w.append(("krun", f"krun = {fm(kr_,2)} ngoai dai Hinh 11 TCVN 8421 (0,1–2,6)."))
        if h1in is None and Dg < 1:
            w.append(("CT(7)", f"Da gio {fm(Dg,2)} km < 1 km: CT(7) TCVN 8419:2022 (dang Dg^1/3) thien lon ro ret. Nen nhap h1% tra tu Hinh A.1/A.2 TCVN 8421."))

    Hsl, quyet = 0.0, "khong xet"
    if cand:
        quyet = max(cand, key=lambda k: cand[k])
        Hsl = cand[quyet]
    else:
        w.append(("Hsl", "Khong tinh thanh phan song leo — phai co luan chung trong thuyet minh."))
    if quyet == "gio":
        w.append(("Hsl", "Hsl dang bi quyet dinh boi song gio. TCVN 9902:2023 dinh nghia Hsl la song leo do tau thuyen — giu ket qua nay thi phai luan chung rieng."))
    if Hsl > 1.0:
        w.append(("Hsl", f"Hsl = {fm(Hsl,2)} m > 1,0 m — bat thuong voi ke bo song noi dia."))

    a = A_VC[cap]
    b = inp.get("b") or 0
    sct = inp.get("sct") or 0
    snen = inp.get("snen") or 0
    s = sct + snen
    if s == 0:
        w.append(("s", "s = 0. TCVN 9902:2023 muc 10.2.1.4 cho phep bo s voi ket cau BT/BTCT/gach da xay, nhung DBSCL co lun nen do khai thac nuoc ngam — can luan chung."))
    if b <= 0:
        w.append(("b", "b = 0. TCVN 9902:2023 yeu cau b >= 0 va phai duoc CDT/co quan co tham quyen chap thuan."))

    Htk = inp.get("Htk") or 0
    Zd = Htk + dH + Hsl + a + b + s
    if Zd - Htk > 1.5:
        w.append(("Tong", f"Phan gia cao (Zd - Htk) = {fm(Zd-Htk,2)} m > 1,5 m — bat thuong voi ke bo song."))

    rb = [("Zd tinh toan", Zd)]
    zhh, mntk = inp.get("zhh"), inp.get("mntk")
    if zhh is not None:
        rb.append(("Cao trinh ke hien huu lan can", zhh))
    if mntk is not None:
        rb.append(("MNTK ke - TCVN 8419 muc 9.3.5.1g", mntk))
    Zyc = max(v for _, v in rb)
    buoc = 0.05
    Zc = math.ceil(Zyc / buoc - 1e-9) * buoc

    return dict(cap=cap, pGio=pGio, T=T, Km=Km, V50=V50, Vl=Vl, kfl=kfl, kl=kl, dh=dh, Vw=Vw,
                kw=kw, L=L, d=d, ca=ca, dH=dH, it=it, ctg=ctg, cand=cand, det=det, Hsl=Hsl,
                quyet=quyet, a=a, b=b, sct=sct, snen=snen, s=s, Htk=Htk, Zd=Zd, rb=rb, Zyc=Zyc,
                buoc=buoc, Zc=Zc, w=w, dia_danh=(inp.get("dia_danh") or "").strip())


# ---------------------------------------------------------------- xuat ----

def yaml_block(r):
    dd = f'\n  dia_danh: "{r["dia_danh"]}"' if r["dia_danh"] else ""
    return (
        "cao_trinh_dinh_ke:" + dd + "\n"
        f'  cap_cong_trinh: {r["cap"]}\n'
        f'  Htk: {r["Htk"]:.3f}\n'
        f'  dH_nuoc_denh: {r["dH"]:.4f}\n'
        f'  Hsl_song_leo: {r["Hsl"]:.3f}\n'
        f'  a_vuot_cao: {r["a"]:.2f}\n'
        f'  b_nuoc_bien_dang: {r["b"]:.3f}\n'
        f'  s_lun: {r["s"]:.3f}\n'
        f'  Zd_tinh_toan: {r["Zd"]:.3f}\n'
        f'  Zc_thiet_ke: {r["Zc"]:.2f}\n'
        f'  Vw_gio_tinh_toan: {r["Vw"]:.2f}\n'
        f'  quyet_dinh_Hsl: {r["quyet"]}\n'
        '  nguon: "TCVN 9902:2023 (10.2.1.1); TCVN 8421:2010 (A.1, 84-86); QCVN 02:2022/BXD (B.5.1, B.5.3)"\n'
        "  trang_thai: cho_duyet"
    )


def chuoi_tinh_md(r):
    rows = []
    rows.append(("Km,T", fm(r["Km"], 3), f'QCVN 02:2022 Bang 5.3 — T = {r["T"]} nam'))
    rows.append(("Vl", f'{fm(r["Km"],3)} x {fm(r["V50"],1)} = {fm(r["Vl"],2)} m/s', "gio 10 phut, cao do 10 m"))
    rows.append(("kfl", fm(r["kfl"], 3), "0,675 + 4,5/Vl <= 1,0 — TCVN 8421 A.3.3"))
    rows.append(("kl", fm(r["kl"], 3), f'Bang A.3 — dia hinh {r["dh"]}'))
    rows.append(("Vw", f'{fm(r["kfl"],3)} x {fm(r["kl"],3)} x {fm(r["Vl"],2)} = {fm(r["Vw"],2)} m/s', ""))
    rows.append(("kw", f'{r["kw"]:.3e}', "Bang A.2, noi suy theo Vw"))
    rows.append(("dH", f'CT(A.1), hoi tu sau {r["it"]} vong lap = {fm(r["dH"],4)} m', ""))
    if "tau" in r["det"]:
        t = r["det"]["tau"]
        vkc_txt = f' -> khong che {fm(t["vkc"],2)}' if t["vkc"] else ""
        rows.append(("v tau", f'CT(85) = {fm(t["v85"],2)}{vkc_txt} -> {fm(t["v"],2)} m/s', ""))
        rows.append(("hsh", f'{fm(t["hsh"],3)} m', "CT (84)"))
        rows.append(("hrsh", f'{fm(t["hrsh"],3)} m (beta_sl = {fm(t["bsl"],1)})', "CT (86)"))
    if "gio" in r["det"]:
        x = r["det"]["gio"]
        nguon = f'TCVN 8419:2022 CT(7), Dg = {fm(x["Dg"],2)} km' if x["tuCT7"] else "nguoi dung nhap tu Hinh A.1/A.2"
        rows.append(("h1%", f'{fm(x["h1"],3)} m', nguon))
        rows.append(("hrun", f'{fm(x["hrun"],3)} m', f'CT (25), mai {x["mo"]}'))
    cand_txt = " . ".join(f"{k} {fm(v,3)}" for k, v in r["cand"].items()) or "—"
    rows.append(("Hsl", f'{fm(r["Hsl"],3)} m', f'lon nhat trong: {cand_txt} -> quyet dinh boi {r["quyet"]}'))
    rows.append(("Zd", f'{fm(r["Htk"],3)} + {fm(r["dH"],3)} + {fm(r["Hsl"],3)} + {fm(r["a"],3)} + {fm(r["b"],3)} + {fm(r["s"],3)} = {fm(r["Zd"],3)} m', ""))
    zc_src = "; ".join(fm(v, 3) for _, v in r["rb"])
    rows.append(("Zc", f'max({zc_src}) lam tron len {fm(r["buoc"],2)} = +{fm(r["Zc"],2)} m', ""))

    lines = ["| Buoc | Gia tri | Nguon |", "|---|---|---|"]
    for k, v, s in rows:
        lines.append(f"| {k} | {v} | {s} |")
    return "\n".join(lines)


def bang_tong_hop_md(r):
    rows = [
        ("Htk — muc nuoc thiet ke", r["Htk"], "Tinh toan thuy van du an / co quan co tham quyen"),
        ("dH — nuoc denh do gio", r["dH"], "TCVN 8421:2010 CT (A.1)"),
        ("Hsl — song leo", r["Hsl"], f'TCVN 8421:2010 — quyet dinh boi {r["quyet"]}'),
        ("a — do vuot cao an toan", r["a"], f'TCVN 9902:2023 Bang 6, cap {r["cap"]}'),
        ("b — nuoc bien dang", r["b"], "Kich ban BDKH–NBD Bo TN&MT ban 2020"),
        ("s — tong do lun", r["s"], f'cong trinh {fm(r["sct"],3)} + nen khu vuc {fm(r["snen"],3)}'),
    ]
    lines = ["| Thanh phan | Gia tri (m) | Nguon |", "|---|---|---|"]
    for n, v, s in rows:
        lines.append(f"| {n} | {fm(v,3)} | {s} |")
    lines.append(f'| **Zd — cao trinh tinh toan** | **{fm(r["Zd"],3)}** | TCVN 9902:2023 CT (1) |')
    return "\n".join(lines)


def canh_bao_md(r):
    if not r["w"]:
        return "- Khong co canh bao. Van phai kiem tra lai nguon cua Htk, b va s truoc khi trinh."
    return "\n".join(f"- **[{t}]** {m}" for t, m in r["w"])


def thuyet_minh_md(r):
    dd = f" tai {r['dia_danh']}" if r["dia_danh"] else ""
    doan_tau = ""
    if "tau" in r["det"]:
        t = r["det"]["tau"]
        vkc_txt = f', khong che theo quy dinh toc do luong con v = {fm(t["v"],2)} m/s' if t["vkc"] else ""
        doan_tau = (
            f"\n\nChieu cao song leo do tau Hsl xac dinh voi mai ke m = {fm(r['ctg'],2)} "
            f"(ctg(phi) = {fm(r['ctg'],3)}), gia co {BSL_TEN.get(r['det'].get('giaco',''), '')}:\n\n"
            f"v = 0,9.can{{[6.cos((pi+arccos(1-ka))/3) - 2(1-ka)].g.A/b}} = {fm(t['v85'],2)} m/s (CT 85){vkc_txt}.\n\n"
            f"hsh = 2.(v^2/g).can(delta.ds/lu) = {fm(t['hsh'],3)} m (CT 84).\n\n"
            f"hrsh = beta_sl.[0,5.hsh + 0,05.ctg(phi).v^2/g] / (1 - 0,05.ctg(phi)) = {fm(t['hrsh'],3)} m (CT 86)."
        )
    doan_gio = ""
    if "gio" in r["det"]:
        x = r["det"]["gio"]
        nguon = f"theo CT (7) TCVN 8419:2022 voi da gio Dg = {fm(x['Dg'],2)} km" if x["tuCT7"] else "nhap truc tiep theo Hinh A.1/A.2 TCVN 8421:2010"
        doan_gio = (
            f"\n\nKiem tra bo sung song leo do gio (can luan chung rieng vi TCVN 9902:2023 dinh nghia "
            f"Hsl la song leo do tau thuyen): chieu cao song h1% = {fm(x['h1'],3)} m {nguon}; "
            f"hrun1% = kr.kp.ksp.krun.h1%.ki = {fm(x['hrun'],3)} m (CT 25, ket cau mai {x['mo']})."
        )
    return (
        f"Ke{dd} duoc xac dinh cao trinh dinh theo cong thuc tai muc 10.2.1.1 TCVN 9902:2023 "
        f'"Cong trinh thuy loi – Yeu cau thiet ke de song", ap dung tuong tu cho ke theo nguyen tac '
        f'muc 9.3.5.2 TCVN 8419:2022 "Cong trinh bao ve de, bo song – Yeu cau thiet ke":\n\n'
        f"Zd = Htk + dH + Hsl + a + b + s\n\n"
        f"Trong do: muc nuoc thiet ke Htk = +{fm(r['Htk'],2)} m; chieu cao nuoc denh do gio "
        f"dH = {fm(r['dH'],3)} m ung voi van toc gio tinh toan Vw = {fm(r['Vw'],2)} m/s (Phu luc A "
        f"TCVN 8421:2010, CT A.1; so lieu gio QCVN 02:2022/BXD Bang 5.1, 5.3); chieu cao song leo "
        f"Hsl = {fm(r['Hsl'],3)} m (quyet dinh boi song do {r['quyet']}); do vuot cao an toan "
        f"a = {fm(r['a'],2)} m (TCVN 9902:2023 Bang 6, cong trinh cap {r['cap']}); nuoc bien dang "
        f"b = {fm(r['b'],3)} m (kich ban BDKH–NBD Bo TN&MT, ban cap nhat 2020); tong do lun "
        f"s = {fm(r['s'],3)} m."
        f"{doan_tau}{doan_gio}\n\n"
        f"Thay so: Zd = {fm(r['Htk'],3)} + {fm(r['dH'],3)} + {fm(r['Hsl'],3)} + {fm(r['a'],3)} + "
        f"{fm(r['b'],3)} + {fm(r['s'],3)} = {fm(r['Zd'],3)} m.\n\n"
        f"Lua chon cao trinh dinh ke thiet ke +{fm(r['Zc'],2)} m (lam tron len boi so "
        f"{fm(r['buoc'],2)} m, can ghi ro ly do phu hop dia hinh / dong bo ke hien huu / du phong lun)."
    )


def markdown_report(r):
    dd_h = f" — {r['dia_danh']}" if r["dia_danh"] else ""
    parts = [
        f"# Phu luc tinh toan cao trinh dinh ke{dd_h}",
        "",
        "Zd = Htk + dH + Hsl + a + b + s (TCVN 9902:2023, muc 10.2.1.1, CT 1)",
        "",
        "## Chuoi tinh va nguon tung thong so",
        "",
        chuoi_tinh_md(r),
        "",
        "## Bang tong hop",
        "",
        bang_tong_hop_md(r),
        "",
        "## Canh bao — doc het truoc khi dung ket qua",
        "",
        canh_bao_md(r),
        "",
        "## Thuyet minh",
        "",
        thuyet_minh_md(r),
        "",
        "## Khoi YAML cho _facts.yaml",
        "",
        "```yaml",
        yaml_block(r),
        "```",
        "",
    ]
    return "\n".join(parts)


def json_result(r):
    out = copy.deepcopy(r)
    out["det"] = {k: dict(v) for k, v in out["det"].items()}
    out["cand"] = dict(out["cand"])
    out["rb"] = [list(x) for x in out["rb"]]
    out["w"] = [list(x) for x in out["w"]]
    return out


# ----------------------------------------------------------------- CLI ----

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?", help="File input.json (bo qua neu dung --mau)")
    ap.add_argument("--mau", action="store_true", help="In file input.json mau ra stdout roi thoat")
    ap.add_argument("-o", "--out", help="Ghi phu luc Markdown ra file nay thay vi in ra stdout")
    ap.add_argument("--json", action="store_true", help="In ket qua dang JSON (may doc) thay vi Markdown")
    args = ap.parse_args()

    if args.mau:
        sample = copy.deepcopy(DEFAULT_INPUT)
        print(SAMPLE_COMMENT)
        print(json.dumps(sample, ensure_ascii=False, indent=2))
        return 0

    if not args.input:
        ap.error("can duong dan input.json (hoac dung --mau de sinh file mau)")

    with open(args.input, "r", encoding="utf-8-sig") as f:
        raw = f.read()
    # Cho phep file input giu lai cac dong // comment sao chep tu --mau.
    cleaned = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("//"))
    inp = dict(DEFAULT_INPUT)
    inp.update(json.loads(cleaned))

    try:
        r = tinh(inp)
    except (ValueError, ZeroDivisionError, KeyError) as exc:
        print(f"Loi du lieu dau vao: {exc}", file=sys.stderr)
        return 2

    if args.json:
        text = json.dumps(json_result(r), ensure_ascii=False, indent=2)
    else:
        text = markdown_report(r)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Da ghi: {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


