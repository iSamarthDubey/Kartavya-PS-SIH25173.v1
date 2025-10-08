/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ISRO Space Theme (Enhanced)
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
        // ISRO Official Colors
        isro: {
          primary: '#003d82',     // ISRO Deep Blue
          secondary: '#1e40af',   // Space Blue
          accent: '#0ea5e9',      // Bright Blue
          orange: '#ff6b35',      // ISRO Orange
          gold: '#fbbf24',        // Achievement Gold
          silver: '#e5e7eb',      // Tech Silver
        },
        // Wazuh-inspired Security Colors
        wazuh: {
          primary: '#1a365d',     // Wazuh Deep Blue
          secondary: '#2d3748',   // Dark Gray
          accent: '#4299e1',      // Security Blue
          success: '#38a169',     // Safe Green
          warning: '#ed8936',     // Alert Orange
          danger: '#e53e3e',      // Threat Red
          info: '#3182ce',        // Info Blue
        },
        // ELK Stack Colors
        elk: {
          elastic: '#005571',     // Elasticsearch Teal
          kibana: '#e7664c',      // Kibana Orange-Red
          logstash: '#f4d03f',    // Logstash Yellow
          beats: '#00bfb3',       // Beats Cyan
          dark: '#1a1c20',        // ELK Dark
          panel: '#2a2d31',       // Panel Gray
        },
        // Unified Security Theme
        security: {
          background: '#0a0f1c',   // Deep Space Background
          surface: '#1a1f3a',     // Surface Dark Blue
          panel: '#252c4a',       // Panel Medium Blue
          border: '#374466',      // Border Light Blue
          text: '#e2e8f0',        // Text Light
          muted: '#94a3b8',       // Muted Text
          accent: '#00d9ff',      // Bright Cyan Accent
          success: '#10b981',     // Success Green
          warning: '#f59e0b',     // Warning Orange
          error: '#ef4444',       // Error Red
          info: '#3b82f6',        // Info Blue
        },
        // Threat Level Colors
        threat: {
          critical: '#dc2626',    // Critical Red
          high: '#ea580c',        // High Orange
          medium: '#d97706',      // Medium Yellow
          low: '#65a30d',         // Low Green
          info: '#0284c7',        // Info Blue
          unknown: '#6b7280',     // Unknown Gray
        },
        // Glass Effect Colors
        glass: {
          light: 'rgba(255, 255, 255, 0.05)',
          medium: 'rgba(255, 255, 255, 0.1)',
          heavy: 'rgba(255, 255, 255, 0.15)',
          dark: 'rgba(0, 0, 0, 0.2)',
          darker: 'rgba(0, 0, 0, 0.4)',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Consolas', 'monospace'],
        'display': ['Space Grotesk', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        // Primary Gradients
        'security-gradient': 'linear-gradient(135deg, #0a0f1c 0%, #1a1f3a 25%, #252c4a 50%, #1a1f3a 75%, #0a0f1c 100%)',
        'isro-gradient': 'linear-gradient(135deg, #003d82 0%, #1e40af 50%, #0ea5e9 100%)',
        'wazuh-gradient': 'linear-gradient(135deg, #1a365d 0%, #2d3748 50%, #4299e1 100%)',
        'elk-gradient': 'linear-gradient(135deg, #005571 0%, #1a1c20 50%, #00bfb3 100%)',
        
        // Accent Gradients
        'space-gradient': 'linear-gradient(135deg, #0c4a6e 0%, #075985 50%, #0369a1 100%)',
        'cyber-gradient': 'linear-gradient(135deg, #0a0f1c 0%, #1a1f3a 50%, #252c4a 100%)',
        'threat-gradient': 'linear-gradient(135deg, #dc2626 0%, #ea580c 50%, #f59e0b 100%)',
        'success-gradient': 'linear-gradient(135deg, #065f46 0%, #10b981 50%, #34d399 100%)',
        
        // Glass and Panel Effects
        'glass-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        'panel-gradient': 'linear-gradient(135deg, rgba(37,44,74,0.8) 0%, rgba(26,31,58,0.9) 100%)',
        'border-gradient': 'linear-gradient(90deg, transparent 0%, rgba(0,217,255,0.5) 50%, transparent 100%)',
        
        // Patterns
        'security-grid': "url('data:image/svg+xml,%3csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3e%3cdefs%3e%3cpattern id='grid' width='40' height='40' patternUnits='userSpaceOnUse'%3e%3cpath d='M 40 0 L 0 0 0 40' fill='none' stroke='%23374466' stroke-width='1' opacity='0.1'/%3e%3c/pattern%3e%3c/defs%3e%3crect width='100%25' height='100%25' fill='url(%23grid)'/%3e%3c/svg%3e')",
        'hex-pattern': "url('data:image/svg+xml,%3csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3e%3cdefs%3e%3cpattern id='hex' width='30' height='30' patternUnits='userSpaceOnUse'%3e%3cpolygon points='15,2 26,10 26,22 15,30 4,22 4,10' fill='none' stroke='%2300d9ff' stroke-width='0.5' opacity='0.1'/%3e%3c/pattern%3e%3c/defs%3e%3crect width='100%25' height='100%25' fill='url(%23hex)'/%3e%3c/svg%3e')",
        'circuit-pattern': "url('data:image/svg+xml,%3csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3e%3cdefs%3e%3cpattern id='circuit' width='80' height='80' patternUnits='userSpaceOnUse'%3e%3cpath d='M0 40h20v-20h20v20h20v-20h20v20' fill='none' stroke='%23374466' stroke-width='1' opacity='0.1'/%3e%3ccircle cx='20' cy='20' r='2' fill='%2300d9ff' opacity='0.2'/%3e%3ccircle cx='60' cy='20' r='2' fill='%2300d9ff' opacity='0.2'/%3e%3c/pattern%3e%3c/defs%3e%3crect width='100%25' height='100%25' fill='url(%23circuit)'/%3e%3c/svg%3e')",
      },
      boxShadow: {
        // Security Theme Shadows
        'security': '0 4px 20px rgba(0, 217, 255, 0.15)',
        'security-lg': '0 8px 40px rgba(0, 217, 255, 0.25)',
        'security-xl': '0 12px 60px rgba(0, 217, 255, 0.35)',
        
        // ISRO Themed
        'isro': '0 4px 20px rgba(14, 165, 233, 0.25)',
        'isro-glow': '0 0 30px rgba(255, 107, 53, 0.4)',
        
        // Wazuh Security
        'wazuh': '0 4px 16px rgba(26, 54, 93, 0.3)',
        'wazuh-panel': '0 2px 8px rgba(45, 55, 72, 0.2)',
        
        // ELK Stack
        'elk': '0 4px 20px rgba(0, 85, 113, 0.2)',
        'elk-accent': '0 0 20px rgba(0, 191, 179, 0.3)',
        
        // Threat Level Glows
        'threat-critical': '0 0 25px rgba(220, 38, 38, 0.5)',
        'threat-high': '0 0 20px rgba(234, 88, 12, 0.4)',
        'threat-medium': '0 0 15px rgba(217, 119, 6, 0.3)',
        'threat-low': '0 0 10px rgba(101, 163, 13, 0.3)',
        
        // Glass and Panels
        'glass': '0 8px 32px rgba(0, 0, 0, 0.1), 0 4px 16px rgba(255, 255, 255, 0.05)',
        'glass-heavy': '0 16px 64px rgba(0, 0, 0, 0.2), 0 8px 32px rgba(255, 255, 255, 0.1)',
        'panel': '0 2px 8px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
        'panel-hover': '0 4px 16px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
        
        // Interactive Elements
        'button': '0 2px 8px rgba(0, 217, 255, 0.2)',
        'button-hover': '0 4px 16px rgba(0, 217, 255, 0.3)',
        'input': 'inset 0 2px 4px rgba(0, 0, 0, 0.2)',
        'input-focus': '0 0 0 3px rgba(0, 217, 255, 0.1), inset 0 2px 4px rgba(0, 0, 0, 0.2)',
      },
      animation: {
        // Base Animations
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',
        
        // Security Themed
        'security-glow': 'securityGlow 2s ease-in-out infinite alternate',
        'security-pulse': 'securityPulse 2s ease-in-out infinite',
        'scan-line': 'scanLine 3s linear infinite',
        'radar-sweep': 'radarSweep 4s linear infinite',
        
        // Interactive Animations
        'slide-in': 'slideIn 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'slide-out': 'slideOut 0.2s cubic-bezier(0.55, 0.06, 0.68, 0.19)',
        'fade-in': 'fadeIn 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'fade-out': 'fadeOut 0.2s cubic-bezier(0.55, 0.06, 0.68, 0.19)',
        'scale-in': 'scaleIn 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'scale-out': 'scaleOut 0.15s cubic-bezier(0.55, 0.06, 0.68, 0.19)',
        
        // Status Animations
        'status-blink': 'statusBlink 1s ease-in-out infinite',
        'alert-flash': 'alertFlash 0.5s ease-in-out infinite alternate',
        'success-bounce': 'successBounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        
        // Data Flow
        'data-flow': 'dataFlow 2s linear infinite',
        'typing': 'typing 1s steps(3) infinite',
      },
      keyframes: {
        // Security Theme Animations
        securityGlow: {
          '0%': { boxShadow: '0 0 10px rgba(0, 217, 255, 0.3)', filter: 'brightness(1)' },
          '100%': { boxShadow: '0 0 25px rgba(0, 217, 255, 0.6), 0 0 40px rgba(0, 217, 255, 0.3)', filter: 'brightness(1.2)' },
        },
        securityPulse: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.05)' },
        },
        scanLine: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '20%': { opacity: '1' },
          '80%': { opacity: '1' },
          '100%': { transform: 'translateX(100%)', opacity: '0' },
        },
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        
        // Movement Animations
        float: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '25%': { transform: 'translateY(-5px) rotate(1deg)' },
          '50%': { transform: 'translateY(-10px) rotate(0deg)' },
          '75%': { transform: 'translateY(-5px) rotate(-1deg)' },
        },
        
        // Entrance Animations
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideOut: {
          '0%': { transform: 'translateX(0)', opacity: '1' },
          '100%': { transform: 'translateX(100%)', opacity: '0' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px) scale(0.95)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        fadeOut: {
          '0%': { opacity: '1', transform: 'translateY(0) scale(1)' },
          '100%': { opacity: '0', transform: 'translateY(-20px) scale(0.95)' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scaleOut: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '100%': { transform: 'scale(0)', opacity: '0' },
        },
        
        // Status Animations
        statusBlink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.3' },
        },
        alertFlash: {
          '0%': { backgroundColor: 'rgba(220, 38, 38, 0.2)' },
          '100%': { backgroundColor: 'rgba(220, 38, 38, 0.6)' },
        },
        successBounce: {
          '0%': { transform: 'scale(0)' },
          '50%': { transform: 'scale(1.2)' },
          '100%': { transform: 'scale(1)' },
        },
        
        // Data Animations
        dataFlow: {
          '0%': { transform: 'translateX(-100%) scaleX(0)' },
          '20%': { transform: 'translateX(-100%) scaleX(1)' },
          '80%': { transform: 'translateX(100%) scaleX(1)' },
          '100%': { transform: 'translateX(100%) scaleX(0)' },
        },
        typing: {
          '0%': { content: '' },
          '33%': { content: '.' },
          '66%': { content: '..' },
          '100%': { content: '...' },
        },
      },
    },
  },
  plugins: [],
}
