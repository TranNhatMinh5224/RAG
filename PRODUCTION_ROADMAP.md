# Kế hoạch cải thiện dự án RAG để triển khai Production

## 1. Mục tiêu

Tài liệu này mô tả các điểm cần cải thiện để chuyển dự án từ một MVP RAG có thể trình diễn thành một hệ thống có thể phục vụ người dùng thật một cách an toàn, ổn định và có khả năng đo lường.

Các mục tiêu chính:

- Không để người dùng đọc, sửa hoặc xóa dữ liệu của tenant khác.
- Không làm mất hoặc lệch dữ liệu giữa PostgreSQL, Qdrant và kho file.
- Không để OCR, embedding và reranking làm treo API.
- Có khả năng đo chất lượng retrieval, câu trả lời và trích dẫn.
- Có test tự động, logging, metrics, backup và quy trình triển khai lặp lại được.
- Không tuyên bố tính năng trong tài liệu khi code chưa triển khai hoặc chưa được kiểm chứng.

## 2. Hiện trạng

### Điểm mạnh

- Backend đã phân tách router, service và repository.
- Có PostgreSQL để lưu user, conversation, message và metadata tài liệu.
- Có Qdrant để lưu vector.
- Có semantic chunking, query rewriting và cross-encoder reranking.
- Hỗ trợ PDF, DOCX, XLSX, PPTX và OCR ảnh/PDF scan.
- Retrieval lọc theo `user_id` và `document_id`.
- Có Docker Compose và Alembic migration.
- Upload đã dùng tên file UUID, giới hạn dung lượng và loại bỏ path traversal cơ bản.
- Access token và refresh token đã được phân biệt bằng claim `token_type`.
- Endpoint reset mật khẩu không xác minh đã được loại bỏ.
- Luồng gắn tài liệu vào conversation đã kiểm tra ownership trong `ChatService`.

### Đánh giá độ sẵn sàng

| Hạng mục | Mức hiện tại | Mục tiêu production |
|---|---:|---:|
| Kiến trúc code | Khá | Tốt |
| Bảo mật API | Trung bình | Tốt |
| Cô lập tenant | Khá | Có test và audit đầy đủ |
| Tính nhất quán dữ liệu | Thấp | Có state machine và retry |
| Hiệu năng | Thấp | Tác vụ nặng chạy ngoài API |
| Chất lượng RAG | Chưa đo | Có benchmark và threshold |
| Automated test | Rất ít | Unit, integration, security, E2E |
| Vận hành | Thấp | Image bất biến, healthcheck, metrics, backup |

## 3. Nguyên tắc ưu tiên

Thứ tự thực hiện:

1. Bảo vệ dữ liệu và phân quyền.
2. Đảm bảo dữ liệu không bị mất hoặc lệch.
3. Tách tác vụ nặng khỏi request HTTP.
4. Viết test để khóa hành vi đúng.
5. Đo chất lượng RAG trước khi tối ưu.
6. Hoàn thiện hạ tầng và trải nghiệm người dùng.

Không nên ưu tiên giao diện hoặc thêm model mới khi các lỗi phân quyền, transaction và ingestion vẫn chưa được xử lý.

---

## 4. Giai đoạn 1 — Bảo mật và cô lập tenant

**Ưu tiên:** P0  
**Thời gian dự kiến:** 2–4 ngày

### 4.1 Kiểm tra ownership tập trung trong service

#### Vấn đề

Nếu router hoặc repository được gọi trực tiếp mà không kiểm tra `user_id`, người dùng có thể đoán ID và tác động đến tài nguyên của người khác.

#### Cách cải thiện

- Router chỉ nhận request, gọi service và chuyển domain error thành HTTP response.
- Mọi thao tác với conversation phải truy vấn bằng `(conversation_id, user_id)`.
- Mọi thao tác với document phải truy vấn bằng `(document_id, user_id)`.
- Không đưa các repository thành thuộc tính được router sử dụng trực tiếp.
- Dùng `404` cho tài nguyên không tồn tại hoặc không thuộc user để tránh tiết lộ ID có tồn tại.

