# ADR 003: Background Profile Auto-Update

## Status
Accepted

## Context
After each conversation, new legal facts should be extracted and added to the user's profile for future conversations.

## Decision
Use FastAPI's BackgroundTasks to run `update_profile_from_conversation()` after each chat response. This task sends the conversation to Claude with an extraction prompt, receives structured facts, and merges them into the profile.

## Consequences
- User doesn't wait for profile update (non-blocking)
- Profile grows richer over time without user effort
- Small delay before new facts appear in profile sidebar
- Extraction uses a separate Claude API call (additional cost)
