import React from 'react';
import { motion } from 'framer-motion';

interface MessageBubbleProps {
  sender: 'user' | 'ai';
  text: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ sender, text }) => {
  const isUser = sender === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`message-bubble ${
          isUser ? 'message-user' : 'message-ai'
        }`}
      >
        <p className="text-sm leading-relaxed">{text}</p>
      </div>
    </motion.div>
  );
};
