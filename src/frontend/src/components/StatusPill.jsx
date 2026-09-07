'use client';

import React from 'react';
import { Sparkles, Activity, CheckCircle, AlertCircle } from 'lucide-react';

const StatusPill = ({ state = 'ready', label }) => {
  const getStateInfo = () => {
    switch (state) {
      case 'thinking':
        return {
          color: 'var(--accent-cyan)',
          bg: 'rgba(6, 182, 212, 0.12)',
          border: 'rgba(6, 182, 212, 0.28)',
          text: label || 'AI đang phân tích ngữ cảnh...',
          dotClass: 'pulsing-dot processing',
        };
      case 'embedding':
        return {
          color: '#f59e0b',
          bg: 'rgba(245, 158, 11, 0.12)',
          border: 'rgba(245, 158, 11, 0.35)',
          text: label || 'Đang bóc tách & Vector hóa...',
          dotClass: 'pulsing-dot processing',
        };
      case 'streaming':
        return {
          color: 'var(--accent-emerald)',
          bg: 'rgba(16, 185, 129, 0.12)',
          border: 'rgba(16, 185, 129, 0.28)',
          text: label || 'Đang phản hồi...',
          dotClass: 'pulsing-dot ready',
        };
      case 'failed':
        return {
          color: 'var(--accent-rose)',
          bg: 'rgba(244, 63, 94, 0.12)',
          border: 'rgba(244, 63, 94, 0.28)',
          text: label || 'Lỗi xử lý',
          dotClass: 'pulsing-dot failed',
        };
      case 'ready':
      default:
        return {
          color: 'var(--text-secondary)',
          bg: 'rgba(255, 255, 255, 0.04)',
          border: 'var(--border-glass)',
          text: label || 'RAG Engine Sẵn sàng',
          dotClass: 'pulsing-dot ready',
        };
    }
  };

  const info = getStateInfo();

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '7px',
        background: info.bg,
        border: `1px solid ${info.border}`,
        color: info.color,
        padding: '4px 11px',
        borderRadius: '20px',
        fontSize: '0.78rem',
        fontWeight: 500,
        fontFamily: 'var(--font-sans)',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
      }}
    >
      <span className={info.dotClass} />
      <span>{info.text}</span>
    </div>
  );
};

export default StatusPill;
