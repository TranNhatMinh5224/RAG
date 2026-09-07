'use client';

import React, { useEffect, useState, useMemo, useRef } from 'react';
import { Modal, Form, Spinner } from 'react-bootstrap';
import { MessageSquarePlus, MessageSquare, Trash2, Search, Sparkles, ChevronLeft, ChevronRight, Clock, UploadCloud, FileText, X, Plus } from 'lucide-react';
import ChatService from '../services/chat_service';
import DocumentService from '../services/document_service';
import { toast } from 'react-toastify';

const Sidebar = ({ currentChatId, onSelectChat, isCollapsed, onToggleCollapse }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [creating, setCreating] = useState(false);
  const fileInputRef = useRef(null);

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

  const handleFilesChosen = (files) => {
    const fileList = Array.from(files || []);
    if (fileList.length === 0) return;
    setSelectedFiles(prev => [...prev, ...fileList]);
    if (!newChatTitle.trim()) {
      // Auto fill title from first file name
      const baseName = fileList[0].name.replace(/\.[^/.]+$/, "");
      setNewChatTitle(baseName);
    }
  };

  const removeSelectedFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleNewChat = async () => {
    const titleToUse = newChatTitle.trim() || (selectedFiles.length > 0 ? selectedFiles[0].name.replace(/\.[^/.]+$/, "") : "Dự án nghiên cứu mới");
    if (creating) return;

    try {
      setCreating(true);
      const uploadedDocIds = [];

      // If files were selected, upload them directly
      if (selectedFiles.length > 0) {
        for (const file of selectedFiles) {
          try {
            const doc = await DocumentService.uploadFile(file);
            if (doc && doc.id) {
              uploadedDocIds.push(doc.id);
            }
          } catch (uploadErr) {
            toast.warn(`Không thể tải file "${file.name}": ${uploadErr.message}`);
          }
        }
      }

      const newChat = await ChatService.createNewChat(titleToUse, uploadedDocIds);
      toast.success(uploadedDocIds.length > 0 
        ? `Đã tạo dự án mới với ${uploadedDocIds.length} tài liệu nguồn!` 
        : "Đã tạo phiên hội thoại mới!");
      
      setShowNewChatModal(false);
      setNewChatTitle('');
      setSelectedFiles([]);
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
      toast.success("Đã xóa cuộc trò chuyện");
      if (currentChatId === id) {
        onSelectChat(null);
      }
      loadConversations();
    } catch (error) {
      toast.error(error.message);
    }
  };

  // Group conversations by time
  const groupedConversations = useMemo(() => {
    const filtered = conversations.filter(chat =>
      (chat.title || '').toLowerCase().includes(searchQuery.toLowerCase())
    );

    const today = [];
    const thisWeek = [];
    const older = [];

    const now = new Date();
    const oneDay = 24 * 60 * 60 * 1000;
    const sevenDays = 7 * oneDay;

    filtered.forEach(chat => {
      const created = chat.created_at ? new Date(chat.created_at) : new Date();
      const diff = now - created;
      if (diff < oneDay) {
        today.push(chat);
      } else if (diff < sevenDays) {
        thisWeek.push(chat);
      } else {
        older.push(chat);
      }
    });

    return { today, thisWeek, older, total: filtered.length };
  }, [conversations, searchQuery]);

  if (isCollapsed) {
    return (
      <div 
        style={{
          width: '64px',
          height: '100%',
          background: 'var(--bg-sidebar)',
          borderRight: '1px solid var(--border-glass)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: '16px 0',
          transition: 'width 0.25s ease',
          zIndex: 10,
        }}
      >
        <button
          className="btn-ghost-glass p-2 mb-4"
          onClick={onToggleCollapse}
          title="Mở rộng Sidebar"
          style={{ borderRadius: '10px' }}
        >
          <ChevronRight size={18} />
        </button>

        <button
          className="btn-brand p-2"
          onClick={() => setShowNewChatModal(true)}
          title="Tạo cuộc trò chuyện mới"
          style={{ borderRadius: '12px', width: '40px', height: '40px' }}
        >
          <MessageSquarePlus size={18} />
        </button>
      </div>
    );
  }

  const renderSection = (title, items) => {
    if (items.length === 0) return null;
    return (
      <div className="mb-3" key={title}>
        <div 
          style={{ 
            fontSize: '0.72rem', 
            textTransform: 'uppercase', 
            letterSpacing: '0.08em', 
            color: 'var(--text-muted)',
            fontWeight: 600,
            padding: '4px 12px 6px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Clock size={11} />
          <span>{title}</span>
        </div>
        {items.map(chat => {
          const isActive = currentChatId === chat.id;
          return (
            <div
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className="group d-flex justify-content-between align-items-center mb-1"
              style={{
                padding: '9px 12px',
                borderRadius: '10px',
                background: isActive ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
                borderLeft: isActive ? '3px solid var(--accent-cyan)' : '3px solid transparent',
                color: isActive ? '#ffffff' : 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.18s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = 'transparent';
              }}
            >
              <div className="d-flex align-items-center gap-2 text-truncate" style={{ maxWidth: '85%' }}>
                <MessageSquare size={15} style={{ color: isActive ? 'var(--accent-cyan)' : 'var(--text-muted)', flexShrink: 0 }} />
                <span className="text-truncate" style={{ fontSize: '0.86rem', fontWeight: isActive ? 600 : 400 }}>
                  {chat.title?.replace(/^\d+_[a-f0-9]{20,}\.?/i, '').replace(/^\d+_/, '').replace(/_/g, ' ')}
                </span>
              </div>

              <button
                onClick={(e) => handleDelete(e, chat.id)}
                title="Xóa không gian này"
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: '2px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  transition: 'color 0.2s ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = 'var(--accent-rose)'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
              >
                <Trash2 size={13} />
              </button>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <>
      <div 
        style={{
          width: isCollapsed ? '0px' : '280px',
          background: 'var(--bg-sidebar)',
          borderRight: '1px solid var(--border-glass)',
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          position: 'relative',
          transition: 'width 0.25s ease',
          zIndex: 10,
        }}
      >
        {/* Top Header */}
        <div style={{ padding: '16px', borderBottom: '1px solid var(--border-glass)' }}>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <div className="d-flex align-items-center gap-2">
              <div 
                style={{ 
                  width: '28px', 
                  height: '28px', 
                  borderRadius: '8px', 
                  background: 'var(--gradient-brand)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 12px var(--glow-cyan)'
                }}
              >
                <Sparkles size={16} color="#fff" />
              </div>
              <span style={{ fontWeight: 700, fontSize: '0.92rem', letterSpacing: '-0.02em', color: '#f8fafc' }}>
                Không Gian Nghiên Cứu
              </span>
            </div>

            <button
              className="btn-ghost-glass"
              onClick={onToggleCollapse}
              title="Thu gọn Sidebar"
              style={{ padding: '5px', borderRadius: '8px' }}
            >
              <ChevronLeft size={16} />
            </button>
          </div>

          <button
            className="btn-brand w-100 py-2 mb-3"
            onClick={() => setShowNewChatModal(true)}
            style={{ borderRadius: '12px', fontSize: '0.88rem' }}
          >
            <MessageSquarePlus size={16} />
            <span>+ Khởi tạo Không Gian Mới</span>
          </button>

          {/* Search Box */}
          <div style={{ position: 'relative' }}>
            <Search size={14} style={{ position: 'absolute', left: '12px', top: '10px', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Tìm kiếm phiên nghiên cứu..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(14, 19, 32, 0.8)',
                border: '1px solid var(--border-glass)',
                borderRadius: '10px',
                padding: '7px 12px 7px 34px',
                fontSize: '0.82rem',
                color: 'var(--text-primary)',
                outline: 'none',
              }}
            />
          </div>
        </div>

        {/* Conversation List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '12px 8px' }}>
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" size="sm" variant="info" />
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                Đang tải danh sách...
              </div>
            </div>
          ) : groupedConversations.total === 0 ? (
            <div className="text-center py-5" style={{ color: 'var(--text-muted)', fontSize: '0.84rem' }}>
              {searchQuery ? 'Không tìm thấy kết quả.' : 'Chưa có cuộc trò chuyện nào.'}
            </div>
          ) : (
            <>
              {renderSection('Hôm nay', groupedConversations.today)}
              {renderSection('7 ngày qua', groupedConversations.thisWeek)}
              {renderSection('Trước đó', groupedConversations.older)}
            </>
          )}
        </div>

        {/* Sidebar Footer */}
        <div 
          style={{ 
            padding: '12px 16px', 
            borderTop: '1px solid var(--border-glass)',
            fontSize: '0.75rem',
            color: 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <span>NexusDoc Core v2.5</span>
          <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Local Secure</span>
        </div>
      </div>

      {/* Modal Tạo Dự Án / Cuộc Trò Chuyện Mới (Phong cách NotebookLM) */}
      <Modal 
        show={showNewChatModal} 
        onHide={() => !creating && setShowNewChatModal(false)} 
        centered
        size="lg"
      >
        <Modal.Header closeButton={!creating} closeVariant="white">
          <Modal.Title className="d-flex align-items-center gap-2" style={{ fontSize: '1.1rem', fontWeight: 600 }}>
            <Sparkles className="text-info" size={20} />
            <span>Tạo Không Gian Nghiên Cứu Mới</span>
          </Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ padding: '24px' }}>
          {/* Tên dự án */}
          <Form.Group className="mb-4">
            <Form.Label style={{ fontSize: '0.86rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
              Tên dự án / Cuộc trò chuyện:
            </Form.Label>
            <Form.Control
              type="text"
              className="glass-input mt-1"
              placeholder="Ví dụ: Phân tích báo cáo Y tế 2026, Đối chiếu hợp đồng..."
              value={newChatTitle}
              onChange={(e) => setNewChatTitle(e.target.value)}
              disabled={creating}
              autoFocus
            />
          </Form.Group>

          {/* Vùng tải lên tài liệu nguồn trực tiếp */}
          <div className="mb-2">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <span style={{ fontSize: '0.86rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
                Tài liệu nguồn của dự án (Tùy chọn tải ngay):
              </span>
              {selectedFiles.length > 0 && (
                <span style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)' }}>
                  Đã chọn {selectedFiles.length} tệp
                </span>
              )}
            </div>

            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                handleFilesChosen(e.dataTransfer?.files);
              }}
              onClick={() => fileInputRef.current?.click()}
              style={{
                border: `2px dashed ${dragOver ? 'var(--accent-cyan)' : 'var(--border-glass-bright)'}`,
                borderRadius: '16px',
                padding: '24px 20px',
                textAlign: 'center',
                background: dragOver ? 'rgba(6, 182, 212, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                cursor: creating ? 'not-allowed' : 'pointer',
                transition: 'all 0.25s ease',
              }}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={(e) => handleFilesChosen(e.target.files)} 
                style={{ display: 'none' }}
                multiple
                accept=".pdf,.docx,.xlsx,.pptx,.png,.jpg,.jpeg" 
                disabled={creating}
              />

              <div 
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '12px',
                  background: 'rgba(6, 182, 212, 0.12)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '10px',
                }}
              >
                <UploadCloud size={20} color="var(--accent-cyan)" />
              </div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)', marginBottom: '4px' }}>
                Kéo & thả tài liệu vào đây hoặc click để chọn tệp
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Hỗ trợ tải nhiều file: PDF, Word (.docx), Excel (.xlsx) (Tối đa 20MB/file)
              </div>
            </div>

            {/* Danh sách các file đã chọn */}
            {selectedFiles.length > 0 && (
              <div className="mt-3 d-flex flex-wrap gap-2" style={{ maxHeight: '120px', overflowY: 'auto' }}>
                {selectedFiles.map((file, idx) => (
                  <div
                    key={idx}
                    className="glass-card d-flex align-items-center gap-2"
                    style={{
                      padding: '6px 12px',
                      borderRadius: '10px',
                      fontSize: '0.8rem',
                      background: 'rgba(6, 182, 212, 0.08)',
                      borderColor: 'rgba(6, 182, 212, 0.3)',
                    }}
                  >
                    <FileText size={14} color="var(--accent-cyan)" />
                    <span className="text-truncate" style={{ maxWidth: '200px' }}>{file.name}</span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      ({(file.size / 1024).toFixed(0)} KB)
                    </span>
                    {!creating && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeSelectedFile(idx);
                        }}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: 'var(--text-muted)',
                          cursor: 'pointer',
                          padding: '0 2px',
                          display: 'flex',
                          alignItems: 'center',
                        }}
                      >
                        <X size={13} />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </Modal.Body>
        <Modal.Footer>
          <button 
            className="btn-ghost-glass" 
            onClick={() => {
              setShowNewChatModal(false);
              setSelectedFiles([]);
            }}
            disabled={creating}
          >
            Hủy
          </button>
          <button 
            className="btn-brand" 
            onClick={handleNewChat} 
            disabled={creating || (!newChatTitle.trim() && selectedFiles.length === 0)}
          >
            {creating ? (
              <>
                <Spinner size="sm" className="me-2" />
                <span>Đang tải tệp & tạo dự án...</span>
              </>
            ) : (
              <span>{selectedFiles.length > 0 ? `Tạo dự án & Nạp ${selectedFiles.length} tài liệu` : 'Tạo dự án'}</span>
            )}
          </button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default Sidebar;
