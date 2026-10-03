from pathlib import Path

import pytest
from src.mantrana.config import CouncilConfig
from src.mantrana.router import Router


@pytest.fixture
def config() -> CouncilConfig:
    return CouncilConfig.load(Path(__file__).parent.parent)


def test_parse_targets(config: CouncilConfig) -> None:
    r = Router(config)
    assert r.parse_targets("@ARCHITECT — design it\n@CRITIC — break it") == [
        "ARCHITECT",
        "CRITIC",
    ]


def test_parse_targets_dedup(config: CouncilConfig) -> None:
    r = Router(config)
    assert r.parse_targets("@SME do this. @SME also that.") == ["SME"]


def test_parse_start(config: CouncilConfig) -> None:
    r = Router(config)
    reply = "<start>\n@ARCHITECT — why\n@CRITIC — why\n</start>"
    assert r.parse_start(reply) == ["ARCHITECT", "CRITIC"]


def test_is_final(config: CouncilConfig) -> None:
    r = Router(config)
    assert r.is_final("<final>done</final>")
    assert not r.is_final("@SME — more please")


def test_extract_final(config: CouncilConfig) -> None:
    r = Router(config)
    assert r.extract_final("<final>result here</final>") == "result here"


def test_enforce_invariants_loan(config: CouncilConfig) -> None:
    r = Router(config)
    result = r.enforce_invariants(["ARCHITECT"], "design a loan system")
    assert "CRITIC" in result
    assert "COMPLIANCE" in result
    assert "ARCHITECT" in result


def test_enforce_invariants_unrelated(config: CouncilConfig) -> None:
    r = Router(config)
    result = r.enforce_invariants(["ARCHITECT"], "design a UI widget")
    assert "CRITIC" in result
    assert "COMPLIANCE" not in result