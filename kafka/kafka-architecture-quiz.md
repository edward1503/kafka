# Quiz trắc nghiệm: Kiến trúc Apache Kafka

**Hình thức:** 10 câu hỏi, mỗi câu có bốn lựa chọn A/B/C/D. Chọn một đáp án đúng nhất cho mỗi câu. Câu 7–10 yêu cầu phân tích tình huống.

**Bài đọc nền tảng:** [Kiến trúc Apache Kafka](kafka-architecture.md).

**Phạm vi:** mốc tài liệu Kafka 4.1; consumer group là nhóm KafkaConsumer thông thường, không bao gồm share groups.

## Câu 1

Trong luồng sự kiện đơn hàng, phát biểu nào mô tả đúng trách nhiệm của các thành phần Kafka?

A. Producer lưu mọi replica; broker cập nhật tồn kho; consumer quản lý metadata cluster.

B. Producer phân công consumer; broker chỉ lưu committed offset; consumer ghi mọi partition.

C. Producer gửi record; broker lưu và phục vụ dữ liệu; consumer đọc và thực hiện xử lý.

D. Producer gửi mọi record qua controller; consumer chỉ được đọc sau khi controller xử lý nghiệp vụ.

## Câu 2

Topic order-events có ba partition. Nhận định nào đúng về thứ tự và offset?

A. Mỗi partition có thứ tự log riêng; offset 7 ở P0 và offset 7 ở P1 là hai vị trí khác nhau.

B. Kafka sắp mọi record trong cả topic theo một dãy offset duy nhất.

C. Record có timestamp nhỏ hơn luôn hoàn tất xử lý trước, bất kể partition.

D. Offset 7 của hai partition luôn chứa cùng một record vì đó là mã định danh toàn cục.

## Câu 3

Producer phân vùng theo key, giữ nguyên số partition, cách serialize key và thuật toán phân vùng. Các sự kiện cùng key o1001 sẽ có đặc điểm nào?

A. Luôn được chia đều sang mọi partition để tăng tốc xử lý một đơn hàng.

B. Luôn ở partition 0 vì Kafka chỉ dùng key để lọc dữ liệu khi đọc.

C. Tạo một partition mới cho từng sự kiện có cùng key.

D. Được đưa vào cùng một partition theo chiến lược phân vùng đã nêu.

## Câu 4

Với Java producer mặc định ở mốc Kafka 4.1, nên giải thích thế nào khi một batch nhỏ không có key phân bố không đều giữa các partition?

A. Kafka chắc chắn bị lỗi vì mọi ba record phải đi lần lượt qua P0, P1 và P2.

B. Producer có cơ chế sticky gắn với batching; không nên giả định round robin cho từng record.

C. Record không có key luôn được ghi đồng thời vào mọi partition của topic.

D. Consumer group quyết định partition của record ngay trước mỗi lần producer gửi.

## Câu 5

Một topic có 3 partition và replication factor bằng 3. Cách đếm nào đúng?

A. Có 9 partition logic và 3 replica tổng cộng.

B. Có 3 partition logic và 12 replica vì leader không được tính vào replication factor.

C. Có 3 partition logic và 9 replica tổng cộng, trong đó có 3 leader.

D. Có 1 partition logic và 3 leader cùng nhận ghi cho partition đó.

## Câu 6

Giả sử ELR không bật, replication factor 3, ISR hiện có 3 replica, min.insync.replicas=2 và producer dùng acks=all. Phát biểu nào đúng?

A. Chỉ cần leader ghi xong; acks=all bỏ qua follower khi min.insync.replicas nhỏ hơn 3.

B. Ngưỡng 2 kiểm tra ISR tối thiểu; acks=all chờ ISR hiện tại, không chỉ hai replica bất kỳ.

C. Lần ghi chỉ thành công sau khi mọi consumer group commit offset của record.

D. min.insync.replicas=2 làm Kafka giảm replication factor của topic xuống 2.

## Vận dụng: phân tích tình huống

## Câu 7

Nhóm quan sát lag theo partition như trong sơ đồ và cần giữ thứ tự cho key có lưu lượng lớn.

