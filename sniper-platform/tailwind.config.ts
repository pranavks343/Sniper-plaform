import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './hooks/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
    './store/**/*.{ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        brand: '#3b82f6',
        success: '#22c55e',
        danger: '#ef4444',
        warning: '#f59e0b'
      },
      fontFamily: {
        heading: ['"Gill Sans"', '"Trebuchet MS"', '"Segoe UI"', 'sans-serif'],
        body: ['"Avenir Next"', '"Segoe UI"', '"Helvetica Neue"', 'sans-serif']
      },
      boxShadow: {
        panel: '0 12px 40px rgba(15, 23, 42, 0.12)'
      }
    }
  },
  darkMode: 'class',
  plugins: []
};

export default config;
