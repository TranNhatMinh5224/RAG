# 🚀 NexusDoc AI - Enterprise AI Legal & Knowledge RAG

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![AWS](https://img.shields.io/badge/AWS-Cloud_Native-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_Store-DC382D?style=for-the-badge&logo=qdrant&logoColor=white)
![Google Gemini](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-orange?style=for-the-badge&logo=google&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Agentic_RAG-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![PaddleOCR](https://img.shields.io/badge/PaddleOCR-PP_OCRv4-blue?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Production_Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Guardrails](https://img.shields.io/badge/Security-Enterprise_Guardrails-green?style=for-the-badge)

**Hệ Thống Trợ Lý AI Pháp Lý & Quản Trị Tri Thức Doanh Nghiệp Cấp Độ Agentic Trên Nền Tảng AWS Cloud**  
*Bảo mật tuyệt đối • Loại bỏ ảo giác • Trích dẫn số trang chính xác • Kiến trúc Grounding kiểu Google NotebookLM*

</div>

---

## 📖 1. Giới Thiệu Tổng Quan

**NexusDoc AI (Enterprise AI Legal & Knowledge RAG)** là giải pháp phần mềm cấp doanh nghiệp cho phép người dùng và tổ chức tương tác, tra cứu, phân tích và trích xuất tri thức từ kho tài liệu nội bộ (Văn bản Pháp luật, Quy chế, Hợp đồng, Hồ sơ kỹ thuật, Báo cáo y tế...) một cách nhanh chóng, an toàn và chính xác tuyệt đối.

Lấy cảm hứng từ trải nghiệm đột phá của **Google NotebookLM**, hệ thống cho phép người dùng tự do gán **"Vùng tri thức" (Document-scoped Context)** cho từng phiên trò chuyện, kết hợp cơ chế kiểm soát an toàn 2 tầng (**Enterprise Security Guardrails**) để loại bỏ hoàn toàn hiện tượng AI bịa đặt thông tin (*hallucination*), bảo vệ dữ liệu bí mật và ngăn chặn tấn công Prompt Injection.

Hệ thống được thiết kế theo tiêu chuẩn Cloud-Native và tối ưu hóa toàn diện để triển khai trên nền tảng điện toán đám mây **Amazon Web Services (AWS)** với mô hình mạng VPC Zero-Trust, cân bằng tải Application Load Balancer (ALB), cơ sở dữ liệu quan hệ RDS PostgreSQL và giám sát tự động qua Amazon CloudWatch.

---

## 🌟 2. Các Tính Năng Cốt Lõi

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
* **Định vị trích dẫn chính xác (Grounding Citations)**: Mọi câu trả lời của AI đều đính kèm nguồn gốc và số trang minh bạch (ví dụ: `[Nguồn: TTTN-01.docx - Trang 1]`).
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

## 🧠 3. Kiến Trúc Pipeline RAG & Sơ Đồ Luồng Xử Lý (RAG Deep Dive)

Quy trình RAG của NexusDoc AI được chuẩn hóa qua 3 chặng khép kín:

<div align="center">

![Sơ đồ luồng xử lý RAG & Guardrails](Office/pipeline_rag.png)  
*Hình 3.1: Sơ đồ luồng xử lý toàn trình Pipeline RAG từ Ingestion, Retrieval Đa Tầng đến Generation có Guardrails*

</div>

### Chặng 1: Ingestion Pipeline (Nạp & Tiền xử lý Dữ liệu)
1. **Trích xuất văn bản**: Kết hợp `PyMuPDF` (cho tài liệu số hóa) và **PaddleOCR** (cho ảnh scan/tài liệu chụp).
2. **Hierarchical Legal Chunking**:
   * Nhận diện tiêu đề: `Chương`, `Mục`, `Điều`, `Khoản`, `Điểm`.
   * Tạo chuỗi breadcrumb: `[Luật Doanh nghiệp 2020] > [Chương II] > [Điều 17] > Khoản 1: ...`
   * Đảm bảo mọi đoạn trích xuất khi đưa vào mô hình nhúng đều giữ trọn ngữ cảnh phân cấp cha.
3. **Embedding Vector**: Sử dụng mô hình cục bộ **`BAAI/bge-m3`** (Vector 1024 chiều) với khả năng biểu diễn ngữ nghĩa tiếng Việt vượt trội, lưu trữ trên Qdrant Vector Store.

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

## ☁️ 4. Triển Khai Hệ Thống Lên Đám Mây AWS (AWS Cloud Production Hosting)

Hệ thống NexusDoc AI được thiết kế và triển khai trên hạ tầng điện toán đám mây **Amazon Web Services (AWS)** chuẩn Enterprise, tuân thủ nghiêm ngặt khung kiến trúc **AWS Well-Architected Framework** về Bảo mật (Security), Độ tin cậy (Reliability), Hiệu năng (Performance) và Tối ưu chi phí (Cost Optimization).

<div align="center">

![Kiến trúc tổng thể AWS Multi-tier](Office/enterprise_aws_architecture.png)  
*Hình 4.1: Sơ đồ kiến trúc triển khai toàn diện của hệ thống NexusDoc AI trên nền tảng AWS Cloud*

</div>

### 4.1. Kiến Trúc Hạ Tầng Mạng VPC Zero-Trust
Toàn bộ tài nguyên được bao bọc trong một đám mây riêng ảo **Virtual Private Cloud (VPC)** với dải mạng `10.0.0.0/16`, trải dài trên **2 Availability Zones (AZs)** độc lập tại Region Singapore (`ap-southeast-1`):

* **2 Public Subnets** (`10.0.1.0/24`, `10.0.2.0/24`): Chứa Internet Gateway (IGW), NAT Gateway và **Application Load Balancer (ALB)** tiếp nhận truy cập từ bên ngoài.
* **2 Private Application Subnets** (`10.0.3.0/24`, `10.0.4.0/24`): Chứa các máy chủ ứng dụng **EC2 / ECS Fargate Task** (chạy Backend FastAPI & Vector Engine Qdrant), định tuyến ra Internet qua NAT Gateway, hoàn toàn cô lập khỏi truy cập trực tiếp từ Internet.
* **2 Isolated Database Subnets** (`10.0.5.0/24`, `10.0.6.0/24`): Chứa cụm cơ sở dữ liệu **Amazon RDS PostgreSQL**, không có route ra Internet Gateway hay NAT Gateway.

<div align="center">

![Sơ đồ phân bổ VPC Resource Map](Office/aws_vpc_resource_map.png)  
*Hình 4.2: Sơ đồ phân bổ tài nguyên VPC Resource Map thực tế trên AWS Management Console*

</div>

---

### 4.2. Ma Trận Tường Lửa Trạng Thái (Security Groups Chaining)
Áp dụng nguyên tắc phòng thủ đa tầng (**Defense-in-Depth**), các Security Groups được liên kết chuỗi (*chaining*) trực tiếp theo ID thay vì mở dải IP:

```
[Internet: Port 80/443] 
        │
        ▼
┌──────────────────┐       Port 8000 (API) / 3000 (UI)        ┌──────────────────┐
│   rag-alb-sg     │ ───────────────────────────────────────► │   rag-ec2-sg     │
│ (Security Group) │                                          │ (Security Group) │
└──────────────────┘                                          └────────┬─────────┘
                                                                       │ Port 5432 (PostgreSQL)
                                                                       │ (Chỉ cho phép rag-ec2-sg)
                                                                       ▼
                                                              ┌──────────────────┐
                                                              │   rag-rds-sg     │
                                                              │ (Security Group) │
                                                              └──────────────────┘
```

* **`rag-alb-sg`**: Mở cổng `80` (HTTP) và `443` (HTTPS) từ `0.0.0.0/0`.
* **`rag-ec2-sg`**: Chỉ mở cổng `8000` (FastAPI) và `3000` (Next.js) nhận request từ **`rag-alb-sg`**; cổng `22` (SSH) giới hạn theo IP quản trị viên.
* **`rag-rds-sg`**: Cổng `5432` **chỉ chấp nhận kết nối duy nhất từ `rag-ec2-sg`**. Ngăn chặn hoàn toàn mọi nguy cơ dò quét từ bên ngoài.

---

### 4.3. Tầng Dữ Liệu & Quản Trị Khóa Bí Mật (Data, Vector & Secrets)

<div align="center">

![Cấu hình RDS PostgreSQL](Office/aws_rds_postgresql.png)  
*Hình 4.3: Thông số cấu hình thực tế của cụm cơ sở dữ liệu Amazon RDS PostgreSQL (db.t4g.micro)*

</div>

* **Amazon RDS PostgreSQL**: Triển khai phiên bản PostgreSQL 18.3 (`db.t4g.micro`) với Multi-AZ readiness, lưu trữ dữ liệu quan hệ, thông tin phân quyền người dùng, metadata tài liệu và lịch sử hội thoại.
* **Amazon S3 Storage**: Tạo S3 Bucket `enterprise-rag-storage-0117967` tại Singapore, kích hoạt **Block Public Access 100%**, phân cấp thư mục tiền tố `draff/` (tài liệu thô nạp vào) và `real/` (tài liệu chính thức sau chuẩn hóa).
* **AWS Secrets Manager**: Quản lý tập trung các khóa nhạy cảm (`DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET_KEY`), tự động mã hóa bằng AWS KMS.
* **IAM Role `EC2-S3-RAG`**: Máy chủ EC2 tự động lấy temporary token qua AWS Security Token Service (STS) để đọc ghi S3 và ECR mà không cần lưu cứng Access Key/Secret Key trong mã nguồn.

---

### 4.4. Đóng Gói Container & Kho Lưu Trữ Amazon ECR

<div align="center">

![Amazon ECR Repositories](Office/aws_ecr_repositories.png)  
*Hình 4.4: Danh sách các Private Container Repositories trên Amazon Elastic Container Registry (ECR)*

</div>

Mã nguồn được đóng gói bằng Docker nhiều giai đoạn (Multi-stage build) để tối ưu dung lượng image và đẩy lên các kho lưu trữ bảo mật **Amazon Elastic Container Registry (ECR)**:
* `enterprise-rag-backend`: Chứa FastAPI, LangChain, PaddleOCR và các dependencies AI.
* `enterprise-rag-frontend`: Chứa ứng dụng React / Next.js được tối ưu hóa tĩnh.

---

### 4.5. Cân Bằng Tải & Định Tuyến (Application Load Balancer)

<div align="center">

![Application Load Balancer Details](Office/aws_alb_active.png)  
*Hình 4.5: Trạng thái hoạt động Active của Application Load Balancer (rag-lb) trên AWS*

</div>

Hệ thống sử dụng **Application Load Balancer (ALB)** mang tên `rag-lb`, hoạt động ở Tầng 7 (Application Layer) với cơ chế định tuyến thông minh theo đường dẫn (**Path-based Routing**):

| Thứ tự Ưu tiên | Quy tắc Path Condition | Target Group chuyển tiếp | Cổng dịch vụ | Mục đích |
| :---: | :--- | :--- | :---: | :--- |
| **Priority 1** | Path is `/api/*` | `rag-backend-tg` | Port 8000 | Định tuyến toàn bộ REST APIs và SSE chat stream tới FastAPI |
| **Default Rule** | Mọi request còn lại (`/*`) | `rag-frontend-tg` | Port 3000 | Phục vụ giao diện người dùng Next.js / React |

<div align="center">

![Target Groups Healthy Status](Office/aws_alb_targets_healthy.png)  
*Hình 4.6: Kết quả Health Check tự động xác nhận toàn bộ Targets trong Target Group đều ở trạng thái Healthy (Cổng 8000)*

</div>

* **Cơ chế Health Check tự động**: ALB định kỳ gửi HTTP GET đến endpoint `/api/health` mỗi 30 giây. Nếu một instance gặp sự cố, ALB sẽ tự động ngắt kết nối và điều phối traffic sang instance dự phòng.

---

### 4.6. Giám Sát Vận Hành & Cảnh Báo Sự Cố (CloudWatch & SNS)

<div align="center">

![CloudWatch Dashboard RAG](Office/cloudwatch_dashboard_rag.png)  
*Hình 4.7: Bảng điều khiển giám sát trực quan hóa thời gian thực Dashboard-RAG trên Amazon CloudWatch*

</div>

* **CloudWatch Dashboard (`Dashboard-RAG`)**: Trực quan hóa 24/7 các chỉ số vận hành trọng yếu:
  * `RequestCount`: Tổng lưu lượng truy cập qua ALB.
  * `TargetResponseTime`: Độ trễ xử lý API của backend.
  * `HTTPCode_Target_4XX_Count` & `5XX_Count`: Tỷ lệ mã lỗi phát sinh.
  * `CPUUtilization`: Tải CPU máy chủ xử lý tác vụ RAG.
* **CloudWatch Alarms & Amazon SNS**:
  * Thiết lập cảnh báo tự động `EC2-High-CPU-Alarm`: Khi mức sử dụng CPU vượt ngưỡng **80%** liên tục trong 5 phút, hệ thống tự động kích hoạt trạng thái **ALARM**.
  * Bắn thông báo cảnh báo tức thời qua **Amazon Simple Notification Service (SNS)** Topic `RAG-Alerts-Topic` tới email của đội ngũ kỹ sư trực ca on-call.

<div align="center">

![CloudWatch Alarm Created Success](Office/cloudwatch_alarm_success.png)  
*Hình 4.8: Cấu hình thành công CloudWatch Alarm kích hoạt thông báo qua SNS Topic khi CPU vượt ngưỡng*

</div>

---

### 4.7. Hướng Dẫn Các Bước Host Hệ Thống Lên AWS (AWS Hosting Runbook)

Để triển khai toàn bộ hệ thống NexusDoc AI từ mã nguồn lên tài khoản AWS của bạn:

#### Bước 1: Khởi tạo Hạ tầng Mạng (VPC & Security Groups)
1. Truy cập **VPC Console** $\rightarrow$ chọn **Create VPC** (chọn *VPC and more*), nhập CIDR `10.0.0.0/16`, tạo 2 Public Subnets, 2 Private Subnets và 2 Isolated DB Subnets trên 2 AZs (`ap-southeast-1a`, `ap-southeast-1b`).
2. Khởi tạo 3 Security Groups (`rag-alb-sg`, `rag-ec2-sg`, `rag-rds-sg`) và cấu hình Inbound Rules theo ma trận liên kết chuỗi tại mục 4.2.

#### Bước 2: Triển khai CSDL RDS PostgreSQL & Khóa Bí Mật
1. Truy cập **RDS Console** $\rightarrow$ chọn **Create database** $\rightarrow$ **PostgreSQL** (version 18.3, template *Free Tier*, instance `db.t4g.micro`).
2. Gán Subnet Group nằm trong 2 Isolated Subnets và gắn Security Group `rag-rds-sg`.
3. Truy cập **AWS Secrets Manager** $\rightarrow$ lưu trữ bí mật `enterprise-rag-secrets` chứa `DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET`.

#### Bước 3: Đóng gói Docker & Đẩy lên Amazon ECR
1. Khởi tạo 2 repositories trên **Amazon ECR**: `enterprise-rag-backend` và `enterprise-rag-frontend`.
2. Đăng nhập Docker CLI vào ECR Registry và thực hiện build & push images:
   ```bash
   # 1. Xác thực Docker với Amazon ECR
   aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.ap-southeast-1.amazonaws.com

   # 2. Build và push Backend Image
   docker build -t enterprise-rag-backend ./src/backend
   docker tag enterprise-rag-backend:latest <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.ap-southeast-1.amazonaws.com/enterprise-rag-backend:latest
   docker push <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.ap-southeast-1.amazonaws.com/enterprise-rag-backend:latest

   # 3. Build và push Frontend Image
   docker build -t enterprise-rag-frontend ./src/frontend
   docker tag enterprise-rag-frontend:latest <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.ap-southeast-1.amazonaws.com/enterprise-rag-frontend:latest
   docker push <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.ap-southeast-1.amazonaws.com/enterprise-rag-frontend:latest
   ```

#### Bước 4: Khởi chạy Máy chủ Ứng dụng & Gán IAM Role
1. Khởi chạy máy chủ EC2 (hoặc ECS Fargate Task) đặt tại Private Subnet, gán Security Group `rag-ec2-sg`.
2. Gán **IAM Role `EC2-S3-RAG`** (chứa chính sách `AmazonS3FullAccess` và quyền đọc Secrets Manager) cho instance.
3. Kéo Docker images từ ECR về và khởi chạy container thông qua `docker-compose.prod.yml`.

#### Bước 5: Cấu hình ALB, Định tuyến Path-based Routing & Kích hoạt CloudWatch
1. Tạo **Application Load Balancer (ALB)** `rag-lb` gắn vào 2 Public Subnets với Security Group `rag-alb-sg`.
2. Tạo 2 Target Groups:
   * `rag-backend-tg`: Type Instance, Protocol HTTP, Port 8000, Health Check path `/api/health`.
   * `rag-frontend-tg`: Type Instance, Protocol HTTP, Port 3000, Health Check path `/`.
3. Cấu hình Listener HTTP:80 trên ALB với quy tắc Path-based routing:
   * Rule 1: IF Path is `/api/*` $\rightarrow$ Forward to `rag-backend-tg`.
   * Default Rule: Forward to `rag-frontend-tg`.
4. Tạo Dashboard `Dashboard-RAG` trên CloudWatch và tạo Alarm gửi thông báo qua SNS Topic `RAG-Alerts-Topic`.

---

## 📸 5. Hình Ảnh Giao Diện & Bằng Chứng Thực Nghiệm (UI Showcase)

Toàn bộ các hình ảnh dưới đây được ghi nhận trực tiếp từ phiên chạy thực tế của hệ thống NexusDoc AI trên môi trường triển khai AWS:

<div align="center">

### 1. Giao diện Trò chuyện Tra cứu & Đối chiếu Nguồn Trích dẫn (Grounded Citations)
*NexusDoc AI tự động đính kèm số trang, tên tài liệu gốc và trích dẫn chuẩn xác từ văn bản `TTTN-01.docx`, loại bỏ hoàn toàn hiện tượng bịa đặt thông tin.*  
![Trích dẫn nguồn chính xác](Office/nexusdoc_chat_citation.png)

---

### 2. Trích xuất Thực thể & Tóm tắt Nghiệp vụ Phức tạp
*Hệ thống phân tích ngữ cảnh sâu, tổng hợp và trả lời nhanh chóng các câu hỏi nghiệp vụ đặc thù về mục tiêu và sản phẩm dự kiến.*  
![Trích xuất thực thể](Office/nexusdoc_chat_product.png)

---

### 3. Kiểm thử Rào chắn An toàn (Enterprise Security Guardrails in Action)
*Khi người dùng đặt câu hỏi nằm ngoài phạm vi tài liệu (tra cứu giá cổ phiếu Amazon ngoài Internet), hệ thống kích hoạt Guardrail từ chối lịch sự, kiên định tuân thủ nguyên tắc bảo mật và tri thức doanh nghiệp.*  
![Kiểm thử Security Guardrails](Office/nexusdoc_guardrail_demo.png)

---

### 4. Giám sát Vận hành & Hiệu Năng Thời Gian Thực (CloudWatch Dashboard)
*Bảng điều khiển theo dõi trực quan số lượng request, độ trễ phản hồi (Target Response Time) và trạng thái tài nguyên hệ thống.*  
![CloudWatch Dashboard](Office/cloudwatch_dashboard_rag.png)

</div>

---

## 📊 6. Đánh Giá & Đo Lường Hiệu Năng (Benchmark Results)

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

## 📂 7. Cấu Trúc Thư Mục Dự Án

```text
RAG/
├── data/                         # Thư mục lưu trữ tài liệu local / sample files
├── qdrant_data/                  # Dữ liệu volume của Qdrant Vector Store
├── Office/                       # Hình ảnh giao diện thực tế và kiến trúc hạ tầng AWS
│   ├── enterprise_aws_architecture.png # Sơ đồ kiến trúc tổng thể trên AWS Cloud
│   ├── pipeline_rag.png          # Sơ đồ luồng xử lý RAG & Guardrails chuyên sâu
│   ├── nexusdoc_chat_citation.png # UI Chatbot trích dẫn số trang chính xác
│   ├── nexusdoc_chat_product.png # UI Trích xuất thông tin nghiệp vụ
│   ├── nexusdoc_guardrail_demo.png # UI Kiểm thử rào chắn an toàn Guardrails
│   ├── aws_vpc_resource_map.png  # Sơ đồ phân bổ VPC Subnets & Routing Tables
│   ├── aws_rds_postgresql.png    # Cấu hình CSDL Amazon RDS PostgreSQL
│   ├── aws_ecr_repositories.png  # Kho lưu trữ Container Images Amazon ECR
│   ├── aws_alb_active.png        # Cấu hình Application Load Balancer (ALB)
│   ├── aws_alb_targets_healthy.png # Bản đồ phân phối Targets Healthy của ALB
│   ├── cloudwatch_dashboard_rag.png # Bảng điều khiển giám sát CloudWatch thời gian thực
│   └── cloudwatch_alarm_success.png # Cấu hình CloudWatch Alarms & thông báo qua SNS
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

## 💻 8. Hướng Dẫn Cài Đặt & Khởi Chạy Cục Bộ (Local Development)

Nếu muốn trải nghiệm hoặc phát triển ứng dụng ở môi trường Local:

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
   * **Khởi chạy toàn bộ hệ thống**:
     ```cmd
     start_all.bat
     ```
   * **Môi trường Development qua PowerShell**:
     ```powershell
     .\start_dev.ps1
     ```

---

### Cách 2: Khởi chạy hoàn toàn bằng Docker Compose

```bash
# Khởi chạy toàn bộ hạ tầng và ứng dụng
docker compose up -d --build

# Kiểm tra trạng thái containers
docker compose ps

# Dừng hệ thống
docker compose down
```

---

## 🌐 9. Danh Mục Cổng Truy Cập Dịch Vụ

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
*Dự án phục vụ nghiên cứu & ứng dụng Trí tuệ Nhân tạo Doanh nghiệp (Enterprise AI RAG trên nền tảng AWS).*

</div>
