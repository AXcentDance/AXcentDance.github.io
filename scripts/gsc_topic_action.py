#!/usr/bin/env python3
"""
Run the AXcent GSC report and convert it into topic-map-aware actions.

This script is report-only. It reads private Search Console exports and the
local AXcent topic map, then writes System/GSC_Topic_Action_Report.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parents[1]
GSC_DATA_FILE = ROOT_DIR / "System" / "gsc_search_console_data.json"
ACTION_REPORT_FILE = ROOT_DIR / "System" / "GSC_Topic_Action_Report.md"
TOPIC_MAP_FILE = ROOT_DIR / "System" / "topic_map" / "page_index.json"
TOPIC_REPORT_FILE = ROOT_DIR / "System" / "topic_map" / "topic_authority_report.md"
TOPIC_MAP_SCRIPT = ROOT_DIR / "scripts" / "topic_map.py"
GSC_SCRIPT = ROOT_DIR / "scripts" / "gsc_report.py"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create an actionable GSC report enriched with the AXcent topic map."
    )
    parser.add_argument("--skip-gsc-refresh", action="store_true", help="Use existing GSC JSON data instead of pulling fresh GSC data.")
    parser.add_argument("--days", type=int, default=28, help="Days to request from GSC when refreshing. Default: 28.")
    parser.add_argument("--lag-days", type=int, default=3, help="GSC data lag buffer. Default: 3.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum page actions to include. Default: 12.")
    return parser.parse_args()


def run_gsc_report(days: int, lag_days: int):
    command = [
        sys.executable,
        str(GSC_SCRIPT),
        "--days",
        str(days),
        "--lag-days",
        str(lag_days),
    ]
    subprocess.run(command, cwd=ROOT_DIR, check=True)


def load_json(path: Path):
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_topic_map_module():
    spec = importlib.util.spec_from_file_location("axcent_topic_map", TOPIC_MAP_SCRIPT)
    if not spec or not spec.loader:
        raise SystemExit(f"Unable to load topic map script: {TOPIC_MAP_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["axcent_topic_map"] = module
    spec.loader.exec_module(module)
    return module


def clean_path_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "index"
    if path.endswith(".html"):
        path = path[:-5]
    if path.endswith("/"):
        path = path[:-1]
    if path == "de":
        return "de/index"
    return path


def aggregate_page_query(rows):
    grouped = defaultdict(lambda: {"clicks": 0.0, "impressions": 0.0, "position_weight": 0.0, "queries": defaultdict(lambda: {"clicks": 0.0, "impressions": 0.0, "position_weight": 0.0})})
    for row in rows:
        page = clean_path_from_url(row["page"])
        query = row["query"]
        impressions = float(row.get("impressions", 0))
        clicks = float(row.get("clicks", 0))
        position = float(row.get("position", 0))
        bucket = grouped[page]
        bucket["clicks"] += clicks
        bucket["impressions"] += impressions
        bucket["position_weight"] += position * impressions
        query_bucket = bucket["queries"][query]
        query_bucket["clicks"] += clicks
        query_bucket["impressions"] += impressions
        query_bucket["position_weight"] += position * impressions

    output = {}
    for page, data in grouped.items():
        impressions = data["impressions"]
        query_rows = []
        for query, query_data in data["queries"].items():
            query_impressions = query_data["impressions"]
            query_clicks = query_data["clicks"]
            query_rows.append(
                {
                    "query": query,
                    "clicks": query_clicks,
                    "impressions": query_impressions,
                    "ctr": query_clicks / query_impressions if query_impressions else 0.0,
                    "position": query_data["position_weight"] / query_impressions if query_impressions else 0.0,
                }
            )
        query_rows.sort(key=lambda item: (item["impressions"], -item["position"]), reverse=True)
        output[page] = {
            "clicks": data["clicks"],
            "impressions": impressions,
            "ctr": data["clicks"] / impressions if impressions else 0.0,
            "position": data["position_weight"] / impressions if impressions else 0.0,
            "queries": query_rows,
        }
    return output


def aggregate_previous_pages(rows):
    grouped = aggregate_page_query(rows)
    return {page: data["clicks"] for page, data in grouped.items()}


def load_topic_pages():
    pages = load_json(TOPIC_MAP_FILE)
    return {page["clean_path"]: page for page in pages}


def topic_for_page(topic_map, page_data):
    try:
        page = topic_map.PageData(**page_data)
        return topic_map.infer_topic(page)
    except Exception:
        haystack = " ".join(
            [
                page_data.get("clean_path", ""),
                page_data.get("title", ""),
                page_data.get("description", ""),
                page_data.get("h1", ""),
            ]
        ).lower()
        if "music" in haystack or "history" in haystack or "bachata" in haystack:
            return "Music & Education"
        return "General"


def topic_for_action(static_topic, page, queries):
    haystack = " ".join([page] + [query["query"] for query in queries]).lower()
    music_terms = (
        "what is",
        "was ist",
        "define",
        "origin",
        "origen",
        "de donde",
        "de dónde",
        "historia",
        "history",
        "roots",
        "ursprung",
        "instrument",
        "musicality",
        "styles",
        "stile",
    )
    if any(term in haystack for term in music_terms):
        return "Music & Education"
    if "private" in haystack or "one-on-one" in haystack or "1-on-1" in haystack:
        return "Private Lessons"
    if "hobby" in haystack or "anfangen" in haystack or "beginner" in haystack or "anfänger" in haystack:
        return "Beginner Bachata"
    if "party" in haystack or "bürkliplatz" in haystack or "event" in haystack:
        return "Events & Community"
    return static_topic


def build_internal_link_suggestions(topic_map):
    try:
        pages = [topic_map.extract_page(path, ROOT_DIR) for path in topic_map.discover_html_files(ROOT_DIR)]
        cache = topic_map.load_cache(topic_map.CACHE_FILE)
        embeddings = topic_map.ensure_embeddings(pages, cache, refresh=False, api_key=None)
        return topic_map.build_link_suggestions(pages, embeddings, max_suggestions=80)
    except Exception as exc:
        print(f"Warning: topic-map link suggestions unavailable: {exc}", file=sys.stderr)
        return []


def match_link_suggestions(suggestions):
    by_target = defaultdict(list)
    by_source = defaultdict(list)
    for suggestion in suggestions:
        by_target[suggestion.target].append(suggestion)
        by_source[suggestion.source].append(suggestion)
    return by_target, by_source


def score_page(page, data, previous_clicks):
    opportunity_queries = [
        query
        for query in data["queries"]
        if query["impressions"] >= 20 and 4.0 <= query["position"] <= 20.0
    ]
    low_ctr_bonus = 1.4 if data["impressions"] >= 50 and data["position"] <= 15 and data["ctr"] < 0.025 else 0.0
    previous = previous_clicks.get(page, 0)
    decay_bonus = 1.2 if previous >= 5 and data["clicks"] <= previous * 0.7 else 0.0
    query_weight = sum(min(query["impressions"], 800) / 160 for query in opportunity_queries[:8])
    return query_weight + low_ctr_bonus + decay_bonus


def classify_action(data, previous_clicks):
    previous = previous_clicks
    if previous >= 5 and data["clicks"] <= previous * 0.7:
        return "Refresh decaying page"
    if data["impressions"] >= 50 and data["position"] <= 15 and data["ctr"] < 0.025:
        return "Improve search snippet"
    return "Strengthen ranking opportunity"


def fmt_int(value):
    return f"{int(round(value)):,}"


def fmt_pct(value):
    return f"{value * 100:.1f}%"


def fmt_pos(value):
    return f"{value:.1f}" if value else "-"


def local_path_for_clean_path(clean_path):
    if clean_path == "index":
        return "index.html"
    if clean_path == "de/index":
        return "de/index.html"
    return f"{clean_path}.html"


def suggested_content_action(topic, queries):
    top_query = queries[0]["query"] if queries else "the target query"
    if topic == "Music & Education":
        return f"Add or tighten a concise answer block for `{top_query}`, then support it with one explanatory subsection and one class-oriented CTA."
    if topic == "Bachata Zurich":
        return f"Make the Zurich intent unmistakable for `{top_query}`: class location, level fit, schedule path, and trial/registration CTA."
    if topic == "Events & Community":
        return f"Clarify current dates, location, and who the event is for; add links to schedule, registration, and related community articles."
    if topic == "Beginner Bachata":
        return f"Answer beginner anxiety directly for `{top_query}`: no partner, first-class expectations, clothing, level fit, and next step."
    if topic == "Private Lessons":
        return f"Add decision copy for `{top_query}`: who private lessons help, result timeline, booking path, and price/contact cue."
    return f"Align the intro, first H2, and meta description with `{top_query}` while keeping the page intent narrow."


def render_report(gsc_data, topic_pages, topic_map, link_suggestions, limit):
    current_rows = gsc_data["current_rows"]
    previous_rows = gsc_data["previous_rows"]
    current_pages = aggregate_page_query(current_rows)
    previous_clicks = aggregate_previous_pages(previous_rows)
    by_target, by_source = match_link_suggestions(link_suggestions)

    scored = []
    for page, data in current_pages.items():
        if page not in topic_pages:
            continue
        score = score_page(page, data, previous_clicks)
        if score <= 0:
            continue
        scored.append((score, page, data))
    scored.sort(key=lambda item: item[0], reverse=True)

    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# AXcent GSC + Topic Map Action Report",
        f"**Generated:** {generated}",
        f"**GSC property:** `{gsc_data.get('site_url', 'unknown')}`",
        f"**Current period:** {gsc_data.get('current_start')} to {gsc_data.get('current_end')}",
        f"**Topic map source:** `{TOPIC_MAP_FILE.relative_to(ROOT_DIR)}`",
        "",
        "## Executive Actions",
        "These are ranked by real Google visibility plus AXcent topic-map context. The report is read-only and does not edit website pages.",
        "",
    ]

    if not scored:
        lines.append("_No high-confidence actions found from the current GSC and topic-map data._")
        lines.append("")

    for index, (score, page, data) in enumerate(scored[:limit], start=1):
        page_data = topic_pages[page]
        top_queries = [
            query
            for query in data["queries"]
            if query["impressions"] >= 20 and 4.0 <= query["position"] <= 20.0
        ][:5]
        if not top_queries:
            top_queries = data["queries"][:5]
        topic = topic_for_action(topic_for_page(topic_map, page_data), page, top_queries)
        previous = previous_clicks.get(page, 0.0)
        action_type = classify_action(data, previous)
        inbound_links = by_target.get(page, [])[:3]
        outbound_links = by_source.get(page, [])[:2]

        lines.extend(
            [
                f"### {index}. {action_type}: `{page}`",
                "",
                f"- Local file: `{local_path_for_clean_path(page)}`",
                f"- Topic-map cluster: **{topic}**",
                f"- GSC signal: {fmt_int(data['clicks'])} clicks, {fmt_int(data['impressions'])} impressions, {fmt_pct(data['ctr'])} CTR, avg position {fmt_pos(data['position'])}",
            ]
        )
        if previous:
            change = (data["clicks"] - previous) / previous
            lines.append(f"- Click trend: {fmt_int(previous)} previous clicks -> {fmt_int(data['clicks'])} current clicks ({fmt_pct(change)})")

        lines.append("- Query focus:")
        for query in top_queries:
            lines.append(
                f"  - `{query['query']}`: {fmt_int(query['impressions'])} impressions, {fmt_int(query['clicks'])} clicks, {fmt_pct(query['ctr'])} CTR, position {fmt_pos(query['position'])}"
            )

        lines.extend(
            [
                f"- Content action: {suggested_content_action(topic, top_queries)}",
                "- Snippet action: rewrite the title/meta to match the highest-impression query while preserving AXcent brand and EN/DE parity.",
            ]
        )

        if inbound_links:
            lines.append("- Internal link actions into this page:")
            for suggestion in inbound_links:
                lines.append(
                    f"  - Add a contextual link from `{suggestion.source}` to `{suggestion.target}` with anchor `{suggestion.suggested_anchor}`."
                )
        else:
            lines.append("- Internal link actions into this page: no high-similarity missing inbound link was found in the cached topic map.")

        if outbound_links:
            lines.append("- Internal link actions from this page:")
            for suggestion in outbound_links:
                lines.append(
                    f"  - Add a contextual link from `{suggestion.source}` to `{suggestion.target}` with anchor `{suggestion.suggested_anchor}`."
                )

        lines.extend(
            [
                "- Safety checks after editing: update matching EN/DE page if relevant, update JSON-LD `dateModified` for blog posts, regenerate sitemap/LLM context, and run SEO/link/heading audits.",
                "",
            ]
        )

    lines.extend(
        [
            "## How To Call This Action",
            "Run:",
            "",
            "```bash",
            "python3 scripts/gsc_topic_action.py",
            "```",
            "",
            "For future Codex requests, say `$gsc-report` to generate this same report.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    args = parse_args()
    if not args.skip_gsc_refresh:
        run_gsc_report(args.days, args.lag_days)

    if not GSC_DATA_FILE.exists():
        raise SystemExit(
            f"Missing {GSC_DATA_FILE}. Run scripts/gsc_report.py first or run this action without --skip-gsc-refresh."
        )
    if not TOPIC_MAP_FILE.exists():
        raise SystemExit(
            f"Missing {TOPIC_MAP_FILE}. Run scripts/topic_map.py first to generate the AXcent topic map."
        )

    gsc_data = load_json(GSC_DATA_FILE)
    topic_pages = load_topic_pages()
    topic_map = load_topic_map_module()
    link_suggestions = build_internal_link_suggestions(topic_map)
    report = render_report(gsc_data, topic_pages, topic_map, link_suggestions, args.limit)
    ACTION_REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"GSC + topic action report written to: {ACTION_REPORT_FILE}")


if __name__ == "__main__":
    main()
