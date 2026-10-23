import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel
from pypdf import PdfReader

from investor_db.constants import BLOCKED_DOMAINS, PAGES_CACHE_DIR, USER_AGENT
from investor_db.dedup import registrable_domain

PDF_CONTENT_TYPE = "application/pdf"
TIMEOUT_SECONDS = 30.0


class Page(BaseModel):
    url: str
    status_code: int
    content_type: str
    text: str
    sha256: str
    fetched_at: datetime


class FetchRefused(Exception):
    pass


def _cache_path(url: str) -> Path:
    return PAGES_CACHE_DIR / f"{hashlib.sha256(url.encode()).hexdigest()}.json"


def _client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=TIMEOUT_SECONDS,
    )


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    return soup.get_text(" ")


def pdf_to_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    return " ".join(page.extract_text() or "" for page in reader.pages)


def is_blocked(url: str) -> bool:
    return registrable_domain(url) in BLOCKED_DOMAINS


_robots_cache: dict[str, RobotFileParser] = {}


def robots_allows(url: str, client: httpx.Client) -> bool:
    parts = urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    if origin not in _robots_cache:
        parser = RobotFileParser()
        try:
            response = client.get(f"{origin}/robots.txt")
            lines = response.text.splitlines() if response.status_code == 200 else []
        except httpx.HTTPError:
            lines = []
        parser.parse(lines)
        _robots_cache[origin] = parser
    return _robots_cache[origin].can_fetch(USER_AGENT, url)


def fetch(url: str) -> Page:
    cache_file = _cache_path(url)
    if cache_file.exists():
        return Page.model_validate_json(cache_file.read_text())
    if is_blocked(url):
        raise FetchRefused(f"blocked domain: {url}")
    with _client() as client:
        if not robots_allows(url, client):
            raise FetchRefused(f"robots.txt disallows: {url}")
        response = client.get(url)
    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    if content_type == PDF_CONTENT_TYPE:
        text = pdf_to_text(response.content)
    else:
        text = html_to_text(response.text)
    page = Page(
        url=url,
        status_code=response.status_code,
        content_type=content_type,
        text=text,
        sha256=hashlib.sha256(response.content).hexdigest(),
        fetched_at=datetime.now(UTC),
    )
    PAGES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(page.model_dump(mode="json"), ensure_ascii=False))
    return page
