/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        popover: "hsl(var(--popover))",
        "popover-foreground": "hsl(var(--popover-foreground))",
        primary: "hsl(var(--primary))",
        "primary-foreground": "hsl(var(--primary-foreground))",
        secondary: "hsl(var(--secondary))",
        "secondary-foreground": "hsl(var(--secondary-foreground))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        accent: "hsl(var(--accent))",
        "accent-foreground": "hsl(var(--accent-foreground))",
        destructive: "hsl(var(--destructive))",
        "destructive-foreground": "hsl(var(--destructive-foreground))",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        // Government color palette
        "gov-green": "hsl(var(--gov-green))",
        "gov-green-dark": "hsl(var(--gov-green-dark))",
        "gov-green-light": "hsl(var(--gov-green-light))",
        "gov-gold": "hsl(var(--gov-gold))",
        "gov-gold-dark": "hsl(var(--gov-gold-dark))",
        "gov-gold-light": "hsl(var(--gov-gold-light))",
        "gov-navy": "hsl(var(--gov-navy))",
        "gov-cream": "hsl(var(--gov-cream))",
        // Accent colors
        "accent-blue": "#3b82f6",
        "accent-emerald": "#10b981",
        "accent-purple": "#8b5cf6",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Playfair Display', 'serif'],
      },
      animation: {
        "float-gentle": "float-gentle 6s ease-in-out infinite",
        "pulse-glow": "pulse-glow 3s ease-in-out infinite",
        "drift-left": "drift-left 8s ease-in-out infinite",
        "drift-right": "drift-right 7s ease-in-out infinite",
      },
      keyframes: {
        "float-gentle": {
          "0%, 100%": { 
            transform: "translateY(0px) rotate(0deg)" 
          },
          "50%": { 
            transform: "translateY(-10px) rotate(1deg)" 
          }
        },
        "pulse-glow": {
          "0%, 100%": { 
            boxShadow: "0 0 20px rgba(255, 255, 255, 0.1)"
          },
          "50%": { 
            boxShadow: "0 0 40px rgba(255, 255, 255, 0.3)"
          }
        },
        "drift-left": {
          "0%": { transform: "translateX(0px)" },
          "50%": { transform: "translateX(-15px)" },
          "100%": { transform: "translateX(0px)" }
        },
        "drift-right": {
          "0%": { transform: "translateX(0px)" },
          "50%": { transform: "translateX(15px)" },
          "100%": { transform: "translateX(0px)" }
        }
      }
    },
  },
  plugins: [],
}