'use client';

import { Message } from '@/app/types/chat';
import MessageBubble from './MessageBubble';
import { useEffect, useRef } from 'react';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="min-h-full p-4 space-y-4 w-full max-w-full overflow-x-hidden">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center min-h-[calc(100vh-200px)] text-gray-500 dark:text-gray-400">
          <div className="text-center">
            <div className="text-6xl mb-4">💬</div>
            <div className="text-xl font-semibold mb-2">
              Start a conversation
            </div>
            <div className="text-sm">
              Ask anything - I have access to tools and can run agents!
            </div>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 dark:bg-gray-800 px-4 py-3 rounded-2xl rounded-bl-sm">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0.2s' }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0.4s' }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-500">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}
