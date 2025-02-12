import pytest
from pathlib import Path
import tomllib
import networkx as nx

@pytest.fixture(scope="session")
def config():
    with open(Path("testdata") / "config.toml", "rb") as handle:
        config_data = tomllib.load(handle)
    return config_data
