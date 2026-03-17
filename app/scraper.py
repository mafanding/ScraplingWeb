import logging
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from urllib.parse import urljoin
from typing import Optional

logger = logging.getLogger(__name__)


def _parse_links(page, base_url: str) -> list[dict]:
    results = []
    for anchor in page.css('a'):
        href = (anchor.attrib.get('href') or '').strip()
        if not href or href.startswith(('#', 'javascript:')):
            continue
        abs_url = urljoin(base_url, href)
        text = (anchor.text or '').strip() or abs_url
        results.append({"title": text, "url": abs_url})
    return results


def extract_links(url: str, proxy: Optional[str] = None) -> tuple[list[dict], str]:
    """Returns (links, fetcher_used). fetcher_used is 'basic', 'stealth', or 'dynamic'."""
    try:
        page = Fetcher(auto_match=False).get(url, proxy=proxy)
        links = _parse_links(page, url)
        if links:
            logger.info("Basic fetcher succeeded (%d links)", len(links))
            return links, "basic"
        logger.info("Basic fetcher returned no links, falling back to stealth")
    except Exception as e:
        logger.info("Basic fetcher failed (%s), falling back to stealth", e)

    try:
        page = StealthyFetcher(auto_match=False).get(url, proxy=proxy)
        links = _parse_links(page, url)
        if links:
            logger.info("Stealth fetcher succeeded (%d links)", len(links))
            return links, "stealth"
        logger.info("Stealth fetcher returned no links, falling back to browser")
    except Exception as e:
        logger.info("Stealth fetcher failed (%s), falling back to browser", e)

    page = DynamicFetcher(auto_match=False).get(url, proxy=proxy)
    links = _parse_links(page, url)
    logger.info("Dynamic fetcher returned %d links", len(links))
    return links, "dynamic"
