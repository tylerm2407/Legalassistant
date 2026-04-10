"use client";

/**
 * Global error boundary page. Warm, calm, reassuring — never alarming.
 */
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-6">
      <div className="text-center max-w-md">
        <h1 className="font-serif text-4xl font-medium text-ink-primary tracking-tight mb-4">
          Something went wrong
        </h1>
        <p className="font-sans text-base text-ink-secondary mb-8 max-w-[50ch] mx-auto leading-relaxed">
          {error.message || "Something on our end broke. It's not you. Let's try again."}
        </p>
        <button
          onClick={reset}
          className="inline-flex items-center px-6 py-3 bg-accent text-white font-sans font-medium rounded-md hover:bg-accent-hover transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