![Group stock · mỗi consumer phụ trách một partition. P0 → Consumer 0, Lag quanh 20. P1 → Consumer 1, Lag 500 → 8.000. P2 → Consumer 2, Lag quanh 20. Khoảng quan sát 15 phút. Mẫu record cho thấy một key chiếm phần lớn lưu lượng vào P1.](<architecture-quiz/Figures/case-7.png>)

Bước xử lý đầu tiên hợp lý nhất là gì?

A. Thêm consumer thứ tư để hai consumer cùng sở hữu P1 trong group hiện tại.

B. Tăng replication factor để follower chia đôi phần việc đọc P1 của group.

C. Đo thời gian xử lý và kiểm tra hệ thống đích của consumer P1; xem lại tải của key nóng trước khi đổi cách phân vùng.

D. Đổi toàn bộ key sang giá trị ngẫu nhiên để dàn tải, rồi giữ nguyên giả định thứ tự theo key.

## Câu 8

Nhóm đang thiết kế consumer group cho hai pipeline có yêu cầu như trong sơ đồ.

![Hai pipeline cùng đọc topic order-events · 6 partition. Tồn kho, Hai instance chia việc, Xử lý mỗi đơn. Báo cáo, Một pipeline đọc toàn bộ, Cần replay dữ liệu còn lưu. Yêu cầu khi replay báo cáo là giữ nguyên tiến độ xử lý của tồn kho.](<architecture-quiz/Figures/case-8.png>)

Kiến trúc nào đáp ứng đồng thời việc chia tải và đọc độc lập?

A. Dùng hai instance cùng group `stock`; báo cáo dùng group khác và chọn vị trí replay riêng của báo cáo.

B. Đưa cả ba instance vào group `stock`, rồi cho báo cáo chạy từ đầu khi cần.

C. Cho từng instance tồn kho một group riêng; dựa vào replication factor để tránh xử lý trùng giữa chúng.

D. Tăng số replica và giữ một group chung; mỗi follower tự lưu offset riêng cho từng pipeline.

## Câu 9

Producer gặp lỗi khi ghi P2. Sơ đồ thể hiện cấu hình topic và trạng thái từng replica.

![Topic payments · RF = 3 · min.insync.replicas = 2 · acks = all · ELR tắt. P2 · Leader, Đang hoạt động, Trong ISR. P2 · Follower A, Mất kết nối, Ngoài ISR. P2 · Follower B, Tụt lại, Ngoài ISR. Các partition khác vẫn ghi được.](<architecture-quiz/Figures/case-9.png>)

Kết luận và hướng khôi phục nào phù hợp nếu phải giữ chính sách xác nhận hiện tại?

A. P2 vẫn ghi thành công vì replication factor trên cấu hình vẫn là 3; chỉ cần tăng timeout producer.

B. P2 không đáp ứng ngưỡng ISR; khôi phục ít nhất một follower và xác nhận ISR trở lại từ 2 thành viên trước khi kỳ vọng lần ghi thành công.

C. Cần thêm consumer cho P2 để consumer gửi xác nhận thay follower.

D. Hạ `min.insync.replicas` xuống 1; như vậy vẫn giữ nguyên yêu cầu có ít nhất hai replica theo kịp.

## Câu 10

Consumer tồn kho gặp sự cố tại thời điểm trong sơ đồ.

![P1 · xử lý theo thứ tự · committed offset = 41. Fetch, Record 41 và 42. Giao dịch tồn kho, Record 41 đã trừ kho. Tiến trình dừng, 42 chưa xử lý, Chưa commit offset mới. Hai record còn trong Kafka. Mỗi sự kiện có event_id duy nhất. Cơ sở dữ liệu hỗ trợ giao dịch.](<architecture-quiz/Figures/case-10.png>)

Thiết kế nào cho phép phục hồi mà không bỏ sót 42 hoặc trừ kho hai lần cho 41?

A. Khi khởi động lại, luôn seek đến offset 43 vì cả hai record đã được fetch trước khi lỗi.

B. Bật producer idempotence rồi tiếp tục trừ kho vô điều kiện cho mọi record được đọc lại.

C. Commit offset 43 ngay sau khi poll; nếu trừ kho thất bại thì chờ Kafka tự phát lại.

D. Đọc lại từ mốc 41, ghi dấu `event_id` và cập nhật tồn kho trong cùng giao dịch khi xử lý mới; bỏ qua tác động đã ghi nhận rồi commit đến vị trí tiếp theo sau khi xử lý xong.
