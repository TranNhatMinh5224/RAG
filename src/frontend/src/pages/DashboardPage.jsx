import React, { useState, useContext } from 'react';
import { Row, Col, Dropdown, Modal, Form, Button } from 'react-bootstrap';
import { AuthContext } from '../contexts/AuthContext';
import { Bot, User, LogOut, ShieldCheck, Cpu, Key, Lock } from 'lucide-react';
import Sidebar from '../features/Sidebar';
import ChatWindow from '../features/ChatWindow';
import DocumentManagerModal from '../features/DocumentManagerModal';
import AuthService from '../services/auth_service';
import { toast } from 'react-toastify';
import GlassInput from '../components/GlassInput';

const DashboardPage = () => {
    const { user, logout } = useContext(AuthContext);
    const [activeChatId, setActiveChatId] = useState(null);
    const [showDocModal, setShowDocModal] = useState(false);
    
    // Change Password State
    const [showChangePassModal, setShowChangePassModal] = useState(false);
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [isChangingPass, setIsChangingPass] = useState(false);

    const handleChangePassword = async (e) => {
        e.preventDefault();
        setIsChangingPass(true);
        try {
            await AuthService.changePassword(oldPassword, newPassword, confirmNewPassword);
            toast.success("Đổi mật khẩu thành công!");
            setShowChangePassModal(false);
            setOldPassword('');
            setNewPassword('');
            setConfirmNewPassword('');
        } catch (error) {
            toast.error(error.message);
        } finally {
            setIsChangingPass(false);
        }
    };

    return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-app-base)', overflow: 'hidden' }}>
            {/* Top Workspace Header */}
            <div className="d-flex justify-content-between align-items-center px-4 py-2 border-bottom glass-panel" style={{ borderRadius: 0, zIndex: 100, background: 'var(--bg-sidebar)', borderBottom: '1px solid var(--border-glass)' }}>
                <div className="d-flex align-items-center gap-3">
                    <div className="p-2 rounded-3" style={{ background: 'var(--gradient-brand)', boxShadow: '0 0 15px var(--glow-cyan)' }}>
                        <Bot size={22} className="text-white" />
                    </div>
                    <div>
                        <h5 className="mb-0 fw-bold" style={{ background: 'var(--gradient-brand)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '1.15rem' }}>
                            Trần Nhật Minh RAG AI Analyst
                        </h5>
                        <div className="d-flex align-items-center gap-2 text-muted" style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                            <span className="d-flex align-items-center gap-1 text-emerald-400">
                                <ShieldCheck size={12} /> Enterprise Secured
                            </span>
                            <span>•</span>
                            <span className="d-flex align-items-center gap-1 text-cyan-400">
                                <Cpu size={12} /> Gemini 2.5 Flash + Hybrid Search
                            </span>
                        </div>
                    </div>
                </div>

                {/* User Account Controls */}
                <Dropdown align="end">
                    <Dropdown.Toggle variant="link" className="d-flex align-items-center gap-2 border-0 text-light bg-transparent text-decoration-none px-3 py-1 rounded-3 glass-panel-hover" style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-glass)' }}>
                        <div className="rounded-circle p-1 bg-secondary bg-opacity-20 d-flex align-items-center justify-content-center" style={{ width: '28px', height: '28px' }}>
                            <User size={16} className="text-cyan-400" />
                        </div>
                        <span style={{ fontSize: '0.88rem', fontWeight: 500 }}>{user?.email || 'Tài khoản'}</span>
                    </Dropdown.Toggle>

                    <Dropdown.Menu variant="dark" className="glass-panel mt-2 p-2 border-secondary" style={{ backdropFilter: 'blur(20px)', minWidth: '200px' }}>
                        <div className="px-3 py-2 border-bottom border-secondary mb-2">
                            <div className="text-secondary" style={{ fontSize: '0.75rem' }}>Đăng nhập với email</div>
                            <div className="fw-bold text-truncate text-light" style={{ fontSize: '0.85rem' }}>{user?.email}</div>
                        </div>
                        <Dropdown.Item onClick={() => setShowChangePassModal(true)} className="text-light d-flex align-items-center gap-2 rounded-2 mb-1">
                            <Key size={16} /> Đổi mật khẩu
                        </Dropdown.Item>
                        <Dropdown.Item onClick={logout} className="text-danger d-flex align-items-center gap-2 rounded-2">
                            <LogOut size={16} /> Đăng xuất
                        </Dropdown.Item>
                    </Dropdown.Menu>
                </Dropdown>
            </div>

            {/* Layout chính 3 cột */}
            <div className="flex-grow-1 overflow-hidden">
                <Row className="h-100 g-0">
                    <Col md={4} lg={3} className="h-100">
                        <Sidebar 
                            currentChatId={activeChatId} 
                            onSelectChat={setActiveChatId} 
                        />
                    </Col>
                    <Col md={8} lg={9} className="h-100">
                        <ChatWindow 
                            conversationId={activeChatId} 
                            onOpenDocs={() => setShowDocModal(true)} 
                        />
                    </Col>
                </Row>
            </div>

            {/* Modal Quản lý Kho Tài liệu */}
            <DocumentManagerModal 
                show={showDocModal} 
                onHide={() => setShowDocModal(false)} 
                conversationId={activeChatId}
            />

            {/* Modal Đổi mật khẩu */}
            <Modal show={showChangePassModal} onHide={() => setShowChangePassModal(false)} centered contentClassName="glass-panel" backdrop="static">
                <Modal.Header closeButton closeVariant="white" className="border-secondary">
                    <Modal.Title className="text-light fw-bold d-flex align-items-center gap-2">
                        <Key size={24} className="text-cyan-400" />
                        Đổi mật khẩu
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body className="p-4">
                    <Form onSubmit={handleChangePassword}>
                        <GlassInput
                            icon={Lock}
                            type="password"
                            placeholder="Mật khẩu hiện tại..."
                            value={oldPassword}
                            onChange={(e) => setOldPassword(e.target.value)}
                            required
                        />
                        <div className="mt-3">
                            <GlassInput
                                icon={Key}
                                type="password"
                                placeholder="Mật khẩu mới..."
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                required
                            />
                        </div>
                        <div className="mt-3">
                            <GlassInput
                                icon={Key}
                                type="password"
                                placeholder="Xác nhận mật khẩu mới..."
                                value={confirmNewPassword}
                                onChange={(e) => setConfirmNewPassword(e.target.value)}
                                required
                            />
                        </div>
                        <div className="d-flex justify-content-end gap-2 mt-4">
                            <Button variant="secondary" onClick={() => setShowChangePassModal(false)} disabled={isChangingPass} className="rounded-3 border-0" style={{ background: 'rgba(255, 255, 255, 0.1)' }}>
                                Hủy bỏ
                            </Button>
                            <Button type="submit" className="btn-brand rounded-3 px-4" disabled={isChangingPass}>
                                {isChangingPass ? 'Đang cập nhật...' : 'Xác nhận đổi'}
                            </Button>
                        </div>
                    </Form>
                </Modal.Body>
            </Modal>
        </div>
    );
};

export default DashboardPage;
