import os
import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, SparseVectorParams
from qdrant_client.http import models
from core.config import settings

class VectorStoreManager:
    def __init__(self, collection_name="document_qna"):
        self.collection_name = collection_name
        self.qdrant_url = settings.QDRANT_URL
        
        print("Đang tải mô hình Embedding BAAI/bge-m3...")
        # Mô hình BAAI/bge-m3 xuất sắc cho tiếng Việt, có dimension = 1024
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
        
        print("Đang tải mô hình Sparse Embedding (BM25)...")
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        
        print(f"Đang kết nối tới Qdrant tại {self.qdrant_url}...")
        self.client = QdrantClient(url=self.qdrant_url)
        self._init_collection()

    def _init_collection(self):
        """Kiểm tra và tạo Collection trong Qdrant nếu chưa có"""
        collections = self.client.get_collections().collections
        exists = any(col.name == self.collection_name for col in collections)
        
        if not exists:
            print(f"Khởi tạo Collection mới: {self.collection_name} (Hỗ trợ Hybrid Search)")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
                sparse_vectors_config={
                    "text-sparse": models.SparseVectorParams()
                }
            )
        else:
            print(f"Collection '{self.collection_name}' đã tồn tại, tiếp tục sử dụng.")
        
        # Tạo giao tiếp giữa Langchain và Qdrant
        self.vector_store = QdrantVectorStore(
            client=self.client, 
            collection_name=self.collection_name, 
            embedding=self.embeddings,
            sparse_embedding=self.sparse_embeddings,
            sparse_vector_name="text-sparse",
            retrieval_mode=RetrievalMode.HYBRID
        )

    async def ingest_document_async(self, file_path: str, user_id: int, document_id: int, original_filename: str = None):
        print(f"\n--- BẮT ĐẦU QUÁ TRÌNH INGESTION (BẤT ĐỒNG BỘ) ---")
        
        # Tiêm Embeddings vào DocumentProcessor để chạy Semantic Chunking
        from services.document_processor import DocumentProcessor
        processor = DocumentProcessor(self.embeddings)
        # Bọc vào to_thread để tránh OCR làm treo server
        chunks = await asyncio.to_thread(processor.process_file, file_path, original_filename)
        
        texts = []
        metadatas = []
        for chunk in chunks:
            texts.append(chunk["content"])
            # Gắn "thẻ căn cước" vào từng mảnh vector để phân tách dữ liệu
            meta = chunk["metadata"]
            meta["user_id"] = user_id
            meta["document_id"] = document_id
            metadatas.append(meta)
        
        print(f"Đang nhúng (Embed) {len(texts)} chunks thành Vector và lưu vào Qdrant...")
        # Dùng hàm aadd_texts (Async Add Texts) để không khóa server
        await self.vector_store.aadd_texts(texts=texts, metadatas=metadatas)
        print("Hoàn tất lưu trữ! Dữ liệu đã sẵn sàng để truy vấn.")

    async def delete_document(self, document_id: int):
        """Xóa toàn bộ Vector của một File PDF khỏi Qdrant (Dùng Bất đồng bộ)"""
        print(f"Đang xóa các Vector có document_id = {document_id} khỏi Qdrant...")
        
        def _delete():
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="metadata.document_id",
                                match=models.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
            
        await asyncio.to_thread(_delete)
        print(f" Đã xóa sạch dữ liệu Vector của document_id {document_id}")
