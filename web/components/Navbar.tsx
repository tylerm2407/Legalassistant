"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChatCircle,
  User,
  Clock,
  BookOpen,
  Briefcase,
  ListChecks,
  List,
  X,
  SignOut,
} from "@phosphor-icons/react";
import { useAuth } from "@/lib/auth";

/** Top navigation links for authenticated users. */
const NAV_LINKS = [
  { label: "Chat", href: "/chat", icon: "chat" },
  { label: "Profile", href: "/profile", icon: "profile" },
  { label: "Deadlines", href: "/deadlines", icon: "deadlines" },
  { label: "Rights", href: "/rights", icon: "rights" },
  { label: "Attorneys", href: "/attorneys", icon: "attorneys" },
  { label: "Workflows", href: "/workflows", icon: "workflows" },
] as const;

/** Phosphor regular-weight icon for each nav link. */
function NavIcon({ icon, className }: { icon: string; className?: string }) {
  const cls = className || "w-[18px] h-[18px]";
  switch (icon) {
    case "chat":
      return <ChatCircle className={cls} weight="regular" />;
    case "profile":
      return <User className={cls} weight="regular" />;
    case "deadlines":
      return <Clock className={cls} weight="regular" />;
    case "rights":
      return <BookOpen className={cls} weight="regular" />;
    case "attorneys":
      return <Briefcase className={cls} weight="regular" />;
    case "workflows":
      return <ListChecks className={cls} weight="regular" />;
    default:
      return null;
  }
}

/** Pages where the navbar should not be displayed. */
const HIDDEN_ROUTES = ["/", "/auth", "/onboarding"];

/**
 * Top navigation bar. Warm off-white background, hairline bottom border,
 * serif wordmark, regular-weight Phosphor icons. No glass, no blur, no glow.
 */
export default function Navbar() {
  const pathname = usePathname();
  const { user, signOut } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (HIDDEN_ROUTES.includes(pathname) || !user) {
    return null;
  }

  return (
    <nav className="sticky top-0 z-50 bg-bg border-b border-border">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Wordmark */}
          <Link href="/chat" className="flex items-center gap-2 shrink-0">
            <span className="font-serif text-xl font-medium text-accent tracking-tight">
              CaseMate
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-sans transition-colors ${
                    active
                      ? "bg-accent-subtle text-accent font-medium"
                      : "text-ink-secondary hover:text-ink-primary hover:bg-bg-hover"
                  }`}
                >
                  <NavIcon icon={link.icon} />
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Right side */}
          <div className="flex items-center gap-2">
            <button
              onClick={signOut}
              className="hidden md:inline-flex items-center gap-1.5 px-3 py-2 text-sm font-sans text-ink-secondary hover:text-ink-primary rounded-md hover:bg-bg-hover transition-colors"
            >
              <SignOut className="w-4 h-4" weight="regular" />
              Sign out
            </button>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 text-ink-secondary hover:text-ink-primary transition-colors"
              aria-label="Toggle navigation menu"
            >
              {mobileOpen ? (
                <X className="w-5 h-5" weight="regular" />
              ) : (
                <List className="w-5 h-5" weight="regular" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-bg">
          <div className="px-4 py-3 space-y-1">
            {NAV_LINKS.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3 px-3 py-3 rounded-md text-base font-sans transition-colors ${
                    active
                      ? "bg-accent-subtle text-accent font-medium"
                      : "text-ink-secondary hover:text-ink-primary hover:bg-bg-hover"
                  }`}
                >
                  <NavIcon icon={link.icon} />
                  {link.label}
                </Link>
              );
            })}
            <button
              onClick={() => {
                setMobileOpen(false);
                signOut();
              }}
              className="w-full flex items-center gap-3 px-3 py-3 rounded-md text-base font-sans text-ink-secondary hover:text-ink-primary hover:bg-bg-hover transition-colors"
            >
              <SignOut className="w-5 h-5" weight="regular" />
              Sign out
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
