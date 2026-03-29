# Export — PDF & Email Delivery

> How CaseMate generates branded PDF documents and delivers them via email.

---

## Overview

When CaseMate generates a demand letter, rights summary, or checklist, users can export it as a branded PDF or have it emailed directly. The export module handles document formatting and delivery.

---

## PDF Generation

**Source:** `backend/export/pdf_generator.py`

### `CaseMatePDF` Class

Extends `fpdf2.FPDF` with CaseMate branding:

- **Header:** "CaseMate" title + generation date + user's display name + blue separator line
- **Footer:** Italicized gray disclaimer: *"This is legal information, not legal advice. CaseMate is not a law firm."* + page number

### Document Types

#### `generate_demand_letter_document(letter: DemandLetter, user_name: str) -> bytes`

Produces a PDF with:
- Title: "Demand Letter"
- Full letter body text
- "Legal Citations" section listing each cited statute

#### `generate_rights_document(summary: RightsSummary, user_name: str) -> bytes`

Produces a PDF with:
- Title: "Your Rights Summary"
- Multi-paragraph explanation text
- "Your Key Rights" section with bullet points for each right

#### `generate_checklist_document(checklist: Checklist, user_name: str) -> bytes`

Produces a PDF with:
- Title: "Action Checklist"
- Each item displayed with checkbox format: `[ ] Item text`
- Associated deadline shown below each item: `Deadline: YYYY-MM-DD`

#### `generate_text_document(title: str, content: str, sections: dict | None, user_name: str) -> bytes`

Generic document generator for custom text with optional named sections.

### PDF Output

All functions return `bytes` — the raw PDF content ready to be served as a file download or attached to an email. The Content-Type is `application/pdf`.

---

## Email Delivery

**Source:** `backend/export/email_sender.py`

### `send_document_email()`

```python
async def send_document_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_bytes: bytes,
    attachment_filename: str,
) -> bool:
```

Sends a PDF attachment via SMTP:

1. Checks SMTP configuration — if not set, logs a warning and returns `False` (feature disabled gracefully)
2. Builds an `EmailMessage` with the body text
3. Attaches the PDF bytes with the given filename
4. Connects via `smtplib.SMTP` with `starttls()` and `login()`
5. Sends the email
6. Returns `True` on success, `False` on `SMTPException` (logs error, never raises)

### SMTP Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | — | SMTP server hostname (e.g., `smtp.gmail.com`) |
| `SMTP_PORT` | `587` | SMTP port (587 for TLS) |
| `SMTP_USER` | — | SMTP login username |
| `SMTP_PASS` | — | SMTP login password or app password |
| `SMTP_FROM` | `support@casemate.ai` | Sender email address |

If `SMTP_HOST` or `SMTP_USER` is not set, email delivery is silently disabled. The rest of the app continues to work — users can still download PDFs directly.

---

## API Endpoints

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|------------|-------------|
| `POST` | `/api/export/document` | JWT | 5/min | Generate and download a PDF |
| `POST` | `/api/export/email` | JWT | 3/min | Generate PDF and email it |

### `POST /api/export/document`

**Request:**
```json
{
  "document_type": "demand_letter",
  "content_id": "..."
}
```

**Response:** PDF file download (`application/pdf`)

### `POST /api/export/email`

**Request:**
```json
{
  "document_type": "demand_letter",
  "content_id": "...",
  "to_email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Document emailed to user@example.com"
}
```

---

## Supported Document Types

| Type | Generator Function | Source Model |
|------|-------------------|--------------|
| `demand_letter` | `generate_demand_letter_document()` | `DemandLetter` |
| `rights_summary` | `generate_rights_document()` | `RightsSummary` |
| `checklist` | `generate_checklist_document()` | `Checklist` |
| `custom` | `generate_text_document()` | Raw text + sections |

---

## Related

- [ACTIONS.md](ACTIONS.md) — How action outputs are generated before export
- [MODELS.md](MODELS.md) — DemandLetter, RightsSummary, Checklist models
- [API.md](API.md) — Complete API reference
- [SECURITY.md](SECURITY.md) — How SMTP credentials are managed
