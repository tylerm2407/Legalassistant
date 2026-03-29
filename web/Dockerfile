# web/Dockerfile — Production Next.js frontend for CaseMate
#
# Multi-stage build:
#   Stage 1 (deps):    installs node_modules
#   Stage 2 (builder): builds the Next.js production bundle
#   Stage 3 (runtime): runs the standalone Next.js server as non-root
#
# Build:  docker build -t casemate-web ./web
# Run:    docker run -p 3000:3000 --env-file .env casemate-web

# ---------------------------------------------------------------------------
# Stage 1: Dependencies
# ---------------------------------------------------------------------------
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

# ---------------------------------------------------------------------------
# Stage 2: Builder — produce the Next.js production build
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build-time env vars (public keys only — no secrets)
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_KEY

RUN npm run build

# ---------------------------------------------------------------------------
# Stage 3: Runtime — minimal production image
# ---------------------------------------------------------------------------
FROM node:20-alpine AS runtime

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nextjs && \
    adduser --system --uid 1001 nextjs

# Copy only the build output and production deps
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nextjs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nextjs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
