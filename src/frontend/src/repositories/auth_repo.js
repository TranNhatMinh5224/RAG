import axiosClient from '../api/axios_client';

/**
 * AuthRepository
 * Chỉ chịu trách nhiệm Giao tiếp với API (Thực hiện HTTP Request)
 * KHÔNG chứa Business Logic.
 */
class AuthRepository {
    static async register(email, password) {
        const response = await axiosClient.post('/auth/register', { email, password });
        return response.data;
    }

    static async login(email, password) {
        // OAuth2 Password Request Form đòi hỏi gửi dạng form-data URL encoded (Dùng email ánh xạ vào username của OAuth2)
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await axiosClient.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        return response.data;
    }

    static async getProfile() {
        const response = await axiosClient.get('/auth/me');
        return response.data;
    }
}

export default AuthRepository;
