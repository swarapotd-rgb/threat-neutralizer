/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    // Make sure it looks at your main component file
    "./src/**/*.{js,ts,jsx,tsx}", 
  ],
  theme: {
    extend: {
      transformStyle: {
        '3d': 'preserve-3d',
      },
      transform: {
        'rotate-y-180': 'rotateY(180deg)',
      },
      backfaceVisibility: {
        'hidden': 'hidden',
      },
      perspective: {
        'default': '2000px',
      },
    },
  },
  plugins: [],
}
