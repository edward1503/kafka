# Bộ bài học: Kiến trúc Apache Kafka

Bộ file sử dụng cách tách nội dung như bài Databricks: lý thuyết, slide, hands-on, đề trắc nghiệm và solution là các tài liệu riêng. Bài đọc, lab, quiz và solution có dự án LaTeX độc lập theo template AIO2026; slide là file PowerPoint dựng từ template trình bày của AIO2026. Mỗi tài liệu đều có bản PDF.

## Các file để đọc và chỉnh sửa

| Tài liệu | Nguồn chỉnh sửa | Dự án LaTeX | PDF |
| --- | --- | --- | --- |
| Bài lý thuyết | [kafka-architecture.md](kafka-architecture.md) | [architecture/main.tex](architecture/main.tex) | [Bài đọc](../output/pdf/kafka-architecture.pdf) |
| Slide bài giảng | [architecture-slides/build_deck.py](architecture-slides/build_deck.py) | PowerPoint: [kafka-architecture-slides.pptx](../output/kafka-architecture-slides.pptx) | [Slide](../output/pdf/kafka-architecture-slides.pdf) |
| Lab | [kafka-architecture-hands-on.md](kafka-architecture-hands-on.md) | [architecture-lab/main.tex](architecture-lab/main.tex) | [Hướng dẫn lab](../output/pdf/kafka-architecture-lab.pdf) |
| File chạy lab | [lab/docker-compose.replication.yml](lab/docker-compose.replication.yml) | — | — |
| Đề trắc nghiệm | [kafka-architecture-quiz.md](kafka-architecture-quiz.md) | [architecture-quiz/main.tex](architecture-quiz/main.tex) | [Đề](../output/pdf/kafka-architecture-quiz.pdf) |
| Lời giải | [kafka-architecture-solution.md](kafka-architecture-solution.md) | [architecture-solution/main.tex](architecture-solution/main.tex) | [Solution](../output/pdf/kafka-architecture-solution.pdf) |

## Nội dung

- **Bài lý thuyết** có khái niệm nền tảng, kiến trúc, topics/partitions, key và producer, replication/ISR, offsets, commit, retention và consumer groups. Ví dụ xuyên suốt là sự kiện đơn hàng.
- **Slide** (24 slide PowerPoint) dựng từ template `Template Format trình bày.pptx` ở thư mục gốc: trang bìa, slide Outline trước mỗi phần (4 section, section đang học được tô đậm, bên phải là hình minh họa của section) và các slide nội dung có tiêu đề là tên section, dòng ❖ là chủ đề slide. Bài giảng khoảng 60 phút. Các slide “Từ lab” dùng output thật của lượt chạy lab kiểm chứng. Ghi chú cho người dạy nằm trong phần Notes của từng slide, gồm câu hỏi gợi mở và đáp án phần kiểm tra nhanh, nên khi phát file cho học viên hãy dùng bản PDF.
- **Lab** dài 90 phút: phần bắt buộc (topic 3 partition, 60 record có key, hai và bốn consumer, group độc lập, lag, reset offset, replay) và phần mở rộng 20 phút với cluster 3 broker (ISR, đổi leader, `acks`, `min.insync.replicas`, ELR). Lab có bảng thời lượng, 8 bằng chứng cần nộp (E1–E8) và 8 câu hỏi (Q1–Q8).
- **Đề** có 10 câu, mỗi câu bốn lựa chọn và một đáp án đúng nhất. Solution có bảng đáp án và giải thích riêng.
- Ảnh gốc và sơ đồ nằm trong `assets/images/`. Metadata nguồn và SHA-256 nằm trong `assets/images/sources.json`. Dự án LaTeX lý thuyết có bản sao các ảnh để biên dịch độc lập; script dựng slide đọc ảnh trực tiếp từ `assets/images/`.

## Trạng thái kiểm chứng lab

Toàn bộ lab, kể cả phần mở rộng, đã chạy end-to-end ngày 10/11/2026 trên Windows 11, Windows PowerShell 5.1, Docker Engine 29.9.2 và `apache/kafka:4.1.2`. Ba phát hiện trong lượt chạy đã được đưa vào tài liệu:

