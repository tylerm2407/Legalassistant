# Extending CaseMate

> How to add new legal domains, states, action types, workflows, rights guides, and API endpoints.

---

## Adding a New Legal Domain

A legal domain is a category of law (e.g., `landlord_tenant`, `immigration`). Adding one touches 5 areas:

### 1. Classifier keywords

**File:** `backend/legal/classifier.py`

Add a new entry to `DOMAIN_KEYWORDS`:

```python
"new_domain": [
    "keyword1", "keyword2",           # Single words (1x weight)
    "multi word phrase",               # Phrases get 3x boost (PHRASE_BOOST)
    "another specific phrase",
],
```

Choose 15-20 keywords. Include both common terms and legal-specific phrases. Multi-word phrases are more specific and should be preferred for accuracy.

### 2. Domain module

**Create:** `backend/legal/areas/new_domain.py`

Export three items:

```python
DOMAIN_GUIDANCE: str = """
Instructions for Claude when responding to questions in this domain.
Include response patterns, what to emphasize, common pitfalls.
"""

KEY_STATUTES: dict[str, str] = {
    "Statute Name §Section": "Plain-English explanation of what this statute means",
}

COMMON_QUESTIONS: list[str] = [
    "Can my employer do X?",
    "What are my rights when Y happens?",
]
```

### 3. State law entries

**Files:** All 6 regional files in `backend/legal/states/` + `federal.py`

Add the new domain key to every state:

```python
# In each state's dict:
"XX": {
    # ... existing domains ...
    "new_domain": "State XX Code §XX-XX governs... [real statute citations]",
}
```

And add federal defaults:

```python
# In federal.py:
"federal_defaults": {
    "new_domain": "Federal law under [Act Name] provides...",
}
```

### 4. Rights guides

**File:** `backend/knowledge/rights_library.py`

Add at least one `RightsGuide` for the new domain (see [RIGHTS_LIBRARY.md](RIGHTS_LIBRARY.md) for the model).

### 5. Tests

**Files:** `tests/test_legal_classifier.py`, `tests/test_memory_injector.py`

- Add classifier tests verifying keywords map to the new domain
- Add injector tests verifying state law injection works for the new domain

---

## Adding a New State

If somehow a state is missing from the database:

### 1. Determine the regional file

| Region | File | States |
|--------|------|--------|
| Northeast | `states/northeast.py` | MA, NY, CT, NJ, PA, ME, NH, VT, RI |
| Southeast | `states/southeast.py` | FL, GA, VA, NC, SC, AL, MS, TN, KY, WV, MD, DE, LA, AR |
| Midwest | `states/midwest.py` | IL, OH, MI, IN, WI, MN, IA, MO, KS, NE, ND, SD |
| South Central | `states/south_central.py` | TX, OK |
| West | `states/west.py` | CA, WA, OR, CO, AZ, NV, UT, NM, ID, MT, WY, HI, AK |

### 2. Add entries for all 10 domains

```python
"XX": {
    "landlord_tenant": "...",
    "employment_rights": "...",
    "consumer_protection": "...",
    "debt_collections": "...",
    "small_claims": "...",
    "contract_disputes": "...",
    "traffic_violations": "...",
    "family_law": "...",
    "criminal_records": "...",
    "immigration": "...",
}
```

Every entry must include **real statute citations** — not generic text.

### 3. Verify

Run `make test` to ensure the classifier and injector work with the new state.

---

## Adding a New Action Type

Action types are generators that produce structured legal documents (like demand letters).

### 1. Define the output model

**File:** `backend/models/action_output.py`

```python
class NewActionOutput(BaseModel):
    """Docstring explaining what this action produces."""
    field1: str
    field2: list[str]
    # ... all fields typed, no Any
```

### 2. Create the generator

**Create:** `backend/actions/new_generator.py`

```python
from backend.utils.retry import retry_anthropic
from backend.utils.client import get_anthropic_client
from backend.models.legal_profile import LegalProfile
from backend.models.action_output import NewActionOutput
from backend.legal.classifier import classify_legal_area
from backend.legal.state_laws import STATE_LAWS

@retry_anthropic
async def generate_new_action(profile: LegalProfile, context: str) -> NewActionOutput:
    """Docstring."""
    legal_area = classify_legal_area(context)
    state_context = STATE_LAWS.get(profile.state, {}).get(legal_area, "")
    federal_context = STATE_LAWS.get("federal_defaults", {}).get(legal_area, "")

    client = get_anthropic_client()
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="...",  # Include profile, state laws, generation instructions
        messages=[{"role": "user", "content": context}],
    )

    # Parse JSON response into NewActionOutput
    ...
```

### 3. Add the API endpoint

**File:** `backend/main.py`

