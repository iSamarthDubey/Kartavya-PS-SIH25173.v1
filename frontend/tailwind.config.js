/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // SYNRGY Design Tokens (SYNRGY.TXT lines 474-495)
        synrgy: {
          bg: {
            900: '#0A0F1E'
          },
          primary: '#00EFFF',    // Electric cyan
          accent: '#FF7A00',     // Solar orange
          muted: '#94A3B8',
          surface: '#0F1724',
          text: '#E6EEF8'
        }
      },
      fontFamily: {
        heading: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif']
      }
    },
  },
  plugins: [],
}
