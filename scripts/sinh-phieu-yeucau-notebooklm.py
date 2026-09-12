#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sinh-phieu-yeucau-notebooklm.py — sinh "Phiếu yêu cầu trích xuất" cho NotebookLM.

Công cụ tương thích bảng extraction cũ, chạy cục bộ và không gọi API.
EXTRACTOR do Global Control resolve; tên file giữ để tương thích các hồ sơ cũ.
Đầu ra nhập qua doc-ket-qua-notebooklm.py vẫn là candidate cần xác minh.

KHÔNG tự bịa câu hỏi hay giá trị — script chỉ liệt kê CẦN GÌ, không đoán TRẢ LỜI.

Cách dùng:
    python3 sinh-phieu-yeucau-notebooklm.py \
        --facts _facts.yaml \
        --chi-tieu ${CLAUDE_PLUGIN_ROOT}/scripts/qc-rules.yaml \
        --ra _YeuCau-TrichXuat-NotebookLM.md

Mã thoát: 0 = xong · 1 = lỗi đầu vào (thiếu file, YAML hỏng)
"""

import argparse
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("! Cần PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

TRANG_THAI_CAN_TRICH = {
    "thieu": "chưa có trong _facts.yaml",
    "unverified": "đã có nhưng chưa duyệt (status: unverified)",
    "conflict": "đang mâu thuẫn giữa nhiều nguồn (status: conflict)",
    "missing": "khai data_type: MISSING — đang chờ khảo sát",
}


def nap_yaml(path: str, bat_buoc: bool = True):
    p = Path(path)
    if not p.exists():
        if bat_buoc:
            print(f"! Không tìm thấy file: {path}", file=sys.stderr)
            sys.exit(1)
        return {}
    try:
        with p.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"! YAML hỏng ở {path}: {e}", file=sys.stderr)
        sys.exit(1)


def gom_danh_sach_can_trich(facts: dict, chi_tieu: dict) -> list[dict]:
    """Trả về danh sách khoá cần trích, mỗi phần tử có khoá/tên/đơn_vị/tình_trạng/nhãn."""
    ket_qua = []
    da_xet = set()

    # 1. Khoá đã có trong _facts.yaml nhưng chưa xong (unverified/conflict/MISSING)
    for key, f in (facts or {}).items():
        if not isinstance(f, dict):
            continue
        da_xet.add(key)
        status = str(f.get("status", "")).lower()
        dt = str(f.get("data_type", "")).upper()
        tinh_trang = None
        if dt == "MISSING":
            tinh_trang = "missing"
        elif status == "conflict":
            tinh_trang = "conflict"
        elif status == "unverified":
            tinh_trang = "unverified"
        if tinh_trang:
            ct = (chi_tieu or {}).get(key, {})
            ket_qua.append({
                "khoa": key,
                "ten": ct.get("ten", key),
                "don_vi": ct.get("don_vi", f.get("unit", "")),
                "nhan": ct.get("nhan", []),
                "tinh_trang": tinh_trang,
            })

    # 2. Khoá có trong danh mục chỉ tiêu nhưng chưa hề xuất hiện trong _facts.yaml
    for key, ct in (chi_tieu or {}).items():
        if key in da_xet:
            continue
        ket_qua.append({
            "khoa": key,
            "ten": ct.get("ten", key),
            "don_vi": ct.get("don_vi", ""),
            "nhan": ct.get("nhan", []),
            "tinh_trang": "thieu",
        })

    return ket_qua


def sinh_markdown(danh_sach: list[dict], ten_du_an: str) -> str:
    hom_nay = date.today().isoformat()
    dong = []
    dong.append(f"# Phiếu yêu cầu trích xuất — đưa cho NotebookLM")
    dong.append("")
    dong.append(f"**Dự án:** {ten_du_an}  ·  **Sinh ngày:** {hom_nay}")
    dong.append("")
    dong.append(
        "Đưa file này (hoặc nội dung mục 1 dưới đây) cho NotebookLM cùng với "
        "hồ sơ khảo sát đã tải lên notebook. Hỏi lần lượt từng dòng — mỗi dòng "
        "một câu hỏi gợi ý. Dán câu trả lời của NotebookLM vào đúng bảng mẫu "
        "ở mục 2, rồi đưa file đã điền lại cho MASTER — dùng "
        "`doc-ket-qua-notebooklm.py` để bóc vào `_facts.yaml`."
    )
    dong.append("")
    dong.append("**Không tự thêm số liệu vào bảng mẫu nếu NotebookLM không trả lời được** "
                 "— để trống ô đó, đừng đoán.")
    dong.append("")
    dong.append("---")
    dong.append("")
    dong.append("## 1. Danh sách cần hỏi")
    dong.append("")
    if not danh_sach:
        dong.append("*(Không có khoá nào cần trích — mọi chỉ tiêu trong danh mục "
                     "đã có trong _facts.yaml và ở trạng thái verified.)*")
    for i, d in enumerate(danh_sach, 1):
        nhan_vi_du = d["nhan"][0] if d["nhan"] else d["ten"]
        dong.append(f"### {i}. `{d['khoa']}` — {d['ten']}")
        dong.append(f"- Đơn vị: **{d['don_vi'] or '(chưa rõ, hỏi luôn NotebookLM)'}**")
        dong.append(f"- Tình trạng hiện tại: {TRANG_THAI_CAN_TRICH.get(d['tinh_trang'], d['tinh_trang'])}")
        dong.append(
            f"- Câu hỏi gợi ý: *\"Hồ sơ có nêu {nhan_vi_du} không? Giá trị là bao "
            f"nhiêu, đơn vị gì, nằm ở trang/mục nào, trích nguyên văn câu chứa số đó.\"*"
        )
        dong.append("")

    dong.append("---")
    dong.append("")
    dong.append("## 2. Bảng mẫu — điền câu trả lời của NotebookLM vào đây")
    dong.append("")
    dong.append(
        "Mỗi dòng một khoá. Cột `nguon` ghi rõ **tên file + số trang/mục** (đừng "
        "chỉ ghi tên hồ sơ chung chung). Cột `quote` là câu trích NGUYÊN VĂN "
        "NotebookLM đưa ra, không diễn giải lại. Nếu số này là mượn của dự án "
        "khác, điền thêm cột `du_an_goc`. Ô nào NotebookLM không trả lời được thì "
        "để trống, đừng xoá dòng."
    )
    dong.append("")
    dong.append(
        "Cột cuối `du_an_goc` chỉ điền khi số này thực ra là số của MỘT DỰ ÁN "
        "KHÁC được dùng tạm (mượn) — để trống nếu số đúng là của chính dự án này."
    )
    dong.append("")
    dong.append("| khoa | value | unit | source | quote | du_an_goc |")
    dong.append("|---|---|---|---|---|---|")
    for d in danh_sach:
        dong.append(f"| {d['khoa']} |  | {d['don_vi']} |  |  |  |")
    dong.append("")
    return "\n".join(dong)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--facts", required=True, help="_facts.yaml của dự án")
    ap.add_argument("--chi-tieu", required=True, help="qc-rules.yaml (danh mục chỉ tiêu)")
    ap.add_argument("--ten-du-an", default="", help="Tên dự án, in vào đầu phiếu")
    ap.add_argument("--ra", required=True, help="File .md xuất ra")
    args = ap.parse_args()

    facts = nap_yaml(args.facts, bat_buoc=False)
    rules = nap_yaml(args.chi_tieu, bat_buoc=True)
    chi_tieu = rules.get("chi_tieu", {}) if isinstance(rules, dict) else {}

    danh_sach = gom_danh_sach_can_trich(facts, chi_tieu)
    ten_du_an = args.ten_du_an or Path(args.facts).resolve().parent.name

    noi_dung = sinh_markdown(danh_sach, ten_du_an)
    Path(args.ra).write_text(noi_dung, encoding="utf-8")

    print(f"{args.ra}  ({len(danh_sach)} khoá cần trích)")
    for d in danh_sach:
        print(f"  - {d['khoa']:35s} [{d['tinh_trang']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
