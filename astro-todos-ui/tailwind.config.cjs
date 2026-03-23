/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        'win95-gray': '#C0C0C0',
        'win95-dark-gray': '#808080',
        'win95-light-gray': '#DFDFDF',
        'win95-blue': '#000080',
        'win95-dark-blue': '#0000A0',
        'win95-green': '#008080',
        'win95-red': '#800000',
        'win95-black': '#000000',
        'win95-white': '#FFFFFF',
      },
      fontFamily: {
        'win95': ['"MS Sans Serif"', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'win95-inset': 'inset -1px -1px #fff, inset 1px 1px #0a0a0a, inset -2px -2px #dfdfdf, inset 2px 2px #808080',
        'win95-outset': 'inset -1px -1px #0a0a0a, inset 1px 1px #fff, inset -2px -2px #808080, inset 2px 2px #dfdfdf',
        'win95-btn-active': 'inset -1px -1px #fff, inset 1px 1px #0a0a0a, inset -2px -2px #dfdfdf, inset 2px 2px #808080',
      },
    },
  },
  plugins: [],
}