'use client';

import { useState, KeyboardEvent, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  enableAgent?: boolean;
  onAgentToggle?: (enabled: boolean) => void;
}

export default function ChatInput({ onSend, disabled, enableAgent, onAgentToggle }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="px-4 py-4 bg-gradient-to-t from-white/80 via-white/60 to-transparent dark:from-black/80 dark:via-black/60 backdrop-blur-2xl">
      <div className="max-w-4xl mx-auto">
        {/* Floating Toolbar */}
        <div className="glass-morphism dark:glass-morphism-dark rounded-[24px] p-3 shadow-2xl">
          <div className="flex items-end gap-3">
            {/* Agent Mode Capsule Toggle */}
            {onAgentToggle && (
              <button
                onClick={() => onAgentToggle(!enableAgent)}
                className={`flex-shrink-0 px-4 py-2.5 rounded-full font-medium text-sm transition-all duration-300 ${
                  enableAgent
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 text-white agent-glow dark:agent-glow-dark'
                    : 'bg-gray-200/80 dark:bg-gray-700/80 text-gray-700 dark:text-gray-300 hover:bg-gray-300/80 dark:hover:bg-gray-600/80'
                } transform hover:scale-105 active:scale-95`}
              >
                <div className="flex items-center gap-2">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                  <span>Agent</span>
                  {enableAgent && (
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse-slow"></div>
                  )}
                </div>
              </button>
            )}

            {/* Input Container */}
            <div className="flex-1 flex items-center gap-2 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-[20px] px-4 py-2 border border-gray-200/50 dark:border-gray-700/50">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message"
                disabled={disabled}
                rows={1}
                className="flex-1 bg-transparent border-none outline-none resize-none text-[15px] placeholder:text-gray-400 dark:placeholder:text-gray-500 disabled:opacity-50"
                style={{ maxHeight: '120px' }}
              />
            </div>

            {/* Send Button */}
            <button
              onClick={handleSend}
              disabled={disabled || !message.trim()}
              className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200 ${
                disabled || !message.trim()
                  ? 'bg-gray-300 dark:bg-gray-700 opacity-40 cursor-not-allowed'
                  : 'bg-gradient-to-br from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl hover:scale-110 active:scale-95'
              }`}
              style={{
                boxShadow:
                  !disabled && message.trim()
                    ? '0 4px 16px rgba(59, 130, 246, 0.4)'
                    : 'none',
              }}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={2.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 10l7-7m0 0l7 7m-7-7v18"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Helper Text */}
        <div className="text-[11px] text-gray-400 dark:text-gray-600 mt-2 text-center">
          {enableAgent && (
            <span className="text-blue-500 dark:text-blue-400 font-medium mr-2">
              Agent Mode Active
            </span>
          )}
          Press ⏎ to send • ⇧⏎ for new line
        </div>
      </div>
    </div>
  );
}
