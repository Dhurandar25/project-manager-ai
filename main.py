"""Start the daily CrewAI governance review."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from workflows.daily_governance import DailyGovernanceWorkflow


def main() -> None:
    """Load local environment settings and run the daily governance crew."""
    project_root = Path(__file__).resolve().parent
    load_dotenv(project_root / ".env")
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    context = os.getenv(
        "PROJECT_CONTEXT",
        "No project data supplied. Request current status, milestones, RAID, "
        "budget, capacity, dependencies, and decisions; clearly identify all gaps.",
    )
    result = DailyGovernanceWorkflow().run(context)
    print(result)


if __name__ == "__main__":
    main()
