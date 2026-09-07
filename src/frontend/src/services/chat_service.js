import ChatRepository from '../repositories/chat_repo';

class ChatService {
    static async createNewChat(title = "Dự án mới", documentIds = []) {
        try {
            return await ChatRepository.createConversation(title, documentIds);
        } catch (error) {
            throw new Error("Lỗi khi tạo dự án mới.");
        }
    }

    static async getHistory() {
        try {
            return await ChatRepository.listConversations();
        } catch (error) {
            throw new Error("Không thể tải danh sách lịch sử.");
        }
    }

    static async setContextDocuments(conversationId, documentIds) {
        if (!conversationId || !Array.isArray(documentIds)) {
            throw new Error("Dữ liệu không hợp lệ.");
        }
        try {
            return await ChatRepository.attachDocumentsToConversation(conversationId, documentIds);
        } catch (error) {
            throw new Error("Lỗi khi đính kèm tài liệu vào cuộc hội thoại.");
        }
    }

    static async loadMessages(conversationId) {
        try {
            return await ChatRepository.getConversationDetails(conversationId);
        } catch (error) {
            throw new Error("Không thể tải nội dung cuộc hội thoại.");
        }
    }

    static async removeChat(conversationId) {
        try {
            return await ChatRepository.deleteConversation(conversationId);
        } catch (error) {
            throw new Error("Không thể xóa đoạn chat.");
        }
    }

    static async askAI(conversationId, question) {
        if (!question.trim()) {
            throw new Error("Vui lòng nhập câu hỏi.");
        }
        try {
            return await ChatRepository.sendMessage(conversationId, question);
        } catch (error) {
            throw new Error("Hệ thống AI đang quá tải hoặc có lỗi xảy ra.");
        }
    }

    static async askAIStream(conversationId, question, onChunk, onError, onComplete, signal = null) {
        if (!question.trim()) {
            throw new Error("Vui lòng nhập câu hỏi.");
        }
        return await ChatRepository.sendMessageStream(conversationId, question, onChunk, onError, onComplete, signal);
    }
}

export default ChatService;

