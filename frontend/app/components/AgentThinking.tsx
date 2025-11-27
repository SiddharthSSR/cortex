'use client';

import { useState } from 'react';
import { AgentStep } from '@/app/types/chat';
import { useTheme } from '@/app/contexts/ThemeContext';

interface AgentThinkingProps {
  steps: AgentStep[];
}

export default function AgentThinking({ steps }: AgentThinkingProps) {
  const { isNeoBrutalism } = useTheme();
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

  const toggleStep = (stepNumber: number) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepNumber)) {
      newExpanded.delete(stepNumber);
    } else {
      newExpanded.add(stepNumber);
    }
    setExpandedSteps(newExpanded);
  };

  const getStatusColor = (status: string) => {
    if (isNeoBrutalism) {
      switch (status) {
        case 'completed':
          return 'bg-neo-mint text-black border-[2px] border-black font-bold';
        case 'failed':
          return 'bg-neo-pink text-white border-[2px] border-black font-bold';
        case 'thinking':
        case 'acting':
        case 'observing':
          return 'bg-neo-yellow text-black border-[2px] border-black font-bold';
        default:
          return 'bg-neo-gray text-black border-[2px] border-black font-bold';
      }
    } else {
      switch (status) {
        case 'completed':
          return 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400';
        case 'failed':
          return 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400';
        case 'thinking':
        case 'acting':
        case 'observing':
          return 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400';
        default:
          return 'bg-gray-50 text-gray-700 dark:bg-gray-800/50 dark:text-gray-400';
      }
    }
  };

  const getToolIcon = (toolName?: string) => {
    if (!toolName) return '🤔';
    switch (toolName) {
      case 'calculator':
        return '🧮';
      case 'web_search':
        return '🔍';
      case 'python_repl':
        return '🐍';
      case 'code_generator':
        return '💻';
      default:
        return '🔧';
    }
  };

  return (
    <div className="mt-3 space-y-1.5">
      <div className={`text-[11px] font-semibold flex items-center gap-1.5 mb-2 ${
        isNeoBrutalism
          ? 'text-black font-bold uppercase tracking-wide'
          : 'text-gray-600 dark:text-gray-400'
      }`}>
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
        Agent Thinking ({steps.length} steps)
      </div>

      <div className="space-y-1.5">
        {steps.map((step) => {
          const isExpanded = expandedSteps.has(step.step_number);

          return (
            <div
              key={step.step_number}
              className={`overflow-hidden ${
                isNeoBrutalism
                  ? 'bg-white border-[3px] border-black shadow-brutal'
                  : 'rounded-xl bg-white/40 dark:bg-black/20 backdrop-blur-sm border border-white/40 dark:border-gray-700/40'
              }`}
            >
              {/* Step Header */}
              <button
                onClick={() => toggleStep(step.step_number)}
                className={`w-full px-3 py-2 flex items-center justify-between transition-colors text-left ${
                  isNeoBrutalism
                    ? 'hover:bg-neo-yellow'
                    : 'hover:bg-white/30 dark:hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-2 flex-1">
                  <span className="text-base">{getToolIcon(step.action || undefined)}</span>
                  <span className={`text-xs font-medium ${
                    isNeoBrutalism
                      ? 'text-black font-bold'
                      : ''
                  }`}>
                    Step {step.step_number}
                    {step.action && `: ${step.action}`}
                  </span>
                  <span
                    className={`text-[10px] px-2 py-0.5 uppercase tracking-wide ${
                      isNeoBrutalism ? '' : 'rounded-full'
                    } ${getStatusColor(step.status)}`}
                  >
                    {step.status}
                  </span>
                </div>
                <svg
                  className={`w-3.5 h-3.5 transition-transform ${
                    isNeoBrutalism ? 'text-black' : 'text-gray-500'
                  } ${isExpanded ? 'transform rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {/* Step Details */}
              {isExpanded && (
                <div className={`px-3 pb-3 space-y-2 text-xs ${
                  isNeoBrutalism ? 'border-t-[3px] border-black' : ''
                }`}>
                  {/* Thought */}
                  <div>
                    <div className={`text-[10px] font-semibold mb-1 ${
                      isNeoBrutalism
                        ? 'text-black font-bold uppercase tracking-wide'
                        : 'text-gray-500 dark:text-gray-400'
                    }`}>
                      💭 Thought
                    </div>
                    <div className={`whitespace-pre-wrap leading-relaxed ${
                      isNeoBrutalism
                        ? 'text-black font-semibold'
                        : 'text-gray-700 dark:text-gray-300'
                    }`}>
                      {step.thought}
                    </div>
                  </div>

                  {/* Action Input */}
                  {step.action_input && Object.keys(step.action_input).length > 0 && (
                    <div>
                      <div className={`text-[10px] font-semibold mb-1 ${
                        isNeoBrutalism
                          ? 'text-black font-bold uppercase tracking-wide'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        ⚙️ Action Input
                      </div>
                      <div className={`px-2 py-1.5 font-mono text-[10px] overflow-x-auto ${
                        isNeoBrutalism
                          ? 'bg-neo-cream border-[2px] border-black font-semibold'
                          : 'bg-gray-50 dark:bg-gray-900/50 rounded-lg'
                      }`}>
                        {JSON.stringify(step.action_input, null, 2)}
                      </div>
                    </div>
                  )}

                  {/* Observation */}
                  {step.observation && (
                    <div>
                      <div className={`text-[10px] font-semibold mb-1 ${
                        isNeoBrutalism
                          ? 'text-black font-bold uppercase tracking-wide'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        👁️ Observation
                      </div>
                      <div className={`whitespace-pre-wrap leading-relaxed ${
                        isNeoBrutalism
                          ? 'text-black font-semibold'
                          : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {step.observation.length > 200
                          ? step.observation.substring(0, 200) + '...'
                          : step.observation}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
