# 🚀 Kế Hoạch Tối Ưu Hóa "Legal RAG" - Trợ Lý AI Pháp Lý

Bản tài liệu này trình bày ý tưởng và lộ trình nâng cấp hệ thống **Enterprise AI RAG** hiện tại, chuyển dịch từ phân tích dữ liệu chung sang chuyên sâu cho domain **Văn bản Pháp luật, Quy định, Điều lệ và Hợp đồng**.

---

## 🎯 1. Bối Cảnh & Mục Tiêu

Hệ thống hiện tại đã sở hữu kiến trúc nền tảng rất mạnh (Hybrid Search + Cross-Encoder Re-ranking). Tuy nhiên, đặc thù của văn bản Pháp lý không đòi hỏi tính toán logic toán học hay sơ đồ phức tạp (PoT/PoG), mà yêu cầu **độ chính xác tuyệt đối về mặt cấu trúc văn bản, tính liên kết chéo và thời hạn hiệu lực**.

**Mục tiêu tối ưu:**
- Loại bỏ hoàn toàn tình trạng "mất ngữ cảnh cha" khi cắt nhỏ văn bản (Chunking).
- Giải quyết bài toán trích dẫn chéo (Tham chiếu đến các Điều/Khoản khác).
- Ngăn chặn triệt để việc AI lấy nhầm văn bản đã hết hiệu lực hoặc sai năm ban hành.

---

## 💡 2. Ý Tưởng Tối Ưu (Core Optimization Ideas)

### 2.1. Tối ưu theo Cấu trúc phân cấp (Hierarchical Chunking)
Thay vì sử dụng `SemanticChunker` (cắt theo ngữ nghĩa) hay Token, hệ thống sẽ sử dụng **Regex (Biểu thức chính quy)** để nhận diện và cắt văn bản dựa trên cấu trúc cứng của Pháp luật Việt Nam: `Phần -> Chương -> Mục -> Điều -> Khoản -> Điểm`.
*   **Chiến thuật:** Khi một `Khoản` hoặc `Điểm` được cắt ra, hệ thống sẽ tự động dán tiêu đề của `Chương` và `Điều` chứa nó lên đầu chunk đó.
*   *Ví dụ output chunk:* `[Luật Doanh nghiệp 2020] > [Chương II: Thành lập doanh nghiệp] > [Điều 17: Quyền thành lập] > Khoản 1: Tổ chức, cá nhân có quyền...`

### 2.2. Lọc Siêu dữ liệu Tự động (Self-Query Retriever)
Trong Luật, việc áp dụng đúng "Nghị định năm nào" là yếu tố sống còn.
*   **Chiến thuật:** Dùng LLM ở bước xử lý câu hỏi đầu vào để tự động bóc tách các điều kiện cứng (Metadata Filters) như: `Loại văn bản` (Thông tư, Nghị định), `Năm ban hành`, `Trạng thái hiệu lực`.
*   Tiêm thẳng các Filters này vào Qdrant trước khi quét Vector.

### 2.3. Cơ chế Truy xuất đệ quy (Recursive/Cross-Reference Retrieval)
Luật pháp chứa rất nhiều câu lệnh tham chiếu (Ví dụ: *"Xử phạt theo điểm a khoản 2 Điều 15"*).
*   **Chiến thuật:** Xây dựng một luồng Agent đơn giản. Khi LLM đọc tài liệu và phát hiện có cụm từ "Theo Điều X...", nó sẽ tự động kích hoạt một lượt tìm kiếm phụ (Second-hop search) để kéo nội dung của "Điều X" về bổ sung vào bối cảnh (Context) trước khi tạo câu trả lời cuối cùng.

---

## 📅 3. Lộ Trình Triển Khai (Implementation Plan)

### Giai đoạn 1: Nâng cấp Data Ingestion Pipeline (Tuần 1)
- [ ] **Viết bộ Regex Parser:** Tạo module Python chuyên nhận diện các pattern `Điều \d+`, `Khoản \d+`, `Chương [IVX]+`.
- [ ] **Hierarchical Chunker:** Cập nhật logic chia nhỏ văn bản, đảm bảo mọi chunk nhỏ nhất (`Điểm`, `Khoản`) đều chứa Metadata đường dẫn của nó (Hierarchy Tree).
- [ ] **Metadata Extraction:** Khi upload file pdf/word, cho LLM quét trang đầu tiên để tự động lấy: `Tên luật`, `Cơ quan ban hành`, `Năm`, `Hiệu lực` lưu vào Qdrant payload.

### Giai đoạn 2: Tối ưu Retrieval Pipeline với Self-Query (Tuần 2)
- [ ] **Cập nhật Query Rewriting:** Sửa prompt của bộ chuẩn hóa câu hỏi, yêu cầu output ra định dạng JSON chứa cả `search_query` (câu hỏi đã làm rõ) và `filters` (điều kiện lọc Qdrant).
- [ ] **Mapping Qdrant Filter:** Viết hàm parse `filters` từ JSON thành các object filter thực tế của thư viện Qdrant (ví dụ `models.FieldCondition`).
- [ ] **Test:** Đánh giá độ chính xác khi tìm kiếm các tài liệu có tên giống nhau nhưng khác năm ban hành.

### Giai đoạn 3: Triển khai Cross-Reference Agent (Tuần 3)
- [ ] **Agentic Retrieval Loop:** Sử dụng LangGraph hoặc luồng loop cơ bản của Langchain.
- [ ] **Prompt Detection:** Tạo một prompt nhỏ để LLM phán đoán: *"Trong những chunks vừa tìm được, có câu nào yêu cầu tham chiếu đến Điều/Khoản khác không? Nếu có, hãy trả về tên Điều/Khoản đó"*.
- [ ] **Second-hop Integration:** Nếu phát hiện tham chiếu, chạy tiếp Vector Search cho điều khoản đó, gộp hai kết quả lại và đưa vào Final Generation Prompt.

---

## 📊 4. Đánh Giá & Đo Lường (Evaluation Metrics)

Sẽ sử dụng các chỉ số sau để đánh giá độ thành công của phiên bản "Legal RAG":
1. **Context Precision (Độ chính xác ngữ cảnh):** 
   - Chunk lấy lên có đúng "Khoản", "Điều" mà user đề cập không?
   - Context có bị vỡ vụn, mất ngữ cảnh cha (Tên Điều) không?
2. **Filter Accuracy (Độ chính xác của bộ lọc):** 
   - Tỷ lệ hệ thống áp dụng đúng Filter (Ví dụ user hỏi Luật 2015, cấm lấy Luật 2020).
3. **Cross-reference Success Rate:** 
   - Khả năng hệ thống tự động tìm và giải thích các trích dẫn chéo trong câu trả lời cuối cùng.
