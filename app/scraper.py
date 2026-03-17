import logging
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode
from typing import Optional

logger = logging.getLogger(__name__)


def _extract_title(anchor) -> str:
    """Extract readable title from an anchor element using multiple strategies."""
    # 1. All descendant text (handles <span>, <strong>, etc.)
    all_text = ' '.join(anchor.css('::text').getall()).strip()
    if all_text:
        return ' '.join(all_text.split())  # normalize whitespace

    # 2. Alt text from contained images
    for img in anchor.css('img'):
        alt = (img.attrib.get('alt') or '').strip()
        if alt:
            return alt

    # 3. title or aria-label attribute on the anchor itself
    for attr in ('title', 'aria-label'):
        val = (anchor.attrib.get(attr) or '').strip()
        if val:
            return val

    return ''


def _normalize_url(url: str) -> str:
    """Normalize a URL for deduplication."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    host = parsed.netloc.lower()
    path = parsed.path.rstrip('/') or '/'
    # Sort query parameters for consistent comparison
    query = urlencode(sorted(parse_qsl(parsed.query)))
    return urlunparse((scheme, host, path, parsed.params, query, ''))


def _parse_links(page, base_url: str) -> list[dict]:
    seen: dict[str, dict] = {}
    for anchor in page.css('a'):
        href = (anchor.attrib.get('href') or '').strip()
        if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            continue
        abs_url = urljoin(base_url, href)
        key = _normalize_url(abs_url)
        title = _extract_title(anchor) or abs_url
        # On duplicate: prefer entry with a real title over URL-as-title
        if key in seen:
            existing = seen[key]
            if existing['title'] == existing['url'] and title != abs_url:
                existing['title'] = title
            continue
        seen[key] = {"title": title, "url": abs_url}
    return list(seen.values())


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
        page = StealthyFetcher(auto_match=False).fetch(url, proxy=proxy)
        links = _parse_links(page, url)
        if links:
            logger.info("Stealth fetcher succeeded (%d links)", len(links))
            return links, "stealth"
        logger.info("Stealth fetcher returned no links, falling back to browser")
    except Exception as e:
        logger.info("Stealth fetcher failed (%s), falling back to browser", e)

    page = DynamicFetcher(auto_match=False).fetch(url, proxy=proxy)
    links = _parse_links(page, url)
    logger.info("Dynamic fetcher returned %d links", len(links))
    return links, "dynamic"
