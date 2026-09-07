'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Spinner } from 'react-bootstrap';
import { 
  Send, FileText, Copy, Check, Sparkles, Paperclip, BarChart3, 
  BookOpen, Layers, ShieldAlert, RotateCcw, Bot, User, CornerDownLeft, ExternalLink,
  UploadCloud, Plus, X, Loader2, Cpu, ThumbsUp, ThumbsDown, ChevronDown, ChevronUp, Square
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ChatService from '../services/chat_service';
import DocumentService from '../services/document_service';
import { toast } from 'react-toastify';
import GlassBadge from '../components/GlassBadge';
import StatusPill from '../components/StatusPill';
import SourceTooltip from '../components/SourceTooltip';

const cleanDocName = (name) => {
  if (!name) return 'Tài liệu không tên';
  let cleaned = name.replace(/^\d+_[a-f0-9]{16,}\.?/i, '');
  if (cleaned.startsWith('.')) cleaned = 'Tài_liệu' + cleaned;
  cleaned = cleaned.replace(/^\d+_/, '').replace(/_/g, ' ');
  return cleaned || name;
};

const extractSources = (content) => {
  if (!content) return [];
  const matches = content.match(/\[Nguồn:[^\]]+\]/g) || [];
  const unique = Array.from(new Set(matches));
  return unique.map(sourceStr => {
    const clean = sourceStr.replace(/^\[Nguồn:\s*|\s*\]$/g, '');
    const parts = clean.split(' - ');
    const rawFile = parts[0] || 'Tài liệu';
    const cleanFile = cleanDocName(rawFile);
    const pageOrSection = parts.slice(1).join(' - ');
    return {
      raw: sourceStr,
      cleanFile,
      pageOrSection: pageOrSection || 'Toàn văn',
    };
  });
};


const CodeBlock = ({ language, value }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    toast.success("Đã sao chép đoạn code");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div 
      style={{
        background: '#070a12',
        border: '1px solid var(--border-glass)',
        borderRadius: '12px',
        margin: '14px 0',
        overflow: 'hidden',
      }}
    >
      <div 
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(255, 255, 255, 0.03)',
          padding: '8px 16px',
          borderBottom: '1px solid var(--border-glass)',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.78rem',
          color: 'var(--text-secondary)',
        }}
      >
        <span>{language || 'text'}</span>
        <button
          onClick={handleCopy}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px',
            fontSize: '0.78rem',
          }}
        >
          {copied ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
          <span>{copied ? 'Đã chép' : 'Sao chép'}</span>
        </button>
      </div>
      <pre style={{ margin: 0, padding: '14px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.88rem', overflowX: 'auto' }}>
        <code>{value}</code>
      </pre>
    </div>
  );
};

