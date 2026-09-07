'use client';

import React, { useState, useContext } from 'react';
import { useRouter } from 'next/navigation';
import { Bot, Mail, Lock, Sparkles, ArrowRight, ShieldCheck } from 'lucide-react';
import AuthService from '../services/auth_service';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import GlassInput from '../components/GlassInput';

const LoginPage = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { login } = useContext(AuthContext);
    const router = useRouter();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            if (isLogin) {
                const data = await AuthService.authenticate(email, password);
                login(data.access_token, { email });
                toast.success("Đăng nhập thành công!");
                router.push('/');
            } else {
                await AuthService.registerUser(email, password, confirmPassword);
                toast.success("Đăng ký thành công! Vui lòng đăng nhập.");
                setIsLogin(true);
                setPassword('');
                setConfirmPassword('');
            }
        } catch (error) {
            toast.error(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div 
            className="ambient-bg"
            style={{ 
                minHeight: '100vh', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                padding: '24px',
                position: 'relative',
                overflow: 'hidden'
            }}
        >
            {/* Ambient Background Aura Lights */}
            <div 
                style={{ 
                    position: 'absolute', 
                    top: '15%', 
                    left: '25%', 
                    width: '380px', 
                    height: '380px', 
                    background: 'radial-gradient(circle, var(--glow-cyan) 0%, transparent 70%)', 
                    filter: 'blur(100px)', 
                    pointerEvents: 'none',
                    opacity: 0.6,
                }} 
            />
            <div 
                style={{ 
                    position: 'absolute', 
                    bottom: '15%', 
                    right: '25%', 
                    width: '350px', 
                    height: '350px', 
                    background: 'radial-gradient(circle, var(--glow-blue) 0%, transparent 70%)', 
                    filter: 'blur(100px)', 
                    pointerEvents: 'none',
                    opacity: 0.5,
                }} 
            />

            {/* Login Glass Card */}
            <div 
                className="glass-card"
                style={{
                    width: '100%',
                    maxWidth: '440px',
                    padding: '40px 36px',
                    position: 'relative',
                    zIndex: 10,
                    boxShadow: '0 25px 60px rgba(0, 0, 0, 0.7), 0 0 35px rgba(6, 182, 212, 0.12)',
                    border: '1px solid var(--border-glass-bright)',
                }}
            >
                {/* Brand Logo & Header */}
                <div className="text-center mb-4">
                    <div 
                        style={{ 
                            width: '56px', 
                            height: '56px', 
                            borderRadius: '16px', 
                            background: 'var(--gradient-brand)', 
                            boxShadow: '0 0 25px var(--glow-cyan)',
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            marginBottom: '16px',
                        }}
                    >
                        <Bot size={30} color="#fff" />
                    </div>

                    <h3 style={{ fontWeight: 800, letterSpacing: '-0.03em', marginBottom: '6px' }}>
                        NexusDoc AI Enterprise
                    </h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', margin: 0 }}>
                        {isLogin ? 'Nền tảng nghiên cứu & phân tích tài liệu chuyên sâu' : 'Khởi tạo tài khoản nghiên cứu mới'}
                    </p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label style={{ fontSize: '0.8rem', fontWeight: 500, color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>
                            Email doanh nghiệp
                        </label>
                        <GlassInput
                            icon={Mail}
                            type="email"
                            placeholder="name@company.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="mb-3">
                        <label style={{ fontSize: '0.8rem', fontWeight: 500, color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>
                            Mật khẩu
                        </label>
                        <GlassInput
                            icon={Lock}
                            type="password"
                            placeholder="••••••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {!isLogin && (
                        <div className="mb-3">
                            <label style={{ fontSize: '0.8rem', fontWeight: 500, color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>
                                Xác nhận mật khẩu
                            </label>
                            <GlassInput
                                icon={Lock}
                                type="password"
                                placeholder="••••••••••••"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn-brand w-100 py-3 mt-4"
                        disabled={isLoading}
                        style={{ borderRadius: '12px', fontSize: '0.92rem' }}
                    >
                        {isLoading ? (
                            'Đang xử lý...'
                        ) : (
                            <span className="d-flex align-items-center justify-content-center gap-2">
                                <span>{isLogin ? 'Đăng nhập vào Hệ thống' : 'Tạo tài khoản ngay'}</span>
                                <ArrowRight size={16} />
                            </span>
                        )}
                    </button>
                </form>

                {/* Footer Switcher */}
                <div className="text-center mt-4 pt-3" style={{ borderTop: '1px solid var(--border-glass)', fontSize: '0.85rem' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>
                        {isLogin ? 'Chưa có tài khoản? ' : 'Đã có tài khoản? '}
                    </span>
                    <a
                        href="#"
                        style={{ color: 'var(--accent-cyan)', fontWeight: 600, textDecoration: 'none' }}
                        onClick={(e) => { e.preventDefault(); setIsLogin(!isLogin); }}
                    >
                        {isLogin ? 'Đăng ký ngay' : 'Đăng nhập'}
                    </a>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
