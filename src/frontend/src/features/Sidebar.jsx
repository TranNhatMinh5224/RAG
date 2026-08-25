import React, { useEffect, useState } from 'react';
import { Button, ListGroup, Modal, Form, Spinner } from 'react-bootstrap';
import { MessageSquarePlus, MessageSquare, Trash2, Search, Sparkles, FolderKanban } from 'lucide-react';
import ChatService from '../services/chat_service';
import { toast } from 'react-toastify';

const Sidebar = ({ currentChatId, onSelectChat }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState('');
  const [creating, setCreating] = useState(false);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await ChatService.getHistory();
      setConversations(data || []);
      if (!currentChatId && data && data.length > 0) {
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
    if (!newChatTitle.trim() || creating) return;
    try {
      setCreating(true);
      const newChat = await ChatService.createNewChat(newChatTitle);
      toast.success("Đã khởi tạo cuộc trò chuyện mới");
      setShowNewChatModal(false);
      setNewChatTitle('');
      await loadConversations();
      onSelectChat(newChat.id);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Bạn có chắc muốn xóa cuộc trò chuyện này cùng toàn bộ lịch sử tin nhắn?")) return;
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

  // Filter conversations by search term
  const filteredConversations = conversations.filter(chat =>
    (chat.title || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <div className="glass-panel h-100 d-flex flex-column" style={{ borderRadius: 0, borderRight: '1px solid var(--border-glass)', background: 'var(--bg-sidebar)' }}>
        {/* Top Header & New Chat Button */}
        <div className="p-3 border-bottom border-secondary">
          <Button
            className="btn-brand w-100 py-2 d-flex align-items-center justify-content-center gap-2 rounded-3 shadow-lg"
            onClick={() => setShowNewChatModal(true)}
          >
            <MessageSquarePlus size={18} />
            <span>Tạo Cuộc Trò Chuyện Mới</span>
          </Button>

          {/* Quick Search Bar */}
          <div className="position-relative mt-3">
            <Search size={15} className="position-absolute text-muted" style={{ left: '12px', top: '10px' }} />
            <input
              type="text"
              className="glass-input ps-5 py-1 text-light"
              placeholder="Tìm kiếm cuộc chat..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ fontSize: '0.85rem', borderRadius: '8px' }}
            />
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-grow-1 overflow-auto p-2">
          {loading ? (
            <div className="text-center text-secondary py-4">
              <Spinner animation="border" size="sm" variant="info" className="me-2" />
              Tải lịch sử...
            </div>
          ) : filteredConversations.length === 0 ? (
            <div className="text-center text-secondary py-4" style={{ fontSize: '0.88rem' }}>
              {searchQuery ? 'Không tìm thấy kết quả.' : 'Chưa có lịch sử trò chuyện nào.'}
            </div>
          ) : (
            <ListGroup variant="flush">
              {filteredConversations.map(chat => {
                const isActive = currentChatId === chat.id;

                return (
                  <ListGroup.Item
                    key={chat.id}
                    action
                    onClick={() => onSelectChat(chat.id)}
                    className="d-flex justify-content-between align-items-center rounded-3 mb-1 border-0 p-2 glass-panel-hover"
                    style={{
                      background: isActive ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                      borderLeft: isActive ? '3px solid var(--accent-cyan)' : '3px solid transparent',
                      color: isActive ? '#ffffff' : 'var(--text-secondary)',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <div className="d-flex align-items-center gap-2 text-truncate" style={{ maxWidth: '82%' }}>
                      <MessageSquare size={16} className={isActive ? 'text-cyan-400' : 'text-secondary'} />
                      <span className="text-truncate" style={{ fontSize: '0.88rem', fontWeight: isActive ? '600' : '400' }}>
                        {chat.title}
                      </span>
                    </div>

                    <Trash2
                      size={15}
                      className="text-danger opacity-50 opacity-100-hover"
                      style={{ cursor: 'pointer', transition: 'opacity 0.2s ease' }}
                      onClick={(e) => handleDelete(e, chat.id)}
                      title="Xóa đoạn chat"
                    />
                  </ListGroup.Item>
                );
              })}
            </ListGroup>
          )}
        </div>

        {/* Sidebar Footer info */}
        <div className="p-3 border-top border-secondary text-muted text-center" style={{ fontSize: '0.78rem' }}>
          <div className="d-flex align-items-center justify-content-center gap-1">
            <Sparkles size={13} className="text-cyan-400" />
            <span>RAG Engine v1.0 • Enterprise</span>
          </div>
        </div>
      </div>

      {/* Modal Tạo Cuộc Trò Chuyện Mới */}
      <Modal show={showNewChatModal} onHide={() => setShowNewChatModal(false)} centered contentClassName="glass-panel text-light" style={{ backdropFilter: 'blur(20px)' }}>
        <Modal.Header closeButton closeVariant="white" className="border-secondary">
          <Modal.Title className="d-flex align-items-center gap-2" style={{ fontSize: '1.1rem' }}>
            <MessageSquarePlus className="text-cyan-400" size={20} />
            Tạo cuộc trò chuyện mới
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group>
            <Form.Label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Nhập tiêu đề hoặc mục tiêu phân tích:
            </Form.Label>
            <Form.Control
              type="text"
              className="glass-input mt-1"
              placeholder="Ví dụ: Phân tích báo cáo tài chính Q3 2026..."
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
          <Button variant="outline-secondary" size="sm" onClick={() => setShowNewChatModal(false)}>
            Hủy
          </Button>
          <Button className="btn-brand" size="sm" onClick={handleNewChat} disabled={!newChatTitle.trim() || creating}>
            {creating ? <Spinner size="sm" /> : 'Khởi tạo'}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default Sidebar;
