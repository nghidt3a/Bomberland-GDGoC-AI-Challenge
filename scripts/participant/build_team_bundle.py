"""Reproducibly build one-file Bomberland submissions from team_agent source.

The evaluator loads a single ``agent.py`` and may not see sibling packages, so we
bundle every internal module into one file. This script:

  1. mirrors the audited source modules into the output dir (for human review),
  2. concatenates them — in dependency order, with internal ``person_a_safety`` /
     ``person_b_strategy`` imports stripped — into ``<out>/agent.py``, rewriting the
     ``STYLE = "..."`` line so each version gets its scoring temperament,
  3. optionally zips that single file into ``<out>/submission.zip``.

Examples:

    python -m scripts.participant.build_team_bundle                 # submit_ver3 (balanced + zip)
    python -m scripts.participant.build_team_bundle --all           # the 3 submit_ver4_* (no zip)
    python -m scripts.participant.build_team_bundle --style safe --out-dir submit_ver4_safe --no-zip
"""

import argparse
import ast
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "agent" / "team_agent"

# Internal modules in dependency order: anything executed at import time (class
# defs, annotations, constants) must come after what it references.
PERSON_A = [
    "constants.py", "state.py", "danger.py", "search.py", "bomb.py",
    "masks.py", "shield.py", "obs.py", "bomb_tracker.py",
]
PERSON_B = ["loop_tracker.py", "scoring.py", "policy_rule.py"]
MIRROR_A = ["__init__.py", *PERSON_A]
MIRROR_B = ["__init__.py", *PERSON_B]
ENTRYPOINT = "agent.py"  # the Agent class wiring, bundled last

STYLES = ("balanced", "aggressive", "safe")
# The three submission versions built by --all.
VER4_TARGETS = {
    "balanced": "submit_ver4_balanced",
    "aggressive": "submit_ver4_aggressive",
    "safe": "submit_ver4_safe",
}


def _is_internal_import(stripped: str) -> bool:
    return (
        stripped.startswith("from person_a_safety")
        or stripped.startswith("from person_b_strategy")
        or stripped.startswith("import person_a_safety")
        or stripped.startswith("import person_b_strategy")
        or stripped.startswith("from .")
    )


def strip_internal_imports(src: str) -> str:
    """Drop internal imports, including parenthesised multi-line ones."""
    out: list[str] = []
    skip_until_close = False
    for line in src.splitlines():
        if skip_until_close:
            if ")" in line:
                skip_until_close = False
            continue
        if _is_internal_import(line.lstrip()):
            if "(" in line and ")" not in line:
                skip_until_close = True
            continue
        out.append(line)
    return "\n".join(out).strip("\n")


def _set_style(entry_src: str, style: str) -> str:
    new, n = re.subn(r'^STYLE = "[a-z]+"', f'STYLE = "{style}"', entry_src, count=1, flags=re.M)
    if n != 1:
        raise SystemExit("Could not find the `STYLE = \"...\"` line in agent.py to rewrite.")
    return new


def mirror_sources(dst: Path) -> None:
    for pkg, files in (("person_a_safety", MIRROR_A), ("person_b_strategy", MIRROR_B)):
        (dst / pkg).mkdir(parents=True, exist_ok=True)
        for name in files:
            shutil.copyfile(SRC / pkg / name, dst / pkg / name)


def _top_level_names(src: str) -> set[str]:
    """Top-level function/class names a module exports into the shared namespace."""
    names = set()
    for node in ast.parse(src).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _check_no_name_collisions(modules: list[tuple[str, str]]) -> None:
    """Fail the build if two bundled modules export the same top-level name.

    In separate packages such names are distinct (``danger.in_bounds`` vs
    ``search.in_bounds``); flattened into one file the later one silently shadows
    the earlier, corrupting calls. Catching it here turns a silent runtime bug
    into a loud build error.
    """
    owner: dict[str, str] = {}
    collisions = []
    for label, src in modules:
        for name in _top_level_names(src):
            if name in owner:
                collisions.append(f"{name!r}: {owner[name]} vs {label}")
            else:
                owner[name] = label
    if collisions:
        raise SystemExit("Bundle name collisions:\n  " + "\n  ".join(sorted(collisions)))


def build_bundle(style: str) -> str:
    modules = []
    for pkg, files in (("person_a_safety", PERSON_A), ("person_b_strategy", PERSON_B)):
        for name in files:
            modules.append((f"{pkg}/{name}", (SRC / pkg / name).read_text(encoding="utf-8")))
    entry_src = _set_style((SRC / ENTRYPOINT).read_text(encoding="utf-8"), style)
    modules.append((ENTRYPOINT, entry_src))
    _check_no_name_collisions(modules)

    chunks = [f"# Bundled one-file Bomberland submission (style={style}). Generated from team_agent.\n"]
    for label, src in modules[:-1]:
        chunks.append(f"\n# --- {label} ---\n\n{strip_internal_imports(src)}\n")
    chunks.append(f"\n# --- Agent entrypoint ---\n\n{strip_internal_imports(modules[-1][1])}\n")
    return "\n".join(chunks)


def build_one(style: str, out_dir: Path, make_zip: bool, multi_file: bool = False) -> None:
    """Build one submission directory.

    ``multi_file=False`` (default): a single self-contained ``agent.py`` (the bundle).
    ``multi_file=True``: the proven layout — a THIN ``agent.py`` that imports the
    mirrored ``person_a_safety`` / ``person_b_strategy`` packages (the format that
    submitted successfully for submit_rule_v1). The zip then contains agent.py +
    both package folders.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    mirror_sources(out_dir)

    if multi_file:
        agent_src = _set_style((SRC / ENTRYPOINT).read_text(encoding="utf-8"), style)
        kind = "multi-file"
        zip_members = ["agent.py", "person_a_safety", "person_b_strategy"]
    else:
        agent_src = build_bundle(style)
        kind = "bundle"
        zip_members = ["agent.py"]

    (out_dir / "agent.py").write_text(agent_src, encoding="utf-8")
    compile(agent_src, str(out_dir / "agent.py"), "exec")  # must be valid Python

    if make_zip:
        with zipfile.ZipFile(out_dir / "submission.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            for member in zip_members:
                path = out_dir / member
                if path.is_dir():
                    for f in sorted(path.rglob("*.py")):
                        zf.write(f, arcname=str(f.relative_to(out_dir)))
                else:
                    zf.write(path, arcname=member)

    rel = out_dir.name
    zip_note = " + submission.zip" if make_zip else " (no zip)"
    print(f"[{style:>10}] -> {rel}/agent.py ({len(agent_src.splitlines())} lines, {kind}){zip_note}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", default="balanced", choices=STYLES)
    parser.add_argument("--out-dir", default="submit_ver3")
    parser.add_argument("--no-zip", action="store_true")
    parser.add_argument("--multi-file", action="store_true",
                        help="thin agent.py + package folders (proven submit_rule_v1 layout)")
    parser.add_argument("--all", action="store_true",
                        help="build the 3 submit_ver4_* versions (no zip)")
    args = parser.parse_args()

    if args.all:
        for style, dirname in VER4_TARGETS.items():
            build_one(style, ROOT / dirname, make_zip=False, multi_file=args.multi_file)
    else:
        build_one(args.style, ROOT / args.out_dir, make_zip=not args.no_zip, multi_file=args.multi_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
