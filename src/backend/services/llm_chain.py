import re
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import settings

class QueryFilter(BaseModel):
    search_query: str = Field(description="Câu hỏi độc lập, rõ nghĩa đã được viết lại")
    year: Optional[int] = Field(description="Năm ban hành văn bản (nếu người dùng có nhắc đến), nếu không để null", default=None)
    doc_type: Optional[str] = Field(description="Loại văn bản (Luật, Nghị định, Thông tư...) nếu nhắc đến, nếu không để null", default=None)

class CrossReference(BaseModel):
    needs_lookup: bool = Field(description="Trả về True nếu văn bản có chứa yêu cầu tham chiếu (Ví dụ: 'Theo Điều X') mà nội dung Điều X KHÔNG có sẵn trong ngữ cảnh. Trả về False nếu không cần.")
    reference_queries: list[str] = Field(description="Danh sách các truy vấn tìm kiếm bổ sung để lấy các Điều/Khoản bị thiếu.", default=[])

try:
    from langfuse.callback import CallbackHandler
    HAS_LANGFUSE = True
except ImportError:
    HAS_LANGFUSE = False

class RAGChain:
    def __init__(self, retriever):
        """Khởi tạo RAG Chain, nhận Retriever từ bên ngoài (Dependency Injection)"""
        self.retriever = retriever
        
        if settings.USE_LOCAL_LLM:
            from langchain_ollama import ChatOllama
            print(f"🚀 Khởi tạo Local LLM Ollama: '{settings.OLLAMA_MODEL}' tại {settings.OLLAMA_BASE_URL}...")
            self.llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.1,
            )
        else:
            # Lấy API Key từ cấu hình tập trung
            gemini_api_key = settings.GEMINI_API_KEY
            if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
                raise ValueError("Vui lòng cấu hình GEMINI_API_KEY trong file .env")

            # Khởi tạo LLM qua Gemini (Google)
            self.llm = ChatGoogleGenerativeAI(
                temperature=0.1,
                google_api_key=gemini_api_key,
                model="gemini-2.5-flash" 
            )
        
        # Cấu hình Langfuse Callback (nếu có key)
        self.callbacks = []
        if HAS_LANGFUSE and settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            langfuse_handler = CallbackHandler(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST
            )
            self.callbacks.append(langfuse_handler)
            print("Đã bật tính năng giám sát bằng Langfuse!")
        
        # Định nghĩa Prompt Template (Kỹ thuật Prompt Engineering)
        self.prompt_template = PromptTemplate(
            input_variables=["context", "conversation_summary", "chat_history", "question"],
            template="""Bạn là một trợ lý AI thông minh chuyên trả lời câu hỏi dựa trên tài liệu nội bộ.
Hãy sử dụng các đoạn thông tin (ngữ cảnh) dưới đây để trả lời câu hỏi của người dùng.
NẾU KHÔNG CÓ THÔNG TIN TRONG TÀI LIỆU, hãy trung thực trả lời là "Tôi không tìm thấy thông tin này trong tài liệu", tuyệt đối không bịa ra thông tin.
QUY TẮC BẮT BUỘC: Khi đưa ra thông tin, bạn phải đính kèm nguồn trích dẫn và số trang ở cuối mỗi ý (ví dụ: [Nguồn: test.pdf - Trang 1]).

--- NGỮ CẢNH TÌM ĐƯỢC ---
{context}
---

--- TÓM TẮT HỘI THOẠI TRƯỚC ĐÓ ---
{conversation_summary}
---

--- LỊCH SỬ TRÒ CHUYỆN GẦN NHẤT ---
{chat_history}
---

Câu hỏi của người dùng: {question}
Câu trả lời của AI: """
        )

        # Prompt Template chuyên dụng cho Tóm tắt ĐƠN TÀI LIỆU kiểu NotebookLM
        self.summary_single_document_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""Bạn là một chuyên gia phân tích tài liệu và trợ lý nghiên cứu AI cấp cao (tương tự Google NotebookLM).
Người dùng đang yêu cầu TÓM TẮT TOÀN DIỆN tài liệu này dựa trên các phần nội dung được trích xuất.

--- CÁC PHẦN NỘI DUNG TRÍCH XUẤT TỪ TÀI LIỆU ---
{context}
---

