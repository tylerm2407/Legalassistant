"""Typed helper functions for safely casting untyped external data.

Centralizes the type narrowing that was previously scattered across modules
as ``# type: ignore`` comments. The main sources of untyped data are:

* **Supabase responses** — ``result.data`` returns ``list[Any]`` from the
  PostgREST client, which must be cast to Pydantic models or typed dicts.
* **Anthropic API messages** — conversation history stored as
  ``list[dict[str, str]]`` needs casting to ``MessageParam`` for the SDK.

By concentrating the ``Any`` boundary in this module, the rest of the codebase
can remain strictly typed without inline suppression comments.
"""

from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel


def parse_supabase_row[T: BaseModel](data: Any, model_class: type[T]) -> T:
    """Construct a Pydantic model from an untyped Supabase row.

    Supabase PostgREST returns rows as opaque objects. This function
    safely casts the row to a ``dict`` and passes it to the model
    constructor.

    Args:
        data: A single row from ``result.data`` (typically ``dict[str, Any]``).
        model_class: The Pydantic model class to instantiate.

    Returns:
        An instance of ``model_class`` populated from the row data.

    Raises:
        pydantic.ValidationError: If the row data doesn't match the model schema.
    """
    row: dict[str, Any] = dict(data)  # type: ignore[arg-type]
    return model_class(**row)


def parse_supabase_rows[T: BaseModel](data: Any, model_class: type[T]) -> list[T]:
    """Construct a list of Pydantic models from untyped Supabase rows.

    Convenience wrapper over :func:`parse_supabase_row` for multi-row
    query results.

    Args:
        data: The ``result.data`` list from a Supabase query (may be ``None``).
        model_class: The Pydantic model class to instantiate per row.

    Returns:
        List of ``model_class`` instances. Empty list if ``data`` is falsy.
    """
    return [parse_supabase_row(row, model_class) for row in (data or [])]


def supabase_row_to_dict(data: Any) -> dict[str, object]:
    """Cast an untyped Supabase row to a typed dictionary.

    Used when the caller needs a plain dict rather than a Pydantic model
    (e.g. for building summary responses).

    Args:
        data: A single row from ``result.data``.

    Returns:
        A ``dict[str, object]`` copy of the row.
    """
    return dict(cast(dict[str, object], data))


def supabase_json_list(raw: object) -> list[dict[str, object]]:
    """Cast a Supabase JSON array column value to a typed list of dicts.

    Supabase stores JSON array columns as opaque objects. This function
    safely narrows the type for downstream iteration.

    Args:
        raw: The raw column value (expected to be a list of dicts, or falsy).

    Returns:
        A ``list[dict[str, object]]``. Empty list if ``raw`` is falsy.
    """
    if not raw:
        return []
    return list(cast(list[dict[str, object]], raw))


def as_anthropic_messages(
    messages: list[dict[str, str]],
) -> Any:
    """Cast conversation message dicts to the Anthropic ``MessageParam`` shape.

    The Anthropic SDK's ``messages.create()`` expects
    ``Iterable[MessageParam]``, which is a TypedDict with ``role`` and
    ``content`` keys. Our internal representation is already
    ``list[dict[str, str]]`` with exactly those keys, but mypy cannot
    verify structural compatibility with the TypedDict.

    This function provides a single, documented cast point so callers
    don't need inline ``# type: ignore`` comments.

    Args:
        messages: Conversation history as dicts with ``role`` and ``content``.

    Returns:
        The same list, typed as ``Any`` to satisfy the Anthropic SDK.
    """
    return messages
