/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef7f4',
          500: '#0d9488',
          600: '#0f766e',
          700: '#115e59',
        },
      },
    },
  },
  plugins: [],
}
