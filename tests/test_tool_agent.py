"""Tests for the ToolAgent tool-calling loop."""

import asyncio
from pathlib import Path

from src.mantrana.agents import ToolAgent
from src.mantrana.clients.fake import FakeClient
from src.mantrana.config import AgentConfig
from src.mantrana.log import Log
from src.mantrana.tools import ToolRegistry


def _agent(tmp_path: Path, responses: list[str]) -> ToolAgent:
    config = AgentConfig(prompt="x", model="fake")
    client = FakeClient("CODER", responses)
    registry = ToolRegistry(tmp_path)
    return ToolAgent("CODER", config, "coder mandate", client, registry=registry)


def test_tool_agent_executes_then_finalizes(tmp_path: Path) -> None:
    responses = [
        '<tool_call name="write_file">{"path": "made.txt", "content": "done"}</tool_call>',
        "<final>wrote the file</final>",
    ]
    agent = _agent(tmp_path, responses)
    result = asyncio.run(agent.respond(Log(), "write a file"))
    assert result.text == "wrote the file"
    assert (tmp_path / "made.txt").read_text() == "done"


def test_tool_agent_reports_tool_error(tmp_path: Path) -> None:
    responses = [
        '<tool_call name="read_file">{"path": "../outside.txt"}</tool_call>',
        "<final>handled the error</final>",
    ]
    agent = _agent(tmp_path, responses)
    result = asyncio.run(agent.respond(Log(), "read outside"))
    assert result.text == "handled the error"


def test_tool_agent_returns_prose_when_no_calls(tmp_path: Path) -> None:
    agent = _agent(tmp_path, ["CODER: nothing to do"])
    result = asyncio.run(agent.respond(Log(), "do nothing"))
    assert result.text == "CODER: nothing to do"


def test_tool_agent_respects_step_budget(tmp_path: Path) -> None:
    responses = ['<tool_call name="read_file">{"path": "x"}</tool_call>'] * 20
    agent = _agent(tmp_path, responses)
    result = asyncio.run(agent.respond(Log(), "loop"))
    assert "step budget" in result.text
