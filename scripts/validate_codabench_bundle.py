#!/usr/bin/env python3
"""Validate a Codabench competition bundle, and optionally a submission against it,
before handing either to a user as finished. See references/codabench.md for the
bundle format this checks against (grounded in Codabench's real wheat_seeds example,
not just the docs prose).

Four tiers, each gated on the previous one making sense to attempt:

  1. Structure  -- always runs. competition.yaml parses, required keys are present,
     every path it references actually exists, leaderboard columns are internally
     consistent, every program directory has a metadata.yaml with a `command`.
  2. Submission contract -- runs if --submission is given. Determines code-submission
     vs results-submission mode for the target task, reads the actual ingestion/scoring
     program source to figure out what the submission zip must contain, and checks it.
  3. Local functional dry run -- runs if --submission is given AND the relevant
     programs use the CODABENCH_ROOT override (see references/codabench.md) rather than
     hardcoding /app. No Docker needed: runs the real ingestion/scoring commands as
     subprocesses against a temp directory, and checks the resulting scores.json has
     every key the leaderboard expects.
  4. Docker faithful run -- best-effort, only attempted with --docker and a reachable
     Docker daemon. Resolves the image first (builds the bundle's own Dockerfile if it
     has one, otherwise uses/pulls competition.yaml's docker_image), then mounts the
     exact /app/... paths real Codabench uses and runs the real ingestion/scoring
     commands inside it. This has NOT been validated against the real Codabench platform
     itself (no way to do that from here) -- treat a pass as "the programs run in this
     image," not "Codabench will definitely accept this."

Tier 4 only ever does local, reversible things: build, pull, run, and (with
--rm-built-image) delete an image it built itself. It never runs `docker push` -- see
references/codabench.md; publishing an image is a public action that needs explicit
per-instance user confirmation and is deliberately out of scope for an automated
validator.

Usage:
    python validate_codabench_bundle.py <bundle_dir> [--submission sub.zip]
        [--task-index 0] [--docker] [--dockerfile PATH] [--no-build]
        [--gpus] [--rm-built-image]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pyyaml. Install it with `pip install pyyaml` and re-run.")

REQUIRED_TOP_KEYS = ["version", "title", "image", "terms"]
DEFAULT_DOCKER_IMAGE = "codalab/codalab-legacy:py3"
DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",  # documented format
    "%Y-%m-%d",
    "%m-%d-%Y",  # format actually used in Codabench's own wheat_seeds example
    "%m/%d/%Y",
]


class Issue:
    def __init__(self, level, message):
        self.level = level  # "error" | "warning" | "info"
        self.message = message

    def __str__(self):
        return f"[{self.level.upper()}] {self.message}"


def try_parse_date(value):
    value = str(value)
    for fmt in DATE_FORMATS:
        try:
            import datetime

            return datetime.datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Tier 1: structure
# ---------------------------------------------------------------------------


def check_structure(bundle_dir):
    issues = []
    yaml_path = bundle_dir / "competition.yaml"
    if not yaml_path.exists():
        return [Issue("error", "competition.yaml not found at bundle root")], None

    try:
        comp = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [Issue("error", f"competition.yaml is not valid YAML: {e}")], None

    for key in REQUIRED_TOP_KEYS:
        if key not in comp:
            issues.append(Issue("error", f"competition.yaml missing required key '{key}'"))
    if comp.get("version") != 2:
        issues.append(Issue("error", f"competition.yaml version is {comp.get('version')!r}, expected 2"))

    def check_path(rel, label):
        if rel and not (bundle_dir / rel).exists():
            issues.append(Issue("error", f"{label} path does not exist: {rel}"))

    check_path(comp.get("image"), "image")
    check_path(comp.get("terms"), "terms")

    for page in comp.get("pages", []) or []:
        if "title" not in page or "file" not in page:
            issues.append(Issue("error", f"page entry missing title/file: {page}"))
        else:
            check_path(page["file"], f"page '{page['title']}'")

    task_indices = set()
    for task in comp.get("tasks", []) or []:
        if "key" in task:
            continue  # references an existing DB task; nothing local to check
        for req in ("index", "name", "scoring_program"):
            if req not in task:
                issues.append(Issue("error", f"task missing required key '{req}': {task}"))
        task_indices.add(task.get("index"))
        check_path(task.get("scoring_program"), f"task {task.get('index')} scoring_program")
        check_path(task.get("input_data"), f"task {task.get('index')} input_data")
        check_path(task.get("reference_data"), f"task {task.get('index')} reference_data")
        check_path(task.get("ingestion_program"), f"task {task.get('index')} ingestion_program")
        for prog_key in ("scoring_program", "ingestion_program"):
            prog_path = task.get(prog_key)
            if prog_path and (bundle_dir / prog_path).is_dir():
                meta = bundle_dir / prog_path / "metadata.yaml"
                if not meta.exists():
                    issues.append(Issue("error", f"{prog_key} at {prog_path} has no metadata.yaml"))
                else:
                    try:
                        meta_data = yaml.safe_load(meta.read_text(encoding="utf-8"))
                        if not meta_data or "command" not in meta_data:
                            issues.append(Issue("error", f"{prog_path}/metadata.yaml has no 'command' key"))
                    except yaml.YAMLError as e:
                        issues.append(Issue("error", f"{prog_path}/metadata.yaml is not valid YAML: {e}"))

    if not comp.get("tasks"):
        issues.append(Issue("error", "no tasks defined"))

    phases = comp.get("phases", []) or []
    if not phases:
        issues.append(Issue("error", "no phases defined"))
    for phase in phases:
        for req in ("name", "start", "tasks"):
            if req not in phase:
                issues.append(Issue("error", f"phase missing required key '{req}': {phase}"))
        if "start" in phase and try_parse_date(phase["start"]) is None:
            issues.append(Issue("warning", f"phase '{phase.get('name')}' start date '{phase['start']}' didn't match any known format ({DATE_FORMATS}) -- may still be valid, verify against current Codabench behavior"))
        if "end" in phase and try_parse_date(phase["end"]) is None:
            issues.append(Issue("warning", f"phase '{phase.get('name')}' end date '{phase['end']}' didn't match any known format"))
        for t in phase.get("tasks", []) or []:
            if t not in task_indices:
                issues.append(Issue("error", f"phase '{phase.get('name')}' references undefined task index {t}"))

    for sol in comp.get("solutions", []) or []:
        for req in ("index", "tasks", "path"):
            if req not in sol:
                issues.append(Issue("error", f"solution missing required key '{req}': {sol}"))
        check_path(sol.get("path"), f"solution {sol.get('index')}")
        for t in sol.get("tasks", []) or []:
            if t not in task_indices:
                issues.append(Issue("error", f"solution {sol.get('index')} references undefined task index {t}"))

    leaderboards = comp.get("leaderboards", []) or []
    if not leaderboards:
        issues.append(Issue("error", "no leaderboards defined"))
    for lb in leaderboards:
        for req in ("title", "key", "columns"):
            if req not in lb:
                issues.append(Issue("error", f"leaderboard missing required key '{req}': {lb}"))
        seen_keys = set()
        for col in lb.get("columns", []) or []:
            for req in ("title", "key", "index"):
                if req not in col:
                    issues.append(Issue("error", f"leaderboard '{lb.get('title')}' column missing '{req}': {col}"))
            if col.get("key") in seen_keys:
                issues.append(Issue("error", f"leaderboard '{lb.get('title')}' has duplicate column key '{col.get('key')}'"))
            seen_keys.add(col.get("key"))

    return issues, comp


# ---------------------------------------------------------------------------
# Tier 2: submission contract
# ---------------------------------------------------------------------------


def find_task(comp, task_index):
    for task in comp.get("tasks", []) or []:
        if task.get("index") == task_index:
            return task
    return None


def guess_code_submission_files(ingestion_dir):
    """Heuristic: find `from X import Y` in the ingestion program, implying the
    submission zip must contain X.py at its root."""
    modules = set()
    for py_file in Path(ingestion_dir).glob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"^\s*from\s+(\w+)\s+import\s+\w+", text, re.MULTILINE):
            modules.add(m.group(1))
    return {f"{m}.py" for m in modules}


def guess_results_submission_files(scoring_dir):
    """Heuristic: find os.path.join(<var containing 'res' or 'prediction'>, 'name')
    in the scoring program, implying the submission zip must contain that filename."""
    names = set()
    pattern = re.compile(
        r"os\.path\.join\(\s*\w*(?:res|prediction)\w*\s*,\s*[\"']([^\"']+)[\"']", re.IGNORECASE
    )
    for py_file in Path(scoring_dir).glob("*.py"):
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        for m in pattern.finditer(text):
            names.add(m.group(1))
    return names


def check_submission_contract(bundle_dir, comp, task_index, submission_zip):
    issues = []
    task = find_task(comp, task_index)
    if task is None:
        return [Issue("error", f"no task with index {task_index} found")]

    with zipfile.ZipFile(submission_zip) as zf:
        names = zf.namelist()
    root_files = {n for n in names if "/" not in n.rstrip("/")}
    nested = [n for n in names if "/" in n.rstrip("/") and not n.startswith("__MACOSX")]
    if nested:
        issues.append(Issue("warning", f"submission has nested paths (expected flat root): {nested[:5]}"))

    ingestion_path = task.get("ingestion_program")
    if ingestion_path:
        expected = guess_code_submission_files(bundle_dir / ingestion_path)
        if not expected:
            issues.append(Issue("info", "could not determine expected submission filename from ingestion program source (no 'from X import Y' found) -- skipping contract check"))
        else:
            missing = expected - root_files
            if missing:
                issues.append(Issue("error", f"submission is missing file(s) the ingestion program imports: {missing} (found at root: {root_files})"))
            else:
                issues.append(Issue("info", f"submission provides expected file(s): {expected}"))
    else:
        scoring_path = task["scoring_program"]
        expected = guess_results_submission_files(bundle_dir / scoring_path)
        if not expected:
            issues.append(Issue("info", "could not determine expected result filename from scoring program source -- skipping contract check"))
        else:
            missing = expected - root_files
            if missing:
                issues.append(Issue("error", f"submission is missing expected result file(s): {missing} (found at root: {root_files})"))
            else:
                issues.append(Issue("info", f"submission provides expected file(s): {expected}"))

    return issues


# ---------------------------------------------------------------------------
# Tier 3: local functional dry run (no Docker)
# ---------------------------------------------------------------------------


def program_supports_local_root(program_dir):
    for py_file in Path(program_dir).glob("*.py"):
        if "CODABENCH_ROOT" in py_file.read_text(encoding="utf-8", errors="ignore"):
            return True
    return False


def _runs(executable):
    """True if `executable --version` actually succeeds. shutil.which() alone isn't
    enough on Windows, where a `python3` App Execution Alias can resolve to a real path
    that still fails at run time with a Store-install prompt (exit code 9009)."""
    try:
        return subprocess.run([executable, "--version"], capture_output=True, timeout=10).returncode == 0
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return False


def run_program(program_dir, root_dir, label):
    meta = yaml.safe_load((Path(program_dir) / "metadata.yaml").read_text(encoding="utf-8"))
    command = meta["command"]
    prefix_issue = None
    # Tier 3 runs on the actual host (unlike tier 4's container, which always has a
    # working python3) -- on a dev machine where `python3` doesn't actually run (e.g.
    # Windows with only the Store-alias stub), substitute transparently rather than
    # reporting a false failure. Local-testing convenience only; doesn't affect what
    # actually runs on Codabench's own (always-Linux, always-python3) containers.
    if command.split()[0] == "python3" and not _runs("python3") and _runs("python"):
        command = "python" + command[len("python3"):]
        prefix_issue = Issue("info", f"{label}: substituted 'python' for 'python3' (host's python3 doesn't actually run) -- local-testing only, does not affect the real container")
    env = dict(os.environ)
    env["CODABENCH_ROOT"] = str(root_dir)
    result = subprocess.run(
        command, shell=True, cwd=str(program_dir), env=env,
        capture_output=True, text=True, timeout=120,
    )
    issues = [prefix_issue] if prefix_issue else []
    if result.returncode != 0:
        issues.append(Issue("error", f"{label} exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"))
    else:
        issues.append(Issue("info", f"{label} ran successfully"))
    return issues


def local_dry_run(bundle_dir, comp, task_index, submission_zip):
    issues = []
    task = find_task(comp, task_index)
    if task is None:
        return [Issue("error", f"no task with index {task_index} found")]

    scoring_dir = bundle_dir / task["scoring_program"]
    ingestion_path = task.get("ingestion_program")
    ingestion_dir = bundle_dir / ingestion_path if ingestion_path else None

    programs_to_check = [scoring_dir] + ([ingestion_dir] if ingestion_dir else [])
    if not all(program_supports_local_root(p) for p in programs_to_check):
        return [Issue("info", "skipping local dry run: program(s) don't use the CODABENCH_ROOT override (they likely hardcode /app) -- use --docker instead, see references/codabench.md")]

    with tempfile.TemporaryDirectory(prefix="codabench_dryrun_") as tmp:
        tmp = Path(tmp)
        res_dir_source = None

        if ingestion_dir:
            ingest_root = tmp / "ingest"
            shutil.copytree(bundle_dir / task["input_data"], ingest_root / "input_data")
            shutil.copytree(ingestion_dir, ingest_root / "program")
            (ingest_root / "output").mkdir(parents=True)
            ingested = ingest_root / "ingested_program"
            ingested.mkdir(parents=True)
            with zipfile.ZipFile(submission_zip) as zf:
                zf.extractall(ingested)
            run_issues = run_program(ingest_root / "program", ingest_root, "ingestion program")
            issues += run_issues
            if any(i.level == "error" for i in run_issues):
                return issues
            res_dir_source = ingest_root / "output"
        else:
            res_dir_source = tmp / "results_submission"
            res_dir_source.mkdir(parents=True)
            with zipfile.ZipFile(submission_zip) as zf:
                zf.extractall(res_dir_source)

        score_root = tmp / "score"
        (score_root / "input").mkdir(parents=True)
        shutil.copytree(bundle_dir / task["reference_data"], score_root / "input" / "ref")
        shutil.copytree(res_dir_source, score_root / "input" / "res")
        shutil.copytree(scoring_dir, score_root / "program")
        (score_root / "output").mkdir(parents=True)
        run_issues = run_program(score_root / "program", score_root, "scoring program")
        issues += run_issues
        if any(i.level == "error" for i in run_issues):
            return issues

        scores_path = score_root / "output" / "scores.json"
        if not scores_path.exists():
            issues.append(Issue("error", "scoring program did not produce output/scores.json"))
            return issues
        try:
            scores = json.loads(scores_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            issues.append(Issue("error", f"scores.json is not valid JSON: {e}"))
            return issues

        issues.append(Issue("info", f"scores.json: {scores}"))
        for lb in comp.get("leaderboards", []) or []:
            for col in lb.get("columns", []) or []:
                if col.get("key") not in scores:
                    issues.append(Issue("error", f"leaderboard '{lb.get('title')}' expects key '{col.get('key')}' but scores.json has {list(scores.keys())}"))

    return issues


# ---------------------------------------------------------------------------
# Tier 4: Docker faithful run (best-effort, unverified against real Codabench)
# ---------------------------------------------------------------------------


def docker_available():
    """(available, reason) -- reason explains the failure so tier 4 can say *why* it
    skipped rather than a bare 'not available'."""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return True, ""
        # docker binary exists but the daemon isn't reachable -- the common case on a
        # dev box where Docker Desktop simply isn't started.
        stderr = (result.stderr or "").strip().splitlines()
        detail = stderr[-1] if stderr else f"exit {result.returncode}"
        return False, f"docker daemon not reachable ({detail})"
    except FileNotFoundError:
        return False, "docker is not installed / not on PATH"
    except subprocess.TimeoutExpired:
        return False, "docker info timed out after 15s"


def find_bundle_dockerfile(bundle_dir, explicit=None):
    """Locate a Dockerfile to build for this bundle. An explicit --dockerfile wins;
    otherwise look for the conventional names at the bundle root. Returns None if the
    bundle doesn't ship one (the normal case -- most bundles just use a stock image)."""
    if explicit:
        p = Path(explicit)
        if not p.is_absolute():
            p = bundle_dir / p
        return p if p.exists() else None
    for name in ("Dockerfile", "Dockerfile.gpu"):
        candidate = bundle_dir / name
        if candidate.exists():
            return candidate
    return None


