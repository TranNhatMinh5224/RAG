from langchain_huggingface import HuggingFaceEmbeddings

print("Đang khởi tạo model BAAI/bge-m3...")
try:
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    print("Khởi tạo model THÀNH CÔNG!")
    vector = embeddings.embed_query("Thử nghiệm nhúng văn bản tiếng Việt.")
    print(f"Kích thước vector: {len(vector)}")
    print("Mọi thứ hoạt động HOÀN HẢO!")
except Exception as e:
    print(f"Lỗi khi khởi tạo model: {e}")
