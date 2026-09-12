# Kết quả kiểm thử 0.7.0

Ngày 07/09/2026, Windows, Python 3.14.7 trong môi trường riêng của plugin.

- 25 tests: PASS, lần chạy cuối 8,263 giây.
- 11 SKILL.md: PASS bộ quick_validate.py với UTF-8.
- 28 file Python tại thời điểm kiểm cú pháp: không lỗi cú pháp (bao gồm scripts trong pack legacy).
- MCP: khởi động subprocess stdio thật, initialize, list_tools, gọi init và status thành công.
- DOCX: render fixture ba phần thành một file, mở lại bằng python-docx và kiểm đủ nội dung; thiếu style/chương thì chặn.
- Regression: importer không ghi đè facts conflict; phê duyệt không theo sang bản sửa; source đổi làm downstream stale; không đè bản sửa ngoài runtime; rollback giữ dependency cũ; worker không gắn kết quả cũ vào input mới.
- Provider/network: HTTP failure/fallback, timeout, budget và web/Perplexity dùng giả lập; không phát sinh gọi API trả phí trong tests.

Lệnh chạy: `.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v`.

Không có live provider/Drive verification, không đo chất lượng model hoặc tiết kiệm token trên hồ sơ thật. Không có kiểm dàn trang bằng Word, mục lục hiển thị hoặc page-break của template người dùng. Server chỉ được kiểm local stdio, chưa cài vào Claude Desktop/ChatGPT hoặc triển khai remote. Requirement coverage kiểm đủ mapping, vẫn cần review ngữ nghĩa và hiệu lực nguồn pháp lý. Template discovery là đọc manifest, không tự suy đoán tổ chức từ file.
