# Workflows

The workflow system provides guided step-by-step legal processes. Users start a workflow from a template, then advance through steps as they complete real-world actions. Progress is persisted to Supabase.

## Architecture

Two modules:
- `backend/workflows/engine.py` -- Data models, Supabase CRUD, step advancement logic
- `backend/workflows/templates/definitions.py` -- Pre-built template definitions

## Data Models

### `WorkflowTemplate`

The static definition of a workflow. Fields: `id`, `title`, `description`, `domain` (legal area), `estimated_time`, and `steps` (ordered list of `WorkflowStep`).

### `WorkflowStep`

A single step within a template or instance. Fields:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `str` | Step identifier (e.g., `"review_notice"`) |
| `title` | `str` | Short title |
| `explanation` | `str` | Detailed instructions for the user |
| `required_documents` | `list[str]` | Documents needed for this step |
| `tips` | `list[str]` | Practical advice |
| `deadlines` | `list[str]` | Time-sensitive requirements |
| `status` | `StepStatus` | Completion state |

### `WorkflowInstance`

A user's in-progress copy of a template. Adds `user_id`, `template_id`, `current_step` (0-based index), overall `status`, and timestamps. Steps are deep-copied from the template via `model_copy()` so each user's progress is independent.

### `WorkflowStepUpdateRequest`

Request body for the step update endpoint: `step_index` (int) and `status` (StepStatus).

## StepStatus Lifecycle

```
NOT_STARTED --> IN_PROGRESS --> COMPLETED
                            \-> SKIPPED
```

`StepStatus` is a `StrEnum` with four values: `not_started`, `in_progress`, `completed`, `skipped`.

When a workflow starts (`start_workflow()`), the first step is automatically set to `IN_PROGRESS`. All other steps remain `NOT_STARTED`.

## Auto-Advancement

`update_workflow_step()` handles step transitions. When a step is marked `COMPLETED`:

1. The engine checks if a next step exists (`step_index + 1 < len(steps)`)
2. If yes: `current_step` advances and the next step's status is set to `IN_PROGRESS`
3. If no (last step completed): the entire workflow's `status` is set to `COMPLETED`

Steps can also be set to `SKIPPED`, which does not trigger auto-advancement. The caller must explicitly advance past skipped steps.

## Template Inventory

Five templates defined in `backend/workflows/templates/definitions.py`:

| Template ID | Title | Domain | Steps | Est. Time |
|---|---|---|---|---|
| `fight_eviction` | Fight an Eviction | landlord_tenant | 7 | 2-6 weeks |
| `file_small_claims` | File a Small Claims Case | small_claims | 5 | 4-8 weeks |
| `expunge_record` | Get a Record Expunged | criminal_records | 6 | 2-6 months |
| `file_wage_complaint` | File a Wage Complaint | employment_rights | 4 | 2-6 months |
| `fight_traffic_ticket` | Fight a Traffic Ticket | traffic_violations | 4 | 2-6 weeks |
| `create_basic_will` | Create a Basic Will | family_law | 5 | 1-2 weeks |

Each step includes `required_documents`, `tips`, and `deadlines` specific to that stage of the legal process.

## Template Lookup Functions

In `backend/workflows/templates/definitions.py`:
- `get_all_templates()` -- Returns the full `WORKFLOW_TEMPLATES` list
- `get_template_by_id(template_id)` -- Returns a single template or `None`
- `get_templates_by_domain(domain)` -- Filters templates by legal domain

## API Endpoints

All workflow endpoints in `backend/main.py` require JWT authentication.

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| `GET` | `/api/workflows/templates` | `list_workflow_templates()` | List all available templates |
| `POST` | `/api/workflows` | `start_user_workflow()` | Start a new workflow from a template ID |
| `GET` | `/api/workflows` | `list_user_workflows()` | List user's active workflow instances |
| `GET` | `/api/workflows/{workflow_id}` | `get_user_workflow()` | Get a specific workflow instance |
| `PATCH` | `/api/workflows/{workflow_id}/steps` | `update_user_workflow_step()` | Update a step's status |

The `POST /api/workflows` endpoint accepts `{"template_id": "..."}`. It looks up the template, calls `start_workflow()`, and returns the instance. Returns 404 if the template ID is invalid.

The `PATCH` endpoint accepts `WorkflowStepUpdateRequest` (step_index + status). It calls `update_workflow_step()` which handles auto-advancement. Returns 404 if the workflow is not found.

## Supabase Table

Workflow instances are stored in `workflow_instances`. The engine serializes steps as a JSON array via `model_dump(mode="json")`. Updates write `steps`, `current_step`, `status`, and `updated_at`.

## Relationship to Other Systems

- **Legal Domains** (`docs/LEGAL_DOMAINS.md`): Each template's `domain` field maps to a domain from the classifier. `get_templates_by_domain()` enables filtering workflows relevant to the user's current issue.
- **Memory System** (`docs/MEMORY_SYSTEM.md`): Workflows are independent of the memory injection pipeline. They do not inject into the system prompt, but the chat system can reference active workflows when responding to user questions.