#### API cần kiểm tra

- Lấy chi tiết conversation.
- Xóa conversation.
- Gắn hoặc tháo document khỏi conversation.
- Gửi chat vào conversation.
- Liệt kê và xóa document.
- Lấy lịch sử message.

#### Tiêu chí hoàn thành

- User B không đọc, sửa hoặc xóa được tài nguyên của User A.
- Không endpoint nào chỉ kiểm tra ID mà không kiểm tra tenant.
- Có test tự động cho từng trường hợp truy cập chéo.

### 4.2 Rate limiting và quota

#### Vấn đề

Login, upload, OCR, embedding và chat đều có thể bị lạm dụng để làm cạn CPU, RAM, disk hoặc quota Gemini.

#### Cách cải thiện

- Rate limit login theo IP và email.
- Rate limit register và refresh token theo IP.
- Rate limit chat theo user.
- Giới hạn số file, tổng dung lượng, số trang và số request theo tenant.
- Trả `429 Too Many Requests` cùng thời gian retry.
- Có thể dùng Redis làm bộ đếm phân tán.

#### Giá trị khởi đầu đề xuất

| Endpoint | Giới hạn ban đầu |
|---|---:|
| Login | 5 lần/phút/IP |
| Register | 3 lần/giờ/IP |
| Refresh | 20 lần/phút/user |
| Upload | 5 file/10 phút/user |
| Chat | 20 câu/phút/user |

Các giá trị phải được điều chỉnh dựa trên metrics thực tế.

### 4.3 Refresh token và session

#### Vấn đề

Refresh token JWT hiện chưa có revoke, token family hoặc reuse detection. Logout phía frontend chỉ xóa token khỏi trình duyệt.

#### Cách cải thiện

- Tạo bảng `auth_sessions`.
- Mỗi refresh token có `jti` ngẫu nhiên.
- Chỉ lưu hash refresh token trong database.
- Rotation refresh token sau mỗi lần sử dụng.
- Nếu một token cũ bị dùng lại, thu hồi toàn bộ token family.
- Thu hồi session khi logout, đổi mật khẩu hoặc khóa tài khoản.
- Đặt refresh token trong cookie `HttpOnly`, `Secure`, `SameSite`.
- Giữ access token ngắn hạn trong memory nếu kiến trúc frontend cho phép.

### 4.4 Khôi phục mật khẩu đúng chuẩn

#### Cách cải thiện

Tạo hai endpoint:

```text
POST /auth/password-reset/request
POST /auth/password-reset/confirm
```

Luồng xử lý:

1. Người dùng nhập email.
2. API luôn trả cùng một response, dù email có tồn tại hay không.
3. Server tạo token ngẫu nhiên có entropy cao.
4. Database chỉ lưu hash token, `user_id`, `expires_at`, `used_at`.
5. Gửi liên kết qua email.
6. Token chỉ dùng một lần và hết hạn sau 15–30 phút.
7. Sau khi đổi mật khẩu, thu hồi toàn bộ session cũ.

### 4.5 Gia cố upload

#### Cách cải thiện

- Kiểm tra extension, MIME và magic bytes.
- Giới hạn dung lượng file và kích thước giải nén.
- Giới hạn số trang PDF, số sheet, số slide và độ phân giải ảnh.
- Phòng chống ZIP bomb trong DOCX, XLSX và PPTX.
- Scan malware nếu tài liệu đến từ nguồn không tin cậy.
- Không tin tưởng tên file do client gửi.
- Lưu checksum SHA-256 để phát hiện file trùng và kiểm tra toàn vẹn.

#### Tiêu chí hoàn thành

- File giả extension bị từ chối.
- File quá lớn trả `413`.
- File lỗi hoặc có cấu trúc nguy hiểm không làm crash worker.
- Không thể ghi file ra ngoài vùng storage đã cấu hình.

---

## 5. Giai đoạn 2 — Tính nhất quán dữ liệu và ingestion nền

**Ưu tiên:** P0–P1  
**Thời gian dự kiến:** 4–7 ngày

