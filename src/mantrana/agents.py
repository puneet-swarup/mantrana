"""ChatAgent and ToolAgent. Config-driven, model-agnostic."""

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .clients.base import ModelClient
from .config import AgentConfig
from .log import Log
from .tools import parse_tool_calls

if TYPE_CHECKING:
    from .tools import ToolRegistry

FINAL_RE = re.compile(r"<final>(.*?)</final>", re.S)


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
    """Coder agent. Parses tool calls, executes them, loops to completion."""

    def __init__(
        self,
        role: str,
        config: AgentConfig,
        prompt: str,
        client: ModelClient,
        registry: "ToolRegistry | None" = None,
        max_steps: int = 8,
    ):
        super().__init__(role, config, prompt, client)
        self.registry = registry
        self.max_steps = max_steps

    async def respond(self, log: Log, ask: str) -> AgentResponse:
        if self.registry is None:
            return await super().respond(log, ask)

        transcript: list[str] = []
        ask_with_tools = (
            f"{ask}\n\n"
            f"Available tools: {', '.join(self.registry.names())}.\n"
            'Emit tool calls as: <tool_call name="TOOL">{json args}</tool_call>\n'
            "When finished, emit: <final>summary</final>"
        )

        for _ in range(self.max_steps):
            prompt = self.build_prompt(log, ask_with_tools)
            if transcript:
                prompt += "\n\n## Tool results so far\n" + "\n".join(transcript)
            reply = await self.client.query(prompt)

            final = FINAL_RE.search(reply)
            if final:
                return AgentResponse(role=self.role, text=final.group(1).strip())

            calls = parse_tool_calls(reply)
            if not calls:
                return AgentResponse(role=self.role, text=reply.strip())

            for name, args in calls:
                try:
                    result = await self.registry.call(name, args)
                except Exception as err:  # noqa: BLE001 - report tool failure back
                    result = f"ERROR: {err}"
                transcript.append(f"[{name}] {result}")

        return AgentResponse(
            role=self.role,
            text="Tool loop reached step budget without a final block.",
        )
