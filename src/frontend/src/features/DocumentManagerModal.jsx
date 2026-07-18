import React, { useState, useEffect } from 'react';
import { Modal, Button, ListGroup, Badge, Spinner } from 'react-bootstrap';
import { Upload, FileText, Trash2, CheckSquare, Square } from 'lucide-react';
import DocumentService from '../services/document_service';
import ChatService from '../services/chat_service';
import { toast } from 'react-toastify';

const DocumentManagerModal = ({ show, onHide, conversationId }) => {
    const [documents, setDocuments] = useState([]);
    const [attachedDocIds, setAttachedDocIds] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);

    const loadData = async () => {
        if (!show) return;
        try {
            setLoading(true);
            // Load toàn bộ file của User
            const myDocs = await DocumentService.fetchMyDocuments();
            setDocuments(myDocs);

            // Load các file đang được đính kèm vào conversation này
            if (conversationId) {
                const chatDetails = await ChatService.loadMessages(conversationId);
                const attachedIds = chatDetails.documents.map(d => d.id);
                setAttachedDocIds(attachedIds);
            }
        } catch (error) {
            toast.error(error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [show, conversationId]);

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            setUploading(true);
            const uploadedDoc = await DocumentService.uploadFile(file);
            toast.success("Tải lên và xử lý AI hoàn tất!");
            
            // Tự động tick file vừa tải lên nếu đang ở trong 1 cuộc trò chuyện
            if (conversationId && uploadedDoc && uploadedDoc.id) {
                const newAttachedIds = [...attachedDocIds, uploadedDoc.id];
                await ChatService.setContextDocuments(conversationId, newAttachedIds);
                setAttachedDocIds(newAttachedIds);
            }
            
            loadData(); // Tải lại danh sách
        } catch (error) {
            toast.error(error.message);
        } finally {
            setUploading(false);
            e.target.value = null; // Reset input
        }
    };

    const handleDelete = async (docId) => {
        if (!window.confirm("Thao tác này sẽ xóa vĩnh viễn file khỏi hệ thống. Bạn chắc chứ?")) return;
        try {
            await DocumentService.removeDocument(docId);
            toast.success("Đã xóa file.");
            loadData();
        } catch (error) {
            toast.error(error.message);
        }
    };

    const toggleAttach = async (docId) => {
        let newAttachedIds = [...attachedDocIds];
        if (newAttachedIds.includes(docId)) {
            newAttachedIds = newAttachedIds.filter(id => id !== docId); // Gỡ bỏ
        } else {
            newAttachedIds.push(docId); // Thêm vào
        }

        try {
            // Gọi API lưu trạng thái ghép nối vào Backend
            await ChatService.setContextDocuments(conversationId, newAttachedIds);
            setAttachedDocIds(newAttachedIds);
            toast.success("Đã cập nhật danh sách tài liệu tham khảo cho đoạn chat này.");
        } catch (error) {
            toast.error(error.message);
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="lg" centered contentClassName="glass-panel">
            <Modal.Header closeButton closeVariant="white" className="border-bottom border-secondary">
                <Modal.Title className="text-light"><FileText className="me-2" /> Kho Tài Liệu</Modal.Title>
            </Modal.Header>
            <Modal.Body className="text-light">
                <div className="d-flex justify-content-between align-items-center mb-3">
                    <p className="mb-0 text-secondary">Tích chọn các file muốn làm "Bộ não" cho cuộc trò chuyện này.</p>
                    <div>
                        <input type="file" id="fileUpload" className="d-none" onChange={handleUpload} accept=".pdf,.docx,.xlsx,.pptx" />
                        <Button 
                            variant="primary" 
                            className="btn-gradient" 
                            onClick={() => document.getElementById('fileUpload').click()}
                            disabled={uploading}
                        >
                            {uploading ? <Spinner size="sm" /> : <Upload size={18} className="me-2" />} 
                            Tải file mới lên
                        </Button>
                    </div>
                </div>

                {loading ? (
                    <div className="text-center py-5"><Spinner animation="border" variant="info" /></div>
                ) : documents.length === 0 ? (
                    <div className="text-center text-secondary py-5">Chưa có tài liệu nào. Hãy tải lên file PDF, Word, Excel hoặc PowerPoint.</div>
                ) : (
                    <ListGroup variant="flush" className="bg-transparent">
                        {documents.map(doc => {
                            const isAttached = attachedDocIds.includes(doc.id);
                            return (
                                <ListGroup.Item 
                                    key={doc.id} 
                                    className="bg-transparent border-secondary text-light d-flex justify-content-between align-items-center"
                                >
                                    <div 
                                        className="d-flex align-items-center" 
                                        style={{ cursor: 'pointer' }}
                                        onClick={() => toggleAttach(doc.id)}
                                    >
                                        {isAttached ? <CheckSquare className="text-success me-3" /> : <Square className="text-secondary me-3" />}
                                        <div>
                                            <div className="fw-bold">{doc.filename}</div>
                                            <div className="text-secondary" style={{ fontSize: '0.85rem' }}>
                                                Upload: {new Date(doc.created_at).toLocaleString()}
                                            </div>
                                        </div>
                                    </div>
                                    <div>
                                        {isAttached && <Badge bg="success" className="me-3">Đang dùng</Badge>}
                                        <Button variant="outline-danger" size="sm" onClick={() => handleDelete(doc.id)}>
                                            <Trash2 size={16} />
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