### 5.1 Thêm trạng thái xử lý tài liệu

Thêm các cột vào bảng `documents`:

```text
status: uploaded | queued | processing | ready | failed | deleting
error_message: nullable text
chunk_count: integer
content_hash: string
processed_at: datetime
updated_at: datetime
```

Luồng trạng thái:

```text
uploaded → queued → processing → ready
                         └──────→ failed
ready → deleting → deleted
```

Frontend chỉ cho phép gắn tài liệu có trạng thái `ready` vào conversation.

### 5.2 Đưa ingestion sang background worker

#### Vấn đề

OCR, parsing, semantic chunking và embedding là tác vụ CPU-bound hoặc IO dài. Chúng đang chạy trong request HTTP và có thể chặn event loop.

#### Cách cải thiện

- API upload chỉ stream file vào storage và tạo bản ghi document.
- API đẩy `document_id` vào queue rồi trả `202 Accepted`.
- Worker lấy file, OCR, chunk, embed và ghi Qdrant.
- Frontend polling trạng thái hoặc nhận event qua SSE/WebSocket.
- Có retry với exponential backoff.
- Job phải idempotent: chạy lại không tạo vector trùng.

Các lựa chọn worker:

- Nhẹ: ARQ + Redis.
- Phổ biến: Celery + Redis/RabbitMQ.
- Đơn giản cho dự án nhỏ: Dramatiq + Redis.

### 5.3 Transaction và Unit of Work

#### Vấn đề

Repository hiện tự `commit()` trong từng method, khiến nghiệp vụ nhiều bước không thể nằm trong cùng transaction.

#### Cách cải thiện

- Repository chỉ `add`, `execute`, `flush` và đọc dữ liệu.
- Service hoặc Unit of Work chịu trách nhiệm `commit/rollback`.
- Tạo conversation và gắn document trong cùng transaction.
- Thêm rollback rõ ràng khi thao tác thất bại.

Lưu ý: PostgreSQL và Qdrant không chia sẻ một ACID transaction. Vì vậy cần state machine, idempotency và reconciliation thay vì cố tạo transaction phân tán phức tạp.

### 5.4 Xóa tài liệu an toàn

Luồng đề xuất:

1. Đánh dấu `deleting`.
2. Worker xóa vector theo `user_id` và `document_id`.
3. Xóa object trong storage.
4. Xóa hoặc soft-delete metadata.
5. Nếu lỗi thì retry.
6. Chạy reconciliation định kỳ để tìm vector hoặc file mồ côi.

### 5.5 Chuyển file sang object storage

Khi chạy nhiều replica, local filesystem không còn đáng tin cậy.

Nên dùng:

- MinIO khi self-host.
- AWS S3, Google Cloud Storage hoặc Azure Blob khi dùng cloud.

Database chỉ lưu `storage_key`, checksum, kích thước và MIME. Cần cấu hình encryption at rest, backup và retention policy.

---

## 6. Giai đoạn 3 — Chất lượng RAG có thể đo lường

**Ưu tiên:** P1  
**Thời gian dự kiến:** 4–7 ngày

### 6.1 Xây tập đánh giá

Tạo tối thiểu 30–100 câu hỏi đại diện:

- Câu trả lời nằm rõ trong một chunk.
- Câu cần tổng hợp nhiều chunk.
- Câu hỏi nối tiếp cần lịch sử chat.
- Câu hỏi không có đáp án trong tài liệu.
- Câu chứa mã số hoặc từ khóa chính xác.
- Tài liệu scan chất lượng thấp.
- Câu hỏi cố prompt injection.

Mỗi mẫu nên có:

```json
{
  "question": "...",
  "expected_document_ids": [1],
  "expected_pages": [3],
  "reference_answer": "...",
  "answerable": true
}
```

### 6.2 Metrics cần theo dõi

- Recall@K của retrieval.
- MRR hoặc nDCG.
- Reranker improvement.
- Answer correctness.
- Groundedness.
- Citation precision và recall.
- Tỷ lệ từ chối đúng với câu không có đáp án.
- Latency p50, p95, p99.
- Chi phí trung bình mỗi câu hỏi.

