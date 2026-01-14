/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx,jsx,js}'],
  theme: {
    extend: {
      colors: {
        // Minimal black and white palette
        background: 'hsl(0 0% 99%)',
        foreground: 'hsl(0 0% 0%)',
        muted: 'hsl(0 0% 96%)',
        'muted-foreground': 'hsl(0 0% 40%)',
        card: 'hsl(0 0% 100%)',
        border: 'hsl(0 0% 30%)',  // Dark borders for white boxes
        
        // Minimalist colors (mostly grayscale with subtle accents)
        primary: 'hsl(0 0% 20%)',
        'primary-foreground': 'hsl(0 0% 100%)',
        'primary-light': 'hsl(0 0% 92%)',
        
        success: 'hsl(0 0% 30%)',   // Dark gray instead of green
        'success-light': 'hsl(0 0% 94%)',
        
        warning: 'hsl(0 0% 40%)',   // Medium gray instead of gold
        'warning-light': 'hsl(0 0% 95%)',
        
        destructive: 'hsl(0 0% 50%)',  // Gray instead of red
        'destructive-light': 'hsl(0 0% 96%)',
        
        accent: 'hsl(0 0% 25%)',    // Dark gray instead of teal
        'accent-light': 'hsl(0 0% 93%)',
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
        'gradient-primary': 'linear-gradient(135deg, hsl(0 0% 20%) 0%, hsl(0 0% 30%) 100%)',
        'gradient-soft': 'linear-gradient(135deg, hsl(0 0% 94%) 0%, hsl(0 0% 92%) 100%)',
        'gradient-gold': 'linear-gradient(135deg, hsl(0 0% 40%) 0%, hsl(0 0% 35%) 100%)',
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


