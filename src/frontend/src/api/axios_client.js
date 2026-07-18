import axios from 'axios';

// Khởi tạo instance của Axios với URL gốc của Backend
const axiosClient = axios.create({
    baseURL: 'http://localhost:8000', // Đổi thành URL production khi deploy
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor: Tự động đính kèm Token vào mọi Request gửi đi
axiosClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor: Xử lý lỗi trả về (Ví dụ: 401 Unauthorized -> Đăng xuất)
axiosClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            // Hết hạn token hoặc không hợp lệ -> Xóa token và bắt đăng nhập lại
            localStorage.removeItem('access_token');
            // Dùng events hoặc window.location để redirect về trang login
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default axiosClient;
