import React from 'react';
import { Button } from 'react-bootstrap';

const GlassButton = ({ children, type = 'button', onClick, disabled = false, className = '' }) => {
    return (
        <Button 
            type={type} 
            className={`btn-gradient ${className}`} 
            onClick={onClick}
            disabled={disabled}
        >
            {children}
        </Button>
    );
};

export default GlassButton;
