import React, { useState, useEffect, useRef } from 'react';
import { Button, Spinner, Dropdown } from 'react-bootstrap';
import { Send, FileText, Copy, Check, Sparkles, PlusCircle, Paperclip, BarChart2, BookOpen, FileCode } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ChatService from '../services/chat_service';
import { toast } from 'react-toastify';
import GlassBadge from '../components/GlassBadge';
import StatusPill from '../components/StatusPill';
import SourceTooltip from '../components/SourceTooltip';

const PromptStarters = [
  {
    icon: <BarChart2 size={18} className="text-cyan-400" />,
    title: 'Phân tích Báo cáo Tài chính',
    prompt: 'Hãy tóm tắt các chỉ số tài chính quan trọng, doanh thu và lợi nhuận từ tài liệu này.'
  },
  {
    icon: <BookOpen size={18} className="text-emerald-400" />,
    title: 'Trích xuất Điều khoản chính',
    prompt: 'Liệt kê tất cả các nghĩa vụ, điều khoản quan trọng và mốc thời gian trong tài liệu.'
  },
  {
    icon: <FileCode size={18} className="text-blue-400" />,
    title: 'So sánh Dữ liệu Bảng',
    prompt: 'So sánh số liệu giữa các phần/sheet và rút ra 3 nhận xét chiến lược.'
  },
  {
    icon: <Sparkles size={18} className="text-amber-400" />,
    title: 'Hỏi đáp Tổng quan',
    prompt: 'Hãy tổng hợp nội dung cốt lõi của tài liệu trong 5 dòng ngắn gọn.'
  }
];

const CodeBlock = ({ language, value }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="code-block-wrapper">
      <div className="code-block-header">
        <span>{language || 'code'}</span>
        <button
          onClick={handleCopy}
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.78rem' }}
        >
          {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
          {copied ? 'Đã chép' : 'Sao chép'}
        </button>
      </div>
      <pre><code>{value}</code></pre>
    </div>
  );
};

