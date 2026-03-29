"use client";

import React, { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Button from "@/components/ui/Button";

function SubscriptionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const userId = searchParams.get("userId");

  function handleFreePlan() {
    router.push(userId ? `/chat?userId=${userId}` : "/chat");
  }

  const freeFeatures = [
    "AI legal guidance",
    "State-specific citations",
    "Document generation",
    "Conversation memory",
  ];

  const proFeatures = [
    "Everything in Free",
    "Priority responses",
    "Advanced templates",
    "Attorney referrals",
    "Unlimited conversations",
  ];

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4">
      <div className="w-full max-w-3xl">
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 text-3xl">
            &#x2696;
          </div>
          <h1 className="text-2xl font-bold text-white">Choose Your Plan</h1>
          <p className="text-sm text-gray-400 mt-2">
            Get personalized legal guidance tailored to your situation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Free Plan */}
          <div className="bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 p-6 flex flex-col">
            <h2 className="text-lg font-semibold text-white">Free</h2>
            <div className="mt-2 mb-6">
              <span className="text-3xl font-bold text-white">$0</span>
              <span className="text-sm text-gray-400">/month</span>
            </div>
            <ul className="space-y-3 mb-8 flex-1">
              {freeFeatures.map((feature: string) => (
                <li key={feature} className="flex items-center gap-2 text-sm text-gray-300">
                  <span className="text-blue-400">&#10003;</span>
                  {feature}
                </li>
              ))}
            </ul>
            <Button onClick={handleFreePlan} className="w-full" variant="outline">
              Continue on Free Plan
            </Button>
          </div>

          {/* Pro Plan */}
          <div className="relative bg-white/[0.03] backdrop-blur-xl rounded-xl border border-blue-500/40 p-6 flex flex-col shadow-[0_0_30px_-5px_rgba(99,102,241,0.15)]">
            <span className="absolute top-4 right-4 text-xs font-medium text-blue-400 bg-blue-500/10 border border-blue-500/20 rounded-full px-2.5 py-0.5">
              Coming Soon
            </span>
            <h2 className="text-lg font-semibold text-white">Pro</h2>
            <div className="mt-2 mb-6">
              <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-violet-500 bg-clip-text text-transparent">
                $30
              </span>
              <span className="text-sm text-gray-400">/month</span>
            </div>
            <ul className="space-y-3 mb-8 flex-1">
              {proFeatures.map((feature: string) => (
                <li key={feature} className="flex items-center gap-2 text-sm text-gray-300">
                  <span className="text-violet-400">&#10003;</span>
                  {feature}
                </li>
              ))}
            </ul>
            <Button disabled className="w-full">
              Coming Soon
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SubscriptionPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#050505] flex items-center justify-center">
          <p className="text-gray-400">Loading...</p>
        </div>
      }
    >
      <SubscriptionContent />
    </Suspense>
  );
}
