"""Entry point. Runs the council.

By default this uses the fake clients (scripted responses) so the loop runs
with no external dependencies. To run against real backends, set the model's
`client` kind in config/models.yaml (e.g. `subprocess` for a CLI agent).
"""

import asyncio
from pathlib import Path

from src.mantrana.clients import FakeClient, build_clients_from_config
from src.mantrana.config import CouncilConfig
from src.mantrana.orchestrator import run_council

FAKE_SCRIPT: dict[str, list[str]] = {
    "moderator": [
        "<start>\n@ARCHITECT - design the system\n@CRITIC - challenge the design\n</start>",
        "@SME - what are the domain invariants I should not get wrong?",
        "<final>Council converged on a modular, event-sourced design. "
        "SME flagged atomicity invariants. CRITIC flagged replay cost as a "
        "potential over-engineering. Recommend: prototype the event log, "
        "measure replay latency, then decide whether to keep it.</final>",
    ],
    "ARCHITECT": [
        "ARCHITECT: Separate domain into three aggregates: Loan, Schedule, "
        "Transaction. Use event sourcing for audit trail. Sacrifice: query "
        "complexity. Gain: replayability and audit compliance."
    ],
    "CRITIC": [
        "CRITIC: Event sourcing adds replay cost. For a small system this is "
        "over-engineering. What is the actual audit requirement?"
    ],
    "SME": [
        "SME: Invariants - each transaction is atomic; balance never goes "
        "negative mid-transaction; interest accrues per-day, not per-month."
    ],
    "COMPLIANCE": [
        "COMPLIANCE: RBI requires monthly snapshots for restructured loans. "
        "You need a reporting table separate from the operational model."
    ],
    "CODER": ["no code requested"],
}


def _with_fake_scripts(clients: dict, script: dict[str, list[str]]) -> dict:
    """Give fake clients scripted responses so main.py stays deterministic."""
    for role, client in clients.items():
        if isinstance(client, FakeClient):
            client.responses = list(script.get(role, []))
    return clients


async def main() -> None:
    root = Path(__file__).parent
    config = CouncilConfig.load(root)

    clients = build_clients_from_config(root, config)
    _with_fake_scripts(clients, FAKE_SCRIPT)

    problem = "Design a loan management system with audit trail."
    final, log = await run_council(problem, config, root, clients)

    for client in clients.values():
        await client.close()

    print("=" * 70)
    print("COUNCIL LOG")
    print("=" * 70)
    print(log.render())
    print()
    print("=" * 70)
    print("FINAL SYNTHESIS")
    print("=" * 70)
    print(final)


if __name__ == "__main__":
    asyncio.run(main())
