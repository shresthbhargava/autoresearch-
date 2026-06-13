import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        grotesk: ["var(--font-grotesk)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
        inter: ["var(--font-inter)", "sans-serif"],
        display: ["var(--font-grotesk)", "sans-serif"],
        // Keep legacy aliases pointing to new vars
        sans: ["var(--font-grotesk)", "sans-serif"],
        serif: ["var(--font-grotesk)", "sans-serif"],
      },
      fontSize: {
        xs: ["12px", { lineHeight: "1.5" }],
        sm: ["14px", { lineHeight: "1.6" }],
        base: ["16px", { lineHeight: "1.7" }],
        lg: ["18px", { lineHeight: "1.7" }],
        xl: ["20px", { lineHeight: "1.6" }],
        "2xl": ["24px", { lineHeight: "1.4" }],
        "3xl": ["30px", { lineHeight: "1.3" }],
        "4xl": ["36px", { lineHeight: "1.2" }],
        "5xl": ["48px", { lineHeight: "1.1" }],
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        card: "var(--card)",
        accent: "var(--accent)",
        accentDark: "var(--accent-dark)",
        accentShadow: "var(--accent-shadow)",
        darkBorder: "var(--border)",
      },
    },
  },
  plugins: [],
};
export default config;
