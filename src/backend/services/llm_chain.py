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
            input_variables=["context", "chat_history", "question"],
            template="""Bạn là một trợ lý AI thông minh chuyên trả lời câu hỏi dựa trên tài liệu nội bộ.
Hãy sử dụng các đoạn thông tin (ngữ cảnh) dưới đây để trả lời câu hỏi của người dùng.
NẾU KHÔNG CÓ THÔNG TIN TRONG TÀI LIỆU, hãy trung thực trả lời là "Tôi không tìm thấy thông tin này trong tài liệu", tuyệt đối không bịa ra thông tin.
QUY TẮC BẮT BUỘC: Khi đưa ra thông tin, bạn phải đính kèm nguồn trích dẫn và số trang ở cuối mỗi ý (ví dụ: [Nguồn: test.pdf - Trang 1]).

--- NGỮ CẢNH TÌM ĐƯỢC ---
{context}
---

--- LỊCH SỬ TRÒ CHUYỆN ---
{chat_history}
---

Câu hỏi của người dùng: {question}
Câu trả lời của AI: """
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
    async def _invoke_llm(self, prompt, user_id=None, session_id=None):
        """Gọi LLM với cơ chế tự động thử lại (Retry) khi gặp lỗi mạng/timeout"""
        config = {}
        if self.callbacks:
            config["callbacks"] = self.callbacks
            config["metadata"] = {}
            if user_id:
                config["metadata"]["user_id"] = str(user_id)
            if session_id:
                config["metadata"]["session_id"] = str(session_id)
                
        return await self.llm.ainvoke(prompt, config=config)

    def format_context(self, docs):
        """Ghép các đoạn văn bản tìm được thành một đoạn ngữ cảnh thống nhất"""
        formatted_texts = []
        for doc in docs:
            source = doc.metadata.get('source', 'Không rõ')
            page = doc.metadata.get('page', '?')
            formatted_texts.append(f"Tài liệu [Nguồn: {source} - Trang {page}]:\n{doc.page_content}")
        return "\n\n".join(formatted_texts)

    async def answer_question_async(self, question: str, user_id: int, document_ids: list[int], chat_history: str = "", conversation_id: int = None):
        """Hàm trả lời câu hỏi bất đồng bộ (Có Memory và Filter)"""
        
        # BƯỚC 0: Query Rewriting & Self-Query Extract
        search_query = question
        extracted_filters = {}
        
        print(" Đang chuẩn hóa câu hỏi và trích xuất Metadata (Self-Query)...")
        rewrite_prompt = self.rewrite_prompt_template.format(
            chat_history=chat_history,
            question=question
        )
        try:
            # Luôn gọi LLM ở bước này kể cả không có chat_history để lấy được JSON Metadata
            rewrite_response = await self._invoke_llm(rewrite_prompt, user_id=user_id, session_id=conversation_id)
            parsed_query = self.query_parser.parse(rewrite_response.content)
            search_query = parsed_query.search_query
            
            if parsed_query.year:
                extracted_filters["year"] = parsed_query.year
            if parsed_query.doc_type:
                extracted_filters["doc_type"] = parsed_query.doc_type
                
            print(f" -> Câu hỏi sau chuẩn hóa: {search_query}")
            print(f" -> Bộ lọc tìm kiếm: {extracted_filters}")
        except Exception as e:
            print(f" Lỗi parse JSON Self-Query, dùng câu hỏi gốc: {e}")
            
        # BƯỚC 1: Lấy top 3 đoạn văn bản liên quan nhất từ Qdrant
        # Truyền thêm tham số filters xuống Retriever
        docs = await self.retriever.search_async(search_query, user_id=user_id, document_ids=document_ids, top_k=3, filters=extracted_filters)
        if not docs:
            return "Xin lỗi, tôi không tìm thấy tài liệu nào liên quan trong cuộc trò chuyện này."
            
        # BƯỚC 1.5: CROSS-REFERENCE CHECK (Kiểm tra và truy xuất đệ quy)
        context_str = self.format_context(docs)
        print(" Đang kiểm tra tham chiếu chéo (Cross-Reference Check)...")
        cross_ref_prompt = self.cross_ref_prompt_template.format(context=context_str, question=search_query)
        try:
            cross_ref_response = await self._invoke_llm(cross_ref_prompt, user_id=user_id, session_id=conversation_id)
            parsed_cross_ref = self.cross_ref_parser.parse(cross_ref_response.content)
            if parsed_cross_ref.needs_lookup and parsed_cross_ref.reference_queries:
                print(f" -> Cảnh báo! Thiếu thông tin tham chiếu chéo. Đang tự động tìm thêm: {parsed_cross_ref.reference_queries}")
                extra_docs = []
                for ref_q in parsed_cross_ref.reference_queries[:2]: # Tối đa tìm thêm 2 references để tránh quá tải
                    ref_docs = await self.retriever.search_async(ref_q, user_id=user_id, document_ids=document_ids, top_k=2, filters=extracted_filters)
                    extra_docs.extend(ref_docs)
                
                if extra_docs:
                    print(f" -> Đã bổ sung thành công {len(extra_docs)} đoạn tài liệu bị thiếu.")
                    docs.extend(extra_docs)
                    context_str = self.format_context(docs) # Cập nhật lại context sau khi cộng dồn
            else:
                print(" -> Không phát hiện tham chiếu chéo, ngữ cảnh đã đủ.")
        except Exception as e:
            print(f" Lỗi bước Cross-Reference Check, tiếp tục với tài liệu hiện có: {e}")
            
        # BƯỚC 2: Ghép vào Prompt cuối cùng
        final_prompt = self.prompt_template.format(
            context=context_str, 
            chat_history=chat_history,
            question=question
        )
        
        print(" LLM (Gemini 2.5 Flash) đang đọc tài liệu và suy nghĩ câu trả lời (Async)...")
        # BƯỚC 4: Gửi cho AI (Gemini) để sinh câu trả lời (có retry)
        response = await self._invoke_llm(final_prompt, user_id=user_id, session_id=conversation_id)
        
        return response.content

    async def answer_question_stream(self, question: str, user_id: int, document_ids: list[int], chat_history: str = "", conversation_id: int = None):
        """Hàm trả lời câu hỏi bất đồng bộ dưới dạng Stream (Generator)"""
        
        # BƯỚC 0: Query Rewriting & Self-Query Extract
        search_query = question
        extracted_filters = {}
        
        print(" Đang chuẩn hóa câu hỏi và trích xuất Metadata (Self-Query)...")
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
            
        # BƯỚC 1: Lấy top 3 đoạn văn bản liên quan nhất từ Qdrant
        docs = await self.retriever.search_async(search_query, user_id=user_id, document_ids=document_ids, top_k=3, filters=extracted_filters)
        if not docs:
            yield "Xin lỗi, tôi không tìm thấy tài liệu nào liên quan trong cuộc trò chuyện này."
            return
            
        # BƯỚC 1.5: CROSS-REFERENCE CHECK (Kiểm tra và truy xuất đệ quy)
        context_str = self.format_context(docs)
        print(" Đang kiểm tra tham chiếu chéo (Cross-Reference Check)...")
        cross_ref_prompt = self.cross_ref_prompt_template.format(context=context_str, question=search_query)
        try:
            cross_ref_response = await self._invoke_llm(cross_ref_prompt, user_id=user_id, session_id=conversation_id)
            parsed_cross_ref = self.cross_ref_parser.parse(cross_ref_response.content)
            if parsed_cross_ref.needs_lookup and parsed_cross_ref.reference_queries:
                print(f" -> Cảnh báo! Thiếu thông tin tham chiếu chéo. Đang tự động tìm thêm: {parsed_cross_ref.reference_queries}")
                extra_docs = []
                for ref_q in parsed_cross_ref.reference_queries[:2]:
                    ref_docs = await self.retriever.search_async(ref_q, user_id=user_id, document_ids=document_ids, top_k=2, filters=extracted_filters)
                    extra_docs.extend(ref_docs)
                
                if extra_docs:
                    print(f" -> Đã bổ sung thành công {len(extra_docs)} đoạn tài liệu bị thiếu.")
                    docs.extend(extra_docs)
                    context_str = self.format_context(docs) # Cập nhật lại context
            else:
                print(" -> Không phát hiện tham chiếu chéo, ngữ cảnh đã đủ.")
        except Exception as e:
            print(f" Lỗi bước Cross-Reference Check, tiếp tục với tài liệu hiện có: {e}")
            
        # BƯỚC 2: Ghép vào Prompt cuối cùng
        final_prompt = self.prompt_template.format(
            context=context_str, 
            chat_history=chat_history,
            question=question
        )
        
        print(" LLM (Gemini 2.5 Flash) đang đọc tài liệu và sinh luồng câu trả lời (Stream)...")
        # BƯỚC 4: Stream từ AI (Tenacity >= 8.3 hỗ trợ retry generator, nhưng để an toàn ta try-except thủ công cho luồng stream đầu tiên)
        
        config = {}
        if self.callbacks:
            config["callbacks"] = self.callbacks
            config["metadata"] = {}
            if user_id:
                config["metadata"]["user_id"] = str(user_id)
            if conversation_id:
                config["metadata"]["session_id"] = str(conversation_id)

        # Thử kết nối với cơ chế tự động thử lại
        try:
            # Nếu khởi tạo stream bị lỗi mạng ngay từ đầu, ta có thể bắt lỗi.
            # Lưu ý: trong lúc đang yield mà đứt mạng thì xử lý phức tạp hơn, nhưng đa số lỗi là lúc gọi hàm.
            async for chunk in self.llm.astream(final_prompt, config=config):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            print(f"Lỗi khi Stream LLM: {e}. Đang thử fallback sang ainvoke...")
            # Fallback sang invoke nếu stream lỗi
            fallback_response = await self._invoke_llm(final_prompt, user_id=user_id, session_id=conversation_id)
            yield fallback_response.content
