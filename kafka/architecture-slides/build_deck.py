"""Build the Kafka lecture deck from the AIO2026 PowerPoint template.

The template (workspace root, "Template Format trình bày.pptx") has three sample slides:
  1. title slide, 2. outline with four sections, 3. content slide (header bar, logo, page number).
Every slide here is a clone of one of those samples, so logo, header, fonts and numbering stay
exactly as in the template. Lab outputs are copied from kafka-architecture-hands-on.md
(verification run on 10/11/2026).

Run with a Python that has python-pptx and lxml:
  python kafka/architecture-slides/build_deck.py
Output: output/kafka-architecture-slides.pptx
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KAFKA = os.path.dirname(HERE)
WORKSPACE = os.path.dirname(KAFKA)
sys.path.insert(0, os.path.join(WORKSPACE, "shared"))

from aio_deck import *  # noqa: E402,F401,F403  (template helpers, colours, Deck)

IMAGES = os.path.join(KAFKA, "assets", "images")
OUTPUT = os.path.join(WORKSPACE, "output", "kafka-architecture-slides.pptx")


def IMG(name):
    return os.path.join(IMAGES, name)


SECTIONS = [
    "Kafka và kiến trúc",
    "Topic, partition và key",
    "Replication và ISR",
    "Offset và consumer group",
]
TOTAL_LABEL = "Tổng kết"


def build(template, out):
    d = Deck(template, SECTIONS)
    S1, S2, S3, S4 = SECTIONS

    # 1 ------------------------------------------------------------------ title
    d.title_slide(
        "Kiến trúc Apache Kafka",
        "Từ broker đến partition, replication và offset",
        "AI VIET NAM – AIO2026",
        "Buổi học khoảng 60 phút lý thuyết, sau đó là lab 90 phút. Nói rõ ngay từ đầu: mọi con số "
        "“Từ lab” trong slide là output thật của lượt chạy kiểm chứng ngày 10/11/2026 trên apache/kafka:4.1.2, "
        "không phải số minh họa. Thay nút Data&Code bằng đường dẫn tài liệu của buổi học.",
    )

    # 2 ------------------------------------------------------------------ goals
    s = d.content("Mục tiêu buổi học", "Sau buổi học, bạn có thể",
                  "Ví dụ xuyên suốt là sự kiện đơn hàng, trùng với bài đọc, quiz và lab. Học viên nên đọc trước "
                  "bài đọc nền tảng; slide chỉ giữ các ý chính.")
    goals = [
        ("Đọc", "một sơ đồ Kafka: producer, broker, controller, consumer"),
        ("Phân biệt", "partition với replica, Replicas với ISR"),
        ("Giải thích", "key ảnh hưởng thế nào đến partition và thứ tự"),
        ("Theo dõi", "tiến độ đọc bằng offset, committed offset và lag"),
        ("Lập luận", "vì sao consumer group có giới hạn mở rộng"),
    ]
    for i, (verb, rest) in enumerate(goals):
        y = 1.65 + i * 1.02
        box(s, 0.7, y, 0.75, 0.75, str(i + 1), fill=BLUE, line=BLUE, size=24, bold=True, color=WHITE,
            shape=MSO_SHAPE.OVAL, name=f"Goal {i + 1} number")
        label(s, 1.7, y + 0.13, 7.5, f"**{verb}** {rest}", size=20, align=PP_ALIGN.LEFT, h=0.5, name=f"Goal {i + 1}")
    callout(s, 9.4, 2.2, 3.4, 3.4,
            "**Tài liệu đi kèm**\n• Bài đọc nền tảng\n• Lab 90 phút\n• Quiz 10 câu\n\nMốc tài liệu: Apache Kafka 4.1",
            kind="key", size=18, name="Materials")

    # 3 ------------------------------------------------------------------ section 1
    d.outline(0, IMG("kafka-architecture-overview.png"),
              "Phần 1: vì sao cần Kafka và các thành phần chính. Hình bên phải sẽ được phân tích ở slide kiến trúc.")

    s = d.content(S1, "Đơn o1001 vừa được tạo. Ai cần biết?",
                  "Câu hỏi mở đầu: nếu dịch vụ thông báo ngừng 10 phút, mô hình bên trái xử lý thế nào? "
                  "Dẫn tới bốn câu hỏi của bài: sự kiện được lưu ở đâu, được chia ra thế nào, có bao nhiêu bản sao, "
                  "mỗi ứng dụng nhớ vị trí đọc bằng cách nào.")
    label(s, 0.5, 1.5, 5.6, "Gọi trực tiếp", size=20, color=ORANGE, bold=True)
    box(s, 0.6, 3.0, 2.0, 1.0, "Dịch vụ\nđơn hàng", size=16, name="Order service A")
    for i, nm in enumerate(["Tồn kho", "Thông báo", "Doanh thu"]):
        yy = 2.0 + i * 1.25
        box(s, 3.9, yy, 1.9, 0.8, nm, fill=WHITE, size=16, name=f"Direct target {i + 1}")
        arrow(s, 2.6, 3.5, 3.9, yy + 0.4, color=ORANGE, name=f"Direct call {i + 1}")
    label(s, 6.9, 1.5, 6.0, "Công bố sự kiện", size=20, color=GREEN, bold=True)
    box(s, 6.9, 3.0, 1.8, 1.0, "Dịch vụ\nđơn hàng", size=16, name="Order service B")
    box(s, 9.1, 2.95, 1.8, 1.1, "Kafka\n`order-events`", fill=RGBColor(0xDE, 0xEB, 0xF7), line=BLUE, size=16, bold=True, name="Kafka topic")
    arrow(s, 8.7, 3.5, 9.1, 3.5, name="Publish")
    for i, nm in enumerate(["Tồn kho", "Thông báo", "Doanh thu"]):
        yy = 2.0 + i * 1.25
        box(s, 11.3, yy, 1.6, 0.8, nm, fill=WHITE, size=16, name=f"Consumer {i + 1}")
        arrow(s, 10.9, 3.5, 11.3, yy + 0.4, name=f"Read {i + 1}")
    callout(s, 0.5, 5.75, 5.8, 1.25, "Thêm ứng dụng mới thì dịch vụ đơn hàng phải biết thêm một đích gọi. "
            "Một dịch vụ chậm thì phải chọn: chờ, thử lại hay bỏ qua.", kind="trap", name="Direct drawback")
    callout(s, 6.9, 5.75, 6.0, 1.25, "Mỗi ứng dụng tự đọc sự kiện theo tốc độ của mình, kể cả đọc lại. "
            "Xử lý nghiệp vụ vẫn do mã ứng dụng thực hiện.", kind="key", name="Event benefit")

    s = d.content(S1, "Kafka là gì? Một record gồm những gì?",
                  "Hai nhầm lẫn cần chặn sớm: (1) Kafka không xử lý nghiệp vụ; (2) timestamp của record khác với "
                  "trường nghiệp vụ occurred_at trong value. Producer gửi record, consumer đọc record; một ứng dụng "
                  "có thể đóng cả hai vai.")
    bullets(s, 0.5, 1.5, 6.3, 2.2, [
        ("plain", "**Apache Kafka** là nền tảng event streaming phân tán, làm ba việc:"),
        ("num", ("1", "nhận sự kiện do ứng dụng gửi đến;")),
        ("num", ("2", "lưu chúng theo cấu trúc có thứ tự;")),
        ("num", ("3", "cung cấp dữ liệu cho các ứng dụng đọc.")),
    ], size=18)
    table(s, 0.6, 3.95, [1.7, 4.4], [
        ["Thành phần", "Ví dụ"],
        ["Topic", "`order-events`"],
        ["Key", "`o1001` – gom theo đơn"],
        ["Value", "JSON sự kiện bên phải"],
        ["Timestamp", "Thời gian của record"],
    ], size=16, name="Record parts")
    end = code_box(s, 7.2, 1.55, 5.6, "Value: một sự kiện OrderCreated",
                   '{\n  "event_id": "e1001",\n  "event_type": "OrderCreated",\n  "order_id": "o1001",\n'
                   '  "total_amount": 450000,\n  "currency": "VND",\n  "occurred_at": "2026-11-02T09:00:00Z"\n}',
                   kind="cmd", size=14, name="Event JSON")
    callout(s, 7.2, end + 0.3, 5.6, 1.3, "JSON chỉ là một cách biểu diễn value. `OrderCreated` và `OrderPaid` "
            "của cùng đơn có `event_id` khác nhau nhưng **cùng key**.", kind="key", name="Key note")

    s = d.content(S1, "Producer, broker, controller và consumer",
                  "Mũi tên xanh là hướng dữ liệu; consumer chủ động gửi yêu cầu fetch, broker không đẩy dữ liệu đi. "
                  "Kafka 4.x chỉ dùng KRaft, không còn ZooKeeper. Một tiến trình có thể vừa là broker vừa là controller, "
                  "như cluster 3 node trong phần mở rộng của lab.")
    picture(s, IMG("kafka-architecture-overview.png"), 0.4, 1.5, 7.6, 5.3, name="Architecture overview")
    caption(s, 0.4, 6.85, 7.6, "Sơ đồ biên soạn cho bài học, dựa trên tài liệu thiết kế và KRaft của Apache Kafka 4.1.")
    bullets(s, 8.3, 1.55, 4.6, 3.6, [
        "**Broker**: tiến trình máy chủ lưu replica của partition, phục vụ đọc và ghi.",
        "**Cluster**: các broker phối hợp với nhau.",
        "**Controller (KRaft)**: quản lý metadata như thành viên cluster, leader của partition.",
        "Controller **không** là trạm trung chuyển mọi message.",
    ], size=17)
    callout(s, 8.3, 5.35, 4.6, 1.35, "Producer **gửi** · broker **lưu và phục vụ** · consumer **đọc và xử lý**.",
            kind="key", size=17, name="Three roles")

    # 2 ------------------------------------------------------------------ section 2
    d.outline(1, IMG("kafka-partition-log.png"),
              "Phần 2: dữ liệu được tổ chức thế nào bên trong một topic, và key quyết định điều gì.")

    s = d.content(S2, "Topic được chia thành partition; mỗi partition là một log",
                  "Hỏi lớp: offset có phải ID toàn cục của message không? Không. Thêm: thứ tự trong log không chứng minh "
                  "thứ tự thời gian nghiệp vụ; producer có thể gửi chậm hoặc thử lại, consumer có thể xử lý song song.")
    picture(s, IMG("kafka-partition-log.png"), 0.5, 1.6, 5.6, 4.0, name="Partition log")
    caption(s, 0.5, 5.7, 5.6, "Nguồn: Apache Kafka, hình log_anatomy.png (hình gốc).")
    table(s, 6.6, 1.65, [1.5, 1.2, 3.5], [
        ["Partition", "Offset", "Record"],
        ["P0", "0", "Tạo đơn `o1001`"],
        ["P0", "1", "Thanh toán `o1001`"],
        ["P1", "0", "Tạo đơn `o1002`"],
    ], size=16, name="Offsets table")
    bullets(s, 6.6, 3.55, 6.3, 1.9, [
        "Record mới luôn được bổ sung vào **cuối** log.",
        "Địa chỉ của record = **(topic, partition, offset)**.",
        "`P0/offset 0` và `P1/offset 0` là hai vị trí khác nhau.",
    ], size=17)
    callout(s, 0.5, 6.15, 12.4, 0.75, "Kafka giữ thứ tự **trong từng partition**, không ghép thành một thứ tự toàn cục cho topic.",
            kind="key", size=17, name="Ordering")

    s = d.content(S2, "Key quyết định record vào partition nào",
                  "Chọn key xuất phát từ yêu cầu thứ tự: cần thứ tự theo đơn thì key là order_id. Hot partition: một key "
                  "phát sinh quá nhiều sự kiện; thêm consumer không giải quyết được vì một partition chỉ thuộc một "
                  "consumer trong group.")
    picture(s, IMG("kafka-record-routing.png"), 0.4, 1.5, 6.0, 3.6, name="Record routing")
    caption(s, 0.4, 5.1, 6.0, "Nguồn: Apache Kafka, Introduction (hình gốc; Apache đặt tên P1–P4).")
    label(s, 6.8, 1.5, 6.1, "Cùng key → cùng partition, **khi giữ nguyên** số partition, cách serialize key và partitioner.",
          size=17, align=PP_ALIGN.LEFT, h=0.75, name="Key rule")
    table(s, 6.8, 2.45, [2.1, 4.0], [
        ["Key", "Điểm cần cân nhắc"],
        ["`order_id`", "Theo dõi vòng đời từng đơn"],
        ["`customer_id`", "Khách nhiều đơn có thể tạo tải lớn"],
        ["Giá trị cố định", "Dồn mọi record vào một partition"],
    ], size=16, name="Key choice")
    callout(s, 0.5, 5.6, 6.0, 1.3, "**Không key ≠ round robin.** Java producer mặc định chọn partition kiểu "
            "sticky, gắn với việc gom batch.", kind="trap", name="No key")
    callout(s, 6.8, 5.6, 6.1, 1.3, "**Tăng số partition** có thể đổi ánh xạ key → partition; record cũ "
            "không tự được phân bố lại.", kind="trap", name="More partitions")

    s = d.content(S2, "Từ lab: 60 record, 30 key, 3 partition",
                  "Output thật. Với cùng 30 key, cùng 3 partition và client Java mặc định, học viên sẽ thấy đúng 20/22/18. "
                  "Nếu khác, kiểm tra số lần gửi và lỗi BOM. Lỗi BOM là ví dụ tốt: “cùng key” phụ thuộc đúng chuỗi byte của key.")
    end = code_box(s, 0.5, 1.6, 5.4, "Đếm record theo partition (lab, phần 5)",
                   "Name Count\n---- -----\n0       20\n1       22\n2       18", size=16, name="Partition counts")
    code_box(s, 0.5, end + 0.3, 5.4, "Hai sự kiện của o0001",
             'Partition:0|Offset:0|o0001|{"event_type":\n  "OrderCreated",...}\nPartition:0|Offset:1|o0001|{"event_type":\n  "OrderPaid",...}',
             size=14, name="o0001 records")
    bullets(s, 6.4, 1.6, 6.5, 3.2, [
        "20/22/18, **không** phải 20/20/20: partitioner băm key, không chia lần lượt.",
        "Hai sự kiện của `o0001` cùng ở P0; `OrderCreated` có offset nhỏ hơn.",
        "Lượt đọc in P2 trước P0: thứ tự in giữa các partition không có ý nghĩa nghiệp vụ.",
    ], size=18)
    callout(s, 6.4, 5.0, 6.5, 1.6, "Lỗi gặp khi kiểm chứng: pipe từ PowerShell 5.1 gắn BOM vào key đầu tiên, biến "
            "`o0001` thành một key khác. Lab ghi file không BOM để tránh.", kind="trap", name="BOM")

    # 3 ------------------------------------------------------------------ section 3
    d.outline(2, IMG("kafka-partition-replication.png"),
              "Phần 3: bản sao của partition, tập ISR và điều kiện xác nhận ghi.")

    s = d.content(S3, "Partition khác replica",
                  "Câu hỏi nhanh: topic 6 partition, RF 2 có bao nhiêu replica? (12). Có bao nhiêu partition? (6).")
    picture(s, IMG("kafka-partition-replication.png"), 0.4, 1.5, 7.2, 5.0, name="Replication diagram")
    caption(s, 0.4, 6.55, 7.2, "3 partition, replication factor 3: 9 replica. Sơ đồ biên soạn theo mô hình replication của Kafka.")
    bullets(s, 7.9, 1.55, 5.0, 3.7, [
        "**Replica**: một bản sao của partition.",
        "**Replication factor**: số replica của mỗi partition, tính cả leader.",
        "Mỗi partition có một **leader** nhận ghi; **follower** sao chép log từ leader.",
        "Một broker có thể là leader của P0 và giữ follower của P1, P2.",
    ], size=17)
    callout(s, 7.9, 5.4, 5.0, 1.2, "3 partition × RF 3 = **9 replica**, nhưng vẫn chỉ có **3 partition** logic.",
            kind="key", size=17, name="Replica count")

    s = d.content(S3, "ISR: replica đang theo kịp leader",
                  "Output thật từ phần 10 của lab. Khi kafka-3 quay lại, nó bắt kịp và trở lại ISR; leader P2 chỉ trả về "
                  "broker 3 sau preferred leader election (tự động theo chu kỳ hoặc chạy kafka-leader-election.sh).")
    end = code_box(s, 0.5, 1.6, 7.0, "Lab mở rộng: 3 broker, trước khi dừng kafka-3",
                   "Partition: 0  Leader: 1  Replicas: 1,2,3  Isr: 1,2,3\n"
                   "Partition: 1  Leader: 2  Replicas: 2,3,1  Isr: 2,3,1\n"
                   "Partition: 2  Leader: 3  Replicas: 3,1,2  Isr: 3,1,2", size=15, name="ISR before")
    code_box(s, 0.5, end + 0.35, 7.0, "Sau docker stop kafka-3",
             "Partition: 0  Leader: 1  Replicas: 1,2,3  Isr: 1,2\n"
             "Partition: 1  Leader: 2  Replicas: 2,3,1  Isr: 2,1\n"
             "Partition: 2  Leader: 1  Replicas: 3,1,2  Isr: 1,2", size=15, name="ISR after")
    bullets(s, 7.9, 1.6, 5.0, 3.0, [
        "**ISR** (in-sync replicas): tập replica đang theo kịp leader theo tiêu chí của Kafka.",
        "`Replicas` không đổi: đó là danh sách **được gán**.",
        "P2 mất leader → broker 1 được bầu làm leader mới.",
    ], size=17)
    callout(s, 7.9, 4.9, 5.0, 1.7, "“Broker còn online” và “replica thuộc ISR” là hai thông tin khác nhau: replica "
            "còn chạy nhưng tụt lại vẫn có thể bị loại khỏi ISR.", kind="trap", name="ISR trap")

    s = d.content(S3, "acks và min.insync.replicas",
                  "Bài đọc giải thích ví dụ này với ELR tắt. Slide tiếp theo cho thấy Kafka 4.1.2 bật ELR mặc định và "
                  "điều đó thay đổi hành vi quan sát được.")
    table(s, 0.5, 1.6, [1.9, 4.3], [
        ["Cấu hình", "Producer chờ gì?"],
        ["`acks=0`", "Không chờ xác nhận"],
        ["`acks=1`", "Leader ghi vào log cục bộ"],
        ["`acks=all`", "Các replica trong ISR xác nhận"],
    ], size=17, name="acks table")
    label(s, 0.5, 3.6, 6.2, "`min.insync.replicas`: ngưỡng ISR tối thiểu để chấp nhận ghi khi producer dùng `acks=all`. "
          "Không phải số replica được tạo ra.", size=17, align=PP_ALIGN.LEFT, h=1.0, name="min ISR")
    label(s, 7.1, 1.6, 5.8, "Ví dụ: RF 3, `min.insync.replicas=2`, `acks=all`", size=18, color=BLUE, bold=True,
          align=PP_ALIGN.LEFT, h=0.45, name="Example title")
    states = [("ISR = 3", "chờ cả ba replica trong ISR", GREEN_LIGHT, GREEN),
              ("ISR = 2", "vẫn nhận ghi", GREEN_LIGHT, GREEN),
              ("ISR = 1", "từ chối: `NOT_ENOUGH_REPLICAS`", PEACH, ORANGE)]
    for i, (k, v, fill, line) in enumerate(states):
        yy = 2.2 + i * 0.85
        box(s, 7.1, yy, 1.6, 0.65, k, fill=fill, line=line, size=17, bold=True, name=f"ISR state {i + 1}")
        label(s, 8.85, yy + 0.12, 4.1, v, size=17, align=PP_ALIGN.LEFT, h=0.45, name=f"ISR outcome {i + 1}")
    callout(s, 0.5, 5.15, 12.4, 1.4, "`acks=all` liên quan đến ISR của partition, không phải mọi broker trong cluster. "
            "Producer nhận ack cũng chưa có nghĩa consumer đã xử lý xong.", kind="trap", name="acks trap")

    s = d.content(S3, "Từ lab: ISR thấp hơn ngưỡng tối thiểu",
                  "Console producer kết thúc với exit code 0 kể cả khi gửi lỗi, nên phải đọc dòng ERROR. Câu Q8 trong lab: "
                  "điều này nói gì về câu “producer nhận ack nghĩa là dữ liệu đã an toàn và sẵn sàng”? "
                  "kafka-features.sh describe cho thấy eligible.leader.replicas.version ở mức 1.")
    end = code_box(s, 0.5, 1.6, 7.2, "kafka-3 dừng, ISR = 2, min.insync.replicas=3, gửi acks=all",
                   "WARN ... retrying (0 attempts left).\n      Error: NOT_ENOUGH_REPLICAS\n"
                   "ERROR Error when sending message to topic\n      lab-replicated ...", size=14, name="acks all error")
    end = code_box(s, 0.5, end + 0.3, 7.2, "Gửi lại bằng acks=1, ngay sau đó xem offset cuối",
                   "lab-replicated:0:4", size=14, name="acks 1 offset")
    code_box(s, 0.5, end + 0.3, 7.2, "Sau docker start kafka-3, ISR trở lại 3",
             "lab-replicated:0:5", size=14, name="Recovered offset")
    bullets(s, 8.1, 1.6, 4.8, 3.3, [
        "`acks=all` bị từ chối đúng như lý thuyết.",
        "`acks=1` được leader xác nhận, nhưng consumer **chưa đọc được** record.",
        "Kafka 4.1.2 bật **ELR** mặc định: high watermark chỉ tăng khi ISR đạt `min.insync.replicas`.",
    ], size=17)
    callout(s, 8.1, 5.05, 4.8, 1.5, "Ba mốc khác nhau: producer nhận ack, record đọc được, nghiệp vụ xử lý xong.",
            kind="key", size=17, name="Three milestones")

    # 4 ------------------------------------------------------------------ section 4
    d.outline(3, IMG("kafka-consumer-groups.png"),
              "Phần 4: consumer nhớ vị trí đọc thế nào, và nhiều consumer chia việc ra sao.")

    s = d.content(S4, "Consumer position và committed offset",
                  "Nhận record chưa đồng nghĩa xử lý thành công. Auto commit không biến thao tác fetch thành xác nhận hoàn tất "
                  "nghiệp vụ. Producer idempotence xử lý phạm vi khác: bản ghi trùng do producer gửi lại; nó không làm việc trừ "
                  "kho ở hệ thống ngoài thành exactly-once.")
    x0, y0, cw = 1.6, 2.35, 0.95
    label(s, 0.6, y0 + 0.12, 0.9, "**P1**", size=20, name="Partition label")
    for i in range(10):
        fill = RGBColor(0xC5, 0xE0, 0xB4) if i < 5 else (PEACH_ACTIVE if i < 8 else WHITE)
        box(s, x0 + i * cw, y0, cw, 0.75, str(i), fill=fill, line=GREEN, size=18, name=f"Offset {i}",
            shape=MSO_SHAPE.RECTANGLE)
    label(s, x0, y0 - 0.5, 5 * cw, "đã xử lý xong", size=15, color=GREEN, bold=True, name="Done label")
    label(s, x0 + 5 * cw, y0 - 0.5, 3 * cw, "đã nhận, chưa commit", size=15, color=ORANGE, bold=True, name="Fetched label")
    arrow(s, x0 + 5.5 * cw, y0 + 1.45, x0 + 5.5 * cw, y0 + 0.8, color=BLUE, name="Committed arrow")
    label(s, x0 + 4.4 * cw, y0 + 1.45, 2.2 * cw, "committed offset = 5", size=15, color=BLUE, bold=True, h=0.6, name="Committed label")
    arrow(s, x0 + 8.5 * cw, y0 + 1.45, x0 + 8.5 * cw, y0 + 0.8, color=ORANGE, name="Position arrow")
    label(s, x0 + 7.6 * cw, y0 + 1.45, 1.9 * cw, "position = 8", size=15, color=ORANGE, bold=True, name="Position label")
    arrow(s, x0 + 10.55 * cw, y0 - 0.35, x0 + 10.05 * cw, y0 + 0.2, color=GREEN, name="LEO arrow")
    label(s, x0 + 9.7 * cw, y0 - 0.75, 2.4 * cw, "log-end offset = 10", size=15, color=GREEN, bold=True, name="LEO label")
    bullets(s, 0.5, 4.5, 6.3, 2.4, [
        "**Position**: offset của record tiếp theo consumer sẽ nhận.",
        "**Committed offset**: mốc đã lưu để group đọc tiếp khi khôi phục.",
        "Committed offset là **vị trí tiếp theo cần đọc**: xử lý xong 0–4 thì commit **5**.",
    ], size=17)
    callout(s, 7.2, 4.6, 5.7, 2.1, "Nếu consumer dừng lúc này, group đọc lại từ 5: record 5, 6, 7 có thể được "
            "**xử lý lần nữa**. Ứng dụng cần **idempotency**, ví dụ ghi nhận `event_id` đã xử lý.",
            kind="trap", size=17, name="Duplicates")

    s = d.content(S4, "Consumer lag, retention và replay",
                  "Lag tăng liên tục gợi ý tốc độ xử lý thấp hơn tốc độ phát sinh dữ liệu; cần xem thêm thời gian xử lý và hệ "
                  "thống đích. auto.offset.reset=earliest chỉ áp dụng khi group không có committed offset hợp lệ. "
                  "Câu Q6 trong lab: replay ở đây gây hậu quả gì với ứng dụng tồn kho thật?")
    end = code_box(s, 0.5, 1.6, 7.3, "Lab, phần 9: dừng consumer, gửi thêm 10 đơn",
                   "PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG\n"
                   "0          21              22              1\n"
                   "1          22              25              3\n"
                   "2          19              25              6", size=16, name="Lag output")
    end = code_box(s, 0.5, end + 0.3, 7.3, "Đặt lại committed offset rồi đọc lại",
                   "kafka-consumer-groups.sh --group lab-stock\n"
                   "  --topic lab-order-events --reset-offsets\n"
                   "  --to-earliest --dry-run   (rồi --execute)", kind="cmd", size=16, name="Reset command")
    code_box(s, 0.5, end + 0.3, 7.3, "Kết quả", "Processed a total of 72 messages   (60 + 2 + 10)", size=16, name="Replay output")
    bullets(s, 8.2, 1.6, 4.7, 5.0, [
        "**Lag** = log-end offset − committed offset, theo từng partition. Ở đây 1 + 3 + 6 = 10.",
        "Lag tính bằng offset, **không** bằng giây.",
        "Commit **không** xóa record; retention của topic quyết định việc dọn dữ liệu.",
        "**Replay** chỉ đọc lại được dữ liệu còn trong log.",
    ], size=17)

    s = d.content(S4, "Một partition thuộc một consumer trong group",
                  "Đây là mô hình consumer group thông thường (KafkaConsumer), không bao gồm share groups. Không nên giả định "
                  "“C1 luôn đọc P0” để lưu trạng thái nghiệp vụ.")
    picture(s, IMG("kafka-consumer-groups.png"), 0.4, 1.55, 6.4, 3.8, name="Consumer groups")
    caption(s, 0.4, 5.35, 6.4, "Nguồn: Apache Kafka, hình consumer-groups.png (hình gốc).")
    table(s, 7.1, 1.6, [1.6, 4.2], [
        ["Số consumer", "Phân công (3 partition)"],
        ["1", "C1: P0, P1, P2"],
        ["2", "C1: P0, P1; C2: P2"],
        ["3", "Mỗi consumer một partition"],
        ["4", "Một consumer không có partition"],
    ], size=16, name="Assignment table")
    bullets(s, 7.1, 4.0, 5.8, 1.7, [
        "Nhiều **group** đọc cùng topic độc lập, mỗi group có tiến độ riêng.",
        "**Rebalance**: phân công lại khi thành viên, subscription hoặc số partition thay đổi.",
    ], size=16)
    callout(s, 0.5, 5.85, 12.4, 0.85, "Thêm consumer vượt số partition không tăng thêm số bên đọc song song cho topic trong cùng group.",
            kind="key", size=17, name="Scaling limit")

    s = d.content(S4, "Từ lab: hai, rồi bốn consumer trong lab-stock",
                  "Bằng chứng phân công là output --members --verbose, không phải lượng dữ liệu in ra màn hình. "
                  "--from-beginning chỉ có tác dụng khi group chưa có committed offset.")
    end = code_box(s, 0.5, 1.6, 7.0, "Hai consumer",
                   "CLIENT-ID  #PARTITIONS  CURRENT-ASSIGNMENT\n"
                   "stock-c1   2            lab-order-events:0,1\n"
                   "stock-c2   1            lab-order-events:2", size=16, name="Two consumers")
    code_box(s, 0.5, end + 0.35, 7.0, "Bốn consumer, sau rebalance",
             "CLIENT-ID  #PARTITIONS  CURRENT-ASSIGNMENT\n"
             "stock-c1   1            lab-order-events:0\n"
             "stock-c3   1            lab-order-events:2\n"
             "stock-c4   0            -\n"
             "stock-c2   1            lab-order-events:1", size=16, name="Four consumers")
    bullets(s, 7.9, 1.6, 5.0, 5.0, [
        "`stock-c2` được giao P2 nhưng **không in record nào**: c1 đã đọc và commit hết 60 record trước khi c2 tham gia.",
        "Với bốn consumer, `stock-c4` có **0 partition**.",
        "`stock-c2` chuyển từ P2 sang P1 sau rebalance.",
        "Group `lab-analytics-01` vẫn đọc đủ 62 record.",
    ], size=17)

    # 5 ------------------------------------------------------------------ wrap-up
    s = d.content(TOTAL_LABEL, "Theo dấu record o1001",
                  "P1 và offset 7 là giả định để dễ theo dõi, không phải kết quả tính hash.")
    table(s, 0.5, 1.55, [0.8, 7.4, 4.2], [
        ["Bước", "Điều diễn ra", "Khái niệm"],
        ["1", "Dịch vụ đơn hàng tạo record key `o1001`", "Producer, key, value"],
        ["2", "Producer chọn partition đích, giả định P1", "Topic, partitioner"],
        ["3", "Leader của P1 ghi record ở offset 7 (giả định)", "Leader, log, offset"],
        ["4", "Follower sao chép; producer nhận ack theo cấu hình", "Replica, ISR, `acks`"],
        ["5", "Consumer được giao P1 trong group tồn kho fetch và xử lý", "Consumer group"],
        ["6", "Xử lý xong đến offset 7, ứng dụng commit **8**", "Committed offset"],
        ["7", "Group phân tích đọc theo tiến độ riêng", "Group độc lập, replay"],
    ], size=16, name="Trace table", row_h=0.5)
    callout(s, 0.5, 5.9, 12.4, 0.8, "Ba loại tiến độ: **Kafka xác nhận ghi**, **consumer đã nhận**, **nghiệp vụ đã xong**.",
            kind="key", size=17, name="Progress types")

    s = d.content(TOTAL_LABEL, "Những điểm dễ nhầm",
                  "Có thể cho lớp bỏ phiếu đúng/sai cho từng dòng bên trái trước khi nói cột phải.")
    table(s, 0.5, 1.55, [6.2, 6.2], [
        ["Dễ nhầm", "Phù hợp"],
        ["3 partition, RF 3 là 9 partition", "3 partition logic, 9 replica"],
        ["Cùng offset là cùng message", "Offset chỉ có nghĩa trong partition của nó"],
        ["Không key thì luôn round robin", "Tùy client; Java mặc định dùng sticky"],
        ["`acks=all`: mọi broker xác nhận", "Liên quan đến ISR của partition"],
        ["Commit offset 7 là xử lý xong record 7", "Xử lý xong đến 7 thì commit 8"],
        ["Commit xong thì record bị xóa", "Retention quyết định việc dọn dữ liệu"],
        ["Thêm consumer luôn nhanh hơn", "Số partition giới hạn số bên đọc song song"],
    ], size=16, header_fill=ORANGE, name="Misconceptions", row_h=0.6)

    s = d.content(TOTAL_LABEL, "Kiểm tra nhanh",
                  "Đáp án: (1) 12 replica. (2) 1 consumer. (3) 10, vị trí tiếp theo cần đọc. (4) Không nhất thiết: lag đo "
                  "committed offset; nếu commit trước khi xử lý xong, hoặc auto commit theo tiến độ đọc, lag có thể bằng 0 "
                  "trong khi việc trừ kho chưa xong. (5) Không ảnh hưởng: mỗi group có committed offset riêng. "
                  "Các câu ở đây không trùng quiz chính thức.")
    qs = [
        "Topic có 6 partition, replication factor 2. Có bao nhiêu replica?",
        "Group có 3 consumer đọc một topic 2 partition. Bao nhiêu consumer không có partition?",
        "Ứng dụng xử lý xong offset 0–9 ở P0. Nên commit giá trị nào?",
        "**LAG = 0** có chứng minh ứng dụng tồn kho đã cập nhật xong mọi đơn không?",
        "Hai group đọc cùng topic. Group A commit offset 50 có ảnh hưởng gì đến group B?",
    ]
    for i, q in enumerate(qs):
        yy = 1.65 + i * 1.02
        box(s, 0.7, yy, 0.75, 0.75, f"Q{i + 1}", fill=ORANGE, line=ORANGE, size=18, bold=True, color=WHITE,
            shape=MSO_SHAPE.OVAL, name=f"Question {i + 1} badge")
        label(s, 1.7, yy + 0.13, 11.2, q, size=20, align=PP_ALIGN.LEFT, h=0.5, name=f"Question {i + 1}")

    s = d.content(TOTAL_LABEL, "Đọc một sơ đồ Kafka bằng sáu câu hỏi",
                  "Nhắc học viên kéo image apache/kafka:4.1.2 trước buổi lab để tránh mạng chậm trong lớp.")
    six = ["Ứng dụng nào phát sự kiện?", "Dữ liệu vào topic nào?", "Key phân phối record ra sao?",
           "Partition được sao chép ở đâu?", "Consumer chia nhóm thế nào?", "Tiến độ được commit khi nào?"]
    for i, q in enumerate(six):
        col, row = i % 2, i // 2
        box(s, 0.5 + col * 3.85, 1.65 + row * 1.6, 3.6, 1.3, f"**{i + 1}.** {q}", fill=WHITE, line=BLUE, size=18,
            name=f"Diagram question {i + 1}")
    callout(s, 8.4, 1.65, 4.5, 4.5,
            "**Tiếp theo: lab 90 phút**\n• Topic 3 partition, 60 record có key\n• Hai và bốn consumer trong một group\n"
            "• Lag, reset offset, replay\n• Mở rộng: 3 broker, ISR, `acks`\n\nChuẩn bị: Docker Desktop đang chạy, "
            "image `apache/kafka:4.1.2`.", kind="key", size=17, name="Lab preview")
    caption(s, 0.5, 6.6, 7.6, "Tài liệu: bài đọc “Kiến trúc Apache Kafka”, hướng dẫn hands-on, quiz 10 câu. Tham chiếu: kafka.apache.org/41")

    d.finish(out)
    return len(d.prs.slides)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else OUTPUT
    n = build(find_template(WORKSPACE), out)
    print(f"Wrote {out} ({n} slides)")
