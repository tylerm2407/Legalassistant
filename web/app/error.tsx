'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="text-center max-w-md">
        <h1 className="text-4xl font-bold text-white mb-4">Something went wrong</h1>
        <p className="text-gray-400 mb-8">
          {error.message || 'An unexpected error occurred.'}
        </p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
