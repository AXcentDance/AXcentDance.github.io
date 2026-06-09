#!/usr/bin/env python3
"""Generate AXcent Dance topic clusters and internal-link recommendations.

This script is intentionally report-only. It reads static HTML files, creates
or reuses cached OpenAI embeddings, and writes Markdown/JSON outputs under
System/topic_map without modifying website pages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from bs4 import BeautifulSoup


ROOT_DIR = Path(__file__).resolve().parents[1]
SITE_URL = "https://axcentdance.com"
MODEL = "text-embedding-3-small"
OUTPUT_DIR = ROOT_DIR / "System" / "topic_map"
CACHE_FILE = OUTPUT_DIR / "embeddings_cache.json"
REPORT_FILE = OUTPUT_DIR / "topic_authority_report.md"
PAGE_INDEX_FILE = OUTPUT_DIR / "page_index.json"

IGNORE_DIRS = {
    ".git",
    ".gemini",
    "__pycache__",
    "assets",
    "node_modules",
    "scripts",
    "System",
    "tmp",
}

PILLAR_WEIGHTS = {
    "index": 1.35,
    "de/index": 1.35,
    "schedule": 1.3,
    "de/schedule": 1.3,
    "registration": 1.25,
    "de/registration": 1.25,
    "beginner-guide": 1.35,
    "de/beginner-guide": 1.35,
    "guide-bachata": 1.3,
    "de/guide-bachata": 1.3,
    "guide-bachata-sensual": 1.25,
    "de/guide-bachata-sensual": 1.25,
    "events": 1.25,
    "de/events": 1.25,
    "private-lessons": 1.2,
    "de/private-lessons": 1.2,
    "room-rental": 1.2,
    "de/room-rental": 1.2,
    "education": 1.25,
    "de/education": 1.25,
}

TOPIC_KEYWORDS = {
    "Beginner Bachata": [
        "beginner",
        "anfanger",
        "anfänger",
        "first class",
        "erste",
        "hobby",
        "wear",
        "anziehen",
        "meet people",
    ],
    "Bachata Zurich": ["bachata", "zurich", "zürich", "altstetten", "course", "kurs", "classes", "tanzkurs"],
    "Events & Community": ["event", "congress", "party", "social", "community", "bootcamp", "festival"],
    "Music & Education": ["music", "musik", "history", "geschichte", "roots", "musicality", "education", "instrument"],
    "Private Lessons": ["private", "1-on-1", "coaching", "lesson", "stunden", "privat"],
    "Room Rental": ["rental", "rent", "space", "studio", "raum", "mieten", "pilates", "yoga"],
    "Wedding & Corporate": ["wedding", "hochzeit", "corporate", "team", "firmenevent", "teambuilding"],
}


@dataclass
class PageData:
    path: str
    clean_path: str
    url: str
    language: str
    page_type: str
    title: str
    description: str
    h1: str
    text: str
    content_hash: str
    internal_links: List[str]
    word_count: int


@dataclass
class LinkSuggestion:
    source: str
    target: str
    score: float
    similarity: float
    priority: str
    topic: str
    suggested_anchor: str
    reason: str


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_path_from_rel(rel_path: str) -> str:
    normalized = rel_path.replace("\\", "/")
    if normalized.endswith(".html"):
        normalized = normalized[:-5]
    if normalized in {"index", "de/index"}:
        return normalized
    return normalized.strip("/")


def clean_url_for_path(clean_path: str) -> str:
    if clean_path == "index":
        return SITE_URL + "/"
    return f"{SITE_URL}/{clean_path}"


def detect_language(rel_path: str) -> str:
    return "de" if rel_path.replace("\\", "/").startswith("de/") else "en"


def detect_page_type(clean_path: str) -> str:
    name = clean_path.split("/")[-1]
    if clean_path in {"index", "de/index"}:
        return "home"
    if "/blog-posts/" in clean_path or clean_path.startswith("blog-posts/") or clean_path.startswith("de/blog-posts/"):
        return "blog"
    if "guide" in name or name in {"education", "faq", "etiquette"}:
        return "guide"
    if name in {"schedule", "registration", "events", "contact", "about", "blog"}:
        return "core"
    if any(token in name for token in ("bachata-", "lady-styling", "private-lessons", "wedding-dance", "corporate-events", "room-rental")):
        return "service"
    if name.startswith("thank-you") or name in {"privacy", "terms", "imprint", "404", "cart"}:
        return "utility"
    return "page"


def should_ignore_dir(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def discover_html_files(root_dir: Path) -> List[Path]:
    files = []
    for path in root_dir.rglob("*.html"):
        rel = path.relative_to(root_dir)
        if should_ignore_dir(rel):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(root_dir).as_posix())


def normalize_internal_link(href: str, source_rel_path: str, root_dir: Optional[Path] = None) -> Optional[str]:
    href = href.strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None

    parsed = urllib.parse.urlparse(href)
    if parsed.scheme and parsed.netloc:
        if parsed.netloc.lower() not in {"axcentdance.com", "www.axcentdance.com"}:
            return None
        link_path = parsed.path
    else:
        link_path = parsed.path

    if not link_path:
        return None

    if link_path.startswith("/"):
        target = Path(link_path.lstrip("/"))
    else:
        source_dir = Path(source_rel_path).parent
        target = (root_dir or Path.cwd()) / source_dir / urllib.parse.unquote(link_path)
        target = target.resolve()
        root = (root_dir or Path.cwd()).resolve()
        try:
            target = target.relative_to(root)
        except ValueError:
            target = source_dir / urllib.parse.unquote(link_path)

    target_str = target.as_posix().strip("/")
    if not target_str:
        return "index"
    if target_str.endswith("/"):
        target_str += "index"
    if target_str.endswith(".html"):
        target_str = target_str[:-5]
    if "." in Path(target_str).name:
        return None
    return target_str


def normalize_internal_link_for_root(href: str, source_rel_path: str, root_dir: Path) -> Optional[str]:
    return normalize_internal_link(href, source_rel_path, root_dir=root_dir)


def extract_page(file_path: Path, root_dir: Path) -> PageData:
    rel_path = file_path.relative_to(root_dir).as_posix()
    html = file_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    title = clean_text(soup.title.get_text(" ")) if soup.title else ""
    meta = soup.find("meta", attrs={"name": "description"})
    description = clean_text(meta.get("content", "")) if meta else ""
    h1_tag = soup.find("h1")
    h1 = clean_text(h1_tag.get_text(" ")) if h1_tag else ""

    for tag in soup(["script", "style", "noscript", "iframe", "svg"]):
        tag.decompose()
    for selector in ("header", "nav", "footer", "form"):
        for tag in soup.find_all(selector):
            tag.decompose()

    main = soup.find("main") or soup.body or soup
    internal_links = []
    for link in main.find_all("a", href=True):
        normalized = normalize_internal_link_for_root(link["href"], rel_path, root_dir)
        if normalized and normalized not in internal_links:
            internal_links.append(normalized)

    text = clean_text(main.get_text(" "))
    embedding_text = clean_text(" ".join([title, description, h1, text]))
    content_hash = hashlib.sha256(embedding_text.encode("utf-8")).hexdigest()
    clean_path = clean_path_from_rel(rel_path)

    return PageData(
        path=rel_path,
        clean_path=clean_path,
        url=clean_url_for_path(clean_path),
        language=detect_language(rel_path),
        page_type=detect_page_type(clean_path),
        title=title,
        description=description,
        h1=h1,
        text=text,
        content_hash=content_hash,
        internal_links=internal_links,
        word_count=len(text.split()),
    )


def load_cache(cache_file: Path) -> Dict[str, dict]:
    if not cache_file.exists():
        return {}
    try:
        return json.loads(cache_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def get_cached_embedding(cache: Dict[str, dict], page: PageData, refresh: bool = False) -> Optional[List[float]]:
    item = cache.get(page.path)
    if refresh or not item:
        return None
    if item.get("content_hash") != page.content_hash or item.get("model") != MODEL:
        return None
    embedding = item.get("embedding")
    if isinstance(embedding, list) and embedding:
        return [float(value) for value in embedding]
    return None


def request_embeddings(texts: Sequence[str], api_key: str, model: str = MODEL, retries: int = 3) -> List[List[float]]:
    payload = json.dumps({"model": model, "input": list(texts), "encoding_format": "float"}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            return [item["embedding"] for item in sorted(data["data"], key=lambda row: row["index"])]
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in {429, 500, 502, 503, 504} and attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"OpenAI embeddings request failed with HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            if attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"OpenAI embeddings request failed: {exc}") from exc

    raise RuntimeError("OpenAI embeddings request failed after retries.")


def embedding_input(page: PageData) -> str:
    # Keep the input focused on unique page semantics, not repeated site chrome.
    return clean_text(
        "\n".join(
            [
                f"Title: {page.title}",
                f"Description: {page.description}",
                f"H1: {page.h1}",
                page.text[:12000],
            ]
        )
    )


def ensure_embeddings(
    pages: Sequence[PageData],
    cache: Dict[str, dict],
    refresh: bool,
    api_key: Optional[str],
    batch_size: int = 32,
) -> Dict[str, List[float]]:
    embeddings: Dict[str, List[float]] = {}
    missing: List[PageData] = []

    for page in pages:
        cached = get_cached_embedding(cache, page, refresh)
        if cached is None:
            missing.append(page)
        else:
            embeddings[page.path] = cached

    if missing and not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is required to create missing embeddings. "
            "No report files were written."
        )

    for start in range(0, len(missing), batch_size):
        batch = missing[start : start + batch_size]
        vectors = request_embeddings([embedding_input(page) for page in batch], api_key)
        for page, vector in zip(batch, vectors):
            embeddings[page.path] = vector
            cache[page.path] = {
                "model": MODEL,
                "content_hash": page.content_hash,
                "embedding": vector,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

    return embeddings


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def infer_topic(page: PageData) -> str:
    haystack = f"{page.clean_path} {page.title} {page.description} {page.h1}".lower()
    best_topic = "General"
    best_score = 0
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in haystack)
        if score > best_score:
            best_topic = topic
            best_score = score
    return best_topic


def pillar_weight(page: PageData) -> float:
    weight = PILLAR_WEIGHTS.get(page.clean_path, 1.0)
    if page.page_type == "core":
        weight += 0.1
    if page.page_type == "guide":
        weight += 0.08
    if page.word_count >= 900:
        weight += 0.07
    return weight


def priority_from_score(score: float) -> str:
    if score >= 1.12:
        return "High"
    if score >= 0.95:
        return "Medium"
    return "Low"


def suggest_anchor(source: PageData, target: PageData) -> str:
    title = target.h1 or target.title or target.clean_path.replace("-", " ")
    title = re.sub(r"\s*\|\s*AXcent.*$", "", title).strip()
    if target.language == "de":
        if target.page_type == "core" and "schedule" in target.clean_path:
            return "Bachata-Stundenplan in Zürich"
        if "beginner" in target.clean_path:
            return "Bachata-Anfänger-Guide"
    else:
        if target.page_type == "core" and "schedule" in target.clean_path:
            return "weekly Bachata schedule"
        if "beginner" in target.clean_path:
            return "beginner Bachata guide"
    return title[:80]


def build_link_suggestions(
    pages: Sequence[PageData],
    embeddings: Dict[str, List[float]],
    max_suggestions: int,
) -> List[LinkSuggestion]:
    clean_to_page = {page.clean_path: page for page in pages}
    suggestions: List[LinkSuggestion] = []

    for source in pages:
        if source.page_type == "utility":
            continue
        source_embedding = embeddings.get(source.path)
        if not source_embedding:
            continue

        existing_links = set(source.internal_links)
        for target_path, target in clean_to_page.items():
            if source.path == target.path:
                continue
            if source.language != target.language:
                continue
            if target.page_type == "utility":
                continue
            if target_path in existing_links:
                continue

            target_embedding = embeddings.get(target.path)
            if not target_embedding:
                continue

            similarity = cosine_similarity(source_embedding, target_embedding)
            if similarity < 0.62:
                continue

            score = similarity * pillar_weight(target)
            if len(source.internal_links) <= 2:
                score += 0.08
            if source.page_type == "blog" and target.page_type in {"core", "guide", "service"}:
                score += 0.07
            topic = infer_topic(target)
            reason = f"Semantic similarity {similarity:.2f}; target type {target.page_type}; source has {len(source.internal_links)} internal links."
            suggestions.append(
                LinkSuggestion(
                    source=source.clean_path,
                    target=target.clean_path,
                    score=score,
                    similarity=similarity,
                    priority=priority_from_score(score),
                    topic=topic,
                    suggested_anchor=suggest_anchor(source, target),
                    reason=reason,
                )
            )

    suggestions.sort(key=lambda item: item.score, reverse=True)
    deduped: List[LinkSuggestion] = []
    seen_sources: Dict[str, int] = {}
    seen_pairs = set()
    for suggestion in suggestions:
        pair = (suggestion.source, suggestion.target)
        if pair in seen_pairs:
            continue
        if seen_sources.get(suggestion.source, 0) >= 3:
            continue
        deduped.append(suggestion)
        seen_pairs.add(pair)
        seen_sources[suggestion.source] = seen_sources.get(suggestion.source, 0) + 1
        if len(deduped) >= max_suggestions:
            break
    return deduped


def build_topic_clusters(
    pages: Sequence[PageData],
    embeddings: Dict[str, List[float]],
    per_locale_limit: int = 8,
) -> Dict[str, Dict[str, List[dict]]]:
    clusters: Dict[str, Dict[str, List[dict]]] = {"en": {}, "de": {}}
    for page in pages:
        topic = infer_topic(page)
        clusters.setdefault(page.language, {}).setdefault(topic, []).append(
            {
                "path": page.clean_path,
                "title": page.h1 or page.title,
                "type": page.page_type,
                "word_count": page.word_count,
                "strength": round(pillar_weight(page), 2),
            }
        )

    for locale_topics in clusters.values():
        for topic, items in locale_topics.items():
            items.sort(key=lambda item: (item["strength"], item["word_count"]), reverse=True)
            del items[per_locale_limit:]
    return clusters


def find_weak_pages(pages: Sequence[PageData]) -> List[PageData]:
    candidates = [
        page
        for page in pages
        if page.page_type not in {"utility", "home"} and len(page.internal_links) <= 1
    ]
    return sorted(candidates, key=lambda page: (page.language, len(page.internal_links), page.clean_path))


def find_overlaps(
    pages: Sequence[PageData],
    embeddings: Dict[str, List[float]],
    limit: int = 20,
) -> List[Tuple[PageData, PageData, float]]:
    overlaps = []
    for index, left in enumerate(pages):
        if left.page_type == "utility":
            continue
        for right in pages[index + 1 :]:
            if left.language != right.language or right.page_type == "utility":
                continue
            left_embedding = embeddings.get(left.path)
            right_embedding = embeddings.get(right.path)
            if not left_embedding or not right_embedding:
                continue
            similarity = cosine_similarity(left_embedding, right_embedding)
            if similarity >= 0.86:
                overlaps.append((left, right, similarity))
    overlaps.sort(key=lambda row: row[2], reverse=True)
    return overlaps[:limit]


def write_outputs(
    pages: Sequence[PageData],
    cache: Dict[str, dict],
    clusters: Dict[str, Dict[str, List[dict]]],
    suggestions: Sequence[LinkSuggestion],
    overlaps: Sequence[Tuple[PageData, PageData, float]],
    weak_pages: Sequence[PageData],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
    PAGE_INDEX_FILE.write_text(
        json.dumps([asdict(page) for page in pages], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    REPORT_FILE.write_text(
        render_report(pages, clusters, suggestions, overlaps, weak_pages),
        encoding="utf-8",
    )


def render_report(
    pages: Sequence[PageData],
    clusters: Dict[str, Dict[str, List[dict]]],
    suggestions: Sequence[LinkSuggestion],
    overlaps: Sequence[Tuple[PageData, PageData, float]],
    weak_pages: Sequence[PageData],
) -> str:
    lines = [
        "# AXcent Dance Topic Authority Report",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        "",
        "This report is read-only. It suggests internal links and topic priorities, but it does not edit website pages.",
        "",
        "## Summary",
        "",
        f"- Pages analyzed: {len(pages)}",
        f"- English pages: {sum(1 for page in pages if page.language == 'en')}",
        f"- German pages: {sum(1 for page in pages if page.language == 'de')}",
        f"- Link suggestions: {len(suggestions)}",
        f"- Weakly connected pages: {len(weak_pages)}",
        "",
        "## Topic Clusters",
        "",
    ]

    for locale in ("en", "de"):
        lines.append(f"### {locale.upper()}")
        lines.append("")
        for topic, items in sorted(clusters.get(locale, {}).items()):
            lines.append(f"#### {topic}")
            if not items:
                lines.append("- No pages found.")
            for item in items:
                lines.append(
                    f"- `{item['path']}` ({item['type']}, {item['word_count']} words, strength {item['strength']}): {item['title']}"
                )
            lines.append("")

    lines.extend(["## Recommended Internal Links", ""])
    if not suggestions:
        lines.append("No missing semantic internal-link opportunities were found above the similarity threshold.")
    for suggestion in suggestions:
        lines.extend(
            [
                f"### {suggestion.priority}: `{suggestion.source}` -> `{suggestion.target}`",
                "",
                f"- Topic: {suggestion.topic}",
                f"- Similarity: {suggestion.similarity:.2f}",
                f"- Score: {suggestion.score:.2f}",
                f"- Suggested anchor: {suggestion.suggested_anchor}",
                f"- Reason: {suggestion.reason}",
                "",
            ]
        )

    lines.extend(["## Weakly Connected Pages", ""])
    if not weak_pages:
        lines.append("No weakly connected non-utility pages were found.")
    for page in weak_pages[:50]:
        lines.append(f"- `{page.clean_path}` ({page.language}, {page.page_type}) has {len(page.internal_links)} contextual internal links.")
    lines.append("")

    lines.extend(["## Overlapping Search Intent Candidates", ""])
    if not overlaps:
        lines.append("No high-similarity overlaps were found.")
    for left, right, similarity in overlaps:
        lines.append(f"- `{left.clean_path}` and `{right.clean_path}` have similarity {similarity:.2f}. Review for duplicate intent or add clearer differentiation.")
    lines.append("")

    lines.extend(
        [
            "## How To Use This Report",
            "",
            "1. Review high-priority suggestions first.",
            "2. Add only links that feel natural in the paragraph context.",
            "3. Apply equivalent improvements in EN and DE where relevant.",
            "4. After editing pages, run the normal SEO/link/heading audits.",
            "",
        ]
    )
    return "\n".join(lines)


def filter_pages(pages: Sequence[PageData], locale: str) -> List[PageData]:
    if locale == "all":
        return list(pages)
    return [page for page in pages if page.language == locale]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AXcent topic clusters and internal-link recommendations.")
    parser.add_argument("--locale", choices=["all", "en", "de"], default="all", help="Limit analysis to one locale.")
    parser.add_argument("--max-suggestions", type=int, default=50, help="Maximum internal-link suggestions to include.")
    parser.add_argument("--refresh", action="store_true", help="Rebuild embeddings even when the content hash matches the cache.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    pages = [extract_page(path, ROOT_DIR) for path in discover_html_files(ROOT_DIR)]
    pages = filter_pages(pages, args.locale)
    if not pages:
        print("No HTML pages found for the requested locale.")
        return 1

    cache = load_cache(CACHE_FILE)
    api_key = os.environ.get("OPENAI_API_KEY")
    embeddings = ensure_embeddings(pages, cache, args.refresh, api_key)
    suggestions = build_link_suggestions(pages, embeddings, args.max_suggestions)
    clusters = build_topic_clusters(pages, embeddings)
    weak_pages = find_weak_pages(pages)
    overlaps = find_overlaps(pages, embeddings)

    write_outputs(pages, cache, clusters, suggestions, overlaps, weak_pages)
    print(f"Topic authority report written to {REPORT_FILE}")
    print(f"Page index written to {PAGE_INDEX_FILE}")
    print(f"Embedding cache written to {CACHE_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
