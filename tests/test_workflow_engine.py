"""Tests for the workflow engine — guided step-by-step legal processes.

Verifies start, list, get, and step update operations with mocked Supabase.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.workflows.engine import (
    StepStatus,
    WorkflowStep,
    WorkflowStepUpdateRequest,
    WorkflowTemplate,
    get_workflow,
    list_workflows,
    start_workflow,
    update_workflow_step,
)

USER_ID = "user_test_workflows"


def _make_template() -> WorkflowTemplate:
    """Build a simple two-step template for testing."""
    return WorkflowTemplate(
        id="test_template",
        title="Test Workflow",
        description="A workflow for testing",
        domain="landlord_tenant",
        estimated_time="1 week",
        steps=[
            WorkflowStep(
                id="step_1",
                title="First Step",
                explanation="Do the first thing.",
            ),
            WorkflowStep(
                id="step_2",
                title="Second Step",
                explanation="Do the second thing.",
            ),
        ],
    )


@pytest.fixture
def mock_supabase_workflows():
    """Patch _get_supabase for the workflow engine module."""
    mock_client = MagicMock()
    with patch("backend.workflows.engine._get_supabase", return_value=mock_client):
        yield mock_client


class TestStartWorkflow:
    """Verify start_workflow creates an instance from a template."""

    async def test_starts_workflow(self, mock_supabase_workflows: MagicMock) -> None:
        mock_supabase_workflows.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(data=[{"id": "w1"}])
        )

        template = _make_template()
        instance = await start_workflow(USER_ID, template)

        assert instance.user_id == USER_ID
        assert instance.template_id == "test_template"
        assert instance.title == "Test Workflow"
        assert len(instance.steps) == 2
        # First step should be auto-set to in_progress
        assert instance.steps[0].status == StepStatus.IN_PROGRESS
        assert instance.steps[1].status == StepStatus.NOT_STARTED

    async def test_raises_on_insert_failure(self, mock_supabase_workflows: MagicMock) -> None:
        mock_supabase_workflows.table.return_value.insert.return_value.execute.return_value = (
            MagicMock(data=None)
        )

        with pytest.raises(RuntimeError, match="Failed to start workflow"):
            await start_workflow(USER_ID, _make_template())


class TestListWorkflows:
    """Verify list_workflows returns summary dicts."""

    async def test_returns_summaries(self, mock_supabase_workflows: MagicMock) -> None:
        mock_supabase_workflows.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "id": "w1",
                    "template_id": "test_template",
                    "title": "Test Workflow",
                    "domain": "landlord_tenant",
                    "current_step": 0,
                    "status": "in_progress",
                    "started_at": "2026-03-01T00:00:00",
                    "updated_at": "2026-03-01T00:00:00",
                    "steps": [
                        {"id": "s1", "status": "completed"},
                        {"id": "s2", "status": "not_started"},
                    ],
                }
            ]
        )

        summaries = await list_workflows(USER_ID)
        assert len(summaries) == 1
        assert summaries[0]["completed_steps"] == 1
        assert summaries[0]["total_steps"] == 2

    async def test_returns_empty_on_error(self, mock_supabase_workflows: MagicMock) -> None:
        mock_supabase_workflows.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
            "DB down"
        )

        summaries = await list_workflows(USER_ID)
        assert summaries == []


class TestGetWorkflow:
    """Verify get_workflow fetches a single workflow instance."""

    async def test_returns_workflow(self, mock_supabase_workflows: MagicMock) -> None:
        mock_result = MagicMock()
        mock_result.data = {
            "id": "w1",
            "user_id": USER_ID,
            "template_id": "test_template",
            "title": "Test Workflow",
            "domain": "landlord_tenant",
            "steps": [
                {"id": "s1", "title": "Step 1", "explanation": "Do it", "status": "in_progress"},
            ],
            "current_step": 0,
            "status": "in_progress",
            "started_at": "2026-03-01T00:00:00",
            "updated_at": "2026-03-01T00:00:00",
        }
        (
            mock_supabase_workflows.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value
        ) = mock_result

        instance = await get_workflow("w1", USER_ID)
        assert instance is not None
        assert instance.id == "w1"

    async def test_returns_none_when_not_found(self, mock_supabase_workflows: MagicMock) -> None:
        mock_result = MagicMock()
        mock_result.data = None
        (
            mock_supabase_workflows.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value
        ) = mock_result

        instance = await get_workflow("nonexistent", USER_ID)
        assert instance is None


class TestUpdateWorkflowStep:
    """Verify update_workflow_step modifies step status and auto-advances."""

    async def test_completes_step_and_advances(self, mock_supabase_workflows: MagicMock) -> None:
        # Mock get_workflow to return an instance
        mock_result = MagicMock()
        mock_result.data = {
            "id": "w1",
            "user_id": USER_ID,
            "template_id": "test_template",
            "title": "Test",
            "domain": "landlord_tenant",
            "steps": [
                {"id": "s1", "title": "Step 1", "explanation": "Do it", "status": "in_progress"},
                {"id": "s2", "title": "Step 2", "explanation": "Do next", "status": "not_started"},
            ],
            "current_step": 0,
            "status": "in_progress",
            "started_at": "2026-03-01T00:00:00",
            "updated_at": "2026-03-01T00:00:00",
        }
        (
            mock_supabase_workflows.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value
        ) = mock_result

        # Mock the update call
        mock_supabase_workflows.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{}]
        )

        update = WorkflowStepUpdateRequest(step_index=0, status=StepStatus.COMPLETED)
        result = await update_workflow_step("w1", USER_ID, update)

        assert result is not None
        assert result.steps[0].status == StepStatus.COMPLETED
        assert result.steps[1].status == StepStatus.IN_PROGRESS
        assert result.current_step == 1
