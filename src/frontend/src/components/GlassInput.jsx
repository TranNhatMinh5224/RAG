'use client';

import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

const GlassInput = ({ icon: Icon, type = 'text', placeholder, value, onChange, required = false }) => {
    const [showPassword, setShowPassword] = useState(false);
    const isPasswordType = type === 'password';
    const inputType = isPasswordType ? (showPassword ? 'text' : 'password') : type;

    return (
        <div style={{ position: 'relative', width: '100%' }}>
            {/* Left Icon */}
            {Icon && (
                <div 
                    style={{ 
                        position: 'absolute', 
                        left: '14px', 
                        top: '50%', 
                        transform: 'translateY(-50%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--text-muted)',
                        pointerEvents: 'none',
                        zIndex: 2,
                    }}
                >
                    <Icon size={18} />
                </div>
            )}

            {/* Main Input Element */}
            <input 
                type={inputType} 
                className="glass-input-field" 
                placeholder={placeholder} 
                style={{ 
                    width: '100%',
                    height: '48px',
                    paddingLeft: Icon ? '44px' : '16px',
                    paddingRight: isPasswordType ? '46px' : '16px',
                    background: 'rgba(12, 17, 30, 0.85)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '12px',
                    color: '#f8fafc',
                    fontSize: '0.92rem',
                    outline: 'none',
                    transition: 'all 0.2s ease',
                    boxShadow: 'inset 0 2px 4px rgba(0, 0, 0, 0.3)',
                }}
                value={value}
                onChange={onChange}
                required={required}
                onFocus={(e) => {
                    e.target.style.borderColor = 'var(--accent-cyan)';
                    e.target.style.boxShadow = '0 0 0 3px rgba(6, 182, 212, 0.25), inset 0 2px 4px rgba(0, 0, 0, 0.2)';
                    e.target.style.background = 'rgba(16, 23, 40, 0.95)';
                }}
                onBlur={(e) => {
                    e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)';
                    e.target.style.boxShadow = 'inset 0 2px 4px rgba(0, 0, 0, 0.3)';
                    e.target.style.background = 'rgba(12, 17, 30, 0.85)';
                }}
            />

            {/* Right Eye Toggle Button for Password Fields */}
            {isPasswordType && (
                <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex={-1}
                    style={{
                        position: 'absolute',
                        right: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'transparent',
                        border: 'none',
                        color: showPassword ? 'var(--accent-cyan)' : 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: '8px',
                        transition: 'all 0.2s ease',
                        zIndex: 2,
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.color = 'var(--accent-cyan)'}
                    onMouseLeave={(e) => {
                        if (!showPassword) e.currentTarget.style.color = 'var(--text-muted)';
                    }}
                    title={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
            )}
        </div>
    );
};

export default GlassInput;
