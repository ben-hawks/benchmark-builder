#!/usr/bin/env python3
"""Validate an MLCommons Science Benchmarks corpus entry against the real
schema (https://github.com/mlcommons-science/benchmark/blob/main/source/benchmarks-format.yaml).
See references/mlcommons-corpus-format.md for the field-by-field rationale
and two known ambiguities in the source schema itself (this validator follows
the documented defaults, not the schema file's own inconsistent example).

Usage:
    python validate_corpus_entry.py <entry.yaml>

Exits non-zero if any required field is missing/empty, a >=1 list field is
empty, a cite entry doesn't look like bibtex, or a rating is out of range.
Warns (doesn't fail) on the deprecated `solutions` field and on ml_motif
diverging from task_types (a real judgment call, not necessarily wrong).
"""

import argparse
import sys

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pyyaml. Install it with `pip install pyyaml` and re-run.")

REQUIRED_SCALAR = ["valid", "valid_date", "name", "url", "focus", "summary", "licensing", "type"]
REQUIRED_LIST_MIN1 = [
    "domain", "keywords", "task_types", "ai_capability_measured",
    "metrics", "models", "ml_motif", "ml_task",
]
RATING_CATEGORIES = ["software", "specification", "dataset", "metrics", "reference_solution", "documentation"]


class Issue:
    def __init__(self, level, message):
        self.level = level
        self.message = message

    def __str__(self):
        return f"[{self.level.upper()}] {self.message}"


def validate_entry(entry, index):
    issues = []
    label = f"entry {index}"

    for field in REQUIRED_SCALAR:
        value = entry.get(field)
        if value is None or value == "":
            issues.append(Issue("error", f"{label}: missing required field '{field}'"))

    if entry.get("valid") is not None and not isinstance(entry.get("valid"), bool):
        issues.append(Issue("error", f"{label}: 'valid' must be a boolean, got {entry.get('valid')!r}"))

    for field in REQUIRED_LIST_MIN1:
        value = entry.get(field)
        non_blank = [v for v in (value or []) if isinstance(value, list) and str(v).strip()]
        if not value or not isinstance(value, list) or len(non_blank) == 0:
            issues.append(Issue("error", f"{label}: '{field}' must be a non-empty list (>=1 item, and not just blank placeholders)"))

    cite = entry.get("cite")
    if not cite or not isinstance(cite, list) or len(cite) == 0:
        issues.append(Issue("error", f"{label}: 'cite' must be a non-empty list"))
    else:
        for i, c in enumerate(cite):
            c_str = str(c).strip()
            if not (c_str.startswith("@") and "{" in c_str):
                issues.append(Issue("error", f"{label}: cite[{i}] doesn't look like bibtex (must start with '@' and contain '{{'): {c_str[:60]!r}"))

    for section in ("datasets", "results"):
        links = (entry.get(section) or {}).get("links")
        if not links or not isinstance(links, list) or len(links) == 0:
            issues.append(Issue("error", f"{label}: '{section}.links' must be a non-empty list"))
        else:
            for i, link in enumerate(links):
                if not isinstance(link, dict) or not str(link.get("name", "")).strip() or not str(link.get("url", "")).strip():
                    issues.append(Issue("error", f"{label}: {section}.links[{i}] must have both a non-blank 'name' and 'url'"))

    fair = entry.get("fair") or {}
    for key in ("reproducible", "benchmark_ready"):
        if key not in fair:
            issues.append(Issue("error", f"{label}: fair.{key} is required"))
        elif not isinstance(fair[key], bool):
            issues.append(Issue("error", f"{label}: fair.{key} must be a boolean, got {fair[key]!r}"))

    if "solutions" in entry:
        issues.append(Issue("warning", f"{label}: 'solutions' is deprecated per the source schema (results supersedes it) -- consider removing"))

    task_types = entry.get("task_types") or []
    ml_motif = entry.get("ml_motif") or []
    if task_types and ml_motif and set(task_types) != set(ml_motif):
        issues.append(Issue("info", f"{label}: ml_motif {ml_motif} differs from task_types {task_types} -- fine if deliberate, but the schema's own convention (and this skill's default) is to match them; see references/mlcommons-corpus-format.md's ml_motif ambiguity note"))

    ratings = entry.get("ratings")
    if ratings:
        for cat in RATING_CATEGORIES:
            if cat not in ratings:
                issues.append(Issue("warning", f"{label}: ratings missing category '{cat}'"))
                continue
            r = ratings[cat].get("rating")
            if r is None:
                issues.append(Issue("error", f"{label}: ratings.{cat}.rating is missing"))
            elif not isinstance(r, (int, float)) or not (0 <= r <= 5 or r == -1):
                issues.append(Issue("error", f"{label}: ratings.{cat}.rating must be 0-5 (or -1 for unevaluated, per the schema's example), got {r!r}"))
            if not ratings[cat].get("reason"):
                issues.append(Issue("warning", f"{label}: ratings.{cat}.reason is empty"))

    contact = entry.get("contact")
    if contact and contact.get("name") and not contact.get("email"):
        issues.append(Issue("info", f"{label}: contact.name given without contact.email -- fine if that's genuinely unknown (the real corpus has precedent for this), just confirm it wasn't accidentally dropped"))

    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entry_path")
    args = parser.parse_args()

    with open(args.entry_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        sys.exit("Top-level content must be a YAML list (even for a single entry) -- see references/mlcommons-corpus-format.md's Structure section.")
    if len(data) != 1:
        print(f"[INFO] file contains {len(data)} entries (expected exactly 1 for a single benchmark's own generated file -- fine if this was deliberately merged from multiple)")

    all_issues = []
    for i, entry in enumerate(data):
        issues = validate_entry(entry, i)
        all_issues += issues
        for issue in issues:
            print(issue)

    n_errors = sum(1 for i in all_issues if i.level == "error")
    n_warnings = sum(1 for i in all_issues if i.level == "warning")
    print(f"\n{n_errors} error(s), {n_warnings} warning(s).")
    sys.exit(1 if n_errors else 0)


if __name__ == "__main__":
    main()
