import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface QueryInputProps {
  onSendMessage: (message: string) => void;
}

export const QueryInput: React.FC<QueryInputProps> = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
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
          placeholder="Ask about failed logins last week..."
          className="cyber-input flex-1"
        />
        <motion.button
          type="submit"
          className="cyber-button"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Send
        </motion.button>
      </form>
    </motion.div>
  );
};
