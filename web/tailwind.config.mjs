/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "Hiragino Sans",
          "Yu Gothic",
          "Meiryo",
          "sans-serif",
        ],
      },
      colors: {
        ink: "#171a20",
        paper: "#f4f6f8",
        line: "#dde3ea",
        accent: "#d34f3f",
        moss: "#55706b",
        navy: "#111827",
      },
    },
  },
  plugins: [],
};
