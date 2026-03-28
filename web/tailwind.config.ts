import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          base: "#050505",
          card: "rgba(255,255,255,0.03)",
          elevated: "rgba(255,255,255,0.05)",
          secondary: "rgba(255,255,255,0.07)",
        },
        primary: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
          950: "#1e1b4b",
        },
      },
      boxShadow: {
        "glow-sm": "0 0 15px rgba(59, 130, 246, 0.15)",
        "glow-md": "0 0 30px rgba(59, 130, 246, 0.2)",
        "glow-lg": "0 0 50px rgba(59, 130, 246, 0.25)",
        "glow-purple": "0 0 30px rgba(139, 92, 246, 0.2)",
      },
      backgroundImage: {
        "gradient-radial":
          "radial-gradient(ellipse at top, var(--tw-gradient-stops))",
        "gradient-glow":
          "radial-gradient(600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(59,130,246,0.06), transparent 40%)",
      },
      animation: {
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
      },
      keyframes: {
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 15px rgba(59, 130, 246, 0.15)" },
          "50%": { boxShadow: "0 0 30px rgba(59, 130, 246, 0.3)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
