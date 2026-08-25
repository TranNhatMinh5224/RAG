import React, { useState, useEffect, useRef } from 'react';
import { Modal, Button, ListGroup, Badge, Spinner, Nav } from 'react-bootstrap';
import { Upload, FileText, Trash2, CheckSquare, Square, RefreshCw, AlertCircle, Image as ImageIcon, Table, FileSpreadsheet } from 'lucide-react';
import DocumentService from '../services/document_service';
import ChatService from '../services/chat_service';
import { toast } from 'react-toastify';
import GlassBadge from '../components/GlassBadge';

const DocumentManagerModal = ({ show, onHide, conversationId }) => {
  const [documents, setDocuments] = useState([]);
  const [attachedDocIds, setAttachedDocIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const pollingRef = useRef(null);

  const loadData = async (silent = false) => {
    if (!show) return;
    try {
      if (!silent) setLoading(true);
      // Load all documents belonging to user
      const myDocs = await DocumentService.fetchMyDocuments();
      setDocuments(myDocs);

      // Load documents attached to current conversation
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
      }, 3000);
    } else {
      if (pollingRef.current) clearInterval(pollingRef.current);
    }

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [show, documents]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      const uploadedDoc = await DocumentService.uploadFile(file);
      toast.success("Đã tải file lên! Celery Worker đang xử lý OCR & Nhúng Vector ngầm.");

      // Auto attach uploaded doc to conversation if active
      if (conversationId && uploadedDoc && uploadedDoc.id) {
        const newAttachedIds = [...attachedDocIds, uploadedDoc.id];
        await ChatService.setContextDocuments(conversationId, newAttachedIds);
        setAttachedDocIds(newAttachedIds);
      }

      await loadData();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm("Thao tác này sẽ xóa vĩnh viễn file khỏi hệ thống và Qdrant Vector Store. Bạn chắc chứ?")) return;
    try {
      await DocumentService.removeDocument(docId);
      toast.success("Đã xóa tài liệu sạch sẽ.");
      await loadData();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const toggleAttach = async (docId) => {
    if (!conversationId) {
      toast.info("Vui lòng chọn một cuộc trò chuyện trước khi đính kèm.");
      return;
    }
    let newAttachedIds = [...attachedDocIds];
    if (newAttachedIds.includes(docId)) {
      newAttachedIds = newAttachedIds.filter(id => id !== docId);
    } else {
      newAttachedIds.push(docId);
    }

    try {
      await ChatService.setContextDocuments(conversationId, newAttachedIds);
      setAttachedDocIds(newAttachedIds);
      toast.success("Đã cập nhật danh sách tài liệu tham chiếu.");
    } catch (error) {
      toast.error(error.message);
    }
  };

  // Filtered documents by tab
  const filteredDocs = documents.filter(doc => {
    if (activeTab === 'all') return true;
    const cat = DocumentService.getFileTypeCategory(doc.filename);
    if (activeTab === 'docs' && cat === 'docs') return true;
    if (activeTab === 'sheets' && cat === 'sheets') return true;
    if (activeTab === 'images' && cat === 'images') return true;
    if (activeTab === 'slides' && cat === 'slides') return true;
    return false;
  });

  return (
    <Modal show={show} onHide={onHide} size="lg" centered contentClassName="glass-panel text-light" style={{ backdropFilter: 'blur(20px)' }}>
      <Modal.Header closeButton closeVariant="white" className="border-bottom border-secondary">
        <Modal.Title className="text-light d-flex align-items-center gap-2">
          <FileText className="text-cyan-400" />
          <span>Kho Tài Liệu & Tri Thức RAG</span>
        </Modal.Title>
      </Modal.Header>

      <Modal.Body className="text-light">
        {/* Top Control Bar */}
        <div className="d-flex justify-content-between align-items-center mb-3">
          <p className="mb-0 text-secondary" style={{ fontSize: '0.9rem' }}>
            Tích chọn các file muốn đưa vào bộ nhớ truy vấn cho cuộc trò chuyện hiện tại.
          </p>
          <div>
            <input type="file" id="modalFileUpload" className="d-none" onChange={handleUpload} accept=".pdf,.docx,.xlsx,.pptx,.png,.jpg,.jpeg" />
            <Button
              className="btn-brand"
              onClick={() => document.getElementById('modalFileUpload').click()}
              disabled={uploading}
            >
              {uploading ? <Spinner size="sm" /> : <Upload size={16} />}
              Tải file mới lên
            </Button>
          </div>
        </div>

        {/* Category Tabs */}
        <Nav variant="pills" activeKey={activeTab} onSelect={(selectedKey) => setActiveTab(selectedKey)} className="mb-3 border-bottom border-secondary pb-2">
          <Nav.Item>
            <Nav.Link eventKey="all" className={`text-light ${activeTab === 'all' ? 'bg-cyan-500 text-white fw-bold' : ''}`}>Tất cả ({documents.length})</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="docs" className={`text-light ${activeTab === 'docs' ? 'bg-cyan-500 text-white fw-bold' : ''}`}>PDF & Word</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="sheets" className={`text-light ${activeTab === 'sheets' ? 'bg-cyan-500 text-white fw-bold' : ''}`}>Excel Bảng</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="images" className={`text-light ${activeTab === 'images' ? 'bg-cyan-500 text-white fw-bold' : ''}`}>Ảnh OCR</Nav.Link>
          </Nav.Item>
        </Nav>

        {loading ? (
          <div className="text-center py-5">
            <Spinner animation="border" variant="info" />
            <div className="text-secondary mt-2">Đang nạp danh sách kho tài liệu...</div>
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="text-center text-secondary py-5">
            Không tìm thấy tài liệu phù hợp trong mục này. Hãy tải lên file PDF, Word, Excel, PPTX hoặc Ảnh.
          </div>
        ) : (
          <ListGroup variant="flush" className="bg-transparent">
            {filteredDocs.map(doc => {
              const isAttached = attachedDocIds.includes(doc.id);
              const status = doc.status || 'READY';

              return (
                <ListGroup.Item
                  key={doc.id}
                  className="bg-transparent border-secondary text-light d-flex justify-content-between align-items-center p-3 rounded-3 mb-2 glass-panel-hover"
                  style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border-glass)' }}
                >
                  <div
                    className="d-flex align-items-center gap-3"
                    style={{ cursor: 'pointer', flexGrow: 1 }}
                    onClick={() => toggleAttach(doc.id)}
                  >
                    {isAttached ? (
                      <CheckSquare className="text-cyan-400 flex-shrink-0" size={20} />
                    ) : (
                      <Square className="text-secondary flex-shrink-0" size={20} />
                    )}

                    <div>
                      <div className="fw-bold text-light" style={{ fontSize: '0.95rem' }}>{doc.filename}</div>
                      <div className="text-muted d-flex align-items-center gap-3 mt-1" style={{ fontSize: '0.8rem' }}>
                        <span>Thêm lúc: {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleString('vi-VN') : 'Mới tạo'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="d-flex align-items-center gap-3">
                    <GlassBadge filename={doc.filename} status={status} active={isAttached} />

                    <Button variant="outline-danger" size="sm" onClick={() => handleDelete(doc.id)} title="Xóa file">
                      <Trash2 size={15} />
                    </Button>
                  </div>
                </ListGroup.Item>
              );
            })}
          </ListGroup>
        )}
      </Modal.Body>
    </Modal>
  );
};

export default DocumentManagerModal;
