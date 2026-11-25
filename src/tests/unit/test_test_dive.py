from rarest_blue.domain.prompt_bank import PROMPTS
from rarest_blue.entrypoints.cli.test_dive import OUT, build_daily, render


def test_web_test_dive_matches_the_prompt_bank():
    # If this fails, rerun: python -m rarest_blue.entrypoints.cli.test_dive
    assert OUT.read_text() == render(build_daily())


def test_test_dive_covers_every_prompt_with_mcgill_zones():
    daily = build_daily()
    assert [p["id"] for p in daily["prompts"]] == [p.id for p in PROMPTS]
    assert daily["zones"][0]["name"] == "Lower Field Shallows"
    for p in daily["prompts"]:
        assert sum(a["golden"] for a in p["play"]["answers"]) == 1
