import DocumentRepository from '../repositories/document_repo';

class DocumentService {
    static async uploadFile(file) {
        // Business logic: Kiểm tra định dạng đuôi file và dung lượng
        const validExtensions = ['.pdf', '.docx', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg'];
        const fileName = file.name || '';
        const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
        
        if (!validExtensions.includes(ext)) {
            throw new Error("Chỉ hỗ trợ file PDF, Word, Excel, PowerPoint hoặc Ảnh (.png, .jpg).");
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

    static getFileTypeCategory(filename) {
        const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase();
        if (['.pdf', '.docx'].includes(ext)) return 'docs';
        if (['.xlsx'].includes(ext)) return 'sheets';
        if (['.png', '.jpg', '.jpeg'].includes(ext)) return 'images';
        if (['.pptx'].includes(ext)) return 'slides';
        return 'other';
    }
}

export default DocumentService;

