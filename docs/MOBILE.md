# Mobile App (Expo React Native)

CaseMate's mobile client is an Expo Router app targeting iOS, Android, and web.
It shares TypeScript type definitions with the Next.js web frontend via `shared/types/`.

## Tech Stack

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Expo | ~55.x canary | Framework + build toolchain |
| expo-router | ^3.5.24 | File-based routing (Stack + Tabs) |
| react-native | ^0.84.1 | UI runtime |
| @supabase/supabase-js | ^2.39.0 | Auth + realtime |
| nativewind | ^2.0.11 | Tailwind CSS in React Native |
| expo-document-picker | ~11.10.0 | Legal document file selection |
| expo-image-picker | ~14.7.0 | Camera capture for document photos |

## Directory Layout

```
mobile/
  app/
    _layout.tsx            Root Stack: index, (auth), (app)
    index.tsx              Splash/landing screen
    (auth)/
      login.tsx            Sign-in screen
      onboarding.tsx       5-question legal intake wizard
    (app)/
      _layout.tsx          Tab navigator (5 tabs + hidden screens)
      chat.tsx             Main AI chat interface
      cases.tsx            Active legal issues list
      tools.tsx            Legal tools hub (letters, rights, checklists)
      deadlines.tsx        Deadline tracking dashboard
      profile.tsx          Legal profile viewer/editor
      attorneys.tsx        Attorney search (hidden, navigated to from tools)
      conversations.tsx    Conversation history (hidden)
      documents.tsx        Document upload manager (hidden)
      rights.tsx           Know Your Rights library (hidden)
      rights-guide.tsx     Individual rights guide detail (hidden)
      workflows.tsx        Legal workflow list (hidden)
      workflow-wizard.tsx  Step-by-step workflow UI (hidden)
  components/
    ChatBubble.tsx         Message bubble with legal area tag + bold formatting
    ProfileCard.tsx        Profile summary card (avatar, state badge, fact/issue counts)
    IssueCard.tsx          Legal issue card with status badge + expandable notes
    DocumentPicker.tsx     File/camera upload with progress bar + extracted facts display
  lib/
    api.ts                 All backend API calls with auth headers + retry logic
    supabase.ts            Supabase client (EXPO_PUBLIC_SUPABASE_URL/KEY)
    types.ts               Re-exports all types from shared/types/
```

## Navigation Structure

**Root Stack** (`app/_layout.tsx`): Three route groups.

1. `index` -- Splash screen with "Get Started" and "Sign In" buttons. Header hidden.
2. `(auth)` -- Onboarding and login. Header hidden. No auth required.
3. `(app)` -- Authenticated area. Redirects to login if no Supabase session.

**App Tabs** (`app/(app)/_layout.tsx`): Five visible tabs + seven hidden stack screens.

| Tab | Icon | Header Title |
|-----|------|-------------|
| Chat | message | CaseMate |
| Cases | folder | Your Cases |
| Tools | wrench | Legal Tools |
| Deadlines | clock | Your Deadlines |
| Profile | person | Your Profile |

Hidden screens (navigated to programmatically, not shown in tab bar): rights, rights-guide, workflows, workflow-wizard, attorneys, conversations, documents.

## Shared Types with Backend

All TypeScript types live in `shared/types/` and are re-exported through `mobile/lib/types.ts`. The mobile app imports from `@/lib/types`. See `docs/MODELS.md` for the full type reference. Key shared interfaces: `LegalProfile`, `LegalIssue`, `Message`, `ChatResponse`, `DemandLetter`, `RightsSummary`, `Checklist`, `Deadline`, `RightsGuide`, `WorkflowTemplate`, `Attorney`.

## API Client

`mobile/lib/api.ts` wraps all backend calls. Every request attaches a Supabase JWT via `getAuthHeaders()`. Failed requests retry up to 3 times with exponential backoff (1s, 2s, 4s). The base URL defaults to `EXPO_PUBLIC_API_URL` or `http://localhost:8000/api`. See `CLAUDE.md` for the full route contract.

## Auth Flow

The `(app)/_layout.tsx` checks `supabase.auth.getSession()` on mount and subscribes to `onAuthStateChange`. If no session exists, the user is redirected to `/(auth)/login`. The splash screen at `index.tsx` offers entry points to onboarding or login.

## Environment Variables

```
EXPO_PUBLIC_SUPABASE_URL   Supabase project URL
EXPO_PUBLIC_SUPABASE_KEY   Supabase anon/public key
EXPO_PUBLIC_API_URL        Backend base URL (default: http://localhost:8000/api)
```

## Running Locally

```bash
cd mobile
npm install
npx expo start          # Dev server (scan QR for Expo Go)
npx expo start --ios    # iOS simulator
npx expo start --android # Android emulator
```
