# Kiến trúc Apache Kafka

Brokers, topic, partition, replication, offset và consumer groups. Bộ tài liệu tiếng Việt dùng ví dụ đơn hàng.

| Tài liệu | Markdown | PDF |
| --- | --- | --- |
| Lý thuyết | [Bài đọc](kafka/kafka-architecture.md) | [PDF](output/pdf/kafka-architecture.pdf) |
| Hands-on | [Hướng dẫn](kafka/kafka-architecture-hands-on.md) | |
| Quiz | [Đề có sơ đồ](kafka/kafka-architecture-quiz.md) | [PDF](output/pdf/kafka-architecture-quiz.pdf) |
| Lời giải | [Đáp án và giải thích](kafka/kafka-architecture-solution.md) | [PDF](output/pdf/kafka-architecture-solution.pdf) |

[Gói nguồn LaTeX](output/kafka-architecture-latex.zip) · [Template AIO2026](Template%20Reading/template.tex)

Các dự án LaTeX, ảnh và tài liệu nguồn nằm trong thư mục [kafka/](kafka/). Mở file main.tex trong từng dự án và dùng pdflatex để biên dịch. Khi cần tạo lại nội dung từ Markdown, cài marked và sharp bằng lệnh npm install --no-save marked sharp rồi chạy script mjs tương ứng.

[Hướng dẫn dựng lại bộ Kafka](kafka/README.md)
