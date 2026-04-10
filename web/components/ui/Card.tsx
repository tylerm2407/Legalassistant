"use client";

import React from "react";

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

/**
 * Editorial card: white on warm off-white, hairline border, generous padding,
 * no drop shadow. Structure reads like a printed page, not a SaaS panel.
 */
function Card({ className = "", children }: CardProps) {
  return (
    <div
      className={`bg-white border border-border rounded-lg overflow-hidden ${className}`}
    >
      {children}
    </div>
  );
}

function CardHeader({ className = "", children }: CardProps) {
  return (
    <div className={`px-8 py-6 border-b border-border ${className}`}>
      {children}
    </div>
  );
}

function CardBody({ className = "", children }: CardProps) {
  return <div className={`px-8 py-6 ${className}`}>{children}</div>;
}

function CardFooter({ className = "", children }: CardProps) {
  return (
    <div
      className={`px-8 py-6 border-t border-border bg-bg ${className}`}
    >
      {children}
    </div>
  );
}

Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

export default Card;