### 6.3 Thêm relevance threshold

Hiện top 3 luôn được đưa cho LLM dù kết quả có thể không liên quan.

Cần:

- Giữ lại dense score và rerank score.
- Chọn threshold bằng tập eval, không chọn cảm tính.
- Nếu không chunk nào đạt ngưỡng, trả câu không tìm thấy.
- Ghi metric số lần retrieval không đạt ngưỡng.

### 6.4 Citation có cấu trúc

Không để LLM tự quyết định toàn bộ citation. API nên trả:

```json
{
  "answer": "...",
  "citations": [
    {
      "document_id": 12,
      "filename": "contract.pdf",
      "page": 4,
      "chunk_id": "...",
      "score": 0.91
    }
  ]
}
```

Metadata citation phải được dựng từ kết quả retrieval phía server. Có thể yêu cầu model tham chiếu các chunk bằng ID cố định rồi server xác minh các ID đó tồn tại.

### 6.5 Hybrid Search thật

Code hiện tại là dense search + reranking, chưa phải dense–sparse hybrid như README mô tả.

Cách triển khai:

1. Tạo dense vector bằng BGE-M3.
2. Tạo sparse vector hoặc BM25 index.
3. Tìm kiếm dense và sparse song song.
4. Kết hợp thứ hạng bằng Reciprocal Rank Fusion.
5. Đưa top N qua cross-encoder reranker.
6. So sánh với baseline dense-only trên tập eval.

Chỉ giữ hybrid nếu metrics cải thiện đủ để bù thêm độ phức tạp và latency.

### 6.6 Chống prompt injection từ tài liệu

- Xem tài liệu là dữ liệu không đáng tin cậy, không phải instruction.
- Tách system instruction và document context bằng message role phù hợp.
- Đặt delimiter rõ ràng.
- Không cho model thực hiện hành động chỉ vì tài liệu yêu cầu.
- Thêm test tài liệu chứa câu “bỏ qua mọi chỉ dẫn trước đó”.
- Không log hoặc hiển thị secret dù document yêu cầu.

---

## 7. Giai đoạn 4 — Automated test và CI

**Ưu tiên:** P0–P1  
**Thời gian dự kiến:** thực hiện song song với các giai đoạn trên

### 7.1 Unit test

- Hash và verify password.
- Tạo/giải mã access token và refresh token.
- Từ chối token sai loại.
- Validation upload.
- Ownership trong `ChatService` và `DocumentService`.
- Context formatting.
- Relevance threshold.

### 7.2 Integration test

- Repository với PostgreSQL test database.
- Qdrant test container.
- Upload → ingestion → retrieval → delete.
- Alembic upgrade từ database trống.
- Retry job không tạo vector trùng.

### 7.3 Multi-tenant security test

Phải có các test sau:

- User B không lấy được conversation của User A.
- User B không gắn document vào conversation của User A.
- User B không xóa conversation của User A.
- User B không xem hoặc xóa document của User A.
- User B truy vấn bằng `document_id` của User A nhận kết quả rỗng.
- User B không lấy được message history của User A.

Ví dụ hành vi cần khóa:

```python
result = await chat_service.attach_documents(
    user_id=user_b.id,
    conversation_id=user_a_conversation.id,
    document_ids=[user_b_document.id],
)

assert result is None
```

### 7.4 End-to-end test

- Register và login.
- Upload tài liệu.
- Theo dõi trạng thái đến `ready`.
- Tạo conversation và gắn tài liệu.
- Gửi câu hỏi.
- Kiểm tra answer và citation.
- Xóa conversation và document.
- Logout và xác minh session bị thu hồi.

### 7.5 CI pipeline

Mỗi pull request phải chạy:

1. Python lint và format check.
2. Python type check.
3. Backend unit test.
4. Integration test với PostgreSQL/Qdrant.
5. Frontend lint và build.
6. Dependency/security scan.
7. Alembic migration check.
8. Docker image build.

