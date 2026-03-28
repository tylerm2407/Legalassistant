# ADR 005: Monorepo with Shared Types

## Status
Accepted

## Context
Lex has three surfaces: Python backend, Next.js web app, and Expo mobile app. They share data models and API contracts.

## Decision
Single monorepo with `shared/types/` containing TypeScript type definitions that mirror the Python Pydantic models. Each frontend imports from shared types.

## Consequences
- Single source of truth for the codebase
- Type changes are visible across all surfaces
- Shared types must be manually kept in sync with Pydantic models
- Simpler deployment and CI/CD than multi-repo
