import React, { useState, useContext } from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { Bot, Mail, Lock, ShieldCheck, Sparkles } from 'lucide-react';
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
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            if (isLogin) {
                const data = await AuthService.authenticate(email, password);
                login(data.access_token, { email });
                toast.success("Đăng nhập thành công!");
                navigate('/');
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
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', background: 'var(--bg-app-base)', position: 'relative' }}>
            {/* Dynamic Background Glows */}
            <div style={{ position: 'absolute', top: '20%', left: '30%', width: '300px', height: '300px', background: 'var(--glow-cyan)', filter: 'blur(120px)', borderRadius: '50%', pointerEvents: 'none' }} />
            <div style={{ position: 'absolute', bottom: '20%', right: '30%', width: '250px', height: '250px', background: 'var(--glow-emerald)', filter: 'blur(100px)', borderRadius: '50%', pointerEvents: 'none' }} />

            <Container style={{ zIndex: 10 }}>
                <Row className="justify-content-center">
                    <Col md={6} lg={5} xl={4}>
                        <div className="glass-panel p-5 text-center rounded-4 shadow-lg" style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-glass-bright)' }}>
                            <div className="mb-4">
                                <div className="d-inline-flex p-3 rounded-4 mb-3" style={{ background: 'var(--gradient-brand)', boxShadow: '0 0 25px var(--glow-cyan)' }}>
                                    <Bot size={40} className="text-white" />
                                </div>
                                <h3 className="fw-bold" style={{ background: 'var(--gradient-brand)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                                    Trần Nhật Minh RAG AI
                                </h3>
                                <p className="text-secondary mt-1" style={{ fontSize: '0.9rem' }}>
                                    {isLogin ? 'Đăng nhập vào Hệ Thống Enterprise' : 'Khởi tạo Tài Khoản Mới'}
                                </p>
                            </div>

                            <Form onSubmit={handleSubmit}>
                                <GlassInput
                                    icon={Mail}
                                    type="email"
                                    placeholder="Địa chỉ Email..."
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />

                                <GlassInput
                                    icon={Lock}
                                    type="password"
                                    placeholder="Mật khẩu..."
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />

                                {!isLogin && (
                                    <GlassInput
                                        icon={Lock}
                                        type="password"
                                        placeholder="Xác nhận mật khẩu..."
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        required
                                    />
                                )}

                                <Button
                                    type="submit"
                                    className="btn-brand w-100 py-2 mt-3 mb-3 rounded-3"
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Đang xử lý...' : (isLogin ? 'Đăng Nhập Ngay' : 'Đăng Ký Tài Khoản')}
                                </Button>
                            </Form>

                            <p className="text-secondary mt-4 mb-0" style={{ fontSize: '0.88rem' }}>
                                {isLogin ? "Chưa có tài khoản? " : "Đã có tài khoản? "}
                                <a href="#" style={{ color: 'var(--accent-cyan)', fontWeight: 600 }} onClick={(e) => { e.preventDefault(); setIsLogin(!isLogin); }}>
                                    {isLogin ? "Đăng ký ngay" : "Đăng nhập"}
                                </a>
                            </p>
                        </div>
                    </Col>
                </Row>
            </Container>
        </div>
    );
};

export default LoginPage;