Không cho merge nếu một bước bắt buộc thất bại.

---

## 8. Giai đoạn 5 — Docker và hạ tầng production

**Ưu tiên:** P1  
**Thời gian dự kiến:** 3–6 ngày

### 8.1 Docker image bất biến

Backend production Dockerfile cần:

- Pin base image.
- Cài dependency từ lock file.
- Copy source vào image.
- Chạy bằng non-root user.
- Không mount source code production.
- Không dùng `--reload`.

Frontend cần multi-stage build:

1. Node stage chạy `npm ci` và `npm run build`.
2. Nginx hoặc Caddy stage phục vụ thư mục `dist`.

Không dùng `vite preview` làm production server và không chạy `npm install` khi container khởi động.

### 8.2 Tách compose dev và prod

- `compose.dev.yml`: bind mount source, hot reload, expose Qdrant nếu cần debug.
- `compose.prod.yml`: image bất biến, không mount source, secret từ secret manager, resource limits, healthcheck.
- Pin Qdrant và PostgreSQL version, không dùng `latest`.

### 8.3 Healthcheck

Tạo:

```text
GET /health/live
GET /health/ready
```

`live` chỉ xác nhận process còn chạy. `ready` kiểm tra PostgreSQL, Qdrant và các dependency bắt buộc. Không gọi Gemini tốn phí ở mọi healthcheck; chỉ kiểm tra cấu hình hoặc có probe riêng tần suất thấp.

### 8.4 Reverse proxy và HTTPS

- Nginx, Caddy hoặc managed load balancer.
- HTTPS bắt buộc.
- HSTS sau khi HTTPS ổn định.
- Request body limit tại proxy và backend.
- Timeout riêng cho upload và chat streaming.
- Security headers và Content Security Policy.

### 8.5 Backup và phục hồi

Phải backup đồng bộ:

- PostgreSQL.
- Qdrant snapshots.
- Object storage.

Cần định nghĩa:

- RPO: chấp nhận mất tối đa bao nhiêu dữ liệu.
- RTO: cần phục hồi trong bao lâu.
- Lịch backup.
- Retention.
- Quy trình restore được kiểm thử định kỳ.

Backup chưa từng restore thử chưa được xem là backup đáng tin cậy.

---

## 9. Giai đoạn 6 — Observability và vận hành

### 9.1 Structured logging

- Dùng logger thay cho `print`.
- Log dạng JSON trong production.
- Có request ID, user ID đã pseudonymize, document ID và job ID.
- Không log access token, refresh token, mật khẩu hoặc nguyên văn document chunk.
- Phân biệt log ứng dụng và audit log.

### 9.2 Metrics

Theo dõi tối thiểu:

- Request count, error rate và latency.
- Upload size và processing duration.
- OCR/chunking/embedding duration.
- Queue depth và job failure rate.
- Qdrant query latency.
- Gemini latency, token usage và chi phí.
- Retrieval no-result rate.
- CPU, RAM, disk và container restart.

### 9.3 Alert

Tạo cảnh báo cho:

- HTTP 5xx tăng cao.
- Queue tồn đọng.
- Worker lỗi liên tục.
- Disk gần đầy.
- PostgreSQL/Qdrant không ready.
- Gemini error hoặc rate limit tăng.
- Chi phí vượt ngưỡng ngày/tháng.

---

## 10. Database và migration cần bổ sung

### Index đề xuất

- `documents(user_id)`
- `conversations(user_id, created_at)`
- `messages(conversation_id, created_at)`
- `auth_sessions(user_id, revoked_at)`
- `password_reset_tokens(user_id, expires_at)`

### Constraint đề xuất

- `ON DELETE CASCADE` cho message và bảng liên kết phù hợp.
- Check constraint cho `messages.role`.
- Check constraint cho `documents.status`.
- Email được normalize và unique theo dạng normalize.
- Các timestamp quan trọng đặt `nullable=False`.

Mỗi thay đổi schema phải có Alembic migration và test upgrade/downgrade phù hợp.