def image_exists_locally(image):
    try:
        result = subprocess.run(["docker", "image", "inspect", image], capture_output=True, timeout=30)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def local_build_tag(comp):
    """Deterministic, obviously-local tag for an image we build ourselves. Kept distinct
    from competition.yaml's docker_image so a local test build can never be confused
    with (or accidentally pushed as) the published image."""
    title = str(comp.get("title", "benchmark")).lower()
    # Strip AFTER truncating too: a cut mid-word can leave a trailing "-", which
    # Docker rejects as an invalid repository name.
    slug = re.sub(r"[^a-z0-9]+", "-", title).strip("-")[:40].strip("-") or "benchmark"
    return f"benchmark-builder-local/{slug}:validate"


def resolve_image(bundle_dir, comp, dockerfile=None, allow_build=True):
    """Figure out which image tier 4 should run in, building or pulling as needed.
    Returns (image_or_None, issues). All local/reversible -- never pushes."""
    issues = []
    declared = comp.get("docker_image", DEFAULT_DOCKER_IMAGE)

    dockerfile_path = find_bundle_dockerfile(bundle_dir, dockerfile) if allow_build else None
    if dockerfile_path:
        tag = local_build_tag(comp)
        issues.append(Issue("info", f"building {dockerfile_path.name} -> {tag} (local only, never pushed)"))
        cmd = ["docker", "build", "-t", tag, "-f", str(dockerfile_path), str(dockerfile_path.parent)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        except subprocess.TimeoutExpired:
            issues.append(Issue("error", "docker build timed out after 30 minutes"))
            return None, issues
        if result.returncode != 0:
            tail = "\n".join((result.stderr or result.stdout or "").strip().splitlines()[-25:])
            issues.append(Issue("error", f"docker build failed:\n{tail}"))
            return None, issues
        issues.append(Issue("info", f"built {tag} successfully"))
        if declared == DEFAULT_DOCKER_IMAGE:
            issues.append(Issue("warning", f"{dockerfile_path.name} exists but competition.yaml's docker_image is still the stock default ({DEFAULT_DOCKER_IMAGE}) -- set it to the name you intend to push this custom image as before going live"))
        else:
            issues.append(Issue("info", f"validated the local build, not competition.yaml's declared docker_image ({declared}) directly -- after `docker push`, re-run with --no-build to confirm the published image matches what was just tested"))
        return tag, issues

    # No Dockerfile to build: use the declared image, pulling it if we don't have it.
    if image_exists_locally(declared):
        issues.append(Issue("info", f"using local image {declared}"))
        return declared, issues

    issues.append(Issue("info", f"image {declared} not present locally -- pulling"))
    try:
        result = subprocess.run(["docker", "pull", declared], capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        issues.append(Issue("error", f"docker pull {declared} timed out after 30 minutes"))
        return None, issues
    if result.returncode != 0:
        tail = "\n".join((result.stderr or "").strip().splitlines()[-10:])
        issues.append(Issue("error", f"docker pull {declared} failed -- is the image name/tag correct and public?\n{tail}"))
        return None, issues
    issues.append(Issue("info", f"pulled {declared}"))
    return declared, issues


def run_in_docker(image, mounts, workdir, command, label, use_gpus=False, timeout=600):
    """Run one program inside the container with Codabench's real /app/... layout.
    `mounts` is a list of (host_path, container_path, mode) tuples."""
    cmd = ["docker", "run", "--rm"]
    if use_gpus:
        cmd += ["--gpus", "all"]
    for host, container, mode in mounts:
        suffix = f":{mode}" if mode else ""
        cmd += ["-v", f"{host}:{container}{suffix}"]
    cmd += ["-w", workdir, image, "bash", "-c", command]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return [Issue("error", f"{label} timed out after {timeout}s inside {image}")]
    if result.returncode != 0:
        return [Issue("error", f"{label} exited {result.returncode} inside {image}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")]
    return [Issue("info", f"{label} ran successfully inside {image}")]


def docker_dry_run(bundle_dir, comp, task_index, submission_zip,
                   dockerfile=None, allow_build=True, use_gpus=False, rm_built_image=False):
    available, reason = docker_available()
    if not available:
        return [Issue("info", f"skipping tier 4 (faithful Docker run): {reason}")]

    task = find_task(comp, task_index)
    if task is None:
        return [Issue("error", f"no task with index {task_index} found")]

    image, issues = resolve_image(bundle_dir, comp, dockerfile=dockerfile, allow_build=allow_build)
    if image is None:
        return issues

    built_locally = image.startswith("benchmark-builder-local/")
    issues.append(Issue("warning", f"tier 4 is best-effort and has not been validated against the real Codabench platform -- treat a pass as 'the programs run in {image}', not a guarantee Codabench will accept the bundle"))

    if use_gpus:
        issues.append(Issue("info", "passing --gpus all; a GPU image also needs a GPU-capable Codabench compute worker attached to the competition's queue, which this check cannot verify"))

    try:
        with tempfile.TemporaryDirectory(prefix="codabench_docker_") as tmp:
            tmp = Path(tmp)
            ingestion_path = task.get("ingestion_program")

            if ingestion_path:
                ingest_root = tmp / "ingest"
                shutil.copytree(bundle_dir / task["input_data"], ingest_root / "input_data")
                shutil.copytree(bundle_dir / ingestion_path, ingest_root / "program")
                (ingest_root / "output").mkdir(parents=True)
                ingested = ingest_root / "ingested_program"
                ingested.mkdir(parents=True)
                with zipfile.ZipFile(submission_zip) as zf:
                    zf.extractall(ingested)
                meta = yaml.safe_load((bundle_dir / ingestion_path / "metadata.yaml").read_text(encoding="utf-8"))
                run_issues = run_in_docker(
                    image,
                    [
                        (ingest_root / "input_data", "/app/input_data", "ro"),
                        (ingest_root / "program", "/app/program", "ro"),
                        (ingested, "/app/ingested_program", "ro"),
                        (ingest_root / "output", "/app/output", None),
                    ],
                    "/app/program", meta["command"], "ingestion program", use_gpus=use_gpus,
                )
                issues += run_issues
                if any(i.level == "error" for i in run_issues):
                    return issues
                res_dir_source = ingest_root / "output"
            else:
                res_dir_source = tmp / "results_submission"
                res_dir_source.mkdir(parents=True)
                with zipfile.ZipFile(submission_zip) as zf:
                    zf.extractall(res_dir_source)

            score_root = tmp / "score"
            (score_root / "input").mkdir(parents=True)
            shutil.copytree(bundle_dir / task["reference_data"], score_root / "input" / "ref")
            shutil.copytree(res_dir_source, score_root / "input" / "res")
            shutil.copytree(bundle_dir / task["scoring_program"], score_root / "program")
            (score_root / "output").mkdir(parents=True)
            meta = yaml.safe_load((bundle_dir / task["scoring_program"] / "metadata.yaml").read_text(encoding="utf-8"))
            run_issues = run_in_docker(
                image,
                [
                    (score_root / "input", "/app/input", "ro"),
                    (score_root / "program", "/app/program", "ro"),
                    (score_root / "output", "/app/output", None),
                ],
                "/app/program", meta["command"], "scoring program", use_gpus=use_gpus,
            )
            issues += run_issues
            if any(i.level == "error" for i in run_issues):
                return issues

            scores_path = score_root / "output" / "scores.json"
            if not scores_path.exists():
                issues.append(Issue("error", "scoring program did not produce output/scores.json inside the container"))
                return issues
            try:
                scores = json.loads(scores_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                issues.append(Issue("error", f"scores.json produced in-container is not valid JSON: {e}"))
                return issues

            issues.append(Issue("info", f"scores.json (in-container): {scores}"))
            for lb in comp.get("leaderboards", []) or []:
                for col in lb.get("columns", []) or []:
                    if col.get("key") not in scores:
                        issues.append(Issue("error", f"leaderboard '{lb.get('title')}' expects key '{col.get('key')}' but in-container scores.json has {list(scores.keys())}"))
    finally:
        # Only ever remove an image we built ourselves this run -- never a pulled or
        # pre-existing one, which may be shared with other projects on this machine.
        if rm_built_image and built_locally:
            result = subprocess.run(["docker", "image", "rm", image], capture_output=True, text=True, timeout=120)
            issues.append(Issue("info", f"removed locally-built image {image}" if result.returncode == 0 else f"could not remove {image}: {(result.stderr or '').strip()}"))

    return issues


# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bundle_dir", type=Path)
    parser.add_argument("--submission", type=Path, help="Path to a submission .zip to validate against the bundle")
    parser.add_argument("--task-index", type=int, default=0)
    parser.add_argument("--docker", action="store_true", help="Also attempt tier 4 (faithful Docker run): build/pull the image and run the real programs inside it")
    parser.add_argument("--dockerfile", help="Dockerfile to build for tier 4 (default: auto-detect Dockerfile/Dockerfile.gpu at the bundle root)")
    parser.add_argument("--no-build", action="store_true", help="Tier 4: never build, always use competition.yaml's docker_image (pulling it if needed)")
    parser.add_argument("--gpus", action="store_true", help="Tier 4: pass --gpus all to docker run (needs a GPU + container toolkit)")
    parser.add_argument("--rm-built-image", action="store_true", help="Tier 4: delete the image afterwards, but only if this run built it")
    args = parser.parse_args()

    bundle_dir = args.bundle_dir.resolve()
    all_issues = []

    print("=== Tier 1: structure ===")
    issues, comp = check_structure(bundle_dir)
    all_issues += issues
    for i in issues:
        print(i)
    if comp is None:
        print("\nCannot continue -- competition.yaml is missing or invalid.")
        sys.exit(1)

    if args.submission:
        print("\n=== Tier 2: submission contract ===")
        issues = check_submission_contract(bundle_dir, comp, args.task_index, args.submission)
        all_issues += issues
        for i in issues:
            print(i)

        print("\n=== Tier 3: local functional dry run ===")
        issues = local_dry_run(bundle_dir, comp, args.task_index, args.submission)
        all_issues += issues
        for i in issues:
            print(i)

        if args.docker:
            print("\n=== Tier 4: Docker faithful run ===")
            issues = docker_dry_run(
                bundle_dir, comp, args.task_index, args.submission,
                dockerfile=args.dockerfile, allow_build=not args.no_build,
                use_gpus=args.gpus, rm_built_image=args.rm_built_image,
            )
            all_issues += issues
            for i in issues:
                print(i)

    n_errors = sum(1 for i in all_issues if i.level == "error")
    n_warnings = sum(1 for i in all_issues if i.level == "warning")
    print(f"\n{n_errors} error(s), {n_warnings} warning(s).")
    sys.exit(1 if n_errors else 0)


if __name__ == "__main__":
    main()
