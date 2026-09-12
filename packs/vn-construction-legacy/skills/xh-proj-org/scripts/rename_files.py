#!/usr/bin/env python3
"""
rename_files.py — Đổi tên file theo quy ước dự án tư vấn thiết kế.
                  Có tích hợp dọn dẹp file rác (.bak, file tạm).

Áp dụng hai quy ước đặt tên:
  A) Văn thư / công văn (trong 60.VanThu/ và các folder pháp lý):
       YYMMDD_TenVanBan.ext
  B) File làm việc nội bộ (trong 41.ThucHien/ThuyetMinh, TinhToan):
       Tap[N].[x]_TenFile_Rx-STATUS-YYYYMMDD.ext
       → Script CHỈ đặt tiền tố YYMMDD cho file này; việc gán số Tập
         cần làm thủ công vì đòi hỏi phán đoán nội dung.

Sử dụng:
  python3 rename_files.py --root /path/to/project --preview        # xem trước đổi tên
  python3 rename_files.py --root /path/to/project                  # thực thi đổi tên
  python3 rename_files.py --root /path/to/project --cleanup        # xóa file rác
  python3 rename_files.py --root /path/to/project --cleanup --preview  # xem trước xóa

Bỏ qua khi đổi tên:
  - File .dwg, .dxf, .bak, .dwl (CAD)
  - File trong thư mục: DuToan/, BanVe_CAD/, 42.PhatHanh/, _NopThau/
  - File dự toán Excel (du toan, BGVL, Dien giai KL, TMDT)
  - File đã đúng định dạng YYMMDD_ ở đầu tên
  - File đã đúng định dạng Tap[N].[x]_ ở đầu tên

File rác bị xóa khi --cleanup:
  - .bak, .tmp, .temp (CAD backup và file tạm)
  - ~$*.docx, ~$*.xlsx, ~$*.pptx (Office lock files)
  - Thumbs.db, .DS_Store (hệ thống)
  - *.dwl, *.dwl2 (AutoCAD lock files)
  - desktop.ini
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Thư mục bỏ qua (không xử lý file bên trong)
SKIP_PATHS = [
    "DuToan",
    "BanVe_CAD",
    "42.PhatHanh",
    "44_PhatHanh",      # tên cũ — vẫn bỏ qua để an toàn
    "_NopThau",
]

# Extension bỏ qua khi đổi tên
SKIP_EXTS = {".dwg", ".dxf", ".bak", ".dwl", ".dwf"}

# ── Cấu hình dọn dẹp file rác (--cleanup) ──────────────────────────────────

# Extension của file rác cần xóa
JUNK_EXTS = {
    ".bak",    # AutoCAD / Office backup
    ".tmp",    # file tạm Windows
    ".temp",   # file tạm
    ".dwl",    # AutoCAD lock
    ".dwl2",   # AutoCAD lock
    ".lnk",    # shortcut Windows (nếu lẫn vào project)
}

# Tên file rác cần xóa (so sánh không phân biệt hoa/thường)
JUNK_NAMES = {
    "thumbs.db",
    ".ds_store",
    "desktop.ini",
    "ehthumbs.db",
}

# Tiền tố tên file rác (Office temp files khi đang mở)
JUNK_PREFIXES = ("~$",)

# Pattern tên file rác bổ sung
JUNK_PATTERNS = [
    re.compile(r"^~\$"),                        # Office lock: ~$file.docx
    re.compile(r"\.tmp\d*$", re.IGNORECASE),    # .tmp, .tmp1, .tmp2 ...
]


def is_junk(path: Path) -> bool:
    """Kiểm tra xem file có phải file rác không."""
    name_lower = path.name.lower()
    ext_lower = path.suffix.lower()

    if name_lower in JUNK_NAMES:
        return True
    if ext_lower in JUNK_EXTS:
        return True
    if any(name_lower.startswith(p) for p in JUNK_PREFIXES):
        return True
    if any(pat.search(path.name) for pat in JUNK_PATTERNS):
        return True
    return False

# Extension xử lý
TARGET_EXTS = {".doc", ".docx", ".pdf", ".xls", ".xlsx", ".pptx", ".ppt", ".txt"}

# Pattern tên file dự toán (Excel) — không đổi tên
DUTOAN_PATTERNS = [
    re.compile(r"du[\s_]?toan", re.IGNORECASE),
    re.compile(r"bgvl", re.IGNORECASE),
    re.compile(r"dien[\s_]?giai[\s_]?kl", re.IGNORECASE),
    re.compile(r"tmdt", re.IGNORECASE),
]


def should_skip(path: Path) -> bool:
    """Kiểm tra xem file có nên bỏ qua khi đổi tên không."""
    path_str = str(path)

    # File rác → bỏ qua (chỉ xử lý bởi --cleanup)
    if is_junk(path):
        return True

    # Kiểm tra đường dẫn chứa thư mục bỏ qua
    for skip in SKIP_PATHS:
        if skip in path_str:
            return True

    # Kiểm tra extension
    if path.suffix.lower() in SKIP_EXTS:
        return True

    # Kiểm tra tên file dự toán (Excel)
    if path.suffix.lower() in {".xls", ".xlsx"}:
        for pat in DUTOAN_PATTERNS:
            if pat.search(path.stem):
                return True

    return False


def extract_date(stem: str):
    """
    Trích ngày tháng từ tên file.
    Trả về (YYMMDD_str, stem_da_xoa_ngay) hoặc (None, stem).
    """
    # 1. YYYY.MM.DD (4 chữ số năm)
    m = re.search(r"20(\d{2})\.(\d{2})\.(\d{2})\.?", stem)
    if m:
        yy, mm, dd = m.group(1), m.group(2), m.group(3)
        cleaned = stem[: m.start()] + stem[m.end() :]
        return f"{yy}{mm}{dd}", cleaned.strip("_. ")

    # 2. YYYY-MM-DD
    m = re.search(r"20(\d{2})-(\d{2})-(\d{2})", stem)
    if m:
        yy, mm, dd = m.group(1), m.group(2), m.group(3)
        cleaned = stem[: m.start()] + stem[m.end() :]
        return f"{yy}{mm}{dd}", cleaned.strip("_. ")

    # 3. _202510021441 (Google export timestamp)
    m = re.search(r"_20(\d{2})(\d{2})(\d{2})\d{4}$", stem)
    if m:
        yy, mm, dd = m.group(1), m.group(2), m.group(3)
        cleaned = stem[: m.start()]
        return f"{yy}{mm}{dd}", cleaned.strip("_. ")

    # 4. YY.MM.DD (2 chữ số năm, trong khoảng 23-30 = 2023-2030)
    m = re.search(r"[_\.]?(\d{2})\.(\d{2})\.(\d{2})(?=[_\.\s\-]|$)", stem)
    if m:
        yy, mm, dd = m.group(1), m.group(2), m.group(3)
        if 23 <= int(yy) <= 30:
            cleaned = stem[: m.start()] + stem[m.end() :]
            return f"{yy}{mm}{dd}", cleaned.strip("_. ")

    # 5. YYMMDD ở cuối tên: _251217
    m = re.search(r"[_](\d{6})$", stem)
    if m:
        date_str = m.group(1)
        if 20 <= int(date_str[:2]) <= 30:
            cleaned = stem[: m.start()]
            return date_str, cleaned.strip("_. ")

    # 6. DD-M-YYYY trong tên (ví dụ: NGAY 14-7-2023)
    m = re.search(r"(\d{1,2})-(\d{1,2})-20(\d{2})", stem)
    if m:
        dd = m.group(1).zfill(2)
        mm = m.group(2).zfill(2)
        yy = m.group(3)
        cleaned = stem[: m.start()] + stem[m.end() :]
        return f"{yy}{mm}{dd}", cleaned.strip("_. ")

    # 7. Ngày dạng NGAY_DD_MM_YYYY hoặc NGAY DD-MM-YYYY
    m = re.search(r"NGAY[\s_]?(\d{1,2})[\s_\-/](\d{1,2})[\s_\-/]20(\d{2})", stem, re.IGNORECASE)
    if m:
        dd = m.group(1).zfill(2)
        mm = m.group(2).zfill(2)
        yy = m.group(3)
        cleaned = stem[: m.start()] + stem[m.end() :]
        return f"{yy}{mm}{dd}", cleaned.strip("_. ")

    return None, stem


def clean_stem(stem: str) -> str:
    """Làm sạch tên file: xóa .signed, (1), khoảng trắng thừa."""
    stem = re.sub(r"\.signed", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"[_\s]*_0001\s*$", "", stem)
    stem = re.sub(r"[_\s]*\(\d+\)\s*$", "", stem)
    stem = re.sub(r"\s+", "_", stem)
    stem = re.sub(r"_+", "_", stem)
    return stem.strip("_. -")


def compute_new_name(path: Path) -> str:
    """Tính tên mới cho file (YYMMDD_TenFile.ext)."""
    stem = path.stem
    ext = path.suffix.lower()

    date_str, stem_no_date = extract_date(stem)
    cleaned_stem = clean_stem(stem_no_date)

    if date_str:
        new_stem = f"{date_str}_{cleaned_stem}" if cleaned_stem else date_str
    else:
        # Dùng ngày sửa đổi cuối (mtime) làm fallback
        mtime = os.path.getmtime(path)
        dt = datetime.fromtimestamp(mtime)
        date_str = dt.strftime("%y%m%d")
        new_stem = f"{date_str}_{cleaned_stem}" if cleaned_stem else date_str

    return new_stem + ext


def already_normalized(name: str) -> bool:
    """
    Kiểm tra file đã đúng định dạng chuẩn chưa.
    Chấp nhận hai dạng:
      - YYMMDD_TenFile.ext       (văn thư / công văn)
      - Tap[N].[x]_TenFile...    (hồ sơ thiết kế)
    """
    # YYMMDD_ prefix (6 chữ số + gạch dưới)
    if re.match(r"^\d{6}_", name):
        return True
    # Tap format: Tap1.1_, Tap2.3_, Tap3.1_, ...
    if re.match(r"^Tap\d+\.\d+_", name, re.IGNORECASE):
        return True
    return False


def run_cleanup(root: Path, preview: bool):
    """Quét và xóa file rác trong toàn bộ thư mục dự án."""
    junk_files = []

    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if is_junk(fpath):
                junk_files.append(fpath)

    tag = "[PREVIEW] " if preview else ""
    print(f"{tag}File rác tìm thấy: {len(junk_files)}")
    print("=" * 70)

    # Nhóm theo extension để dễ đọc
    by_ext: dict = {}
    for f in sorted(junk_files):
        ext = f.suffix.lower() or "(no ext)"
        by_ext.setdefault(ext, []).append(f)

    total_size = 0
    for ext, files in sorted(by_ext.items()):
        size = sum(f.stat().st_size for f in files if f.exists())
        total_size += size
        print(f"\n  [{ext}]  {len(files)} file  ({size // 1024} KB)")
        for f in files:
            rel = f.relative_to(root) if root in f.parents or f.parent == root else f
            print(f"    {rel}")

    print(f"\n{'=' * 70}")
    print(f"Tổng dung lượng sẽ giải phóng: {total_size // 1024} KB ({total_size / 1048576:.1f} MB)")

    if preview:
        print("\n[PREVIEW] Chạy lại với --cleanup (không có --preview) để xóa thực sự.")
        return

    # Xóa
    deleted = 0
    errors = 0
    for fpath in junk_files:
        try:
            fpath.unlink()
            deleted += 1
        except Exception as e:
            print(f"LỖI xóa {fpath.name}: {e}")
            errors += 1

    print(f"\nKết quả: Đã xóa {deleted} file | Lỗi: {errors}")


def run_rename(root: Path, preview: bool):
    """Quét và đổi tên file theo quy ước YYMMDD_."""
    renames = []
    skipped = 0

    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fpath = Path(dirpath) / fname

            if should_skip(fpath):
                skipped += 1
                continue

            ext = fpath.suffix.lower()
            if ext not in TARGET_EXTS:
                skipped += 1
                continue

            if already_normalized(fname):
                skipped += 1
                continue

            new_name = compute_new_name(fpath)
            new_path = fpath.parent / new_name

            if new_name != fname:
                renames.append((fpath, new_path))

    tag = "[PREVIEW] " if preview else ""
    print(f"{tag}Tổng số file sẽ đổi tên: {len(renames)}")
    print(f"Bỏ qua (CAD/DuToan/đã chuẩn/Tap-format): {skipped}")
    print("=" * 70)

    for old, new in sorted(renames):
        print(f"  {old.name}")
        print(f"→ {new.name}")
        print()

    if preview:
        print("[PREVIEW] Chạy lại không có --preview để thực thi.")
        return

    done = 0
    errors = 0
    for old, new in renames:
        if new.exists() and new != old:
            print(f"TRÙNG TÊN (bỏ qua): {old.name} → {new.name}")
            errors += 1
            continue
        try:
            old.rename(new)
            done += 1
        except Exception as e:
            print(f"LỖI: {old.name} → {new.name}: {e}")
            errors += 1

    print(f"\nKết quả: Đổi tên thành công {done} file | Lỗi: {errors}")


def main():
    parser = argparse.ArgumentParser(
        description="Đổi tên file theo quy ước dự án và dọn dẹp file rác",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  # Xem trước file sẽ đổi tên:
  python3 rename_files.py --root D:/GDrive/2508_CM_KeG6_NCKT --preview

  # Thực thi đổi tên:
  python3 rename_files.py --root D:/GDrive/2508_CM_KeG6_NCKT

  # Xem trước file rác sẽ bị xóa:
  python3 rename_files.py --root D:/GDrive/2508_CM_KeG6_NCKT --cleanup --preview

  # Xóa file rác:
  python3 rename_files.py --root D:/GDrive/2508_CM_KeG6_NCKT --cleanup
        """,
    )
    parser.add_argument("--root", required=True, help="Đường dẫn thư mục gốc dự án")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Chỉ in danh sách, không thực thi",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Xóa file rác (.bak, .tmp, ~$..., Thumbs.db, ...) thay vì đổi tên",
    )
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"LỖI: Không tìm thấy thư mục '{root}'")
        sys.exit(1)

    if args.cleanup:
        run_cleanup(root, args.preview)
    else:
        run_rename(root, args.preview)


if __name__ == "__main__":
    main()
        