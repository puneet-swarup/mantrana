"""ChatAgent and ToolAgent. Config-driven, model-agnostic."""

from dataclasses import dataclass

from .clients.base import ModelClient
from .config import AgentConfig
from .log import Log


@dataclass
class AgentResponse:
    role: str
    text: str


class ChatAgent:
    def __init__(
        self,
        role: str,
        config: AgentConfig,
        prompt: str,
        client: ModelClient,
    ):
        self.role = role
        self.config = config
        self.prompt = prompt
        self.client = client

    def build_prompt(self, log: Log, ask: str) -> str:
        return (
            f"{self.prompt}\n\n"
            f"## Conversation log\n{log.render_trimmed()}\n\n"
            f"## Your turn\n{ask}\n\n"
            f"Respond in under {self.config.max_words} words. "
            f"Start with your role name, then a colon."
        )

    async def respond(self, log: Log, ask: str) -> AgentResponse:
        prompt = self.build_prompt(log, ask)
        text = await self.client.query(prompt)
        return AgentResponse(role=self.role, text=text)


class ToolAgent(ChatAgent):
    """Coder agent. Phase 0: text only. Phase 2: dispatches tool calls."""
