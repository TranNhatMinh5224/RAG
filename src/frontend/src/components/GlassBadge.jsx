import React from 'react';
import { FileText, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';

const GlassBadge = ({ filename, status = 'READY', onClick, onRemove, active = false }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'READY':
        return {
          bg: 'rgba(16, 185, 129, 0.12)',
          border: 'rgba(16, 185, 129, 0.3)',
          color: '#10b981',
          icon: <CheckCircle2 size={12} className="text-emerald-400" />
        };
      case 'PROCESSING':
        return {
          bg: 'rgba(245, 158, 11, 0.12)',
          border: 'rgba(245, 158, 11, 0.3)',
          color: '#f59e0b',
          icon: <Loader2 size={12} className="animate-spin text-amber-400" />
        };
      case 'FAILED':
        return {
          bg: 'rgba(244, 63, 94, 0.12)',
          border: 'rgba(244, 63, 94, 0.3)',
          color: '#f43f5e',
          icon: <AlertCircle size={12} className="text-rose-400" />
        };
      default:
        return {
          bg: 'rgba(6, 182, 212, 0.12)',
          border: 'rgba(6, 182, 212, 0.3)',
          color: '#06b6d4',
          icon: <FileText size={12} />
        };
    }
  };

  const cfg = getStatusConfig();

  return (
    <div
      onClick={onClick}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        background: active ? 'rgba(6, 182, 212, 0.22)' : cfg.bg,
        border: `1px solid ${active ? 'var(--accent-cyan)' : cfg.border}`,
        color: active ? '#ffffff' : cfg.color,
        padding: '4px 10px',
        borderRadius: '20px',
        fontSize: '0.82rem',
        fontWeight: 500,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        userSelect: 'none',
        backdropFilter: 'blur(8px)'
      }}
      className="glass-badge"
    >
      {cfg.icon}
      <span style={{ maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {filename}
      </span>
      {onRemove && (
        <span
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          style={{
            marginLeft: '4px',
            opacity: 0.7,
            cursor: 'pointer',
            fontSize: '0.85rem'
          }}
          title="Gỡ khỏi hội thoại"
        >
          ✕
        </span>
      )}
    </div>
  );
};

export default GlassBadge;
