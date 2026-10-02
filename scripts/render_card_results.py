#!/usr/bin/env python3
"""Write a benchmark's own scores into a Genesis/GEAR model card, traceably.

    python scripts/render_card_results.py MODEL_CARD.md --benchmark <name> --model <model> \\
        --results reference_results [--splits test exemplar] [-o OUT] [--dry-run | --check]

For benchmarks that aren't LLM evaluations (an LLM benchmark's cards come from the genesis
card-eval-updater skill; references/llm-benchmarks.md). It follows that skill's rule:
**numbers in a card are copied by script from the scoring output, never retyped.** For each
split it reads `<results>/<split>/<model>/metrics.json` (as written by the benchmark's
score.py; references/repo-structure.md) and:

- writes a `### Benchmark results (from metrics.json)` block under the card's
  `## Evaluation results` section: one table row per split, output and metric, plus the
  coverage counts and the source file with its sha256 prefix. The section is created under
  `# Evaluation details` (or at the end) if missing. Prose already in the section stays
  above the block. Re-running replaces only the block.
- adds `<benchmark>/<metric>` entries to the `metrics:` frontmatter, keeping existing
  entries (never prunes).

`--check` re-renders from the metrics files and compares with the card: exit 1 if the
block is missing or differs (a number that no longer traces to its metrics.json, e.g. after
a re-run, or a hand edit). `--dry-run` prints the result instead of writing it.

Conventions shared with card-eval-updater, so both tools can work on one card:
- the anchor is a visible heading, not an HTML comment, because the BPSW card pipeline strips
  comments;
- headings are matched after the same normalization (lowercase, no punctuation or emphasis),
  so `## Evaluation Results` matches;
- this block's heading differs from card-eval-updater's `### Automated benchmark results`,
  so neither tool overwrites the other's block.

Expected metrics.json shape: {"coverage": {...}, "groups": {"<group>": {<output>:
{<metric>: value}}}} (assets/repo/report.py), or {<metric>: value} per group when the
benchmark has a single output. --group picks the group (default "all").
Standard library only.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import re
import sys

BLOCK_HEADING = "### Benchmark results (from metrics.json)"
SECTION = "evaluation results"
PARENT = "evaluation details"
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def normalize_heading(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"\s+", " ", text)


BLOCK_NORM = normalize_heading(BLOCK_HEADING.lstrip("#"))


def headings(lines):
    out, in_code = [], False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        m = None if in_code else HEADING_RE.match(line)
        if m:
            out.append((len(m.group(1)), normalize_heading(m.group(2)), i))
    return out


def span(lines, norm, within=None, include_heading=False):
    """(start, end) line span of the first heading `norm` (inside `within`)."""
    hs = headings(lines)
    lo, hi = within or (0, len(lines))
    for k, (lvl, n, i) in enumerate(hs):
        if not (lo <= i < hi) or n != norm:
            continue
        end = hi
        for lvl2, _, j in hs[k + 1:]:
            if j >= hi:
                break
            if lvl2 <= lvl:
                end = j
                break
        return (i if include_heading else i + 1), end
    return None


def split_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL) if text.startswith("---") else None
    return (m.group(1), text[m.end():]) if m else (None, text)


def merge_metrics(front, entries):
    lines = front.split("\n") if front is not None else []
    start = next((i for i, l in enumerate(lines) if re.match(r"^metrics\s*:\s*(#.*)?$", l)), None)
    if start is None:
        return "\n".join(lines + ["metrics:"] + [f"    - {e}" for e in entries]), entries
    end, existing = start + 1, []
    while end < len(lines):
        s = lines[end].strip()
        if s and not lines[end].startswith((" ", "\t")):
            break
        if s.startswith("-"):
            v = re.sub(r"\s*#.*$", "", s.lstrip("-").strip()).strip().strip("\"'")
            if v:
                existing.append(v)
        elif s:
            break
        end += 1
    added = [e for e in entries if e not in existing]
    block = ["metrics:"] + [f"    - {e}" for e in existing + added]
    return "\n".join(lines[:start] + block + lines[end:]), added


def fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "N/A"
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return str(v).replace("|", "\\|")
    return f"{v:.6g}"


def rows_for(metrics, group):
    groups = metrics.get("groups", metrics)
    if group not in groups:
        raise SystemExit(f"render_card_results: no group {group!r} in metrics.json (have {list(groups)})")
    out = []
    for key, val in groups[group].items():
        if isinstance(val, dict):
            out += [(key, m, v) for m, v in val.items() if not isinstance(v, (dict, list))]
        elif not isinstance(val, list):
            out.append(("—", key, val))
    return out


def find_runs(results, model, splits):
    if not splits:
        splits = sorted(os.path.basename(os.path.dirname(os.path.dirname(p)))
                        for p in glob.glob(os.path.join(results, "*", model, "metrics.json")))
    if not splits:
        raise SystemExit(f"render_card_results: no {results}/<split>/{model}/metrics.json found")
    runs = []
    for s in splits:
        path = os.path.join(results, s, model, "metrics.json")
        if not os.path.exists(path):
            raise SystemExit(f"render_card_results: missing {path}")
        runs.append((s, path))
    return runs


def render(benchmark, model, runs, group):
    lines = [BLOCK_HEADING, "",
             f"Scores of `{model}` on the {benchmark} benchmark, copied by "
             "`render_card_results.py` from the benchmark's own scoring output "
             f"(group `{group}`). Don't edit this block by hand; re-run the script.", "",
             "| Split | Output | Metric | Value |", "|---|---|---|---|"]
    notes, entries = [], []
    for split, path in runs:
        with open(path, "rb") as f:
            raw = f.read()
        m = json.loads(raw)
        for out, met, val in rows_for(m, group):
            lines.append(f"| {split} | {out} | {met} | {fmt(val)} |")
            entries.append(f"{benchmark}/{met}")
        cov = m.get("coverage")
        cov_txt = ", ".join(f"{k} {fmt(v)}" for k, v in cov.items()) if isinstance(cov, dict) else "not recorded"
        notes.append(f"- **{split}**: coverage {cov_txt}. Source `{path}` "
                     f"(sha256 `{hashlib.sha256(raw).hexdigest()[:12]}`).")
    lines += [""] + notes
    return lines, list(dict.fromkeys(entries))


def apply(card_text, block):
    front, body = split_frontmatter(card_text)
    lines = body.split("\n")
    sec = span(lines, SECTION)
    if sec is None:
        parent = span(lines, PARENT)
        at = parent[1] if parent else len(lines)
        lines = lines[:at] + ["", "## Evaluation results", ""] + lines[at:]
        sec = span(lines, SECTION)
    inner = span(lines, BLOCK_NORM, within=sec, include_heading=True)
    if inner:
        s, e = inner
        lines = lines[:s] + block + [""] + lines[e:]
    else:
        s, e = sec
        existing = lines[s:e]
        while existing and not existing[-1].strip():
            existing.pop()
        while existing and not existing[0].strip():
            existing.pop(0)
        lines = lines[:s] + [""] + existing + ([""] if existing else []) + block + [""] + lines[e:]
    return front, "\n".join(lines)


def current_block(card_text):
    _, body = split_frontmatter(card_text)
    lines = body.split("\n")
    sec = span(lines, SECTION)
    inner = sec and span(lines, BLOCK_NORM, within=sec, include_heading=True)
    if not inner:
        return None
    blk = lines[inner[0]:inner[1]]
    while blk and not blk[-1].strip():
        blk.pop()
    return blk


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("card")
    p.add_argument("--benchmark", required=True, help="benchmark name used in metrics: entries")
    p.add_argument("--model", required=True, help="model directory name under <results>/<split>/")
    p.add_argument("--results", default="reference_results")
    p.add_argument("--splits", nargs="*", help="default: every split with a metrics.json for the model")
    p.add_argument("--group", default="all")
    p.add_argument("-o", "--out", help="default: overwrite the card")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--check", action="store_true")
    a = p.parse_args(argv)

    with open(a.card, encoding="utf-8") as f:
        text = f.read()
    block, entries = render(a.benchmark, a.model, find_runs(a.results, a.model, a.splits), a.group)

    if a.check:
        have = current_block(text)
        front, _ = split_frontmatter(text)
        _, missing = merge_metrics(front or "", entries)
        if have is None:
            print(f"MISSING: no '{BLOCK_HEADING}' block under '## Evaluation results'")
            return 1
        if have != block:
            print("UNTRACED: the card's block differs from what the metrics files produce now:")
            for i, (x, y) in enumerate(zip(have + [""] * len(block), block + [""] * len(have))):
                if x != y:
                    print(f"  line {i + 1}: card   {x!r}\n           render {y!r}")
            return 1
        for e in missing:
            print(f"WARN: metrics: frontmatter doesn't list {e}")
        print("ok: every number in the block traces to its metrics.json")
        return 0

    front, body = apply(text, block)
    front, added = merge_metrics(front, entries)
    out_text = f"---\n{front}\n---\n{body}" if front else body
    if a.dry_run:
        sys.stdout.write(out_text)
    else:
        with open(a.out or a.card, "w", encoding="utf-8") as f:
            f.write(out_text)
        print(f"wrote {a.out or a.card}: {len(block)} block lines; metrics: added {added or 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
