from rapidplugin.domain.package import Package
import pytest
import lizard


@pytest.fixture
def path():
    return None


@pytest.fixture
def forge():
    return None


@pytest.fixture
def product():
    return None


@pytest.fixture
def version():
    return None


@pytest.fixture
def package(forge, product, version, path):
    p = Package(forge, product, version, path)
    yield p
    p.clear()


@pytest.mark.parametrize('forge, product, version, path', ['mvn', 'fasten-project:fasten', '1.0.0', '/repos/fasten'])
def test_metrics():
    assert True
