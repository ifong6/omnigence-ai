/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  // 禁用 oklch 颜色格式，使用传统的 RGB/HSL
  experimental: {
    optimizeUniversalDefaults: true,
  },
  // 强制使用 RGB 颜色
  future: {
    hoverOnlyWhenSupported: true,
  },
}

