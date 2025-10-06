import React from 'react';
import { motion } from 'framer-motion';
import { ChatWindow } from '../components/ChatWindow';
import { useChatStore } from '../store/useChatStore';

export const Chat: React.FC = () => {
  const { addMessage } = useChatStore();

  const handleSendMessage = async (message: string) => {
    // Add user message
    addMessage({ sender: 'user', text: message });

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        `Found 23 suspicious login attempts across 4 devices. Top sources: Windows authentication failures and SSH brute force attacks.`,
        `Analysis complete: 15 suspicious network connections detected. IP addresses include 192.168.1.100 and 10.0.0.50.`,
        `Security summary: 8 critical alerts, 25 high severity events, and 67 medium priority incidents detected.`,
      ];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      addMessage({ sender: 'ai', text: randomResponse });
    }, 1000);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="h-full flex flex-col"
    >
      <ChatWindow onSendMessage={handleSendMessage} />
    </motion.div>
  );
};
