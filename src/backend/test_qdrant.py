import asyncio
from services.vector_store import VectorStoreManager

print("Đang khởi tạo VectorStoreManager...")
try:
    vsm = VectorStoreManager(collection_name="document_qna")
    print("Khởi tạo VectorStoreManager THÀNH CÔNG!")
    print(f"Collection: {vsm.collection_name}")
except Exception as e:
    print(f"Lỗi khi khởi tạo VectorStoreManager: {e}")
