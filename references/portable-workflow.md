# Quy trình portable 0.7

Nguồn plugin dùng chung, mỗi dự án giữ state/artifacts riêng. Đây là quy trình hiện hành; `packs/vn-construction-legacy` là tham khảo có điều kiện, không phải policy điều phối. Các hướng dẫn cổng Gemini cố định của bản cũ đã được thay bằng phân bổ capability.

## Khởi động và intake

1. Nhận thư mục dự án/Drive và loại báo cáo. Xác định host thật: Claude Desktop → ưu tiên Opus; ChatGPT/Codex → ưu tiên Astra/Sol. Plugin không đổi model của ứng dụng; dùng model người dùng chọn ở host. Không gọi lại nhạc trưởng qua API.
2. `init` tạo workspace; `metadata` cập nhật các trường riêng. Chưa biết đơn vị/chủ đầu tư để null, không bịa. “Cứ làm” cho phép draft và TODO; không phải duyệt số liệu hay cho phép ghi final.
3. Nguồn Drive: host dùng connector thực tế hoặc folder đã đồng bộ, lưu file dưới sources/. `ingest` đăng ký với source_id là file ID đã chuẩn hóa, source_url, source_kind. Bản chuyển đổi MD phải `register` artifact `extracted:<id>` với deps `source:<id>`. Lưu số trang/cell/bảng để truy về gốc. Nguồn thêm sau tạo revision, status chỉ ra phần stale.
4. `library` xếp hạng tên file để khám phá, không phải quyết định pháp lý. Chọn đủ files phù hợp từ XH_REPORT_LIBRARY; `requirements` snapshot toàn văn và tạo IDs. `outline` ánh xạ mọi ID vào sections hoặc exclusions có lý do. Nhạc trưởng phải kiểm semantic coverage; máy chỉ kiểm không mất ID. Người dùng duyệt outline đúng revision.

## Các lệnh cùng một giao diện

CLI: `python <plugin>/scripts/xh.py <action> --project <project-root> --data <payload.json>`.
MCP: `xh_project(action, project_code, payload)`, project_code tương đối với XH_PROJECTS_ROOT.

| Action | Payload chính |
|---|---|
| init | `{"metadata":{"project_name":"...","report_type":"..."}}` |
| metadata | `{"consultant":"...","investor":"..."}`; chỉ cập nhật trường được cung cấp |
| requirements | `{"root":"<library>","files":["<filename.md>"]}`; MCP lấy root từ cấu hình |
| outline | `{"sections":[{"id":"C01","title":"...","requirements":["<id>"],"depends_on":[],"risk":"normal"}],"exclusions":{}}` |
| approve | `{"artifact":"outline","revision":"<current-id>","actor":"<người đã duyệt>"}` |
| plan | `{"mode":"incremental","parallel":2}`; mode all/section/incremental, tùy chọn section |
| fact | `{"key":"...","record":{"value":0,"unit":"m","source":"file#page","quote":"...","data_type":"PROJECT"}}`; ví dụ số 0 là minh họa schema |
| resolve-fact | `{"key":"...","candidate_index":0,"actor":"<người duyệt>"}` |
| section | `{"sid":"C01","text":"# ...","deps":["source:..."],"expected":"<revision hiện hành khi sửa>"}` |
| review | `{"sid":"C01","findings":[],"reviewer":"<model/agent thật>","coverage_checked":true}` |
| register | `{"artifact":"extracted:...","path":"sources/converted/file.md","deps":["source:..."],"origin":"system"}` |
| retrieve | `{"query":"...","limit":5,"max_chars":12000}`; trả đoạn nguyên, không cắt giữa câu |
| context | `{"artifacts":["section:C01","fact:..."],"max_bytes":32000}` |
| attachment | `{"name":"calc-01","file":"calculations/calc.xlsx","summary":"<MD kết quả có ô nguồn>","deps":["fact:..."]}` |
| assemble | `{"final":false}`; ghép MD, không viết lại bằng AI |
| render | `{"template":"templates/report.dotx","template_map":"templates/contract.yaml","final":false}`; thêm section để preview |
| rollback | `{"revision":"<id cũ>","actor":"<người yêu cầu>"}`; giữ dependency cũ để không chứng nhận bản cũ trên số mới |
| export | `{"destination":"<file ZIP mới>"}`; CLI path do user chọn, MCP giới hạn trong project |

`status` không cần payload. File sources chưa register không nằm trong archive xuất tự động. Không lưu API key vào project hoặc source artifacts. Khóa API chỉ qua môi trường server.

## Dispatch và fallback

