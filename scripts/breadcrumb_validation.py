"""Shared breadcrumb JSON-LD parsing and validation helpers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse

from bs4 import BeautifulSoup

BASE_URL = "https://axcentdance.com"


class BreadcrumbValidationError(Exception):
    """Raised when breadcrumb schema cannot be parsed for validation."""


@dataclass(frozen=True)
class BreadcrumbScript:
    start: int
    end: int
    body: str
    objects: list[dict]
    canonical_url: str | None


def jsonld_blocks(content: str) -> Iterable[tuple[int, int, str]]:
    pattern = re.compile(
        r'(<script\s+type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
        re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(content):
        yield match.start(2), match.end(2), match.group(2)


def canonical_url(content: str) -> str | None:
    soup = BeautifulSoup(content, "html.parser")
    canonical_tag = soup.find("link", rel="canonical")
    return canonical_tag.get("href") if canonical_tag else None


def schema_objects_from_json(data: object) -> list[dict]:
    if not isinstance(data, dict):
        return []
    graph = data.get("@graph")
    if isinstance(graph, list):
        return [item for item in graph if isinstance(item, dict)]
    return [data]


def schema_objects(content: str, rel_path: str) -> tuple[list[dict], str | None]:
    saw_jsonld = False
    objects: list[dict] = []

    for _start, _end, body in jsonld_blocks(content):
        saw_jsonld = True
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise BreadcrumbValidationError(f"Invalid JSON in <script> tag: {exc}") from exc
        objects.extend(schema_objects_from_json(data))

    if not saw_jsonld:
        raise BreadcrumbValidationError("Missing JSON-LD script")
    return objects, canonical_url(content)


def object_type(item: dict) -> str | list[str] | None:
    return item.get("@type")


def is_type(item: dict, expected: str) -> bool:
    value = object_type(item)
    if isinstance(value, list):
        return expected in value
    return value == expected


def breadcrumb_url(element: dict) -> str | None:
    item = element.get("item")
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("@id") or item.get("url")
    return None


def find_breadcrumb(objects: list[dict]) -> dict:
    breadcrumbs = [item for item in objects if is_type(item, "BreadcrumbList")]
    if not breadcrumbs:
        raise BreadcrumbValidationError("Missing BreadcrumbList schema")
    if len(breadcrumbs) > 1:
        raise BreadcrumbValidationError("Duplicate BreadcrumbList schema objects")
    return breadcrumbs[0]


def find_breadcrumb_script(content: str, rel_path: str) -> BreadcrumbScript:
    page_canonical = canonical_url(content)
    saw_jsonld = False

    for start, end, body in jsonld_blocks(content):
        saw_jsonld = True
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise BreadcrumbValidationError(f"Invalid JSON in <script> tag: {exc}") from exc
        objects = schema_objects_from_json(data)
        if any(is_type(item, "BreadcrumbList") for item in objects):
            return BreadcrumbScript(start, end, body, objects, page_canonical)

    if not saw_jsonld:
        raise BreadcrumbValidationError("Missing JSON-LD script")
    raise BreadcrumbValidationError("Missing BreadcrumbList schema")


def validate_url(url: str, position: int, is_german: bool) -> list[str]:
    errors: list[str] = []
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        errors.append(f"Absolute URL required: '{url}' at position {position}")
    if ".html" in url:
        errors.append(f"Clean URL violation: contains '.html' in '{url}'")
    if url.endswith("/") and url not in {f"{BASE_URL}/", f"{BASE_URL}/de/"}:
        errors.append(f"Trailing slash violation: '{url}'")

    if url.startswith(f"{BASE_URL}/"):
        if is_german and position > 1 and not url.startswith(f"{BASE_URL}/de/"):
            errors.append(f"Language mismatch: '{url}' in German page (missing /de/)")
        if not is_german and url.startswith(f"{BASE_URL}/de/"):
            errors.append(f"Language mismatch: '{url}' in English page (contains /de/)")

    return errors


def validate_breadcrumb(breadcrumb: dict, rel_path: str, page_canonical: str | None) -> list[str]:
    errors: list[str] = []
    elements = breadcrumb.get("itemListElement")
    is_german = rel_path.startswith("de/")

    if not isinstance(elements, list) or not elements:
        return ["BreadcrumbList has no itemListElement content"]

    if "blog-posts/" in rel_path:
        if len(elements) < 3:
            errors.append(f"Insufficient levels. Expected 3 (Home > Blog > Post), found {len(elements)}")
    elif len(elements) < 2:
        errors.append(f"Insufficient levels. Expected at least 2, found {len(elements)}")

    seen_positions: set[int] = set()
    for index, element in enumerate(elements, start=1):
        if not isinstance(element, dict):
            errors.append(f"Invalid breadcrumb element at position {index}")
            continue

        position = element.get("position")
        if position != index:
            errors.append(f"Invalid position at element {index - 1}. Found {position}, expected {index}")
        if isinstance(position, int):
            if position in seen_positions:
                errors.append(f"Duplicate breadcrumb position {position}")
            seen_positions.add(position)

        item = element.get("item", {})
        name = element.get("name") or (item.get("name") if isinstance(item, dict) else None)
        if not name:
            errors.append(f"Missing name for element at position {index}")

        url = breadcrumb_url(element)
        if not url:
            errors.append(f"Missing URL for element at position {index}")
            continue
        errors.extend(validate_url(url, index, is_german))

    last_element = elements[-1]
    last_url = breadcrumb_url(last_element) if isinstance(last_element, dict) else None
    if page_canonical and last_url != page_canonical:
        errors.append(f"Last breadcrumb URL ({last_url}) does not match canonical ({page_canonical})")

    return errors


def validate_breadcrumb_content(content: str, rel_path: str) -> list[str]:
    try:
        objects, page_canonical = schema_objects(content, rel_path)
        breadcrumb = find_breadcrumb(objects)
    except BreadcrumbValidationError as exc:
        return [str(exc)]

    return validate_breadcrumb(breadcrumb, rel_path, page_canonical)
