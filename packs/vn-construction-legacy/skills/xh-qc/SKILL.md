---
name: xh-qc
description: |
  Rà soát bản thảo báo cáo tư vấn thiết kế trước khi trình duyệt — đối chiếu số liệu với _facts.yaml, bắt số lệch giữa các mục, số trong văn không khớp bảng, mất dấu phẩy thập phân, vi phạm ràng buộc vật lý, placeholder còn sót, ký tự font Symbol. Kích hoạt khi người dùng nhắc: rà soát báo cáo, kiểm tra bản thảo, soát lỗi số liệu, QC báo cáo, kiểm mâu thuẫn, qc-check, kiểm tra trước khi nộp, bắt lỗi hồ sơ. Kể cả khi lỗi số liệu chỉ lộ ra sau khi đã render thành file Word, vẫn dùng xh-qc trước để sửa gốc (_facts.yaml / bản thảo Markdown) rồi mới render lại — xh-qc luôn đi trước xh-docx khi vấn đề là con số sai, không phải trình bày.
---

# XH_QC — rà soát ba tầng

Rà soát chạy **theo đúng thứ tự tầng**. Bỏ tầng 1 để gọi thẳng agent là lãng phí: 60–70% lỗi bắt được bằng luật cứng, miễn phí, không bao giờ quên. Từ v0.3.0, dừng ở ba tầng — không còn tầng gọi mô hình ngoài Claude, không cần khoá API trả phí nào.

```
TẦNG 1 — qc-check.py           luật cứng, 1 giây, 0 token
     ↓ chỉ phần còn lại mới cần đến LLM
TẦNG 2 — agent xh-qc           5 lăng kính, ngữ cảnh sạch, nhiệm vụ đối nghịch
     ↓ tuỳ chọn, lỗi chuyên môn quan trọng
TẦNG 3 — bỏ phiếu              3 agent, ≥2 phiếu mới báo
```

## Tầng 1 — chạy trước, luôn luôn

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/qc-check.py BaoCao.docx \
       --rules ${CLAUDE_PLUGIN_ROOT}/scripts/qc-rules.yaml \
       --facts _facts.yaml --json ketqua.json
```

Chạy được trên `.docx` hoặc thư mục `10_content/*.md`. Mã thoát 1 nếu có lỗi nghiêm trọng.

| Mã lỗi | Bắt gì |
|---|---|
| `SO_LECH` | cùng một chỉ tiêu có nhiều giá trị khác nhau giữa các mục |
| `VAN_LECH_BANG` | số trong văn không khớp giá trị nào trong bảng (chấp nhận cả tổng các đoạn) |
| `BANG_SAI_TEN` | tiêu đề bảng không khớp đại lượng nằm trong bảng |
| `NGHI_MAT_PHAY` | hai lần nêu cùng chỉ tiêu chênh **đúng 10 lần** |
| `RANG_BUOC` | vi phạm ràng buộc vật lý về cao trình |
| `CON_TODO` `CON_FACT` `SO_DE_TRONG` `KY_TU_PUA` | chỗ trống và ký tự rác còn sót |
| `QUY_UOC` | dấu thập phân lẫn chấm/phẩy, viết `oC` thay `°C` |
| `SO_CHUA_DUYET` | bản thảo dùng khoá `_facts.yaml` chưa `verified` |
| `DEM_THANG_SAI` `UOC_LUONG_MAU_THUAN` | "6 tháng, từ tháng 5 đến tháng 11"; "gần 2.404" |
| `MUON_THIEU_KHAI_NGUON` `MUON_THIEU_DAN_NGUON` `MUON_THIEU_KHUYEN_CAO` | số mượn từ dự án khác (`data_type: REFERENCE`) thiếu tên nguồn hoặc thiếu khuyến cáo khảo sát bổ sung |
| `FACT_MISSING` `LEGAL_THIEU_NGUON` | dùng khoá `MISSING` chưa có số; trị số `LEGAL` không dẫn văn bản |

**Chỉ tiêu chưa khai trong `qc-rules.yaml` thì script không biết mà so.** Khi làm loại công trình mới, thêm chỉ tiêu vào file đó — mỗi mục cần `nhan` (các cách viết mà báo cáo thật dùng), `don_vi`, `hop_ly` (khoảng giá trị hợp lý, để chống nhặt nhầm số thứ tự), `dung_sai`. Nếu nhãn không đủ chính xác thì thêm `mau` — danh sách regex có nhóm 1 là con số.

## Tầng 2 — gọi agent, không tự kiểm

Gọi bằng công cụ **Agent** với `subagent_type: "xh-qc"`. Đừng bảo chính mình "kiểm lại" — cùng một ngữ cảnh đã viết ra bản thảo thì vẫn giữ nguyên mọi giả định sai, và luôn dễ dãi với bài của mình.

```
Agent(subagent_type="xh-qc",
      prompt="Rà soát 10_content/C2-1.md của dự án <mã>.
              Nguồn: _facts.yaml, _references-scope.md, specs/<LoaiBC>.yaml.
              Đã chạy qc-check.py, kết quả ở ketqua.json — đừng lặp lại
              những lỗi đó, hãy tìm thứ script không thấy.")
```

Agent chỉ **báo cáo**, không sửa file. Cho quyền sửa thì nó vá lỗi rồi im lặng, và người dùng mất thông tin.

## Tầng 3 — Bỏ phiếu (chỉ áp dụng cho lỗi chuyên môn cao)

Khi Tầng 2 phát hiện lỗi nghiêm trọng liên quan đến **giải pháp kỹ thuật, lập luận thiếu logic, hoặc sai khác lớn so với định mức** — loại lỗi mà một agent đọc một lần dễ báo nhầm hoặc bỏ sót:

- Gọi 3 agent `xh-qc` độc lập cùng đọc lại ngữ cảnh của đúng lỗi đó, mỗi agent với ngữ cảnh sạch.
- Báo cáo lỗi cho người dùng **CHỈ KHI có từ 2 phiếu trở lên (≥2/3) đồng thuận** đó là lỗi.

Không có tầng thứ tư gọi mô hình ngoài Claude — bỏ hẳn khỏi luồng từ v0.3.0, vì không có connector MCP nào cho ChatGPT/OpenAI và người dùng chọn không tiếp tục giữ khoá API trả phí cho việc này. Tầng 3 vẫn chỉ dùng Claude (qua Agent), không có mô hình ngoài nào tham gia bỏ phiếu.

## Chống báo lỗi sai

Báo sai nguy hiểm hơn bỏ sót: sau vài lần bị báo nhầm, người dùng bỏ qua cả danh sách, kể cả lỗi thật.

- **Bắt buộc trích nguyên văn.** Không trích được đoạn có lỗi thì không được báo.
- **Tự phản biện một lần** với lỗi số liệu và lỗi chéo chương: *"có cách đọc nào khiến điều này KHÔNG phải lỗi không?"* Có → hạ xuống mức cảnh báo.
- **Việc không có căn cứ trong hồ sơ → đặt thành câu hỏi**, không báo thành lỗi.

Kinh nghiệm thật: một cao trình ghi trong mục "lan can" có thể là cao độ **đỉnh kè** tức chân lan can, không phải đỉnh lan can. Đọc sát ngữ cảnh trước khi kết luận vi phạm an toàn.

## Sau khi rà xong

Trả về danh sách có **vị trí** (tên mục, số dòng), **trích nguyên văn**, **mức độ**, và **việc cần làm**. Lỗi số liệu thì chỉ về khoá `_facts.yaml` cần sửa, không sửa rải rác trong bản thảo.
