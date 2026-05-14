import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          base: "#0a0a0b",
          panel: "#13131a",
          card: "#1a1a23",
          border: "#2a2a35",
        },
        ink: {
          base: "#e6e6ed",
          muted: "#8b8b9a",
          dim: "#5a5a6a",
        },
        accent: {
          green: "#10b981",
          red: "#ef4444",
          amber: "#f59e0b",
          blue: "#3b82f6",
          violet: "#8b5cf6",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
