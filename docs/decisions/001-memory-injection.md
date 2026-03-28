# ADR 001: Memory Injection as Core Architecture

## Status
Accepted

## Context
Lex needs to provide personalized legal guidance. Generic chatbot responses are not sufficient — users need answers specific to their state, situation, and history.

## Decision
Every Claude API call receives a system prompt assembled by `build_system_prompt()` that includes:
1. The user's complete LegalProfile
2. State-specific statute citations for the classified legal domain
3. Domain-specific response guidance
4. Response rules ensuring personalized, actionable answers

## Consequences
- Responses are always personalized without requiring the user to repeat context
- System prompt size grows with profile richness (managed by keeping facts concise)
- Profile quality directly determines answer quality
