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
        canvas: "#050505",
        card: "#121212",
        "card-alt": "#141414",
        inset: "#0e0e0e",
        border: "#2a2a2a",
        "text-primary": "#f2f2f2",
        "text-muted": "#a3a3a3",
        accent: "#3dd68c",
        "accent-hover": "#32b876",
        warning: "#fbbf24",
        "warning-bg": "#241a0d",
        "warning-border": "#684514",
        error: "#f87171",
        "error-bg": "#241010",
        "error-border": "#632020",
      },
      fontFamily: {
        serif: ["var(--font-fraunces)", "Georgia", "serif"],
        sans: ["var(--font-manrope)", "Segoe UI", "sans-serif"],
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
