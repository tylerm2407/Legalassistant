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

## Screen-by-Screen Breakdown

### Splash / Landing (`index.tsx`)

Entry point. Shows the CaseMate logo, tagline, and two CTAs:
- **"Get Started"** → navigates to `/(auth)/onboarding`
- **"Sign In"** → navigates to `/(auth)/login`

No header. No auth required.

### Login (`(auth)/login.tsx`)

Email/password authentication via Supabase. On successful login, redirects to `/(app)/chat`. If no profile exists yet, redirects to onboarding.

### Onboarding (`(auth)/onboarding.tsx`)

5-question legal intake wizard (same questions as web):
1. Display name
2. State (dropdown, all 50 states)
3. Housing situation (free text)
4. Employment type (free text)
5. Family status (free text)

On completion, creates the user's `LegalProfile` via `POST /api/profile` and navigates to the chat screen.

### Chat (`(app)/chat.tsx`)

Primary interface. Features:
- Message input with send button
- Scrolling message list with `ChatBubble` components
- Legal area tag on each CaseMate response
- Loading indicator during Claude API call
- Pull-to-refresh for conversation reload
- Navigation to conversation history via header button

### Cases (`(app)/cases.tsx`)

Lists all active legal issues from the user's profile. Each issue displayed as an `IssueCard` with:
- Issue type badge (e.g., "landlord_tenant")
- Summary text
- Status indicator (open/resolved/watching/escalated)
- Expandable notes section
- Timestamp (started_at, updated_at)

### Tools (`(app)/tools.tsx`)

Hub screen with cards linking to:
- **Generate Demand Letter** → action generator
- **Know Your Rights** → rights library
- **Legal Checklists** → checklist generator
- **Find an Attorney** → attorney search
- **Legal Workflows** → workflow list
- **Upload Documents** → document manager

### Deadlines (`(app)/deadlines.tsx`)

Deadline tracking dashboard:
- List of deadlines sorted by date (earliest first)
- Status filter (active/completed/dismissed/expired)
- Swipe actions to complete or dismiss
- Color coding: red for upcoming (<7 days), yellow for near (<30 days), green for later

### Profile (`(app)/profile.tsx`)

Displays and allows editing of the user's `LegalProfile`:
- Editable fields: name, state, housing, employment, family
- Read-only sections: legal facts (extracted), documents (uploaded), member since, conversation count
- "Save Changes" button for edits

### Attorney Search (`(app)/attorneys.tsx`)

Hidden screen navigated from Tools:
- State filter (auto-populated from profile)
- Legal area filter
- Results as `AttorneyCard` components with rating, specializations, cost range, contact info
- "Free consultation" badge

### Rights Library (`(app)/rights.tsx` → `rights-guide.tsx`)

Two-screen flow:
1. **List view** — Browse 19 guides organized by domain, search filter
2. **Detail view** — Full guide with sections: explanation, your rights, action steps, deadlines, common mistakes, when to get a lawyer

### Workflows (`(app)/workflows.tsx` → `workflow-wizard.tsx`)

Two-screen flow:
1. **List view** — Available workflow templates and in-progress instances
2. **Wizard view** — Step-by-step guided process with progress indicator, step completion, and guidance text

## Components

### `ChatBubble.tsx`

Renders a single message in the chat:
- User messages: right-aligned, blue background
- CaseMate messages: left-aligned, gray background, legal area tag
- Supports bold formatting (markdown-style) in message text
- Timestamp display

### `ProfileCard.tsx`

Compact profile summary:
- User avatar/initial
- State badge (2-letter code)
- Fact count and issue count
- Member since date

### `IssueCard.tsx`

Legal issue display:
- Status badge with color (open=blue, resolved=green, watching=yellow, escalated=red)
- Issue type label
- Summary text
- Expandable notes section with timestamps

### `DocumentPicker.tsx`

File upload component:
- "Choose File" button → expo-document-picker (PDFs)
- "Take Photo" button → expo-image-picker (camera)
- Upload progress bar
- After upload: displays extracted facts preview from the document analysis pipeline

## API Client

