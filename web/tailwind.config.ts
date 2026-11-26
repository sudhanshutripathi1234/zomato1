import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#071425",
        card: "#FFFFFF",
        "card-alt": "#F4F7FB",
        inset: "#EEF3FA",
        border: "#D5E1F0",
        "text-primary": "#0C1B33",
        "text-muted": "#41536B",
        primary: "#1D4ED8",
        accent: "#1D4ED8",
        "accent-hover": "#1E3A8A",
        "on-accent": "#FFFFFF",
        warning: "#A16207",
        "warning-bg": "#FEF3C7",
        "warning-border": "#F6D27A",
        error: "#B91C1C",
        "error-bg": "#FEF2F2",
        "error-border": "#FECACA",
      },
      fontFamily: {
        serif: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-body)", "Segoe UI", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      borderRadius: {
        custom: "14px",
      },
      maxWidth: {
        feed: "960px",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.55" },
        },
      },
      animation: {
        fadeUp: "fadeUp 0.45s ease-out both",
        pulseSoft: "pulseSoft 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
