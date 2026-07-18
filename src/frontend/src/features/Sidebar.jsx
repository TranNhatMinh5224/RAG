import React, { useEffect, useState } from 'react';
import { Button, ListGroup, Modal, Form } from 'react-bootstrap';
import { MessageSquarePlus, MessageCircle, Trash2 } from 'lucide-react';
import ChatService from '../services/chat_service';
import { toast } from 'react-toastify';

const Sidebar = ({ currentChatId, onSelectChat }) => {
    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showNewChatModal, setShowNewChatModal] = useState(false);
    const [newChatTitle, setNewChatTitle] = useState('');

    const loadConversations = async () => {
        try {
            setLoading(true);
            const data = await ChatService.getHistory();
            setConversations(data);
            // Auto select the first chat if none is selected
            if (!currentChatId && data.length > 0) {
                onSelectChat(data[0].id);
            }
        } catch (error) {
            toast.error(error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadConversations();
    }, []);

    const handleNewChat = async () => {
        if (!newChatTitle.trim()) return;
        try {
            const newChat = await ChatService.createNewChat(newChatTitle);
            toast.success("Đã tạo cuộc trò chuyện mới");
            setShowNewChatModal(false);
            setNewChatTitle('');
            await loadConversations();
            onSelectChat(newChat.id);
        } catch (error) {
            toast.error(error.message);
        }
    };

    const handleDelete = async (e, id) => {
        e.stopPropagation(); // Ngăn chặn trigger sự kiện click chọn chat
        if (!window.confirm("Bạn có chắc muốn xóa cuộc trò chuyện này?")) return;
        try {
            await ChatService.removeChat(id);
            toast.success("Đã xóa cuộc trò chuyện.");
            if (currentChatId === id) {
                onSelectChat(null);
            }
            loadConversations();
        } catch (error) {
            toast.error(error.message);
        }
    };

    return (
        <>
        <div className="glass-panel h-100 d-flex flex-column" style={{ borderRadius: '0', borderLeft: 'none', borderTop: 'none', borderBottom: 'none' }}>
            <div className="p-3 border-bottom" style={{ borderColor: 'var(--border-color)' }}>
                <Button variant="outline-info" className="w-100 d-flex align-items-center justify-content-center gap-2" onClick={() => setShowNewChatModal(true)}>
                    <MessageSquarePlus size={20} /> Mở Chat Mới
                </Button>
            </div>
            
            <div className="flex-grow-1 overflow-auto p-2">
                {loading ? (
                    <div className="text-center text-secondary mt-4">Đang tải...</div>
                ) : conversations.length === 0 ? (
                    <div className="text-center text-secondary mt-4">Chưa có lịch sử.</div>
                ) : (
                    <ListGroup variant="flush">
                        {conversations.map(chat => (
                            <ListGroup.Item 
                                key={chat.id} 
                                action 
                                onClick={() => onSelectChat(chat.id)}
                                className={`d-flex justify-content-between align-items-center rounded mb-1 border-0 ${currentChatId === chat.id ? 'bg-primary text-white' : 'bg-transparent text-light'}`}
                                style={{ transition: 'all 0.2s ease', cursor: 'pointer' }}
                            >
                                <div className="text-truncate" style={{ maxWidth: '80%' }}>
                                    <MessageCircle size={16} className="me-2" />
                                    {chat.title}
                                </div>
                                <Trash2 
                                    size={16} 
                                    className="text-danger" 
                                    style={{ opacity: 0.7, cursor: 'pointer' }} 
                                    onClick={(e) => handleDelete(e, chat.id)}
                                />
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                )}
            </div>
        </div>
            
            {/* Modal Tạo Cuộc Trò Chuyện Mới */}
            <Modal show={showNewChatModal} onHide={() => setShowNewChatModal(false)} centered contentClassName="glass-panel text-light">
                <Modal.Header closeButton closeVariant="white" className="border-secondary">
                    <Modal.Title>Tạo cuộc trò chuyện mới</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form.Group>
                        <Form.Label>Nhập tiêu đề cuộc trò chuyện:</Form.Label>
                        <Form.Control 
                            type="text" 
                            className="glass-input"
                            placeholder="Ví dụ: Phân tích báo cáo tài chính Q1..." 
                            value={newChatTitle}
                            onChange={(e) => setNewChatTitle(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    handleNewChat();
                                }
                            }}
                            autoFocus
                        />
                    </Form.Group>
                </Modal.Body>
                <Modal.Footer className="border-secondary">
                    <Button variant="outline-secondary" onClick={() => setShowNewChatModal(false)}>
                        Hủy
                    </Button>
                    <Button className="btn-gradient" onClick={handleNewChat} disabled={!newChatTitle.trim()}>
                        Tạo mới
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
};

export default Sidebar;
