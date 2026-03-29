"""Workflow engine for guided step-by-step legal processes.

Provides the execution engine for multi-step legal workflows. Each workflow
is a sequence of steps with explanations, required documents, and tips.
User progress is tracked per workflow instance.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.memory.profile import _get_supabase
from backend.utils.logger import get_logger

_logger = get_logger(__name__)


class StepStatus(StrEnum):
    """Status values for a workflow step."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class WorkflowStep(BaseModel):
    """A single step in a guided legal workflow.

    Attributes:
        id: Step identifier within the workflow.
        title: Short title for this step.
        explanation: Detailed explanation of what to do.
        required_documents: Documents needed for this step.
        tips: Helpful tips for completing this step.
        deadlines: Any deadlines associated with this step.
        status: Current completion status.
    """

    id: str
    title: str
    explanation: str
    required_documents: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    status: StepStatus = StepStatus.NOT_STARTED


class WorkflowTemplate(BaseModel):
    """Template definition for a guided legal workflow.

    Attributes:
        id: Unique template identifier.
        title: Human-readable workflow title.
        description: Brief description of what this workflow covers.
        domain: Legal domain this workflow belongs to.
        estimated_time: Approximate time to complete all steps.
        steps: Ordered list of workflow steps.
    """

    id: str
    title: str
    description: str
    domain: str
    estimated_time: str
    steps: list[WorkflowStep]


class WorkflowInstance(BaseModel):
    """A user's active workflow instance with progress tracking.

    Attributes:
        id: Unique instance identifier.
        user_id: Owner of this workflow instance.
        template_id: Which workflow template this is based on.
        title: Title from the template.
        domain: Legal domain from the template.
        steps: Steps with user's progress.
        current_step: Index of the current step (0-based).
        status: Overall workflow status.
        started_at: When the user started this workflow.
        updated_at: When the last progress was made.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    template_id: str
    title: str
    domain: str
    steps: list[WorkflowStep]
    current_step: int = 0
    status: StepStatus = StepStatus.IN_PROGRESS
    started_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowStepUpdateRequest(BaseModel):
    """Request body for updating a workflow step.

    Attributes:
        step_index: Which step to update (0-based).
        status: New status for the step.
    """

    step_index: int
    status: StepStatus


async def start_workflow(
    user_id: str,
    template: WorkflowTemplate,
) -> WorkflowInstance:
    """Start a new workflow instance from a template.

    Args:
        user_id: The Supabase auth user ID.
        template: The workflow template to instantiate.

    Returns:
        The newly created WorkflowInstance.

    Raises:
        RuntimeError: If the insert fails.
    """
    instance = WorkflowInstance(
        user_id=user_id,
        template_id=template.id,
        title=template.title,
        domain=template.domain,
        steps=[step.model_copy() for step in template.steps],
    )
    # Mark first step as in_progress
    if instance.steps:
        instance.steps[0].status = StepStatus.IN_PROGRESS

    try:
        client = _get_supabase()
        data = instance.model_dump(mode="json")
        result = client.table("workflow_instances").insert(data).execute()
        if not result.data:
            raise RuntimeError(f"Failed to start workflow for user_id={user_id}")
        _logger.info(
            "workflow_started",
            user_id=user_id,
            workflow_id=instance.id,
            template_id=template.id,
        )
        return instance
    except Exception as exc:
        _logger.error(
            "workflow_start_error",
            user_id=user_id,
            template_id=template.id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(f"Failed to start workflow: {exc}") from exc


async def get_workflow(workflow_id: str, user_id: str) -> WorkflowInstance | None:
    """Fetch a workflow instance by ID, verifying ownership.

    Args:
        workflow_id: The workflow instance UUID.
        user_id: The authenticated user ID.

    Returns:
        The WorkflowInstance if found, else None.
    """
    try:
        client = _get_supabase()
        result = (
            client.table("workflow_instances")
            .select("*")
            .eq("id", workflow_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        data = getattr(result, "data", None)
        if data is None:
            return None
        return WorkflowInstance(**data)
    except Exception as exc:
        _logger.error(
            "workflow_fetch_error",
            workflow_id=workflow_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return None


async def list_workflows(user_id: str) -> list[dict[str, object]]:
    """List a user's workflow instances.

    Args:
        user_id: The Supabase auth user ID.

    Returns:
        List of workflow summary dicts.
    """
    try:
        client = _get_supabase()
        result = (
            client.table("workflow_instances")
            .select(
                "id, template_id, title, domain, current_step, "
                "status, started_at, updated_at, steps"
            )
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        summaries: list[dict[str, object]] = []
        for raw_row in result.data or []:
            row: dict[str, Any] = dict(raw_row)  # type: ignore[arg-type]
            steps: list[dict[str, Any]] = row.get("steps") or []
            completed = sum(1 for s in steps if s.get("status") == "completed")
            summaries.append(
                {
                    "id": row["id"],
                    "template_id": row.get("template_id"),
                    "title": row.get("title"),
                    "domain": row.get("domain"),
                    "current_step": row.get("current_step", 0),
                    "total_steps": len(steps),
                    "completed_steps": completed,
                    "status": row.get("status"),
                    "started_at": row.get("started_at"),
                    "updated_at": row.get("updated_at"),
                }
            )
        return summaries
    except Exception as exc:
        _logger.error(
            "workflow_list_error",
            user_id=user_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        return []


async def update_workflow_step(
    workflow_id: str,
    user_id: str,
    update: WorkflowStepUpdateRequest,
) -> WorkflowInstance | None:
    """Update a step's status in a workflow instance.

    Args:
        workflow_id: The workflow instance UUID.
        user_id: The authenticated user ID.
        update: The step update request.

    Returns:
        The updated WorkflowInstance, or None if not found.

    Raises:
        RuntimeError: If the update fails.
    """
    instance = await get_workflow(workflow_id, user_id)
    if instance is None:
        return None

    if update.step_index < 0 or update.step_index >= len(instance.steps):
        raise RuntimeError(f"Invalid step index: {update.step_index}")

    instance.steps[update.step_index].status = update.status
    instance.updated_at = datetime.utcnow()

    # Auto-advance current_step if completed
    if update.status == StepStatus.COMPLETED:
        next_step = update.step_index + 1
        if next_step < len(instance.steps):
            instance.current_step = next_step
            instance.steps[next_step].status = StepStatus.IN_PROGRESS
        else:
            instance.status = StepStatus.COMPLETED

    try:
        client = _get_supabase()
        steps_data = [s.model_dump(mode="json") for s in instance.steps]
        client.table("workflow_instances").update(
            {
                "steps": steps_data,
                "current_step": instance.current_step,
                "status": instance.status.value,
                "updated_at": instance.updated_at.isoformat(),
            }
        ).eq("id", workflow_id).eq("user_id", user_id).execute()

        _logger.info(
            "workflow_step_updated",
            workflow_id=workflow_id,
            step_index=update.step_index,
            new_status=update.status.value,
        )
        return instance
    except Exception as exc:
        _logger.error(
            "workflow_step_update_error",
            workflow_id=workflow_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise RuntimeError(f"Failed to update workflow step: {exc}") from exc
