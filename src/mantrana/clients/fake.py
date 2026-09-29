"""Deterministic fake client for Phase 0 testing."""


class FakeClient:
    """Returns scripted responses. No network. No browser. Fast."""

    def __init__(self, name: str, responses: list[str] | None = None):
        self.name = name
        self.responses = list(responses or [])
        self.calls: list[str] = []

    async def query(self, prompt: str) -> str:
        self.calls.append(prompt)
        if not self.responses:
            return f"<final>[{self.name}] no more scripted responses</final>"
        return self.responses.pop(0)

    async def is_available(self) -> bool:
        return True

    async def close(self) -> None:
        pass