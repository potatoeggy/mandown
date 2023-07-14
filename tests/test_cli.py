import sys

import pytest
from typer import Exit

from mandown import BaseComic, __version_str__, cli


def assert_expected_output(capsys, input: str, output: str) -> None:
    sys.argv = input.split()

    with pytest.raises((Exit, SystemExit)):
        cli.main()

    captured = capsys.readouterr()
    assert output in captured.out


def test_cli_query(capsys) -> None:
    url = "https://mangasee123.com/manga/Kaguya-Wants-To-Be-Confessed-To"

    res = cli.cli_query(url)
    assert isinstance(res, BaseComic)

    captured = capsys.readouterr()
    assert f"Searching sources for {url}" in captured.out


def test_invalid_cli_query(capsys) -> None:
    with pytest.raises(Exit):
        cli.cli_query("invalid")

    captured = capsys.readouterr()
    assert "Could not match URL with available sources" in captured.out


def test_callbacks(capsys) -> None:
    assert_expected_output(capsys, "mandown -v", f"mandown {__version_str__}")
    assert_expected_output(capsys, "mandown --version", f"mandown {__version_str__}")

    assert_expected_output(capsys, "mandown --help", "Usage: mandown [OPTIONS] COMMAND")
    assert_expected_output(capsys, "mandown", "Usage: mandown [OPTIONS] COMMAND")

    assert_expected_output(
        capsys, "mandown --supported-sites", "Webtoons: https://webtoons.com"
    )

    assert_expected_output(capsys, "mandown -l", " - Kobo Sage: 'sage'")
