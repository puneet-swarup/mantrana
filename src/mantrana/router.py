"""Moderator protocol parsing and invariant enforcement."""

import re

from .config import CouncilConfig

TARGET_RE = re.compile(r"@([A-Z][A-Z0-9_\-]*)")
START_RE = re.compile(r"<start>(.*?)</start>", re.S)
FINAL_RE = re.compile(r"<final>(.*?)</final>", re.S)


class Router:
    def __init__(self, config: CouncilConfig):
        self.config = config

    def parse_targets(self, reply: str) -> list[str]:
        """Extract @NAME tags in order, dedup, preserve first occurrence."""
        seen: list[str] = []
        for m in TARGET_RE.finditer(reply):
            name = m.group(1)
            if name not in seen:
                seen.append(name)
        return seen

    def parse_start(self, reply: str) -> list[str]:
        block = START_RE.search(reply)
        if not block:
            return []
        return self.parse_targets(block.group(1))

    def is_final(self, reply: str) -> bool:
        return FINAL_RE.search(reply) is not None

    def extract_final(self, reply: str) -> str:
        m = FINAL_RE.search(reply)
        return m.group(1).strip() if m else reply.strip()

    def enforce_invariants(self, picks: list[str], problem: str) -> list[str]:
        forced = list(self.config.moderator.invariants.always_include)
        low = problem.lower()
        for rule in self.config.moderator.invariants.per_domain:
            if any(k.lower() in low for k in rule.match):
                forced.extend(rule.must_include)
        return sorted(set(picks) | set(forced))