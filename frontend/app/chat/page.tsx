'use client';

import { useState, useEffect } from 'react';
import { Message, Model } from '@/app/types/chat';
import { apiClient } from '@/app/lib/api';
import MessageList from '@/app/components/MessageList';
import ChatInput from '@/app/components/ChatInput';
import { useTheme } from '@/app/contexts/ThemeContext';

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
}

export default function ChatPage() {
  const { toggleTheme, isNeoBrutalism } = useTheme();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [enableAgent, setEnableAgent] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: '1',
      title: 'New Conversation',
      lastMessage: 'Start chatting...',
      timestamp: new Date(),
    },
  ]);
  const [activeConversation, setActiveConversation] = useState('1');

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiClient.healthCheck();
        setIsConnected(true);
      } catch (error) {
        console.error('Backend not reachable:', error);
        setIsConnected(false);
      }
    };

    const loadModels = async () => {
      try {
        const modelsList = await apiClient.getModels();
        setModels(modelsList);
        if (modelsList.length > 0) {
          setSelectedModel(modelsList[0].id);
        }
      } catch (error) {
        console.error('Failed to load models:', error);
      }
    };

    checkConnection();
    loadModels();
  }, []);

  const handleSend = async (content: string) => {
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Update conversation with last message
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === activeConversation
          ? {
              ...conv,
              lastMessage: content.slice(0, 50),
              timestamp: new Date(),
              title: messages.length === 0 ? content.slice(0, 30) : conv.title,
            }
          : conv
      )
    );

    try {
      // Use streaming for better UX when agent is disabled
      const useStreaming = !enableAgent;

      if (useStreaming) {
        // Streaming mode - tokens appear as they're generated
        const assistantMessage: Message = {
          role: 'assistant',
          content: 'Thinking...',
          timestamp: new Date().toISOString(),
        };

        // Add placeholder message immediately for better UX
        setMessages((prev) => [...prev, assistantMessage]);

        let fullContent = '';
        let isFirstChunk = true;

        for await (const chunk of apiClient.chatStream({
          messages: [...messages, userMessage],
          model: selectedModel,
          enable_agent: false,
        })) {
          // Clear placeholder on first chunk
          if (isFirstChunk) {
            fullContent = chunk;
            isFirstChunk = false;
          } else {
            fullContent += chunk;
          }

          // Update the last message with accumulated content
          setMessages((prev) => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              ...newMessages[newMessages.length - 1],
              content: fullContent,
            };
            return newMessages;
          });
        }
      } else {
        // Non-streaming mode - for agent/tool usage
        const response = await apiClient.chat({
          messages: [...messages, userMessage],
          model: selectedModel,
          enable_agent: enableAgent,
        });

        const assistantMessage: Message = {
          ...response.message,
          timestamp: new Date().toISOString(),
          agent_steps: response.agent_steps,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const newConversation = () => {
    const newId = Date.now().toString();
    setConversations((prev) => [
      {
        id: newId,
        title: 'New Conversation',
        lastMessage: 'Start chatting...',
        timestamp: new Date(),
      },
      ...prev,
    ]);
    setActiveConversation(newId);
    setMessages([]);
  };

  const clearChat = () => {
    setMessages([]);
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === activeConversation
          ? {
              ...conv,
              title: 'New Conversation',
              lastMessage: 'Start chatting...',
            }
          : conv
      )
    );
  };

  return (
    <div className={`flex h-screen overflow-hidden ${
      isNeoBrutalism
        ? 'bg-neo-cream'
        : 'bg-gradient-to-br from-[#f0f2f5] via-[#f8f9fa] to-[#e9ecef] dark:from-[#000000] dark:via-[#0a0a0a] dark:to-[#050505]'
    }`}>
      {/* Frosted Glass Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 transition-all duration-500 ease-out ${
          sidebarOpen ? 'w-80' : 'w-0'
        }`}
      >
        <div className={`h-full ${
          isNeoBrutalism
            ? 'bg-white border-r-[4px] border-black'
            : 'glass-morphism dark:glass-morphism-dark border-r border-gray-200/20 dark:border-gray-800/20'
        } overflow-hidden`}>
          {sidebarOpen && (
            <div className="h-full flex flex-col p-5 animate-fadeIn">
              {/* Header */}
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className={`w-11 h-11 flex items-center justify-center text-xl font-bold ${
                    isNeoBrutalism
                      ? 'bg-neo-pink border-[3px] border-black shadow-brutal text-white'
                      : 'rounded-2xl bg-gradient-to-br from-blue-500 via-blue-600 to-purple-600 text-white shadow-xl'
                  }`}>
                    C
                  </div>
                  <div>
                    <h1 className={`text-xl font-bold ${
                      isNeoBrutalism
                        ? 'text-black uppercase tracking-tight'
                        : 'bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent'
                    }`}>
                      Cortex
                    </h1>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <div
                        className={`w-1.5 h-1.5 ${
                          isNeoBrutalism
                            ? isConnected ? 'bg-neo-mint' : 'bg-neo-pink'
                            : isConnected ? 'bg-green-500 animate-pulse rounded-full' : 'bg-red-500 rounded-full'
                        }`}
                      ></div>
                      <span className={`text-[10px] font-medium ${
                        isNeoBrutalism
                          ? 'text-black font-bold uppercase tracking-wide'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        {isConnected ? 'ONLINE' : 'OFFLINE'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* New Conversation Button */}
                <button
                  onClick={newConversation}
                  className={`w-full px-4 py-3 text-sm font-medium transition-all ${
                    isNeoBrutalism
                      ? 'brutal-button text-black'
                      : 'bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 hover:from-blue-600 hover:to-blue-700 text-white rounded-2xl shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4v16m8-8H4"
                      />
                    </svg>
                    <span>New Chat</span>
                  </div>
                </button>
              </div>

              {/* Conversation Threads */}
              <div className="flex-1 overflow-y-auto mb-4 space-y-2">
                <div className={`text-xs font-semibold mb-3 px-2 ${
                  isNeoBrutalism
                    ? 'text-black font-bold uppercase tracking-brutalist'
                    : 'text-gray-500 dark:text-gray-400'
                }`}>
                  CONVERSATIONS
                </div>
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => setActiveConversation(conv.id)}
                    className={`w-full text-left p-3 transition-all ${
                      isNeoBrutalism
                        ? conv.id === activeConversation
                          ? 'bg-neo-yellow border-[3px] border-black shadow-brutal'
                          : 'bg-white border-[2px] border-black hover:bg-neo-gray hover:-translate-y-0.5'
                        : conv.id === activeConversation
                          ? 'bg-gradient-to-br from-blue-500/20 to-purple-500/20 dark:from-blue-600/20 dark:to-purple-600/20 border border-blue-500/30 shadow-sm rounded-xl'
                          : 'hover:bg-gray-100/50 dark:hover:bg-gray-800/30 rounded-xl'
                    }`}
                  >
                    <div className={`text-sm font-medium truncate mb-1 ${
                      isNeoBrutalism
                        ? 'text-black font-bold'
                        : 'text-gray-900 dark:text-white'
                    }`}>
                      {conv.title}
                    </div>
                    <div className={`text-xs truncate ${
                      isNeoBrutalism
                        ? 'text-black font-semibold'
                        : 'text-gray-500 dark:text-gray-400'
                    }`}>
                      {conv.lastMessage}
                    </div>
                  </button>
                ))}
              </div>

              {/* Settings Section */}
              <div className={`space-y-3 pt-4 ${
                isNeoBrutalism
                  ? 'border-t-[3px] border-black'
                  : 'border-t border-gray-200/30 dark:border-gray-700/30'
              }`}>
                {/* Model Selector */}
                <div>
                  <label className={`flex items-center gap-2 text-xs font-semibold mb-3 ${
                    isNeoBrutalism
                      ? 'text-black font-bold uppercase tracking-brutalist'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span>AI MODEL</span>
                  </label>
                  <div className="relative group">
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className={`w-full px-4 py-3.5 text-sm font-semibold focus:outline-none transition-all cursor-pointer appearance-none pr-10 ${
                        isNeoBrutalism
                          ? 'brutal-input'
                          : 'bg-gradient-to-br from-white/60 to-white/40 dark:from-gray-900/60 dark:to-gray-900/40 border border-gray-200/50 dark:border-gray-700/50 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 backdrop-blur-sm hover:from-white/80 hover:to-white/60 dark:hover:from-gray-900/80 dark:hover:to-gray-900/60 text-gray-800 dark:text-gray-100'
                      }`}
                      style={{
                        boxShadow: isNeoBrutalism ? undefined : '0 2px 8px rgba(0, 0, 0, 0.04)',
                        fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", system-ui, sans-serif',
                        letterSpacing: '-0.01em',
                      }}
                    >
                      {models.map((model) => (
                        <option
                          key={model.id}
                          value={model.id}
                          style={{
                            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", system-ui, sans-serif',
                            fontSize: '14px',
                            fontWeight: '600',
                            padding: '12px 16px',
                            backgroundColor: 'white',
                            color: '#1f2937',
                          }}
                        >
                          {model.name || model.id}
                        </option>
                      ))}
                    </select>
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none transition-transform group-hover:translate-y-[-45%]">
                      <svg className="w-5 h-5 text-gray-500 dark:text-gray-400 transition-colors group-hover:text-gray-700 dark:group-hover:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                  {selectedModel && (
                    <div className={`mt-2 flex items-center gap-1.5 px-3 py-1.5 ${
                      isNeoBrutalism
                        ? 'bg-neo-mint border-[2px] border-black font-bold uppercase tracking-wide'
                        : 'bg-blue-500/10 dark:bg-blue-600/10 rounded-lg'
                    }`}>
                      <div className={`w-1.5 h-1.5 ${
                        isNeoBrutalism
                          ? 'bg-black'
                          : 'rounded-full bg-blue-500 animate-pulse'
                      }`}></div>
                      <span className={`text-xs font-medium ${
                        isNeoBrutalism
                          ? 'text-black font-bold'
                          : 'text-blue-600 dark:text-blue-400'
                      }`}>
                        Active
                      </span>
                    </div>
                  )}
                </div>

                {/* Clear Button */}
                <button
                  onClick={clearChat}
                  className={`w-full px-4 py-3 text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 group ${
                    isNeoBrutalism
                      ? 'bg-neo-pink border-[3px] border-black shadow-brutal text-white hover:-translate-y-0.5 hover:shadow-brutal-lg active:translate-y-0.5 active:shadow-brutal-sm uppercase tracking-brutalist'
                      : 'bg-gradient-to-br from-red-500/10 to-red-600/10 hover:from-red-500/20 hover:to-red-600/20 text-red-600 dark:text-red-400 rounded-2xl'
                  }`}
                  style={{
                    boxShadow: isNeoBrutalism ? undefined : '0 2px 8px rgba(239, 68, 68, 0.1)',
                  }}
                >
                  <svg className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <span>Clear Chat</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div
        className={`flex-1 flex flex-col transition-all duration-500 overflow-hidden ${
          sidebarOpen ? 'ml-80' : 'ml-0'
        }`}
      >
        {/* Top Bar with Hamburger */}
        <div className={`${
          isNeoBrutalism
            ? 'bg-white border-b-[3px] border-black'
            : 'glass-morphism dark:glass-morphism-dark border-b border-gray-200/20 dark:border-gray-800/20'
        } px-6 py-4 flex-shrink-0`}>
          <div className="flex items-center justify-between max-w-5xl mx-auto">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2.5 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-xl transition-all group"
            >
              <div className="space-y-1.5">
                <div
                  className={`w-6 h-0.5 bg-gray-600 dark:bg-gray-400 rounded-full transition-all duration-300 ${
                    sidebarOpen ? 'rotate-45 translate-y-2' : ''
                  }`}
                ></div>
                <div
                  className={`w-6 h-0.5 bg-gray-600 dark:bg-gray-400 rounded-full transition-all duration-300 ${
                    sidebarOpen ? 'opacity-0' : ''
                  }`}
                ></div>
                <div
                  className={`w-6 h-0.5 bg-gray-600 dark:bg-gray-400 rounded-full transition-all duration-300 ${
                    sidebarOpen ? '-rotate-45 -translate-y-2' : ''
                  }`}
                ></div>
              </div>
            </button>

            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className={`px-4 py-2 rounded-xl font-semibold text-sm transition-all ${
                isNeoBrutalism
                  ? 'brutal-button'
                  : 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600 shadow-md hover:shadow-lg'
              }`}
            >
              <div className="flex items-center gap-2">
                {isNeoBrutalism ? (
                  <>
                    <span>🌫️</span>
                    <span className="hidden sm:inline">GLASS</span>
                  </>
                ) : (
                  <>
                    <span>⚡</span>
                    <span className="hidden sm:inline">Brutal</span>
                  </>
                )}
              </div>
            </button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden">
          <MessageList messages={messages} isLoading={isLoading} />
        </div>

        {/* Input Area with Agent Toggle */}
        <ChatInput
          onSend={handleSend}
          disabled={isLoading || !isConnected}
          enableAgent={enableAgent}
          onAgentToggle={setEnableAgent}
        />
      </div>
    </div>
  );
}
