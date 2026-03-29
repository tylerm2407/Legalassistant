# Frontend — Web App Architecture

> Next.js 14 App Router + TypeScript + Tailwind CSS

---

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 14 (App Router) | SSR, file-based routing, API routes |
| TypeScript | Strict mode | Type safety across all components |
| Tailwind CSS | 3.x | Utility-first styling |
| Supabase JS | ^2.39 | Client-side auth + realtime |
| React | 18 | UI framework |

---

## Page Structure

```
web/app/
├── page.tsx              → Marketing landing page (redirects to /auth if logged in)
├── api/waitlist/route.ts → Waitlist signup API (Mailchimp + Supabase)
├── auth/page.tsx         → Login / signup
├── onboarding/page.tsx   → 5-question legal intake wizard
├── chat/page.tsx         → Main chat interface (3-panel layout)
├── profile/page.tsx      → Legal profile viewer/editor
├── attorneys/page.tsx    → Attorney search and referral
├── deadlines/page.tsx    → Deadline tracking dashboard
├── rights/page.tsx       → Know Your Rights library browser
├── workflows/page.tsx    → Guided legal workflow page
└── subscription/page.tsx → Subscription management
```

### Page Descriptions

| Page | Auth Required | Description |
|------|---------------|-------------|
| `/` | No | Marketing landing with value proposition and waitlist signup |
| `/auth` | No | Supabase email/password auth (login + signup) |
| `/onboarding` | Yes | 5-step intake: name, state, housing, employment, family status |
| `/chat` | Yes | Primary interface — 3-panel layout with sidebar + history + chat |
| `/profile` | Yes | View and edit legal profile, see extracted facts |
| `/attorneys` | Yes | Search attorneys by state and legal area |
| `/deadlines` | Yes | View, manage, and dismiss tracked deadlines |
| `/rights` | Yes | Browse 19 Know Your Rights guides by domain |
| `/workflows` | Yes | Start and continue guided legal workflows |
| `/subscription` | Yes | Manage subscription tier, view billing |

---

## Component Inventory

### Chat Components

| Component | File | Description |
|-----------|------|-------------|
| `ChatInterface` | `components/ChatInterface.tsx` | Main conversation UI with message input, streaming response display, and memory indicator showing when profile was last updated |
| `ConversationHistory` | `components/ConversationHistory.tsx` | Left panel listing past conversations with preview text, legal area tags, and timestamps. Click to load. |
| `LegalProfileSidebar` | `components/LegalProfileSidebar.tsx` | Right panel showing the user's live profile — state, housing, employment, family, active issues, and extracted legal facts. Updates after every conversation. |
| `CaseHistory` | `components/CaseHistory.tsx` | Active issues timeline showing each legal dispute with status, dates, and notes |

### Action Components

| Component | File | Description |
|-----------|------|-------------|
| `ActionGenerator` | `components/ActionGenerator.tsx` | UI for generating demand letters, rights summaries, and checklists. Shows output inline with export/email options. |
| `DocumentUpload` | `components/DocumentUpload.tsx` | File upload with drag-and-drop, progress indicator, and fact extraction preview showing what CaseMate learned from the document |

### Onboarding & Auth

| Component | File | Description |
|-----------|------|-------------|
| `OnboardingFlow` | `components/OnboardingFlow.tsx` | 5-step wizard component with progress bar, validation, and Supabase profile creation on completion |
| `WaitlistForm` | `components/WaitlistForm.tsx` | Email signup form for pre-launch waitlist (connects to Mailchimp + Supabase) |

### Feature Components

| Component | File | Description |
|-----------|------|-------------|
| `DeadlineDashboard` | `components/DeadlineDashboard.tsx` | Deadline list with status management (complete, dismiss), sorted by date |
| `AttorneyCard` | `components/AttorneyCard.tsx` | Attorney referral display with rating, specializations, cost, contact links, and match reason |
| `WorkflowWizard` | `components/WorkflowWizard.tsx` | Step-by-step workflow UI with progress tracking and step completion |
| `RightsGuide` | `components/RightsGuide.tsx` | Rights guide detail display with sections for rights, steps, deadlines, and common mistakes |

