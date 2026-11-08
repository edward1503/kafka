# Bộ bài học: Kiến trúc Apache Kafka

Bộ file sử dụng cách tách nội dung như bài Databricks: lý thuyết, hands-on, đề trắc nghiệm và solution là các tài liệu riêng. Ba tài liệu lý thuyết/quiz/solution có dự án LaTeX độc lập theo template AIO2026 và bản PDF; lab hiện ở định dạng Markdown.

## Các file để đọc và chỉnh sửa

| Tài liệu | Markdown | Dự án LaTeX | PDF |
| --- | --- | --- | --- |
| Bài lý thuyết | [kafka-architecture.md](kafka-architecture.md) | [architecture/main.tex](architecture/main.tex) | [Bài đọc](../output/pdf/kafka-architecture.pdf) |
| Lab | [kafka-architecture-hands-on.md](kafka-architecture-hands-on.md) | Chưa tạo, cùng cách tách của bộ Databricks | Chưa tạo |
| Đề trắc nghiệm | [kafka-architecture-quiz.md](kafka-architecture-quiz.md) | [architecture-quiz/main.tex](architecture-quiz/main.tex) | [Đề](../output/pdf/kafka-architecture-quiz.pdf) |
| Lời giải | [kafka-architecture-solution.md](kafka-architecture-solution.md) | [architecture-solution/main.tex](architecture-solution/main.tex) | [Solution](../output/pdf/kafka-architecture-solution.pdf) |

## Nội dung và nguồn chỉnh sửa

- Bài lý thuyết có khái niệm nền tảng, kiến trúc, topics/partitions, key và producer, replication/ISR, offsets, commit, retention và consumer groups. Ví dụ xuyên suốt là sự kiện đơn hàng.
- Đề có 10 câu, mỗi câu bốn lựa chọn và một đáp án đúng nhất. Câu 1–6 ôn kiến thức nền; câu 7–10 yêu cầu phân tích tình huống thực tế. Solution có bảng đáp án và giải thích riêng.
- Lab hướng dẫn dùng image Apache Kafka 4.1.2, tạo topic 3 partition, gửi 60 record có key và quan sát phân phối/assignment/lag. Lab một broker dùng replication factor 1, chưa kiểm chứng end-to-end trên máy hiện tại; các kết quả trong lab được ghi là kỳ vọng.
- Ảnh gốc và sơ đồ nằm trong `assets/images/`. Metadata nguồn và SHA-256 nằm trong `assets/images/sources.json`. Dự án LaTeX lý thuyết có bản sao các ảnh để biên dịch độc lập.

Để sửa lý thuyết, chỉnh `kafka-architecture.md` rồi chạy `architecture/build-from-markdown.mjs` để tạo lại `content.tex`. Để sửa câu hỏi và lời giải, chỉnh `architecture-quiz/quiz-data.json` rồi chạy `architecture-quiz/build-quiz.mjs`; script đồng bộ cả Markdown và TeX.

Hai script tạo nội dung cần Node.js và thư viện `marked` cho script lý thuyết. Nếu chỉ biên dịch các nguồn TeX đã có thì không cần Node.js. Mỗi dự án có `main.tex`, `style.tex` và các file phụ cần thiết; ảnh trong TeX dùng đường dẫn tương đối.

## Biên dịch lại PDF

Máy cần MiKTeX hoặc TeX Live với `pdflatex` trên PATH. Từ thư mục workspace `slaivn`, chạy PowerShell:

```powershell
./kafka/build-pdfs.ps1
```

Script biên dịch các nguồn TeX đã lưu, xuất ba PDF vào `output/pdf/` và tạo `output/kafka-architecture-latex.zip`. Log trung gian nằm trong `tmp/pdfs/`. Nếu sửa Markdown hoặc dữ liệu quiz, chạy script đồng bộ tương ứng trước khi biên dịch PDF.

Gói ZIP chứa ba dự án LaTeX, bốn file Markdown, ảnh/nguồn hình và script dựng. Nó không chứa đáp án trong file đề, nhưng có cả dự án solution riêng nên phù hợp để lưu trữ hoặc bàn giao cho người biên soạn. Khi phát đề cho học viên, chỉ dùng PDF quiz.
