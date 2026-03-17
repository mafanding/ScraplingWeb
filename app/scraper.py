from scrapling.fetchers import Fetcher
from urllib.parse import urljoin
from typing import Optional


def extract_links(url: str, proxy: Optional[str] = None) -> list[dict]:
    fetcher = Fetcher(auto_match=False)
    page = fetcher.get(url, proxy=proxy)  # proxy=None is ignored by Scrapling
    results = []
    for anchor in page.css('a'):
        href = (anchor.attrib.get('href') or '').strip()
        if not href or href.startswith(('#', 'javascript:')):
            continue
        abs_url = urljoin(url, href)
        text = (anchor.text or '').strip() or abs_url
        results.append({"title": text, "url": abs_url})
    return results
