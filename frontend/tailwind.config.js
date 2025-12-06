/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './public/index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#7c3aed',
          secondary: '#06b6d4'
        }
      },
      boxShadow: {
        glow: '0 10px 30px rgba(124,58,237,0.35)'
      },
      keyframes: {
        floaty: {
          '0%': { transform: 'translate3d(-2%, -1%, 0) rotate(-1deg)' },
          '100%': { transform: 'translate3d(2%, 1%, 0) rotate(1deg)' }
        },
        shine: {
          '0%': { '--x': '0%' },
          '50%': { '--x': '100%' },
          '100%': { '--x': '0%' }
        }
      },
      animation: {
        floaty: 'floaty 18s ease-in-out infinite alternate',
        shine: 'shine 1.8s ease-in-out infinite'
      }
    }
  },
  plugins: []
}
