# Lex — Build Progress

## Phase 0 — Scaffold ✅
- [x] Repository structure created
- [x] Root config files (pyproject.toml, Makefile, .env.example)
- [x] Documentation (CLAUDE.md, ARCHITECTURE.md, README.md)
- [x] CI/CD pipeline (.github/workflows/ci.yml)
- [x] ADR decisions (001-005)

## Phase 1 — Backend Foundation
- [ ] Models (LegalProfile, Conversation, ActionOutput)
- [ ] Utils (logger, retry)
- [ ] Memory injector (build_system_prompt)
- [ ] Legal classifier (10 domains)
- [ ] State laws (MA, CA, NY, TX, FL)
- [ ] Legal area modules (10 files)
- [ ] FastAPI main.py with routes

## Phase 2 — Profile CRUD
- [ ] Profile CRUD (get_profile, update_profile)
- [ ] Profile auto-updater (background task)
- [ ] Supabase schema applied

## Phase 3 — Document Pipeline
- [ ] PDF/image text extraction
- [ ] Claude document analysis
- [ ] Upload route

## Phase 4 — Action Generators
- [ ] Demand letter generator
- [ ] Rights summary generator
- [ ] Checklist generator

## Phase 5 — Web Frontend
- [ ] Shared types
- [ ] API client + Supabase client
- [ ] UI primitives (Button, Card, Input, Badge)
- [ ] Onboarding flow
- [ ] Chat interface with sidebar
- [ ] Action generator UI
- [ ] Profile page

## Phase 6 — Mobile Frontend
- [ ] Expo setup + routing
- [ ] Chat screen
- [ ] Profile + Cases screens
- [ ] Components (ChatBubble, ActionSheet, etc.)

## Phase 7 — Tests
- [ ] Memory injector tests
- [ ] Legal classifier tests
- [ ] Profile updater tests
- [ ] Action generator tests

## Phase 8 — Demo Prep
- [ ] Sarah Chen demo profile seeded
- [ ] End-to-end verification
