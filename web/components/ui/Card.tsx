"use client";

import React from "react";

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

function Card({ className = "", children }: CardProps) {
  return (
    <div
      className={`bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden ${className}`}
    >
      {children}
    </div>
  );
}

function CardHeader({ className = "", children }: CardProps) {
  return (
    <div className={`px-6 py-4 border-b border-gray-100 ${className}`}>
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
      className={`px-6 py-4 border-t border-gray-100 bg-gray-50 ${className}`}
    >
      {children}
    </div>
  );
}

Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

export default Card;
