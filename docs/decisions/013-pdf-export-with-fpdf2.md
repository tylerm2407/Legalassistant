# ADR 013 — fpdf2 for branded PDF generation

**Date:** 2026-03-28
**Status:** Accepted
**Deciders:** CaseMate founding team

---

## Decision

PDF generation for demand letters, rights summaries, checklists, and custom documents uses fpdf2 (the `FPDF` class) with a custom `CaseMatePDF` subclass that applies consistent branding. The implementation lives in `backend/export/pdf_generator.py`.

---

## Context

CaseMate generates four types of exportable documents: demand letters, rights summaries, next-steps checklists, and custom legal documents. These are served via `POST /api/export/document` as downloadable PDFs and can also be emailed via `POST /api/export/email`. The PDF output is a key demo feature — the demand letter generation is the climax of the 2-minute-45-second demo script.

The PDF needs to look professional and branded: a CaseMate header with the generation date and user name, consistent typography, legal citation formatting, and a disclaimer footer. It does not need complex layouts, images, charts, or interactive elements.

---

## The implementation

`backend/export/pdf_generator.py` defines a `CaseMatePDF` class that subclasses `FPDF` from fpdf2. It overrides `header()` and `footer()` to apply CaseMate branding on every page:

- **Header:** "CASEMATE - AI Legal Assistant" in blue-700 Helvetica Bold 16pt, generation date, optional user name, and a blue separator line
- **Footer:** A gray separator line followed by the legal disclaimer in Helvetica Italic 7pt

The class provides three helper methods: `add_title()` for section headings in gray-900 Bold 14pt, `add_body()` for body text in gray-700 Regular 10pt, and `add_section()` for subsection headings in blue Bold 11pt.

Four generator functions handle specific document types:

- `generate_demand_letter_document()` — Letter body + legal citations section
- `generate_rights_document()` — Summary text + numbered key rights list
- `generate_checklist_document()` — Checkbox-style items with optional deadline annotations
- `generate_text_document()` — Generic document with optional sections (used as the base for all others)

All generators return `bytes` that are sent directly as `application/pdf` responses in `backend/main.py` with `Content-Disposition: attachment` headers.

---

## Alternatives considered

**ReportLab**
Considered. ReportLab is more powerful (supports advanced layouts, vector graphics, and Platypus for complex document flow) but is significantly heavier. The CaseMate PDFs are linear text documents — header, body, citations, footer. fpdf2 handles this without the learning curve or dependency weight of ReportLab.

**WeasyPrint (HTML-to-PDF)**
Considered. Would allow designing PDFs as HTML/CSS templates, which is more familiar to web developers. Rejected because WeasyPrint depends on system-level libraries (Cairo, Pango, GDK-PixBuf) that complicate deployment. fpdf2 is pure Python with zero system dependencies.

**wkhtmltopdf / Puppeteer**
Rejected. Both require a headless browser or WebKit binary, which is excessive for generating text documents. Adds deployment complexity and potential security surface area.

**Client-side PDF generation (jsPDF)**
Rejected. Would move PDF generation to the frontend, making the export unavailable from the mobile app and the email export endpoint. Server-side generation keeps the logic centralized and testable.

---

## Consequences

**Positive:**
- Pure Python — no system dependencies, installs with `pip install fpdf2`
- Consistent branding across all document types via the `CaseMatePDF` subclass
- Small output files — text-only PDFs are typically 10–50KB
- Disclaimer footer appears on every page automatically
- Personalized with user name and generation date from the profile

**Negative:**
- Limited typographic control — fpdf2 uses built-in fonts (Helvetica, Courier, Times) without custom font embedding in our current implementation
- No support for complex layouts (tables, multi-column, embedded images) without significant additional code
- Unicode support requires explicit font registration — special characters in legal text may render incorrectly with default fonts
- No PDF/A compliance for archival legal documents

---

## Status

Accepted. fpdf2 meets the current requirements for professional-looking text-based legal documents. If future features require complex layouts (e.g., court form filling, table-based documents), ReportLab or a template-based approach can be evaluated as an upgrade path.
