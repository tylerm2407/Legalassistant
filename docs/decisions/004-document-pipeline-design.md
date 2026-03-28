# ADR 004 — Document pipeline design

**Date:** 2026-03-27
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

Users can upload legal documents — leases, court letters, demand notices, employment agreements, medical bills — and CaseMate reads them, extracts key legal facts into the user's profile, and makes the document available as context for all future conversations. Documents become permanent memory.

---

## Context

Legal situations almost always involve documents. A tenant's dispute with a landlord involves a lease. An employment dispute involves an offer letter or non-compete. A debt collection issue involves a dunning letter. A small claims case involves a contract.

Without document ingestion, users have to manually type out the relevant clauses or facts from their documents — a high-friction, error-prone process. With it, they upload once and every future conversation is informed by what the document actually says.

The document pipeline transforms a PDF or photo into structured legal facts in the user's profile. A lease becomes: "Month-to-month tenancy, $1,850/month, landlord responsible for heat and hot water, 30-day notice required." Those facts are then available in every subsequent chat without the user re-stating them.

---

## The implementation

### Pipeline stages

```
User uploads file (PDF or image)
        │
        ▼
Supabase Storage (raw file stored, path saved to user profile)
        │
        ▼
Text Extraction
  PDFs  → PyPDF2 (text-based PDFs)
  Images → pytesseract OCR (photos of documents)
        │
        ▼
Claude Analysis
  - Document type classification
  - Key clause extraction
  - Legal red flags identification
  - Fact extraction for user profile
        │
        ▼
Profile Update
  - Extracted facts appended to legal_facts[]
  - Document reference added to documents[]
  - Active issues created if document reveals ongoing dispute
        │
        ▼
Response to user
  - Document summary
  - Key findings
  - Red flags highlighted
  - Offer to ask questions about the document
```

### Document analysis prompt

```
You are analyzing a legal document uploaded by a user.

USER PROFILE CONTEXT:
{profile.to_context_string()}

DOCUMENT TEXT:
{extracted_text}

Analyze this document and return JSON with:

1. document_type: What kind of document this is
   (lease, employment_agreement, demand_letter, court_notice, contract, etc.)

2. key_facts: List of specific factual claims from the document
   that are relevant to the user's legal situation.
   Write each fact as a clear, standalone statement.
   Example: "Landlord is responsible for all appliance repairs under Section 8"

3. red_flags: List of clauses, terms, or statements that may be
   problematic, unenforceable, or contrary to the user's interests.
   Cite the specific language and explain why it is a red flag.

4. user_rights: Rights the document establishes OR rights the document
   may be attempting to waive (illegal waivers should be called out).

5. summary: 3-sentence plain-English summary of what this document is
   and what the user needs to know about it.

Be specific. Cite exact language from the document where relevant.
Do not give generic information — analyze THIS document for THIS user.
```

### Supported file types

| Type | Extraction method | Notes |
|------|------------------|-------|
| PDF (text-based) | PyPDF2 | Fast, high accuracy |
| PDF (scanned) | pytesseract | Slower, accuracy depends on scan quality |
| JPEG/PNG/HEIC | pytesseract | For photos of paper documents |
| DOCX | python-docx | For Word documents |

File size limit: 10MB. Pages extracted: up to 50 (covers most legal documents).

---

## Alternatives considered

**No document upload — text input only**
Rejected. Legal situations almost always involve documents. Requiring users to manually transcribe document content is high friction and error-prone. Document upload is table stakes for a legal assistant.

**Store documents as vector embeddings for semantic search**
Considered for future version. For MVP, extracting structured facts into the profile is faster to build and more directly useful than building a RAG system. Semantic search over document content can be layered in once the core pipeline is working.

**Client-side OCR (process in browser)**
Rejected. Client-side OCR with Tesseract.js is slow and produces lower quality results than server-side pytesseract. Server-side also keeps the document processing logic centralized and easier to improve.

**Third-party document AI service (e.g., AWS Textract)**
Considered. Rejected for MVP due to cost, additional API key complexity, and vendor dependency. PyPDF2 + pytesseract is sufficient for common document types and completely free.

**Store full document text in conversation context**
Rejected. Full document text would consume too much context window for every conversation. Extracting facts into the profile is more efficient — only the relevant extracted facts are injected, not 20 pages of lease text.

---

## Privacy and security

Legal documents contain highly sensitive personal information. Specific protections:

**Storage:** Documents stored in Supabase Storage with Row Level Security — users can only access their own documents. Storage paths are never exposed in API responses, only served via signed URLs with expiry.

**Processing:** Document text is sent to the Anthropic API for analysis. Users consent to this in onboarding. Document text is not used by Anthropic for model training (API usage, not Claude.ai usage).

**Retention:** Documents are retained for the life of the account and deleted when the account is deleted. Users can delete individual documents from their profile.

**No cross-user contamination:** Each document is isolated to the uploading user's profile. Extracted facts are scoped to the individual user_id.

---

## Consequences

**Positive:**
- Users upload a document once and it informs every future conversation
- Red flag detection adds immediate value — catches problematic lease clauses, illegal contract terms, FDCPA violations in debt letters
- The document becomes part of the user's permanent legal memory
- Significantly reduces conversation friction — no manual fact transcription

**Negative:**
- OCR accuracy varies with scan quality — badly photographed documents may extract poorly
- Adds Supabase Storage dependency and file handling complexity
- Processing time varies (1–5 seconds for PDFs, 5–15 seconds for OCR)
- pytesseract requires server-side installation (handled by Docker/Railway)

---

## Status

Accepted. Implemented in `backend/documents/extractor.py` and `backend/documents/analyzer.py`.
