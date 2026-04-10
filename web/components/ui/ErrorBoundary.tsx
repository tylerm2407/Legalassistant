"use client";

import React, { Component, type ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Editorial error boundary. Calm terracotta tone, never a loud red alert.
 * Communicates "something went wrong and here is the next step" rather
 * than shouting at a user who is probably already stressed.
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    this.props.onError?.(error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center rounded-lg border border-warning/30 bg-warning-subtle p-10">
          <p className="font-serif text-2xl font-medium text-ink-primary">
            Something went wrong
          </p>
          <p className="mt-3 text-base text-ink-secondary max-w-[50ch] text-center">
            {this.state.error?.message || "An unexpected error occurred. You can try again below."}
          </p>
          <button
            onClick={this.handleReset}
            className="mt-6 rounded-md bg-accent px-6 py-3 text-base font-sans font-medium text-white transition-colors hover:bg-accent-hover"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
