from datetime import date

from rarest_blue.domain import days, rules
from rarest_blue.domain.matching import match_answer
from rarest_blue.domain.prompt_bank import PROMPT_SOURCES, PROMPTS, PROMPTS_BY_ID


def test_bank_has_sources_unique_ids_and_spare_questions():
    assert len(PROMPTS_BY_ID) == len(PROMPTS) > rules.PROMPTS_PER_DAY
    assert set(PROMPT_SOURCES) == set(PROMPTS_BY_ID)
    assert all(PROMPT_SOURCES.values())


def test_every_accepted_name_matches_its_own_answer():
    for prompt in PROMPTS:
        for names in prompt.answers:
            for name in names:
                assert match_answer(prompt, name) == names[0], (prompt.id, name)


def test_residence_questions_keep_upper_rez_inside_first_year_rez():
    rez = PROMPTS_BY_ID["residences"]
    upper = PROMPTS_BY_ID["upper_rez"]
    assert len(upper.answers) == 5
    for hall in upper.canonical_answers:
        assert match_answer(rez, hall) == hall
    for name in ("RVC", "New Rez", "Solin", "Laird"):
        assert match_answer(rez, name) is not None
        assert match_answer(upper, name) is None
    assert match_answer(rez, "Thomson House") is None


def test_faculties_and_engineering_departments_stay_separate():
    faculties = PROMPTS_BY_ID["faculties"]
    eng = PROMPTS_BY_ID["engineering_departments"]
    assert len(faculties.answers) == 11 and len(eng.answers) == 6
    assert match_answer(faculties, "Desautels") == "Desautels Faculty of Management"
    assert match_answer(faculties, "Ingram School of Nursing") is None
    assert match_answer(eng, "Bioengineering") == "Bioengineering"
    assert match_answer(eng, "Architecture") is None


def test_fallback_prompts_have_decoys_that_dont_score():
    for p in PROMPTS:
        assert len(p.decoys) >= 8, f"{p.id}: needs decoys so autocomplete doesn't list only answers"
        for d in p.decoys:
            assert match_answer(p, d) is None, f"{p.id}: decoy '{d}' scores"


def test_golden_answers_are_valid_deep_cuts():
    for p in PROMPTS:
        names = p.canonical_answers
        assert p.golden in names, f"{p.id}: golden '{p.golden}' isn't an answer"
        assert names.index(p.golden) >= 3, f"{p.id}: golden answer is too obvious"


def test_fallback_prompts_are_stable_and_vary():
    d1, d2 = date(2026, 11, 23), date(2026, 11, 24)
    assert [p.id for p in days.pick_fallback(d1, PROMPTS)] == [p.id for p in days.pick_fallback(d1, PROMPTS)]
    assert len(days.pick_fallback(d1, PROMPTS)) == rules.PROMPTS_PER_DAY
    assert days.pick_fallback(d1, PROMPTS) != days.pick_fallback(d2, PROMPTS)


def test_prompt_round_trips_through_dict():
    for p in PROMPTS:
        assert type(p).from_dict(p.to_dict()) == p
