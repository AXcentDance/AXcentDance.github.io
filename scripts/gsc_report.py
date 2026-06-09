#!/usr/bin/env python3
"""
Generate a private Google Search Console content report for AXcent Dance.

The script reads OAuth client credentials from private/gsc_oauth_client.json,
stores the local OAuth token in private/gsc_token.json, and writes a Markdown
report to System/GSC_Content_Report.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT_DIR / "private"
CLIENT_FILE = PRIVATE_DIR / "gsc_oauth_client.json"
TOKEN_FILE = PRIVATE_DIR / "gsc_token.json"
REPORT_FILE = ROOT_DIR / "System" / "GSC_Content_Report.md"
DATA_FILE = ROOT_DIR / "System" / "gsc_search_console_data.json"
DEFAULT_SITE_URL = "https://axcentdance.com/"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def load_google_modules():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ModuleNotFoundError as exc:
        missing = exc.name or "Google API dependency"
        print(f"Missing Python dependency: {missing}", file=sys.stderr)
        print(
            "Install dependencies with:\n"
            "python3 -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    return Request, Credentials, InstalledAppFlow, build


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate AXcent Dance Google Search Console opportunity report."
    )
    parser.add_argument(
        "--site-url",
        default=os.environ.get("GSC_SITE_URL", DEFAULT_SITE_URL),
        help="Search Console property URL, for example https://axcentdance.com/ or sc-domain:axcentdance.com.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=28,
        help="Number of days to analyze. Default: 28.",
    )
    parser.add_argument(
        "--lag-days",
        type=int,
        default=3,
        help="Exclude the most recent N days because GSC data can lag. Default: 3.",
    )
    parser.add_argument(
        "--row-limit",
        type=int,
        default=25000,
        help="Maximum GSC rows to request per period. Default: 25000.",
    )
    return parser.parse_args()


def ensure_private_files():
    if not CLIENT_FILE.exists():
        raise SystemExit(
            f"Missing OAuth client file: {CLIENT_FILE}\n"
            "Download the Desktop app OAuth JSON from Google Cloud and save it there."
        )


def get_credentials():
    Request, Credentials, InstalledAppFlow, _ = load_google_modules()
    ensure_private_files()

    credentials = None
    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
        credentials = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")
    return credentials


def build_service():
    _, _, _, build = load_google_modules()
    credentials = get_credentials()
    return build("searchconsole", "v1", credentials=credentials)


def query_search_analytics(service, site_url, start_date, end_date, row_limit):
    request = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "dimensions": ["page", "query"],
        "rowLimit": row_limit,
        "dataState": "final",
    }
    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
    return normalize_rows(response.get("rows", []))


def normalize_rows(rows):
    normalized = []
    for row in rows:
        keys = row.get("keys", [])
        if len(keys) != 2:
            continue
        normalized.append(
            {
                "page": keys[0],
                "query": keys[1],
                "clicks": float(row.get("clicks", 0)),
                "impressions": float(row.get("impressions", 0)),
                "ctr": float(row.get("ctr", 0)),
                "position": float(row.get("position", 0)),
            }
        )
    return normalized


def aggregate_by(rows, key):
    totals = defaultdict(lambda: {"clicks": 0.0, "impressions": 0.0, "position_weight": 0.0})
    for row in rows:
        bucket = totals[row[key]]
        bucket["clicks"] += row["clicks"]
        bucket["impressions"] += row["impressions"]
        bucket["position_weight"] += row["position"] * row["impressions"]

    aggregated = []
    for value, data in totals.items():
        impressions = data["impressions"]
        clicks = data["clicks"]
        aggregated.append(
            {
                key: value,
                "clicks": clicks,
                "impressions": impressions,
                "ctr": clicks / impressions if impressions else 0.0,
                "position": data["position_weight"] / impressions if impressions else 0.0,
            }
        )
    return aggregated


def path_language(url):
    return "DE" if "/de/" in url else "EN"


def find_opportunities(rows):
    candidates = [
        row
        for row in rows
        if row["impressions"] >= 20 and 4.0 <= row["position"] <= 20.0
    ]
    return sorted(candidates, key=lambda row: (row["impressions"], -row["position"]), reverse=True)


def find_low_ctr(rows):
    page_rows = aggregate_by(rows, "page")
    candidates = [
        row
        for row in page_rows
        if row["impressions"] >= 50 and row["position"] <= 15.0 and row["ctr"] < 0.025
    ]
    return sorted(candidates, key=lambda row: row["impressions"], reverse=True)


def find_decay(current_rows, previous_rows):
    current_pages = {row["page"]: row for row in aggregate_by(current_rows, "page")}
    previous_pages = {row["page"]: row for row in aggregate_by(previous_rows, "page")}
    decays = []

    for page, previous in previous_pages.items():
        current = current_pages.get(page, {"clicks": 0.0, "impressions": 0.0, "ctr": 0.0, "position": 0.0})
        previous_clicks = previous["clicks"]
        current_clicks = current["clicks"]
        if previous_clicks < 5:
            continue
        drop = (previous_clicks - current_clicks) / previous_clicks
        if drop >= 0.30:
            decays.append(
                {
                    "page": page,
                    "previous_clicks": previous_clicks,
                    "current_clicks": current_clicks,
                    "drop": drop,
                    "current_impressions": current["impressions"],
                    "current_position": current["position"],
                }
            )

    return sorted(decays, key=lambda row: row["drop"], reverse=True)


def fmt_int(value):
    return f"{int(round(value)):,}"


def fmt_pct(value):
    return f"{value * 100:.1f}%"


def fmt_pos(value):
    return f"{value:.1f}" if value else "-"


def markdown_table(headers, rows):
    if not rows:
        return "_No rows matched this section._\n"

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def build_report(site_url, current_start, current_end, previous_start, previous_end, current_rows, previous_rows):
    page_totals = sorted(aggregate_by(current_rows, "page"), key=lambda row: row["clicks"], reverse=True)
    query_totals = sorted(aggregate_by(current_rows, "query"), key=lambda row: row["clicks"], reverse=True)
    opportunities = find_opportunities(current_rows)
    low_ctr = find_low_ctr(current_rows)
    decay = find_decay(current_rows, previous_rows)

    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_clicks = sum(row["clicks"] for row in current_rows)
    total_impressions = sum(row["impressions"] for row in current_rows)
    average_ctr = total_clicks / total_impressions if total_impressions else 0.0

    lines = [
        "# AXcent Dance - Google Search Console Content Report",
        f"**Generated:** {generated}",
        f"**Property:** `{site_url}`",
        f"**Current period:** {current_start} to {current_end}",
        f"**Comparison period:** {previous_start} to {previous_end}",
        "",
        "## Summary",
        f"- Clicks: **{fmt_int(total_clicks)}**",
        f"- Impressions: **{fmt_int(total_impressions)}**",
        f"- Average CTR: **{fmt_pct(average_ctr)}**",
        f"- Page/query rows analyzed: **{fmt_int(len(current_rows))}**",
        "",
        "## Ranking Opportunities",
        "Queries in positions 4-20 with meaningful impressions. These are usually the easiest SEO wins.",
        markdown_table(
            ["Lang", "Page", "Query", "Clicks", "Impr.", "CTR", "Pos."],
            [
                [
                    path_language(row["page"]),
                    row["page"],
                    row["query"].replace("|", "\\|"),
                    fmt_int(row["clicks"]),
                    fmt_int(row["impressions"]),
                    fmt_pct(row["ctr"]),
                    fmt_pos(row["position"]),
                ]
                for row in opportunities[:25]
            ],
        ),
        "## Low CTR Pages",
        "Pages with visibility but weak click-through. Review title tags, meta descriptions, and search intent.",
        markdown_table(
            ["Lang", "Page", "Clicks", "Impr.", "CTR", "Pos."],
            [
                [
                    path_language(row["page"]),
                    row["page"],
                    fmt_int(row["clicks"]),
                    fmt_int(row["impressions"]),
                    fmt_pct(row["ctr"]),
                    fmt_pos(row["position"]),
                ]
                for row in low_ctr[:20]
            ],
        ),
        "## Click Decay",
        "Pages down at least 30% versus the previous comparable period.",
        markdown_table(
            ["Lang", "Page", "Previous clicks", "Current clicks", "Drop", "Current impr.", "Current pos."],
            [
                [
                    path_language(row["page"]),
                    row["page"],
                    fmt_int(row["previous_clicks"]),
                    fmt_int(row["current_clicks"]),
                    fmt_pct(row["drop"]),
                    fmt_int(row["current_impressions"]),
                    fmt_pos(row["current_position"]),
                ]
                for row in decay[:20]
            ],
        ),
        "## Top Pages",
        markdown_table(
            ["Lang", "Page", "Clicks", "Impr.", "CTR", "Pos."],
            [
                [
                    path_language(row["page"]),
                    row["page"],
                    fmt_int(row["clicks"]),
                    fmt_int(row["impressions"]),
                    fmt_pct(row["ctr"]),
                    fmt_pos(row["position"]),
                ]
                for row in page_totals[:20]
            ],
        ),
        "## Top Queries",
        markdown_table(
            ["Query", "Clicks", "Impr.", "CTR", "Pos."],
            [
                [
                    row["query"].replace("|", "\\|"),
                    fmt_int(row["clicks"]),
                    fmt_int(row["impressions"]),
                    fmt_pct(row["ctr"]),
                    fmt_pos(row["position"]),
                ]
                for row in query_totals[:20]
            ],
        ),
        "## Recommended Workflow",
        "1. Start with Ranking Opportunities where the query already matches the page intent.",
        "2. For Low CTR Pages, improve titles and meta descriptions before rewriting body content.",
        "3. For Click Decay, check whether the page has outdated claims, old event dates, weak internal links, or mismatched German/English parity.",
        "4. When changing website content, update the matching EN/DE page, JSON-LD, sitemap, and LLM context files.",
        "",
    ]
    return "\n".join(lines)


def save_data(payload):
    DATA_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    args = parse_args()
    if args.days < 1:
        raise SystemExit("--days must be at least 1")
    if args.lag_days < 0:
        raise SystemExit("--lag-days cannot be negative")

    today = dt.date.today()
    current_end = today - dt.timedelta(days=args.lag_days + 1)
    current_start = current_end - dt.timedelta(days=args.days - 1)
    previous_end = current_start - dt.timedelta(days=1)
    previous_start = previous_end - dt.timedelta(days=args.days - 1)

    service = build_service()
    current_rows = query_search_analytics(
        service, args.site_url, current_start, current_end, args.row_limit
    )
    previous_rows = query_search_analytics(
        service, args.site_url, previous_start, previous_end, args.row_limit
    )

    report = build_report(
        args.site_url,
        current_start,
        current_end,
        previous_start,
        previous_end,
        current_rows,
        previous_rows,
    )
    REPORT_FILE.write_text(report, encoding="utf-8")
    save_data(
        {
            "site_url": args.site_url,
            "current_start": current_start.isoformat(),
            "current_end": current_end.isoformat(),
            "previous_start": previous_start.isoformat(),
            "previous_end": previous_end.isoformat(),
            "current_rows": current_rows,
            "previous_rows": previous_rows,
        }
    )

    print(f"Report written to: {REPORT_FILE}")
    print(f"Raw data written to: {DATA_FILE}")


if __name__ == "__main__":
    main()
