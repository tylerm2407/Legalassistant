"use client";

import React from "react";

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

function Card({ className = "", children }: CardProps) {
  return (
    <div
      className={`bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 overflow-hidden ${className}`}
    >
      {children}
    </div>
  );
}

function CardHeader({ className = "", children }: CardProps) {
  return (
    <div className={`px-6 py-4 border-b border-white/[0.06] ${className}`}>
      {children}
    </div>
  );
}

function CardBody({ className = "", children }: CardProps) {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>;
}

function CardFooter({ className = "", children }: CardProps) {
  return (
    <div
      className={`px-6 py-4 border-t border-white/[0.06] bg-white/[0.02] ${className}`}
    >
      {children}
    </div>
  );
}

Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

export default Card;
