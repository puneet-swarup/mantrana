import asyncio
from pathlib import Path

import pytest
from src.mantrana.clients.fake import FakeClient
from src.mantrana.config import CouncilConfig
from src.mantrana.orchestrator import run_council

SCRIPT: dict[str, list[str]] = {
    "moderator": [
        "<start>\n@ARCHITECT — design\n@CRITIC — critique\n</start>",
        "<final>final synthesis</final>",
    ],
    "ARCHITECT": ["ARCHITECT: my design"],
    "CRITIC": ["CRITIC: my critique"],
    "SME": ["SME: invariants"],
    "COMPLIANCE": ["COMPLIANCE: requirements"],
    "CODER": ["no code requested"],
}


@pytest.fixture
def root() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture
def config(root: Path) -> CouncilConfig:
    return CouncilConfig.load(root)


def test_council_terminates_with_final(root: Path, config: CouncilConfig) -> None:
    clients = {
        role: FakeClient(role, SCRIPT.get(role, []))
        for role in ["moderator", *config.agents.keys()]
    }
    final, log = asyncio.run(run_council("build a thing", config, root, clients))
    assert final == "final synthesis"
    assert any(e.who == "ARCHITECT" for e in log.entries)
    assert any(e.who == "CRITIC" for e in log.entries)


def test_council_pins_problem_and_catalog(root: Path, config: CouncilConfig) -> None:
    clients = {
        role: FakeClient(role, SCRIPT.get(role, []))
        for role in ["moderator", *config.agents.keys()]
    }
    _, log = asyncio.run(run_council("build a thing", config, root, clients))
    pinned = [e for e in log.entries if e.pinned]
    who = {e.who for e in pinned}
    assert "PROBLEM" in who
    assert "CATALOG" in who