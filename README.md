# 🚀 Enterprise AI RAG - Hệ Thống Truy Vấn Tài Liệu Cục Bộ Thông Minh

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-ff5252)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini_2.5_Flash-orange)
![LangChain](https://img.shields.io/badge/LangChain-AI_Pipeline-1C3C3C?logo=langchain&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

**Enterprise AI RAG** là hệ thống giải pháp cho phép người dùng và doanh nghiệp giao tiếp trực tiếp với kho tài liệu nội bộ (PDF, Word, Excel, PowerPoint) một cách bảo mật, chính xác và loại bỏ hoàn toàn tình trạng "ảo giác" (hallucination) của AI. 

Dự án áp dụng kiến trúc **Retrieval-Augmented Generation (RAG)** tiên tiến, lấy cảm hứng từ luồng trải nghiệm của **Google NotebookLM**, cho phép người dùng tự do tuỳ biến "Vùng tri thức" cho từng cuộc trò chuyện.

---

## 🎯 1. Bối Cảnh & Giải Pháp

### Vấn đề
- **Tra cứu khó khăn:** Việc tìm kiếm một thông tin cụ thể trong hàng ngàn trang tài liệu tốn quá nhiều thời gian.
- **Hạn chế của AI thông thường:** Các mô hình như ChatGPT/Claude thiếu kiến thức nội bộ của bạn, dễ dàng bịa đặt thông tin khi không biết và tiềm ẩn rủi ro rò rỉ dữ liệu khi tải trực tiếp file lên server công cộng.

### Giải pháp RAG
Thay vì hỏi AI bằng kiến thức chung, hệ thống sẽ:
1. **Trích xuất (Retrieval):** Tìm chính xác đoạn văn bản liên quan nhất từ kho tài liệu của riêng bạn.
2. **Sinh văn bản (Generation):** Ép mô hình AI (Gemini) chỉ được phép trả lời dựa trên những dữ liệu vừa tìm được kèm theo **trích dẫn nguồn và số trang**.

---

## ⚙️ 2. Kiến Trúc Hệ Thống (Architecture)

Hệ thống được thiết kế theo kiến trúc Microservices tinh gọn, dễ dàng mở rộng và chạy hoàn toàn trong container Docker:

- **Frontend:** React (Vite) - Giao diện hiện đại, quản lý hội thoại và kho tài liệu trực quan.
- **Backend:** FastAPI (Python) - Xử lý API tốc độ cao, quản lý xác thực JWT, và điều phối luồng RAG.
- **Database:** PostgreSQL - Lưu trữ thông tin người dùng, lịch sử chat và metadata tài liệu.
- **Vector Database:** Qdrant - Lưu trữ và truy vấn ngữ nghĩa các Vector Embeddings siêu tốc.
- **AI Pipeline (Langchain):**
  - *Mô hình Nhúng (Embedding):* `BAAI/bge-m3` - Mô hình tối ưu hoá cực tốt cho Tiếng Việt, dimension 1024, chạy hoàn toàn cục bộ.
  - *Mô hình Ngôn ngữ (LLM):* `Google Gemini 2.5 Flash` - Tốc độ phản hồi cực nhanh và thông minh.

---

## ✨ 3. Tính Năng Nổi Bật

### 🔐 Quản trị Định danh & Xác thực
- Xác thực bảo mật OAuth2 với **Access Token** & **Refresh Token** (JWT).
- Quản lý phân quyền, đổi mật khẩu, quên mật khẩu và thông tin cá nhân.
- Mật khẩu được băm (hash) an toàn.

### 📂 Quản lý Tài liệu Đa định dạng
- Hỗ trợ đa dạng file: `.pdf`, `.docx`, `.xlsx`, `.pptx`.
- Thuật toán trích xuất linh hoạt: 
  - Đọc text theo trang (PDF).
  - Đọc text theo đoạn (Word).
  - Tự động chuyển đổi bảng dữ liệu thành Markdown (Excel) giúp AI đọc hiểu xuất sắc.
  - Đọc text theo từng Slide (PowerPoint).
- Xóa tài liệu đồng bộ: Xóa file khỏi Database và dọn sạch Vector Embeddings tương ứng trên Qdrant.

### 💬 Quản lý Cuộc trò chuyện "NotebookLM Style"
- Mỗi cuộc trò chuyện độc lập đều có thể được **đính kèm** với một danh sách các tài liệu (Document IDs) cụ thể.
- Hệ thống thiết lập "Vùng tri thức" giới hạn cho đoạn chat, tránh việc AI lấy nhầm dữ liệu sang các tài liệu không liên quan.
- Multi-tenant an toàn: Dữ liệu của từng User được cô lập hoàn toàn.

---

## 🧠 4. Phân Tích Pipeline AI RAG Chuyên Sâu

Dự án triển khai một Pipeline RAG cực kỳ chặt chẽ với 3 giai đoạn:

### Giai đoạn 1: Ingestion Pipeline (Nạp & Tiền xử lý dữ liệu)
- **Làm sạch:** Tự động xoá khoảng trắng, dấu xuống dòng thừa.
- **Semantic Chunking:** Không cắt văn bản cơ học theo số chữ. Sử dụng `SemanticChunker` (ngưỡng phân vị 80%) kết hợp mô hình Embedding để tính toán sự thay đổi ngữ nghĩa. Khối văn bản (Chunk) chỉ được cắt khi ý nghĩa chuyển sang một hướng khác, đảm bảo độ trọn vẹn của thông tin.
- **Embedding & Vector Storage:** Nén chunks qua mô hình `BAAI/bge-m3` (tiếng Việt xuất sắc) và lưu vào Qdrant cùng với Metadata chi tiết (`source`, `page`, `user_id`, `document_id`).

### Giai đoạn 2: Retrieval Pipeline (Truy xuất dữ liệu)
- **Hard-Filtering:** Sử dụng cơ chế Filter của Qdrant. Hệ thống sẽ bắt buộc truy vấn phải khớp với `user_id` hiện tại VÀ nằm trong mảng `document_ids` đang đính kèm vào cuộc trò chuyện.
- **Similarity Search:** Sử dụng Cosine Similarity để trích xuất ra Top 3 Chunk có ngữ nghĩa sát nhất với câu hỏi.

### Giai đoạn 3: Generation Pipeline (Sinh câu trả lời)
- **Format Context:** Tiêm metadata vào ngữ cảnh (`Tài liệu [Nguồn: ... - Trang: ...]`).
- **Memory Load:** Truy xuất 5 tin nhắn gần nhất để AI hiểu ngữ cảnh trò chuyện liên tục.
- **Prompt Engineering chống Ảo giác:** Lệnh bắt buộc AI trả lời "Tôi không tìm thấy thông tin" nếu dữ liệu không khớp. Bắt buộc để lại Trích dẫn ở cuối mỗi câu trả lời.
- **LLM Call:** Gửi tới Gemini 2.5 Flash để sinh văn bản phản hồi tự nhiên.

---


## 📂 5. Cấu Trúc Thư Mục Chính

```text
├── data/                    # Nơi chứa tài liệu người dùng upload (nếu có lưu local)
├── qdrant_data/             # Volume lưu trữ Vector Database Qdrant
├── src/
│   ├── backend/             # Source code FastAPI
│   │   ├── api/             # API Routers (auth, chat, conversation, document)
│   │   ├── core/            # Cấu hình bảo mật, setting hệ thống
│   │   ├── models/          # SQLAlchemy Models & Pydantic Schemas
│   │   ├── repositories/    # Database Repository Pattern
│   │   └── services/        # Logic Business (RAG, Processor, LLM, VectorStore)
│   └── frontend/            # Source code React Vite
│       ├── src/
│       │   ├── api/         # Axios API clients
│       │   ├── components/  # Các UI Component tái sử dụng
│       │   ├── contexts/    # React Context (Auth, Theme...)
│       │   ├── features/    # Tính năng (ChatWindow, DocumentModal, Sidebar)
│       │   └── pages/       # Các trang chính (Login, Dashboard)
├── docker-compose.yml       # Cấu hình triển khai hệ thống
└── README.md                # Tài liệu dự án
```

---

## 📸 6. Hình Ảnh Giao Diện (Screenshots)

### Chatbot trả lời 
![Giao diện 1](Office/1.png)


![Giao diện 2](Office/2.png)

![Giao diện 3](Office/3.png)


![Giao diện 4](Office/4.png)

---
## 🚀 7. Hướng Dẫn Cài Đặt (Installation)

### Yêu cầu tiên quyết
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) đã được cài đặt.
- API Key của Google Gemini.

### Các bước khởi chạy

1. **Clone repository:**
   ```bash
   git clone <your-repo-url>
   cd <repository-folder>
   ```

2. **Cấu hình môi trường (.env):**
   Tạo file `.env` tại thư mục gốc (hoặc copy từ `.env.example`) và cập nhật thông tin:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

3. **Chạy hệ thống với Docker Compose:**
   ```bash
   docker compose up -d --build
   ```
   > **Lưu ý:** Trong lần khởi chạy đầu tiên, hệ thống sẽ tự động tải các weights của mô hình `BAAI/bge-m3` về máy (khoảng 1-2GB), có thể mất 5-10 phút phụ thuộc vào tốc độ mạng.

4. **Trải nghiệm:**
   - **Giao diện người dùng (Frontend):** `http://localhost:5173`
   - **Tài liệu API Backend (Swagger UI):** `http://localhost:8000/docs`

---

*Phát triển bởi Trần Nhật Minh.*
