/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {
      scan: {
        '0%': { transform: 'translateY(-100vh)' },
        '100%': { transform: 'translateY(100vh)' },
      }
    },
    animation: {
      scan: 'scan 10s linear infinite',
    }
    },
  },
  plugins: [require("tailwindcss-animate")],
}