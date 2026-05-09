#!/usr/bin/env python3
"""Build a recent top-venue CS paper research plan."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from urllib.parse import quote_plus


SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
WHITELIST_PATH = SKILL_DIR / "references" / "venue_whitelist.json"


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def selected_years(args: argparse.Namespace) -> list[int]:
    if args.years:
        years = [int(year.strip()) for year in args.years.split(",") if year.strip()]
        return sorted(set(years))

    current_year = args.current_year or dt.date.today().year
    start_year = args.start_year
    end_year = args.end_year

    if start_year is None:
        start_year = current_year - args.years_back
    if end_year is None:
        end_year = current_year
    if start_year > end_year:
        raise ValueError("--start-year cannot be later than --end-year")
    return list(range(start_year, end_year + 1))


def load_whitelist() -> dict:
    with WHITELIST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def include_venue(venue: dict, mode: str) -> bool:
    if mode == "broad":
        return venue["mode"] in {"strict", "broad"}
    return venue["mode"] == "strict"


def source_name(url: str) -> str:
    if "arxiv.org" in url:
        return "arXiv"
    if "dblp.org" in url:
        return "DBLP"
    if "openreview.net" in url:
        return "OpenReview"
    if "aclanthology.org" in url:
        return "ACL Anthology"
    if "proceedings.mlr.press" in url:
        return "PMLR"
    if "neurips.cc" in url:
        return "NeurIPS Proceedings"
    return "official proceedings"


def make_queries(venue: dict, year: int, topic: str | None, include_submissions: bool) -> list[dict]:
    topic_part = f" {topic}" if topic else ""
    aliases = " OR ".join(f'"{alias}"' for alias in [venue["name"], *venue.get("aliases", [])])
    quoted_topic = quote_plus(topic or "")
    queries = []

    for url in venue.get("sources", []):
        domain = re.sub(r"^https?://", "", url).split("/", 1)[0]
        queries.append(
            {
                "paper_status": "accepted_or_published",
                "evidence_tier": "top_venue_accepted_or_published",
                "source": source_name(url),
                "url": url,
                "query": f"site:{domain} {venue['name']} {year}{topic_part}",
            }
        )

    if include_submissions:
        for template in venue.get("submission_sources", []):
            url = template.format(year=year)
            domain = re.sub(r"^https?://", "", url).split("/", 1)[0]
            queries.append(
                {
                    "paper_status": "submitted_or_under_review",
                    "evidence_tier": "top_venue_submission",
                    "source": source_name(url),
                    "url": url,
                    "query": f"site:{domain} {venue['name']} {year} submission OR under review{topic_part}",
                }
            )

    semantic_query = f"({aliases}) {year}{topic_part}"
    queries.append(
        {
            "paper_status": "accepted_or_published",
            "evidence_tier": "top_venue_accepted_or_published",
            "source": "Semantic Scholar",
            "url": "https://www.semanticscholar.org/",
            "query": semantic_query,
        }
    )
    queries.append(
        {
            "paper_status": "accepted_or_published",
            "evidence_tier": "top_venue_accepted_or_published",
            "source": "OpenAlex",
            "url": "https://openalex.org/",
            "query": f"{venue['name']} {year}{topic_part}",
        }
    )
    if topic:
        queries.append(
            {
                "paper_status": "accepted_or_published",
                "evidence_tier": "top_venue_accepted_or_published",
                "source": "Papers With Code",
                "url": f"https://paperswithcode.com/search?q={quoted_topic}",
                "query": f"{topic} {venue['name']} {year}",
            }
        )
    return queries


def make_preprint_queries(years: list[int], tracks: list[str], topic: str | None) -> list[dict]:
    if not topic:
        return []

    topic_query = quote_plus(topic)
    quoted_topic = f'"{topic}"'
    track_terms = {
        "ml": ["LLM agent", "agentic memory", "long-term memory", "reinforcement learning agent"],
        "nlp": ["language agent", "conversational agent", "LLM agents", "memory retrieval"],
        "dbdm": ["recommender agent", "retrieval agent", "data mining", "information retrieval"],
    }
    terms = sorted({term for track in tracks for term in track_terms.get(track, [])})
    year_terms = " OR ".join(str(year) for year in years)
    query_terms = " OR ".join(f'"{term}"' for term in terms)

    return [
        {
            "paper_status": "preprint",
            "evidence_tier": "preprint_supplement",
            "source": "arXiv",
            "url": f"https://arxiv.org/search/?query={topic_query}&searchtype=all&source=header",
            "query": f'site:arxiv.org/abs {quoted_topic} ({query_terms}) ({year_terms})',
        },
        {
            "paper_status": "preprint_or_unverified",
            "evidence_tier": "preprint_supplement",
            "source": "Semantic Scholar",
            "url": "https://www.semanticscholar.org/",
            "query": f'{quoted_topic} ({query_terms}) ({year_terms})',
        },
        {
            "paper_status": "preprint_or_unverified",
            "evidence_tier": "preprint_supplement",
            "source": "OpenAlex",
            "url": "https://openalex.org/",
            "query": f'{quoted_topic} ({query_terms}) ({year_terms})',
        },
        {
            "paper_status": "preprint_or_unverified",
            "evidence_tier": "preprint_supplement",
            "source": "Papers With Code",
            "url": f"https://paperswithcode.com/search?q={topic_query}",
            "query": f'{quoted_topic} ({query_terms}) ({year_terms})',
        },
    ]


def build_plan(args: argparse.Namespace) -> dict:
    whitelist = load_whitelist()
    years = selected_years(args)
    tracks = parse_csv(args.tracks) if args.tracks else whitelist["default_tracks"]
    unknown_tracks = sorted(set(tracks) - set(whitelist["tracks"]))
    if unknown_tracks:
        raise ValueError(f"Unknown tracks: {', '.join(unknown_tracks)}")

    venues = []
    for track in tracks:
        for venue in whitelist["tracks"][track]["venues"]:
            if include_venue(venue, args.mode):
                venues.append(
                    {
                        "track": track,
                        "track_label": whitelist["tracks"][track]["label"],
                        "name": venue["name"],
                        "aliases": venue.get("aliases", []),
                        "type": venue["type"],
                        "venue_mode": venue["mode"],
                        "sources": venue["sources"],
                        "submission_sources": venue.get("submission_sources", []),
                        "year_queries": {
                            str(year): make_queries(venue, year, args.topic, args.include_submissions) for year in years
                        },
                    }
                )

    return {
        "generated_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "years": years,
        "mode": args.mode,
        "tracks": tracks,
        "topic": args.topic,
        "include_submissions": args.include_submissions,
        "include_preprints": args.include_preprints,
        "venue_count": len(venues),
        "expected_records": "Enumerate all matching papers per venue/year when proceedings are available; otherwise report the gap.",
        "venues": venues,
        "preprint_queries": make_preprint_queries(years, tracks, args.topic) if args.include_preprints else [],
        "exclusion_terms": whitelist["exclusion_terms"],
        "source_priority": whitelist["source_priority"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", help="Research topic or keyword phrase.")
    parser.add_argument("--tracks", help="Comma-separated tracks: ml,nlp,dbdm.")
    parser.add_argument("--mode", choices=["strict", "broad"], default="broad")
    parser.add_argument("--current-year", type=int, help="Current year for rolling window.")
    parser.add_argument("--years-back", type=int, default=2, help="Number of years before current year to include.")
    parser.add_argument("--years", help="Explicit comma-separated years, e.g. 2024,2025,2026.")
    parser.add_argument("--start-year", type=int)
    parser.add_argument("--end-year", type=int)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    parser.add_argument("--summary", action="store_true", help="Print a compact Markdown summary instead of JSON.")
    parser.add_argument("--include-submissions", action="store_true", help="Include public submitted or under-review records from venue-hosted systems such as OpenReview.")
    parser.add_argument("--include-preprints", action="store_true", help="Include a separate arXiv/preprint supplement query plan.")
    args = parser.parse_args()

    try:
        plan = build_plan(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.summary:
        print(f"Years: {', '.join(str(year) for year in plan['years'])}")
        print(f"Mode: {plan['mode']}")
        print(f"Tracks: {', '.join(plan['tracks'])}")
        print(f"Include submissions: {str(plan['include_submissions']).lower()}")
        print(f"Include preprints: {str(plan['include_preprints']).lower()}")
        print(f"Venue count: {plan['venue_count']}")
        print("")
        by_track: dict[str, list[str]] = {}
        for venue in plan["venues"]:
            label = venue["track_label"]
            by_track.setdefault(label, []).append(f"{venue['name']} ({venue['venue_mode']})")
        for label, names in by_track.items():
            print(f"{label}:")
            print(", ".join(names))
            print("")
        if plan["preprint_queries"]:
            print("Preprint supplement sources:")
            print(", ".join(query["source"] for query in plan["preprint_queries"]))
    else:
        indent = 2 if args.pretty else None
        print(json.dumps(plan, ensure_ascii=False, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
