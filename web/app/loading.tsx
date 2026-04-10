/**
 * Global loading state. Quiet text-only indicator — no spinner, no glow.
 */
export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg">
      <p className="font-sans text-base text-ink-secondary">Loading…</p>
    </div>
  );
}
