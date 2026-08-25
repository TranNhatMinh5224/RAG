import React from 'react';
import { Sparkles, Activity, CheckCircle } from 'lucide-react';

const StatusPill = ({ state = 'ready', label }) => {
  const getStateInfo = () => {
    switch (state) {
      case 'thinking':
        return {
          color: 'var(--accent-cyan)',
          bg: 'rgba(6, 182, 212, 0.15)',
          border: 'rgba(6, 182, 212, 0.3)',
          text: label || 'AI đang đọc tài liệu & suy nghĩ...',
          icon: <Activity size={13} className="animate-spin" />
        };
      case 'streaming':
        return {
          color: 'var(--accent-emerald)',
          bg: 'rgba(16, 185, 129, 0.15)',
          border: 'rgba(16, 185, 129, 0.3)',
          text: label || 'Đang tạo câu trả lời...',
          icon: <Sparkles size={13} className="animate-pulse" />
        };
      case 'ready':
      default:
        return {
          color: 'var(--accent-cyan)',
          bg: 'rgba(6, 182, 212, 0.1)',
          border: 'rgba(6, 182, 212, 0.2)',
          text: label || 'RAG Engine Sẵn Sàng',
          icon: <CheckCircle size={13} />
        };
    }
  };

  const info = getStateInfo();

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        background: info.bg,
        border: `1px solid ${info.border}`,
        color: info.color,
        padding: '3px 10px',
        borderRadius: '12px',
        fontSize: '0.78rem',
        fontWeight: 500,
        fontFamily: 'var(--font-mono)'
      }}
    >
      {info.icon}
      <span>{info.text}</span>
    </div>
  );
};

export default StatusPill;
