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
        // Primary: Deep Rust (#8B3103)
        brand: {
          50: "#FDF6F0",
          100: "#FAECE2",
          200: "#F4D6C3",
          300: "#E9B498",
          400: "#D7855C",
          500: "#BD4809",
          600: "#8B3103", // Primary Deep Rust
          700: "#742802",
          800: "#5D1F02",
          900: "#461701",
          950: "#2D0E00",
        },
        // Secondary: Pearl (#EAE0CB)
        pearl: {
          50: "#FAF8F5",
          100: "#F5EFE6",
          200: "#EAE0CB", // Primary Pearl
          300: "#DDD0B5",
          400: "#CDBE9E",
          500: "#B8A783",
          600: "#9C8A66",
          700: "#7A6B4D",
          800: "#5C503A",
          900: "#3F3728",
          950: "#252017",
        },
        rust: {
          DEFAULT: "#8B3103",
          50: "#FDF6F0",
          100: "#FAECE2",
          200: "#F4D6C3",
          500: "#BD4809",
          600: "#8B3103",
          700: "#742802",
          800: "#5D1F02",
        },
      },
    },
  },
  plugins: [],
};
export default config;
