"""Seed script to create the Sarah Chen demo profile in Supabase.

This script upserts a fully populated demo user profile that showcases
Lex's personalized legal assistant capabilities, including active issues,
legal facts, and document references.

Usage:
    SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... python -m scripts.seed_demo
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta

from supabase import create_client

DEMO_PROFILE: dict[str, object] = {
    "display_name": "Sarah",
    "state": "Massachusetts",
    "housing_situation": "Renter | Month-to-month | No formal signed lease renewal",
    "employment_type": "Full-time W2 | Marketing Coordinator | $52,000/year",
    "family_status": "Single | No dependents",
    "active_issues": [
        {
            "issue_type": "landlord_tenant",
            "summary": "Landlord claiming $800 for bathroom tile damage from pre-existing water damage",
            "status": "open",
            "started_at": (datetime.utcnow() - timedelta(days=18)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
            "notes": [
                "Landlord sent written notice on March 9, 2026",
                "Claiming damage occurred during tenancy",
                "Water damage pre-existed move-in",
            ],
        }
    ],
    "legal_facts": [
        "Landlord did not perform a move-in inspection checklist",
        "Pre-existing water stain documented in move-in photos taken January 15, 2024",
        "Sarah gave written 30-day notice to vacate on February 28, 2026",
        "Tenancy began January 15, 2024 — over 2 years",
        "Security deposit paid was $2,200 (equal to one month's rent)",
        "Landlord has not provided interest on security deposit for 2024 or 2025",
        "Lease renewal was verbal only — no written renewal signed after first year",
        "Landlord entered unit without 24-hour notice on February 15, 2026",
    ],
    "documents": [
        "lease_jan_2024.pdf",
        "move_in_photos.zip",
        "vacate_notice_feb_2026.png",
    ],
    "conversation_count": 12,
    "member_since": (datetime.utcnow() - timedelta(days=73)).isoformat(),
}


async def seed() -> None:
    """Seed the Sarah Chen demo profile into Supabase.

    Reads SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from environment
    variables and upserts the demo profile into the user_profiles table.

    Raises:
        KeyError: If required environment variables are not set.
    """
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    supabase = create_client(url, key)

    result = (
        supabase.table("user_profiles")
        .upsert(
            {
                "user_id": "demo-sarah-chen-uuid",
                **DEMO_PROFILE,
            }
        )
        .execute()
    )
    print(f"Seeded: {result.data}")


if __name__ == "__main__":
    asyncio.run(seed())
