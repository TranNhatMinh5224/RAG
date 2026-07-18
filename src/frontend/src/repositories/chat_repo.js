import axiosClient from '../api/axios_client';

class ChatRepository {
    // ---- PHẦN CONVERSATION ----
    static async createConversation(title) {
        const response = await axiosClient.post('/conversation/', { title });
        return response.data;
    }

    static async listConversations() {
        const response = await axiosClient.get('/conversation/list');
        return response.data;
    }

    static async attachDocumentsToConversation(conversationId, documentIds) {
        const response = await axiosClient.post(`/conversation/${conversationId}/documents`, documentIds);
        return response.data;
    }

    static async getConversationDetails(conversationId) {
        const response = await axiosClient.get(`/conversation/${conversationId}`);
        return response.data;
    }

    static async deleteConversation(conversationId) {
        const response = await axiosClient.delete(`/conversation/${conversationId}`);
        return response.data;
    }

    // ---- PHẦN CHAT (RAG) ----
    static async sendMessage(conversationId, query) {
        const response = await axiosClient.post('/chat/', {
            conversation_id: conversationId,
            question: query
        });
        return response.data;
    }
}

export default ChatRepository;
