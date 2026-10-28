/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        beige: {
          50: '#FAF8F5',
          100: '#F5F0E8',
          150: '#EFE9DF',
          200: '#E6DFD3',
          300: '#D5CBB9',
          400: '#B6A68F',
          500: '#94836B',
          600: '#736450',
          700: '#54493A',
          800: '#383026',
          900: '#231F19',
          950: '#171410',
        },
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        risk: {
          low: '#16a34a',
          medium: '#d97706',
          high: '#dc2626',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
