import React, { useState, useEffect, useRef } from 'react';
import { Button, Spinner } from 'react-bootstrap';
import { Send, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ChatService from '../services/chat_service';
import { toast } from 'react-toastify';

const ChatWindow = ({ conversationId, onOpenDocs }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [chatDetails, setChatDetails] = useState(null);
    const messagesEndRef = useRef(null);

    const loadChat = async () => {
        if (!conversationId) return;
        try {
            setLoading(true);
            const data = await ChatService.loadMessages(conversationId);
            setChatDetails(data);
            setMessages(data.messages || []);
        } catch (error) {
            toast.error("Không thể tải tin nhắn.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadChat();
    }, [conversationId]);

    // Tự động cuộn xuống dưới cùng khi có tin nhắn mới
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || !conversationId) return;

        const userMsg = { sender: 'human', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await ChatService.askAI(conversationId, userMsg.content);
            const aiMsg = { sender: 'ai', content: response.answer };
            setMessages(prev => [...prev, aiMsg]);
        } catch (error) {
            toast.error(error.message);
        } finally {
            setLoading(false);
        }
    };

    if (!conversationId) {
        return (
            <div className="h-100 d-flex align-items-center justify-content-center text-secondary">
                <h4>Vui lòng chọn hoặc tạo một cuộc trò chuyện để bắt đầu.</h4>
            </div>
        );
    }

    return (
        <div className="h-100 d-flex flex-column position-relative">
            {/* Header của Chat */}
            <div className="p-3 border-bottom d-flex justify-content-between align-items-center glass-panel" style={{ borderRadius: '0', borderLeft: 'none', borderRight: 'none', borderTop: 'none', zIndex: 10 }}>
                <h5 className="mb-0 fw-bold">{chatDetails?.title || 'Đang tải...'}</h5>
                <Button variant="outline-info" size="sm" onClick={onOpenDocs} className="d-flex align-items-center gap-2">
                    <FileText size={16} /> 
                    {chatDetails?.documents?.length > 0 ? `${chatDetails.documents.length} File đang dùng` : 'Kẹp tài liệu'}
                </Button>
            </div>

            {/* Vùng hiển thị tin nhắn */}
            <div className="flex-grow-1 overflow-auto p-4" style={{ paddingBottom: '100px' }}>
                {messages.map((msg, idx) => (
                    <div key={idx} className={`d-flex mb-4 ${msg.sender === 'human' ? 'justify-content-end' : 'justify-content-start'}`}>
                        <div 
                            className={`p-3 rounded-4 ${msg.sender === 'human' ? 'bg-primary text-white' : 'glass-panel text-light'}`}
                            style={{ maxWidth: '80%', display: 'inline-block' }}
                        >
                            {msg.sender === 'human' ? (
                                msg.content
                            ) : (
                                <ReactMarkdown remarkPlugins={[remarkGfm]} className="markdown-body text-light bg-transparent">
                                    {msg.content}
                                </ReactMarkdown>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="d-flex justify-content-start mb-4">
                        <div className="glass-panel text-light p-3 rounded-4" style={{ maxWidth: '80%' }}>
                            <Spinner animation="grow" size="sm" variant="info" className="me-2" /> AI đang suy nghĩ...
                        </div>
                    </div>
                )}
                {/* Khoảng trống để tin nhắn cuối không bị thanh chat đè lên */}
                <div style={{ height: '80px' }} />
                <div ref={messagesEndRef} />
            </div>

            {/* Vùng nhập liệu dính ở dưới đáy */}
            <div className="position-absolute bottom-0 w-100 p-3" style={{ background: 'linear-gradient(to top, var(--bg-darker) 60%, transparent)' }}>
                <form onSubmit={handleSend} className="d-flex gap-2">
                    <input
                        type="text"
                        className="glass-input flex-grow-1"
                        placeholder="Hỏi AI về nội dung tài liệu..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={loading}
                    />
                    <Button type="submit" className="btn-gradient" disabled={loading || !input.trim()}>
                        <Send size={20} />
                    </Button>
                </form>
            </div>
        </div>
    );
};

export default ChatWindow;
