"use client";

import { useState, FormEvent } from "react";
import { CheckCircle } from "@phosphor-icons/react";

/** Possible states of the waitlist form submission lifecycle. */
type FormState = "idle" | "submitting" | "success" | "error";

/**
 * Email waitlist signup form for the CaseMate landing page.
 *
 * Collects email addresses and submits them to the /api/waitlist endpoint,
 * which syncs to Mailchimp and stores in Supabase as backup. Shows a success
 * confirmation after signup or error messages on failure.
 */
export default function WaitlistForm() {
  const [email, setEmail] = useState("");
  const [state, setState] = useState<FormState>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;

    setState("submitting");
    setErrorMessage("");

    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), source: "landing_page" }),
      });

      const data = await res.json();

      if (!res.ok) {
        setState("error");
        setErrorMessage(data.error || "Something went wrong. Please try again.");
        return;
      }

      setState("success");
    } catch {
      setState("error");
      setErrorMessage("Something went wrong. Please try again.");
    }
  }

  if (state === "success") {
    return (
      <div className="flex items-center justify-center gap-2 py-3 px-6 bg-accent-subtle border border-accent/30 rounded-md max-w-md mx-auto">
        <CheckCircle className="w-5 h-5 text-accent" weight="regular" />
        <span className="text-accent font-sans font-medium text-sm">
          You&apos;re on the list. We&apos;ll email you when CaseMate is ready.
        </span>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto">
      <div className="flex flex-col sm:flex-row items-stretch gap-3">
        <label htmlFor="waitlist-email" className="sr-only">
          Email address
        </label>
        <input
          id="waitlist-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
          className="flex-1 bg-white border border-border rounded-md px-4 py-3 font-sans text-sm text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-ink-tertiary transition-colors"
        />
        <button
          type="submit"
          disabled={state === "submitting"}
          className="bg-accent text-white px-6 py-3 rounded-md font-sans font-medium text-sm hover:bg-accent-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {state === "submitting" ? "Joining..." : "Join the waitlist"}
        </button>
      </div>
      {state === "error" && (
        <p className="mt-3 text-sm font-sans text-warning bg-warning-subtle border border-warning/30 rounded-md px-3 py-2">
          {errorMessage}
        </p>
      )}
    </form>
  );
}
