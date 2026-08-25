import AuthRepository from '../repositories/auth_repo';

/**
 * AuthService
 * Chịu trách nhiệm chứa Business Logic. 
 * Xử lý dữ liệu trước khi gửi đi và sau khi nhận về từ Repository.
 */
class AuthService {
    static async registerUser(email, password, confirmPassword) {
        // Business Logic: Kiểm tra mật khẩu khớp
        if (password !== confirmPassword) {
            throw new Error("Mật khẩu xác nhận không khớp!");
        }
        if (password.length > 70) {
            throw new Error("Mật khẩu quá dài, vui lòng giới hạn dưới 70 ký tự!");
        }
        if (password.length < 6) {
            throw new Error("Mật khẩu phải chứa ít nhất 6 ký tự!");
        }
        
        try {
            return await AuthRepository.register(email, password);
        } catch (error) {
            // Xử lý lỗi trả về từ API để có câu thông báo thân thiện hơn
            if (error.response && error.response.status === 400) {
                throw new Error(error.response.data.detail || "Tài khoản đã tồn tại.");
            }
            throw new Error("Có lỗi xảy ra khi kết nối tới máy chủ.");
        }
    }

    static async authenticate(email, password) {
        if (!email || !password) {
            throw new Error("Vui lòng nhập đầy đủ email và mật khẩu.");
        }
        
        try {
            const data = await AuthRepository.login(email, password);
            return data; // Trả về { access_token, token_type }
        } catch (error) {
            throw new Error("Sai tài khoản hoặc mật khẩu.");
        }
    }

    static async changePassword(oldPassword, newPassword, confirmNewPassword) {
        if (!oldPassword || !newPassword || !confirmNewPassword) {
            throw new Error("Vui lòng nhập đầy đủ các trường.");
        }
        if (newPassword !== confirmNewPassword) {
            throw new Error("Mật khẩu mới không khớp!");
        }
        if (newPassword.length < 6) {
            throw new Error("Mật khẩu mới phải chứa ít nhất 6 ký tự!");
        }
        try {
            return await AuthRepository.changePassword(oldPassword, newPassword);
        } catch (error) {
            if (error.response && error.response.status === 400) {
                throw new Error("Mật khẩu cũ không chính xác.");
            }
            throw new Error("Lỗi kết nối máy chủ, vui lòng thử lại.");
        }
    }
}

export default AuthService;