Câu hỏi của người dùng: {question}

HÃY CUNG CẤP MỘT BẢN TÓM TẮT CHUYÊN SÂU, SẮC BÉN VÀ ĐẦY ĐỦ THEO CÁC MỤC:
1. **Bối cảnh & Động lực nghiên cứu (Context & Motivation)**: Tài liệu nghiên cứu/đề cập về lĩnh vực gì? Giải quyết khó khăn hay bài toán gì trong thực tế?
2. **Mục tiêu chính (Core Objective)**: Mục tiêu cụ thể mà tác giả/tài liệu hướng đến.
3. **Phương pháp & Mô hình đề xuất (Methodology & Architecture)**: Kỹ thuật, thuật toán, mô hình, hoặc dữ liệu chính được sử dụng.
4. **Kết quả thử nghiệm & Phát hiện nổi bật (Key Results & Findings)**: Các con số, phát hiện hoặc kết quả so sánh đạt được.
5. **Kết luận & Ý nghĩa thực tiễn (Conclusion & Impact)**: Ứng dụng thực tế và giá trị đem lại.

QUY TẮC BẮT BUỘC:
- TUYỆT ĐỐI KHÔNG lặp lại nội dung giữa các mục. Mỗi thông điệp chỉ nêu một lần duy nhất.
- TUYỆT ĐỐI KHÔNG chỉ liệt kê hình thức mục lục hay tiêu đề chương (KHÔNG trả lời theo kiểu 'Tài liệu gồm có mục lục, phụ lục A...').
- Đi sâu vào BẢN CHẤT KỸ THUẬT, tên công nghệ, số liệu và kiến thức thực tế được trình bày.
- Đính kèm nguồn trích dẫn và số trang cụ thể ở các luận điểm chính (ví dụ: [Nguồn: tên_file - Trang X]).

