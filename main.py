"""Entry point. Runs the council with fake clients."""

import asyncio
from pathlib import Path

from src.mantrana.clients.fake import FakeClient
from src.mantrana.config import CouncilConfig
from src.mantrana.orchestrator import run_council

FAKE_SCRIPT: dict[str, list[str]] = {
    "moderator": [
        "<start>\n@ARCHITECT — design the system\n@CRITIC — challenge the design\n</start>",
        "@SME — what are the domain invariants I should not get wrong?",
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
        "over-engineering. What is the actual audit requirement? If it's just "
        "'who changed what', an append-only audit table is simpler."
    ],
    "SME": [
        "SME: Invariants — each transaction is atomic; balance never goes "
        "negative mid-transaction; interest accrues per-day, not per-month. "
        "Don't conflate principal with outstanding."
    ],
    "COMPLIANCE": [
        "COMPLIANCE: RBI requires monthly snapshots for restructured loans. "
        "You need a reporting table separate from the operational model. "
        "Retention: 8 years minimum."
    ],
    "CODER": ["no code requested"],
}


async def main() -> None:
    root = Path(__file__).parent
    config = CouncilConfig.load(root)

    clients: dict[str, FakeClient] = {}
    for role in ["moderator", *config.agents.keys()]:
        clients[role] = FakeClient(role, FAKE_SCRIPT.get(role, []))

    problem = "Design a loan management system with audit trail."
    final, log = await run_council(problem, config, root, clients)

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