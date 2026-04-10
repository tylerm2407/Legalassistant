"use client";

import React from "react";

type BadgeVariant = "default" | "success" | "warning";
type BadgeSize = "sm" | "md";

interface BadgeProps {
  variant?: BadgeVariant;
  size?: BadgeSize;
  className?: string;
  children: React.ReactNode;
}

/**
 * Editorial badges. No pill shapes, no bright colors — everything sits in
 * the warm palette. "Warning" uses the muted terracotta, never red.
 */
const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-bg-hover text-ink-secondary border border-border",
  success: "bg-accent-subtle text-accent border border-accent/20",
  warning: "bg-warning-subtle text-warning border border-warning/30",
};

const sizeStyles: Record<BadgeSize, string> = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-1 text-sm",
};

function Badge({
  variant = "default",
  size = "sm",
  className = "",
  children,
}: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center font-sans font-medium rounded-md ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </span>
  );
}

export default Badge;
