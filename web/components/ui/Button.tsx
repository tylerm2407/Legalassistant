"use client";

import React from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: React.ReactNode;
}

/**
 * Button styles for the CaseMate editorial design system.
 *
 * Primary: deep forest green, one per screen, never pill-shaped, never shadowed.
 * Secondary: hairline-bordered, warm hover background.
 * Ghost: text-only, used for low-emphasis actions.
 */
const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-accent text-white hover:bg-accent-hover focus:ring-2 focus:ring-accent/30",
  secondary:
    "bg-transparent text-ink-primary border border-border-strong hover:bg-bg-hover focus:ring-2 focus:ring-accent/20",
  ghost:
    "bg-transparent text-ink-secondary hover:text-ink-primary hover:bg-bg-hover focus:ring-2 focus:ring-accent/20",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "px-4 py-2 text-sm",
  md: "px-5 py-2.5 text-base",
  lg: "px-6 py-3 text-base",
};

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { variant = "primary", size = "md", className = "", disabled, children, ...props },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={`inline-flex items-center justify-center font-sans font-medium rounded-md transition-colors focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

export default Button;
