#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evidence-gemini.py — trích Evidence Pack từ hồ sơ nặng bằng Gemini, ra thẳng
định dạng khoá của _facts.yaml.

Nguồn: skill `gemini-retriever` (plugin xh-tuvan-v2), viết lại 25/08/2026.

SỬA SO VỚI BẢN GỐC — bản gốc khi thiếu GEMINI_API_KEY sẽ rơi về chế độ "bóc
cục bộ": grep những dòng chứa từ khoá rồi trả về như thể đó là bằng chứng.
Kết quả là một đống dòng rời rạc không có số trang, không có ngữ cảnh, trông
giống dữ liệu thật. Bản này THOÁT VỚI MÃ LỖI 2.

KHI NÀO DÙNG:
  • Hồ sơ khảo sát scan hàng trăm trang, đọc thẳng vào ngữ cảnh thì tràn.
  • Cần quét nhiều file cùng lúc tìm một nhóm chỉ tiêu.
  • File PDF quá lớn, connector Drive trả về bản bị cắt.
KHI NÀO KHÔNG CẦN:
  • File .docx/.pdf vừa phải trên Drive — đọc thẳng bằng connector, xem skill xh-drive.

LƯU Ý VỀ NOTEBOOKLM: NotebookLM không có API công khai, không tự động hoá được.
Muốn dùng thì phải thao tác tay trên giao diện rồi chép kết quả về. Script này
chỉ nói chuyện với Gemini API.

    export GEMINI_API_KEY=...
    python3 evidence-gemini.py \
        --tai-lieu "BC_KhaoSatDiaChat.pdf" \
        --chi-tieu qc-rules.yaml \
        --ra evidence-pack.yaml

Mã thoát: 0 xong · 1 lỗi đầu vào · 2 thiếu khoá API · 3 lỗi gọi API
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

MODEL = os.environ.get("XH_GEMINI_MODEL", "gemini-3.6-flash")

HE_THONG = """\
Bạn là trợ lý trích xuất bằng chứng cho hồ sơ tư vấn thiết kế xây dựng Việt Nam.

NHIỆM VỤ: tìm trong tài liệu được cung cấp những chỉ tiêu được yêu cầu, và CHỈ những
chỉ tiêu đó. Không tóm tắt tài liệu. Không suy diễn.

QUY TẮC BẤT DI BẤT DỊCH:
1. Chỉ trích thông tin XUẤT HIỆN TRỰC TIẾP trong tài liệu. Không tính toán, không nội suy,
   không quy đổi đơn vị, không lấy giá trị "gần đúng" từ hình vẽ.
2. Mỗi chỉ tiêu phải kèm CÂU TRÍCH NGUYÊN VĂN và VỊ TRÍ (số trang, số bảng, số mục).
   Không trích được nguyên văn thì ghi trang_thai: khong_tim_thay, KHÔNG đoán.
3. Một chỉ tiêu xuất hiện nhiều giá trị khác nhau ở nhiều chỗ → liệt kê TẤT CẢ dưới
   ung_vien, đặt trang_thai: conflict. TUYỆT ĐỐI không tự chọn giá trị "hợp lý hơn".
4. Số trong hồ sơ Việt Nam dùng DẤU PHẨY thập phân (+2,80m). Giữ nguyên cách viết của
   tài liệu, không đổi sang dấu chấm.
5. Cao trình luôn phải kèm hệ cao độ (VN2000, Hòn Dấu, Mũi Nai…). Tài liệu không ghi hệ
   cao độ thì ghi rõ "he_cao_do: khong_ghi_trong_tai_lieu".
6. Nếu tài liệu là hồ sơ của DỰ ÁN KHÁC (dự án lân cận, giai đoạn trước), ghi
   data_type: REFERENCE và điền nguon_du_an bằng đúng tên dự án ghi trên tài liệu.

TRẢ VỀ: chỉ một khối YAML hợp lệ, không lời dẫn, không giải thích, theo đúng lược đồ:

ten_khoa_chi_tieu:
  value: <giá trị nguyên văn>
  unit: <đơn vị>
  source: "<tên file>#tr.<số trang>" hoặc "<tên file>#bảng <số>"
  quote: "<câu trích nguyên văn>"
  status: unverified          # luôn là unverified — người duyệt mới đổi được
  data_type: PROJECT | REFERENCE | LEGAL
  nguon_du_an: "<tên dự án>"  # chỉ khi data_type: REFERENCE
"""


