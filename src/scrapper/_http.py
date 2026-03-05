import logging
import cloudscraper

logger = logging.getLogger(__name__)


def get_page_html(url, timeout=10):
    """Fetch page HTML using cloudscraper and return the source text.

    Raises RuntimeError on network errors (keeps behaviour of previous scrapers).
    """
    scraper = cloudscraper.create_scraper()
    try:
        resp = scraper.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        logger.exception("Failed to fetch page HTML")
        raise RuntimeError(f"Failed to get URL {url}: {e}")

    return resp.text
