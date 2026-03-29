# ADR 026: Navbar Component

## Status
Accepted

## Context
CaseMate had navigation links scattered inline within the ChatInterface header. Users needed a consistent way to navigate between chat, rights library, deadlines, attorneys, and workflows from any page — not just the chat view.

## Decision
Extract navigation into a dedicated `Navbar` component (`web/components/Navbar.tsx`) and render it in `web/app/layout.tsx` so it appears on every page. The navbar uses the i18n system for translated labels and highlights the active route.

## Consequences
- **Positive:** Consistent navigation across all pages, single source of truth for nav links, i18n-ready out of the box.
- **Positive:** Layout.tsx wraps all children with `LanguageWrapper` > `AuthProvider` > `Navbar`, so auth and language context are always available.
- **Negative:** Slightly more complex layout tree with nested providers.
