import dynamic from "next/dynamic";
import Link from "next/link";
import WaitlistForm from "@/components/WaitlistForm";

const LiquidEther = dynamic(() => import("@/components/LiquidEther"), { ssr: false });

export default function HomePage() {
  return (
    <div className="relative min-h-screen bg-[#030305] overflow-hidden">
      {/* Liquid Ether Background — z-0 */}
      <div className="absolute inset-0 z-0">
        <LiquidEther
          colors={['#5227FF', '#FF9FFC', '#B19EEF']}
          mouseForce={20}
          cursorSize={100}
          isViscous
          viscous={30}
          iterationsViscous={32}
          iterationsPoisson={32}
          resolution={0.5}
          isBounce={false}
          autoDemo
          autoSpeed={0.5}
          autoIntensity={2.2}
          takeoverDuration={0.25}
          autoResumeDelay={3000}
          autoRampDuration={0.6}
        />
      </div>

      {/* Gradient overlay — z-1 */}
      <div className="absolute inset-0 z-[1] bg-gradient-to-b from-[#030305]/40 via-[#030305]/60 to-[#030305]/90 pointer-events-none" />

      {/* Content — z-10 */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Nav */}
        <nav className="container-wide py-6 flex items-center justify-between animate-fade-up">
          <div className="text-xl font-bold text-blue-400">CaseMate</div>
          <Link
            href="/chat?demo=true"
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Try Demo
          </Link>
        </nav>

        {/* Hero — centered vertically */}
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="text-center max-w-2xl mx-auto">
            {/* Badge */}
            <div className="animate-fade-up delay-100">
              <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs font-medium text-blue-400 mb-8">
                <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
                AI-Powered Legal Help
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-[1.1] mb-6 animate-fade-up delay-200">
              <span className="text-white">Legal Help That</span>
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-violet-400 to-blue-400">
                Remembers You
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl text-gray-400 max-w-lg mx-auto mb-10 leading-relaxed animate-fade-up delay-300">
              Your state. Your situation. Your rights.
              <br />
              <span className="text-gray-500">$20/month instead of $349/hour.</span>
            </p>

            {/* Email form — glassmorphic card */}
            <div className="animate-fade-up delay-400">
              <div className="bg-white/[0.04] backdrop-blur-xl border border-white/10 rounded-2xl p-6 sm:p-8 max-w-md mx-auto shadow-[0_0_80px_rgba(59,130,246,0.08)]">
                <WaitlistForm />
                <p className="text-gray-600 text-xs mt-4">
                  Join 100+ people on the waitlist
                </p>
              </div>
            </div>

            {/* Trust bar */}
            <div className="flex items-center justify-center gap-6 sm:gap-8 mt-10 text-gray-500 text-sm animate-fade-up delay-500">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
                <span>Private</span>
              </div>
              <div className="border-r border-white/10 h-4" />
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                </svg>
                <span>Real Citations</span>
              </div>
              <div className="border-r border-white/10 h-4" />
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M20.893 13.393l-1.135-1.135a2.252 2.252 0 01-.421-.585l-1.08-2.16a.414.414 0 00-.663-.107.827.827 0 01-.812.21l-1.273-.363a.89.89 0 00-.738 1.595l.587.39c.59.395.674 1.23.172 1.732l-.2.2c-.212.212-.33.498-.33.796v.41c0 .409-.11.809-.32 1.158l-1.315 2.191a2.11 2.11 0 01-1.81 1.025 1.055 1.055 0 01-1.055-1.055v-1.172c0-.92-.56-1.747-1.414-2.089l-.655-.261a2.25 2.25 0 01-1.383-2.46l.007-.042a2.25 2.25 0 01.29-.787l.09-.15a2.25 2.25 0 012.37-1.048l1.178.236a1.125 1.125 0 001.302-.795l.208-.73a1.125 1.125 0 00-.578-1.315l-.665-.332-.091.091a2.25 2.25 0 01-1.591.659h-.18a.94.94 0 00-.662.274.931.931 0 01-1.458-1.137l1.411-2.353a2.25 2.25 0 00.286-.76M11.25 2.25L12 2c3.209 0 6.168 1.06 8.55 2.85" />
                </svg>
                <span>50 States</span>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="py-6 text-center">
          <p className="text-xs text-gray-600 max-w-md mx-auto px-4">
            CaseMate is an AI assistant and does not provide legal advice.
            Consult a licensed attorney for legal matters.
          </p>
        </footer>
      </div>
    </div>
  );
}
