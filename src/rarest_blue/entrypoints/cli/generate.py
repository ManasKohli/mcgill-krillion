"""Nightly job: have an LLM write the coming days' prompt sets, fact-check them with a second LLM, and store them.

    python -m rarest_blue.entrypoints.cli.generate [--day YYYY-MM-DD] [--dry-run]

Scheduled at 23:30 Montreal time. It fills every day from tomorrow through two days out that has no stored set yet.
Normally that's just the day two out, so each set sits stored for a full day where someone can read it (and fix it
with the review tool) before the API starts serving it. If a night was missed (or at launch), it also backfills
tomorrow, so tomorrow gets a generated set instead of the built-in fallback. Days that already have a set are left
alone, so re-running is safe. Exits non-zero if any day couldn't get a valid set, so the Cloud Run job retries.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, timedelta

from ...application.generation import GenerationFailed, Outcome, PromptSetGenerator, run_nightly
from ...application.ports import PromptWriter
from ...config import Settings
from ...domain import days
from ...infrastructure import postgres
from ...infrastructure.openrouter import OpenRouterWriter

# Generate this far ahead so a day's set can be read before it goes live.
DAYS_AHEAD = 2


def target_days(today: date) -> list[date]:
    """Tomorrow through DAYS_AHEAD out, oldest first, so each set can avoid repeating the one before it."""
    return [today + timedelta(days=n) for n in range(1, DAYS_AHEAD + 1)]


def main(argv: list[str] | None = None, settings: Settings | None = None, writer: PromptWriter | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--day",
        type=date.fromisoformat,
        help="generate just this day (default: every missing day from tomorrow through two days out)",
    )
    parser.add_argument("--dry-run", action="store_true", help="print the set instead of storing it")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    settings = settings or Settings.from_env()
    if args.day:
        targets = [args.day]
    elif args.dry_run:
        targets = [days.today() + timedelta(days=DAYS_AHEAD)]
    else:
        targets = target_days(days.today())

    postgres.init_schema(settings.database_url)
    generator = PromptSetGenerator(
        writer or OpenRouterWriter(settings.openrouter_api_key), settings.generator_model, settings.verifier_model
    )
    failed = False
    for day in targets:
        try:
            result = run_nightly(
                lambda: postgres.PostgresUnitOfWork(settings.database_url), generator, day, args.dry_run
            )
        except GenerationFailed as e:
            print(e, file=sys.stderr)
            failed = True
            continue

        if result.outcome is Outcome.DRY_RUN:
            print(json.dumps([p.to_dict() for p in result.prompts], indent=2))
        elif result.outcome is Outcome.SKIPPED:
            print(f"{day} already has a set; nothing to do")
        elif result.outcome is Outcome.ALREADY_HAD_SET:
            print(f"{day}: already had a set, kept it ({', '.join(p.id for p in result.prompts)})")
        else:
            print(f"{day}: stored ({', '.join(p.id for p in result.prompts)})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
