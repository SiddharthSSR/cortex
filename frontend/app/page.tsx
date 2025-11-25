import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-b from-[#f5f5f7] to-white dark:from-black dark:to-gray-900">
      <div className="text-center max-w-4xl">
        {/* Logo/Icon */}
        <div className="mb-8 flex justify-center">
          <div className="w-24 h-24 rounded-[28px] bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-5xl font-bold shadow-2xl">
            C
          </div>
        </div>

        {/* Title */}
        <h1 className="text-6xl sm:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Cortex
        </h1>
        <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-400 mb-4 font-medium">
          MLX-Powered AI Platform
        </p>
        <p className="text-base text-gray-500 dark:text-gray-500 mb-12 max-w-2xl mx-auto">
          Chat with locally-running LLMs, use powerful tools, and watch intelligent agents solve problems step-by-step
        </p>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12">
          <div className="p-6 bg-white/80 dark:bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-200/50 dark:border-gray-800/50">
            <div className="text-4xl mb-3">💬</div>
            <h3 className="font-semibold text-lg mb-2 text-gray-900 dark:text-white">
              Local LLM Chat
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Powered by MLX running on Apple Silicon
            </p>
          </div>
          <div className="p-6 bg-white/80 dark:bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-200/50 dark:border-gray-800/50">
            <div className="text-4xl mb-3">🔧</div>
            <h3 className="font-semibold text-lg mb-2 text-gray-900 dark:text-white">
              Powerful Tools
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Calculator, web search, code execution, and more
            </p>
          </div>
          <div className="p-6 bg-white/80 dark:bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-200/50 dark:border-gray-800/50">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="font-semibold text-lg mb-2 text-gray-900 dark:text-white">
              ReAct Agents
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Multi-step reasoning and autonomous problem solving
            </p>
          </div>
        </div>

        {/* CTA Button */}
        <Link
          href="/chat"
          className="inline-flex items-center gap-3 px-8 py-4 bg-[#007AFF] dark:bg-[#0A84FF] hover:opacity-90 text-white rounded-full text-lg font-semibold transition-all shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95"
          style={{
            boxShadow: '0 4px 24px rgba(0, 122, 255, 0.3)',
          }}
        >
          <span>Start Chatting</span>
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth={2.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13 7l5 5m0 0l-5 5m5-5H6"
            />
          </svg>
        </Link>

        {/* Footer Info */}
        <div className="mt-16 text-sm text-gray-500 dark:text-gray-600">
          <p>Running locally with privacy and speed</p>
          <p className="mt-1">Backend: http://localhost:8000</p>
        </div>
      </div>
    </main>
  );
}
