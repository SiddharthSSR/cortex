import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        // Neo-brutalism color palette
        'neo-yellow': '#FFD23F',
        'neo-pink': '#FF006E',
        'neo-mint': '#06D6A0',
        'neo-black': '#000000',
        'neo-white': '#FFFFFF',
        'neo-cream': '#FFFEF2',
        'neo-gray': '#F5F5F5',
      },
      boxShadow: {
        'brutal': '6px 6px 0 #000',
        'brutal-lg': '8px 8px 0 #000',
        'brutal-sm': '4px 4px 0 #000',
        'brutal-yellow': '6px 6px 0 #FFD23F',
        'brutal-pink': '6px 6px 0 #FF006E',
        'brutal-mint': '6px 6px 0 #06D6A0',
      },
      borderWidth: {
        '3': '3px',
        '4': '4px',
      },
      letterSpacing: {
        'brutalist': '0.5px',
      },
    },
  },
  plugins: [],
};

export default config;
