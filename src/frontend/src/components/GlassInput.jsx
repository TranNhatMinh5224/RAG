import React from 'react';

const GlassInput = ({ icon: Icon, type = 'text', placeholder, value, onChange, required = false }) => {
    return (
        <div className="mb-4 position-relative text-start">
            {Icon && (
                <Icon 
                    className="position-absolute" 
                    size={20} 
                    style={{ left: '15px', top: '14px', color: 'var(--text-secondary)' }} 
                />
            )}
            <input 
                type={type} 
                className="glass-input" 
                placeholder={placeholder} 
                style={{ paddingLeft: Icon ? '45px' : '15px' }}
                value={value}
                onChange={onChange}
                required={required}
            />
        </div>
    );
};

export default GlassInput;
