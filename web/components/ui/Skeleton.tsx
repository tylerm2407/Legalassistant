import React from "react";

/**
 * Editorial skeletons. Warm gray placeholders on warm off-white,
 * no shimmer, no glow.
 */
function SkeletonLine({ width = "100%", height = "16px" }: { width?: string; height?: string }) {
  return (
    <div
      className="animate-pulse rounded bg-border"
      style={{ width, height }}
    />
  );
}

function SkeletonBlock({ lines = 3, className = "" }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_: unknown, i: number) => (
        <SkeletonLine key={i} width={i === lines - 1 ? "70%" : "100%"} />
      ))}
    </div>
  );
}

function SkeletonCard({ className = "" }: { className?: string }) {
  return (
    <div className={`rounded-lg border border-border bg-white p-8 ${className}`}>
      <SkeletonLine width="40%" height="20px" />
      <div className="mt-4 space-y-2">
        <SkeletonLine />
        <SkeletonLine />
        <SkeletonLine width="60%" />
      </div>
    </div>
  );
}

function SkeletonChat() {
  return (
    <div className="space-y-4 p-4">
      <div className="flex justify-start">
        <div className="max-w-[80%] rounded-lg border border-border bg-white p-6">
          <SkeletonBlock lines={3} />
        </div>
      </div>
      <div className="flex justify-end">
        <div className="max-w-[60%] rounded-lg bg-accent-subtle p-6">
          <SkeletonBlock lines={2} />
        </div>
      </div>
      <div className="flex justify-start">
        <div className="max-w-[80%] rounded-lg border border-border bg-white p-6">
          <SkeletonBlock lines={4} />
        </div>
      </div>
    </div>
  );
}

function SkeletonList({ items = 4, className = "" }: { items?: number; className?: string }) {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: items }).map((_: unknown, i: number) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

function SkeletonProfile() {
  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center gap-4">
        <div className="h-16 w-16 animate-pulse rounded-full bg-border" />
        <div className="flex-1 space-y-2">
          <SkeletonLine width="50%" height="20px" />
          <SkeletonLine width="30%" />
        </div>
      </div>
      <SkeletonBlock lines={4} />
    </div>
  );
}

export { SkeletonLine, SkeletonBlock, SkeletonCard, SkeletonChat, SkeletonList, SkeletonProfile };
export default SkeletonCard;
