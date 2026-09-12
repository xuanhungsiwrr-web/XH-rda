> Lịch sử bản 0.7. Không áp dụng model routing/budget trong tài liệu này cho runtime 0.8. Xem ARCHITECTURE-0.8.md.

# Cách dùng hệ thống báo cáo tùy biến

## 1. Nhạc trưởng theo nơi làm việc

Thiết kế giữ nhạc trưởng ngay trong phiên anh đang dùng: Claude Desktop ưu tiên Opus; ChatGPT/Codex ưu tiên Astra hoặc Sol. Nhạc trưởng lập kế hoạch, chọn nguồn, phân việc, tổng hợp và trao đổi với anh. Không cần trả thêm tiền API chỉ để gọi lại cùng vai này. Anh chọn model của phiên trong ứng dụng; plugin không tự đổi được model bằng cách ghi tên vào cấu hình.

Phần chung là các skills, cấu hình dự án, kho Markdown và server MCP. Bản 0.7 đã có CLI và server MCP local stdio. Dùng ChatGPT web cần kết nối MCP phù hợp với tài khoản và môi trường, không chỉ chép đường dẫn ổ D vào cuộc chat. Việc cài/kết nối thực tế chưa làm trong phiên này. [Hướng dẫn kết nối chính thức](https://developers.openai.com/plugins/deploy/connect-chatgpt).

## 2. Dự phòng nhưng giữ chất lượng

Ưu tiên theo khả năng xử lý đầu vào, không theo tên hãng. Với văn bản, có thể chuyển tác vụ viết/trích số từ OpenAI/Gemini sang DeepSeek đã cấu hình; với PDF scan/bản vẽ phải chọn tool nhận PDF/ảnh hoặc OCR trước. DeepSeek có model vision riêng; không phải mọi model DeepSeek đều nhận ảnh. [Tài liệu vision DeepSeek](https://api-docs.deepseek.com/guides/vision/).

NotebookLM qua thao tác tay là một adapter có thể dùng, không phải nút tự động mà plugin giả định luôn gọi được. Gemini MCP/xh-llm đã cài được host gọi qua packet; runtime không giả vờ tool tồn tại. Nếu tool lỗi rõ ràng, thử ứng viên đủ khả năng tiếp theo. Nếu timeout chưa biết server đã tính phí/xử lý hay chưa, lưu trạng thái để đối soát, đồng thời làm phần độc lập. Không lặp không giới hạn.

Chất lượng được giữ qua source/quote, trạng thái facts, tiêu chí section, reviewer khi rủi ro cao và phê duyệt đúng phiên bản. Không lấy câu “tôi tự tin” của model làm chứng nhận. Scores khởi tạo chỉ là giả định, cần benchmark từ hồ sơ thật; chưa thể hứa chọn được model rẻ nhất mà luôn tốt nhất.

## 3. Gemini Pro và router tính phí

Không nên đặt chi phí Gemini API bằng 0 chỉ vì anh có Google AI Pro. Gemini API có billing theo project/tier và mức sử dụng. Google AI Pro hiện có quyền lợi Google Developer Program, gồm Cloud credits theo điều kiện; cần xem đúng tài khoản, cách kích hoạt và phạm vi credit, không suy ra mọi API được miễn phí. [Gemini API billing](https://ai.google.dev/gemini-api/docs/billing), [quyền lợi Google AI Pro](https://support.google.com/googleone/answer/14534406).

MintRouter có thể là một đường API: tài liệu công bố endpoint tương thích OpenAI tại `https://api.mintrouter.ai/v1`, đồng thời có format Anthropic/Gemini. Runtime đã có cấu hình adapter OpenAI-compatible, nhưng chưa bật tài khoản hay gửi hồ sơ. [Tài liệu MintRouter](https://mintrouter.ai/introduction).

Danh mục công khai kiểm tra 07/09/2026 liệt kê Claude, Gemini, Kimi và OpenAI; chưa thấy DeepSeek/Perplexity. Không nên giả định một key MintRouter thay được tất cả. Giá niêm yết là của nhà cung cấp router, chưa phải chi phí thực đo trên tài khoản anh. [Danh mục/giá MintRouter](https://mintrouter.ai/models).

Khuyến nghị: cho router làm một lựa chọn, giữ endpoint trực tiếp DeepSeek/Perplexity làm đường riêng. Cùng một model qua hai đường có thể khác tính năng, alias, caching và giới hạn. Thử mẫu không chứa dữ liệu dự án trước; kiểm model ID thật, token usage, nguồn/citations và output. Hệ thống lưu khóa qua biến môi trường, không nhúng vào plugin hoặc ZIP dự án. Chưa xác minh chính sách lưu dữ liệu của MintRouter; cần đọc trước khi đưa hồ sơ nội bộ lên đó.

## 4. Đề cương từ thư viện của anh

Đã tìm thấy và đưa snapshot của **9 file** trong `AI_Workspace/NoiDung_CacBaoCao` vào gói portable. Trên máy này tiếp tục dùng thư viện gốc theo cấu hình, nên khi anh bổ sung file mới có thể khám phá lại. Khi chọn loại báo cáo, nhạc trưởng đối chiếu cả file nội dung chung lẫn tài liệu chuyên ngành nếu áp dụng.

Không chỉ nhìn tên mục: mỗi đoạn yêu cầu có ID và phải được map vào section hoặc giải thích tại sao không áp dụng. Có thể bổ sung mục con tùy dự án. Máy kiểm đủ ID; nhạc trưởng/reviewer kiểm nội dung có đáp ứng thật không. Các file này chứa một số trích dẫn dạng số chú thích và có file kết thúc bằng bullet trống; chúng là đầu vào cần rà nguồn, chưa được coi là xác nhận hiệu lực pháp lý. Không tự xóa yêu cầu hoặc bịa phần bị thiếu.

## 5. Dữ liệu đầu vào và bảng thông tin

Anh chỉ cần đưa thư mục Google Drive hoặc đường dẫn local và nói loại báo cáo. Bước đầu lập danh mục metadata, phân nguồn dự án/đối chứng/pháp lý, đọc chọn lọc và ghi danh sách thiếu. Không bắt anh chuẩn bị đủ địa hình, địa chất, bản vẽ ngay lần đầu.

| Thông tin | Khi chưa rõ | Bổ sung sau |
|---|---|---|
| Tên dự án, địa điểm | Ghi chưa xác định, dùng mã làm việc | Sửa metadata |
| Đơn vị tư vấn, chủ đầu tư | Để trống có dấu nhận biết trong draft | Cập nhật một lần; render lại metadata |
| Loại báo cáo, bước thiết kế | Nếu ảnh hưởng khung thì hỏi ngắn; nếu anh bảo cứ làm thì ghi giả định dự thảo | Duyệt lại outline khi loại/bước thay đổi |
| Quy mô, cao trình, địa chất | Không tự điền; tạo TODO và phần còn thiếu | Nhập facts có nguồn, anh duyệt |
| Khuôn Word, văn phong | Chọn từ thư viện hoặc ghi cần bổ sung | Snapshot template/profile theo version |
| Thư mục Drive | Lưu ID/URL và nguồn nào thuộc dự án tham khảo | Quét file mới/đổi khi làm lần sau |

Ví dụ giao việc: “Lập BCĐXCTĐT cho dự án X từ folder Drive này. Cứ làm bản nháp; chủ đầu tư và địa chất bổ sung sau.” Hệ thống viết phần có căn cứ, giữ TODO ở phần chưa đủ. Không dùng số của dự án bên cạnh như số dự án X.

Lần 2 dùng lại MD lần 1 và bản chuyển đổi còn khớp source hash. Nguồn mới chỉ làm các phần phụ thuộc cần cập nhật. Dependency phải được ghi đúng: nếu một thay đổi ảnh hưởng lập luận bằng lời thì nhạc trưởng cũng phải khai quan hệ, máy không tự hiểu hết mọi liên hệ ngữ nghĩa.

## 6. Hao token khi tìm và cào web

Skill xh-trinh-sat cũ chủ yếu hướng dẫn Exa tìm và ghi snippet, **không có log chứng minh nó luôn đọc toàn bộ website**. Vì vậy chưa thể kết luận đổi scraper sẽ tiết kiệm một tỷ lệ cố định. Cần so hai đường trên cùng câu hỏi, cùng nguồn và cùng yêu cầu bằng chứng.

Scraper của anh có ý tưởng đúng: lưu file, trả đường dẫn ngắn. Nhưng nếu model sau đó đọc toàn bộ file nhiều lần thì token vẫn phát sinh. Bản tích hợp đã sửa các điểm: lưu vào research thay vì 10_content; giữ raw HTML và URL/thời điểm; bỏ UI noise, giữ bảng và link; trả metadata; cache nguồn; lấy đoạn phù hợp thay vì đẩy cả trang vào nhạc trưởng. Trang JS/login hoặc dữ liệu quá lớn báo chưa xử lý được, không trả “đã lấy trọn vẹn” khi chưa chứng minh.

Ví dụ minh họa, không phải benchmark: 20 trang × 4.000 token = 80.000 token nội dung. Nếu nhạc trưởng đọc cả 80.000 thì chịu toàn bộ input đó. Nếu worker đọc 80.000 rồi trả evidence 4.000 cho nhạc trưởng, input nhạc trưởng giảm 95%, nhưng tổng input hai model là khoảng 84.000, chưa tính prompt/output. Tiết kiệm tiền chỉ xảy ra khi worker rẻ hơn đủ nhiều và không phải sửa lại. Nếu worker input rẻ bằng 1/10, phần input quy đổi thành khoảng 12.000 token giá nhạc trưởng, giảm 85% so với baseline 80.000; đây vẫn chỉ là phép tính giả định, chưa tính output, phí tìm kiếm, retries và cache.

Muốn giảm **tổng token**, tốt hơn là scraper + lọc trùng + chọn đoạn tất định trước, chỉ gửi các đoạn liên quan cho worker. Cần giữ câu trích/trang/URL và kiểm mức đầy đủ để tránh tiết kiệm bằng cách bỏ mất dữ liệu. Nếu đầu vào đã là MD, không gọi chuyển MD lần nữa sau extraction. Đo riêng: bytes tải, text chars, token provider báo, cached input, output, số lần sửa, độ đầy đủ nguồn và tổng USD. Byte/4 chỉ là ước lượng yếu, đặc biệt với tiếng Việt; bản này ghi tokens=null khi không có số đo.

## 7. Perplexity và Humanizer

Perplexity hợp lý cho **khám phá văn bản, tìm nguồn và phát hiện văn bản liên quan**. Không giao cho nó quyền tự xác nhận mọi điều khoản/hiệu lực. Bản script tích hợp bỏ filter một năm mặc định, ưu tiên cổng văn bản/chính phủ/tiêu chuẩn, lưu cả kết quả đầy đủ/citations/usage ra file và trả bản chỉ mục ngắn. Date filter chỉ dùng khi tìm văn bản mới theo yêu cầu rõ ràng. [Tài liệu filter Perplexity](https://docs.perplexity.ai/docs/sonar/filters).

Sau tìm kiếm cần mở văn bản gốc, đối chiếu số hiệu, cơ quan, hiệu lực, sửa đổi/bãi bỏ, điều kiện chuyển tiếp và phạm vi dự án. Không có full text TCVN thì không tự suy điều khoản từ snippet. Đây là cơ chế nghiên cứu và kiểm nguồn, không phải kết luận pháp lý về các văn bản trong thư viện.

Humanizer đã được đưa vào gói kèm MIT license, qua skill xh-humanize riêng. Chỉ dùng cho phần văn xuôi cần biên tập sau khi có nội dung: bỏ câu sáo rỗng/lặp lại, giữ giọng kỹ thuật và văn phong mẫu của anh. Không áp dụng ngôi thứ nhất/cảm xúc của bài blog. Guard kiểm số, placeholders, heading, bảng, URL và code; vẫn cần đọc lại ý nghĩa. Bản sửa văn phong tạo revision mới và phải review lại, không tự ghi đè bản anh đã sửa.

## 8. Viết tuần tự hay nhiều model cùng lúc

Khuyến nghị mặc định: **chốt đề cương + dữ liệu chung trước, sau đó viết tối đa hai phần độc lập cùng lúc** nếu host có khả năng gọi worker. Các phần liên quan cao trình, quy mô và phương án phải theo dependency; chương tổng hợp/kết luận viết sau. Nhiều model không tự động tốt hơn và thường tăng chi phí review.

Ba chế độ đã có: all (lập kế hoạch toàn báo cáo), section (phần chọn và phần phụ thuộc), incremental (phần chưa có hoặc stale). “Toàn báo cáo” vẫn chia task vừa đủ; không nhất thiết dồn cả report vào một lần gọi API. Plan tạo batch, còn nhạc trưởng thực sự giao worker; chưa có background worker pool tự chạy độc lập khỏi host.

Nếu sửa riêng tên đơn vị, thường cập nhật metadata và render lại, không viết lại chương kỹ thuật. Nếu sửa cao trình thì phải cập nhật tính toán, section dùng nó và kết luận liên quan. MD không đổi được giữ nguyên từng byte trong thử nghiệm.

## 9. Artifact tính toán và Word

Đăng ký Excel/Word tính toán như một artifact có nguồn, version, input facts và bản tóm tắt MD. Summary ghi công thức, giả định, đơn vị, kết quả, vị trí sheet/cell hoặc trang. Người kiểm duyệt kết quả trước khi chuyển thành verified fact. Khi Excel đổi, summary và phần báo cáo phụ thuộc bị stale. Runtime không tự khẳng định công thức tính cao trình đúng; cần mô-đun tính toán/người kiểm theo phương pháp dự án.

Có thể render một phần để rà nhanh. Bản giao cuối nên **render một lượt từ toàn bộ MD hiện hành**, cùng khuôn, style, đánh số đề mục/hình/bảng và TOC. Đây là thao tác định dạng, không phải dùng AI viết lại toàn bộ. Không ghép các DOCX đã render riêng vì dễ lệch numbering/section/header. Sau render phải cập nhật trường Word và kiểm trang thực tế; bài thử hiện tại xác minh DOCX mở được và có đủ nội dung, chưa thay cho QA bằng Word thật.

## 10. Đã triển khai và còn cần kết nối

Đã có source 0.7: 10 skill entrypoints refactor + xh-humanize; runtime revision/approval/impact; coverage requirement; plan; source retrieval; attachment; render; MCP stdio; cấu hình router; script web/pháp lý mới; source library snapshot; backup và export project. Bản gốc Tools và các dự án hiện hữu không bị di chuyển.

Chưa có trong phiên: tài khoản/API key cho provider/router, MCP Gemini_QC/xh-llm đang cài thực tế, kết nối Drive của anh, template thật và phiên Word để kiểm dàn trang. Do đó chưa kiểm live fallback, chi phí thật, khả năng deploy ChatGPT và Word layout. Không tuyên bố plugin đã tự vận hành trên cả hai ứng dụng. Cấu hình mẫu và hướng dẫn kỹ thuật đi kèm để bước kết nối tiếp theo cụ thể, không cần anh đọc lại bản audit kiến trúc.
