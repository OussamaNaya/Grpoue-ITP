/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "on-primary-container": "#eeefff",
        "surface-container-lowest": "#ffffff",
        "surface-dim": "#d8dadc",
        "on-error-container": "#93000a",
        "primary-container": "#dfe0ff",
        "outline-variant": "#c4c6d0",
        "surface-container-high": "#e7e8ea",
        "on-surface-variant": "#44474e",
        "inverse-surface": "#2e3032",
        "error": "#ba1a1a",
        "error-container": "#ffdad6",
        "surface": "#f9f9fb",
        "on-surface": "#191c1e",
        "surface-container": "#ecedef",
        "surface-container-low": "#f3f3f6",
        "primary": "#0055d4",
        "on-primary": "#ffffff",
        "outline": "#74777f"
      }
    },
  },
  plugins: [],
}
