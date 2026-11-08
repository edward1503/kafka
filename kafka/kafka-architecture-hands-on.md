# Hands-on: Kiến trúc Apache Kafka

*Tạo topic nhiều partition và quan sát cách phân phối message*

**Bài đọc nền tảng:** [Kiến trúc Apache Kafka](kafka-architecture.md).

**Mục tiêu:** khởi động Kafka cho một bài thực hành cục bộ, tạo topic có 3 partition, gửi các sự kiện có key, kiểm tra partition/offset và quan sát cách consumer group chia việc.

**Môi trường:** Windows, PowerShell và Docker Desktop chạy Linux containers. Các lệnh Kafka chạy trong container, nên không cần cài Java hoặc Kafka trực tiếp trên Windows.

> **Trạng thái:** đây là bản hướng dẫn thực hành, chưa được chạy end-to-end trên máy hiện tại vì Docker engine chưa hoạt động khi soạn. Các kết quả bên dưới là điều cần kiểm tra hoặc kết quả kỳ vọng, không phải log hay ảnh chụp của một lần chạy đã hoàn tất. Image được cố định ở `apache/kafka:4.1.2`, cùng nhánh tài liệu 4.1 của bài lý thuyết.

## 1. Hiểu mô hình lab trước khi chạy

Lab dùng một container có tên `kafka-architecture-lab`. Topic `lab-order-events` có **3 partition**, nhưng **replication factor bằng 1** vì môi trường chỉ có một broker.

| Thành phần | Giá trị dùng trong lab |
| --- | --- |
| Docker image | `apache/kafka:4.1.2` |
| Container | `kafka-architecture-lab` |
| Bootstrap server trong container | `localhost:9092` |
| Topic | `lab-order-events` |
| Partition | 3 |
| Replication factor | 1 |
| Key của record | `order_id` |
| Dữ liệu ban đầu | 30 đơn, mỗi đơn có hai sự kiện, tổng cộng 60 record |

Mô hình này phù hợp để quan sát partition, key, offset và group assignment. Nó chưa kiểm chứng replication giữa nhiều broker hoặc khả năng chịu lỗi khi mất broker. Phần replication factor 3 trong bài lý thuyết là mô hình khác.

## 2. Chuẩn bị Docker và khởi động Kafka

Mở Docker Desktop, chờ engine sẵn sàng rồi mở PowerShell. Chạy:

```powershell
docker version
```

Cần có thông tin **Server**, không chỉ Client. Nếu có lỗi kết nối Docker API hoặc named pipe, quay lại Docker Desktop trước khi chạy các bước tiếp theo.

Tải image và tạo container theo cách khởi động Docker trong [Kafka Quick Start][quickstart]:

```powershell
docker pull apache/kafka:4.1.2
docker run -d --name kafka-architecture-lab -p 127.0.0.1:9092:9092 apache/kafka:4.1.2
docker ps --filter name=kafka-architecture-lab
```

Nếu tên container đã được dùng từ lần trước, kiểm tra container đó bằng `docker ps -a --filter name=kafka-architecture-lab`. Dùng `docker start kafka-architecture-lab` nếu muốn tiếp tục dữ liệu cũ; một lượt lab mới cần topic hoặc môi trường mới để giữ đúng số lượng record.

Kiểm tra broker đã nhận yêu cầu được chưa:

