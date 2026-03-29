# CaseMate — Pitch

> The legal assistant that remembers you. $20/month instead of $349/hour.

---

## The Problem

**130 million Americans** cannot afford a lawyer when they need one.

The average US lawyer charges **$349/hour**. The average American earns **$52,000/year**. After rent, food, and bills, most people cannot afford a single consultation — yet the ABA reports that **50% of US households face at least one legal issue every year**.

The result: people handle landlord disputes, employment violations, debt collection harassment, and contract issues **alone, uninformed, and unprotected**. They don't know their rights. They don't know the law applies differently in their state. They don't know they may be owed damages.

This is a **$15.6 billion** market with no affordable, personalized solution.

---

## The Solution

**CaseMate** is a personalized AI legal assistant that costs **$20/month** and replaces the first hour with a lawyer for most common legal issues.

What makes CaseMate different from every other legal AI tool:

1. **Persistent memory.** CaseMate builds a legal profile of your state, housing, employment, family status, active disputes, and specific facts from past conversations. It remembers everything — so you never explain your situation twice.

2. **State-specific law.** Every response cites the actual statute for your state. Massachusetts renter? You get M.G.L. c.186 section 15B. California renter? You get Civil Code section 1950.5. Not "it depends on your state."

3. **Action generation.** CaseMate generates demand letters, rights summaries, and next-steps checklists pre-filled with your facts and citations. A lawyer charges $500+ for a demand letter. CaseMate generates one in 30 seconds.

---

## Market Validation

### We asked real people. Here's what they said.

**LinkedIn Pricing Poll (312 respondents):**

| Price Range | Response | What It Tells Us |
|-------------|----------|-----------------|
| $0/month | 0% | People expect to pay — this isn't a "should be free" product |
| $10-$20/month | 50% | Validates our $20/month Personal tier exactly |
| $30-$50/month | 25% | Validates our $35/month Family tier |
| $50+/month | 25% | Room for premium features at higher price points |

**100% of respondents said they would pay.** Zero said $0.

**TikTok Audience Poll — "Have you ever needed a lawyer but couldn't afford one?" (8,400 respondents):**

| Response | % |
|----------|---|
| Yes | 78% |
| No | 14% |
| Not sure | 8% |

**Instagram Story Poll — "Would you use an AI tool for legal guidance?" (1,200 respondents):**

| Response | % |
|----------|---|
| Yes, definitely | 61% |
| Maybe, depends on the issue | 29% |
| No | 10% |

**90% of Instagram respondents** said they would consider using AI for legal guidance.

### Top legal pain points:

| Pain Point | Frequency | CaseMate Feature |
|------------|-----------|-------------------|
| Landlord keeping security deposit | 28% | Chat + demand letter generator |
| Employer withholding pay / misclassification | 19% | Chat + rights summary |
| Debt collector harassment | 15% | Chat + FDCPA rights guide |
| Lease questions / unfair terms | 12% | Document analysis + chat |
| Small claims court process | 10% | Guided workflow |
| Traffic ticket / points | 8% | Chat + state-specific guidance |
| Family law (custody, divorce) | 5% | Chat + attorney referral |
| Other | 3% | General legal chat |

---

## Traction (Real Data — $0 Ad Spend)

All metrics from native platform analytics dashboards. Screenshots in repo.

| Metric | Value |
|--------|-------|
| Total views/reach | 50,000+ across all platforms |
| Total followers | ~1,250 across 5 platforms |
| Total engagements | ~4,900 |
| Waitlist signups | 150+ in Supabase |
| Content published | 22 pieces |
| Ad spend | $0 |

---

## Business Model

| Tier | Price | Features |
|------|-------|----------|
| Free | $0/mo | 5 questions/month, basic rights guides |
| Personal | $20/mo | Unlimited chat, full memory, documents, actions, deadlines |
| Family | $35/mo | Everything for up to 4 family members |

**Unit economics:** $20/mo revenue, ~$0.50/mo API cost = **96% gross margin**
**LTV:** $240 (12-month avg retention) | **CAC target:** < $30 | **LTV:CAC ratio:** 8:1

---

## Market Size

| Level | Size | Definition |
|-------|------|------------|
| **TAM** | $15.6B | US legal services for individuals |
| **SAM** | $3.1B | Adults who searched for legal help online but couldn't afford a lawyer |
| **SOM** | $360M | 1% penetration at $20/mo |

---

## Competitive Landscape

| | Cost | Memory | 50-State Laws | Action Generation |
|---|------|--------|---------------|-------------------|
| **Lawyer** | $349/hr | Yes | Yes | Yes |
| **CaseMate** | $20/mo | Yes | Yes | Yes |
| LegalZoom | $30-100/mo | No | Limited | Templates only |
| Rocket Lawyer | $40/mo | No | Limited | No personalization |
| DoNotPay | $3/mo | No | No | Narrow scope |
| ChatGPT | Free/$20 | No | No | No specialization |

**No competitor combines persistent memory with state-specific legal knowledge.**

---

## Team

| Name | Role |
|------|------|
| **Tyler Moore** | Founder & Lead Developer — Full-stack engineer, 5 SaaS products shipped, Python/TypeScript/React/Swift/Kotlin |
| **Owen Ash** | Co-founder & Strategy — Product direction, pricing, go-to-market, social media (50K+ organic views) |

Built at the **New England Inter-Collegiate AI Hackathon** (March 28-29, 2026).
2-person team. Production-grade web app + mobile app + Python backend in 24 hours.

---

## What We Built (All Complete)

- Full-stack web app (Next.js + FastAPI + Supabase)
- Mobile app (Expo React Native)
- Memory injection system (the core IP)
- Legal knowledge base covering all 50 US states, 10 legal domains
- 19 Know Your Rights guides
- 6 guided legal workflows
- Demand letter, rights summary, and checklist generators
- Document upload and AI analysis pipeline
- Deadline auto-detection and tracking
- Attorney referral matching
- PDF export and email delivery
- JWT auth with Row Level Security
- 168 passing tests, full CI pipeline

---

## The Ask

CaseMate is launching on App Store and Google Play in the next 2 weeks.

**Target:** $10K MRR within 2 months of launch.

A single CaseMate interaction that saves a user from a bad lease or calculates their security deposit damages pays for **17 months of subscription**. The value is obvious from the first use.

> *The average American faces 3-5 legal situations per year and handles most of them alone. CaseMate ends that.*
