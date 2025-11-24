export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">
          Welcome to Cortex
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          MLX-Powered AI Platform with LLM, Tools, and Agents
        </p>
        <div className="flex gap-4 justify-center">
          <div className="px-6 py-3 bg-blue-600 text-white rounded-lg">
            Chat Interface Coming Soon
          </div>
        </div>
      </div>
    </main>
  );
}
