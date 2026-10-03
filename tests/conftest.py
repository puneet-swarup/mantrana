"""Shared test fixtures."""

from pathlib import Path

import pytest
from src.mantrana.config import CouncilConfig


@pytest.fixture
def root() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture
def config(root: Path) -> CouncilConfig:
    return CouncilConfig.load(root)
