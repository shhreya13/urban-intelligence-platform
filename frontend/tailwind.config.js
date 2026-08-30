/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Command-center dark theme: deep slate-navy base, signal colors
        // for the two departments (PWD = amber/road, TRAFFIC = cyan/flow)
        base: {
          950: "#0a0e14",
          900: "#0f1520",
          800: "#161d2c",
          700: "#212a3d",
          600: "#31405a",
        },
        signal: {
          cyan: "#3ddcd6",
          amber: "#e8a33d",
          red: "#e8543d",
          green: "#4fd67a",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "'Roboto Mono'", "monospace"],
      },
    },
  },
  plugins: [],
}
