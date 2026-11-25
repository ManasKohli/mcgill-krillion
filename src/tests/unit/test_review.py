import pytest

from rarest_blue.application import review
from rarest_blue.domain.matching import match_answer
from rarest_blue.domain.prompt_bank import PROMPTS_BY_ID


def test_accept_as_alias_checks_the_answer():
    rez = PROMPTS_BY_ID["residences"]
    updated = review.with_answer(rez, "Cit Rez", "citadelle")
    assert match_answer(updated, "cit rez") == "La Citadelle"
    with pytest.raises(ValueError, match="isn't an answer"):
        review.with_answer(rez, "Cit Rez", "Concordia")
    with pytest.raises(ValueError, match="already counts"):
        review.with_answer(rez, "rvc", "Solin")
