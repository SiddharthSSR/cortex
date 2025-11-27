'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Theme = 'glassmorphism' | 'neo-brutalism';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  isNeoBrutalism: boolean;
  isGlassmorphism: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('glassmorphism');

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('cortex-theme') as Theme;
    if (savedTheme === 'neo-brutalism' || savedTheme === 'glassmorphism') {
      setTheme(savedTheme);
    }
  }, []);

  // Save theme to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('cortex-theme', theme);
    // Add theme class to html element for CSS targeting
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'glassmorphism' ? 'neo-brutalism' : 'glassmorphism'));
  };

  const value = {
    theme,
    toggleTheme,
    isNeoBrutalism: theme === 'neo-brutalism',
    isGlassmorphism: theme === 'glassmorphism',
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
