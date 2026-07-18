import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

class RAGChain:
    def __init__(self, retriever):
        """Khởi tạo RAG Chain, nhận Retriever từ bên ngoài (Dependency Injection)"""
        self.retriever = retriever
        
        # Lấy API Key từ biến môi trường
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
            raise ValueError("Vui lòng cấu hình GEMINI_API_KEY trong file .env")

        # Khởi tạo LLM qua Gemini (Google)
        self.llm = ChatGoogleGenerativeAI(
            temperature=0.1,
            google_api_key=gemini_api_key,
            model="gemini-2.5-flash" 
        )
        
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

    def format_context(self, docs):
        """Ghép các đoạn văn bản tìm được thành một đoạn ngữ cảnh thống nhất"""
        formatted_texts = []
        for doc in docs:
            source = doc.metadata.get('source', 'Không rõ')
            page = doc.metadata.get('page', '?')
            formatted_texts.append(f"Tài liệu [Nguồn: {source} - Trang {page}]:\n{doc.page_content}")
        return "\n\n".join(formatted_texts)

    async def answer_question_async(self, question: str, user_id: int, document_ids: list[int], chat_history: str = ""):
        """Hàm trả lời câu hỏi bất đồng bộ (Có Memory và Filter)"""
        # BƯỚC 1: Lấy top 3 đoạn văn bản liên quan nhất từ Qdrant
        # Đã cập nhật để truyền user_id và document_ids xuống Retriever
        docs = await self.retriever.search_async(question, user_id=user_id, document_ids=document_ids, top_k=3)
        if not docs:
            return "Xin lỗi, tôi không tìm thấy tài liệu nào liên quan trong cuộc trò chuyện này."
            
        # BƯỚC 2: Định dạng thành Ngữ cảnh (Context)
        context_str = self.format_context(docs)
        
        # BƯỚC 3: Ghép vào Prompt
        final_prompt = self.prompt_template.format(
            context=context_str, 
            chat_history=chat_history,
            question=question
        )
        
        print(" LLM (Gemini 2.5 Pro) đang đọc tài liệu và suy nghĩ câu trả lời (Async)...")
        # BƯỚC 4: Gửi cho AI (Gemini) để sinh câu trả lời
        response = await self.llm.ainvoke(final_prompt)
        
        return response.content
