# Lex — Architecture

## System Overview

Lex is a monorepo containing a Python backend (FastAPI), a web frontend (Next.js), and a mobile app (Expo React Native). All frontends communicate with a single backend API.

## Memory Architecture

The core innovation is **persistent legal profile injection**:

```
User Question
    ↓
classify_legal_area(question) → legal domain
    ↓
get_profile(user_id) → LegalProfile from Supabase
    ↓
build_system_prompt(profile, question) → personalized system prompt
    ↓
Claude API call with system prompt + user message
    ↓
Response to user
    ↓
Background: update_profile_from_conversation() → extract new facts → update Supabase
```

## Data Flow

### Chat Request
1. Frontend sends `{ user_id, question }` to `POST /api/chat`
2. Backend retrieves user's `LegalProfile` from Supabase
3. `classify_legal_area()` identifies the legal domain (keyword-based, no LLM)
4. `build_system_prompt()` assembles: base instructions + profile + state laws + response rules
5. Claude API returns personalized answer
6. Background task extracts new legal facts from conversation → updates profile
7. Frontend refreshes profile sidebar to show new facts

### Profile Auto-Update
After every chat response, `update_profile_from_conversation()`:
1. Sends conversation to Claude with an extraction prompt
2. Claude returns structured JSON of new facts
3. New facts are merged into the user's profile in Supabase
4. Next conversation will include these facts in the system prompt

## API Contracts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Send legal question, get personalized answer |
| GET | `/api/profile/{user_id}` | Get user's legal profile |
| POST | `/api/profile` | Create/update legal profile |
| POST | `/api/actions/letter` | Generate demand letter |
| POST | `/api/actions/rights` | Generate rights summary |
| POST | `/api/actions/checklist` | Generate next-steps checklist |
| POST | `/api/documents` | Upload and analyze legal document |

## Database Schema (Supabase)

- `user_profiles` — Legal profile with active_issues (JSONB), legal_facts (JSONB)
- `conversations` — Chat history with legal_area classification
- `documents` — Uploaded documents with extracted_facts, red_flags

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Pydantic v2 |
| AI | Anthropic Claude API (claude-sonnet-4-6) |
| Database | Supabase (PostgreSQL + Auth + Storage) |
| Web | Next.js 14, React, Tailwind CSS |
| Mobile | Expo, React Native, Expo Router |
| Logging | structlog |
| PDF | pdfplumber |
