import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface QueryInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const QueryInput: React.FC<QueryInputProps> = ({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Ask about failed logins last week..." 
}) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-4"
    >
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className={`cyber-input flex-1 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        />
        <motion.button
          type="submit"
          disabled={disabled || !message.trim()}
          className={`cyber-button ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          whileHover={disabled ? {} : { scale: 1.02 }}
          whileTap={disabled ? {} : { scale: 0.98 }}
        >
          Send
        </motion.button>
      </form>
    </motion.div>
  );
};
