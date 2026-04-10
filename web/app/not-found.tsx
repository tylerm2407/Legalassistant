import Link from "next/link";

/**
 * 404 page. Editorial, not ironic. Points the user back home.
 */
export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-6">
      <div className="text-center max-w-md">
        <p className="font-mono text-sm text-ink-tertiary mb-4">404</p>
        <h1 className="font-serif text-5xl font-medium text-ink-primary tracking-tight leading-tight mb-4">
          We couldn't find that page
        </h1>
        <p className="font-sans text-base text-ink-secondary mb-8 max-w-[45ch] mx-auto">
          The page you're looking for doesn't exist. Let's get you back home.
        </p>
        <Link
          href="/"
          className="inline-flex items-center px-6 py-3 bg-accent text-white font-sans font-medium rounded-md hover:bg-accent-hover transition-colors"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}
