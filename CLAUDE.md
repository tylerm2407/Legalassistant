# Lex — AI Legal Assistant

## What This Is
Lex is a personalized AI legal assistant that remembers the user's full legal situation across every conversation. The core differentiator: every Claude API call injects the user's legal profile as structured context.

## Build Order
1. Backend models → utils → memory → legal → actions → documents → main.py
2. Web frontend (Next.js + Tailwind)
3. Mobile frontend (Expo React Native)
4. Tests → Polish → Demo

## Code Standards — No Exceptions
- Every class and public method: full docstring with Args/Returns/Raises
- Every function: full type annotations — no `Any`, no missing return types
- Structured logging with user_id context — never bare `print()`
- All Anthropic API calls through `backend/utils/retry.py` (3-attempt backoff)
- No bare `except` — catch specific, log with context, re-raise or handle
- No placeholder code — stubs raise `NotImplementedError`
- Run `make verify` before every commit

## Architecture
- **Memory Injector** (`backend/memory/injector.py`): Most important file. Builds personalized system prompts.
- **Legal Classifier** (`backend/legal/classifier.py`): Keyword-based, not LLM-based, for speed.
- **State Laws** (`backend/legal/state_laws.py`): Real statute citations per state per domain.
- **Profile Auto-Updater** (`backend/memory/updater.py`): Background task extracts facts post-response.

## Legal Domain — NOT Trading
This is a legal assistant. Ignore trading/fintech patterns. The only domain knowledge is legal.

## Commit Format
```
feat(scope): description
fix(scope): description
test(scope): description
docs(scope): description
chore: description
```
