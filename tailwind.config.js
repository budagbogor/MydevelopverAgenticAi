/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Outfit', 'sans-serif'],
      },
      colors: {
        'brand-dark': '#0a0a0a',
        'brand-light': '#f5f5f5',
        'brand-accent': '#4f46e5',
        'glass-stroke': 'rgba(255, 255, 255, 0.1)',
      },
      backgroundColor: {
        'glass': 'rgba(17, 25, 40, 0.75)',
      },
      backdropBlur: {
        'xl': '24px',
      }
    },
  },
  plugins: [],
}