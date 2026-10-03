"""Tests for the client factory and subprocess client."""

from pathlib import Path

import pytest
from src.mantrana.clients import (
    FakeClient,
    SubprocessClient,
    UnknownClientKind,
    build_client,
    load_model_registry,
)


@pytest.fixture
def registry() -> dict[str, dict]:
    return {
        "fake-model": {"client": "fake"},
        "cli-model": {"client": "subprocess", "command": "forge-agent", "timeout": 30},
        "broken-cli": {"client": "subprocess"},
        "weird": {"client": "carrier-pigeon"},
    }


def test_build_fake_client(registry: dict[str, dict]) -> None:
    client = build_client("fake-model", "ARCHITECT", registry)
    assert isinstance(client, FakeClient)


def test_build_subprocess_client(registry: dict[str, dict]) -> None:
    client = build_client("cli-model", "CRITIC", registry)
    assert isinstance(client, SubprocessClient)
    assert client.session == "CRITIC"
    assert client.role == "CRITIC"
    assert client.timeout == 30.0


def test_unknown_model_raises(registry: dict[str, dict]) -> None:
    with pytest.raises(KeyError):
        build_client("nope", "SME", registry)


def test_subprocess_without_command_raises(registry: dict[str, dict]) -> None:
    with pytest.raises(ValueError):
        build_client("broken-cli", "SME", registry)


def test_unknown_client_kind_raises(registry: dict[str, dict]) -> None:
    with pytest.raises(UnknownClientKind):
        build_client("weird", "SME", registry)


def test_load_model_registry() -> None:
    root = Path(__file__).resolve().parent.parent
    registry = load_model_registry(root)
    assert "deepseek" in registry
    assert registry["deepseek"]["client"] == "fake"
