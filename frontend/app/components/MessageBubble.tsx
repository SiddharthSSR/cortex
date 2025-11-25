'use client';

import { useState } from 'react';
import { Message } from '@/app/types/chat';
import AgentThinking from './AgentThinking';
import MarkdownRenderer from './MarkdownRenderer';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
  };

  if (isSystem) {
    return (
      <div className="flex justify-center my-6 px-4 animate-fadeIn">
        <div className="bg-white/40 dark:bg-black/30 backdrop-blur-md px-4 py-2 rounded-full text-xs text-gray-600 dark:text-gray-400 border border-white/20 dark:border-white/10 shadow-sm">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 px-4 animate-slideUp`}>
      <div className="flex flex-col max-w-[75%]">
        <div
          className={`relative group px-5 py-3 rounded-[20px] ${
            isUser
              ? 'bg-gradient-to-br from-blue-500/90 to-blue-600/90 dark:from-blue-600/90 dark:to-blue-700/90 text-white backdrop-blur-xl border border-white/20 shadow-lg rounded-br-md'
              : 'bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl border border-gray-200/30 dark:border-gray-700/30 text-gray-900 dark:text-gray-100 shadow-md rounded-bl-md'
          }`}
          style={{
            boxShadow: isUser
              ? '0 8px 32px rgba(59, 130, 246, 0.3), 0 2px 8px rgba(59, 130, 246, 0.2)'
              : '0 4px 24px rgba(0, 0, 0, 0.06), 0 2px 8px rgba(0, 0, 0, 0.04)',
          }}
        >
          {/* Copy button */}
          <button
            onClick={handleCopy}
            className={`absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1.5 rounded-lg ${
              isUser
                ? 'bg-white/20 hover:bg-white/30 text-white'
                : 'bg-gray-200/60 hover:bg-gray-300/60 dark:bg-gray-700/60 dark:hover:bg-gray-600/60 text-gray-700 dark:text-gray-200'
            }`}
            title="Copy message"
          >
            {copied ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>

          <div className="text-[15px]">
            <MarkdownRenderer content={message.content} isUser={isUser} />
          </div>

          {message.tool_calls && message.tool_calls.length > 0 && (
            <div className="mt-3 space-y-2">
              {message.tool_calls.map((tool, idx) => (
                <div
                  key={idx}
                  className={`rounded-2xl p-3 text-sm backdrop-blur-md border ${
                    isUser
                      ? 'bg-white/20 border-white/30'
                      : 'bg-gray-100/50 dark:bg-gray-900/50 border-gray-300/30 dark:border-gray-600/30'
                  }`}
                >
                  <div className="font-semibold flex items-center gap-2 mb-2">
                    <span className="text-lg">🔧</span>
                    <span>{tool.tool_name}</span>
                  </div>
                  <div className="text-xs opacity-80 font-mono bg-black/10 dark:bg-white/10 rounded-lg p-2">
                    {JSON.stringify(tool.parameters, null, 2)}
                  </div>
                  {tool.result && (
                    <div className="text-xs opacity-80 mt-2 pt-2 border-t border-current/20">
                      <div className="font-medium mb-1">Result:</div>
                      <div className="bg-black/10 dark:bg-white/10 rounded-lg p-2">
                        {JSON.stringify(tool.result).slice(0, 100)}...
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {message.agent_steps && message.agent_steps.length > 0 && (
            <div className="mt-3">
              <AgentThinking steps={message.agent_steps} />
            </div>
          )}
        </div>

        {message.timestamp && (
          <div
            className={`text-[11px] mt-1.5 px-2 ${
              isUser ? 'text-right text-gray-500/80' : 'text-left text-gray-500/80'
            }`}
          >
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: 'numeric',
              minute: '2-digit',
            })}
          </div>
        )}
      </div>
    </div>
  );
}
