import Link from "next/link";

function FeatureCard({
  icon,
  iconColor,
  title,
  description,
}: {
  icon: React.ReactNode;
  iconColor: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 p-6 hover:border-white/20 hover:shadow-glow-sm transition-all duration-300">
      <div className={`text-3xl mb-4 ${iconColor}`}>{icon}</div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#050505] bg-[radial-gradient(ellipse_at_top,rgba(59,130,246,0.15)_0%,rgba(139,92,246,0.05)_45%,transparent_70%)]">
      {/* Nav */}
      <nav className="container-wide py-6 flex items-center justify-between">
        <div className="text-xl font-bold text-blue-400">CaseMate</div>
        <div className="flex items-center gap-4">
          <Link
            href="/chat?demo=true"
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Try Demo
          </Link>
          <Link
            href="/onboarding"
            className="inline-flex items-center px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-400 shadow-glow-md hover:shadow-glow-lg transition-all duration-200"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="container-narrow pt-16 pb-20 text-center">
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6 leading-tight">
          Your Personal AI
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-violet-400">Legal Assistant</span>
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          CaseMate remembers your situation, cites your state&apos;s actual statutes,
          and generates demand letters, rights summaries, and checklists
          tailored to you.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            href="/onboarding"
            className="inline-flex items-center px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-400 shadow-glow-lg hover:shadow-[0_0_60px_rgba(59,130,246,0.3)] transition-all duration-200 text-base"
          >
            Get Started
          </Link>
          <Link
            href="/chat?demo=true"
            className="inline-flex items-center px-6 py-3 border border-white/15 text-gray-300 font-medium rounded-lg hover:bg-white/5 hover:border-white/25 transition-all text-base"
          >
            Try Demo
          </Link>
        </div>
      </section>

      {/* Trust bar */}
      <section className="container-narrow pb-16">
        <div className="flex items-center justify-center gap-8 text-gray-500 text-sm">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
            <span>Private & Encrypted</span>
          </div>
          <div className="border-r border-white/10 h-4" />
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <span>Data Never Shared</span>
          </div>
          <div className="border-r border-white/10 h-4" />
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
            <span>Real Statute Citations</span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container-wide pb-24">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <FeatureCard
            icon={
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
              </svg>
            }
            iconColor="text-blue-400"
            title="Memory"
            description="CaseMate builds a profile of your legal situation over time. No need to repeat yourself — it remembers your housing, employment, family status, and active issues."
          />
          <FeatureCard
            icon={
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" />
              </svg>
            }
            iconColor="text-violet-400"
            title="State-Specific"
            description="Get answers grounded in your state's actual statutes and regulations. Real legal citations, not generic advice."
          />
          <FeatureCard
            icon={
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
            }
            iconColor="text-emerald-400"
            title="Actions"
            description="Generate demand letters, rights summaries, and step-by-step legal checklists with deadlines — all personalized to your situation."
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="container-wide text-center text-sm text-gray-600">
          CaseMate is an AI assistant and does not provide legal advice. Consult a
          licensed attorney for legal matters.
        </div>
      </footer>
    </div>
  );
}
