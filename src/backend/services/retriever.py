from qdrant_client.http import models

class Retriever:
    def __init__(self, vsm):
        """Khởi tạo Retriever, nhận VectorStoreManager từ bên ngoài truyền vào (Dependency Injection)"""
        self.vsm = vsm
        self.vector_store = self.vsm.vector_store

    async def search_async(self, query: str, user_id: int, document_ids: list[int], top_k: int = 3):
        """Hàm tìm kiếm bất đồng bộ (Có bộ lọc Multi-tenant)"""

        print(f"Đang tìm kiếm thông tin cho câu hỏi: '{query}' ...")
        
        # Thiết lập bộ lọc (Filter): Phải đúng user_id VÀ đúng document_id nằm trong danh sách
        search_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.user_id",
                    match=models.MatchValue(value=user_id)
                ),
                models.FieldCondition(
                    key="metadata.document_id",
                    match=models.MatchAny(any=document_ids)
                )
            ]
        )
        
        # Dùng asimilarity_search với filter
        results = await self.vector_store.asimilarity_search(
            query, 
            k=top_k,
            filter=search_filter
        )
        
        print(f"Đã tìm thấy {len(results)} đoạn văn bản liên quan nhất:\n")
        for i, doc in enumerate(results):
            source = doc.metadata.get('source', 'Không rõ')
            page = doc.metadata.get('page', '?')
            print(f" KẾT QUẢ {i+1} (Nguồn: {source} - Trang: {page}) ---")
            print(f"{doc.page_content}\n")
            
        return results
