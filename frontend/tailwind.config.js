/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ISRO Space Theme
        space: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        // ISRO Colors
        isro: {
          primary: '#1e40af',
          secondary: '#7c3aed',
          accent: '#0ea5e9',
          orange: '#ea580c',
        },
        // Cybersecurity Theme
        cyber: {
          dark: '#0a0e27',
          darker: '#060920',
          navy: '#1a1f3a',
          blue: '#2563eb',
          cyan: '#06b6d4',
          green: '#10b981',
          red: '#ef4444',
          orange: '#f59e0b',
          purple: '#8b5cf6',
          accent: '#00f5ff',
          yellow: '#ffd23f',
        },
        // Status Colors for SIEM
        status: {
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#3b82f6',
          critical: '#dc2626',
          high: '#ea580c',
          medium: '#d97706',
          low: '#65a30d',
        },
        // Glass Effect Colors
        glass: {
          light: 'rgba(255, 255, 255, 0.1)',
          medium: 'rgba(255, 255, 255, 0.2)',
          dark: 'rgba(0, 0, 0, 0.2)',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Consolas', 'monospace'],
        'display': ['Space Grotesk', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #060920 100%)',
        'space-gradient': 'linear-gradient(135deg, #0c4a6e 0%, #075985 50%, #0369a1 100%)',
        'isro-gradient': 'linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #0ea5e9 100%)',
        'glass-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        'threat-gradient': 'linear-gradient(135deg, #dc2626 0%, #ea580c 100%)',
        'cyber-grid': "url('data:image/svg+xml,%3csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3e%3cdefs%3e%3cpattern id='grid' width='60' height='60' patternUnits='userSpaceOnUse'%3e%3cpath d='M 60 0 L 0 0 0 60' fill='none' stroke='%23334155' stroke-width='1' opacity='0.1'/%3e%3c/pattern%3e%3c/defs%3e%3crect width='100%25' height='100%25' fill='url(%23grid)'/%3e%3c/svg%3e')",
      },
      boxShadow: {
        'cyber': '0 0 20px rgba(6, 182, 212, 0.3)',
        'cyber-lg': '0 0 40px rgba(6, 182, 212, 0.4)',
        'glow': '0 0 20px rgba(59, 130, 246, 0.5)',
        'glow-lg': '0 0 40px rgba(59, 130, 246, 0.6)',
        'space': '0 4px 20px rgba(14, 165, 233, 0.25)',
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'scan': 'scan 2s linear infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #0ea5e9, 0 0 10px #0ea5e9, 0 0 15px #0ea5e9' },
          '100%': { boxShadow: '0 0 10px #0ea5e9, 0 0 20px #0ea5e9, 0 0 30px #0ea5e9' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scan: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
  plugins: [],
}