def main():
    ap = argparse.ArgumentParser(description="Trích Evidence Pack bằng Gemini")
    ap.add_argument("--tai-lieu", required=True, nargs="+",
                    help="Một hoặc nhiều file tài liệu (pdf, docx, txt, md)")
    ap.add_argument("--chi-tieu", required=True,
                    help="File danh mục chỉ tiêu cần tìm (qc-rules.yaml hoặc .txt liệt kê)")
    ap.add_argument("--ra", help="File YAML kết quả (mặc định in ra màn hình)")
    ap.add_argument("--model", default=MODEL)
    a = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "[DỪNG] Chưa có GEMINI_API_KEY trong môi trường.\n"
            "       Script KHÔNG chạy và KHÔNG trả về kết quả thay thế.\n"
            "       Bản gốc của skill gemini-retriever ở đây sẽ grep vài dòng chứa từ khoá\n"
            "       rồi trả về như thể là bằng chứng — không có số trang, không có ngữ cảnh.\n"
            "       Đó là dữ liệu giả, nguy hiểm hơn không có dữ liệu.\n"
            "       Đặt khoá:  export GEMINI_API_KEY=...",
            file=sys.stderr,
        )
        sys.exit(2)

    dm = Path(a.chi_tieu)
    if not dm.exists():
        print(f"[LỖI] Không thấy danh mục chỉ tiêu: {a.chi_tieu}", file=sys.stderr)
        sys.exit(1)
    danh_muc = dm.read_text(encoding="utf-8")

    files = [Path(p) for p in a.tai_lieu]
    thieu = [str(p) for p in files if not p.exists()]
    if thieu:
        print(f"[LỖI] Không thấy tài liệu: {', '.join(thieu)}", file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("[LỖI] Chưa cài thư viện:  pip install google-genai --break-system-packages",
              file=sys.stderr)
        sys.exit(3)

    client = genai.Client(api_key=api_key)

    # Tải file lên File API — cách duy nhất xử lý được PDF scan hàng trăm trang
    da_tai = []
    for p in files:
        try:
            da_tai.append(client.files.upload(file=str(p)))
            print(f"  đã nạp: {p.name}", file=sys.stderr)
        except Exception as e:
            print(f"[LỖI NẠP FILE] {p.name}: {e}", file=sys.stderr)
            sys.exit(3)

    yeu_cau = (
        "DANH MỤC CHỈ TIÊU CẦN TÌM (chỉ tìm những chỉ tiêu này, không tìm gì khác):\n"
        + danh_muc
        + "\n\nTÊN FILE NGUỒN để ghi vào trường source: "
        + ", ".join(p.name for p in files)
    )

    try:
        resp = client.models.generate_content(
            model=a.model,
            contents=[*da_tai, yeu_cau],
            config=types.GenerateContentConfig(
                system_instruction=HE_THONG,
                temperature=0.0,
            ),
        )
        kq = resp.text
    except Exception as e:
        print(f"[LỖI GỌI API] {e}", file=sys.stderr)
        sys.exit(3)

    # bỏ rào ```yaml nếu mô hình vẫn bọc
    kq = kq.strip()
    if kq.startswith("```"):
        kq = "\n".join(kq.split("\n")[1:])
        if kq.rstrip().endswith("```"):
            kq = kq.rstrip()[:-3]

    dau_de = (
        f"# Evidence Pack — trích bằng {a.model} ngày {date.today().isoformat()}\n"
        f"# Nguồn: {', '.join(p.name for p in files)}\n"
        f"#\n"
        f"# ⚠️ MỌI KHOÁ Ở ĐÂY ĐỀU status: unverified. Đây là bản trích của máy, chưa ai duyệt.\n"
        f"# Người duyệt đọc trường quote là biết ngay có hiểu đúng ngữ cảnh không —\n"
        f"# đọc quote nhanh hơn mở lại PDF gốc rất nhiều.\n"
        f"# Chỉ sau khi người duyệt đổi sang verified thì mới dùng được cho số high-stakes.\n\n"
    )

    # Validate before any output is published. Provider text is not a trusted schema.
    import yaml
    parsed = yaml.safe_load(kq)
    if not isinstance(parsed, dict) or not parsed:
        raise ValueError('Evidence must be a nonempty mapping')
    for key, record in parsed.items():
        if not isinstance(record, dict) or not all(f in record for f in
                ('value', 'unit', 'source', 'quote', 'data_type')):
            raise ValueError(f'Invalid evidence record: {key}')
        if not record['source'] or not record['quote']:
            raise ValueError(f'Missing provenance: {key}')
        record['status'] = 'unverified'
    kq = yaml.safe_dump(parsed, allow_unicode=True, sort_keys=False)
    if a.ra:
        Path(a.ra).parent.mkdir(parents=True, exist_ok=True)
        from xh_core import atomic
        atomic(Path(a.ra), (dau_de + kq + "\n").encode('utf-8'))
        print(f"Đã ghi: {a.ra}")
    else:
        print(dau_de + kq)

    # kiểm YAML hợp lệ
    try:
        import yaml
        yaml.safe_load(kq)
    except Exception as e:
        print(f"[CẢNH BÁO] Kết quả không phải YAML hợp lệ, phải sửa tay: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
