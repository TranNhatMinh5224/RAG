import re
from typing import List
from langchain_core.documents import Document

class LegalDocumentParser:
    """
    Parser chuyên dụng cho văn bản Pháp luật Việt Nam.
    Tự động nhận diện cấu trúc Chương, Điều, Khoản để giữ nguyên ngữ cảnh (Context)
    khi chia nhỏ văn bản (Chunking).
    """
    def __init__(self, doc_metadata: dict):
        """
        Khởi tạo parser với metadata của tài liệu.
        :param doc_metadata: dict chứa ít nhất key 'title' (Tên văn bản luật)
        """
        self.doc_title = doc_metadata.get("title", "Tài liệu Pháp lý")
        self.base_metadata = doc_metadata
        self.current_chuong = ""
        self.current_dieu = ""

    def parse(self, text: str) -> List[Document]:
        """
        Đọc text raw và trả về danh sách các Langchain Documents đã được chunking theo cấu trúc.
        """
        documents = []
        lines = text.split('\n')
        
        current_chunk_lines = []
        
        # Biểu thức chính quy (Regex) nhận diện cấu trúc
        chuong_pattern = re.compile(r'^Chương\s+[IVXLCDM]+', re.IGNORECASE)
        dieu_pattern = re.compile(r'^Điều\s+\d+[\.:]?', re.IGNORECASE)
        khoan_pattern = re.compile(r'^\d+\.\s+') # Ví dụ: "1. ", "2. "
        
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
                
            # 1. Phát hiện "Chương"
            if chuong_pattern.match(clean_line):
                self.current_chuong = clean_line
                continue
                
            # 2. Phát hiện "Điều"
            if dieu_pattern.match(clean_line):
                # Lưu chunk trước đó (nếu có)
                if current_chunk_lines:
                    documents.append(self._create_document(current_chunk_lines))
                    current_chunk_lines = []
                
                self.current_dieu = clean_line
                current_chunk_lines.append(clean_line)
                continue
                
            # 3. Phát hiện "Khoản" (Tùy chọn: Tách riêng từng Khoản thành chunk nếu Điều quá dài)
            # Ở phiên bản cơ bản này, ta gom các Khoản vào chung 1 Điều. 
            # Nếu gặp một Khoản mới mà Điều hiện tại đã khá dài (>300 từ), ta có thể ngắt chunk tại đây.
            word_count = sum(len(l.split()) for l in current_chunk_lines)
            if khoan_pattern.match(clean_line) and word_count > 200:
                # Ngắt chunk ở Khoản này để tránh quá tải Token, nhưng vẫn giữ Context của Điều
                documents.append(self._create_document(current_chunk_lines))
                current_chunk_lines = []
                # Không gán lại self.current_dieu vì Khoản này vẫn thuộc Điều cũ
            
            current_chunk_lines.append(clean_line)
            
        # Lưu chunk cuối cùng
        if current_chunk_lines:
            documents.append(self._create_document(current_chunk_lines))
            
        return documents

    def _create_document(self, lines: List[str]) -> Document:
        """
        Tạo Langchain Document, tự động dán "Ngữ cảnh cha" lên đầu chunk.
        """
        content = "\n".join(lines)
        
        # Xây dựng Header ngữ cảnh (Context Header)
        header_parts = [f"[{self.doc_title}]"]
        if self.current_chuong:
            header_parts.append(f"[{self.current_chuong}]")
        
        # Nếu nội dung chunk không bắt đầu bằng chữ "Điều" (tức là nó bị cắt ngang ở Khoản),
        # ta phải bổ sung tên Điều vào Header.
        if self.current_dieu and not content.startswith(self.current_dieu):
            header_parts.append(f"[{self.current_dieu}]")
            
        context_header = " > ".join(header_parts)
        
        # Ghép Context Header với nội dung thực tế
        final_content = f"{context_header}\nNội dung:\n{content}"
        
        # Cập nhật metadata
        chunk_metadata = self.base_metadata.copy()
        chunk_metadata.update({
            "chuong": self.current_chuong,
            "dieu": self.current_dieu
        })
        
        return Document(page_content=final_content, metadata=chunk_metadata)

# --- Test logic nhanh ---
if __name__ == "__main__":
    sample_text = \"\"\"
Chương I. NHỮNG QUY ĐỊNH CHUNG
Điều 1. Phạm vi điều chỉnh
Luật này quy định về việc thành lập, tổ chức quản lý, tổ chức lại, giải thể và hoạt động có liên quan của doanh nghiệp.
Điều 2. Đối tượng áp dụng
1. Các doanh nghiệp.
2. Cơ quan, tổ chức, cá nhân có liên quan đến việc thành lập, tổ chức quản lý, tổ chức lại, giải thể và hoạt động có liên quan của doanh nghiệp.
3. Các trường hợp khác.
    \"\"\"
    
    parser = LegalDocumentParser({"title": "Luật Doanh nghiệp 2020", "source": "luat_dn.pdf"})
    docs = parser.parse(sample_text)
    
    for i, doc in enumerate(docs):
        print(f"--- Chunk {i+1} ---")
        print(doc.page_content)
        print("Metadata:", doc.metadata)
        print()
