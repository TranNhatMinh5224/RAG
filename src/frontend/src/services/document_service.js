import DocumentRepository from '../repositories/document_repo';

class DocumentService {
    static async uploadFile(file) {
        // Business logic: Kiểm tra định dạng và dung lượng
        const allowedTypes = [
            'application/pdf', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
            'application/vnd.openxmlformats-officedocument.presentationml.presentation' // .pptx
        ];
        
        if (!allowedTypes.includes(file.type)) {
            throw new Error("Chỉ hỗ trợ file PDF, Word, Excel và PowerPoint.");
        }

        if (file.size > 20 * 1024 * 1024) { // 20MB
            throw new Error("Dung lượng file không được vượt quá 20MB.");
        }

        try {
            return await DocumentRepository.uploadDocument(file);
        } catch (error) {
            throw new Error("Lỗi khi tải file lên máy chủ.");
        }
    }

    static async fetchMyDocuments() {
        try {
            return await DocumentRepository.listDocuments();
        } catch (error) {
            throw new Error("Không thể lấy danh sách tài liệu.");
        }
    }

    static async removeDocument(docId) {
        try {
            return await DocumentRepository.deleteDocument(docId);
        } catch (error) {
            throw new Error("Không thể xóa tài liệu này.");
        }
    }
}

export default DocumentService;
