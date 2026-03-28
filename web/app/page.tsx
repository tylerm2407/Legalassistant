import Link from "next/link";

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 hover:shadow-md transition-shadow">
      <div className="text-3xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-white">
      {/* Nav */}
      <nav className="container-wide py-6 flex items-center justify-between">
        <div className="text-xl font-bold text-blue-600">Lex</div>
        <div className="flex items-center gap-4">
          <Link
            href="/chat?demo=true"
            className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            Try Demo
          </Link>
          <Link
            href="/onboarding"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="container-narrow pt-16 pb-20 text-center">
        <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6 leading-tight">
          Your Personal AI
          <br />
          <span className="text-blue-600">Legal Assistant</span>
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed">
          Lex remembers your situation, cites your state&apos;s actual statutes,
          and generates demand letters, rights summaries, and checklists
          tailored to you.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            href="/onboarding"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm text-base"
          >
            Get Started
          </Link>
          <Link
            href="/chat?demo=true"
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors text-base"
          >
            Try Demo
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container-wide pb-24">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <FeatureCard
            icon="🧠"
            title="Memory"
            description="Lex builds a profile of your legal situation over time. No need to repeat yourself — it remembers your housing, employment, family status, and active issues."
          />
          <FeatureCard
            icon="📜"
            title="State-Specific"
            description="Get answers grounded in your state's actual statutes and regulations. Real legal citations, not generic advice."
          />
          <FeatureCard
            icon="⚡"
            title="Actions"
            description="Generate demand letters, rights summaries, and step-by-step legal checklists with deadlines — all personalized to your situation."
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8">
        <div className="container-wide text-center text-sm text-gray-500">
          Lex is an AI assistant and does not provide legal advice. Consult a
          licensed attorney for legal matters.
        </div>
      </footer>
    </div>
  );
}
