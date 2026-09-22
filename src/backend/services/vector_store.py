import os
import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, SparseVectorParams
from qdrant_client.http import models
from core.config import settings

class VectorStoreManager:
    _shared_embeddings = None
    _shared_sparse_embeddings = None

    def __init__(self, collection_name="document_qna"):
        self.collection_name = collection_name
        self.qdrant_url = settings.QDRANT_URL
        
        # Tái sử dụng Singleton Embedding để không load lại weights nhiều lần
        if VectorStoreManager._shared_embeddings is None:
            print("[INFO] Loading paraphrase-multilingual-MiniLM-L12-v2 into RAM (Batch Size: 32)...")
            VectorStoreManager._shared_embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                encode_kwargs={"batch_size": 32, "normalize_embeddings": True}
            )
        self.embeddings = VectorStoreManager._shared_embeddings
        
        if VectorStoreManager._shared_sparse_embeddings is None:
            print("[INFO] Loading Sparse BM25 model...")
            VectorStoreManager._shared_sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.sparse_embeddings = VectorStoreManager._shared_sparse_embeddings
        
        print(f"[INFO] Connecting to Qdrant at {self.qdrant_url}...")
        self.client = QdrantClient(url=self.qdrant_url)
        self._init_collection()

    def _init_collection(self):
        """Kiểm tra và tạo Collection trong Qdrant nếu chưa có (kèm kiểm tra vector size 384)"""
        collections = self.client.get_collections().collections
        exists = any(col.name == self.collection_name for col in collections)
        
        if exists:
            try:
                info = self.client.get_collection(self.collection_name)
                vectors_cfg = info.config.params.vectors
                current_size = getattr(vectors_cfg, 'size', None)
                if current_size and current_size != 384:
                    print(f"[WARN] Collection '{self.collection_name}' co vector size={current_size} != 384. Dang tao lai collection...")
                    self.client.delete_collection(self.collection_name)
                    exists = False
            except Exception as e:
                print(f"[WARN] Khong the kiem tra vector size collection: {e}")

        if not exists:
            print(f"[INFO] Khoi tao Collection moi: {self.collection_name} (Vector size: 384, Hybrid Search)")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                sparse_vectors_config={
                    "text-sparse": models.SparseVectorParams()
                }
            )
        else:
            print(f"[INFO] Collection '{self.collection_name}' da ton tai voi vector size=384.")
        
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
        import time
        print(f"\n--- BAT DAU QUA TRINH INGESTION (BAT DONG BO) ---")
        
        from services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        # Bọc vào to_thread để tránh I/O làm treo server
        start_chunk = time.time()
        chunks = await asyncio.to_thread(processor.process_file, file_path, original_filename)
        chunk_time = time.time() - start_chunk
        
        texts = []
        metadatas = []
        for chunk in chunks:
            texts.append(chunk["content"])
            meta = chunk["metadata"]
            meta["user_id"] = user_id
            meta["document_id"] = document_id
            metadatas.append(meta)
        
        print(f"[INFO] Dang nhung (Embed) {len(texts)} chunks thanh Vector 384-dim va luu vao Qdrant...")
        start_embed = time.time()
        await self.vector_store.aadd_texts(texts=texts, metadatas=metadatas)
        embed_time = time.time() - start_embed
        print(f"[INFO] Hoan tat! Chunking: {chunk_time:.2f}s | Embedding: {embed_time:.2f}s | Tong chunks: {len(texts)}")

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
