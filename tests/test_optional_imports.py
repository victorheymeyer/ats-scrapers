"""Importing the scraper registry must not require optional extras."""

from __future__ import annotations

import subprocess
import sys
import textwrap

_BLOCK_BS4 = textwrap.dedent(
    """
    import sys

    sys.modules["bs4"] = None  # any `import bs4` now raises ImportError
    """
)


def _run_without_bs4(body: str) -> subprocess.CompletedProcess[str]:
    # A fresh interpreter: the parent has already imported every scraper module.
    return subprocess.run(
        [sys.executable, "-c", _BLOCK_BS4 + textwrap.dedent(body)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_scrapers_import_without_beautifulsoup4() -> None:
    result = _run_without_bs4(
        """
        from ats_scrapers.scrapers import get_scraper  # noqa: F401
        from ats_scrapers.scrapers.herp import HerpScraper  # noqa: F401
        from ats_scrapers.scrapers.hrmos import HrmosScraper  # noqa: F401
        from ats_scrapers.scrapers.keka import KekaScraper  # noqa: F401
        """
    )

    assert result.returncode == 0, result.stderr


def test_bs4_scrapers_raise_scraper_error_when_parsing_without_beautifulsoup4() -> None:
    result = _run_without_bs4(
        """
        from ats_scrapers.exceptions import ScraperError
        from ats_scrapers.scrapers.herp import HerpScraper
        from ats_scrapers.scrapers.hrmos import HrmosScraper
        from ats_scrapers.scrapers.keka import _html_to_text

        for parse in (
            lambda: HerpScraper("acme")._parse_listing("<html></html>"),
            lambda: HrmosScraper("acme")._parse_page("<html></html>"),
            lambda: _html_to_text("<p>x</p>"),
        ):
            try:
                parse()
            except ScraperError as exc:
                assert "beautifulsoup4" in str(exc)
            else:
                raise AssertionError("expected ScraperError")
        """
    )

    assert result.returncode == 0, result.stderr
