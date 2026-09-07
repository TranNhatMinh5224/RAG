'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Modal, Spinner } from 'react-bootstrap';
import { 
  UploadCloud, FileText, Trash2, CheckCircle2, Circle, RefreshCw, 
  AlertCircle, Image as ImageIcon, FileSpreadsheet, FileCode, Check, X
} from 'lucide-react';
import DocumentService from '../services/document_service';
import ChatService from '../services/chat_service';
import { toast } from 'react-toastify';

const cleanDocName = (name) => {
  if (!name) return 'Tài liệu không tên';
  let cleaned = name.replace(/^\d+_[a-f0-9]{16,}\.?/i, '');
  if (cleaned.startsWith('.')) cleaned = 'Tài_liệu' + cleaned;
  cleaned = cleaned.replace(/^\d+_/, '').replace(/_/g, ' ');
  return cleaned || name;
};

const DocumentManagerModal = ({ show, onHide, conversationId, onDocumentsUpdated }) => {
  const [documents, setDocuments] = useState([]);
  const [attachedDocIds, setAttachedDocIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const pollingRef = useRef(null);
  const fileInputRef = useRef(null);

  const loadData = async (silent = false) => {
    if (!show) return;
    try {
      if (!silent) setLoading(true);
      const myDocs = await DocumentService.fetchMyDocuments();
      setDocuments(myDocs);

      if (conversationId) {
        const chatDetails = await ChatService.loadMessages(conversationId);
        const attachedIds = (chatDetails.documents || []).map(d => d.id);
        setAttachedDocIds(attachedIds);
      }
    } catch (error) {
      if (!silent) toast.error(error.message);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [show, conversationId]);

  // Auto Polling if any file has PROCESSING status
  useEffect(() => {
    const hasProcessing = documents.some(doc => doc.status === 'PROCESSING');
    if (show && hasProcessing) {
      pollingRef.current = setInterval(() => {
        loadData(true);
        onDocumentsUpdated?.();
      }, 3000);
    } else {
      if (pollingRef.current) clearInterval(pollingRef.current);
    }

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [show, documents]);

  const processFile = async (file) => {
    if (!file) return;

    try {
      setUploading(true);
      const uploadedDoc = await DocumentService.uploadFile(file);
      toast.success(`Đã tải lên "${file.name}". Đang bóc tách & lưu trữ Vector...`);

      if (conversationId && uploadedDoc && uploadedDoc.id) {
        const newAttachedIds = [...attachedDocIds, uploadedDoc.id];
        await ChatService.setContextDocuments(conversationId, newAttachedIds);
        setAttachedDocIds(newAttachedIds);
        onDocumentsUpdated?.();
      }

      await loadData();
      onDocumentsUpdated?.();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
    e.target.value = '';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer?.files?.[0];
    if (file) processFile(file);
  };

  const toggleAttachDoc = async (docId) => {
    if (!conversationId) {
      toast.warn("Vui lòng mở một cuộc trò chuyện để gắn tài liệu.");
      return;
    }

    const isAttached = attachedDocIds.includes(docId);
    const updatedIds = isAttached
      ? attachedDocIds.filter(id => id !== docId)
      : [...attachedDocIds, docId];

    try {
      await ChatService.setContextDocuments(conversationId, updatedIds);
      setAttachedDocIds(updatedIds);
      onDocumentsUpdated?.();
      toast.info(isAttached ? "Đã gỡ tài liệu khỏi hội thoại" : "Đã gắn tài liệu vào hội thoại");
    } catch (error) {
      toast.error("Không thể cập nhật tài liệu cho phiên chat.");
    }
  };

  const handleDelete = async (e, docId, filename) => {
    e.stopPropagation();
    if (!window.confirm(`Bạn có chắc muốn xóa vĩnh viễn tài liệu "${filename}"?`)) return;

    try {
      await DocumentService.deleteDocument(docId);
      toast.success("Đã xóa tài liệu khỏi kho tri thức.");
      onDocumentsUpdated?.();
      loadData();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const getFileIcon = (filename) => {
    const ext = filename?.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FileText size={20} color="var(--accent-rose)" />;
    if (['xlsx', 'xls', 'csv'].includes(ext)) return <FileSpreadsheet size={20} color="var(--accent-emerald)" />;
    if (['docx', 'doc'].includes(ext)) return <FileText size={20} color="var(--accent-cyan)" />;
    if (['png', 'jpg', 'jpeg'].includes(ext)) return <ImageIcon size={20} color="var(--accent-indigo)" />;
    return <FileCode size={20} color="var(--text-secondary)" />;
  };

  return (
    <Modal 
      show={show} 
      onHide={onHide} 
      size="lg" 
      centered
    >
      <Modal.Header closeButton closeVariant="white">
        <Modal.Title className="d-flex align-items-center gap-2" style={{ fontSize: '1.1rem', fontWeight: 600 }}>
          <UploadCloud size={22} color="var(--accent-cyan)" />
          <span>Kho Lưu Trữ Tri Thức & Tài Liệu Nguồn</span>
        </Modal.Title>
      </Modal.Header>

      <Modal.Body style={{ padding: '24px' }}>
        {/* Drag & Drop Upload Zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${dragOver ? 'var(--accent-cyan)' : 'var(--border-glass-bright)'}`,
            borderRadius: '16px',
            padding: '32px 20px',
            textAlign: 'center',
            background: dragOver ? 'rgba(6, 182, 212, 0.08)' : 'rgba(255, 255, 255, 0.02)',
            cursor: 'pointer',
            transition: 'all 0.25s ease',
            marginBottom: '24px',
            position: 'relative',
          }}
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileInput} 
            style={{ display: 'none' }}
            accept=".pdf,.docx,.xlsx,.pptx,.png,.jpg,.jpeg" 
          />

          {uploading ? (
            <div className="py-2">
              <Spinner animation="border" variant="info" className="mb-2" />
              <div style={{ color: 'var(--text-primary)', fontWeight: 500, fontSize: '0.9rem' }}>
                Đang tải tệp lên và vector hóa...
              </div>
            </div>
          ) : (
            <>
              <div 
                style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '14px',
                  background: 'rgba(6, 182, 212, 0.12)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '12px',
                }}
              >
                <UploadCloud size={24} color="var(--accent-cyan)" />
              </div>
              <div style={{ fontWeight: 600, fontSize: '0.94rem', color: 'var(--text-primary)', marginBottom: '4px' }}>
                Kéo & thả tệp vào đây, hoặc click để chọn từ máy tính
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Hỗ trợ: PDF (báo cáo, hợp đồng), Word (.docx), Excel (.xlsx), Ảnh hóa đơn (Tối đa 25MB)
              </div>
            </>
          )}
        </div>

        {/* Documents Table / List */}
        <div>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Tri thức & Tài liệu đã nạp ({documents.length})
            </span>
            {conversationId && (
              <span style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)' }}>
                Đang liên kết vào không gian này: {attachedDocIds.length} tài liệu
              </span>
            )}
          </div>

          {loading && documents.length === 0 ? (
            <div className="text-center py-5" style={{ color: 'var(--text-muted)' }}>
              <Spinner animation="border" size="sm" variant="info" className="me-2" />
              Đang tải danh sách tài liệu...
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-5" style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              Kho tài liệu chưa có tệp nào. Hãy tải lên tài liệu đầu tiên ở trên!
            </div>
          ) : (
            <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
              {documents.map((doc) => {
                const isAttached = attachedDocIds.includes(doc.id);
                const isReady = doc.status === 'READY';
                const isProcessing = doc.status === 'PROCESSING';

                return (
                  <div
                    key={doc.id}
                    onClick={() => toggleAttachDoc(doc.id)}
                    className="glass-card mb-2"
                    style={{
                      padding: '12px 16px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      background: isAttached ? 'rgba(6, 182, 212, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                      borderColor: isAttached ? 'rgba(6, 182, 212, 0.35)' : 'var(--border-glass)',
                      cursor: 'pointer',
                    }}
                  >
                    <div className="d-flex align-items-center gap-3 text-truncate" style={{ maxWidth: '75%' }}>
                      {/* Checkbox Icon */}
                      {isAttached ? (
                        <CheckCircle2 size={18} color="var(--accent-cyan)" style={{ flexShrink: 0 }} />
                      ) : (
                        <Circle size={18} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                      )}

                      {/* File Icon */}
                      <div style={{ flexShrink: 0 }}>
                        {getFileIcon(doc.filename)}
                      </div>

                      {/* Name & Date */}
                      <div className="text-truncate">
                        <div className="text-truncate" style={{ fontWeight: 500, fontSize: '0.88rem', color: 'var(--text-primary)' }} title={doc.filename}>
                          {cleanDocName(doc.filename)}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                          {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString('vi-VN') : 'Mới cập nhật'}
                        </div>
                      </div>
                    </div>

                    {/* Status & Actions */}
                    <div className="d-flex align-items-center gap-3">
                      {isProcessing ? (
                        <span 
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            background: 'rgba(245, 158, 11, 0.12)',
                            color: 'var(--accent-amber)',
                            fontSize: '0.75rem',
                            padding: '3px 9px',
                            borderRadius: '12px',
                            fontWeight: 500,
                          }}
                        >
                          <span className="pulsing-dot processing" />
                          <span>Đang bóc tách</span>
                        </span>
                      ) : isReady ? (
                        <span 
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            background: 'rgba(16, 185, 129, 0.12)',
                            color: 'var(--accent-emerald)',
                            fontSize: '0.75rem',
                            padding: '3px 9px',
                            borderRadius: '12px',
                            fontWeight: 500,
                          }}
                        >
                          <span className="pulsing-dot ready" />
                          <span>Sẵn sàng</span>
                        </span>
                      ) : (
                        <span 
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            background: 'rgba(244, 63, 94, 0.12)',
                            color: 'var(--accent-rose)',
                            fontSize: '0.75rem',
                            padding: '3px 9px',
                            borderRadius: '12px',
                            fontWeight: 500,
                          }}
                        >
                          <span className="pulsing-dot failed" />
                          <span>Lỗi vector</span>
                        </span>
                      )}

                      <button
                        onClick={(e) => handleDelete(e, doc.id, doc.filename)}
                        title="Xóa tài liệu"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: 'var(--text-muted)',
                          cursor: 'pointer',
                          padding: '4px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          transition: 'color 0.2s ease',
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.color = 'var(--accent-rose)'}
                        onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </Modal.Body>

      <Modal.Footer>
        <button 
          className="btn-brand" 
          onClick={onHide}
          style={{ borderRadius: '10px', padding: '8px 22px' }}
        >
          Xong
        </button>
      </Modal.Footer>
    </Modal>
  );
};

export default DocumentManagerModal;
