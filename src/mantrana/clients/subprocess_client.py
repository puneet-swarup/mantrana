"""Subprocess-backed model client.

Drives an external agent CLI (e.g. the forked forge-agent) as the model
behind a role. Each client instance owns one named session, so multiple
roles can run concurrently without colliding on a shared browser profile.
"""

import asyncio
import os
import shutil
from pathlib import Path


class SubprocessClient:
    """Runs a CLI agent and reads its final answer from stdout.

    The CLI is invoked once per query with the prompt on stdin. Output is
    captured and returned as text. A sentinel line delimits the answer so
    progress chatter on stdout does not leak into the model response.
    """

    RESULT_START = "<<<MANTRANA_RESULT>>>"
    RESULT_END = "<<<END_MANTRANA_RESULT>>>"

    def __init__(
        self,
        command: str,
        session: str,
        role: str | None = None,
        working_dir: Path | None = None,
        timeout: float = 600.0,
    ) -> None:
        self.command = command
        self.session = session
        self.role = role or session
        self.working_dir = working_dir
        self.timeout = timeout

    def _resolve_command(self) -> str:
        resolved = shutil.which(self.command)
        if resolved is None:
            raise FileNotFoundError(
                f"CLI command not found on PATH: {self.command!r}. "
                "Install the agent CLI or set the command in config/models.yaml."
            )
        return resolved

    def _build_argv(self) -> list[str]:
        exe = self._resolve_command()
        return [
            exe,
            "--session",
            self.session,
            "--role",
            self.role,
            "--no-tui",
            "--compact",
        ]

    async def query(self, prompt: str) -> str:
        argv = self._build_argv()
        env = dict(os.environ)
        env["FORGE_SESSION_NAME"] = self.session
        env["FORGE_ROLE"] = self.role

        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.working_dir) if self.working_dir else None,
            env=env,
        )

        try:
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(prompt.encode("utf-8")), timeout=self.timeout
            )
        except asyncio.TimeoutError as err:
            proc.kill()
            await proc.wait()
            raise TimeoutError(
                f"Agent CLI timed out after {self.timeout}s (session={self.session!r})"
            ) from err

        stdout = stdout_b.decode("utf-8", errors="replace")
        stderr = stderr_b.decode("utf-8", errors="replace")

        if proc.returncode != 0:
            raise RuntimeError(
                f"Agent CLI exited {proc.returncode} (session={self.session!r}): "
                f"{stderr.strip() or stdout.strip()}"
            )

        return self._extract_result(stdout)

    def _extract_result(self, stdout: str) -> str:
        start = stdout.find(self.RESULT_START)
        end = stdout.find(self.RESULT_END)
        if start != -1 and end != -1 and end > start:
            return stdout[start + len(self.RESULT_START) : end].strip()
        return stdout.strip()

    async def is_available(self) -> bool:
        try:
            self._resolve_command()
            return True
        except FileNotFoundError:
            return False

    async def close(self) -> None:
        return None
