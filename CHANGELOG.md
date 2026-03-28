# Changelog

All notable changes to Lex will be documented in this file.

## [Unreleased]

### Added
- Initial project scaffold with full monorepo structure
- Backend models: LegalProfile, LegalIssue, Conversation, Message, ActionOutput
- Memory injection system: build_system_prompt() with profile + state laws
- Legal classifier: keyword-based classification across 10 legal domains
- State law library: MA, CA, NY, TX, FL with real statute citations
- FastAPI backend with chat, profile, actions, and document routes
- Web frontend: Next.js with chat interface, profile sidebar, onboarding
- Mobile frontend: Expo React Native with chat, profile, cases screens
- Action generators: demand letters, rights summaries, checklists
- Document pipeline: PDF extraction + Claude analysis
- Test suite for memory layer, classifier, and action generators
- CI/CD pipeline with lint + test on push
- 5 Architecture Decision Records
