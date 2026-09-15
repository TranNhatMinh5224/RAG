# 🚀 NexusDoc AI - Enterprise AI Legal & Knowledge RAG

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_Store-DC382D?style=for-the-badge&logo=qdrant&logoColor=white)
![Google Gemini](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-orange?style=for-the-badge&logo=google&logoColor=white)
![Ollama](https://img.shields.io/badge/Local_LLM-Qwen_2.5_7B-black?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-Agentic_RAG-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![PaddleOCR](https://img.shields.io/badge/PaddleOCR-PP_OCRv4-blue?style=for-the-badge)
![Celery](https://img.shields.io/badge/Celery-Distributed_Task-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Production_Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Guardrails](https://img.shields.io/badge/Security-Enterprise_Guardrails-green?style=for-the-badge)

**Hệ Thống Trợ Lý AI Pháp Lý & Quản Trị Tri Thức Doanh Nghiệp Cấp Độ Agentic**  
*Bảo mật tuyệt đối • Loại bỏ ảo giác • Trích dẫn số trang chính xác • Kiến trúc Grounding kiểu Google NotebookLM*

</div>

---

## 📖 1. Giới Thiệu Tổng Quan

**NexusDoc AI (Enterprise AI Legal & Knowledge RAG)** là giải pháp phần mềm cấp doanh nghiệp cho phép người dùng và tổ chức tương tác, tra cứu, phân tích và trích xuất tri thức từ kho tài liệu nội bộ (Văn bản Pháp luật, Quy chế, Hợp đồng, Hồ sơ kỹ thuật, Báo cáo y tế...) một cách nhanh chóng, an toàn và chính xác tuyệt đối.

Lấy cảm hứng từ trải nghiệm đột phá của **Google NotebookLM**, hệ thống cho phép người dùng tự do gán **"Vùng tri thức" (Document-scoped Context)** cho từng phiên trò chuyện, kết hợp cơ chế kiểm soát an toàn 2 tầng (**Enterprise Security Guardrails**) để loại bỏ hoàn toàn hiện tượng AI bịa đặt thông tin (*hallucination*), bảo vệ dữ liệu bí mật và ngăn chặn tấn công Prompt Injection.

---

## 🌟 2. Các Tính Năng Nổi Bật

### 🔐 1. Quản trị Định danh & Multi-Tenant Isolation
* **Xác thực an toàn OAuth2**: Cấp phát và luân chuyển bộ đôi **Access Token** & **Refresh Token** (JWT).
* **Cô lập dữ liệu nghiêm ngặt**: Dữ liệu tài liệu, vector embedding và lịch sử chat của từng người dùng/tổ chức được cô lập hoàn toàn (*Zero data leakage across tenants*).
* Quản lý thông tin tài khoản, đổi mật khẩu, cấp lại mật khẩu và băm mật khẩu chuẩn bcrypt.

### 📑 2. Xử lý & Phân tích Tài liệu Đa định dạng
* **Hỗ trợ toàn diện các định dạng**: `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.png`, `.jpg`.
* **Tích hợp PaddleOCR (PP-OCRv4)**: Tự động trích xuất chữ viết có độ chính xác cao từ hình ảnh scan, tài liệu chụp máy ảnh và infographic.
* **Hierarchical Legal Chunking**: Thuật toán phân tích cú pháp phân cấp chuyên biệt cho văn bản Pháp luật Việt Nam, nhận diện cấu trúc `Chương → Điều → Khoản → Điểm`, tự động kế thừa tiêu đề ngữ cảnh cha vào từng chunk nhỏ để không bị mất gốc nghĩa.
* **Semantic Chunking Fallback**: Với văn bản tài liệu thông thường, áp dụng phân đoạn theo biến thiên ngữ nghĩa (ngưỡng phân vị 80%).
* **Chuyển đổi bảng biểu**: Tự động parse bảng tính Excel và bảng Word thành định dạng Markdown có cấu trúc để LLM dễ đọc hiểu.

### 💬 3. Trải Nghiệm Hội Thoại Kiểu "NotebookLM"
* Mỗi cuộc hội thoại là một không gian làm việc độc lập. Người dùng có thể tích chọn 1 hoặc nhiều tài liệu cụ thể để tạo **Vùng tri thức riêng**.
* **Định vị trích dẫn chính xác (Grounding Citations)**: Mọi câu trả lời của AI đều đính kèm nguồn gốc và số trang minh bạch (ví dụ: `[Nguồn: Bao_cao_Y_te.docx - Trang 3]`).
* **Hỗ trợ Streaming Token**: Hiển thị phản hồi thời gian thực mượt mà qua Server-Sent Events (SSE).

### 🛡️ 4. Hệ Thống Phòng Vệ 2 Tầng (Enterprise Security Guardrails)
* **Tầng 1 (Pre-flight Input Filtering - `rules/security_rules.py`)**:
  * Kiểm tra và vô hiệu hóa các nỗ lực **Prompt Injection**, **Jailbreak** (kịch bản DAN, Developer Mode, System Override, Bỏ qua chỉ dẫn trước).
  * Chặn đứng các hành vi cố tình trích xuất System Prompt, biến môi trường, khóa API (`GEMINI_API_KEY`) hay chuỗi kết nối Database.
* **Tầng 2 (Hardened System Prompts & Grounding - `rules/prompt_rules.py`)**:
  * **Chống Indirect Prompt Injection**: Coi toàn bộ nội dung tài liệu trích xuất là dữ liệu tham khảo, không thực thi mệnh lệnh ẩn giấu bên trong file.
  * **Strict Grounding**: Ép buộc LLM chỉ trả lời khi có bằng chứng trực tiếp trong ngữ cảnh tìm được; từ chối phỏng đoán khi tài liệu không đề cập.
  * **Giao tiếp thân thiện thông minh**: Tự động nhận diện các câu chào hỏi xã giao (Hello, Hi, Bạn là ai...) để phản hồi lịch sự, tự nhiên mà không kích hoạt cảnh báo an toàn giả tạo.

---

## 🏗️ 3. Kiến Trúc Hệ Thống (Architecture Overview)

Hệ thống được thiết kế theo kiến trúc Microservices phân lớp, dễ dàng mở rộng và sẵn sàng triển khai trên Docker / Kubernetes / Cloud AWS:

```
                                    ┌────────────────────────┐
                                    │   React 18 Frontend    │
                                    │ (Vite / Tailwind / UI) │
                                    └───────────┬────────────┘
                                                │ HTTP / SSE
                                                ▼
                                    ┌────────────────────────┐
                                    │    Nginx / Ingress     │
                                    └───────────┬────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                FastAPI Backend Services                                │
│  ┌──────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────┐  │
│  │   Auth & Identity    │   │      Document Ingest      │   │   Agentic RAG Engine  │  │
│  │   (JWT / OAuth2)     │   │ (PaddleOCR / LegalParser) │   │ (Hybrid / Re-ranking) │  │
│  └──────────────────────┘   └─────────────┬─────────────┘   └───────────┬───────────┘  │
│                                           │                             │              │
│  ┌────────────────────────────────────────┴─────────────────────────────┴───────────┐  │
│  │  Enterprise Guardrails (Input Regex Filter + Hardened Grounding System Prompts)  │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└──────────────┬────────────────────────────┬─────────────────────────────┬──────────────┘
               │ Async Tasks                │ Embeddings / Search         │ Relational Data
               ▼                            ▼                             ▼
┌──────────────────────────────┐  ┌──────────────────┐          ┌───────────────────┐
│ Redis Queue + Celery Worker  │  │  Qdrant Vector   │          │    PostgreSQL     │
│ (Background Document Parser) │  │ (BAAI/bge-m3 1024d)│        │ (Users, History,  │
└──────────────────────────────┘  └──────────────────┘          │  Metadata, Scopes)│
                                                                └───────────────────┘
```

---

## 🧠 4. Phân Tích Chuyên Sâu Pipeline RAG (Deep Dive)

Quy trình RAG của NexusDoc AI được chuẩn hóa qua 3 chặng nghiêm ngặt:

```
[Upload File] ──► [PaddleOCR / Parser] ──► [Legal / Semantic Chunking] ──► [BAAI/bge-m3] ──► [Qdrant]
                                                                                                 │
[User Query] ──► [Security Guardrails] ──► [Self-Query & Filters] ──► [Hybrid Search (Dense+BM25)]
                                                                               │
[Answer + Citation] ◄── [LLM Generation] ◄── [Cross-Reference Agent] ◄── [BGE-Reranker-v2-m3]
```

### Chặng 1: Ingestion Pipeline (Nạp & Xử lý Tài liệu)
1. **Trích xuất văn bản**: Kết hợp `PyMuPDF` (cho tài liệu số hóa) và **PaddleOCR** (cho ảnh scan/tài liệu chụp).
2. **Hierarchical Legal Chunking**:
   * Nhận diện tiêu đề: `Chương`, `Mục`, `Điều`, `Khoản`, `Điểm`.
   * Tạo chuỗi breadcrumb: `[Luật Doanh nghiệp 2020] > [Chương II] > [Điều 17] > Khoản 1: ...`
   * Đảm bảo mọi đoạn trích xuất khi đưa vào mô hình nhúng đều giữ trọn ngữ cảnh phân cấp cha.
3. **Embedding Vector**: Sử dụng mô hình cục bộ **`BAAI/bge-m3`** (Vector 1024 chiều) với khả năng biểu diễn ngữ nghĩa tiếng Việt vượt trội.

### Chặng 2: Retrieval Pipeline (Truy xuất Đa Tầng Cấp Độ Agentic)
1. **Self-Query Retriever**: Trích xuất metadata từ câu hỏi (Năm ban hành, loại văn bản) và biến thành bộ lọc cứng (*Hard Filters*) áp thẳng vào payload của Qdrant.
2. **Hybrid Search**: Quét đồng thời tìm kiếm ngữ nghĩa (Dense Vector Search) và tìm kiếm từ khóa chính xác (Sparse BM25) để thu về **Top 15** chunks ứng viên.
3. **Cross-Encoder Re-ranking**: Mô hình **`BAAI/bge-reranker-v2-m3`** đóng vai trò trọng tài, chấm điểm lại sự phù hợp ngữ cảnh để giữ lại **Top 3 - 5** đoạn văn bản tinh túy nhất.
4. **Cross-Reference Agent (Truy xuất đệ quy - Second-hop)**:
   * Agent tự động đọc Top 3 chunks xem có chứa các điều khoản tham chiếu chéo (*ví dụ: "Xử phạt theo điểm a khoản 2 Điều 15"*) hay không.
   * Nếu phát hiện có tham chiếu chéo mà nội dung chưa đủ, Agent tự động kích hoạt lượt tìm kiếm thứ hai (*Second-hop search*) để kéo nội dung Điều 15 vào ngữ cảnh trước khi trả lời.

### Chặng 3: Generation Pipeline (Sinh Phản Hồi Có Trích Dẫn)
1. **Context Assembly**: Ghép cấu trúc cây tài liệu, lịch sử tóm tắt và hội thoại gần nhất vào prompt được gia cố.
2. **Context Cache Service**: Tận dụng cơ chế lưu bộ đệm ngữ cảnh giúp giảm độ trễ và tiết kiệm chi phí gọi LLM.
3. **Mô hình LLM linh hoạt**: 
   * Mặc định sử dụng **Google Gemini 2.5 Flash** (tốc độ cao, suy luận sắc bén, hỗ trợ context lớn).
   * Hỗ trợ chuyển đổi sang **Ollama (Qwen 2.5 7B)** khi vận hành hoàn toàn Offline/On-premise.

---

## 📂 5. Cấu Trúc Thư Mục Dự Án

```text
RAG/
├── data/                         # Thư mục lưu trữ tài liệu local / sample files
├── qdrant_data/                  # Dữ liệu volume của Qdrant Vector Store
├── Office/                       # Hình ảnh chụp màn hình giao diện hệ thống
│   ├── 1.png                     # Giao diện Chatbot & Trích dẫn nguồn
│   ├── 2.png                     # Quản lý tài liệu & gán vùng tri thức
│   ├── 3.png                     # Phân tích văn bản pháp lý chuyên sâu
│   └── 4.png                     # Quản trị hệ thống & phân quyền
├── src/
│   ├── backend/                  # Mã nguồn FastAPI Backend
│   │   ├── api/                  # API Endpoints (Auth, Chat, Document, Conversation)
│   │   ├── core/                 # Cấu hình bảo mật, JWT, Database, Celery App
│   │   ├── models/               # SQLAlchemy Models & Pydantic Schemas
│   │   ├── repositories/         # Database Access Layer (Repository Pattern)
│   │   ├── rules/                # Bộ quy tắc bảo mật & Prompt Hardening
│   │   │   ├── prompt_rules.py   # System Prompts, Chitchat handling & Grounding rules
│   │   │   └── security_rules.py # Pre-flight Input Guardrails (Chống Injection & Jailbreak)
│   │   ├── services/             # Business Logic Layer
│   │   │   ├── chat_service.py   # Điều phối luồng chat & SSE Streaming
│   │   │   ├── document_processor.py # Xử lý đa định dạng & trích xuất chữ
│   │   │   ├── legal_parser.py   # Bộ phân tích cú pháp văn bản Luật (Hierarchical)
│   │   │   ├── llm_chain.py      # Tích hợp Gemini & LangChain Chains
│   │   │   ├── retriever.py      # Hybrid Search, Re-ranking & Cross-Reference Agent
│   │   │   ├── vector_store.py   # Tương tác Qdrant Client & Payload Filters
│   │   │   └── context_cache_service.py # Quản lý bộ nhớ đệm ngữ cảnh
│   │   ├── main.py               # Điểm khởi chạy ứng dụng FastAPI
│   │   ├── requirements.txt      # Thư viện Python phụ thuộc
│   │   └── Dockerfile            # Dockerfile cho Backend
│   └── frontend/                 # Mã nguồn Giao diện React Vite
│       ├── src/
│       │   ├── api/              # Axios API Service & Endpoints
│       │   ├── components/       # Các UI Component dùng chung
│       │   ├── features/         # Module tính năng (ChatWindow, Sidebar, DocModal)
│       │   ├── contexts/         # React Context (AuthContext, ThemeContext)
│       │   └── pages/            # Trang Dashboard, Login, Register
│       ├── package.json          # Dependencies Frontend
│       └── Dockerfile            # Dockerfile cho Frontend
├── docker-compose.yml            # Docker Compose chạy toàn bộ hệ thống
├── docker-compose.dev.yml        # Docker Compose môi trường Development
├── docker-compose.prod.yml       # Docker Compose môi trường Production
├── start_all.bat                 # Script 1-click khởi chạy toàn bộ trên Windows
├── start_dev.ps1                 # Script PowerShell chạy môi trường Dev
├── test_rag_e2e.py               # Kịch bản kiểm thử tự động toàn trình End-to-End
├── benchmark_results.json        # Kết quả đánh giá hiệu năng & độ chính xác RAG
└── README.md                     # Tài liệu hướng dẫn dự án
```

---

## 📸 6. Hình Ảnh Giao Diện & Bằng Chứng Thực Nghiệm (UI Showcase)

<div align="center">

### 1. Giao diện Trò chuyện Tra cứu & Đối chiếu Nguồn Trích dẫn (Grounded Citations)
*NexusDoc AI tự động đính kèm số trang, tên tài liệu gốc và trích dẫn chuẩn xác, loại bỏ hoàn toàn hiện tượng bịa đặt thông tin.*  
![Trích dẫn nguồn chính xác](Office/nexusdoc_chat_citation.png)

---

### 2. Trích xuất Thực thể & Tóm tắt Nghiệp vụ Phức tạp
*Hệ thống phân tích ngữ cảnh sâu, tổng hợp và trả lời nhanh chóng các câu hỏi nghiệp vụ đặc thù.*  
![Trích xuất thực thể](Office/nexusdoc_chat_product.png)

---

### 3. Kiểm thử Rào chắn An toàn (Enterprise Security Guardrails in Action)
*Khi người dùng đặt câu hỏi nằm ngoài phạm vi tài liệu (ví dụ: tra cứu giá cổ phiếu ngoài Internet), hệ thống kích hoạt Guardrail từ chối lịch sự, kiên định tuân thủ nguyên tắc bảo mật và tri thức doanh nghiệp.*  
![Kiểm thử Security Guardrails](Office/nexusdoc_guardrail_demo.png)

---

### 4. Quản lý Kho Tài liệu & Thiết lập "Vùng Tri Thức" kiểu NotebookLM
*Người dùng có thể linh hoạt tải lên nhiều định dạng file (PDF, Word, Excel, Hình ảnh) và gán tài liệu cho từng phiên hội thoại.*  
![Quản lý tài liệu](Office/2.png)

---

### 5. Phân tích Cấu trúc Phân cấp Văn bản Pháp luật (Hierarchical Parser)
*Hệ thống tự động bóc tách theo Chương, Điều, Khoản, bảo tồn quan hệ phả hệ ngữ cảnh cha.*  
![Phân tích cấu trúc](Office/3.png)

---

### 6. Giám sát Vận hành & Hiệu Năng Hệ thống (CloudWatch Observability)
*Theo dõi trực quan thời gian thực số lượng yêu cầu, độ trễ phản hồi (Response Time), tài nguyên CPU/RAM và tỷ lệ lỗi.*  
![CloudWatch Dashboard RAG](Office/cloudwatch_dashboard_rag.png)

---

### 7. Bảng điều khiển Quản trị & Lịch sử Hội thoại
*Quản trị người dùng, phân quyền bảo mật multi-tenant và xem lại toàn bộ lịch sử tương tác.*  
![Quản trị hệ thống](Office/4.png)

</div>

---

## 📊 7. Đánh Giá & Đo Lường Hiệu Năng (Benchmark Results)

Hệ thống được đánh giá định kỳ thông qua bộ kịch bản kiểm thử tự động `test_rag_e2e.py` trên tập câu hỏi thực tế đa cấp độ (từ câu hỏi sự thật factual đến câu hỏi suy luận phức tạp và câu hỏi gài bẫy). 

Kết quả ghi nhận từ `benchmark_results.json`:

| Chỉ số Đánh giá | Kết quả Đạt được | Ý nghĩa Thực tiễn |
| :--- | :---: | :--- |
| **Tỷ lệ vượt qua (Pass Rate)** | **100.0%** (10/10) | Vượt qua toàn bộ các bài kiểm tra thực tế không có lỗi. |
| **Điểm số trung bình (Average Score)** | **9.4 / 10.0** | Độ chính xác câu trả lời và mức độ bao phủ thông tin gần như tuyệt đối. |
| **Độ trung thực (Faithfulness / Zero-Hallucination)** | **100.0%** | Không có hiện tượng bịa đặt thông tin ngoài tài liệu. |
| **Độ chính xác trích dẫn (Citation Accuracy)** | **100.0%** | 100% câu trả lời đều đính kèm tên file và số trang tương ứng. |
| **Phản hồi câu hỏi gài bẫy (Trap Handling)** | **Xuất sắc** | Từ chối trả lời chính xác khi dữ liệu không có trong tài liệu. |

---

## 🚀 8. Hướng Dẫn Cài Đặt & Khởi Chạy

### Yêu cầu tiên quyết
* Hệ điều hành: Windows 10/11, macOS, hoặc Linux.
* [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) (Khuyến nghị Docker Desktop).
* [Python 3.10+](https://www.python.org/downloads/) và [Node.js 18+](https://nodejs.org/).
* Khóa API Google Gemini (lấy miễn phí tại [Google AI Studio](https://aistudio.google.com/)).

---

### Cách 1: Khởi chạy 1-Click bằng Script (Khuyến nghị trên Windows)

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd RAG
   ```

2. **Cấu hình môi trường (`.env`)**:
   Tạo file `.env` tại thư mục gốc từ `.env.example`:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag_db
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your_super_secret_jwt_key
   ```

3. **Chạy script tự động**:
   * **Cách A (Khởi chạy toàn bộ hệ thống)**:
     ```cmd
     start_all.bat
     ```
   * **Cách B (Môi trường Development qua PowerShell)**:
     ```powershell
     .\start_dev.ps1
     ```

Script sẽ tự động kiểm tra Docker containers (PostgreSQL, Qdrant, Redis), khởi động Celery Background Worker, FastAPI Backend và React Frontend trên các cửa sổ riêng biệt.

---

### Cách 2: Khởi chạy hoàn toàn bằng Docker Compose

Nếu muốn đóng gói và chạy toàn bộ dịch vụ trong Docker containers:

```bash
# Khởi chạy toàn bộ hạ tầng và ứng dụng
docker compose up -d --build
```

Để kiểm tra trạng thái các containers đang chạy:
```bash
docker compose ps
```

Dừng toàn bộ hệ thống:
```bash
docker compose down
```

---

## 🌐 9. Địa Chỉ Truy Cập Dịch Vụ

Sau khi hệ thống khởi động thành công:

| Dịch vụ | Địa chỉ truy cập | Mô tả chức năng |
| :--- | :--- | :--- |
| **Giao diện Người dùng (Frontend)** | `http://localhost:5173` *(hoặc `http://localhost:3000`)* | Ứng dụng chat, quản lý tài liệu và vùng tri thức. |
| **Tài liệu API (Swagger UI)** | `http://localhost:8000/docs` | Kiểm thử và xem chi tiết tất cả RESTful APIs. |
| **Bảng điều khiển Vector Qdrant** | `http://localhost:6333/dashboard` | Giám sát Collections, Vector points và Payload filters. |
| **PostgreSQL Database** | `localhost:5432` | Cơ sở dữ liệu quan hệ lưu trữ User, Document & Chat History. |

---

## 🛡️ 10. Bảo Mật & Đóng Góp Ý Kiến

* **Báo cáo lỗ hổng**: Nếu phát hiện bất kỳ vấn đề bảo mật hoặc rủi ro rò rỉ dữ liệu, vui lòng mở Issue riêng hoặc liên hệ trực tiếp với tác giả.
* **Đóng góp mã nguồn**: Mọi Pull Request cải thiện tốc độ parser, tối ưu prompt guardrails hoặc nâng cấp giao diện đều được hoan nghênh.

---

<div align="center">

**Tác giả**: Trần Nhật Minh  
*Dự án phục vụ nghiên cứu & ứng dụng Trí tuệ Nhân tạo Doanh nghiệp (Enterprise AI RAG).*

</div>
