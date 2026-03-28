# ADR 002: Keyword-Based Legal Classifier

## Status
Accepted

## Context
We need to classify user questions into legal domains to inject the correct state laws.

## Decision
Use keyword matching (not LLM) for classification. Map keyword sets to 10 legal domains. Falls back to "general" if no match.

## Consequences
- Classification is instant (no API call latency)
- No additional cost per classification
- Less accurate than LLM classification for ambiguous questions
- Can be upgraded to LLM classification later if needed
