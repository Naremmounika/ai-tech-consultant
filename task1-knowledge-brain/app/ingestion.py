import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.config import HELP_CENTER_SITEMAP, INDEX_PATH

HEADERS = {
    "User-Agent": "AI-Tech-Consultant-KnowledgeBrain/1.1"
}

MAX_PAGES = 100
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def get_sitemap_urls(
    sitemap_url: str,
    visited: set[str] | None = None,
    depth: int = 0,
) -> list[str]:
    """Read page URLs from a sitemap or sitemap index."""
    if visited is None:
        visited = set()

    if sitemap_url in visited or depth > 2:
        return []

    visited.add(sitemap_url)

    with httpx.Client(
        timeout=30.0,
        follow_redirects=True,
        headers=HEADERS,
    ) as client:
        response = client.get(sitemap_url)
        response.raise_for_status()

    root = ET.fromstring(response.content)
    urls: list[str] = []

    for element in root:
        loc_element = element.find("{*}loc")

        if loc_element is None or not loc_element.text:
            continue

        loc = loc_element.text.strip()

        if element.tag.endswith("sitemap"):
            remaining = MAX_PAGES - len(urls)

            if remaining > 0:
                urls.extend(
                    get_sitemap_urls(loc, visited, depth + 1)[
                        :remaining
                    ]
                )

        elif element.tag.endswith("url"):
            urls.append(loc)

        if len(urls) >= MAX_PAGES:
            break

    return list(dict.fromkeys(urls))[:MAX_PAGES]


def extract_page(url: str) -> dict | None:
    """Download a page and extract its readable content."""
    try:
        with httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers=HEADERS,
        ) as client:
            response = client.get(url)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "")

        if "html" not in content_type.lower():
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "svg",
                "nav",
                "footer",
            ]
        ):
            element.decompose()

        title = (
            soup.title.get_text(" ", strip=True)
            if soup.title
            else url
        )

        main = (
            soup.find("main")
            or soup.find("article")
            or soup.body
        )

        if main is None:
            return None

        text = main.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) < 80:
            return None

        return {
            "title": title,
            "url": url,
            "text": text,
        }

    except (httpx.HTTPError, ValueError, ET.ParseError):
        return None


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    text = re.sub(r"\s+", " ", text).strip()

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def ingest_knowledge_base() -> dict:
    """Fetch help-center pages and save their text chunks."""
    page_urls = get_sitemap_urls(HELP_CENTER_SITEMAP)

    documents = []
    failed_pages = 0

    for url in page_urls:
        page = extract_page(url)

        if page is None:
            failed_pages += 1
            continue

        for index, chunk in enumerate(chunk_text(page["text"])):
            documents.append(
                {
                    "id": f'{url}#chunk-{index}',
                    "title": page["title"],
                    "url": page["url"],
                    "text": chunk,
                }
            )

    if not documents:
        raise RuntimeError(
            "No help-center content was indexed. "
            "Check the sitemap URL and internet connection."
        )

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sitemap": HELP_CENTER_SITEMAP,
        "pages_discovered": len(page_urls),
        "pages_failed_or_skipped": failed_pages,
        "chunks_indexed": len(documents),
        "documents": documents,
    }

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = INDEX_PATH.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary_path.replace(INDEX_PATH)

    return {
        "pages_discovered": len(page_urls),
        "pages_failed_or_skipped": failed_pages,
        "chunks_indexed": len(documents),
        "index_path": str(INDEX_PATH),
        "created_at": payload["created_at"],
    }