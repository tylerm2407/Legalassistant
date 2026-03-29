# ADR 017 — Mobile architecture with Expo and file-based routing

**Date:** 2026-03-29
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

The CaseMate mobile app is built with Expo React Native using file-based routing via expo-router. The app shares TypeScript types with the web frontend and integrates with the same Supabase backend for authentication and data.

---

## Context

CaseMate needs a mobile app to reach users where they most commonly interact with legal questions — on their phones. The team has two developers with strong TypeScript and React experience but limited native iOS and Android experience. The mobile app must support the same core features as the web app: authenticated login, chat with the legal assistant, legal profile viewing, and a Know Your Rights browser.

The key constraint is team size. A two-person team cannot maintain separate iOS and Android codebases alongside the web frontend and Python backend. The mobile framework must maximize code sharing and minimize platform-specific work.

---

## The implementation

The mobile app lives in `mobile/` with an Expo managed workflow. Routing uses expo-router's file-based convention in `mobile/app/`, mirroring the Next.js App Router pattern used in the web frontend:

- `mobile/app/(auth)/login.tsx` — Login screen with inline validation and auto-redirect
- `mobile/app/(tabs)/chat.tsx` — Chat interface with typed conversation history and typing indicators
- `mobile/app/(tabs)/profile.tsx` — Legal profile display with pull-to-refresh
- `mobile/app/(tabs)/rights.tsx` — Rights browser with search, domain icons, and expandable guides

Shared TypeScript types from `web/lib/types.ts` define the data contracts (LegalProfile, Conversation, Message, RightsGuide) used by both web and mobile. The mobile API client calls the same FastAPI backend endpoints.

Supabase authentication is handled through `@supabase/supabase-js` with secure token storage via `expo-secure-store`. The auth flow mirrors the web implementation — JWT tokens in Supabase, validated by the backend on every request.

---

## Alternatives considered

**React Native CLI (bare workflow)**
Considered. The bare workflow provides full control over native modules and build configuration. Rejected because the additional setup time for configuring Metro, linking native modules, and managing Xcode/Gradle projects is not justified for an app that uses standard UI components and network requests. Expo's managed workflow handles all of this automatically.

**Flutter**
Considered. Flutter's widget system produces high-quality cross-platform UIs and Dart's type system is strong. Rejected because adopting Dart introduces a second language to the stack, eliminates the possibility of sharing types with the TypeScript web frontend, and requires the team to learn a new framework under hackathon time constraints.

**Native iOS (Swift) + Native Android (Kotlin)**
Considered. Native apps provide the best platform integration and performance. Rejected because maintaining two separate mobile codebases plus the web frontend would triple the frontend maintenance burden for a two-person team. The features CaseMate needs (text chat, list views, forms) do not require native performance.

**Progressive Web App (PWA)**
Considered. A PWA would eliminate the mobile codebase entirely. Rejected because PWAs have limited access to push notifications on iOS, cannot be listed on the App Store, and lack the native feel that users expect from a paid subscription app.

---

## Consequences

**Positive:**
- Single TypeScript codebase for iOS and Android
- File-based routing mirrors the Next.js web app, reducing cognitive overhead when switching between web and mobile
- Shared types between web and mobile reduce data contract drift
- Expo's managed workflow handles native build configuration, signing, and over-the-air updates
- expo-router supports deep linking out of the box

**Negative:**
- Expo managed workflow limits access to some native modules (mitigated by Expo's extensive module library)
- React Native performance is lower than native for complex animations (not relevant for CaseMate's text-heavy UI)
- Expo build service introduces a dependency on Expo's infrastructure for production builds
- File-based routing in expo-router is less mature than Next.js App Router and has occasional edge cases with nested layouts

---

## Status

Accepted. Expo with file-based routing is the right choice for a small team building a text-centric mobile app that shares a backend and type system with a Next.js web frontend. If platform-specific features (background processing, advanced push notifications) become requirements, ejecting to the bare workflow is a supported migration path.
