import type { Metadata } from 'next';
import './globals.css';
import { ThemeProvider } from './contexts/ThemeContext';

export const metadata: Metadata = {
  title: 'Cortex - MLX-Powered AI Platform',
  description: 'Local LLM platform with tools and agents powered by MLX',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
