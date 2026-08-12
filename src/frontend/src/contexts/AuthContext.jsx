import React, { createContext, useState, useEffect } from 'react';
import axiosClient from '../api/axios_client';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Kiểm tra session khi ứng dụng vừa tải
    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    // Gọi API lấy thông tin profile để xác thực token
                    const response = await axiosClient.get('/auth/me');
                    setUser(response.data);
                } catch (error) {
                    console.error("Token không hợp lệ hoặc đã hết hạn", error);
                    localStorage.removeItem('access_token');
                    setUser(null);
                }
            }
            setLoading(false);
        };
        checkAuth();
    }, []);

    const login = (token, userData) => {
        localStorage.setItem('access_token', token);
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
