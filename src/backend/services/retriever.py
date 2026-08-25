import asyncio
from qdrant_client.http import models
from sentence_transformers import CrossEncoder

class Retriever:
    def __init__(self, vsm):
        """Khởi tạo Retriever, nhận VectorStoreManager từ bên ngoài truyền vào (Dependency Injection)"""
        self.vsm = vsm
        self.vector_store = self.vsm.vector_store
        
        print("Đang tải mô hình Re-ranker (BAAI/bge-reranker-v2-m3)...")
        self.reranker = CrossEncoder('BAAI/bge-reranker-v2-m3')

    async def search_async(self, query: str, user_id: int, document_ids: list[int], top_k: int = 3, filters: dict = None):
        """Hàm tìm kiếm bất đồng bộ (Có bộ lọc Multi-tenant và Self-Query Filter)"""

        fetch_k = 15
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
        
        # Lấy top_k kết quả xuất sắc nhất
        final_results = ranked_results[:top_k]
        
        print(f"Đã chọn được Top {len(final_results)} kết quả chuẩn xác nhất:\n")
        for i, doc in enumerate(final_results):
            source = doc.metadata.get('source', 'Không rõ')
            page = doc.metadata.get('page', '?')
            score = doc.metadata.get('rerank_score', 0.0)
            print(f" KẾT QUẢ {i+1} (Nguồn: {source} - Trang: {page} - Điểm: {score:.4f}) ---")
            print(f"{doc.page_content}\n")
            
        return final_results
