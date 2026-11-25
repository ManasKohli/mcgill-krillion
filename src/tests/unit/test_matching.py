import json
from pathlib import Path

from rarest_blue.domain.matching import match_answer, normalize, recognize
from rarest_blue.domain.models import Prompt
from rarest_blue.domain.prompt_bank import PROMPTS, PROMPTS_BY_ID


def test_shared_browser_matching_fixture_tracks_server_rules():
    fixture = json.loads((Path(__file__).resolve().parents[1] / "fixtures/local_matching.json").read_text())
    prompt = Prompt.from_dict(fixture["prompt"])
    for case in fixture["cases"]:
        raw = case["raw"]
        recognized, suggestion = recognize(prompt, raw)
        answer = match_answer(prompt, raw)
        assert normalize(raw) == case["normalized"]
        assert answer == case["answer"]
        assert case["check"] == {
            "recognized": recognized,
            "correct": recognized and answer is not None,
            "suggestion": suggestion,
        }


def test_aliases_and_typos_match():
    rez = PROMPTS_BY_ID["residences"]
    assert match_answer(rez, "RVC") == "Royal Victoria College"
    assert match_answer(PROMPTS_BY_ID["green_line"], "St. Laurent") == "Saint-Laurent"
    assert match_answer(PROMPTS_BY_ID["green_line"], "prefontaine") == "Préfontaine"
    assert match_answer(rez, "Carrefour Sherbroke") == "Carrefour Sherbrooke"
    assert match_answer(rez, "Concordia") is None
    assert match_answer(rez, "   ") is None


def test_short_codes_do_not_fuzz():
    courses = Prompt("codes", "Course codes", "", "COMP251", [("COMP250",), ("COMP251",)])
    assert match_answer(courses, "comp250") == "COMP250"
    assert match_answer(courses, "COMP") is None


def test_short_forms_and_extra_words_match():
    buildings = Prompt(
        "places",
        "Places",
        "",
        "Redpath Hall Library",
        [
            ("Otto Maass Chemistry Building",),
            ("Brown Student Services Building",),
            ("Peel",),
            ("Redpath Hall Library", "redpath"),
            ("University Centre",),
            ("University Street",),
        ],
    )
    assert match_answer(buildings, "Otto Maass Chemistry") == "Otto Maass Chemistry Building"
    assert match_answer(buildings, "Brown Student") == "Brown Student Services Building"
    assert match_answer(buildings, "Peel Station") == "Peel"
    assert match_answer(buildings, "Redpath Library") == "Redpath Hall Library"
    # Ambiguous or generic leading words don't count.
    assert match_answer(buildings, "University") is None
    assert match_answer(buildings, "Faculty") is None


def test_no_alias_collisions_within_a_prompt():
    for p in PROMPTS:
        seen: dict[str, str] = {}
        for names in p.answers:
            for name in names:
                key = normalize(name)
                assert seen.setdefault(key, names[0]) == names[0], f"{p.id}: '{name}' collides"


def test_recognize_treats_answers_and_decoys_alike():
    rez = PROMPTS_BY_ID["residences"]
    assert recognize(rez, "rvc") == (True, None)
    assert recognize(rez, "Thomson House") == (True, None)
    # Typos of either kind are suggested, never silently accepted.
    assert recognize(rez, "Carrefour Sherbroke") == (False, "Carrefour Sherbrooke")
    assert recognize(rez, "Thomsen House") == (False, "Thomson House")
    assert recognize(rez, "Concordia Hall") == (False, None)
