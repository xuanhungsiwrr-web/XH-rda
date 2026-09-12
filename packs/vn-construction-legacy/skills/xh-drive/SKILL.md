---
name: xh-drive
description: |
  Làm việc thẳng với hồ sơ dự án nằm trên Google Drive mà không cần chép về ổ cứng — quét thư mục gốc, phân loại và sắp xếp file theo cây hồ sơ chuẩn, đọc nội dung tài liệu để dựng _facts.yaml, lập danh mục tra cứu. Kích hoạt khi người dùng nhắc: hồ sơ trên Drive, đọc thẳng từ Drive, folder Google Drive, sắp xếp trên Drive, không copy về máy, kho dự án trên Drive, danh mục file Drive. Chỉ dùng khi hồ sơ nằm trên Drive; hồ sơ đã có trên ổ đĩa hoặc trong thư mục đã kết nối thì dùng xh-proj-org.
---

# XH_Drive — hồ sơ nằm trên Drive, không cần chép về máy

Trước đây mỗi lần viết phải chép nguồn vào xưởng báo cáo. Không cần nữa. Connector Google Drive đọc thẳng được, kể cả `.docx`, `.pdf`, `.xlsx` — trả về **Markdown đã bóc chữ**, không phải base64.

Kiểm chứng 25/08/2026 trên `1.CauSD_DeXuatCTDT_V4R1.docx` (226KB): `get_file_metadata` trả về đúng heading, bảng và văn bản tiếng Việt có dấu.

## Việc nào làm được, việc nào không

| Việc | Được | Bằng gì |
|---|---|---|
| Liệt kê thư mục, tìm file | ✅ | `search_files` với `parentId = '<id>'` |
| Đọc nội dung `.docx` `.pdf` `.xlsx` `.pptx` | ✅ | `read_file_content` — ra Markdown |
| Xem nhanh phần đầu file | ✅ | `get_file_metadata` — trường `contentSnippet` |
| Tạo thư mục mới | ✅ | `create_file` với `contentMimeType: application/vnd.google-apps.folder` |
| **Di chuyển file sang thư mục khác** | ✅ | `update_file` với `parentId` mới |
| Đổi tên file | ✅ | `update_file` với `title` mới |
| Xoá file | ✅ | `trash_file` — vào thùng rác, khôi phục được |
| Ghi file text nhỏ lên Drive | ✅ | `create_file` với `textContent` |
| **Ghi `.docx` thành phẩm lên Drive** | ❌ | phải base64; bản 456KB thành 608.000 ký tự — không đẩy nổi |
| **Trích hình từ bản vẽ PDF** | ❌ | connector chỉ trả chữ, không trả ảnh |
| So hash phát hiện trùng lặp thật | ❌ | Drive không trả hash qua connector |

