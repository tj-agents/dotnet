#!/usr/bin/env python3
"""Generate a compilable fixture per contract csharp snippet, verbatim, for the scaffold compile gate."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest import SNIPPETS

ROOT = Path(__file__).resolve().parent
CONTRACTS_ROOT = ROOT.parents[2] / "contract"
FENCE = re.compile(r"```csharp\n(.*?)\n```", re.DOTALL)
BEGIN = "// snippet:begin\n"
END = "// snippet:end\n"


def extract_block(skill_path: Path, block: int) -> str:
    text = skill_path.read_text(encoding="utf-8")
    matches = FENCE.findall(text)
    if block < 1 or block > len(matches):
        raise ValueError(f"{skill_path} has {len(matches)} csharp blocks, requested block {block}")
    return matches[block - 1]


def fixture_text(namespace: str, verbatim: str, header: str = "", footer: str = "") -> str:
    return f"namespace {namespace};\n\n{header}{BEGIN}{verbatim}\n{END}{footer}"


def region(text: str) -> str:
    start = text.index(BEGIN) + len(BEGIN)
    end = text.index(END)
    return text[start:end].removesuffix("\n")


def write_or_check(check: bool) -> int:
    stale = False
    for snippet in SNIPPETS:
        if snippet["skip"]:
            continue
        skill_path = CONTRACTS_ROOT / snippet["skill"]
        verbatim = extract_block(skill_path, snippet["block"])
        expected = fixture_text(snippet["namespace"], verbatim, snippet.get("header", ""), snippet.get("footer", ""))
        target = ROOT / snippet["project"] / f"{snippet['id']}.Snippet.cs"
        if check:
            try:
                actual = target.read_text(encoding="utf-8")
            except OSError:
                actual = None
            if actual != expected:
                print(f"STALE: {target}")
                stale = True
            else:
                print(f"current: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected, encoding="utf-8", newline="\n")
            print(f"generated: {target}")
    return 1 if stale else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return write_or_check(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
