/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx,jsx,js}'],
  theme: {
    extend: {
      colors: {
        // Light mode - Monetary/Financial palette
        background: 'hsl(0 0% 99%)',
        foreground: 'hsl(200 20% 8%)',
        muted: 'hsl(200 15% 95%)',
        'muted-foreground': 'hsl(200 15% 40%)',
        card: 'hsl(0 0% 100%)',
        border: 'hsl(200 20% 90%)',
        
        // Primary (Deep Blue - Banking/Trust)
        primary: 'hsl(200 80% 35%)',
        'primary-foreground': 'hsl(0 0% 100%)',
        'primary-light': 'hsl(200 85% 92%)',
        
        // Success (Prosperity Green)
        success: 'hsl(120 65% 45%)',
        'success-light': 'hsl(120 65% 92%)',
        
        // Warning (Gold - Wealth)
        warning: 'hsl(45 95% 52%)',
        'warning-light': 'hsl(45 95% 92%)',
        
        // Destructive (Alert Red)
        destructive: 'hsl(0 80% 55%)',
        'destructive-light': 'hsl(0 80% 92%)',
        
        // Accent (Teal - Growth)
        accent: 'hsl(180 70% 45%)',
        'accent-light': 'hsl(180 70% 92%)',
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        'card': '0 4px 12px rgba(0, 0, 0, 0.08)',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, hsl(200 80% 35%) 0%, hsl(200 70% 45%) 100%)',
        'gradient-soft': 'linear-gradient(135deg, hsl(200 85% 92%) 0%, hsl(180 70% 92%) 100%)',
        'gradient-gold': 'linear-gradient(135deg, hsl(45 95% 52%) 0%, hsl(40 90% 45%) 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};


