import pytest

from mandown.sources import BaseSource


def test_init() -> None:
    url = "test.test"
    testee = BaseSource(url)
    assert testee.url == url


def test_unimplemented() -> None:
    """
    Test any generic subclass to ensure
    that functions must be properly defined.
    """
    url = "test.test"
    testee = BaseSource(url)
    with pytest.raises(NotImplementedError):
        testee.metadata  # noqa: B018

    with pytest.raises(NotImplementedError):
        testee.chapters  # noqa: B018
