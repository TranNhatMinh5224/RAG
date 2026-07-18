import React, { useState, useContext } from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { Bot, Mail, Lock } from 'lucide-react';
import AuthService from '../services/auth_service';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import GlassInput from '../components/GlassInput';
import GlassButton from '../components/GlassButton';

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
                // Xử lý Đăng nhập
                const data = await AuthService.authenticate(email, password);
                login(data.access_token, { email });
                toast.success("Đăng nhập thành công!");
                navigate('/');
            } else {
                // Xử lý Đăng ký
                await AuthService.registerUser(email, password, confirmPassword);
                toast.success("Đăng ký thành công! Vui lòng đăng nhập.");
                setIsLogin(true); // Chuyển về form đăng nhập
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
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', background: 'var(--bg-darker)' }}>
            <Container>
                <Row className="justify-content-center">
                    <Col md={6} lg={5} xl={4}>
                        <div className="glass-panel p-5 text-center">
                            <div className="mb-4">
                                <Bot size={48} color="var(--accent-primary)" />
                                <h2 className="mt-3 fw-bold">Trần Nhật Minh AI</h2>
                                <p className="text-secondary">{isLogin ? 'Đăng nhập để tiếp tục' : 'Tạo tài khoản mới'}</p>
                            </div>

                            <Form onSubmit={handleSubmit}>
                                <GlassInput
                                    icon={Mail}
                                    type="email"
                                    placeholder="Địa chỉ Email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />

                                <GlassInput
                                    icon={Lock}
                                    type="password"
                                    placeholder="Mật khẩu"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />

                                {!isLogin && (
                                    <GlassInput
                                        icon={Lock}
                                        type="password"
                                        placeholder="Xác nhận mật khẩu"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        required
                                    />
                                )}

                                <GlassButton
                                    type="submit"
                                    className="w-100 mb-3"
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Đang xử lý...' : (isLogin ? 'Đăng nhập' : 'Đăng ký')}
                                </GlassButton>
                            </Form>

                            <p className="text-secondary mt-4 mb-0">
                                {isLogin ? "Chưa có tài khoản? " : "Đã có tài khoản? "}
                                <a href="#" onClick={(e) => { e.preventDefault(); setIsLogin(!isLogin); }}>
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
