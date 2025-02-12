import json
from pathlib import Path

import pytest
import tomllib


@pytest.fixture(scope="session")
def config():
    with open(Path("testdata") / "config.toml", "rb") as handle:
        config_data = tomllib.load(handle)
    return config_data


@pytest.fixture(scope="session")
def sram():
    with open(Path("testdata") / "sram.json", "rb") as handle:
        sram_data = json.load(handle)
    return sram_data
