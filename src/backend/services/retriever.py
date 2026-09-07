import asyncio
import re
from qdrant_client.http import models
from sentence_transformers import CrossEncoder

def is_table_of_contents_chunk(text: str) -> bool:
    """Nhận diện các đoạn chỉ là mục lục hoặc chấm bi phân trang"""
    if not text:
        return True
    clean = text.strip()
    if len(clean) < 35:
        return True
    # Dấu chấm nối dòng (dot leaders) đặc trưng của mục lục (. . . . hoặc ........)
    if re.search(r'(?:\.\s*){4,}', clean):
        return True
    if re.search(r'\bcontents\b', clean, re.IGNORECASE) and re.search(r'\babstract\b', clean, re.IGNORECASE) and re.search(r'\d+\s+\d+', clean):
        return True
    lines = [line.strip() for line in clean.split('\n') if line.strip()]
    if lines:
        toc_lines = sum(1 for l in lines if re.search(r'[\.\-\s]{2,}\s*\d+$', l) or re.search(r'^(?:chapter|\d+\.|\bappendix\b).*\s+\d+$', l, re.IGNORECASE))
        if len(lines) >= 3 and (toc_lines / len(lines) >= 0.35 or toc_lines >= 4):
            return True
    return False

class Retriever:
    def __init__(self, vsm):
        """Khởi tạo Retriever, nhận VectorStoreManager từ bên ngoài truyền vào (Dependency Injection)"""
        self.vsm = vsm
        self.vector_store = self.vsm.vector_store
        
        print("Đang tải mô hình Re-ranker (BAAI/bge-reranker-v2-m3)...")
        self.reranker = CrossEncoder('BAAI/bge-reranker-v2-m3')

    async def search_async(self, query: str, user_id: int, document_ids: list[int], top_k: int = 6, filters: dict = None):
        """Hàm tìm kiếm bất đồng bộ (Có bộ lọc Multi-tenant, Self-Query Filter và loại bỏ Mục lục)"""

        fetch_k = 25
        print(f"BƯỚC 1: Đang tìm kiếm Hybrid {fetch_k} kết quả thô cho câu hỏi: '{query}' ...")
        
        # Thiết lập bộ lọc (Filter): Phải đúng user_id VÀ đúng document_id nằm trong danh sách
        must_conditions = [
            models.FieldCondition(
                key="metadata.user_id",
                match=models.MatchValue(value=user_id)
            ),
            models.FieldCondition(
                key="metadata.document_id",
                match=models.MatchAny(any=document_ids)
            )
        ]
        
        # Thêm các điều kiện lọc tự động từ Self-Query (Năm, Loại văn bản)
        if filters:
            if "year" in filters and filters["year"] is not None:
                must_conditions.append(
                    models.FieldCondition(
                        key="metadata.year",
                        match=models.MatchValue(value=filters["year"])
                    )
                )
            if "doc_type" in filters and filters["doc_type"] is not None:
                must_conditions.append(
                    models.FieldCondition(
                        key="metadata.doc_type",
                        match=models.MatchValue(value=filters["doc_type"])
                    )
                )

        search_filter = models.Filter(must=must_conditions)
        
        # Dùng asimilarity_search với filter lấy fetch_k kết quả
        raw_results = await self.vector_store.asimilarity_search(
            query, 
            k=fetch_k,
            filter=search_filter
        )
        
        # Fallback: Nếu bộ lọc nâng cao (năm, loại văn bản) không khớp đoạn nào,
        # tự động tìm lại với bộ lọc cơ bản (user_id + document_ids) để không bỏ sót thông tin
        if not raw_results and filters:
            print(" Không tìm thấy kết quả với bộ lọc nâng cao, tự động thử lại với bộ lọc cơ bản...")
            fallback_filter = models.Filter(must=[
                models.FieldCondition(
                    key="metadata.user_id",
                    match=models.MatchValue(value=user_id)
                ),
                models.FieldCondition(
                    key="metadata.document_id",
                    match=models.MatchAny(any=document_ids)
                )
            ])
            raw_results = await self.vector_store.asimilarity_search(
                query,
                k=fetch_k,
                filter=fallback_filter
            )

        if not raw_results:
            return []

        print(f"BƯỚC 2: Đang dùng Re-ranker chấm điểm lại {len(raw_results)} kết quả...")
        
        # Tạo danh sách các cặp (Câu hỏi, Đoạn văn) để cho Giám khảo chấm
        pairs = [[query, doc.page_content] for doc in raw_results]
        
        # Chấm điểm bằng CrossEncoder (đưa vào thread để không chặn luồng chính)
        scores = await asyncio.to_thread(self.reranker.predict, pairs)
        
        # Gắn điểm số vào metadata
        for doc, score in zip(raw_results, scores):
            doc.metadata["rerank_score"] = float(score)
            
        # Sắp xếp giảm dần theo điểm rerank
        ranked_results = sorted(raw_results, key=lambda x: x.metadata["rerank_score"], reverse=True)
        
        # Lọc bỏ các đoạn mục lục/chấm bi nếu có các đoạn nội dung thực tế
        substantive_docs = [d for d in ranked_results if not is_table_of_contents_chunk(d.page_content)]
        final_candidates = substantive_docs if substantive_docs else ranked_results

        # Lấy top_k kết quả xuất sắc nhất
        final_results = final_candidates[:top_k]
        
        print(f"Đã chọn được Top {len(final_results)} kết quả chuẩn xác nhất:\n")
        for i, doc in enumerate(final_results):
            source = doc.metadata.get('source', 'Không rõ')
            page = doc.metadata.get('page', '?')
            score = doc.metadata.get('rerank_score', 0.0)
            print(f" KẾT QUẢ {i+1} (Nguồn: {source} - Trang: {page} - Điểm: {score:.4f}) ---")
            print(f"{doc.page_content[:200]}...\n")
            
        return final_results

    async def retrieve_for_summary_async(self, user_id: int, document_ids: list[int], top_k: int = 14):
        """
        Truy xuất đa khía cạnh (Multi-Aspect Retrieval) cho yêu cầu Tóm tắt/Tổng quan tài liệu kiểu NotebookLM.
        Thu thập các phần: Bối cảnh/Mục tiêu, Kiến trúc/Phương pháp, Thực nghiệm/Kết luận và loại bỏ mục lục.
        """
        print(f" Đang kích hoạt Multi-Aspect Retrieval để Tóm tắt Toàn diện...")
        
        aspect_queries = [
            "bối cảnh nghiên cứu, động lực, khó khăn thực tế, bài toán cần giải quyết, abstract, introduction, problem, motivation",
            "mục tiêu nghiên cứu, đóng góp chính, phương pháp đề xuất, goal, objectives, contributions, proposed architecture",
            "mô hình, kiến trúc kỹ thuật, dữ liệu thực nghiệm, methodology, technical architecture, model, dataset, features",
            "kết quả thử nghiệm, phát hiện nổi bật, đánh giá so sánh, kết luận, experimental results, evaluation, findings, conclusion"
        ]
        
        all_docs = []
        seen_texts = set()
        
        # Tìm kiếm theo từng khía cạnh
        for aspect_q in aspect_queries:
            docs = await self.search_async(
                query=aspect_q,
                user_id=user_id,
                document_ids=document_ids,
                top_k=4,
                filters=None
            )
            for d in docs:
                content_key = d.page_content.strip()[:100]
                if content_key not in seen_texts and not is_table_of_contents_chunk(d.page_content):
                    seen_texts.add(content_key)
                    all_docs.append(d)
                    
        # Đảm bảo phân bổ đều các đoạn tri thức giữa các tài liệu khác nhau nếu là đa tài liệu
        docs_by_source = {}
        for d in all_docs:
            src = d.metadata.get('source', 'default')
            docs_by_source.setdefault(src, []).append(d)

        num_sources = len(docs_by_source)
        if num_sources > 1:
            per_doc_limit = max(4, (top_k + num_sources - 1) // num_sources)
            balanced_docs = []
            for src, doc_list in docs_by_source.items():
                doc_list.sort(key=lambda d: d.metadata.get('page', 0))
                balanced_docs.extend(doc_list[:per_doc_limit])
            final_summary_docs = balanced_docs[:top_k]
        else:
            all_docs.sort(key=lambda d: (d.metadata.get('source', ''), d.metadata.get('page', 0)))
            final_summary_docs = all_docs[:top_k]

        print(f" Đã chọn lọc {len(final_summary_docs)} phân đoạn tri thức từ {num_sources} tài liệu cho bản tóm tắt.")
        return final_summary_docs
