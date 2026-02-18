import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './hooks/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
    './store/**/*.{ts,tsx}',
    '../../../sniper-framework/src/**/*.{ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        /* TradingView palette */
        'tv-base':      '#131722',
        'tv-surface':   '#1e2230',
        'tv-elevated':  '#2a2e39',
        'tv-overlay':   '#363a45',
        'tv-blue':      '#2962ff',
        'tv-blue-dim':  'rgba(41,98,255,0.12)',
        'tv-bull':      '#26a69a',
        'tv-bear':      '#ef5350',
        'tv-bull-dim':  'rgba(38,166,154,0.12)',
        'tv-bear-dim':  'rgba(239,83,80,0.12)',
        'tv-text':      '#d1d4dc',
        'tv-secondary': '#787b86',
        'tv-muted':     '#50535e',
        'tv-border':    '#2a2e39',
        'tv-border-lg': '#363a45',
        'tv-warning':   '#f7a600',

        /* Legacy aliases */
        brand:   '#2962ff',
        success: '#26a69a',
        danger:  '#ef5350',
        warning: '#f7a600',
        ink:     '#d1d4dc',
        muted:   '#787b86',
        line:    '#2a2e39',
        panel:   '#1e2230'
      },
      fontFamily: {
        sans:    ['Inter', 'Trebuchet MS', 'sans-serif'],
        heading: ['Inter', 'Trebuchet MS', 'sans-serif'],
        body:    ['Inter', 'Trebuchet MS', 'sans-serif'],
        mono:    ['"IBM Plex Mono"', '"JetBrains Mono"', 'Menlo', 'monospace']
      },
      fontSize: {
        '10': '10px',
        '11': '11px',
        '12': '12px',
        '13': '13px'
      },
      boxShadow: {
        panel:  '0 4px 16px rgba(0,0,0,0.4)',
        card:   '0 2px 8px rgba(0,0,0,0.3)',
        popup:  '0 8px 32px rgba(0,0,0,0.5)',
        'glow-bull': '0 0 12px rgba(38,166,154,0.35)',
        'glow-bear': '0 0 12px rgba(239,83,80,0.35)',
        'glow-blue': '0 0 12px rgba(41,98,255,0.35)'
      },
      borderRadius: {
        sm: '3px',
        DEFAULT: '4px',
        md: '6px',
        lg: '8px',
        xl: '12px'
      },
      spacing: {
        '13': '52px',
        '15': '60px',
        '18': '72px'
      },
      transitionDuration: {
        '150': '150ms'
      }
    }
  },
  darkMode: 'class',
  plugins: []
};

export default config;
