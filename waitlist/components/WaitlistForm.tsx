"use client";

import { useState, FormEvent } from "react";

type FormState = "idle" | "submitting" | "success" | "error";

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
        setErrorMessage(data.error || "Something went wrong.");
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
      <div className="flex items-center justify-center gap-2 py-3 px-6 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
        <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="text-emerald-400 font-medium text-sm">
          You&apos;re on the list! Check your email to confirm your account.
        </span>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-center gap-3 max-w-md mx-auto">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
        className="flex-1 w-full px-4 py-3 bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/25 transition-all"
      />
      <button
        type="submit"
        disabled={state === "submitting"}
        className="w-full sm:w-auto px-6 py-3 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-400 shadow-glow-md hover:shadow-glow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
      >
        {state === "submitting" ? "Joining..." : "Join Waitlist"}
      </button>
      {state === "error" && (
        <p className="text-red-400 text-xs mt-1 sm:mt-0">{errorMessage}</p>
      )}
    </form>
  );
}