const ChatWindow = ({ conversationId, onOpenDocs }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiState, setAiState] = useState('ready'); // 'ready' | 'thinking' | 'streaming'
  const [chatDetails, setChatDetails] = useState(null);
  const messagesEndRef = useRef(null);

  const loadChat = async () => {
    if (!conversationId) return;
    try {
      setLoading(true);
      const data = await ChatService.loadMessages(conversationId);
      setChatDetails(data);
      // Backend return messages role: 'user' or 'ai'
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

  useEffect(() => {
    loadChat();
  }, [conversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, aiState]);

  const handleSendPrompt = async (promptText) => {
    if (!promptText.trim() || !conversationId || loading) return;

    const userMsg = { sender: 'human', content: promptText };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setAiState('thinking');

    // Add empty placeholder AI message for streaming
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
          toast.error(error.message || "Lỗi khi nhận phản hồi từ AI.");
          setAiState('ready');
          setLoading(false);
        },
        () => {
          setAiState('ready');
          setLoading(false);
        }
      );
    } catch (error) {
      toast.error(error.message);
      setAiState('ready');
      setLoading(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    handleSendPrompt(input);
  };

  // Helper to render markdown citations into interactive buttons
  const renderMessageContent = (content) => {
    // Replace citation tags like [Nguồn: test.pdf - Trang 1] with custom marker or render
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
      <div className="h-100 d-flex flex-column align-items-center justify-content-center text-center p-4">
        <div className="glass-panel p-5 rounded-4 max-w-lg" style={{ background: 'rgba(10, 15, 29, 0.6)', border: '1px solid var(--border-glass)' }}>
          <Sparkles size={48} className="text-cyan-400 mb-3 animate-pulse" />
          <h3 className="fw-bold mb-2" style={{ background: 'var(--gradient-brand)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Chào mừng tới RAG AI Analyst
          </h3>
          <p className="text-secondary mb-4" style={{ fontSize: '0.95rem' }}>
            Vui lòng chọn một cuộc trò chuyện ở danh sách bên trái hoặc nhấn nút để tạo hội thoại mới.
          </p>
        </div>
      </div>
    );
  }

  const attachedDocs = chatDetails?.documents || [];

  return (
    <div className="h-100 d-flex flex-column position-relative" style={{ background: 'var(--bg-app-base)' }}>
      {/* Header Chuyên Nghiệp */}
      <div className="p-3 border-bottom d-flex justify-content-between align-items-center glass-panel" style={{ borderRadius: 0, borderLeft: 'none', borderRight: 'none', borderTop: 'none', zIndex: 20 }}>
        <div>
          <div className="d-flex align-items-center gap-2">
            <h5 className="mb-0 fw-bold text-light" style={{ fontSize: '1.1rem' }}>
              {chatDetails?.title || 'Đang tải...'}
            </h5>
            <StatusPill state={aiState} />
          </div>
          {/* Active Documents Bar */}
          <div className="d-flex align-items-center gap-2 mt-2 flex-wrap">
            <span className="text-muted" style={{ fontSize: '0.78rem' }}>Bộ não tham chiếu:</span>
            {attachedDocs.length === 0 ? (
              <span className="text-amber-400" style={{ fontSize: '0.78rem' }}>⚠️ Chưa đính kèm file nào</span>
            ) : (
              attachedDocs.map(doc => (
                <GlassBadge key={doc.id} filename={doc.filename} status={doc.status || 'READY'} />
              ))
            )}
          </div>
        </div>

        <Button
          variant="outline-info"
          size="sm"
          onClick={onOpenDocs}
          className="d-flex align-items-center gap-2 rounded-3"
          style={{ borderColor: 'var(--border-glass-bright)', background: 'rgba(6, 182, 212, 0.1)' }}
        >
          <Paperclip size={16} className="text-cyan-400" />
          <span style={{ fontSize: '0.85rem' }}>
            {attachedDocs.length > 0 ? `Quản lý kho (${attachedDocs.length})` : 'Kẹp tài liệu'}
          </span>
        </Button>
      </div>

      {/* Dynamic Messages Area */}
      <div className="flex-grow-1 overflow-auto p-4" style={{ paddingBottom: '120px' }}>
        {messages.length === 0 && !loading && (
          <div className="py-4">
            <div className="text-center mb-4">
              <Sparkles size={36} className="text-cyan-400 mb-2" />
              <h5 className="fw-bold text-light">Bạn muốn phân tích điều gì hôm nay?</h5>
              <p className="text-secondary" style={{ fontSize: '0.9rem' }}>
                Chọn một câu hỏi gợi ý bên dưới hoặc tự nhập nội dung tra cứu từ tài liệu.
              </p>
            </div>

            <div className="row g-3">
              {PromptStarters.map((ps, idx) => (
                <div key={idx} className="col-md-6">
                  <div
                    onClick={() => handleSendPrompt(ps.prompt)}
                    className="glass-panel glass-panel-hover p-3 rounded-4 cursor-pointer h-100 d-flex flex-column justify-content-between"
                    style={{ background: 'rgba(15, 23, 42, 0.6)' }}
                  >
                    <div className="d-flex align-items-center gap-2 mb-2">
                      {ps.icon}
                      <span className="fw-bold text-light" style={{ fontSize: '0.95rem' }}>{ps.title}</span>
                    </div>
                    <p className="text-secondary mb-0" style={{ fontSize: '0.85rem' }}>{ps.prompt}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`d-flex mb-4 ${msg.sender === 'human' ? 'justify-content-end' : 'justify-content-start'}`}>
            <div
              className={`p-3 rounded-4 ${msg.sender === 'human' ? 'bg-primary text-white shadow-lg' : 'glass-panel text-light'}`}
              style={{
                maxWidth: '82%',
                background: msg.sender === 'human' ? 'var(--bg-chat-user)' : 'var(--bg-chat-ai)',
                border: msg.sender === 'human' ? 'none' : '1px solid var(--border-glass)',
                lineHeight: '1.6'
              }}
            >
              {msg.sender === 'human' ? (
                <div>{msg.content}</div>
              ) : (
                <div className="markdown-body bg-transparent">
                  {msg.content ? renderMessageContent(msg.content) : (
                    <div className="d-flex align-items-center gap-2 text-cyan-400 py-1">
                      <Spinner animation="grow" size="sm" />
                      <span style={{ fontSize: '0.88rem' }}>AI đang đọc tài liệu & tạo câu trả lời...</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* Floating Glass Input Bar */}
      <div className="position-absolute bottom-0 w-100 p-3" style={{ background: 'linear-gradient(to top, var(--bg-app-base) 80%, transparent)', zIndex: 30 }}>
        <form onSubmit={handleFormSubmit} className="d-flex gap-2 align-items-center glass-panel p-2 rounded-4" style={{ background: 'rgba(10, 15, 29, 0.85)', border: '1px solid var(--border-glass-bright)' }}>
          <button
            type="button"
            onClick={onOpenDocs}
            className="btn btn-link text-secondary p-2 text-decoration-none"
            title="Đính kèm file mới"
          >
            <PlusCircle size={22} className="text-cyan-400" />
          </button>

          <input
            type="text"
            className="glass-input flex-grow-1 border-0 bg-transparent text-light"
            placeholder={attachedDocs.length > 0 ? "Hỏi AI bất kỳ điều gì về tài liệu đã đính kèm..." : "Hỏi AI (Lưu ý: Hãy đính kèm file trước khi tra cứu)..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            style={{ boxShadow: 'none' }}
          />

          <Button type="submit" className="btn-brand" disabled={loading || !input.trim()}>
            {loading ? <Spinner size="sm" /> : <Send size={18} />}
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow;