`execute` nhận `{"task":{"objective":"...","artifacts":[...],"capabilities":["writing"],"modality":"text","quality_floor":0.7,"criteria":[...],"output_format":"markdown"},"available_tools":["<tool thật>"]}`.

`config/providers.json` là khởi điểm, scores là prior chưa benchmark. Copy thành providers.local.json, điền model ID chính xác, enable, limits và reserve khi có tài khoản. Model/key chưa cấu hình không được gọi. `openai-chat` hỗ trợ dịch vụ dùng giao thức Chat Completions; Gemini/NotebookLM/xh-llm dùng handoff tới MCP/host/manual. Kết quả handoff là yêu cầu để host gọi tool, không phải tool đã chạy. Khi lỗi rõ ràng, thêm ID vào task.exclude và gọi lại. Host phải giới hạn tối đa 3 lựa chọn, 2 vòng sửa và ghi review/usage; generic direct API adapter tự lưu attempt và budget. Handoff/manual/Perplexity có usage riêng do host cộng, chưa nằm trong bộ đếm direct API.

`execute` chỉ xuất candidate. Hệ thống không tự dùng câu trả lời API làm nội dung đã duyệt. Timeout không biết upstream đã xử lý chưa được lưu uncertain: giữ reserve, không replay tự động; làm tiếp phần độc lập. Lỗi HTTP/output rõ ràng có thể chuyển ứng viên. Chuỗi DeepSeek dự phòng chỉ hợp lệ nếu model và adapter nhận được modality; runtime direct adapter hiện chỉ text, ảnh/PDF phải qua MCP hoặc OCR/chuyển đổi trước.

Budget là cap số call và reserve theo call ở local, không thay billing cap upstream. `call_ceiling_usd` là ước tính bảo thủ do operator đặt, chưa phải trần được provider cưỡng chế. Dùng thêm spending cap ở dịch vụ để có trần tiền thật. Usage thiếu ghi null; không coi miễn phí. Không có chi phí/token benchmark thực tế trong bản này.

## Incremental và song song

Mỗi section có ID bền vững, dependency facts/source/calculations/section. Mọi nội dung liên quan bằng diễn giải cũng phải ghi deps; hệ thống không tự suy ra dependency ngữ nghĩa hoàn hảo. Chốt outline và các facts chung trước. Mặc định 2 worker độc lập khi host hỗ trợ, mỗi worker viết section riêng. Plan chỉ tạo batches; host thực thi. Chương kết luận/tổng hợp chạy sau đầu vào. Chế độ all nghĩa là xử lý toàn report theo task, không ép một prompt khổng lồ.

Worker song song phải gửi `expected_deps` mapping tất cả dependency ID → revision đã đọc, gồm outline/facts/section. Nếu nguồn đổi khi worker đang viết, runtime từ chối gắn kết quả cũ vào input mới. Direct API executor tự pin mapping từ context packet. Khi sửa section hiện hữu, gửi thêm `expected` là revision output ban đầu.

Sửa ngoài hệ thống: register/section với origin human để nhập lại, hoặc rollback theo revision. Bản human không tự được approved. Không tự ghi đè file có thay đổi ngoài runtime. Chỉ lưu true coverage_checked sau khi đã đối chiếu, không đánh dấu máy móc.

## Word và tính toán

Action `templates` đọc các file `templates/*.template.json` và xếp theo metadata. Manifest có dạng `{"id":"template-id","file":"templates/report.dotx","contract":"templates/contract.yaml","matches":{"report_type":["tên loại báo cáo"],"consultant":["tên đơn vị"]}}`. Thêm file/manifest là được khám phá; thiếu metadata/đồng điểm phải chọn rõ, không tự khẳng định đúng khuôn. Trước render vẫn kiểm styles. `contract.yaml` nhận cấu trúc template-map cũ hoặc `styles` ánh xạ semantic roles như test fixture.

Có thể preview từng phần; bản tổng cuối render một lượt từ MD hiện hành theo outline và cùng template. Không ghép DOCX đã dàn trang riêng. Renderer hỗ trợ semantic style map và phát hiện thiếu file/style. Template cần chứa cấu trúc TOC/numbering; Word cập nhật fields và con người/host kiểm layout sau render. `final:true` kiểm cổng nội dung, không tự chứng nhận bản Word đã chuẩn.

Attachment giữ bản Excel/Word gốc, summary MD và deps; người kiểm xác nhận công thức, unit, điều kiện áp dụng, ô/trang nguồn. Muốn chèn vào báo cáo: đưa summary/bảng/ảnh vào section, thêm attachment ID vào deps. Không tự nhập công thức Excel bằng suy đoán hoặc coi bảng Word là tính toán đã kiểm. `{{artifact:...}}` chưa materialize phải được xử lý trước final.
