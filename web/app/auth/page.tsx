"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

/**
 * Auth page — first impression. Warm off-white background, centered card,
 * serif wordmark, plain-language copy. No logo tile, no emoji, no gradient.
 */
export default function AuthPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      if (isSignUp) {
        const { data, error: signUpError } = await supabase.auth.signUp({
          email: email.trim(),
          password,
        });
        if (signUpError) throw signUpError;
        if (data.session) {
          router.push("/onboarding");
          return;
        }
        setMessage(
          "Check your email for a confirmation link, then come back and sign in."
        );
        setIsSignUp(false);
      } else {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });
        if (signInError) throw signInError;
        router.push("/chat");
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <Link href="/" className="inline-block">
            <h1 className="font-serif text-4xl font-medium text-accent tracking-tight">
              CaseMate
            </h1>
          </Link>
          <p className="mt-4 font-sans text-base text-ink-secondary max-w-[40ch] mx-auto">
            {isSignUp
              ? "Create an account and we'll get to know your situation."
              : "Welcome back. Let's pick up where you left off."}
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white border border-border rounded-lg p-8 space-y-5"
        >
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="Password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && (
            <p className="text-sm font-sans text-warning bg-warning-subtle border border-warning/30 rounded-md p-3">
              {error}
            </p>
          )}
          {message && (
            <p className="text-sm font-sans text-accent bg-accent-subtle border border-accent/20 rounded-md p-3">
              {message}
            </p>
          )}

          <Button
            type="submit"
            disabled={loading || !email.trim() || !password}
            className="w-full"
          >
            {loading
              ? "One moment..."
              : isSignUp
              ? "Create account"
              : "Sign in"}
          </Button>

          <p className="text-center text-sm font-sans text-ink-secondary">
            {isSignUp ? "Already have an account? " : "Don't have an account yet? "}
            <button
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError("");
                setMessage("");
              }}
              className="text-accent hover:text-accent-hover font-medium underline underline-offset-2"
            >
              {isSignUp ? "Sign in" : "Create one"}
            </button>
          </p>
        </form>

        <p className="mt-8 text-center text-xs font-sans text-ink-tertiary max-w-[50ch] mx-auto leading-relaxed">
          CaseMate isn't a law firm and we aren't your lawyer. We explain your rights in plain English and help you figure out what to do next.
        </p>
      </div>
    </div>
  );
}
