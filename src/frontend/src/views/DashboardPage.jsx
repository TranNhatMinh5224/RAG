'use client';

import React, { useState, useContext } from 'react';
import { Dropdown, Modal, Form } from 'react-bootstrap';
import { AuthContext } from '../contexts/AuthContext';
import { 
  Bot, User, LogOut, ShieldCheck, Cpu, Key, Lock, 
  FolderGit2, Database, ChevronDown 
} from 'lucide-react';
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
    const [chatRefreshKey, setChatRefreshKey] = useState(0);
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    
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
        <div 
            className="ambient-bg"
            style={{ 
                height: '100vh', 
                display: 'flex', 
                flexDirection: 'column', 
                overflow: 'hidden' 
            }}
        >
            {/* Top Workspace Header */}
            <div 
                style={{
                    height: '56px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0 20px',
                    background: 'rgba(10, 13, 22, 0.9)',
                    borderBottom: '1px solid var(--border-glass)',
                    backdropFilter: 'blur(20px)',
                    zIndex: 100,
                }}
            >
                {/* Brand Logo & Subtitle */}
                <div className="d-flex align-items-center gap-3">
                    <div 
                        style={{ 
                            width: '32px', 
                            height: '32px', 
                            borderRadius: '10px', 
                            background: 'var(--gradient-brand)', 
                            boxShadow: '0 0 16px var(--glow-cyan)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <Bot size={20} color="#fff" />
                    </div>

                    <div>
                        <div className="d-flex align-items-center gap-2">
                            <span style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.02em', color: '#ffffff' }}>
                                NexusDoc <span style={{ color: 'var(--accent-cyan)' }}>AI</span>
                            </span>
                            <span 
                                style={{
                                    fontSize: '0.65rem',
                                    background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(99, 102, 241, 0.2))',
                                    color: '#38bdf8',
                                    border: '1px solid rgba(56, 189, 248, 0.35)',
                                    padding: '2px 7px',
                                    borderRadius: '6px',
                                    fontWeight: 700,
                                    letterSpacing: '0.04em',
                                    boxShadow: '0 0 10px rgba(6, 182, 212, 0.25)'
                                }}
                            >
                                DEEP RESEARCH PRO
                            </span>
                        </div>
                    </div>
                </div>

                {/* Right Action Controls */}
                <div className="d-flex align-items-center gap-3">
                    <button
                        className="btn-ghost-glass"
                        onClick={() => setShowDocModal(true)}
                        style={{ padding: '6px 14px', borderRadius: '10px' }}
                    >
                        <Database size={15} color="var(--accent-cyan)" />
                        <span>Kho Lưu Trữ Tri Thức</span>
                    </button>

                    {/* User Account Controls */}
                    <Dropdown align="end">
                        <Dropdown.Toggle 
                            as="button"
                            className="btn-ghost-glass"
                            style={{ 
                                padding: '5px 12px', 
                                borderRadius: '10px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                            }}
                        >
                            <div 
                                style={{ 
                                    width: '24px', 
                                    height: '24px', 
                                    borderRadius: '50%', 
                                    background: 'rgba(6, 182, 212, 0.2)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}
                            >
                                <User size={13} color="var(--accent-cyan)" />
                            </div>
                            <span style={{ fontSize: '0.84rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                                {user?.email?.split('@')[0] || 'Tài khoản'}
                            </span>
                            <ChevronDown size={14} color="var(--text-muted)" />
                        </Dropdown.Toggle>

                        <Dropdown.Menu 
                            className="glass-dropdown-menu mt-2 p-2" 
                            style={{ minWidth: '240px' }}
                        >
                            <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-glass)', marginBottom: '8px' }}>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    Tài khoản đang đăng nhập
                                </div>
                                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', marginTop: '2px' }}>
                                    {user?.email}
                                </div>
                            </div>

                            <button 
                                type="button"
                                onClick={() => setShowChangePassModal(true)} 
                                className="glass-dropdown-item mb-1"
                            >
                                <Key size={15} color="var(--accent-cyan)" />
                                <span>Đổi mật khẩu</span>
                            </button>

                            <div style={{ height: '1px', background: 'var(--border-glass)', margin: '4px 0' }} />

                            <button 
                                type="button"
                                onClick={logout} 
                                className="glass-dropdown-item danger"
                            >
                                <LogOut size={15} />
                                <span>Đăng xuất</span>
                            </button>
                        </Dropdown.Menu>
                    </Dropdown>
                </div>
            </div>

            {/* Main Application Workspace */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                <Sidebar 
                    currentChatId={activeChatId} 
                    onSelectChat={setActiveChatId} 
                    isCollapsed={isSidebarCollapsed}
                    onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                />

                <div style={{ flex: 1, height: '100%', overflow: 'hidden' }}>
                    <ChatWindow 
                        conversationId={activeChatId} 
                        refreshKey={chatRefreshKey}
                        onOpenDocs={() => setShowDocModal(true)} 
                    />
                </div>
            </div>

            {/* Modal Quản lý Kho Tài liệu */}
            <DocumentManagerModal 
                show={showDocModal} 
                onHide={() => {
                    setShowDocModal(false);
                    setChatRefreshKey(k => k + 1);
                }} 
                conversationId={activeChatId}
                onDocumentsUpdated={() => setChatRefreshKey(k => k + 1)}
            />

            {/* Modal Đổi mật khẩu */}
            <Modal 
                show={showChangePassModal} 
                onHide={() => setShowChangePassModal(false)} 
                centered 
                backdrop="static"
            >
                <Modal.Header closeButton closeVariant="white">
                    <Modal.Title className="d-flex align-items-center gap-2" style={{ fontSize: '1.05rem', fontWeight: 600 }}>
                        <Key size={20} color="var(--accent-cyan)" />
                        <span>Đổi mật khẩu tài khoản</span>
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body style={{ padding: '24px' }}>
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
                            <button 
                                type="button"
                                className="btn-ghost-glass" 
                                onClick={() => setShowChangePassModal(false)} 
                                disabled={isChangingPass}
                            >
                                Hủy bỏ
                            </button>
                            <button 
                                type="submit" 
                                className="btn-brand" 
                                disabled={isChangingPass}
                            >
                                {isChangingPass ? 'Đang cập nhật...' : 'Xác nhận đổi'}
                            </button>
                        </div>
                    </Form>
                </Modal.Body>
            </Modal>
        </div>
    );
};

export default DashboardPage;