```python
@app.post("/api/actions/new-action")
async def create_new_action(
    request: ActionRequest,
    user_id: str = Depends(verify_supabase_jwt),
    _: None = Depends(rate_limit(max_requests=5, window_seconds=60)),
) -> NewActionOutput:
    profile = await get_profile(user_id)
    return await generate_new_action(profile, request.context)
```

### 4. Add the UI trigger

**File:** `web/components/ActionGenerator.tsx`

Add the new action type to the generator's dropdown/button options. Add the API method to `web/lib/api.ts`.

### 5. Add PDF export support

**File:** `backend/export/pdf_generator.py`

Add a `generate_new_action_document()` function to the `CaseMatePDF` class.

### 6. Write tests

**File:** `tests/test_action_generators.py`

Test the generator with a mock profile and mock Claude response.

---

## Adding a New Workflow Template

Workflows are guided, multi-step legal processes.

### 1. Define the template

**File:** `backend/workflows/templates/definitions.py`

```python
WorkflowTemplate(
    id="unique_template_id",
    domain="legal_domain",
    title="Workflow Title",
    description="What this workflow helps with",
    steps=[
        WorkflowStep(title="Step 1", description="What to do", guidance="Detailed instructions"),
        WorkflowStep(title="Step 2", ...),
        # ...
    ],
    estimated_duration="2-4 weeks",
)
```

### 2. Register the template

Add it to the `WORKFLOW_TEMPLATES` list in the same file. The API automatically serves it — no route changes needed.

### 3. Test

Add verification in `tests/test_workflow_templates.py`.

---

## Adding a New Rights Guide

See [RIGHTS_LIBRARY.md](RIGHTS_LIBRARY.md) → "How to Add a New Guide" section.

Short version:

1. Define a `RightsGuide` object in `backend/knowledge/rights_library.py`
2. Add it to the `RIGHTS_GUIDES` list
3. Test in `tests/test_rights_library.py`

---

## Adding a New API Endpoint

### Checklist

1. **Route:** Add in `backend/main.py` with HTTP method and path
2. **Auth:** Apply `Depends(verify_supabase_jwt)` for authenticated endpoints
3. **Rate limit:** Apply `Depends(rate_limit(max_requests=N, window_seconds=60))`
4. **Request model:** Define Pydantic model for request body (if POST/PATCH)
5. **Response model:** Define Pydantic model for response — annotate the return type
6. **No `Any`:** Every field must be explicitly typed
7. **Docstring:** Every endpoint function gets a docstring
8. **Structured logging:** Log key events with `user_id`
9. **Tests:** Add tests in `tests/test_api_endpoints.py`
10. **API docs:** Update `docs/API.md` with the new endpoint

### Example

```python
@app.get("/api/new-resource")
async def get_new_resource(
    user_id: str = Depends(verify_supabase_jwt),
    _: None = Depends(rate_limit(max_requests=10, window_seconds=60)),
) -> NewResourceResponse:
    """Fetches the new resource for the authenticated user."""
    log.info("new_resource_requested", user_id=user_id)
    # ... implementation
```

---

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Legal area module | `backend/legal/areas/{domain}.py` | `areas/landlord_tenant.py` |
| State laws | `backend/legal/states/{region}.py` | `states/northeast.py` |
| Action generator | `backend/actions/{type}_generator.py` | `actions/letter_generator.py` |
| Pydantic model | `backend/models/{category}.py` | `models/action_output.py` |
| Utility | `backend/utils/{function}.py` | `utils/rate_limiter.py` |
| Test | `tests/test_{module}.py` | `tests/test_memory_injector.py` |
| ADR | `docs/decisions/NNN-{title}.md` | `docs/decisions/001-memory-as-differentiator.md` |

---

## Module Patterns

Every backend module follows these conventions:

1. **Imports** at top — stdlib, then third-party, then internal
2. **Constants** after imports (UPPER_CASE)
3. **Pydantic models** if needed (in `models/` or local)
4. **Functions** — all public functions have type annotations and docstrings
5. **No bare except** — always catch specific exceptions
6. **Structured logging** — use `get_logger(__name__)`, always include `user_id`
7. **Retry on API calls** — `@retry_anthropic` on all Anthropic calls

---

## Related

- [ACTIONS.md](ACTIONS.md) — Existing action generators
- [LEGAL_KNOWLEDGE_BASE.md](LEGAL_KNOWLEDGE_BASE.md) — State law and classifier system
- [RIGHTS_LIBRARY.md](RIGHTS_LIBRARY.md) — Rights guide system
- [WORKFLOWS.md](WORKFLOWS.md) — Workflow engine and templates
- [API.md](API.md) — Full API reference
- [TESTING.md](TESTING.md) — How to write tests