Câu trả lời của AI: """
        )

        # Prompt Template chuyên dụng cho Tổng hợp & Đối chiếu ĐA TÀI LIỆU (Tránh lặp tuyệt đối)
        self.summary_multi_document_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""Bạn là một chuyên gia phân tích tài liệu và cố vấn chiến lược AI cấp cao (tương tự Google NotebookLM).
Người dùng đang yêu cầu TỔNG HỢP VÀ TÓM TẮT ĐỐI CHIẾU NHIỀU TÀI LIỆU (đa tài liệu) cùng lúc dựa trên các phần nội dung trích xuất.

--- CÁC PHẦN NỘI DUNG TRÍCH XUẤT TỪ CÁC TÀI LIỆU ---
{context}
---

Câu hỏi của người dùng: {question}

BẮT BUỘC TRÌNH BÀY THEO CẤU TRÚC 3 PHẦN CHUYÊN NGHIỆP, RÕ RÀNG, TUYỆT ĐỐI KHÔNG TRÙNG LẶP:

### 1. BẢNG SO SÁNH ĐỐI CHIẾU TỔNG QUAN (Comparative Matrix)
Tạo 1 bảng Markdown so sánh các tài liệu theo các tiêu chí:
| Tiêu chí so sánh | [Tên File 1] | [Tên File 2] | ... |
Các dòng so sánh:
- **Định vị & Loại tài liệu** (ví dụ: Nghiên cứu lý thuyết / Quy trình kỹ thuật MLOps / Báo cáo nghiệp vụ...)
- **Mục tiêu / Bài toán cốt lõi**
- **Phương pháp / Công nghệ / Dữ liệu sử dụng**
- **Sản phẩm đầu ra & Ứng dụng thực tế**

### 2. TÓM TẮT TRỌNG TÂM TỪNG TÀI LIỆU (Detailed Breakdown)
(Trình bày riêng từng tài liệu một cách cô đọng, sâu sắc; TUYỆT ĐỐI KHÔNG lặp lại các ý đã nói ở bảng trên):
- **Tài liệu 1: [Tên File 1]**
  - *Bối cảnh & Vấn đề:* Thách thức thực tế tài liệu tập trung giải quyết.
  - *Giải pháp & Đóng góp kỹ thuật:* Kỹ thuật, kiến trúc, mô hình hoặc bộ dữ liệu được sử dụng.
  - *Phát hiện chính / Kết quả:* Các phát hiện quan trọng, chỉ số đánh giá (Kèm trích dẫn minh chứng: [Nguồn: tên_file - Trang X]).
- **Tài liệu 2: [Tên File 2]**
  - *Bối cảnh & Vấn đề:* ...
  - *Giải pháp & Đóng góp kỹ thuật:* ...
  - *Phát hiện chính / Kết quả:* (Kèm trích dẫn minh chứng: [Nguồn: tên_file - Trang X]).

### 3. TÍNH BỔ TRỢ & MỐI QUAN HỆ GIỮA CÁC TÀI LIỆU (Synthesis & Synergy)
- Phân tích rõ các tài liệu này liên kết và bổ trợ cho nhau như thế nào trong chuỗi giá trị / vòng đời dự án (ví dụ: tài liệu này đặt nền tảng bài toán nghiên cứu lý thuyết, tài liệu kia là cẩm nang quy trình triển khai công nghệ vào thực tế).
- Đưa ra kết luận tổng hợp và khuyến nghị triển khai.

QUY TẮC CẤM TRÙNG LẶP NGHIÊM NGẶT (CRITICAL ANTI-REPETITION RULES):
- TUYỆT ĐỐI KHÔNG tạo 2 bản tóm tắt lặp nhau (CẤM viết một bản tóm tắt chung rồi lại viết tiếp một bản chi tiết y hệt).
- Mỗi luận điểm chỉ được trình bày 1 lần duy nhất tại vị trí thích hợp nhất.
- KHÔNG dùng câu chữ mơ hồ như 'không có kết quả' nếu tài liệu có đề cập đến các chỉ số, bài toán hay mục tiêu thử nghiệm cụ thể.
- Đính kèm nguồn trích dẫn cụ thể [Nguồn: tên_file - Trang X] ở các ý quan trọng.

Câu trả lời của AI: """
        )

        # Giữ bí danh tương thích ngược
        self.summary_document_prompt_template = self.summary_single_document_prompt_template

        # Định nghĩa Prompt Template cho Tóm tắt hội thoại (Conversation Summarization)
        self.summary_prompt_template = PromptTemplate(
            input_variables=["existing_summary", "new_messages"],
            template="""Bạn là một trợ lý AI chuyên tóm tắt tiến trình hội thoại pháp lý.
Dưới đây là tóm tắt trước đó (nếu có) và các tin nhắn trao đổi mới giữa Người dùng và AI.
Hãy tạo một bản tóm tắt súc tích, ngắn gọn (dưới 150 từ) cập nhật lại toàn bộ nội dung thảo luận.
Bản tóm tắt PHẢI giữ lại:
- Các chủ đề luật, văn bản, số hiệu, điều khoản người dùng quan tâm.
- Các thắc mắc chính và kết luận đã đưa ra.

--- TÓM TẮT TRƯỚC ĐÓ ---
{existing_summary}
---
--- CÁC TIN NHẮN MỚI ---
{new_messages}
---
Bản tóm tắt cập nhật (dưới 150 từ):"""
        )
        
        # Định nghĩa Prompt Template cho việc Chuẩn hóa câu hỏi và Trích xuất Metadata (Self-Query)
        self.query_parser = PydanticOutputParser(pydantic_object=QueryFilter)
        self.rewrite_prompt_template = PromptTemplate(
            input_variables=["chat_history", "question"],
            partial_variables={"format_instructions": self.query_parser.get_format_instructions()},
            template="""Dựa vào lịch sử trò chuyện, hãy phân tích câu hỏi mới nhất của người dùng.
1. Viết lại câu hỏi thành một câu truy vấn tìm kiếm ĐỘC LẬP và RÕ NGHĨA.
2. Trích xuất các điều kiện lọc (metadata) nếu có nhắc đến trong câu hỏi (năm, loại văn bản).

--- LỊCH SỬ TRÒ CHUYỆN ---
{chat_history}
---

Câu hỏi gốc: {question}

{format_instructions}"""
        )

        # Định nghĩa Prompt cho Agent phát hiện tham chiếu chéo (Cross-Reference Check)
        self.cross_ref_parser = PydanticOutputParser(pydantic_object=CrossReference)
        self.cross_ref_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            partial_variables={"format_instructions": self.cross_ref_parser.get_format_instructions()},
            template="""Bạn là một AI chuyên kiểm tra tính toàn vẹn của dữ liệu Pháp lý.
Người dùng đang hỏi: {question}

Dưới đây là các tài liệu hệ thống vừa tìm được:
--- NGỮ CẢNH ---
{context}
---

Nhiệm vụ của bạn: Kiểm tra xem trong Ngữ cảnh trên có câu văn nào yêu cầu tham chiếu sang một Điều/Khoản/Phụ lục khác để trả lời câu hỏi, nhưng BẢN THÂN Ngữ cảnh đó lại CHƯA CHỨA nội dung của Điều/Khoản/Phụ lục được nhắc đến hay không?
(Ví dụ: Tài liệu ghi 'Phạt theo khoản 2 Điều 5' nhưng bạn đọc không thấy Khoản 2 Điều 5 đâu).
Nếu có thiếu sót, hãy tạo ra các câu truy vấn để hệ thống đi tìm nội dung bị thiếu đó.

{format_instructions}"""
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _invoke_llm(self, prompt, user_id=None, session_id=None, cached_content=None):
        """Gọi LLM với cơ chế tự động thử lại (Retry) khi gặp lỗi mạng/timeout, hỗ trợ cached_content"""
        config = {}
        if self.callbacks:
            config["callbacks"] = self.callbacks
            config["metadata"] = {}
            if user_id:
                config["metadata"]["user_id"] = str(user_id)
            if session_id:
                config["metadata"]["session_id"] = str(session_id)
                
        llm_instance = self.llm
        if cached_content and not settings.USE_LOCAL_LLM:
            try:
                llm_instance = ChatGoogleGenerativeAI(
                    temperature=0.1,
                    google_api_key=settings.GEMINI_API_KEY,
                    model="gemini-2.5-flash",
                    cached_content=cached_content
                )
            except Exception as e:
                print(f"⚠️ Không thể khởi tạo LLM với cached_content: {e}")
                llm_instance = self.llm

        return await llm_instance.ainvoke(prompt, config=config)

    async def generate_conversation_summary_async(
        self,
        existing_summary: str | None,
        messages_text: str,
        user_id: int | None = None,
        session_id: int | None = None,
    ) -> str:
        """Tự động tóm tắt chuỗi tin nhắn để thu gọn Context Window."""
        prompt = self.summary_prompt_template.format(
            existing_summary=existing_summary or "Chưa có tóm tắt trước đó.",
            new_messages=messages_text,
        )
        try:
            response = await self._invoke_llm(prompt, user_id=user_id, session_id=session_id)
            return response.content.strip()
        except Exception as e:
            print(f"⚠️ Lỗi sinh tóm tắt hội thoại: {e}")
            return existing_summary or ""

    def format_context(self, docs):
        """Ghép các đoạn văn bản tìm được thành một đoạn ngữ cảnh thống nhất có cấu trúc"""
        formatted_texts = []
        for doc in docs:
            source = doc.metadata.get('filename') or doc.metadata.get('source', 'Không rõ')
            clean_source = re.sub(r'^\d+_[a-f0-9]{16,}\.?', '', source)
            clean_source = re.sub(r'^\d+_', '', clean_source).strip()
            if not clean_source or clean_source.startswith('.'):
                clean_source = source
            page = doc.metadata.get('page', '?')
            section = doc.metadata.get('section_title')
            section_str = f" - Mục: {section}" if section and section not in ["Tổng quan", "Overview"] else ""
            formatted_texts.append(f"Tài liệu [Nguồn: {clean_source} - Trang {page}{section_str}]:\n{doc.page_content}")
        return "\n\n".join(formatted_texts)

    SUMMARY_TRIGGERS = [
        "tóm tắt", "tom tat", "tổng quan", "tong quan", "nội dung chính", "noi dung chinh",
        "nói về cái gì", "noi ve cai gi", "tổng hợp", "tong hop", "khái quát", "khai quat",
        "summarize", "summary", "overview", "what is this document about", "giới thiệu tài liệu"
    ]

    async def answer_question_async(
        self,
        question: str,
        user_id: int,
        document_ids: list[int],
        chat_history: str = "",
        conversation_id: int = None,
        conversation_summary: str = "",
        cached_content: str = None,
    ):
        """Hàm trả lời câu hỏi bất đồng bộ (Hỗ trợ Tóm tắt NotebookLM và Tra cứu sâu)"""
        
        is_summary = any(trig in question.lower() for trig in self.SUMMARY_TRIGGERS)
        
        if is_summary:
            print(f" [Intent: SUMMARY] Kích hoạt chế độ Tóm tắt Toàn diện kiểu NotebookLM cho: '{question}'")
            fetch_k = 18 if len(document_ids) > 1 else 14
            docs = await self.retriever.retrieve_for_summary_async(user_id=user_id, document_ids=document_ids, top_k=fetch_k)
            if not docs:
                return "Xin lỗi, tôi không tìm thấy tài liệu nào liên quan trong cuộc trò chuyện này."
            context_str = self.format_context(docs)
            
            unique_sources = set()
            for d in docs:
                src = d.metadata.get('filename') or d.metadata.get('source')
                if src:
                    unique_sources.add(src)
            is_multi_doc = len(document_ids) > 1 or len(unique_sources) > 1

            if is_multi_doc:
                print(f" [Summary: Multi-Doc Mode] Phát hiện {len(unique_sources)} tài liệu. Áp dụng Prompt Tổng hợp Đa Tài liệu.")
                final_prompt = self.summary_multi_document_prompt_template.format(context=context_str, question=question)
            else:
                print(" [Summary: Single-Doc Mode] Áp dụng Prompt Tóm tắt Đơn Tài liệu.")
                final_prompt = self.summary_single_document_prompt_template.format(context=context_str, question=question)
        else:
            # Tra cứu thông thường (Specific Q&A)
            search_query = question
            extracted_filters = {}
            
            # Chỉ rewrite nếu có lịch sử trò chuyện để tiết kiệm quota & độ trễ
            if chat_history.strip():
                print(" Đang chuẩn hóa câu hỏi theo ngữ cảnh hội thoại (Self-Query)...")
                rewrite_prompt = self.rewrite_prompt_template.format(
                    chat_history=chat_history,
                    question=question
                )
                try:
                    rewrite_response = await self._invoke_llm(rewrite_prompt, user_id=user_id, session_id=conversation_id)
                    parsed_query = self.query_parser.parse(rewrite_response.content)
                    search_query = parsed_query.search_query
                    if parsed_query.year:
                        extracted_filters["year"] = parsed_query.year
                    if parsed_query.doc_type:
                        extracted_filters["doc_type"] = parsed_query.doc_type
                except Exception as e:
                    print(f" Lỗi parse JSON Self-Query, dùng câu hỏi gốc: {e}")
                    
            docs = await self.retriever.search_async(search_query, user_id=user_id, document_ids=document_ids, top_k=6, filters=extracted_filters)
            if not docs:
                return "Xin lỗi, tôi không tìm thấy tài liệu nào liên quan trong cuộc trò chuyện này."
                
            context_str = self.format_context(docs)
            final_prompt = self.prompt_template.format(
                context=context_str,
                conversation_summary=conversation_summary or "Chưa có tóm tắt trước đó.",
                chat_history=chat_history,
                question=question
            )
            model_name = f"Ollama {settings.OLLAMA_MODEL}" if settings.USE_LOCAL_LLM else "Gemini Flash"
            print(f" LLM ({model_name}) đang đọc tài liệu và sinh câu trả lời...")
        response = await self._invoke_llm(
            final_prompt,
            user_id=user_id,
            session_id=conversation_id,
            cached_content=cached_content,
        )
        return response.content

    async def answer_question_stream(
        self,
        question: str,
        user_id: int,
        document_ids: list[int],
        chat_history: str = "",
        conversation_id: int = None,
        conversation_summary: str = "",
        cached_content: str = None,
    ):
        """Hàm trả lời câu hỏi bất đồng bộ dưới dạng Stream (Generator)"""
        
        is_summary = any(trig in question.lower() for trig in self.SUMMARY_TRIGGERS)
        
        if is_summary:
            print(f" [Intent: SUMMARY] Kích hoạt chế độ Tóm tắt Toàn diện kiểu NotebookLM cho: '{question}'")
            fetch_k = 18 if len(document_ids) > 1 else 14
            docs = await self.retriever.retrieve_for_summary_async(user_id=user_id, document_ids=document_ids, top_k=fetch_k)
            if not docs:
                yield "Xin lỗi, tôi không tìm thấy tài liệu nào liên quan trong cuộc trò chuyện này."
                return
            context_str = self.format_context(docs)
            
            unique_sources = set()
            for d in docs:
                src = d.metadata.get('filename') or d.metadata.get('source')
                if src:
                    unique_sources.add(src)
            is_multi_doc = len(document_ids) > 1 or len(unique_sources) > 1

            if is_multi_doc:
                print(f" [Summary: Multi-Doc Mode] Phát hiện {len(unique_sources)} tài liệu. Áp dụng Prompt Tổng hợp Đa Tài liệu.")
                final_prompt = self.summary_multi_document_prompt_template.format(context=context_str, question=question)
            else:
                print(" [Summary: Single-Doc Mode] Áp dụng Prompt Tóm tắt Đơn Tài liệu.")
                final_prompt = self.summary_single_document_prompt_template.format(context=context_str, question=question)
        else:
            search_query = question
            extracted_filters = {}
            
            if chat_history.strip():
                print(" Đang chuẩn hóa câu hỏi theo ngữ cảnh hội thoại (Self-Query)...")
                rewrite_prompt = self.rewrite_prompt_template.format(
                    chat_history=chat_history,
                    question=question
                )
                try:
                    rewrite_response = await self._invoke_llm(rewrite_prompt, user_id=user_id, session_id=conversation_id)
                    parsed_query = self.query_parser.parse(rewrite_response.content)
                    search_query = parsed_query.search_query
                    if parsed_query.year:
                        extracted_filters["year"] = parsed_query.year
                    if parsed_query.doc_type:
                        extracted_filters["doc_type"] = parsed_query.doc_type
                except Exception as e:
                    print(f" Lỗi parse JSON Self-Query, dùng câu hỏi gốc: {e}")
                    
            docs = await self.retriever.search_async(search_query, user_id=user_id, document_ids=document_ids, top_k=6, filters=extracted_filters)
            if not docs:
                yield "Xin lỗi, tôi không tìm thấy tài liệu nào liên quan trong cuộc trò chuyện này."
                return
                
            context_str = self.format_context(docs)
            final_prompt = self.prompt_template.format(
                context=context_str,
                conversation_summary=conversation_summary or "Chưa có tóm tắt trước đó.",
                chat_history=chat_history,
                question=question
            )
        
        print(" LLM (Gemini 2.5 Flash) đang đọc tài liệu và sinh luồng câu trả lời (Stream)...")
        
        config = {}
        if self.callbacks:
            config["callbacks"] = self.callbacks
            config["metadata"] = {}
            if user_id:
                config["metadata"]["user_id"] = str(user_id)
            if conversation_id:
                config["metadata"]["session_id"] = str(conversation_id)

        llm_instance = self.llm
        if cached_content:
            try:
                llm_instance = ChatGoogleGenerativeAI(
                    temperature=0.1,
                    google_api_key=settings.GEMINI_API_KEY,
                    model="gemini-2.5-flash",
                    cached_content=cached_content
                )
            except Exception as e:
                print(f" Không thể stream LLM với cached_content: {e}")
                llm_instance = self.llm

        try:
            async for chunk in llm_instance.astream(final_prompt, config=config):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            print(f"Lỗi khi Stream LLM: {e}. Đang thử fallback sang ainvoke...")
            try:
                fallback_response = await self._invoke_llm(
                    final_prompt,
                    user_id=user_id,
                    session_id=conversation_id,
                    cached_content=cached_content,
                )
                yield fallback_response.content
            except Exception as final_err:
                print(f"❌ Cả Stream và Fallback LLM đều thất bại: {final_err}")
                err_str = f"{e} {final_err}"
                if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
                    yield "\n\n⚠️ **Hệ thống đã trích xuất thành công tri thức tài liệu**, nhưng **GEMINI_API_KEY** trong AWS Secrets Manager đang là mã mẫu hoặc không hợp lệ.\n\n👉 Vui lòng cập nhật API Key chính xác từ Google AI Studio vào Secret `rag/production/credentials` trên AWS."
                else:
                    yield f"\n\n⚠️ Lỗi sinh câu trả lời từ AI: {str(final_err)[:200]}"