---

## 11. Quản lý dependency và secret

### Dependency

- Pin version Python package.
- Dùng lock file có hash nếu có thể.
- Dùng `npm ci` thay vì `npm install` trong build.
- Quét CVE tự động.
- Pin Docker image theo version hoặc digest.

### Secret

- Không commit `.env`.
- Cung cấp `.env.example` chỉ chứa tên biến và giá trị giả.
- Production dùng secret manager.
- Có quy trình rotate `SECRET_KEY`, Gemini key và database credential.
- Không in secret ra log hoặc error response.

Các biến môi trường tối thiểu nên được tài liệu hóa:

```env
DATABASE_URL=
SECRET_KEY=
GEMINI_API_KEY=
QDRANT_URL=
ALLOWED_ORIGINS=
MAX_UPLOAD_SIZE_MB=25
UPLOAD_DIR=/app/data
```

---

## 12. Kế hoạch thực hiện theo sprint

### Sprint 1 — Security foundation

- [x] Phân biệt access token và refresh token.
- [x] Loại bỏ reset mật khẩu không xác minh.
- [x] Gia cố filename và giới hạn upload cơ bản.
- [x] Kiểm tra ownership khi gắn document vào conversation.
- [ ] Viết test multi-tenant.
- [ ] Loại bỏ mọi truy cập repository trực tiếp từ router.
- [ ] Thêm rate limiting.
- [ ] Thêm kiểm tra MIME và magic bytes.

### Sprint 2 — Data reliability

- [ ] Thêm document processing status.
- [ ] Tạo Alembic migration.
- [ ] Refactor Unit of Work và transaction boundary.
- [ ] Tạo background worker.
- [ ] Thêm retry và idempotency.
- [ ] Xử lý vector/file mồ côi.

### Sprint 3 — RAG quality

- [ ] Tạo eval dataset.
- [ ] Đo dense retrieval baseline.
- [ ] Thêm rerank threshold.
- [ ] Trả citation có cấu trúc.
- [ ] Test prompt injection.
- [ ] Thử nghiệm hybrid search và so sánh metrics.

### Sprint 4 — Production deployment

- [ ] Tạo Dockerfile production.
- [ ] Tách compose dev/prod rõ ràng.
- [ ] Thêm healthcheck.
- [ ] Thêm reverse proxy và HTTPS.
- [ ] Structured logging và metrics.
- [ ] Backup và restore drill.
- [ ] CI/CD và security scan.

---

## 13. Definition of Done cho Production v1

Chỉ xem hệ thống đạt Production v1 khi đáp ứng tất cả điều kiện:

- Test multi-tenant đều đạt.
- Không có lỗ hổng Critical hoặc High đã biết chưa có biện pháp giảm thiểu.
- Upload và ingestion chạy qua queue, có retry và trạng thái.
- Restart giữa ingestion không tạo dữ liệu trùng hoặc mồ côi không thể phục hồi.
- Có benchmark RAG và relevance threshold.
- Citation lấy từ metadata server và có thể xác minh.
- Docker image không phụ thuộc bind mount source.
- Production không chạy `--reload`, `npm install` hoặc Vite dev/preview server.
- Có healthcheck, logging, metrics và alert cơ bản.
- Có backup và đã kiểm thử restore.
- Dependency được pin và quét bảo mật.
- Có quy trình migrate và rollback database.
- README phản ánh đúng tính năng thực tế.

## 14. Việc nên làm ngay tiếp theo

Thứ tự khuyến nghị:

1. Viết test cho `ChatService.attach_documents` và toàn bộ multi-tenant boundary.
2. Refactor endpoint lấy chi tiết conversation để router không gọi repository trực tiếp.
3. Thêm trạng thái xử lý vào `documents` và migration.
4. Đưa ingestion sang background worker.
5. Xây tập eval RAG trước khi triển khai hybrid search.

Việc đầu tiên nên được triển khai trong code là bộ test multi-tenant. Nó bảo đảm lỗi phân quyền vừa sửa không quay trở lại trong những lần refactor sau.
