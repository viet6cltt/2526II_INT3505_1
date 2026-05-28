# Business Model Canvas - VolunteerHub API

## 1. Customer Segments

- `Tình nguyện viên`: người tìm kiếm, đăng ký, tham gia và theo dõi các hoạt động cộng đồng.
- `Nhà tổ chức/Manager`: cá nhân hoặc tổ chức tạo sự kiện, xét duyệt người tham gia và quản lý vận hành sự kiện.
- `Quản trị viên hệ thống`: người kiểm duyệt sự kiện, quản lý người dùng và theo dõi chỉ số toàn nền tảng.
- `Tổ chức xã hội/CLB/Trường học`: đơn vị sử dụng nền tảng để triển khai, mở rộng và báo cáo các chương trình thiện nguyện.

## 2. Value Propositions

- Cung cấp một `API platform` thống nhất để kết nối tình nguyện viên với các cơ hội tham gia phù hợp.
- Hỗ trợ quản lý trọn vòng đời sự kiện: tạo sự kiện, duyệt sự kiện, đăng ký tham gia, xét duyệt người tham gia và cập nhật trạng thái tham gia.
- Tăng độ tin cậy trong vận hành bằng `QR check-in` và `QR completion`, giúp xác nhận tham gia và hoàn thành hoạt động minh bạch hơn.
- Tạo trải nghiệm gắn kết sau đăng ký nhờ các tính năng `community`, `chat realtime`, `reaction`, `comment` và `notification`.
- Hỗ trợ ra quyết định bằng `analytics dashboard`, `application rate`, `approval rate`, thống kê người dùng, sự kiện và dữ liệu export.
- Phù hợp cho mô hình microservices, dễ mở rộng frontend web hoặc tích hợp thêm client/mobile trong tương lai.

## 3. Channels

- `Frontend web/dashboard` là kênh chính đang tiêu thụ API.
- `API Gateway` là đầu vào tập trung cho toàn bộ client.
- `Web push notification` giúp tiếp cận người dùng theo thời gian thực.
- `In-app chat` và `community feed` là các kênh tương tác trực tiếp trong hệ thống.
- `Export CSV/JSON` là kênh phục vụ báo cáo nội bộ, giảng viên, quản trị viên hoặc nhà tổ chức.

## 4. Customer Relationships

- `Self-service`: tình nguyện viên có thể tự khám phá, đăng ký và theo dõi trạng thái tham gia.
- `Operational support`: manager có thể chủ động quản lý danh sách participant, review hồ sơ đăng ký và theo dõi hiệu quả sự kiện.
- `Automated engagement`: hệ thống duy trì tương tác qua thông báo, cập nhật trạng thái và cảnh báo liên quan đến sự kiện.
- `Community-based retention`: giữ chân người dùng bằng bài viết, bình luận, cảm xúc và hội thoại theo từng sự kiện.

## 5. Revenue Streams

- Hiện tại codebase `chưa thể hiện luồng thanh toán trực tiếp`, nên doanh thu chưa phải trọng tâm của phiên bản API này.
- Mô hình phù hợp nhất là `B2B/B2G SaaS`, thu phí từ tổ chức, CLB, trường học hoặc đơn vị cộng đồng khi sử dụng hệ thống để vận hành hoạt động thiện nguyện.
- Có thể mở rộng theo các gói `premium` như:
  - analytics nâng cao,
  - export báo cáo chuyên sâu,
  - nhiều manager trong cùng tổ chức,
  - giao diện hoặc domain tùy biến cho từng đơn vị.
- Ngoài doanh thu trực tiếp, nền tảng cũng có thể nhận `tài trợ CSR`, hợp tác xã hội hoặc hỗ trợ từ trường học và tổ chức phi lợi nhuận.

## 6. Key Resources

- Hệ thống `microservices backend` gồm: Auth, User, Event, Registration, Community, Chat, Notification, Analytics, Aggregation.
- Dữ liệu lõi: người dùng, hồ sơ, sự kiện, đăng ký, trạng thái tham gia, bài viết cộng đồng, tin nhắn và số liệu phân tích.
- Hạ tầng kỹ thuật: `Authorization Server`, `API Gateway`, `Service Discovery`.
- Thành phần hạ tầng dữ liệu và messaging: `PostgreSQL`, `Redis`, `RabbitMQ`.
- Dịch vụ hỗ trợ media và notification như `Firebase Storage` và `Web Push`.
- Tài nguyên logic nghiệp vụ: phân quyền theo role, aggregation giữa các service và analytics/reporting.

## 7. Key Activities

- Phát triển và vận hành API ổn định, bảo mật và có khả năng mở rộng.
- Quản lý nghiệp vụ sự kiện và đăng ký tham gia của tình nguyện viên.
- Điều phối giao tiếp giữa các service thông qua gateway, message broker và internal APIs.
- Gửi notification, hỗ trợ chat/community và duy trì tương tác của người dùng.
- Tổng hợp dữ liệu, xây dựng dashboard và export báo cáo cho manager/admin.
- Cải thiện trải nghiệm người dùng và tối ưu hiệu quả kết nối giữa volunteer với tổ chức.

## 8. Key Partners

- Các `CLB`, `trường đại học`, `tổ chức xã hội`, `nhóm cộng đồng` là đối tác nghiệp vụ chính.
- `Google OAuth` và `Firebase` là đối tác công nghệ quan trọng cho xác thực và lưu trữ media.
- Nhà cung cấp hạ tầng cloud, database, cache và message queue hỗ trợ vận hành hệ thống.
- Các doanh nghiệp tài trợ, đơn vị CSR và cơ quan địa phương có thể là đối tác mở rộng khi triển khai thực tế.

## 9. Cost Structure

- Chi phí hạ tầng chạy service, database, cache, queue và storage.
- Chi phí phát triển, bảo trì và kiểm thử hệ thống microservices.
- Chi phí bảo mật, logging, monitoring, backup và xử lý sự cố.
- Chi phí tích hợp dịch vụ bên thứ ba như OAuth, push notification, media storage.
- Chi phí vận hành nội dung, kiểm duyệt người dùng/sự kiện và hỗ trợ các tổ chức tham gia nền tảng.

## Kết luận

VolunteerHub API phù hợp với mô hình `nền tảng quản lý và kết nối hoạt động tình nguyện`. Trong đó, tình nguyện viên là nhóm người dùng cuối tạo ra lưu lượng và giá trị cộng đồng, còn `manager`, `CLB`, `trường học` và `tổ chức xã hội` là nhóm khách hàng có tiềm năng sử dụng nền tảng như một giải pháp vận hành thực tế. Điểm mạnh nổi bật của hệ thống là không chỉ dừng ở CRUD sự kiện, mà đã mở rộng sang `QR attendance`, `community`, `chat`, `notification`, `analytics` và `reporting`, cho thấy đây là một backend có định hướng platform khá đầy đủ.
