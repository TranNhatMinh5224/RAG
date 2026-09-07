import axiosClient from '../api/axios_client';

class ChatRepository {
    // ---- PHẦN CONVERSATION ----
    static async createConversation(title, documentIds = []) {
        const response = await axiosClient.post('/conversation/', { 
            title, 
            document_ids: documentIds 
        });
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

    static async sendMessageStream(conversationId, query, onChunk, onError, onComplete, signal = null) {
        const baseURL = axiosClient.defaults.baseURL || 'http://localhost:8000';
        const token = localStorage.getItem('access_token');

        try {
            const response = await fetch(`${baseURL}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    question: query
                }),
                signal: signal
            });

            if (!response.ok) {
                const errJson = await response.json().catch(() => ({}));
                throw new Error(errJson.detail || `Lỗi kết nối máy chủ (${response.status})`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                if (chunk && onChunk) {
                    onChunk(chunk);
                }
            }

            if (onComplete) onComplete(false);
        } catch (err) {
            if (err.name === 'AbortError') {
                if (onComplete) onComplete(true);
                return;
            }
            if (onError) onError(err);
            else throw err;
        }
    }
}

export default ChatRepository;