```powershell
docker exec kafka-architecture-lab /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

Lệnh thành công nhưng chưa có topic lab là bình thường. Nếu Kafka còn khởi động, xem log và thử lại sau khi server sẵn sàng:

```powershell
docker logs --tail 60 kafka-architecture-lab
```

**Điểm kiểm tra:** container đang chạy và lệnh liệt kê topic không còn báo lỗi kết nối broker.

## 3. Tạo topic với ba partition

```powershell
docker exec kafka-architecture-lab /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic lab-order-events --partitions 3 --replication-factor 1
docker exec kafka-architecture-lab /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic lab-order-events
```

Không dùng `--if-not-exists` ở đây để tránh vô tình tiếp tục trên topic đã chứa dữ liệu cũ. Nếu topic đã tồn tại, dùng tên mới và thay nhất quán trong các lệnh còn lại.

Trong kết quả `--describe`, cần kiểm tra:

- `PartitionCount` là 3; có các partition 0, 1 và 2.
- `ReplicationFactor` là 1.
- Mỗi partition có một leader; chỉ một broker ID trong `Replicas` và `Isr`.

Broker ID cụ thể phụ thuộc cấu hình image; không cần nó phải bằng một giá trị cố định. Xem [các thao tác với topic][operations].

**Ảnh nên lưu khi tự thực hành:** terminal hiển thị lệnh `--describe` và thông tin của đủ ba partition.

## 4. Tạo và gửi 60 record có key

Chạy đoạn PowerShell sau để tạo dữ liệu trong bộ nhớ. Mỗi đơn có hai sự kiện theo thứ tự tạo đơn rồi thanh toán; mỗi dòng có cấu trúc `key|JSON`.

```powershell
$events = foreach ($number in 1..30) {
    $orderId = "o{0:D4}" -f $number
    foreach ($eventType in @("OrderCreated", "OrderPaid")) {
        $value = [ordered]@{
            event_id = "$orderId-$eventType"
            event_type = $eventType
            order_id = $orderId
            amount = 450000
            currency = "VND"
        }
        '{0}|{1}' -f $orderId, ($value | ConvertTo-Json -Compress)
    }
}
$events.Count
$events | Select-Object -First 4
```

`$events.Count` cần bằng **60**. Gửi toàn bộ dữ liệu bằng console producer:

```powershell
$events | docker exec -i kafka-architecture-lab /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic lab-order-events --property parse.key=true --property 'key.separator=|' --producer-property acks=all
```

`parse.key=true` yêu cầu console producer đọc phần trước dấu `|` làm key. Dấu phân cách chỉ phục vụ nhập liệu ở công cụ console; nó không phải cấu trúc bắt buộc của một Kafka record. Xem [mã nguồn LineMessageReader][line-reader].

Chỉ chạy lệnh gửi này **một lần** cho lượt dữ liệu đầu tiên. Gửi lại toàn bộ danh sách sẽ tạo thêm record trong topic; trùng `event_id` trong JSON không tự khiến Kafka bỏ qua record mới.

## 5. Đọc kèm partition, offset và key

Trong cùng cửa sổ PowerShell, lấy một ảnh chụp dữ liệu bằng console consumer. Group riêng này chỉ phục vụ lượt quan sát:

```powershell
$lines = docker exec kafka-architecture-lab /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic lab-order-events --group lab-inspect-01 --from-beginning --max-messages 60 --timeout-ms 15000 --consumer-property enable.auto.commit=false --property print.partition=true --property print.offset=true --property print.key=true --property 'key.separator=|'
$lines | Select-Object -First 12
```

Các thuộc tính `print.partition`, `print.offset` và `print.key` yêu cầu công cụ in địa chỉ record cùng dữ liệu. Xem [DefaultMessageFormatter][message-formatter]. Dòng tổng kết của công cụ có thể xuất hiện ở luồng thông báo riêng với các dòng dữ liệu.

Đếm các dòng record theo partition:

```powershell
$partitionIds = $lines | ForEach-Object {
    if ($_ -match 'Partition:(\d+)') {
        $Matches[1]
    }
}
$partitionIds.Count
$partitionIds | Group-Object | Sort-Object Name | Select-Object Name, Count
```

Tổng số record nhận được cần bằng **60** nếu topic mới và bước gửi thành công đúng một lần. Không yêu cầu ba partition phải có đúng 20 record mỗi partition. Hãy ghi số quan sát được vào bảng:

| Partition | Số record thực tế |
| --- | --- |
| P0 | Điền sau khi chạy |
| P1 | Điền sau khi chạy |
| P2 | Điền sau khi chạy |
| Tổng | Cần kiểm tra bằng 60 |

Kiểm tra hai sự kiện của đơn đầu tiên:

```powershell
$lines | Where-Object { $_ -match 'o0001\|' }
```

Cần thấy hai record cùng key ở cùng partition và sự kiện `OrderCreated` có offset trước `OrderPaid`. Không khẳng định key `o0001` phải vào P0, P1 hay P2 trong mọi client hoặc cấu hình. Thứ tự hiển thị chung giữa các partition cũng không phải thứ tự nghiệp vụ toàn cục.

**Ảnh nên lưu:** một ảnh có các dòng record kèm partition/offset và một ảnh có bảng đếm phân phối. Đây sẽ là bằng chứng quan sát của lượt chạy, thay cho một bảng số liệu tự đặt.

## 6. Quan sát hai consumer chia việc trong cùng group

Mở **hai cửa sổ PowerShell mới**. Giữ các tiến trình consumer chạy trong bước này; dùng cửa sổ ban đầu làm terminal quản trị.

**Cửa sổ A:**

```powershell
docker exec -it kafka-architecture-lab /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic lab-order-events --group lab-stock --from-beginning --consumer-property client.id=stock-c1 --consumer-property enable.auto.commit=true --consumer-property auto.commit.interval.ms=1000 --property print.partition=true --property print.offset=true --property print.key=true
```

**Cửa sổ B:**

```powershell
docker exec -it kafka-architecture-lab /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic lab-order-events --group lab-stock --from-beginning --consumer-property client.id=stock-c2 --consumer-property enable.auto.commit=true --consumer-property auto.commit.interval.ms=1000 --property print.partition=true --property print.offset=true --property print.key=true
```

Sau khi group ổn định, kiểm tra thành viên và partition được giao:

```powershell
docker exec kafka-architecture-lab /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group lab-stock --members --verbose
docker exec kafka-architecture-lab /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group lab-stock
```

Kỳ vọng hai consumer chia nhau ba partition, chẳng hạn một consumer nhận hai partition và consumer còn lại nhận một. Consumer khởi động trước có thể đã đọc hết 60 record trước khi consumer thứ hai tham gia; việc màn hình thứ hai chưa có record cũ không chứng minh nó chưa được phân công.

Gửi thêm hai sự kiện mới từ terminal quản trị để quan sát sau rebalance:

```powershell
@(
    'o9991|{"event_id":"e-new-1","event_type":"OrderCreated","order_id":"o9991"}',
    'o9992|{"event_id":"e-new-2","event_type":"OrderCreated","order_id":"o9992"}'
) | docker exec -i kafka-architecture-lab /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic lab-order-events --property parse.key=true --property 'key.separator=|'
```

Hai record mới có thể vào cùng partition, nên không bắt buộc cả hai cửa sổ đều in dữ liệu. Dùng kết quả assignment để xác định consumer sở hữu partition nhận record.

Trong bảng `--describe`, quan sát `CURRENT-OFFSET`, `LOG-END-OFFSET` và `LAG`. Auto commit trong ví dụ console giúp theo dõi tiến độ đọc; nó không chứng minh một thao tác nghiệp vụ như trừ tồn kho đã hoàn tất. Xem [quản lý và theo dõi consumer group][operations].

**Ảnh nên lưu:** kết quả `--members --verbose` có hai client ID và assignment, cùng bảng offset/lag sau khi gửi dữ liệu mới.

## 7. Đọc độc lập bằng một group khác

Giữ group `lab-stock` chạy. Từ terminal quản trị, dùng một group mới để đọc các record đang được lưu:

```powershell
docker exec kafka-architecture-lab /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic lab-order-events --group lab-analytics-01 --from-beginning --max-messages 62 --timeout-ms 15000 --consumer-property enable.auto.commit=false --property print.partition=true --property print.offset=true --property print.key=true
```

Nếu đã gửi đúng 60 record ban đầu và hai record mới, group mới cần đọc được **62 record**. Nếu bạn đã gửi thêm ở các bước trước, điều chỉnh `--max-messages` theo số thực tế, hoặc bỏ giới hạn và dùng `Ctrl+C` để dừng.

Điều cần rút ra là group mới vẫn có thể đọc các record mà group tồn kho đã đọc. Commit không làm mất dữ liệu của topic. `--from-beginning` áp dụng khi group cần xác định vị trí ban đầu; dùng lại group đã có committed offset không phải cách chắc chắn để reset tiến độ. Trong bước này ta dùng một tên group mới và tắt auto commit cho lượt quan sát. Xem [consumer offset reset][consumer-config].

## 8. Mở rộng quan sát và xử lý lỗi

Nếu muốn quan sát giới hạn số consumer, mở thêm C3 và C4 với cùng `group.id=lab-stock`, thay `client.id` thành `stock-c3`, `stock-c4`. Khi cả bốn thành viên ổn định trên topic ba partition, ít nhất một thành viên không có partition của topic này. Dùng `--members --verbose` để kiểm tra, thay vì suy luận chỉ từ lượng dữ liệu in ra.

| Hiện tượng | Cách kiểm tra |
| --- | --- |
| Không kết nối Docker API | Mở Docker Desktop, kiểm tra engine và chạy lại `docker version` |
| Container thoát hoặc broker chưa sẵn sàng | Xem `docker ps -a` và `docker logs --tail 60 kafka-architecture-lab` |
| Cổng 9092 đang được dùng | Kiểm tra tiến trình/container đang chiếm cổng; nếu chỉ đổi host port, các lệnh `docker exec` trong lab vẫn dùng cổng trong container 9092 |
| Topic đã tồn tại | Chọn tên topic mới và thay nhất quán; không mặc định dữ liệu cũ là dữ liệu của lượt này |
| Consumer chưa đủ 60 record rồi timeout | Kiểm tra số lần gửi, lỗi producer, tên topic và vị trí offset; tăng timeout nếu broker chậm |
| Group mới vào chưa thấy record | Kiểm tra assignment và committed offset; gửi thêm dữ liệu sau khi rebalance ổn định |
| `CURRENT-OFFSET` chưa có hoặc lag chưa cập nhật | Consumer có thể chưa commit; chờ chu kỳ commit và kiểm tra lại |
| Đang rebalance khi describe group | Chờ group ổn định rồi chạy lại lệnh describe |

## 9. Dừng môi trường và lưu bằng chứng

Dùng `Ctrl+C` ở từng cửa sổ consumer để kết thúc chúng. Nếu muốn giữ container và dữ liệu để học tiếp:

```powershell
docker stop kafka-architecture-lab
```

Lần sau dùng `docker start kafka-architecture-lab`. Nếu đã hoàn tất và muốn bỏ container lab cùng dữ liệu lưu bên trong nó, chạy sau khi đã dừng:

```powershell
docker rm kafka-architecture-lab
```

Trước khi dọn, nên lưu bốn bằng chứng: mô tả topic, số record theo partition, hai sự kiện cùng key kèm offset và assignment/lag của consumer group. Ghi kèm phiên bản image và số record thực tế đã gửi để người đọc có thể hiểu kết quả của lượt chạy.

## Tài liệu tham khảo

- [Kafka Quick Start: khởi động Docker, ghi và đọc sự kiện][quickstart].
- [Basic Kafka Operations: topic và consumer group][operations].
- [LineMessageReader của Kafka 4.1.2: nhập key/value ở console producer][line-reader].
- [DefaultMessageFormatter của Kafka 4.1.2: in partition, offset và key][message-formatter].
- [Consumer Configs: auto commit và offset reset][consumer-config].

[quickstart]: https://kafka.apache.org/41/getting-started/quickstart/
[operations]: https://kafka.apache.org/41/operations/basic-kafka-operations/
[line-reader]: https://github.com/apache/kafka/blob/4.1.2/tools/src/main/java/org/apache/kafka/tools/LineMessageReader.java
[message-formatter]: https://github.com/apache/kafka/blob/4.1.2/tools/src/main/java/org/apache/kafka/tools/consumer/DefaultMessageFormatter.java
[consumer-config]: https://kafka.apache.org/41/configuration/consumer-configs/
