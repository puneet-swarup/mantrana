"""Tests for the tool registry and tool-call parser."""

import asyncio
from pathlib import Path

import pytest
from src.mantrana.tools import ToolError, ToolRegistry, parse_tool_calls


@pytest.fixture
def registry(tmp_path: Path) -> ToolRegistry:
    return ToolRegistry(tmp_path)


def test_parse_tool_calls_single() -> None:
    text = '<tool_call name="write_file">{"path": "a.txt", "content": "hi"}</tool_call>'
    calls = parse_tool_calls(text)
    assert calls == [("write_file", {"path": "a.txt", "content": "hi"})]


def test_parse_tool_calls_multiple() -> None:
    text = (
        '<tool_call name="read_file">{"path": "a"}</tool_call>\n'
        '<tool_call name="run_shell">{"command": "ls"}</tool_call>'
    )
    calls = parse_tool_calls(text)
    assert [c[0] for c in calls] == ["read_file", "run_shell"]


def test_parse_tool_calls_skips_malformed() -> None:
    text = '<tool_call name="read_file">not json</tool_call>'
    assert parse_tool_calls(text) == []


def test_parse_tool_calls_none() -> None:
    assert parse_tool_calls("just prose") == []


def test_write_then_read(registry: ToolRegistry, tmp_path: Path) -> None:
    asyncio.run(registry.call("write_file", {"path": "out.txt", "content": "hello"}))
    result = asyncio.run(registry.call("read_file", {"path": "out.txt"}))
    assert result == "hello"
    assert (tmp_path / "out.txt").read_text() == "hello"


def test_append_to_file(registry: ToolRegistry, tmp_path: Path) -> None:
    asyncio.run(registry.call("write_file", {"path": "f.txt", "content": "a"}))
    asyncio.run(registry.call("append_to_file", {"path": "f.txt", "content": "b"}))
    assert (tmp_path / "f.txt").read_text() == "ab"


def test_path_escape_rejected(registry: ToolRegistry) -> None:
    with pytest.raises(ToolError):
        asyncio.run(registry.call("read_file", {"path": "../escape.txt"}))


def test_unknown_tool_rejected(registry: ToolRegistry) -> None:
    with pytest.raises(ToolError):
        asyncio.run(registry.call("nope", {}))


def test_run_shell(registry: ToolRegistry) -> None:
    result = asyncio.run(registry.call("run_shell", {"command": "echo hi"}))
    assert "hi" in result
    assert "exit=0" in result


def test_registry_names(registry: ToolRegistry) -> None:
    names = registry.names()
    assert "write_file" in names
    assert "run_shell" in names
    assert "raise_alarm" in names