---

## State Management

CaseMate uses **React hooks only** — no external state library (Redux, Zustand, etc.).

- `useState` for local component state (form inputs, loading states, UI toggles)
- `useEffect` for data fetching on mount and auth state changes
- Props for parent-to-child data flow
- API calls via `web/lib/api.ts` for all server communication

This is intentional — the app's state is primarily server-side (profiles and conversations live in Supabase), so client-side state management complexity is not justified.

---

## API Client

**Source:** `web/lib/api.ts`

### Configuration

- `API_BASE` reads from `NEXT_PUBLIC_API_URL` environment variable, falls back to `"/api"`
- All requests include `Content-Type: application/json` and `Authorization: Bearer <jwt>`

### Auth Headers

```typescript
async function getAuthHeaders(): Promise<Headers> {
    const { data: { session } } = await supabase.auth.getSession();
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session?.access_token}`,
    };
}
```

### Retry Logic

`fetchWithRetry()` retries up to **3 times** on 5xx errors or network failures:

- Attempt 1: immediate
- Attempt 2: after 1s
- Attempt 3: after 2s
- 4xx errors return immediately (no retry — these are client errors)

### API Methods

The `api` object exports typed methods for every backend endpoint:

```typescript
const api = {
    chat(message: string, conversationId?: string): Promise<ChatResponse>,
    getProfile(): Promise<LegalProfile>,
    createProfile(data: ProfileRequest): Promise<LegalProfile>,
    generateLetter(context: string): Promise<DemandLetter>,
    generateRights(context: string): Promise<RightsSummary>,
    generateChecklist(context: string): Promise<Checklist>,
    listDeadlines(status?: string): Promise<Deadline[]>,
    searchAttorneys(state: string, legalArea?: string): Promise<Attorney[]>,
    // ... 60+ methods covering all endpoints
};
```

---

## Auth Flow

1. User visits `/auth` → signs up or logs in via Supabase email/password
2. Supabase client stores session in browser (cookie/localStorage)
3. On authenticated pages, `useEffect` checks `supabase.auth.getSession()`
4. If no session → redirect to `/auth`
5. `onAuthStateChange` listener handles token refresh and sign-out events
6. Every API call attaches the JWT via `getAuthHeaders()`
7. Backend verifies JWT via `verify_supabase_jwt()` dependency

---

## Layout — 3-Panel Chat

The chat page uses a responsive 3-panel layout:

```
┌─────────────────┬───────────────────────┬──────────────────┐
│  Conversation   │                       │  Legal Profile   │
│  History        │    Chat Area          │  Sidebar         │
│                 │                       │                  │
│  - Conv 1       │  [User message]       │  State: MA       │
│  - Conv 2       │  [CaseMate response]  │  Housing: Renter │
│  - Conv 3       │  [User message]       │  Issues: 1       │
│  ...            │  [CaseMate response]  │  Facts: 8        │
│                 │                       │                  │
│                 │  ┌──────────────────┐  │                  │
│                 │  │ Type message...  │  │                  │
│                 │  └──────────────────┘  │                  │
└─────────────────┴───────────────────────┴──────────────────┘
```

### Responsive behavior

- **Desktop (1024px+):** Full 3-panel layout
- **Tablet (768px–1023px):** Chat + sidebar, conversation history in drawer
- **Mobile (<768px):** Single panel with tab/drawer navigation

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_APP_URL` | Frontend URL (e.g., `http://localhost:3000`) |
| `NEXT_PUBLIC_API_URL` | Backend API URL (e.g., `http://localhost:8000/api`) |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase public/anon key |

---

## Related

- [API.md](API.md) — Backend API that the frontend calls
- [MOBILE.md](MOBILE.md) — React Native mobile app (shares types with web)
- [MODELS.md](MODELS.md) — TypeScript type definitions matching backend models
- [SECURITY.md](SECURITY.md) — Auth and JWT handling
