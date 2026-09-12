#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ghi-ket-qua-trinh-sat.py — sổ ghi tất định cho việc "trinh sát tự động" (skill
xh-trinh-sat). Bản thân việc TÌM là do Claude gọi công cụ MCP `web_search_exa`
làm trực tiếp trong hội thoại — script này chỉ lo phần cơ học: tạo thư mục,
ghi từng kết quả vào một danh mục thống nhất, tránh Claude tự bịa định dạng
mỗi lần khác nhau hoặc quên ghi nguồn.

Không tự tìm kiếm gì cả. Không có mạng. Không gọi Exa. Chỉ ghi những gì được
truyền vào qua tham số dòng lệnh.

Cách dùng — bước 1, khởi tạo thư mục (gọi một lần mỗi dự án):
    python3 ghi-ket-qua-trinh-sat.py khoi-tao --thu-muc-du-an 00_input/

Cách dùng — bước 2, ghi một kết quả tìm được (gọi lại cho mỗi kết quả Exa trả về):
    python3 ghi-ket-qua-trinh-sat.py ghi \
        --thu-muc-du-an 00_input/ \
        --tu-khoa "quy hoạch khu neo đậu tránh trú bão Sông Đốc" \
        --tieu-de "Quyết định phê duyệt quy hoạch ..." \
        --url "https://..." \
        --trich-doan "câu/đoạn ngắn liên quan trực tiếp, không tóm tắt cả trang"

Mã thoát: 0 = xong · 1 = lỗi tham số (thiếu --url hoặc --tieu-de khi ghi)
"""

import argparse
import sys
from datetime import date
from pathlib import Path

THU_MUC_CON = "90.TrinhSat-Exa"
TEN_DANH_MUC = "_DanhMuc-TrinhSat.md"

HEADER = (
    "# Danh mục trinh sát tự động (Exa)\n\n"
    "Mỗi dòng là một kết quả tìm được qua công cụ MCP `web_search_exa`. "
    "Đây là hồ sơ THAM KHẢO công khai — không phải số liệu chính thức của dự "
    "án; khi dùng vào bản thảo phải ghi rõ nguồn URL, và số high-stakes vẫn "
    "phải qua `xh-evidence` để vào `_facts.yaml`, không lấy thẳng từ đây.\n\n"
    "| Ngày tìm | Từ khoá | Tiêu đề | Nguồn (URL) | Trích đoạn |\n"
    "|---|---|---|---|---|\n"
)


def duong_dan_danh_muc(thu_muc_du_an: str) -> Path:
    thu_muc = Path(thu_muc_du_an) / THU_MUC_CON
    thu_muc.mkdir(parents=True, exist_ok=True)
    return thu_muc / TEN_DANH_MUC


def lenh_khoi_tao(args):
    danh_muc = duong_dan_danh_muc(args.thu_muc_du_an)
    if danh_muc.exists():
        print(f"Đã có sẵn: {danh_muc}")
        return 0
    danh_muc.write_text(HEADER, encoding="utf-8")
    print(f"Đã tạo: {danh_muc}")
    return 0


def don_o(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def lenh_ghi(args):
    if not args.tieu_de or not args.url:
        print("! Cần đủ --tieu-de và --url", file=sys.stderr)
        return 1
    danh_muc = duong_dan_danh_muc(args.thu_muc_du_an)
    if not danh_muc.exists():
        danh_muc.write_text(HEADER, encoding="utf-8")
    hom_nay = args.ngay or date.today().isoformat()
    dong = (
        f"| {hom_nay} | {don_o(args.tu_khoa)} | {don_o(args.tieu_de)} | "
        f"{don_o(args.url)} | {don_o(args.trich_doan)} |\n"
    )
    with danh_muc.open("a", encoding="utf-8") as f:
        f.write(dong)
    print(f"Đã ghi vào {danh_muc}: {args.tieu_de}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)

    p1 = sub.add_parser("khoi-tao", help="Tạo thư mục + file danh mục rỗng")
    p1.add_argument("--thu-muc-du-an", required=True, help="Thư mục 00_input/ của dự án")
    p1.set_defaults(func=lenh_khoi_tao)

    p2 = sub.add_parser("ghi", help="Ghi thêm một kết quả tìm được")
    p2.add_argument("--thu-muc-du-an", required=True)
    p2.add_argument("--tu-khoa", default="")
    p2.add_argument("--tieu-de", required=True)
    p2.add_argument("--url", required=True)
    p2.add_argument("--trich-doan", default="")
    p2.add_argument("--ngay", default="", help="Mặc định hôm nay (ISO), truyền vào nếu cần cố định")
    p2.set_defaults(func=lenh_ghi)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
