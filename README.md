# Lex — Your Personal AI Legal Assistant

**Lex remembers your legal situation.** Every answer is specific to your state, your housing, your employment, and every legal fact you've shared. Not a generic chatbot — a knowledgeable friend who has been advising you for months.

## The Problem

Legal advice is expensive ($200-500/hour). Free resources give generic answers that don't account for your specific situation, state laws, or history. Most people facing legal issues — landlord disputes, employment violations, debt collection — can't afford real help and don't know their rights.

## The Solution

Lex builds a persistent legal profile from every conversation. When you ask about your security deposit, Lex already knows you're in Massachusetts, you've been renting for 2 years, your landlord didn't do a move-in inspection, and your deposit hasn't earned interest. The answer cites M.G.L. c.186 §15B and calculates your specific damages.

## Features

- **Persistent Memory**: Legal profile grows with every conversation
- **State-Specific Guidance**: Real statute citations for MA, CA, NY, TX, FL
- **10 Legal Domains**: Landlord/tenant, employment, consumer, debt, small claims, contracts, traffic, family law, criminal records, immigration
- **Action Generators**: Demand letters, rights summaries, next-steps checklists — all pre-filled from your profile
- **Document Analysis**: Upload leases, notices, contracts — Lex extracts key facts and red flags
- **Cross-Platform**: Web app + iOS/Android mobile app

## Quick Start

```bash
# Backend
cp .env.example .env  # Add your API keys
pip install -e ".[dev]"
make dev

# Web
cd web && npm install && npm run dev

# Mobile
cd mobile && npm install && npx expo start
```

## Demo

Ask Sarah Chen's profile: *"Can my landlord keep my security deposit for bathroom tile damage?"*

Lex responds with MA-specific deposit law (M.G.L. c.186 §15B), references her move-in photos showing pre-existing water damage, calculates triple damages ($6,600), and offers to generate a demand letter.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full system design.

## Team

Built by Tyler Moore and Owen Ash for the New England Inter-Collegiate AI Hackathon, March 2026.
