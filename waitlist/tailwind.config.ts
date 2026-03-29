import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        "glow-sm": "0 0 15px rgba(59, 130, 246, 0.15)",
        "glow-md": "0 0 30px rgba(59, 130, 246, 0.2)",
        "glow-lg": "0 0 50px rgba(59, 130, 246, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
