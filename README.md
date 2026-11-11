# Kiến trúc Apache Kafka

Brokers, topic, partition, replication, offset và consumer groups. Bộ tài liệu tiếng Việt dùng ví dụ đơn hàng.

| Tài liệu | Nguồn | Bản phát hành |
| --- | --- | --- |
| Lý thuyết | [Bài đọc](kafka/kafka-architecture.md) | [PDF](output/pdf/kafka-architecture.pdf) |
| Slide bài giảng | [Script dựng slide](kafka/architecture-slides/build_deck.py) | [PowerPoint](output/kafka-architecture-slides.pptx) · [PDF](output/pdf/kafka-architecture-slides.pdf) |
| Lab 90 phút | [Hướng dẫn](kafka/kafka-architecture-hands-on.md) · [Docker Compose 3 broker](kafka/lab/docker-compose.replication.yml) | [PDF](output/pdf/kafka-architecture-lab.pdf) |
| Quiz | [Đề có sơ đồ](kafka/kafka-architecture-quiz.md) | [PDF](output/pdf/kafka-architecture-quiz.pdf) |
| Lời giải | [Đáp án và giải thích](kafka/kafka-architecture-solution.md) | [PDF](output/pdf/kafka-architecture-solution.pdf) |

[Gói nguồn](output/kafka-architecture-latex.zip) · [Template AIO2026](Template%20Reading/template.tex)

Lab đã được chạy end-to-end với `apache/kafka:4.1.2` trên Docker, kể cả phần mở rộng 3 broker; các khối “Kết quả quan sát” trong hướng dẫn là output thật của lượt chạy đó. Slide PowerPoint có ghi chú cho người dạy trong phần Notes (gồm đáp án phần kiểm tra nhanh); khi phát cho học viên, dùng bản PDF.

Các dự án LaTeX, ảnh và tài liệu nguồn nằm trong thư mục [kafka/](kafka/). Mở file main.tex trong từng dự án và dùng pdflatex để biên dịch. Khi cần tạo lại nội dung từ Markdown, cài marked bằng lệnh `npm install --no-save marked` rồi chạy script mjs tương ứng. Script dựng slide cần Python có `python-pptx` và file template trình bày AIO2026 (`Template Format trình bày.pptx`) đặt ở thư mục gốc; template này không nằm trong repo.

[Hướng dẫn dựng lại bộ Kafka](kafka/README.md)
