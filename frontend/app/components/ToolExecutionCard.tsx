'use client';

import { ToolCall } from '@/app/types/chat';
import { useTheme } from '@/app/contexts/ThemeContext';

interface ToolExecutionCardProps {
  toolCalls: ToolCall[];
}

const getToolIcon = (toolName: string) => {
  switch (toolName) {
    case 'calculator':
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      );
    case 'web_search':
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      );
    case 'python_repl':
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      );
    case 'code_generator':
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
      );
    default:
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
      );
  }
};

const getToolDisplayName = (toolName: string) => {
  const nameMap: Record<string, string> = {
    calculator: 'Calculator',
    web_search: 'Web Search',
    python_repl: 'Python',
    code_generator: 'Code Generator',
  };
  return nameMap[toolName] || toolName;
};

export default function ToolExecutionCard({ toolCalls }: ToolExecutionCardProps) {
  const { isNeoBrutalism } = useTheme();

  if (!toolCalls || toolCalls.length === 0) return null;

  return (
    <div className="space-y-2 my-3">
      {toolCalls.map((toolCall, index) => (
        <div
          key={toolCall.id || index}
          className={`p-4 ${
            isNeoBrutalism
              ? 'bg-neo-mint border-[3px] border-black shadow-brutal'
              : 'glass-morphism dark:glass-morphism-dark rounded-xl border border-blue-200/30 dark:border-blue-700/30'
          }`}
        >
          <div className="flex items-start gap-3">
            {/* Tool Icon */}
            <div className={`flex-shrink-0 w-10 h-10 flex items-center justify-center ${
              isNeoBrutalism
                ? 'bg-black text-neo-yellow border-[2px] border-black'
                : 'rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 text-blue-600 dark:text-blue-400'
            }`}>
              {getToolIcon(toolCall.tool_name)}
            </div>

            {/* Tool Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-sm font-semibold ${
                  isNeoBrutalism
                    ? 'text-black font-bold uppercase tracking-wide'
                    : 'text-gray-900 dark:text-white'
                }`}>
                  {getToolDisplayName(toolCall.tool_name)}
                </span>
                <div className="flex items-center gap-1">
                  <div className={`w-1.5 h-1.5 animate-pulse ${
                    isNeoBrutalism
                      ? 'bg-neo-pink'
                      : 'rounded-full bg-blue-500'
                  }`}></div>
                  <span className={`text-xs ${
                    isNeoBrutalism
                      ? 'text-black font-bold uppercase tracking-wide'
                      : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    Executing
                  </span>
                </div>
              </div>

              {/* Parameters */}
              {toolCall.parameters && Object.keys(toolCall.parameters).length > 0 && (
                <div className="mt-2 text-xs">
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(toolCall.parameters).map(([key, value]) => (
                      <div
                        key={key}
                        className={`px-2 py-1 ${
                          isNeoBrutalism
                            ? 'bg-white border-[2px] border-black font-semibold'
                            : 'rounded-md bg-gray-100/60 dark:bg-gray-800/60'
                        }`}
                      >
                        <span className={isNeoBrutalism ? 'text-black' : 'text-gray-600 dark:text-gray-400'}>{key}:</span>{' '}
                        <span className={`font-mono ${
                          isNeoBrutalism
                            ? 'text-black font-bold'
                            : 'text-gray-900 dark:text-white'
                        }`}>
                          {typeof value === 'string' && value.length > 30
                            ? value.slice(0, 30) + '...'
                            : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Result (if available) */}
              {toolCall.result && (
                <div className={`mt-2 p-2 ${
                  isNeoBrutalism
                    ? 'bg-neo-mint border-[2px] border-black'
                    : 'rounded-lg bg-green-500/10 border border-green-500/20'
                }`}>
                  <div className={`text-xs flex items-center gap-1 ${
                    isNeoBrutalism
                      ? 'text-black font-bold uppercase tracking-wide'
                      : 'text-green-700 dark:text-green-400'
                  }`}>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Completed</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
