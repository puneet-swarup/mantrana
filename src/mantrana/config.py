"""Configuration loading and validation."""

from pathlib import Path

import yaml
from pydantic import BaseModel


class InvariantRule(BaseModel):
    match: list[str]
    must_include: list[str]


class Invariants(BaseModel):
    always_include: list[str] = []
    per_domain: list[InvariantRule] = []


class ModeratorConfig(BaseModel):
    role: str
    prompt: str
    catalog: str
    model: str
    fallback_model: str | None = None
    invariants: Invariants = Invariants()


class AgentConfig(BaseModel):
    prompt: str
    model: str
    max_words: int = 150
    type: str = "chat_agent"
    tools: list[str] = []


class LoopConfig(BaseModel):
    max_rounds: int = 3
    max_turns: int = 30
    log_trim_after: int = 15
    pin: list[str] = []


class AlarmConfig(BaseModel):
    on_agent_unavailable: str = "warning"
    on_max_rounds: str = "critical"
    on_task_complete: str = "success"


class CouncilConfig(BaseModel):
    moderator: ModeratorConfig
    agents: dict[str, AgentConfig]
    loop: LoopConfig
    alarms: AlarmConfig

    @classmethod
    def load(cls, root: Path) -> "CouncilConfig":
        data = yaml.safe_load((root / "config" / "council.yaml").read_text())
        return cls(**data)

    def read_prompt(self, root: Path, path: str) -> str:
        return (root / path).read_text(encoding="utf-8")

    def read_catalog(self, root: Path) -> str:
        return (root / self.moderator.catalog).read_text(encoding="utf-8")