const ChatWindow = ({ conversationId, onOpenDocs, refreshKey }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiState, setAiState] = useState('ready');
  const [chatDetails, setChatDetails] = useState(null);
  const [uploadingSource, setUploadingSource] = useState(false);
  const [centerDragOver, setCenterDragOver] = useState(false);
  const [copiedMsgIdx, setCopiedMsgIdx] = useState(null);
  const [feedbackMap, setFeedbackMap] = useState({});
  const [expandedThoughts, setExpandedThoughts] = useState({});
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const messagesEndRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const isUserAtBottomRef = useRef(true);
  const abortControllerRef = useRef(null);
  const textareaRef = useRef(null);
  const sourceFileInputRef = useRef(null);

  const attachedDocs = chatDetails?.documents || [];
  const hasProcessingDocs = attachedDocs.some(d => d.status === 'PROCESSING');
  const allDocsReady = attachedDocs.length > 0 && !hasProcessingDocs;

  const loadChat = async () => {
    if (!conversationId) return;
    try {
      setLoading(true);
      const data = await ChatService.loadMessages(conversationId);
      setChatDetails(data);
      const formatted = (data.messages || []).map(m => ({
        sender: m.role === 'user' ? 'human' : 'ai',
        content: m.content
      }));
      setMessages(formatted);
    } catch (error) {
      toast.error("Không thể tải lịch sử tin nhắn.");
    } finally {
      setLoading(false);
    }
  };

  // Tự động poll trạng thái tài liệu khi có tài liệu đang PROCESSING
  useEffect(() => {
    if (!hasProcessingDocs || !conversationId) return;

    const interval = setInterval(async () => {
      try {
        const data = await ChatService.loadMessages(conversationId);
        setChatDetails(data);
        const docs = data.documents || [];
        const stillProcessing = docs.some(d => d.status === 'PROCESSING');
        if (!stillProcessing) {
          toast.success("✨ Tài liệu đã được bóc tách & Vector hóa hoàn tất! Sẵn sàng hỏi đáp.");
        }
      } catch (err) {
        console.error("Lỗi khi kiểm tra tiến trình bóc tách tài liệu:", err);
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [hasProcessingDocs, conversationId]);

  const handleDirectUploadSource = async (files) => {
    const fileList = Array.from(files || []);
    if (fileList.length === 0 || !conversationId) return;

    setUploadingSource(true);
    try {
      const currentDocIds = (chatDetails?.documents || []).map(d => d.id);
      const newIds = [];

      for (const file of fileList) {
        try {
          const doc = await DocumentService.uploadFile(file);
          if (doc && doc.id) {
            newIds.push(doc.id);
          }
        } catch (err) {
          toast.warn(`Không thể tải tệp "${file.name}": ${err.message}`);
        }
      }

      if (newIds.length > 0) {
        const updatedIds = [...currentDocIds, ...newIds];
        await ChatService.setContextDocuments(conversationId, updatedIds);
        toast.info(`Đã thêm ${newIds.length} tài liệu vào dự án. Đang tiến hành bóc tách & Vector hóa...`);
        await loadChat();
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setUploadingSource(false);
    }
  };

  const handleRemoveDocFromChat = async (docId, filename) => {
    if (!conversationId) return;
    try {
      const currentDocIds = (chatDetails?.documents || []).map(d => d.id);
      const updatedIds = currentDocIds.filter(id => id !== docId);
      await ChatService.setContextDocuments(conversationId, updatedIds);
      toast.info(`Đã gỡ "${filename}" khỏi dự án này.`);
      await loadChat();
    } catch (error) {
      toast.error("Không thể gỡ tài liệu khỏi hội thoại.");
    }
  };

  useEffect(() => {
    loadChat();
  }, [conversationId, refreshKey]);

  const handleScroll = () => {
    const container = scrollContainerRef.current;
    if (!container) return;
    const isAtBottom = container.scrollHeight - container.scrollTop - container.clientHeight <= 100;
    isUserAtBottomRef.current = isAtBottom;
    setShowScrollBottom(!isAtBottom);
  };

  const scrollToBottom = (behavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
    isUserAtBottomRef.current = true;
    setShowScrollBottom(false);
  };

  // Chỉ cuộn xuống tự động nếu người dùng đang ở cuối khung chat
  useEffect(() => {
    if (isUserAtBottomRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, aiState]);

  // Hủy tiến trình sinh phản hồi (Dừng / Pause)
  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setLoading(false);
    setAiState('ready');
    toast.info("Đã dừng tạo câu trả lời.");
  };

  // Phím tắt Esc để dừng sinh
  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      if (e.key === 'Escape' && (loading || aiState === 'streaming' || aiState === 'thinking')) {
        handleStopGeneration();
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [loading, aiState]);

  // Auto resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleSendPrompt = async (promptText) => {
    if (!promptText.trim() || !conversationId || loading) return;

    if (hasProcessingDocs) {
      toast.warn("Tài liệu đang trong quá trình bóc tách & Vector hóa. Vui lòng đợi trong giây lát!");
      return;
    }

    // Validate that this conversation has at least one attached document
    if (!chatDetails?.documents || chatDetails.documents.length === 0) {
      toast.warn("Đoạn chat này chưa được gắn tài liệu. Vui lòng bấm 'Kẹp tài liệu' để tải lên hoặc chọn tài liệu riêng cho hội thoại!");
      onOpenDocs?.();
      return;
    }

    const userMsg = { sender: 'human', content: promptText };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setLoading(true);
    setAiState('thinking');

    // Reset cuộn xuống cuối khi người dùng vừa gửi câu hỏi mới
    isUserAtBottomRef.current = true;
    setShowScrollBottom(false);
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 50);

    // Khởi tạo AbortController cho tác vụ này
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    // Add empty placeholder AI message
    setMessages(prev => [...prev, { sender: 'ai', content: '' }]);

    try {
      await ChatService.askAIStream(
        conversationId,
        promptText,
        (chunk) => {
          setAiState('streaming');
          setMessages(prev => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx >= 0 && updated[lastIdx].sender === 'ai') {
              updated[lastIdx] = {
                ...updated[lastIdx],
                content: updated[lastIdx].content + chunk
              };
            }
            return updated;
          });
        },
        (error) => {
          if (error.name !== 'AbortError') {
            toast.error(error.message || "Lỗi khi nhận phản hồi từ AI.");
          }
          setAiState('ready');
          setLoading(false);
          abortControllerRef.current = null;
        },
        () => {
          setAiState('ready');
          setLoading(false);
          abortControllerRef.current = null;
        },
        abortController.signal
      );
    } catch (error) {
      if (error.name !== 'AbortError') {
        toast.error(error.message);
      }
      setAiState('ready');
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendPrompt(input);
    }
  };

  const copyMessage = (text, idx = null) => {
    navigator.clipboard.writeText(text);
    if (idx !== null) {
      setCopiedMsgIdx(idx);
      setTimeout(() => setCopiedMsgIdx(null), 2000);
    }
    toast.success("Đã sao chép phản hồi vào clipboard!");
  };

  const handleFeedback = (idx, type) => {
    setFeedbackMap(prev => ({
      ...prev,
      [idx]: prev[idx] === type ? null : type
    }));
    toast.info(type === 'up' ? "Cảm ơn bạn đã đánh giá hữu ích! 👍" : "Đã ghi nhận góp ý cải thiện. 👎");
  };

  const toggleThought = (idx) => {
    setExpandedThoughts(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const handleRegenerate = (msgIdx) => {
    if (loading) return;
    for (let i = msgIdx - 1; i >= 0; i--) {
      if (messages[i]?.sender === 'human') {
        handleSendPrompt(messages[i].content);
        return;
      }
    }
    toast.warn("Không tìm thấy câu hỏi trước đó để thử lại.");
  };

  const renderMessageContent = (content) => {
    const parts = content.split(/(\[Nguồn:[^\]]+\])/g);

    return parts.map((part, index) => {
      if (/^\[Nguồn:[^\]]+\]$/.test(part)) {
        return <SourceTooltip key={index} sourceText={part} />;
      }
      return (
        <ReactMarkdown
          key={index}
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {part}
        </ReactMarkdown>
      );
    });
  };

  if (!conversationId) {
    return (
      <div 
        style={{ 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          padding: '24px',
          background: 'var(--bg-app-base)',
        }}
      >
        <div 
          className="glass-card text-center" 
          style={{ maxWidth: '480px', padding: '48px 32px' }}
        >
          <div 
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '16px',
              background: 'var(--gradient-brand)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 25px var(--glow-cyan)',
              marginBottom: '20px'
            }}
          >
            <Sparkles size={28} color="#fff" />
          </div>
          <h4 style={{ fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '8px' }}>
            RAG Enterprise Assistant
          </h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6', marginBottom: '24px' }}>
            Chọn một cuộc hội thoại từ danh sách bên trái hoặc khởi tạo phiên chat mới để bắt đầu.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div 
      style={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column', 
        position: 'relative', 
        background: 'var(--bg-app-base)',
        overflow: 'hidden' 
      }}
    >
      {/* Top Header Bar */}
      <div 
        style={{
          padding: '12px 24px',
          borderBottom: '1px solid var(--border-glass)',
          background: 'rgba(10, 13, 22, 0.85)',
          backdropFilter: 'blur(20px)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          zIndex: 20,
        }}
      >
        <div style={{ maxWidth: '70%' }}>
          <div className="d-flex align-items-center gap-3">
            <h5 
              className="mb-0 text-truncate" 
              style={{ fontSize: '1rem', fontWeight: 600, letterSpacing: '-0.01em' }}
            >
              {chatDetails?.title || 'Đang tải hội thoại...'}
            </h5>
            <StatusPill state={hasProcessingDocs ? 'embedding' : aiState} />
          </div>

          <div className="d-flex align-items-center gap-2 mt-1 flex-wrap">
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Nguồn tài liệu:</span>
            {attachedDocs.length === 0 ? (
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-amber)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                Chưa có tài liệu nguồn
              </span>
            ) : (
              attachedDocs.map(doc => (
                <GlassBadge 
                  key={doc.id} 
                  filename={doc.filename} 
                  status={doc.status || 'READY'} 
                  onRemove={() => handleRemoveDocFromChat(doc.id, doc.filename)}
                />
              ))
            )}

            {/* Nút nạp thêm tài liệu trực tiếp vào dự án */}
            <button
              type="button"
              className="btn-ghost-glass"
              onClick={() => sourceFileInputRef.current?.click()}
              style={{ padding: '2px 8px', borderRadius: '12px', fontSize: '0.74rem' }}
              disabled={uploadingSource}
              title="Thêm tài liệu vào phiên chat này"
            >
              {uploadingSource ? <Spinner size="sm" style={{ width: '12px', height: '12px' }} /> : <Plus size={12} color="var(--accent-cyan)" />}
              <span>{uploadingSource ? 'Đang nạp...' : '+ Nạp thêm'}</span>
            </button>
            <input 
              type="file" 
              ref={sourceFileInputRef} 
              onChange={(e) => {
                handleDirectUploadSource(e.target.files);
                e.target.value = '';
              }} 
              style={{ display: 'none' }}
              multiple
              accept=".pdf,.docx,.xlsx,.pptx,.png,.jpg,.jpeg" 
            />
          </div>
        </div>

        <button
          className="btn-ghost-glass"
          onClick={onOpenDocs}
          style={{ padding: '7px 14px', borderRadius: '10px' }}
          title="Xem tất cả tài liệu lưu trữ"
        >
          <Paperclip size={15} color="var(--accent-cyan)" />
          <span>Kho Tri Thức ({attachedDocs.length})</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div 
        ref={scrollContainerRef}
        onScroll={handleScroll}
        style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '24px 20px 140px',
        }}
      >
        <div style={{ maxWidth: '860px', margin: '0 auto' }}>
          {/* Trạng thái 1: Dự án mới tạo, chưa có tài liệu nào (Phong cách NotebookLM) */}
          {messages.length === 0 && !loading && attachedDocs.length === 0 && (
            <div style={{ padding: '40px 0 20px', textAlign: 'center' }}>
              <div 
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '20px',
                  background: 'var(--gradient-brand)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 35px var(--glow-cyan)',
                  marginBottom: '20px'
                }}
              >
                <BookOpen size={32} color="#fff" />
              </div>
              <h3 style={{ fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '8px' }}>
                Không Gian Nghiên Cứu Mới
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', maxWidth: '540px', margin: '0 auto 28px' }}>
                Mỗi cuộc trò chuyện hoạt động như một sổ tay độc lập. Hãy tải lên tài liệu nguồn để AI đối chiếu và trích xuất câu trả lời chuẩn xác.
              </p>

              {/* Vùng kéo thả trực tiếp giữa màn hình */}
              <div
                onDragOver={(e) => { e.preventDefault(); setCenterDragOver(true); }}
                onDragLeave={() => setCenterDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setCenterDragOver(false);
                  handleDirectUploadSource(e.dataTransfer?.files);
                }}
                onClick={() => sourceFileInputRef.current?.click()}
                className="glass-card"
                style={{
                  maxWidth: '560px',
                  margin: '0 auto',
                  border: `2px dashed ${centerDragOver ? 'var(--accent-cyan)' : 'var(--border-glass-bright)'}`,
                  borderRadius: '18px',
                  padding: '40px 24px',
                  textAlign: 'center',
                  background: centerDragOver ? 'rgba(6, 182, 212, 0.1)' : 'rgba(255, 255, 255, 0.02)',
                  cursor: uploadingSource ? 'not-allowed' : 'pointer',
                  transition: 'all 0.25s ease',
                }}
              >
                {uploadingSource ? (
                  <div className="py-2">
                    <Spinner animation="border" variant="info" className="mb-3" />
                    <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.95rem' }}>
                      Đang nạp tài liệu vào dự án & lưu trữ Vector...
                    </div>
                  </div>
                ) : (
                  <>
                    <div 
                      style={{
                        width: '50px',
                        height: '50px',
                        borderRadius: '14px',
                        background: 'rgba(6, 182, 212, 0.12)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginBottom: '14px',
                      }}
                    >
                      <UploadCloud size={26} color="var(--accent-cyan)" />
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '6px' }}>
                      Kéo & thả tài liệu vào đây, hoặc click để chọn tệp
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Hỗ trợ PDF, Word (.docx), Excel (.xlsx), Ảnh (Tối đa 20MB)
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Trạng thái 1.5: Tài liệu đang trong tiến trình bóc tách & Vector hóa */}
          {messages.length === 0 && !loading && hasProcessingDocs && (
            <div style={{ padding: '36px 0 20px', textAlign: 'center' }}>
              <div 
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '20px',
                  background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(217, 119, 6, 0.12))',
                  border: '1px solid rgba(245, 158, 11, 0.4)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 35px rgba(245, 158, 11, 0.25)',
                  marginBottom: '20px',
                }}
              >
                <Cpu size={32} color="var(--accent-amber)" />
              </div>
              <h3 style={{ fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '8px', color: '#f59e0b' }}>
                Đang Bóc Tách & Vector Hóa Tài Liệu...
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', maxWidth: '560px', margin: '0 auto 28px', lineHeight: 1.6 }}>
                Hệ thống AI đang lọc nhiễu, phân tích cấu trúc văn bản thông minh (loại trừ mục lục, phân nhóm đề mục) và lưu vector embedding vào Qdrant.
              </p>

              <div 
                className="glass-card" 
                style={{ 
                  maxWidth: '560px', 
                  margin: '0 auto 20px', 
                  padding: '20px', 
                  textAlign: 'left', 
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  background: 'rgba(15, 19, 32, 0.7)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Tài liệu dự án ({attachedDocs.length})
                  </span>
                  <span style={{ fontSize: '0.78rem', color: '#f59e0b', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                    <Loader2 size={13} className="animate-spin" />
                    Đang xử lý nền Celery
                  </span>
                </div>

                <div className="d-flex flex-column gap-2">
                  {attachedDocs.map(doc => (
                    <div 
                      key={doc.id} 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between', 
                        padding: '10px 14px', 
                        borderRadius: '10px', 
                        background: doc.status === 'PROCESSING' ? 'rgba(245, 158, 11, 0.08)' : 'rgba(255, 255, 255, 0.03)', 
                        border: `1px solid ${doc.status === 'PROCESSING' ? 'rgba(245, 158, 11, 0.25)' : 'var(--border-glass)'}`
                      }}
                    >
                      <div className="d-flex align-items-center gap-2 text-truncate" style={{ maxWidth: '72%' }}>
                        <FileText size={16} color={doc.status === 'PROCESSING' ? 'var(--accent-amber)' : 'var(--accent-emerald)'} />
                        <span style={{ fontSize: '0.88rem', fontWeight: 500 }} className="text-truncate" title={doc.filename}>{cleanDocName(doc.filename)}</span>
                      </div>
                      {doc.status === 'PROCESSING' ? (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#f59e0b', background: 'rgba(245, 158, 11, 0.15)', padding: '4px 10px', borderRadius: '12px', fontWeight: 600 }}>
                          <Loader2 size={12} className="animate-spin" />
                          Đang Vector hóa...
                        </span>
                      ) : (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#10b981', background: 'rgba(16, 185, 129, 0.12)', padding: '4px 10px', borderRadius: '12px', fontWeight: 600 }}>
                          <Check size={12} />
                          Đã sẵn sàng
                        </span>
                      )}
                    </div>
                  ))}
                </div>

                <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  <Spinner animation="border" size="sm" style={{ width: '13px', height: '13px', borderWidth: '1.5px', color: '#f59e0b' }} />
                  <span>Giao diện tự động kích hoạt ngay khi hoàn tất (không cần tải lại trang).</span>
                </div>
              </div>
            </div>
          )}

          {/* Trạng thái 2: Đã có tài liệu nguồn và tất cả đã sẵn sàng -> Hiển thị gợi ý câu hỏi */}
          {messages.length === 0 && !loading && allDocsReady && (
            <div style={{ padding: '40px 0 20px', textAlign: 'center' }}>
              <div 
                style={{
                  width: '60px',
                  height: '60px',
                  borderRadius: '18px',
                  background: 'var(--gradient-brand)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 35px var(--glow-cyan)',
                  marginBottom: '20px'
                }}
              >
                <Bot size={32} color="#fff" />
              </div>
              <h3 style={{ fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '10px' }}>
                Không Gian Tri Thức Đã Sẵn Sàng
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', maxWidth: '560px', margin: '0 auto 24px', lineHeight: 1.6 }}>
                Đã kết nối và lập chỉ mục {attachedDocs.length} tài liệu nghiên cứu. Bạn có thể nhập bất kỳ câu hỏi nào vào khung chat bên dưới để bắt đầu tra cứu.
              </p>

              <div 
                style={{ 
                  display: 'inline-flex', 
                  flexWrap: 'wrap', 
                  gap: '8px', 
                  justifyContent: 'center', 
                  maxWidth: '650px', 
                  margin: '0 auto' 
                }}
              >
                {attachedDocs.map(doc => (
                  <div
                    key={doc.id}
                    title={doc.filename}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid var(--border-glass)',
                      padding: '6px 12px',
                      borderRadius: '16px',
                      fontSize: '0.8rem',
                      color: 'var(--text-primary)',
                      backdropFilter: 'blur(8px)',
                    }}
                  >
                    <Check size={13} color="var(--accent-emerald)" />
                    <FileText size={14} color="var(--accent-cyan)" />
                    <span style={{ fontWeight: 500, maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {cleanDocName(doc.filename)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Render Messages */}
          {messages.map((msg, idx) => {
            const isUser = msg.sender === 'human';
            const isCurrentlyStreaming = !isUser && idx === messages.length - 1 && aiState === 'streaming';
            const sources = !isUser ? extractSources(msg.content) : [];
            const isThoughtOpen = expandedThoughts[idx] === true;
            const feedback = feedbackMap[idx];
            const isCopied = copiedMsgIdx === idx;

            return (
              <div 
                key={idx} 
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: isUser ? 'flex-end' : 'flex-start',
                  marginBottom: '28px',
                  width: '100%',
                }}
              >
                {/* Sender Tag */}
                <div 
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '0.78rem',
                    color: 'var(--text-muted)',
                    marginBottom: '6px',
                    padding: '0 4px',
                  }}
                >
                  {isUser ? (
                    <>
                      <span>Bạn</span>
                      <User size={13} />
                    </>
                  ) : (
                    <>
                      <div 
                        style={{
                          width: '18px',
                          height: '18px',
                          borderRadius: '5px',
                          background: 'var(--gradient-brand)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        <Bot size={11} color="#fff" />
                      </div>
                      <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>NexusDoc Intelligence</span>
                    </>
                  )}
                </div>

                {/* Message Bubble */}
                <div
                  style={{
                    maxWidth: isUser ? '85%' : '100%',
                    width: isUser ? 'auto' : '100%',
                    background: isUser ? 'var(--bg-chat-user)' : 'var(--bg-chat-ai)',
                    border: isUser ? '1px solid rgba(255, 255, 255, 0.15)' : '1px solid var(--border-glass)',
                    borderRadius: isUser ? '18px 18px 4px 18px' : '18px',
                    padding: '16px 20px',
                    color: 'var(--text-primary)',
                    boxShadow: isUser 
                      ? '0 8px 24px rgba(29, 78, 216, 0.25)' 
                      : '0 12px 30px rgba(0, 0, 0, 0.35)',
                    lineHeight: '1.65',
                  }}
                >
                  {isUser ? (
                    <div style={{ fontSize: '0.94rem', whiteSpace: 'pre-wrap' }}>
                      {msg.content}
                    </div>
                  ) : (
                    <div className="markdown-content">
                      {/* Thought Process Accordion */}
                      {msg.content && (
                        <div 
                          style={{
                            marginBottom: '14px',
                            borderRadius: '10px',
                            border: '1px solid rgba(6, 182, 212, 0.22)',
                            background: 'rgba(6, 182, 212, 0.04)',
                            overflow: 'hidden',
                          }}
                        >
                          <div 
                            onClick={() => toggleThought(idx)}
                            style={{
                              padding: '8px 12px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              cursor: 'pointer',
                              userSelect: 'none',
                              color: 'var(--accent-cyan)',
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', fontWeight: 600 }}>
                              <Sparkles size={14} className={isCurrentlyStreaming ? "animate-pulse" : ""} />
                              <span>Quá trình phân tích & đối chiếu tri thức</span>
                              {sources.length > 0 && (
                                <span style={{
                                  fontSize: '0.7rem',
                                  background: 'rgba(6, 182, 212, 0.15)',
                                  border: '1px solid rgba(6, 182, 212, 0.3)',
                                  color: '#38bdf8',
                                  padding: '1px 6px',
                                  borderRadius: '6px',
                                  fontWeight: 500,
                                }}>
                                  {sources.length} trích dẫn nguồn
                                </span>
                              )}
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--text-muted)', fontSize: '0.74rem' }}>
                              <span>{isThoughtOpen ? 'Thu gọn' : 'Xem chi tiết'}</span>
                              {isThoughtOpen ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                            </div>
                          </div>

                          {isThoughtOpen && (
                            <div style={{ padding: '8px 12px 10px', borderTop: '1px solid rgba(6, 182, 212, 0.12)', color: 'var(--text-secondary)', fontSize: '0.78rem', lineHeight: '1.6' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
                                <span style={{ color: 'var(--accent-cyan)' }}>✓</span>
                                <span>Truy xuất ngữ nghĩa đa chiều qua Qdrant Vector Store (bge-m3 dense + sparse BM25)</span>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
                                <span style={{ color: 'var(--accent-emerald)' }}>✓</span>
                                <span>Tái xếp hạng và lọc nhiễu văn bản với BAAI Cross-Encoder Re-ranker v2 m3</span>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <span style={{ color: '#a855f7' }}>✓</span>
                                <span>Lập luận, đối chiếu chéo và tổng hợp với mô hình Qwen 2.5 (7B Local Deep Engine)</span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Main Message Markdown Content */}
                      {msg.content ? (
                        <>
                          {renderMessageContent(msg.content)}
                          {isCurrentlyStreaming && <span className="typing-cursor" title="AI đang suy nghĩ và gõ chữ..." />}
                        </>
                      ) : (
                        <div className="d-flex align-items-center gap-2 py-2" style={{ color: 'var(--accent-cyan)' }}>
                          <Spinner animation="grow" size="sm" />
                          <span style={{ fontSize: '0.88rem' }}>Đang trích xuất tri thức và lập luận chuyên sâu...</span>
                        </div>
                      )}

                      {/* Dedicated Sources Footer */}
                      {sources.length > 0 && (
                        <div 
                          style={{
                            marginTop: '16px',
                            paddingTop: '12px',
                            borderTop: '1px solid var(--border-glass)',
                          }}
                        >
                          <div 
                            style={{
                              fontSize: '0.74rem',
                              fontWeight: 600,
                              color: 'var(--text-muted)',
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em',
                              marginBottom: '8px',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                            }}
                          >
                            <BookOpen size={13} color="var(--accent-cyan)" />
                            <span>Tài liệu nguồn đã đối chiếu ({sources.length})</span>
                          </div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {sources.map((src, sIdx) => (
                              <div
                                key={sIdx}
                                title={src.raw}
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  background: 'rgba(255, 255, 255, 0.03)',
                                  border: '1px solid var(--border-glass)',
                                  padding: '4px 10px',
                                  borderRadius: '8px',
                                  fontSize: '0.76rem',
                                  color: 'var(--text-secondary)',
                                  cursor: 'default',
                                  transition: 'all 0.2s ease',
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.borderColor = 'var(--accent-cyan)';
                                  e.currentTarget.style.color = '#ffffff';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.borderColor = 'var(--border-glass)';
                                  e.currentTarget.style.color = 'var(--text-secondary)';
                                }}
                              >
                                <FileText size={12} color="var(--accent-cyan)" />
                                <span style={{ fontWeight: 500, maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                  {src.cleanFile}
                                </span>
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem', background: 'rgba(255, 255, 255, 0.06)', padding: '1px 5px', borderRadius: '4px' }}>
                                  {src.pageOrSection}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* AI Message Action Toolbar */}
                {!isUser && msg.content && (
                  <div 
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      width: '100%',
                      marginTop: '8px',
                      padding: '0 4px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      {/* Nút Sao chép */}
                      <button
                        onClick={() => copyMessage(msg.content, idx)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: isCopied ? 'var(--accent-emerald)' : 'var(--text-muted)',
                          cursor: 'pointer',
                          fontSize: '0.76rem',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          transition: 'color 0.2s ease',
                        }}
                        title="Sao chép toàn bộ phản hồi"
                        onMouseEnter={(e) => { if (!isCopied) e.currentTarget.style.color = 'var(--accent-cyan)'; }}
                        onMouseLeave={(e) => { if (!isCopied) e.currentTarget.style.color = 'var(--text-muted)'; }}
                      >
                        {isCopied ? <Check size={13} color="var(--accent-emerald)" /> : <Copy size={13} />}
                        <span>{isCopied ? 'Đã sao chép' : 'Sao chép'}</span>
                      </button>

                      {/* Nút Thử lại (Regenerate) */}
                      <button
                        onClick={() => handleRegenerate(idx)}
                        disabled={loading}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: 'var(--text-muted)',
                          cursor: loading ? 'not-allowed' : 'pointer',
                          fontSize: '0.76rem',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          opacity: loading ? 0.5 : 1,
                          transition: 'color 0.2s ease',
                        }}
                        title="Hỏi lại câu hỏi này để nhận phản hồi khác"
                        onMouseEnter={(e) => { if (!loading) e.currentTarget.style.color = 'var(--accent-cyan)'; }}
                        onMouseLeave={(e) => { if (!loading) e.currentTarget.style.color = 'var(--text-muted)'; }}
                      >
                        <RotateCcw size={13} />
                        <span>Thử lại</span>
                      </button>

                      {/* Đánh giá Thumbs Up */}
                      <button
                        onClick={() => handleFeedback(idx, 'up')}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: feedback === 'up' ? 'var(--accent-emerald)' : 'var(--text-muted)',
                          cursor: 'pointer',
                          padding: '2px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          transition: 'all 0.2s ease',
                        }}
                        title="Câu trả lời hữu ích"
                        onMouseEnter={(e) => { if (feedback !== 'up') e.currentTarget.style.color = 'var(--accent-emerald)'; }}
                        onMouseLeave={(e) => { if (feedback !== 'up') e.currentTarget.style.color = 'var(--text-muted)'; }}
                      >
                        <ThumbsUp size={13} />
                      </button>

                      {/* Đánh giá Thumbs Down */}
                      <button
                        onClick={() => handleFeedback(idx, 'down')}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: feedback === 'down' ? 'var(--accent-rose)' : 'var(--text-muted)',
                          cursor: 'pointer',
                          padding: '2px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          transition: 'all 0.2s ease',
                        }}
                        title="Câu trả lời cần cải thiện"
                        onMouseEnter={(e) => { if (feedback !== 'down') e.currentTarget.style.color = 'var(--accent-rose)'; }}
                        onMouseLeave={(e) => { if (feedback !== 'down') e.currentTarget.style.color = 'var(--text-muted)'; }}
                      >
                        <ThumbsDown size={13} />
                      </button>
                    </div>

                    {/* Model Info Badge */}
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Cpu size={12} color="var(--accent-cyan)" />
                      <span>Qwen 2.5 (7B Local) • BAAI Re-ranker</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Nút Cuộn xuống nhanh khi người dùng cuộn lên đọc */}
      {showScrollBottom && (
        <div 
          style={{
            position: 'absolute',
            bottom: '95px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 35,
          }}
        >
          <button
            type="button"
            onClick={() => scrollToBottom('smooth')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '20px',
              background: 'rgba(15, 23, 42, 0.9)',
              border: '1px solid rgba(6, 182, 212, 0.45)',
              color: 'var(--text-primary)',
              fontSize: '0.78rem',
              fontWeight: 500,
              backdropFilter: 'blur(12px)',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5), 0 0 15px rgba(6, 182, 212, 0.25)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-cyan)';
              e.currentTarget.style.background = 'rgba(21, 32, 54, 0.95)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.45)';
              e.currentTarget.style.background = 'rgba(15, 23, 42, 0.9)';
            }}
          >
            <ChevronDown size={14} color="var(--accent-cyan)" />
            <span>Cuộn xuống dưới</span>
            {(aiState === 'streaming' || loading) && (
              <span 
                style={{ 
                  width: '7px', 
                  height: '7px', 
                  borderRadius: '50%', 
                  background: 'var(--accent-cyan)',
                  boxShadow: '0 0 8px var(--accent-cyan)',
                  display: 'inline-block' 
                }} 
              />
            )}
          </button>
        </div>
      )}

      {/* Floating Bottom Prompt Bar */}
      <div 
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          background: 'linear-gradient(to top, var(--bg-app-base) 80%, rgba(8, 10, 17, 0) 100%)',
          padding: '20px 24px',
          zIndex: 30,
        }}
      >
        <div style={{ maxWidth: '860px', margin: '0 auto' }}>
          {hasProcessingDocs && (
            <div 
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '8px 16px',
                marginBottom: '10px',
                background: 'rgba(245, 158, 11, 0.12)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                borderRadius: '12px',
                color: '#f59e0b',
                fontSize: '0.82rem',
                fontWeight: 500,
                backdropFilter: 'blur(10px)',
              }}
            >
              <Loader2 size={15} className="animate-spin" />
              <span>Hệ thống đang bóc tách và tạo Vector embedding cho tài liệu... Vui lòng chờ hoàn tất để đặt câu hỏi.</span>
            </div>
          )}

          <div className="floating-prompt-container p-2 d-flex align-items-end gap-2">
            <button
              type="button"
              onClick={onOpenDocs}
              title="Đính kèm tài liệu vào phiên chat"
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-glass)',
                borderRadius: '12px',
                width: '38px',
                height: '38px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--accent-cyan)',
                cursor: 'pointer',
                flexShrink: 0,
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(6, 182, 212, 0.15)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)'}
            >
              <Paperclip size={18} />
            </button>

            <textarea
              ref={textareaRef}
              rows={1}
              className="prompt-textarea"
              placeholder={
                hasProcessingDocs
                  ? "⏳ Đang bóc tách & Vector hóa tài liệu, vui lòng đợi trong giây lát..."
                  : attachedDocs.length > 0
                  ? "Tra cứu, suy luận hoặc yêu cầu phân tích sâu từ tài liệu nguồn..."
                  : "Nhập câu hỏi nghiên cứu hoặc nạp thêm tài liệu để phân tích..."
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading || hasProcessingDocs}
              style={{ 
                padding: '8px 6px',
                opacity: hasProcessingDocs ? 0.6 : 1,
                cursor: hasProcessingDocs ? 'not-allowed' : 'text'
              }}
            />

            {/* Nút Gửi / Nút Dừng sinh phản hồi */}
            {loading || aiState === 'streaming' || aiState === 'thinking' ? (
              <button
                type="button"
                onClick={handleStopGeneration}
                style={{
                  width: '38px',
                  height: '38px',
                  padding: 0,
                  borderRadius: '12px',
                  flexShrink: 0,
                  background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(185, 28, 28, 0.95))',
                  border: '1px solid rgba(239, 68, 68, 0.5)',
                  color: '#ffffff',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 15px rgba(239, 68, 68, 0.35)',
                  transition: 'all 0.2s ease',
                }}
                title="Dừng sinh câu trả lời (Esc)"
              >
                <Square size={13} fill="#ffffff" />
              </button>
            ) : (
              <button
                type="button"
                className="btn-brand"
                onClick={() => handleSendPrompt(input)}
                disabled={loading || hasProcessingDocs || !input.trim()}
                style={{
                  width: '38px',
                  height: '38px',
                  padding: 0,
                  borderRadius: '12px',
                  flexShrink: 0,
                  opacity: (hasProcessingDocs || !input.trim()) ? 0.5 : 1,
                  cursor: (hasProcessingDocs || !input.trim()) ? 'not-allowed' : 'pointer'
                }}
                title={hasProcessingDocs ? "Đang Vector hóa tài liệu..." : "Gửi câu hỏi (Enter)"}
              >
                <Send size={16} />
              </button>
            )}
          </div>

          <div 
            style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              fontSize: '0.72rem', 
              color: 'var(--text-muted)',
              padding: '6px 12px 0' 
            }}
          >
            <span>⚡ NexusDoc Deep Engine • Qwen 2.5 (7B Local) • BAAI Hybrid Reranker</span>
            <span>Nhấn <strong>Enter ↵</strong> để gửi • <strong>Esc</strong> để dừng • <strong>Shift + Enter</strong> xuống dòng</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
