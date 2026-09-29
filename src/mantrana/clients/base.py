"""The ModelClient protocol. Three methods. That's the entire contract."""

from typing import Protocol


class ModelClient(Protocol):
    async def query(self, prompt: str) -> str: ...

    async def is_available(self) -> bool: ...

    async def close(self) -> None: ...