import React, { useState, useContext } from 'react';
import { Container, Row, Col, Dropdown } from 'react-bootstrap';
import { AuthContext } from '../contexts/AuthContext';
import { User } from 'lucide-react';
import Sidebar from '../features/Sidebar';
import ChatWindow from '../features/ChatWindow';
import DocumentManagerModal from '../features/DocumentManagerModal';

const DashboardPage = () => {
    const { user, logout } = useContext(AuthContext);
    const [activeChatId, setActiveChatId] = useState(null);
    const [showDocModal, setShowDocModal] = useState(false);

    return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-dark)' }}>
            {/* Header chung nhỏ gọn */}
            <div className="d-flex justify-content-between align-items-center p-2 px-4 border-bottom glass-panel" style={{ borderRadius: 0, zIndex: 100 }}>
                <h4 className="mb-0 fw-bold" style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    RAG SaaS
                </h4>
                <Dropdown>
                    <Dropdown.Toggle variant="outline-secondary" className="d-flex align-items-center gap-2 border-0 text-light bg-transparent">
                        <User size={20} /> {user?.email}
                    </Dropdown.Toggle>
                    <Dropdown.Menu variant="dark">
                        <Dropdown.Item onClick={logout}>Đăng xuất</Dropdown.Item>
                    </Dropdown.Menu>
                </Dropdown>
            </div>

            {/* Layout chính */}
            <div className="flex-grow-1 overflow-hidden">
                <Row className="h-100 g-0">
                    <Col md={3} lg={3} className="h-100">
                        <Sidebar 
                            currentChatId={activeChatId} 
                            onSelectChat={setActiveChatId} 
                        />
                    </Col>
                    <Col md={9} lg={9} className="h-100">
                        <ChatWindow 
                            conversationId={activeChatId} 
                            onOpenDocs={() => setShowDocModal(true)} 
                        />
                    </Col>
                </Row>
            </div>

            {/* Modal Quản lý Tài liệu */}
            <DocumentManagerModal 
                show={showDocModal} 
                onHide={() => setShowDocModal(false)} 
                conversationId={activeChatId}
            />
        </div>
    );
};

export default DashboardPage;
