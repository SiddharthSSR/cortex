'use client';

import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import { useTheme } from '@/app/contexts/ThemeContext';

interface CodeBlockProps {
  code: string;
  language?: string;
}

export default function CodeBlock({ code, language = 'javascript' }: CodeBlockProps) {
  const { isNeoBrutalism } = useTheme();
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  return (
    <div className={`relative group my-3 overflow-hidden ${
      isNeoBrutalism
        ? 'border-[3px] border-black shadow-brutal'
        : 'rounded-2xl backdrop-blur-xl border border-gray-200/30 dark:border-gray-700/30 shadow-lg'
    }`}>
      {/* Header with language and copy button */}
      <div className={`flex items-center justify-between px-4 py-2 ${
        isNeoBrutalism
          ? 'bg-neo-yellow border-b-[3px] border-black'
          : 'bg-gray-800/90 dark:bg-gray-900/90 backdrop-blur-sm border-b border-gray-700/50'
      }`}>
        <span className={`text-xs font-semibold uppercase tracking-wider ${
          isNeoBrutalism
            ? 'text-black font-bold tracking-brutalist'
            : 'text-gray-300'
        }`}>
          {language}
        </span>
        <button
          onClick={handleCopy}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
            isNeoBrutalism
              ? 'bg-black text-neo-yellow border-[2px] border-black font-bold uppercase hover:-translate-y-0.5'
              : 'rounded-lg bg-gray-700/50 hover:bg-gray-600/50 text-gray-200 hover:scale-105 active:scale-95'
          }`}
        >
          {copied ? (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Copied!</span>
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code content with syntax highlighting */}
      <div className="overflow-y-auto max-w-full">
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            padding: '1rem',
            background: isNeoBrutalism ? '#FFFFFF' : 'rgba(17, 24, 39, 0.95)',
            fontSize: '0.875rem',
            lineHeight: '1.5',
            maxWidth: '100%',
            overflowWrap: 'break-word',
            wordBreak: 'break-word',
            border: isNeoBrutalism ? '2px solid #000000' : 'none',
            borderTop: isNeoBrutalism ? '3px solid #000000' : 'none',
          }}
          showLineNumbers={true}
          lineNumberStyle={{
            minWidth: '2.5em',
            paddingRight: '1em',
            color: isNeoBrutalism ? '#000000' : '#6b7280',
            userSelect: 'none',
            fontWeight: isNeoBrutalism ? '700' : 'normal',
          }}
          wrapLongLines={true}
          codeTagProps={{
            style: {
              color: isNeoBrutalism ? '#000000' : undefined,
              fontFamily: isNeoBrutalism ? 'monospace' : undefined,
              fontWeight: isNeoBrutalism ? '600' : undefined,
            }
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
