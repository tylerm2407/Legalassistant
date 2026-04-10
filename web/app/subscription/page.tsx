"use client";

import React, { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { CheckCircle } from "@phosphor-icons/react";

/**
 * Stripe price ID for the Pro plan ($30/month).
 * Set via environment variable in production; falls back to empty string.
 */
const PRO_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_PRO_PRICE_ID || "";

function SubscriptionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const userId = searchParams.get("userId");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFreePlan() {
    router.push(userId ? `/chat?userId=${userId}` : "/chat");
  }

  async function handleProPlan() {
    setLoading(true);
    setError("");

    try {
      const origin = window.location.origin;
      const result = await api.createCheckoutSession({
        priceId: PRO_PRICE_ID,
        successUrl: `${origin}/chat?subscription=success`,
        cancelUrl: `${origin}/subscription${userId ? `?userId=${userId}` : ""}`,
      });

      if (result.url) {
        window.location.href = result.url;
      } else {
        setError("We couldn't start checkout. Let's try again.");
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "We couldn't start checkout. Let's try again."
      );
    } finally {
      setLoading(false);
    }
  }

  const freeFeatures = [
    "Plain-language legal guidance",
    "State-specific citations",
    "Document generation",
    "Memory of your situation",
  ];

  const proFeatures = [
    "Everything in Free",
    "Priority responses",
    "More letter and form templates",
    "Attorney referrals",
    "Unlimited conversations",
  ];

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-12 max-w-[40ch] mx-auto">
          <h1 className="font-serif text-5xl md:text-6xl font-medium tracking-tight leading-tight text-ink-primary">
            Pick a plan
          </h1>
          <p className="font-sans text-base text-ink-secondary mt-4">
            The average lawyer charges $349 an hour. CaseMate is a few dollars
            a month. Start free and upgrade whenever it's useful.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Free Plan */}
          <div className="bg-white border border-border rounded-lg p-8 flex flex-col">
            <h2 className="font-serif text-3xl font-medium tracking-tight text-ink-primary">
              Free
            </h2>
            <div className="mt-4 mb-8">
              <span className="font-serif text-5xl font-medium tracking-tight text-ink-primary">
                $0
              </span>
              <span className="font-sans text-base text-ink-secondary ml-1">
                /month
              </span>
            </div>
            <ul className="space-y-4 mb-10 flex-1">
              {freeFeatures.map((feature: string) => (
                <li
                  key={feature}
                  className="flex items-start gap-3 font-sans text-base text-ink-primary"
                >
                  <CheckCircle
                    className="w-5 h-5 text-ink-secondary shrink-0 mt-0.5"
                    weight="regular"
                  />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            <button
              onClick={handleFreePlan}
              className="w-full bg-transparent text-ink-primary border border-border-strong rounded-md px-6 py-3 font-sans font-medium hover:bg-bg-hover transition-colors"
            >
              Continue on Free
            </button>
          </div>

          {/* Pro Plan */}
          <div className="relative bg-white border border-accent/30 rounded-lg p-8 flex flex-col">
            <span className="absolute top-6 right-6 bg-accent-subtle border border-accent/20 text-accent font-sans text-xs font-medium px-3 py-1 rounded-md">
              Recommended
            </span>
            <h2 className="font-serif text-3xl font-medium tracking-tight text-ink-primary">
              Pro
            </h2>
            <div className="mt-4 mb-8">
              <span className="font-serif text-5xl font-medium tracking-tight text-accent">
                $30
              </span>
              <span className="font-sans text-base text-ink-secondary ml-1">
                /month
              </span>
            </div>
            <ul className="space-y-4 mb-10 flex-1">
              {proFeatures.map((feature: string) => (
                <li
                  key={feature}
                  className="flex items-start gap-3 font-sans text-base text-ink-primary"
                >
                  <CheckCircle
                    className="w-5 h-5 text-accent shrink-0 mt-0.5"
                    weight="regular"
                  />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            {error && (
              <p className="font-sans text-sm text-warning mb-3">{error}</p>
            )}
            <button
              onClick={handleProPlan}
              disabled={loading}
              className="w-full bg-accent text-white px-6 py-3 rounded-md font-sans font-medium hover:bg-accent-hover transition-colors disabled:opacity-50"
            >
              {loading ? "Starting checkout…" : "Subscribe to Pro"}
            </button>
          </div>
        </div>

        <p className="text-center font-sans text-sm text-ink-tertiary mt-8">
          Cancel anytime. No hidden fees.
        </p>
      </div>
    </div>
  );
}

export default function SubscriptionPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-bg flex items-center justify-center">
          <p className="font-sans text-ink-secondary">Loading…</p>
        </div>
      }
    >
      <SubscriptionContent />
    </Suspense>
  );
}
