import axios from 'axios';

// Tự động xác định baseURL:
// 1. Ưu tiên biến môi trường NEXT_PUBLIC_API_URL nếu được định nghĩa
// 2. Nếu chạy trên trình duyệt (Client), dùng '' (relative path) để tự động gọi qua Load Balancer / Domain hiện tại
// 3. Fallback cho Server-Side Rendering
const getBaseURL = () => {
    if (process.env.NEXT_PUBLIC_API_URL) {
        return process.env.NEXT_PUBLIC_API_URL;
    }
    if (typeof window !== 'undefined') {
        return '';
    }
    return 'http://localhost:8000';
};

// Khởi tạo instance của Axios với URL gốc của Backend
const axiosClient = axios.create({
    baseURL: getBaseURL(),
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor: Tự động đính kèm Token vào mọi Request gửi đi
axiosClient.interceptors.request.use(
    (config) => {
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('access_token');
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }
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
            if (typeof window !== 'undefined') {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default axiosClient;
