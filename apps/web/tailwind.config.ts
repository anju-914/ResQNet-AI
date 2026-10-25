import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0a",
        panel: "rgba(10, 10, 10, 0.85)",
        card: "rgba(255, 255, 255, 0.05)",
        border: "rgba(255, 255, 255, 0.12)",
        gold: {
          DEFAULT: "#a78b71",
          light: "#c9b8a0",
          hover: "#e8d5b7",
        },
        status: {
          high: "#ef4444",
          medium: "#f59e0b",
          low: "#60a5fa",
          resolved: "#22c55e",
          unverified: "rgba(255, 255, 255, 0.60)",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        serif: ["Playfair Display", "Georgia", "serif"],
      },
      borderRadius: {
        panel: "24px",
        card: "16px",
        input: "12px",
      },
    },
  },
  plugins: [],
};

export default config;

