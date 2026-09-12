#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-ket-qua-notebooklm.py — bóc bảng kết quả NotebookLM (đã người dùng dán vào
phiếu do sinh-phieu-yeucau-notebooklm.py sinh ra) ngược trở lại vào _facts.yaml.

Đây là nửa sau của quy trình thủ công thay Gemini API:
    xh-evidence sinh phiếu → người dùng hỏi NotebookLM (ngoài Claude) → dán kết
    quả vào bảng mẫu → script này đọc file đã điền, ghi vào _facts.yaml.

QUY TẮC — khớp đúng "Không làm" của skill xh-evidence:
  * status luôn ghi "unverified" — KHÔNG BAO GIỜ tự đặt "verified" thay người
    dùng, kể cả khi NotebookLM trả lời rất chắc chắn.
  * Không tính toán / quy đổi đơn vị — chép nguyên giá trị NotebookLM đưa ra.
  * Dòng thiếu value hoặc thiếu quote thì BỎ QUA, không ghi vào _facts.yaml
    (một khoá không có câu trích thì người duyệt phải mở lại hồ sơ gốc, và họ
    sẽ không mở — xem "Không làm" trong SKILL.md).
  * Khoá đã tồn tại trong _facts.yaml (kể cả đã verified) thì KHÔNG bị ghi đè
    tự động — báo ra danh sách riêng, để người dùng tự quyết (tránh việc trích
    lần hai vô tình hạ một số đã duyệt xuống unverified).

Cách dùng:
    python3 doc-ket-qua-notebooklm.py \
        --ket-qua _YeuCau-TrichXuat-NotebookLM.md \
        --facts _facts.yaml \
        --ra _facts.yaml

Mã thoát: 0 = xong (có thể 0 dòng hợp lệ) · 1 = lỗi đầu vào
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("! Cần PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def doc_bang_markdown(path: str) -> list[dict]:
    """Đọc bảng '| khoa | value | unit | source | quote | du_an_goc |' từ file .md."""
    text = Path(path).read_text(encoding="utf-8")
    dong_bang = [l for l in text.splitlines() if l.strip().startswith("|")]
    if not dong_bang:
        return []

    hang = []
    header = None
    for line in dong_bang:
        cot = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cot]
            continue
        if all(re.fullmatch(r":?-+:?", c) for c in cot):
            continue  # dòng gạch ngang phân cách header
        if len(cot) != len(header):
            continue
        hang.append(dict(zip(header, cot)))
    return hang


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ket-qua", required=True, help="File .md đã dán kết quả NotebookLM vào bảng mẫu")
    ap.add_argument("--facts", required=True, help="_facts.yaml hiện có của dự án")
    ap.add_argument("--ra", required=True, help="Ghi _facts.yaml đã bổ sung ra đây (có thể trùng --facts)")
    args = ap.parse_args()

    if not Path(args.ket_qua).exists():
        print(f"! Không tìm thấy file kết quả: {args.ket_qua}", file=sys.stderr)
        sys.exit(1)

    facts_path = Path(args.facts)
    facts = {}
    if facts_path.exists():
        with facts_path.open(encoding="utf-8") as f:
            facts = yaml.safe_load(f) or {}
    elif not facts_path.exists() and str(args.ra) == str(args.facts):
        pass  # dự án mới, _facts.yaml chưa có — tạo mới

    hang = doc_bang_markdown(args.ket_qua)

    da_ghi, bo_qua_trong, bi_chan_da_co = [], [], []

    for h in hang:
        khoa = h.get("khoa", "").strip()
        value = h.get("value", "").strip()
        quote = h.get("quote", "").strip()
        if not khoa:
            continue
        if not value or not quote:
            bo_qua_trong.append(khoa)
            continue

        khoa_hien_co = facts.get(khoa)
        if khoa in facts:
            bi_chan_da_co.append(khoa)
            continue

        muc = {
            "value": value,
            "unit": h.get("unit", "").strip(),
            "source": h.get("source", "").strip(),
            "quote": quote,
            "status": "unverified",
            "data_type": "PROJECT",
        }
        du_an_goc = h.get("du_an_goc", "").strip()
        if du_an_goc:
            muc["data_type"] = "REFERENCE"
            muc["nguon_du_an"] = du_an_goc

        facts[khoa] = muc
        da_ghi.append(khoa)

    if da_ghi:
        if facts_path.exists():
            backup = facts_path.with_suffix(facts_path.suffix + f".bak-{datetime.now():%Y%m%d-%H%M%S}")
            shutil.copy2(facts_path, backup)
            print(f"Đã sao lưu bản cũ: {backup}")
        from xh_core import atomic
        atomic(Path(args.ra), yaml.safe_dump(facts, allow_unicode=True, sort_keys=True,
                                            default_flow_style=False).encode('utf-8'))

    print(f"Ghi vào {args.ra}: {len(da_ghi)} khoá mới (status: unverified)")
    for k in da_ghi:
        print(f"  + {k}")
    if bo_qua_trong:
        print(f"Bỏ qua (thiếu value hoặc quote): {len(bo_qua_trong)}")
        for k in bo_qua_trong:
            print(f"  - {k}")
    if bi_chan_da_co:
        print(f"Không ghi đè (khoá đã tồn tại, cần đối chiếu ứng viên): {len(bi_chan_da_co)}")
        for k in bi_chan_da_co:
            print(f"  ! {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
