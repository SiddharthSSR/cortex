'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeBlock from './CodeBlock';

interface MarkdownRendererProps {
  content: string;
  isUser?: boolean;
}

export default function MarkdownRenderer({ content, isUser = false }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // Code blocks
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          const codeContent = String(children).replace(/\n$/, '');

          if (!inline && match) {
            // Multi-line code block with language
            return <CodeBlock code={codeContent} language={match[1]} />;
          } else if (!inline) {
            // Multi-line code block without language
            return <CodeBlock code={codeContent} language="text" />;
          } else {
            // Inline code
            return (
              <code
                className={`px-1.5 py-0.5 rounded-md text-sm font-mono ${
                  isUser
                    ? 'bg-white/20 text-white'
                    : 'bg-gray-200/60 dark:bg-gray-700/60 text-gray-900 dark:text-gray-100'
                }`}
                {...props}
              >
                {children}
              </code>
            );
          }
        },
        // Headings
        h1({ children }) {
          return (
            <h1 className="text-2xl font-bold mt-4 mb-2">
              {children}
            </h1>
          );
        },
        h2({ children }) {
          return (
            <h2 className="text-xl font-bold mt-3 mb-2">
              {children}
            </h2>
          );
        },
        h3({ children }) {
          return (
            <h3 className="text-lg font-semibold mt-3 mb-1.5">
              {children}
            </h3>
          );
        },
        // Lists
        ul({ children }) {
          return (
            <ul className="list-disc list-inside space-y-1 my-2 ml-2">
              {children}
            </ul>
          );
        },
        ol({ children }) {
          return (
            <ol className="list-decimal list-inside space-y-1 my-2 ml-2">
              {children}
            </ol>
          );
        },
        li({ children }) {
          return (
            <li className="leading-relaxed">
              {children}
            </li>
          );
        },
        // Blockquotes
        blockquote({ children }) {
          return (
            <blockquote
              className={`border-l-4 pl-4 py-1 my-2 italic ${
                isUser
                  ? 'border-white/40'
                  : 'border-gray-400/60 dark:border-gray-600/60'
              }`}
            >
              {children}
            </blockquote>
          );
        },
        // Links
        a({ href, children }) {
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className={`underline hover:opacity-80 transition-opacity ${
                isUser ? 'text-white' : 'text-blue-600 dark:text-blue-400'
              }`}
            >
              {children}
            </a>
          );
        },
        // Paragraphs - use div to allow nested block elements
        p({ children }) {
          return (
            <div className="leading-relaxed my-1.5">
              {children}
            </div>
          );
        },
        // Tables
        table({ children }) {
          return (
            <div className="w-full my-3 overflow-y-auto">
              <table className={`w-full border-collapse ${
                isUser
                  ? 'border border-white/30'
                  : 'border border-gray-300/60 dark:border-gray-700/60'
              }`}>
                {children}
              </table>
            </div>
          );
        },
        th({ children }) {
          return (
            <th className={`px-3 py-2 text-left font-semibold border break-words ${
              isUser
                ? 'border-white/30 bg-white/10'
                : 'border-gray-300/60 dark:border-gray-700/60 bg-gray-100/60 dark:bg-gray-800/60'
            }`}>
              {children}
            </th>
          );
        },
        td({ children }) {
          return (
            <td className={`px-3 py-2 border break-words ${
              isUser
                ? 'border-white/30'
                : 'border-gray-300/60 dark:border-gray-700/60'
            }`}>
              {children}
            </td>
          );
        },
        // Horizontal rule
        hr() {
          return (
            <hr className={`my-3 ${
              isUser
                ? 'border-white/30'
                : 'border-gray-300/60 dark:border-gray-700/60'
            }`} />
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
