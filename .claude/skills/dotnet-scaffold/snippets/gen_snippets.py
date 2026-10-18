#!/usr/bin/env python3
"""Generate a compilable fixture per contract csharp snippet, verbatim, for the scaffold compile gate."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest import SNIPPETS, Snippet

ROOT = Path(__file__).resolve().parent
FENCE = re.compile(r"```csharp\n(.*?)\n```", re.DOTALL)
BEGIN = "// snippet:begin\n"
END = "// snippet:end\n"



def contract_roots() -> dict[str, Path]:
    owners = {snippet["owner"] for snippet in SNIPPETS}
    for ancestor in ROOT.parents:
        if not (ancestor / ".agents/dotnet/contract").is_dir():
            continue
        if (ancestor / "harness.json").is_file():
            return {
                owner: (ancestor if owner == "dotnet" else ancestor.parent / owner) / ".agents" / owner / "contract"
                for owner in owners
            }
        return {owner: ancestor / ".agents" / owner / "contract" for owner in owners}
    raise ValueError("Cannot locate the dotnet authored contracts for this snippet generator")


def contract_path(snippet: Snippet, roots: dict[str, Path]) -> Path:
    owner = snippet["owner"]
    path = roots[owner] / snippet["skill"]
    if not path.is_file():
        raise ValueError(
            f"Cannot locate {owner} contract: {path}. "
            f"Supply --contract-root {owner}=<owning-plugin-contract-directory>."
        )
    return path


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


def write_or_check(check: bool, roots: dict[str, Path] | None = None) -> int:
    roots = contract_roots() if roots is None else roots
    stale = False
    for snippet in SNIPPETS:
        if snippet["skip"]:
            continue
        skill_path = contract_path(snippet, roots)
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
    parser.add_argument(
        "--contract-root", action="append", default=[], metavar="OWNER=DIRECTORY",
        help="Bind an owner's contracts when plugin payloads are installed separately; repeat per owner.",
    )
    args = parser.parse_args()
    roots = contract_roots()
    for binding in args.contract_root:
        owner, separator, directory = binding.partition("=")
        if not separator or owner not in roots or not directory:
            parser.error("--contract-root requires a known OWNER=DIRECTORY")
        path = Path(directory).expanduser().resolve()
        if not path.is_dir():
            parser.error(f"--contract-root directory does not exist: {path}")
        roots[owner] = path
    try:
        return write_or_check(args.check, roots)
    except ValueError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