**Hai việc ❌ cuối xử lý thế nào:** file cần cắt hình hoặc cần render ra `.docx` thì tải về qua Drive for Desktop (ổ `G:\`) hoặc thư mục đã kết nối, làm ở đó, rồi để Drive tự đồng bộ ngược lên. Đọc thì qua connector, ghi bản nặng thì qua ổ đĩa.

**Trùng lặp:** không có hash thì chỉ nghi được, không khẳng định được. Dấu hiệu dùng được: **cùng tên** và **cùng `fileSize` từng byte**. Hai file cùng tên khác kích thước là hai phiên bản khác nhau — trong ngành này rất hay gặp, tuyệt đối không tự xoá.

## Quy trình năm bước

### Bước 1 — Xác định thư mục gốc

Hỏi người dùng tên thư mục, rồi tìm `id`:

```
search_files: query = "mimeType = 'application/vnd.google-apps.folder' and title contains '<tên>'"
```

Ghi `id` lại. Mọi bước sau đi theo `parentId`, **không đi theo tên** — tên trùng nhau rất nhiều.

### Bước 2 — Quét toàn bộ cây

Đệ quy theo `parentId`, mỗi cấp một lệnh `search_files`, đặt `excludeContentSnippets: true` để khỏi kéo nội dung về vô ích. Gom kết quả thành JSON.

> Connector không quét đệ quy sẵn. Kho lớn thì tốn nhiều lượt gọi — báo trước cho người dùng, đừng để họ ngồi chờ không biết đang làm gì.

### Bước 3 — Phân loại bằng script, không bằng cảm tính

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/phan-loai-ho-so.py --json ds-file.json --ra mapping.json
```

Script chấm theo tên và đuôi file, trả ba mức: `chac` · `doan` · `khong_ro`, kèm cột nghi trùng.

**Chỉ tự xếp những file `chac`.** File `doan` và `khong_ro` gom thành một bảng, hỏi người dùng **một lần** — kèm tên file thật, không hỏi chung chung. Đây là Nguyên tắc 1 của `xh-proj-org`, áp dụng nguyên vẹn ở đây.

### Bước 4 — Trình bảng mapping, chờ xác nhận, rồi mới di chuyển

Trình bảng `file → nhóm hiện tại → nhóm đề xuất`, người dùng gật thì mới chạy.

Tạo thư mục:
```
create_file: title = "10.PhapLy", contentMimeType = "application/vnd.google-apps.folder", parentId = "<id cha>"
```

Di chuyển từng file:
```
update_file: fileId = "<id>", parentId = "<id thư mục đích>"
```

**Ba điều bắt buộc:**

- **Ghi log trước khi chạy** — mỗi dòng: `fileId`, tên, `parentId` cũ, `parentId` mới. Không có log thì không hoàn tác được.
- **Di chuyển từng file một, không có thao tác hàng loạt.** Kho vài trăm file sẽ chạy lâu; chia đợt và báo tiến độ.
- **Không xoá gì ở bước này.** File rác và file nghi trùng chỉ liệt kê ra, xoá là việc riêng, hỏi riêng.

### Bước 5 — Lập danh mục tra cứu

Xuất một file Excel (dùng skill `xlsx`) đặt ngay tại thư mục gốc: mỗi dòng một file, kèm `viewUrl` làm hyperlink mở thẳng. Thêm sheet riêng cho: file chưa xếp được · file nghi trùng · log di chuyển.

Link dùng `viewUrl` mà Drive trả về, **không tự dựng đường dẫn** `file:///` như khi làm trên ổ đĩa.

## Đọc nội dung để dựng `_facts.yaml`

Đây mới là chỗ tiết kiệm công nhất — trước phải chép file về, giờ đọc thẳng.

1. `read_file_content` trên đúng những file có số cần lấy, **không đọc cả kho**.
2. Quét **theo danh mục chỉ tiêu** của `qc-rules.yaml`, không quét tự do. Bảo mô hình "trích mọi số liệu" sẽ trả về hàng nghìn con số vô dụng.
3. Mỗi khoá ghi đủ: `value` · `unit` · `source` · `quote` · `status` · `data_type` — và `nguon_du_an` nếu là số mượn.
4. `source` ghi **tên file kèm `id` Drive**, để lần sau truy ngược được:
   `source: "1.CauSD_DeXuatCTDT_V4R1.docx#drive:1DBkQhm_Af53kRiw1Dw1z4EWvds7nJKzk"`

> ⚠️ **CẢNH BÁO NGHIÊM TRỌNG: API tự động cắt file.**
> Lệnh `read_file_content` qua Google Drive API bị giới hạn ngầm (~10MB) và sẽ **tự động cắt bỏ phần đuôi file mà không báo lỗi**. Với hồ sơ khảo sát dày, đọc xong phải KIỂM TRA NGAY: mục lục có tới chương cuối không, câu cuối cùng có bị đứt ngang không. Nếu nghi ngờ bị cắt, PHẢI tải file về ổ đĩa cứng và đọc cục bộ, hoặc dùng `xh-evidence` để xử lý file nặng.

## Không làm

- **Không xoá, không đổi tên hàng loạt khi chưa có xác nhận từng nhóm.** Thùng rác Drive khôi phục được, nhưng một trăm file bị đổi tên sai thì không ai dựng lại nổi thứ tự cũ.
- **Không coi hai file cùng tên là trùng lặp.** Phải cùng cả kích thước, và vẫn phải hỏi.
- **Không đọc cả kho vào ngữ cảnh** để "hiểu tổng quan". Đọc theo danh mục chỉ tiêu.
- **Không ghi bản `.docx` thành phẩm lên Drive qua connector.** Ghi qua ổ đĩa đồng bộ.
