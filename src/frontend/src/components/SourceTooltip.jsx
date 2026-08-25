import React, { useState } from 'react';
import { FileText, ExternalLink } from 'lucide-react';
import { OverlayTrigger, Popover } from 'react-bootstrap';

const SourceTooltip = ({ sourceText }) => {
  // Parsing [Nguồn: file.pdf - Trang 1] or similar text
  const cleanText = sourceText.replace(/^\[|\]$/g, '');
  
  const popover = (
    <Popover id="popover-source" style={{ background: 'var(--bg-app-base)', border: '1px solid var(--border-glass-bright)', backdropFilter: 'blur(16px)', color: '#f8fafc', maxWidth: '320px' }}>
      <Popover.Header as="h3" style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)', borderBottom: '1px solid var(--border-glass)', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
        <FileText size={14} /> Chi Tiết Trích Dẫn
      </Popover.Header>
      <Popover.Body style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
        <div>Trích dẫn nguồn chính xác từ bộ tài liệu của bạn trong cuộc trò chuyện này.</div>
        <div style={{ marginTop: '8px', padding: '6px 8px', background: 'rgba(255, 255, 255, 0.04)', borderRadius: '6px', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
          {cleanText}
        </div>
      </Popover.Body>
    </Popover>
  );

  return (
    <OverlayTrigger trigger={['hover', 'focus']} placement="top" overlay={popover}>
      <span className="source-citation-badge">
        <FileText size={12} />
        {cleanText}
      </span>
    </OverlayTrigger>
  );
};

export default SourceTooltip;
