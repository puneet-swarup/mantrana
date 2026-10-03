"""Tool registry for the CODER tool loop.

Each tool is a callable that takes a dict of arguments and returns a
string result. Tools are sandboxed to the project root: file paths are
resolved under the root and rejected if they escape it.
"""

import asyncio
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any


class ToolError(Exception):
    """Raised when a tool call is invalid or fails."""


class ToolRegistry:
    """Maps tool names to callables, sandboxed to a root directory."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._tools: dict[str, Callable[[dict[str, Any]], Any]] = {}
        self._register_builtins()

    def _safe_path(self, raw: str) -> Path:
        if not raw or not isinstance(raw, str):
            raise ToolError("path must be a non-empty string")
        candidate = (self.root / raw).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as err:
            raise ToolError(f"path escapes project root: {raw!r}") from err
        return candidate

    def _register_builtins(self) -> None:
        self.register("read_file", self._read_file)
        self.register("write_file", self._write_file)
        self.register("append_to_file", self._append_to_file)
        self.register("run_shell", self._run_shell)
        self.register("raise_alarm", self._raise_alarm)

    def register(self, name: str, fn: Callable[[dict[str, Any]], Any]) -> None:
        self._tools[name] = fn

    def names(self) -> list[str]:
        return sorted(self._tools)

    async def call(self, name: str, args: dict[str, Any]) -> str:
        fn = self._tools.get(name)
        if fn is None:
            raise ToolError(f"unknown tool: {name!r}")
        try:
            result = fn(args)
            if asyncio.iscoroutine(result):
                result = await result
            return str(result)
        except ToolError:
            raise
        except Exception as err:  # noqa: BLE001 - surface any tool failure as text
            raise ToolError(f"tool {name!r} failed: {err}") from err

    def _read_file(self, args: dict[str, Any]) -> str:
        path = self._safe_path(args.get("path", ""))
        if not path.is_file():
            raise ToolError(f"not a file: {args.get('path')!r}")
        return path.read_text(encoding="utf-8")

    def _write_file(self, args: dict[str, Any]) -> str:
        path = self._safe_path(args.get("path", ""))
        content = args.get("content", "")
        if not isinstance(content, str):
            raise ToolError("content must be a string")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"wrote {len(content)} bytes to {args.get('path')}"

    def _append_to_file(self, args: dict[str, Any]) -> str:
        path = self._safe_path(args.get("path", ""))
        content = args.get("content", "")
        if not isinstance(content, str):
            raise ToolError("content must be a string")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(content)
        return f"appended {len(content)} bytes to {args.get('path')}"

    async def _run_shell(self, args: dict[str, Any]) -> str:
        command = args.get("command", "")
        if not command or not isinstance(command, str):
            raise ToolError("command must be a non-empty string")
        timeout = float(args.get("timeout", 120))
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(self.root),
        )
        try:
            out_b, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError as err:
            proc.kill()
            await proc.wait()
            raise ToolError(f"command timed out after {timeout}s") from err
        out = out_b.decode("utf-8", errors="replace")
        return f"exit={proc.returncode}\n{out}"

    async def _raise_alarm(self, args: dict[str, Any]) -> str:
        try:
            import winsound

            duration = int(args.get("duration", 2))
            for _ in range(max(1, duration)):
                winsound.Beep(1000, 400)
            return "alarm sounded"
        except Exception:  # noqa: BLE001 - non-Windows or no audio
            print("\a", end="", flush=True)
            return "alarm (bell) sounded"


_TOOL_CALL_RE = re.compile(
    r'<tool_call\s+name="(?P<name>[^"]+)"\s*>(?P<body>.*?)</tool_call>',
    re.DOTALL,
)


def parse_tool_calls(text: str) -> list[tuple[str, dict[str, Any]]]:
    """Extract (name, args) pairs from a model response.

    Accepts blocks of the form:
        <tool_call name="write_file">{"path": "x", "content": "y"}</tool_call>
    The body must be JSON. Malformed blocks are skipped, not raised, so a
    stray block never crashes the loop.
    """
    calls: list[tuple[str, dict[str, Any]]] = []
    for m in _TOOL_CALL_RE.finditer(text):
        name = m.group("name").strip()
        body = m.group("body").strip()
        try:
            args = json.loads(body) if body else {}
        except json.JSONDecodeError:
            continue
        if not isinstance(args, dict):
            continue
        calls.append((name, args))
    return calls
