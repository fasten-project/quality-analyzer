import pytest
from rapidplugin.entrypoint import RapidPlugin

@pytest.fixture
def plugin():
    plugin = RapidPlugin(base_dir="src")
    return  plugin


def test_no_sourcesURL(payload: str):
    path = plugin()._

