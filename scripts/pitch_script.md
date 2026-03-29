# CaseMate — Pitch Script (3 minutes)

> Target: New England Inter-Collegiate AI Hackathon judges
> Presenters: Tyler Moore & Owen Ash
> Setup: CaseMate open in browser with Sarah Chen's profile loaded in the sidebar

---

## OPEN — The Hook (20 seconds)

**Tyler:**

"The average American lawyer charges $349 an hour. The average American earns $52,000 a year. That means a single legal consultation costs more than a week of take-home pay.

130 million Americans can't afford a lawyer when they need one. We built CaseMate to close that gap."

---

## THE PROBLEM (30 seconds)

**Owen:**

"Here's what happens today. You Google 'can my landlord keep my security deposit?' You get a generic article that says 'it depends on your state.' That's useless.

You ask ChatGPT. It gives you a paragraph about security deposit laws — but it doesn't know you live in Massachusetts, it doesn't know your landlord skipped the move-in inspection, and it forgets everything the next time you ask.

The information exists. It's just locked behind a $349/hour paywall — or buried in generic answers that ignore your actual situation."

---

## THE PRODUCT — Live Demo (60 seconds)

**Tyler:**

*[Screen shows CaseMate with Sarah Chen's profile visible in the sidebar]*

"This is CaseMate. On the left you can see Sarah Chen's legal profile — she's a renter in Massachusetts, month-to-month, no signed lease. She has an active dispute: her landlord is claiming $800 for bathroom tile damage.

CaseMate already knows 8 legal facts about Sarah — including that her landlord never did a move-in inspection, and that she has photos of pre-existing water damage. She didn't fill out a form for these — CaseMate extracted them automatically from her conversations over time.

Watch what happens when she asks a question."

*[Types: "My landlord is saying I owe $800 for the bathroom tiles"]*

*[Response streams in — cites M.G.L. c.186 section 15B, references the missing inspection, calculates up to $3,200 in potential recovery]*

"Look at that response. It cited the exact Massachusetts statute. It referenced the missing move-in inspection that Sarah mentioned three conversations ago. And it calculated that Sarah may be owed her deposit plus up to three times damages — $3,200 — because her landlord violated the law.

A lawyer would have given that same consultation. For $349."

*[Clicks 'Generate Demand Letter']*

"And now — one click — CaseMate generates a demand letter pre-filled with Sarah's facts, the statute citation, and the damage calculation. Ready to send."

---

## HOW IT WORKS — The Architecture (30 seconds)

**Tyler:**

"This isn't a chatbot with a legal wrapper. Every response is assembled from three layers:

**One** — the user's legal profile. State, housing, employment, active issues, and every legal fact extracted from past conversations. This is a structured Pydantic model that grows over time — not raw chat history.

**Two** — state-specific statutes. We built a knowledge base covering all 50 states across 10 legal domains — real statute citations, not vague references.

**Three** — a memory injection system that combines both into a system prompt. Every API call is personalized to this specific user's situation.

The result: the more you use CaseMate, the better it knows your situation. Memory is the product."

---

## THE BUSINESS (20 seconds)

**Owen:**

"CaseMate is $20 a month. Our API cost per user is 50 cents. That's 97.5% gross margin.

We've already validated demand: 8,400 TikTok respondents — 78% have needed a lawyer but couldn't afford one. 312 LinkedIn respondents — 100% willing to pay, half chose the $10-20 range. 300 people on our waitlist, all at zero ad spend.

The $15.6 billion US legal services market for individuals is underserved by a factor of 50 to 1. We're not competing with lawyers — we're replacing the first hour."

---

## THE MOAT (15 seconds)

**Tyler:**

"Three things make this defensible. First, compounding memory — every conversation makes CaseMate more valuable to that user. Switching means starting over from zero context. Second, our 50-state legal knowledge base — Owen spent 8-plus hours during this hackathon hand-building statute references. Third, domain-specific prompt engineering that a general chatbot can't replicate without equivalent legal investment.

LegalZoom sells templates. ChatGPT gives generic answers. CaseMate gives you a knowledgeable friend who actually remembers your situation."

---

## CLOSE — The Number (5 seconds)

**Tyler:**

"A lawyer would have charged Sarah $700 for that consultation and demand letter. CaseMate costs $20 a month. That's the gap we're closing."

---

## JUDGE Q&A — Prepared Answers

**"What stops OpenAI/Anthropic from building this?"**
> Incentive misalignment — they sell API tokens. Building a $20/month vertical app competes with their own customers. Google didn't build Salesforce. AWS didn't build Slack. Platform providers don't build niche vertical apps. Plus, the 50-state legal knowledge base and user profiles are non-replicable.

**"Is this legal advice? Are you worried about UPL (unauthorized practice of law)?"**
> CaseMate provides legal information, not legal advice — every response includes a disclaimer. We follow the same model as LegalZoom, Nolo, and Avvo, which have operated for 20+ years. The ABA's 2025 resolution explicitly encouraged AI-assisted legal services. We also route users to real attorneys via our referral feature when they need actual representation.

**"How accurate are the legal citations?"**
> Our statute citations are deterministic — they come from a hand-built database, not hallucinated by the model. The AI generates the explanation; the citations are injected from our verified knowledge base. We cover all 50 states across 10 legal domains.

**"What's your go-to-market?"**
> Organic social media — we've already built an audience (50K+ views, 1,250 followers) through legal tips content on TikTok and Instagram. Our waitlist has 300+ signups at zero ad spend. Phase 2 is paid social retargeting waitlist visitors.

**"How do you handle hallucination?"**
> Three layers of defense. First, statute citations are injected from a verified database — the model doesn't generate them. Second, the system prompt explicitly instructs the model to only reference facts from the user's profile. Third, we have prompt injection defenses that prevent profile data from being interpreted as instructions.

**"What's the tech stack?"**
> Next.js 14 frontend, FastAPI Python backend, Supabase for database/auth/storage, dual-model LLM architecture with automatic failover, 509 backend tests at 90% coverage. Built entirely with Claude Code in 24 hours.

**"What would you build next?"**
> Multi-language support — Spanish first, serving 41 million native Spanish speakers in the US who face even worse access-to-justice barriers. Then real-time statute updates via an automated legislative change pipeline.
