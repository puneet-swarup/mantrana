"""Client factory. Maps a model name to a ModelClient instance.

Reads config/models.yaml and constructs the right client kind. The factory
is the single place where a model name becomes a live client, so the
orchestrator stays ignorant of how any model is reached.
"""

from pathlib import Path
from typing import Any

import yaml

from .base import ModelClient
from .fake import FakeClient
from .subprocess_client import SubprocessClient


class UnknownClientKind(ValueError):
    """Raised when models.yaml names a client kind with no implementation."""


def load_model_registry(root: Path) -> dict[str, dict[str, Any]]:
    """Read config/models.yaml into a plain dict."""
    path = root / "config" / "models.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping of model name to config")
    return data


def build_client(
    model: str,
    role: str,
    registry: dict[str, dict[str, Any]],
    working_dir: Path | None = None,
) -> ModelClient:
    """Construct a client for one role from its model binding."""
    spec = registry.get(model)
    if spec is None:
        raise KeyError(f"Model {model!r} is not defined in config/models.yaml")

    kind = spec.get("client", "fake")

    if kind == "fake":
        return FakeClient(role)

    if kind == "subprocess":
        command = spec.get("command")
        if not command:
            raise ValueError(
                f"Model {model!r} uses client 'subprocess' but has no 'command'"
            )
        return SubprocessClient(
            command=command,
            session=role,
            role=role,
            working_dir=working_dir,
            timeout=float(spec.get("timeout", 600)),
        )

    raise UnknownClientKind(f"Unknown client kind {kind!r} for model {model!r}")


def build_clients_from_config(
    root: Path, config: object
) -> dict[str, ModelClient]:
    """Build a {role: client} map for the moderator and every agent.

    The moderator is keyed as 'moderator'. Each agent is keyed by its
    role name. Clients are constructed from config/models.yaml via each
    role's bound model name.
    """
    registry = load_model_registry(root)
    clients: dict[str, ModelClient] = {}

    moderator_model = config.moderator.model  # type: ignore[attr-defined]
    clients["moderator"] = build_client(
        moderator_model, "moderator", registry, working_dir=root
    )

    for role, acfg in config.agents.items():  # type: ignore[attr-defined]
        clients[role] = build_client(acfg.model, role, registry, working_dir=root)

    return clients
