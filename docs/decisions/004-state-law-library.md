# ADR 004: Static State Law Library

## Status
Accepted

## Context
Lex needs to cite real statutes. LLMs can hallucinate legal citations.

## Decision
Maintain a static `STATE_LAWS` dictionary with verified statute citations for each state-domain combination. Currently covering MA, CA, NY, TX, FL with federal defaults.

## Consequences
- Citations are always real and verified
- Limited to states we've manually researched
- Needs periodic updates when laws change
- Federal defaults ensure coverage even for unsupported states
