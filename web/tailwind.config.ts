import type { Config } from "tailwindcss";

/**
 * CaseMate design system — "trustworthy editorial".
 *
 * Calibrated for users in stressful legal situations. Every color is warm,
 * quiet, and considered. The palette is deliberately narrow: one accent
 * (deep forest green), one warning (muted terracotta), warm off-white bg,
 * near-black ink. No gradients, no glows, no pure white, no pure black.
 */
const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#FBF9F4",
          hover: "#F5F2EB",
        },
        ink: {
          primary: "#1A1A1A",
          secondary: "#5A5A5A",
          tertiary: "#8A8A8A",
        },
        accent: {
          DEFAULT: "#1F4D3A",
          hover: "#173A2C",
          subtle: "#E8EFEB",
        },
        warning: {
          DEFAULT: "#B5654A",
          subtle: "#F5E8E2",
        },
        border: {
          DEFAULT: "#E5E1D8",
          strong: "#C9C3B5",
        },
      },
      fontFamily: {
        serif: ["var(--font-source-serif)", "Georgia", "serif"],
        sans: ["var(--font-source-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