`mobile/lib/api.ts` wraps all backend calls. Every request attaches a Supabase JWT via `getAuthHeaders()`. Failed requests retry up to 3 times with exponential backoff (1s, 2s, 4s). The base URL defaults to `EXPO_PUBLIC_API_URL` or `http://localhost:8000/api`. See `CLAUDE.md` for the full route contract.

### `fetchWithRetry()` Implementation

```typescript
async function fetchWithRetry(url: string, options: RequestInit, retries = 3): Promise<Response> {
    for (let attempt = 0; attempt < retries; attempt++) {
        try {
            const response = await fetch(url, options);
            if (response.ok || response.status < 500) return response; // Don't retry 4xx
            if (attempt < retries - 1) {
                await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 1000)); // 1s, 2s, 4s
            }
        } catch (error) {
            if (attempt === retries - 1) throw error;
            await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 1000));
        }
    }
    throw new Error('All retries exhausted');
}
```

### `getAuthHeaders()`

Fetches the current Supabase session and returns headers with the JWT:

```typescript
async function getAuthHeaders(): Promise<Record<string, string>> {
    const { data: { session } } = await supabase.auth.getSession();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session?.access_token}`,
    };
}
```

## Auth Flow

The `(app)/_layout.tsx` checks `supabase.auth.getSession()` on mount and subscribes to `onAuthStateChange`. If no session exists, the user is redirected to `/(auth)/login`. The splash screen at `index.tsx` offers entry points to onboarding or login.

### Auth State Flow

```
App Launch
    ↓
index.tsx (splash)
    ↓
User taps "Get Started" or "Sign In"
    ↓
(auth)/onboarding.tsx or (auth)/login.tsx
    ↓
Supabase auth succeeds → session stored
    ↓
(app)/_layout.tsx checks session
    ↓
Session valid → show tab navigator
Session invalid → redirect to /(auth)/login
    ↓
onAuthStateChange listener handles:
  - Token refresh (automatic)
  - Sign out → redirect to index
  - Session expired → redirect to login
```

## Shared Types with Backend

All TypeScript types live in `shared/types/` and are re-exported through `mobile/lib/types.ts`. The mobile app imports from `@/lib/types`. See `docs/MODELS.md` for the full type reference. Key shared interfaces: `LegalProfile`, `LegalIssue`, `Message`, `ChatResponse`, `DemandLetter`, `RightsSummary`, `Checklist`, `Deadline`, `RightsGuide`, `WorkflowTemplate`, `Attorney`.

### Shared Directory Structure

```
shared/
  types/
    index.ts          Re-exports all types
    profile.ts        LegalProfile, LegalIssue
    conversation.ts   Message, ChatResponse, ChatRequest
    actions.ts        DemandLetter, RightsSummary, Checklist
    deadline.ts       Deadline, DeadlineStatus
    rights.ts         RightsGuide
    workflow.ts       WorkflowTemplate, WorkflowInstance, WorkflowStep
    attorney.ts       Attorney, ReferralSuggestion
```

Both `web/` and `mobile/` import from this shared directory, ensuring type consistency between platforms.

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

## EAS Build Profiles

CaseMate uses Expo Application Services (EAS) for building and submitting native binaries.

### Build Profiles

| Profile | Use Case | Distribution |
|---------|----------|--------------|
| `development` | Local development with dev client | Internal |
| `preview` | Testing builds for team review | Internal |
| `production` | App Store / Play Store submission | Store |

### Build Commands

```bash
# Development build (includes dev tools)
eas build --profile development --platform ios
eas build --profile development --platform android

# Preview build (for testing)
eas build --profile preview --platform all

# Production build (for store submission)
eas build --profile production --platform ios
eas build --profile production --platform android
```

### Submit to Stores

```bash
eas submit --platform ios      # Submits to App Store Connect
eas submit --platform android  # Submits to Google Play Console
```

Configuration is in `eas.json` at the mobile project root.

---

## Related

- [FRONTEND.md](FRONTEND.md) — Web app architecture (parallel platform)
- [MODELS.md](MODELS.md) — Shared type definitions
- [API.md](API.md) — Backend API consumed by the mobile client
- [SECURITY.md](SECURITY.md) — Auth and JWT handling
