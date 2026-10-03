"""End-to-end council integration test.

Drives the full loop through a real CODER tool execution, using fake
clients with scripted responses, and verifies the coder actually wrote a
file to disk.
"""

import asyncio
from pathlib import Path

from src.mantrana.clients import FakeClient
from src.mantrana.config import CouncilConfig
from src.mantrana.orchestrator import run_council

SCRIPT: dict[str, list[str]] = {
    "moderator": [
        "<start>\n@ARCHITECT - design\n@CRITIC - critique\n</start>",
        "@CODER - implement it",
    ],
    "ARCHITECT": ["ARCHITECT: a simple module"],
    "CRITIC": ["CRITIC: keep it minimal"],
    "SME": ["SME: invariants"],
    "COMPLIANCE": ["COMPLIANCE: requirements"],
    "CODER": [
        '<tool_call name="write_file">{"path": "generated.txt", "content": "hello"}</tool_call>',
        "<final>CODER: wrote generated.txt</final>",
    ],
}


def test_council_reaches_coder_and_executes() -> None:
    root = Path(__file__).resolve().parent.parent
    config = CouncilConfig.load(root)

    clients = {
        role: FakeClient(role, SCRIPT.get(role, []))
        for role in ["moderator", *config.agents.keys()]
    }

    # Point the coder at a throwaway file under the project root.
    target = root / "generated.txt"
    if target.exists():
        target.unlink()

    final, log = asyncio.run(run_council("build a thing", config, root, clients))

    # The coder tool loop must have run and produced a final answer.
    assert any(e.who == "CODER" for e in log.entries)
    assert target.exists()
    assert target.read_text() == "hello"
    assert final

    target.unlink()
