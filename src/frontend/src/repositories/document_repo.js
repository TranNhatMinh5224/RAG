import axiosClient from '../api/axios_client';

class DocumentRepository {
    static async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await axiosClient.post('/document/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }

    static async listDocuments() {
        const response = await axiosClient.get('/document/list');
        return response.data;
    }

    static async deleteDocument(docId) {
        const response = await axiosClient.delete(`/document/${docId}`);
        return response.data;
    }
}

export default DocumentRepository;
