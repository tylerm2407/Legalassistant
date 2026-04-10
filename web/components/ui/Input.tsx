"use client";

import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

/**
 * Text input styled for the editorial design system.
 *
 * Labels sit above the input in small uppercase-ish sans font.
 * The input itself is white on warm off-white with a hairline border.
 * Focus state uses the accent green — no glow, no ring bleed.
 */
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = "", id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-sans font-medium text-ink-primary mb-2"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`w-full px-4 py-3 bg-white text-ink-primary border rounded-md text-base font-sans transition-colors focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-ink-tertiary ${
            error ? "border-warning" : "border-border"
          } ${className}`}
          {...props}
        />
        {error && <p className="mt-2 text-sm font-sans text-warning">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
