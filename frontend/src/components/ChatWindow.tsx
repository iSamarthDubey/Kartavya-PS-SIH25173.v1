import React from 'react';
import { motion } from 'framer-motion';
import { MessageBubble } from './MessageBubble';
import { QueryInput } from './QueryInput';
import { useChatStore } from '../store/useChatStore';

interface ChatWindowProps {
  onSendMessage: (message: string) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ onSendMessage }) => {
  const { messages } = useChatStore();

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto scrollbar-cyber mb-4">
        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="glass-card p-8 max-w-md mx-auto">
              <h3 className="text-lg font-semibold mb-2 neon-text">
                Welcome to SIEM Assistant
              </h3>
              <p className="text-gray-400 text-sm">
                Start a conversation by asking about your security data
              </p>
            </div>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {messages.map((message, index) => (
              <MessageBubble
                key={index}
                sender={message.sender}
                text={message.text}
              />
            ))}
          </div>
        )}
      </div>

      {/* Input Area */}
      <QueryInput onSendMessage={onSendMessage} />
    </div>
  );
};