1. Pipe dữ liệu từ PowerShell 5.1 vào `docker exec -i` gắn BOM vào key của record đầu tiên. Lab ghi file UTF-8 không BOM, chép vào container rồi để producer đọc file.
2. Cluster Kafka 4.1.2 mới tạo có ELR bật mặc định. Khi ISR nhỏ hơn `min.insync.replicas`, record gửi bằng `acks=1` được leader nhận nhưng chỉ đọc được sau khi ISR đạt lại ngưỡng. Bài đọc mô tả ví dụ `acks`/ISR với ELR tắt; lab và slide nêu rõ khác biệt này.
3. Console producer kết thúc với exit code 0 kể cả khi gửi lỗi (`NOT_ENOUGH_REPLICAS`), nên học viên phải đọc dòng `ERROR`.

## Chỉnh sửa và dựng lại

- **Lý thuyết:** chỉnh `kafka-architecture.md` rồi chạy `node kafka/architecture/build-from-markdown.mjs` để tạo lại `content.tex`.
- **Lab:** chỉnh `kafka-architecture-hands-on.md` rồi chạy `node kafka/architecture-lab/build-from-markdown.mjs`. Khối lệnh dùng fence `powershell`, khối kết quả dùng fence `text`; nội dung trong khối code phải là ASCII vì `listings` không dựng được tiếng Việt có dấu (script sẽ báo lỗi).
- **Slide:** nội dung, vị trí và ghi chú của từng slide nằm trong `architecture-slides/build_deck.py`. Script nhân bản ba slide mẫu của template nên logo, thanh tiêu đề, số trang và font Times New Roman giữ đúng như template. Chạy `python kafka/architecture-slides/build_deck.py` với một Python có `python-pptx`; kết quả ghi vào `output/kafka-architecture-slides.pptx`. Nếu sửa trực tiếp trong PowerPoint thì lần chạy script sau sẽ ghi đè, nên chỉ chọn một nơi để chỉnh. Trên trang bìa, nút Data&Code vẫn trỏ tới đường dẫn có sẵn trong template và dòng tác giả đang là “AI VIET NAM – AIO2026”; cần thay bằng thông tin của buổi học.
- **Câu hỏi và lời giải:** chỉnh `architecture-quiz/quiz-data.json` rồi chạy `node kafka/architecture-quiz/build-quiz.mjs`; script đồng bộ cả Markdown và TeX.

Hai script dựng lý thuyết và lab cần Node.js và thư viện `marked`. Nếu chỉ biên dịch các nguồn TeX đã có thì không cần Node.js.

## Biên dịch lại PDF

Máy cần MiKTeX hoặc TeX Live với `pdflatex` trên PATH. Từ thư mục workspace `slaivn`, chạy PowerShell:

```powershell
./kafka/build-pdfs.ps1
```

Script biên dịch các nguồn TeX đã lưu thành bốn PDF (bài đọc, lab, đề, solution) trong `output/pdf/`. Sau đó script dựng lại `output/kafka-architecture-slides.pptx` nếu tìm được Python có `python-pptx` (đặt `$env:PPTX_PYTHON` để chỉ định), rồi xuất `kafka-architecture-slides.pdf` bằng PowerPoint nếu máy có PowerPoint. Cuối cùng script tạo `output/kafka-architecture-latex.zip`. Log trung gian nằm trong `tmp/pdfs/`. Nếu sửa Markdown hoặc dữ liệu quiz, chạy script đồng bộ tương ứng trước khi biên dịch PDF.

Gói ZIP chứa các dự án LaTeX, file Markdown, file compose của lab, script dựng slide, file PowerPoint, ảnh/nguồn hình và script dựng. Nó có cả dự án solution và file PowerPoint có ghi chú (chứa đáp án phần kiểm tra nhanh), nên phù hợp để lưu trữ hoặc bàn giao cho người biên soạn. Khi phát cho học viên, chỉ dùng PDF bài đọc, PDF slide, lab và quiz.
