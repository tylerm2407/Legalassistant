"""Smoke test against a live CaseMate deployment.

Verifies that critical endpoints respond correctly without requiring
authentication or real data. Safe to run against staging or production.

Usage:
    python scripts/smoke_test.py https://casemate-api.up.railway.app
    python scripts/smoke_test.py http://localhost:8000
"""

from __future__ import annotations

import sys
import time

import requests


def _base_url() -> str:
    """Resolve the target base URL from CLI args or default to localhost."""
    if len(sys.argv) > 1:
        return sys.argv[1].rstrip("/")
    return "http://localhost:8000"


def _test(
    name: str,
    method: str,
    path: str,
    expected_status: int | set[int],
    body: dict[str, str] | None = None,
) -> bool:
    """Run a single HTTP test against the deployment.

    Args:
        name: Human-readable test label.
        method: HTTP method (GET or POST).
        path: URL path to request.
        expected_status: Expected HTTP status code, or a set of valid codes.
        body: Optional JSON body for POST requests.

    Returns:
        True if the response status matches expected_status.
    """
    url = f"{_base_url()}{path}"
    valid = (
        expected_status
        if isinstance(expected_status, set)
        else {expected_status}
    )
    start = time.monotonic()
    try:
        if method == "GET":
            resp = requests.get(url, timeout=30)
        else:
            resp = requests.post(url, json=body, timeout=30)

        latency_ms = round((time.monotonic() - start) * 1000)
        if resp.status_code in valid:
            print(f"  PASS | {name} ({latency_ms}ms)")
            return True
        expected_str = "/".join(str(c) for c in sorted(valid))
        print(
            f"  FAIL | {name} — expected {expected_str},"
            f" got {resp.status_code} ({latency_ms}ms)",
        )
        return False
    except requests.exceptions.ConnectionError:
        print(f"  ERROR | {name} — connection refused at {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"  ERROR | {name} — timed out after 30s")
        return False


def main() -> None:
    """Run all smoke tests and report results."""
    base = _base_url()
    print(f"\nSmoke Testing: {base}\n")

    results: list[bool] = []

    # Health and infrastructure
    results.append(_test("Health check", "GET", "/health", 200))
    results.append(_test("Metrics endpoint", "GET", "/metrics", 200))
    results.append(_test("OpenAPI docs", "GET", "/docs", 200))
    results.append(_test("ReDoc", "GET", "/redoc", 200))

    # Auth-gated endpoints return 401 or 403 without token
    results.append(
        _test("Chat without auth", "POST", "/api/chat", {401, 403}),
    )
    results.append(
        _test("Profile without auth", "GET", "/api/profile/test", {401, 403}),
    )

    # Non-existent routes
    results.append(_test("Unknown route → 404", "GET", "/api/nonexistent", 404))

    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 40}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'=' * 40}\n")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
