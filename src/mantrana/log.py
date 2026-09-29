"""Shared conversation log with pinning and trimming."""

from dataclasses import dataclass, field


@dataclass
class LogEntry:
    who: str
    text: str
    pinned: bool = False


@dataclass
class Log:
    trim_after: int = 15
    entries: list[LogEntry] = field(default_factory=list)

    def append(self, who: str, text: str) -> None:
        self.entries.append(LogEntry(who=who, text=text, pinned=False))

    def pin(self, who: str, text: str) -> None:
        self.entries.append(LogEntry(who=who, text=text, pinned=True))

    def turn_count(self) -> int:
        return sum(1 for e in self.entries if not e.pinned)

    def render(self) -> str:
        return "\n".join(f"[{e.who}]: {e.text}" for e in self.entries)

    def render_trimmed(self) -> str:
        pinned_idx = [i for i, e in enumerate(self.entries) if e.pinned]
        unpinned_idx = [i for i, e in enumerate(self.entries) if not e.pinned]
        if len(unpinned_idx) > self.trim_after:
            unpinned_idx = unpinned_idx[-self.trim_after :]
        keep = sorted(pinned_idx + unpinned_idx)
        return "\n".join(f"[{self.entries[i].who}]: {self.entries[i].text}" for i in keep)

    def last(self, n: int = 1) -> list[LogEntry]:
        return self.entries[-n:]