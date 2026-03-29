# Document Pipeline

The document pipeline handles the flow from file upload through text extraction, Claude analysis, and fact injection into the user's legal profile. It turns static legal documents (leases, notices, contracts) into structured knowledge that improves every future CaseMate response.

## Pipeline Flow

```
Upload (POST /api/documents)
  |
  v
Size check (<= MAX_UPLOAD_BYTES)
  |
  v
Text extraction (extractor.py)
  |
  v
Profile fetch (get_profile)
  |
  v
Claude analysis (analyzer.py)
  |
  v
Return structured analysis to user
  |
  v
Background: fact extraction --> profile update (updater.py)
```

## Step 1: Upload Endpoint

`POST /api/documents` in `backend/main.py` (line 567). Accepts a `file: UploadFile` with JWT authentication. Rate-limited to 3 requests per 60 seconds via `_documents_rate_limit`.

**Size check**: File bytes are read into memory and compared against `MAX_UPLOAD_BYTES`. Files exceeding the limit return HTTP 413.

**Auth**: `user_id` is extracted from the Supabase JWT via `verify_supabase_jwt` dependency.

## Step 2: Text Extraction

`extract_text()` in `backend/documents/extractor.py` routes by MIME type:

| Content Type | Handler | Method |
|---|---|---|
| `application/pdf` | `_extract_pdf()` | `pdfplumber.open()` on `io.BytesIO(file_bytes)`, iterates pages, concatenates with double-newline separators |
| `text/*` | `_extract_text()` | UTF-8 decode via `bytes.decode("utf-8")` |
| `image/*` | `_extract_image_placeholder()` | Returns placeholder string (OCR not yet implemented) |

Any other MIME type raises `ValueError` with a message listing supported types. The endpoint catches this and returns HTTP 400.

**PDF extraction** uses `pdfplumber` (lazy-imported). Each page's text is extracted individually. Empty pages are skipped. Page count and character count are logged.

**Error handling**: `RuntimeError` if pdfplumber fails; `ImportError` if pdfplumber is not installed (with an install hint). `ValueError` for UTF-8 decode failures on text files.

## Step 3: Claude Analysis

`analyze_document()` in `backend/documents/analyzer.py` sends the extracted text plus the user's profile to Claude for structured analysis.

**Analysis prompt** (`ANALYSIS_PROMPT`) instructs Claude to return JSON with four keys:
- `document_type` -- Classification (lease agreement, demand letter, court notice, etc.)
- `key_facts` -- Important facts extracted from the document
- `red_flags` -- Concerning clauses, missing protections, potential issues
- `summary` -- Plain-English 2-3 paragraph summary tailored to the user

**Prompt rules** require Claude to:
1. Identify unenforceable clauses under the user's state law
2. Flag deadlines and time-sensitive requirements
3. Note contradictions with the user's known legal facts
4. Cite section numbers from the document

**Profile context**: The user's `LegalProfile` is serialized via `profile.to_context_string()` and prepended to the document text in the user message as `USER PROFILE:\n{context}\n\nDOCUMENT TEXT:\n{text}`.

**Model**: `claude-sonnet-4-20250514` with `max_tokens=4096`. Decorated with `@retry_anthropic` for automatic retry with exponential backoff.

**Response parsing**: The first `TextBlock` from Claude's response is parsed as JSON. Missing expected keys are backfilled with defaults (`"unknown"` for document_type, empty list for key_facts/red_flags, raw response text for summary). `JSONDecodeError` raises `RuntimeError`.

## Step 4: Fact Injection

After the analysis is returned to the user, the background task system runs `update_profile_from_conversation()` (see `docs/MEMORY_SYSTEM.md` for full details). Facts extracted from the document analysis conversation are merged into the user's `legal_facts` list using the append-only, deduplicated merge strategy.

This means a user who uploads a lease agreement gets the key terms automatically added to their profile. Future chat responses will reference those terms without the user having to repeat them.

## Error Boundaries

Each stage has independent error handling:

| Stage | Failure Mode | Response |
|-------|---|---|
| Size check | File too large | HTTP 413 |
| Extraction | Unsupported type | HTTP 400 |
| Extraction | PDF parse failure | HTTP 500 (RuntimeError) |
| Profile fetch | Not found | HTTP 404 |
| Analysis | Claude API error | HTTP 500 with logged error |
| Analysis | JSON parse failure | HTTP 500 (RuntimeError) |
| Background fact extraction | Any exception | Logged and swallowed (never crashes) |

## Current Limitations

- **No OCR**: Image uploads return a placeholder message asking the user to upload as PDF or describe the contents manually.
- **No storage**: Uploaded files are analyzed in memory but not persisted to Supabase Storage. Document references in `LegalProfile.documents` must be populated separately.
- **Single-file**: The endpoint accepts one file per request. Multi-document uploads require multiple calls.

## Relationship to Other Systems

- **Memory System** (`docs/MEMORY_SYSTEM.md`): Extracted facts flow into `legal_facts` via the background updater
- **Legal Domains** (`docs/LEGAL_DOMAINS.md`): Analysis is domain-aware through the user's profile context, which includes active issues classified by domain
