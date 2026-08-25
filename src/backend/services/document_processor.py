import fitz  # PyMuPDF
import docx
import pandas as pd
from pptx import Presentation
import re
import os
import numpy as np
from paddleocr import PaddleOCR
from langchain_experimental.text_splitter import SemanticChunker
from src.backend.services.legal_parser import LegalDocumentParser

class DocumentProcessor:
    def __init__(self, embeddings):
        """Khởi tạo với Semantic Chunker - Cắt văn bản dựa trên ý nghĩa ngữ nghĩa"""
        # Sử dụng model embeddings để tính độ tương đồng giữa các câu
        self.text_splitter = SemanticChunker(
            embeddings,
            breakpoint_threshold_type="percentile", # Cắt khi sự thay đổi ngữ nghĩa vượt mức phân vị
            breakpoint_threshold_amount=80 # Cắt ở top 20% những câu có sự khác biệt lớn nhất về ý nghĩa
        )
        print("Đang khởi tạo PaddleOCR...")
        self.ocr = PaddleOCR(use_angle_cls=True, lang='vi', show_log=False)

    def clean_text(self, text: str) -> str:
        # 1. Nối lại các từ bị gãy ở cuối dòng do dấu gạch nối (Ví dụ: "trách nhi- \n ệm")
        text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
        
        # 2. Xóa các ký tự Unicode rác (tránh làm nhiễu mô hình Embedding)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        
        # 3. Gom các khoảng trắng, dấu tab, dấu xuống dòng liên tiếp thành 1 dấu cách
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def process_pdf(self, file_path: str):
        """Hàm phụ: Đọc file PDF (Hỗ trợ Text-PDF và Scan-PDF bằng OCR)"""
        doc = fitz.open(file_path)
        pages_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text").strip()
            if text:
                pages_text.append({"text": text, "page": page_num + 1})
            else:
                # Nếu trang PDF không có text điện tử -> Kích hoạt OCR
                pix = page.get_pixmap()
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                if pix.n == 4:
                    import cv2
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                elif pix.n == 1:
                    import cv2
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                
                result = self.ocr.ocr(img, cls=True)
                page_text = ""
                if result and result[0]:
                    for line in result[0]:
                        page_text += line[1][0] + "\n"
                
                if page_text.strip():
                    pages_text.append({"text": page_text, "page": page_num + 1})
        doc.close()
        return pages_text

    def process_image(self, file_path: str):
        """Hàm phụ: Đọc trực tiếp file ảnh bằng PaddleOCR"""
        result = self.ocr.ocr(file_path, cls=True)
        page_text = ""
        if result and result[0]:
            for line in result[0]:
                page_text += line[1][0] + "\n"
        return [{"text": page_text, "page": 1}] if page_text.strip() else []

    def process_docx(self, file_path: str):
        """Hàm phụ: Đọc file Word (.docx)"""
        doc = docx.Document(file_path)
        # Word không có khái niệm trang (Page) rõ ràng như PDF, nên gộp tất cả thành Trang 1
        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return [{"text": full_text, "page": 1}] if full_text else []

    def process_xlsx(self, file_path: str):
        """Hàm phụ: Đọc file Excel (.xlsx) và chuyển thành bảng Markdown"""
        # Đọc tất cả các sheet trong file Excel
        excel_data = pd.read_excel(file_path, sheet_name=None)
        pages_text = []
        for sheet_name, df in excel_data.items():
            # Xóa các dòng/cột rỗng hoàn toàn để dữ liệu sạch hơn
            df = df.dropna(how='all').dropna(axis=1, how='all')
            if not df.empty:
                # Chuyển DataFrame thành định dạng Markdown (Rất tốt cho AI đọc)
                markdown_table = df.to_markdown(index=False)
                text = f"--- Dữ liệu từ Sheet: {sheet_name} ---\n{markdown_table}"
                pages_text.append({"text": text, "page": f"Sheet {sheet_name}"})
        return pages_text

    def process_pptx(self, file_path: str):
        """Hàm phụ: Đọc file PowerPoint (.pptx)"""
        prs = Presentation(file_path)
        pages_text = []
        for i, slide in enumerate(prs.slides):
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    slide_text.append(shape.text)
            
            full_text = "\n".join([t for t in slide_text if t.strip()])
            if full_text:
                pages_text.append({"text": full_text, "page": i + 1})
        return pages_text

    def process_file(self, file_path: str):
        """Đọc PDF/Docx/Xlsx/Pptx, dọn dẹp Text, cắt Semantic Chunk và gắn Metadata"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

        print(f"Đang đọc file: {file_path}")
        
        file_ext = file_path.lower()
        if file_ext.endswith(".pdf"):
            pages_data = self.process_pdf(file_path)
        elif file_ext.endswith((".png", ".jpg", ".jpeg")):
            pages_data = self.process_image(file_path)
        elif file_ext.endswith(".docx"):
            pages_data = self.process_docx(file_path)
        elif file_ext.endswith(".xlsx"):
            pages_data = self.process_xlsx(file_path)
        elif file_ext.endswith(".pptx"):
            pages_data = self.process_pptx(file_path)
        else:
            raise ValueError("Định dạng file không được hỗ trợ (Chỉ nhận .pdf, .docx, .xlsx, .pptx, .png, .jpg, .jpeg)")

        chunks_with_metadata = []

        # Kiểm tra nhanh xem đây có phải là văn bản pháp luật không (Chứa "Điều 1.", "Điều 2.")
        full_document_text = "\n".join([self.clean_text(d["text"]) for d in pages_data])
        is_legal_doc = bool(re.search(r'^Điều\s+\d+[\.:]?', full_document_text, re.MULTILINE | re.IGNORECASE))
        
        if is_legal_doc and file_ext in [".pdf", ".docx"]:
            print("Phát hiện văn bản Pháp luật -> Kích hoạt LegalDocumentParser")
            parser = LegalDocumentParser({"title": os.path.basename(file_path), "source": os.path.basename(file_path)})
            legal_docs = parser.parse(full_document_text)
            
            for doc in legal_docs:
                if len(doc.page_content.strip()) > 10:
                    chunks_with_metadata.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    })
            print(f" Legal Chunking hoàn tất: Tạo ra {len(chunks_with_metadata)} khối theo cấu trúc Điều/Khoản.")
        else:
            print("Văn bản thông thường -> Sử dụng SemanticChunker")
            for data in pages_data:
                cleaned_text = self.clean_text(data["text"])
                
                # SemanticChunker cắt dựa trên câu và gom nhóm ý nghĩa
                page_chunks = self.text_splitter.split_text(cleaned_text)
                
                for chunk in page_chunks:
                    if len(chunk.strip()) > 10: # Chỉ lấy các đoạn có nội dung thực tế
                        chunks_with_metadata.append({
                            "content": chunk,
                            "metadata": {
                                "source": os.path.basename(file_path),
                                "page": data["page"]
                            }
                        })
                    
            print(f" Semantic Chunking hoàn tất: Tạo ra {len(chunks_with_metadata)} khối ý nghĩa từ tài liệu.")
            
        return chunks_with_metadata
