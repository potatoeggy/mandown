import pytest

from mandown.sources.common_source import CommonSource


def test_init() -> None:
    url = "test.test"
    testee = CommonSource(url)
    assert testee.url == url


def test_unimplemented() -> None:
    """
    Test any generic subclass to ensure
    that functions must be properly defined.
    """
    url = "test.test"
    testee = CommonSource(url)
    with pytest.raises(NotImplementedError):
        testee.metadata  # noqa: B018

    with pytest.raises(NotImplementedError):
        testee.chapters  # noqa: B018
