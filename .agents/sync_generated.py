#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat


FRONTMATTER = re.compile(r"\A---\n(?P<header>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)
NAME = re.compile(r"^[a-z][a-z0-9-]*$")
QUALIFIED_SKILL = re.compile(r"(?<![-/\w])(dotnet|engineering):(?!:)([a-z][a-z0-9-]+)")
REQUIRED_METADATA = ("name", "description", "kind", "domain", "profile", "applicability", "requires", "provenance")
RESERVED_AGENT_DIRS = {"plugins", "skills", "tests"}
EXPECTED_GENERATED_ROOTS = (
    ".codex/skills",
    ".claude/skills",
    "plugins",
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".agents/INDEX.md",
)
EXPECTED_HOST_ADAPTER_ROOTS = {"codex": ".codex/skills", "claude": ".claude/skills"}
EXPECTED_HOST_MANIFEST_ROOTS = {"codex": ".agents/plugins/manifests/codex", "claude": ".agents/plugins/manifests/claude"}
EXPECTED_MARKETPLACE_TEMPLATES = {
    "codex": ".agents/plugins/manifests/codex/marketplace.json",
    "claude": ".agents/plugins/manifests/claude/marketplace.json",
}
EXPECTED_MARKETPLACE_OUTPUTS = {"codex": ".agents/plugins/marketplace.json", "claude": ".claude-plugin/marketplace.json"}
TIER_DECLARATION = ".agents/tiers/dotnet.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def load(path: Path):
    return json.loads(read(path))


def metadata(body: str, source: Path) -> dict[str, str]:
    match = FRONTMATTER.match(body)
    if match is None:
        raise ValueError(f"Missing frontmatter: {source}")
    values: dict[str, str] = {}
    for line in match.group("header").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    for field in REQUIRED_METADATA:
        if not values.get(field):
            raise ValueError(f"{source}: missing {field}")
    if not NAME.fullmatch(values["name"]):
        raise ValueError(f"{source}: invalid skill name {values['name']}")
    if not NAME.fullmatch(values["kind"]):
        raise ValueError(f"{source}: kind must be one lowercase ASCII word")
    return values


def split_tags(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def discover(root: Path, config: dict) -> dict[str, dict]:
    agents_root = root / config["scope"]["root"]
    found: dict[str, dict] = {}
    for kind_dir in sorted(path for path in agents_root.iterdir() if path.is_dir() and path.name not in RESERVED_AGENT_DIRS):
        for path in sorted(kind_dir.glob("*/SKILL.md")):
            body = read(path)
            if "\ufeff" in body:
                raise ValueError(f"{path}: embedded UTF-8 BOM")
            values = metadata(body, path)
            name = values["name"]
            if name != path.parent.name:
                raise ValueError(f"{path}: folder and public skill name differ")
            if values["kind"] != kind_dir.name:
                raise ValueError(f"{path}: kind metadata and folder differ")
            if values["domain"] != "dotnet":
                raise ValueError(f"{path}: domain must be dotnet")
            if name in found:
                raise ValueError(f"Duplicate public skill name: {name}")
            lowered = body.lower()
            if "standards/" in lowered or "concertable" in lowered:
                raise ValueError(f"{path}: canonical definition retains a retired source path or product owner")
            found[name] = {
                "name": name,
                "body": body,
                "metadata": values,
                "relative": path.relative_to(root).as_posix(),
            }
    if not found:
        raise ValueError("No canonical skills discovered")
    return found


def validated_config(config: dict) -> None:
    if config.get("scope") != {"root": ".agents", "layout": "kind", "domain": "dotnet", "plugin": "dotnet"}:
        raise ValueError("The single dotnet scope declaration changed")
    if config.get("host_adapter_roots") != EXPECTED_HOST_ADAPTER_ROOTS:
        raise ValueError("Host adapter roots must remain repository-owned paths")
    if config.get("host_manifest_roots") != EXPECTED_HOST_MANIFEST_ROOTS:
        raise ValueError("Host manifest roots must remain repository-owned paths")
    if config.get("marketplace_templates") != EXPECTED_MARKETPLACE_TEMPLATES:
        raise ValueError("Marketplace templates must remain repository-owned paths")
    if config.get("marketplace_outputs") != EXPECTED_MARKETPLACE_OUTPUTS:
        raise ValueError("Marketplace outputs must remain repository-owned paths")
    declared = config.get("generated_roots", [])
    if len(declared) != len(set(declared)) or set(declared) != set(EXPECTED_GENERATED_ROOTS):
        raise ValueError("Generated roots must equal the fixed repository-owned output set")
    if config.get("packages") != {"dotnet": {"scope": "dotnet"}} or config.get("package_root") != "plugins":
        raise ValueError("Package outputs must remain rooted at plugins/dotnet")


def validate_tier(root: Path) -> None:
    declaration = load(root / TIER_DECLARATION)
    if declaration.get("schema_version") not in (1, 2):
        raise ValueError("The tier declaration must declare a known schema_version")
    if declaration.get("tier") != "dotnet" or declaration.get("applies") != "stack-present":
        raise ValueError("dotnet is a stack tier and must declare itself as one")
    if "tj-agents/dotnet" not in (declaration.get("owner_repository") or []):
        raise ValueError("The tier declaration must name this repository as its owner")
    detect = declaration.get("detect") or {}
    if not any(detect.get(field) for field in ("files", "globs", "content", "remote")):
        raise ValueError("A stack tier must declare at least one detectable marker")


def validate_host_metadata(codex: dict, claude: dict, codex_marketplace: dict, claude_marketplace: dict) -> None:
    for field in ("name", "description", "author", "repository", "skills", "keywords"):
        if not codex.get(field) or codex.get(field) != claude.get(field):
            raise ValueError(f"Claude and Codex manifests disagree on {field}")
    if codex.get("name") != "dotnet" or codex.get("skills") != "./skills/":
        raise ValueError("Host manifests must retain the dotnet identity and packaged skills path")
    if "version" in claude:
        raise ValueError("Claude manifest must remain commit-versioned and omit version")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(codex.get("version", ""))):
        raise ValueError("Codex manifest must declare a semantic version")
    if not claude.get("displayName") or claude.get("displayName") != codex.get("interface", {}).get("displayName"):
        raise ValueError("Claude and Codex manifests disagree on display name")

    codex_entries = codex_marketplace.get("plugins", [])
    claude_entries = claude_marketplace.get("plugins", [])
    if len(codex_entries) != 1 or len(claude_entries) != 1:
        raise ValueError("Each marketplace must declare exactly the dotnet plugin")
    codex_entry, claude_entry = codex_entries[0], claude_entries[0]
    if codex_entry.get("name") != "dotnet" or claude_entry.get("name") != "dotnet":
        raise ValueError("Each marketplace must declare exactly the dotnet plugin")
    if codex_entry.get("source") != {"source": "local", "path": "./plugins/dotnet"}:
        raise ValueError("Codex marketplace must use the repository-local dotnet package")
    if codex_entry.get("policy") != {"installation": "INSTALLED_BY_DEFAULT", "authentication": "ON_INSTALL"}:
        raise ValueError("Codex marketplace policy changed")
    if claude_entry.get("source") != "./plugins/dotnet":
        raise ValueError("Claude marketplace must use the repository-local dotnet package")
    if not codex_entry.get("category") or claude_entry.get("category") != codex_entry.get("category"):
        raise ValueError("Claude and Codex marketplaces disagree on category")
    for field in ("description", "keywords"):
        if claude_entry.get(field) != claude.get(field):
            raise ValueError(f"Claude marketplace and plugin disagree on {field}")


def validate(root: Path, config: dict, payloads: dict, skills: dict[str, dict]) -> None:
    validated_config(config)
    if payloads.get("publicPlugins") != ["dotnet"] or payloads.get("payloads") != {"dotnet": ["dotnet"]}:
        raise ValueError("The public dotnet package declaration changed")
    profiles = payloads.get("profiles", {})
    assigned: list[str] = []
    for profile, names in profiles.items():
        if not NAME.fullmatch(profile) or len(names) != len(set(names)):
            raise ValueError(f"Invalid profile: {profile}")
        assigned.extend(names)
    if len(assigned) != len(set(assigned)) or set(assigned) != set(skills):
        raise ValueError("Every skill must belong to exactly one selection profile")
    if profiles.get("core") != ["comments", "csharp-naming", "csharp-style"]:
        raise ValueError("The stack-free core profile changed")
    for skill in skills.values():
        values = skill["metadata"]
        if skill["name"] not in profiles.get(values["profile"], []):
            raise ValueError(f"{skill['name']}: profile metadata disagrees with payloads")
        for namespace, name in QUALIFIED_SKILL.findall(skill["body"]):
            if namespace == "dotnet" and name not in skills:
                raise ValueError(f"{skill['name']}: missing local skill reference {namespace}:{name}")
    validate_tier(root)
    codex = load(root / EXPECTED_HOST_MANIFEST_ROOTS["codex"] / "dotnet.json")
    claude = load(root / EXPECTED_HOST_MANIFEST_ROOTS["claude"] / "dotnet.json")
    codex_marketplace = load(root / EXPECTED_MARKETPLACE_TEMPLATES["codex"])
    claude_marketplace = load(root / EXPECTED_MARKETPLACE_TEMPLATES["claude"])
    validate_host_metadata(codex, claude, codex_marketplace, claude_marketplace)


def adapter_body(skill: dict, adapter_root: str) -> str:
    source = PurePosixPath(skill["relative"])
    adapter = PurePosixPath(adapter_root) / skill["name"] / "SKILL.md"
    relative = PurePosixPath(os.path.relpath(source.as_posix(), adapter.parent.as_posix()).replace("\\", "/"))
    match = FRONTMATTER.match(skill["body"])
    title = next((line for line in match.group("body").splitlines() if line.startswith("# ")), f"# {skill['name']}")
    return (
        f"---\n{match.group('header')}\n---\n\n{title}\n\n"
        f"Read and follow the [canonical shared definition]({relative.as_posix()}) in full.\n"
        "This discovery entry is generated; edit the referenced `.agents/` definition.\n"
    )


def build(root: Path) -> tuple[dict[str, bytes], dict]:
    config = load(root / ".agents/plugins/sources.json")
    payloads = load(root / ".agents/plugins/payloads.json")
    skills = discover(root, config)
    validate(root, config, payloads, skills)
    output: dict[str, bytes] = {}

    def emit(relative: str, data: str | bytes) -> None:
        key = PurePosixPath(relative).as_posix()
        if key in output:
            raise ValueError(f"Duplicate generated output: {key}")
        output[key] = data.encode("utf-8") if isinstance(data, str) else data

    for adapter_root in EXPECTED_HOST_ADAPTER_ROOTS.values():
        for skill in skills.values():
            emit(f"{adapter_root}/{skill['name']}/SKILL.md", adapter_body(skill, adapter_root))

    lines = ["# dotnet capabilities", "", "Generated from canonical `.agents/<kind>/<name>/` definitions.", ""]
    for skill in sorted(skills.values(), key=lambda item: (item["metadata"]["kind"], item["name"])):
        values = skill["metadata"]
        lines.append(f"- `{skill['name']}` — {values['kind']} — {values['profile']} — `{skill['relative']}`")
    lines.append("")
    emit(".agents/INDEX.md", "\n".join(lines))

    for skill in sorted(skills.values(), key=lambda item: item["name"]):
        emit(f"plugins/dotnet/skills/{skill['name']}/SKILL.md", skill["body"])
    for host, manifest_root in EXPECTED_HOST_MANIFEST_ROOTS.items():
        emit(f"plugins/dotnet/.{host}-plugin/plugin.json", read(root / manifest_root / "dotnet.json"))
    emit("plugins/dotnet/tier.json", read(root / TIER_DECLARATION))
    emit("plugins/dotnet/INDEX.md", "\n".join(lines).replace("# dotnet capabilities", "# dotnet package capabilities"))
    selection = {
        "plugin": "dotnet",
        "profiles": payloads["profiles"],
        "skills": [
            {
                "name": skill["name"],
                "kind": skill["metadata"]["kind"],
                "profile": skill["metadata"]["profile"],
                "applicability": split_tags(skill["metadata"]["applicability"]),
                "requires": split_tags(skill["metadata"]["requires"]),
                "provenance": split_tags(skill["metadata"]["provenance"]),
            }
            for skill in sorted(skills.values(), key=lambda item: item["name"])
        ],
    }
    emit("plugins/dotnet/selection.json", json.dumps(selection, indent=2) + "\n")
    for host, template in EXPECTED_MARKETPLACE_TEMPLATES.items():
        emit(EXPECTED_MARKETPLACE_OUTPUTS[host], read(root / template))
    return output, config


def is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    if is_junction is not None and is_junction():
        return True
    if os.name != "nt":
        return False
    try:
        attributes = path.lstat().st_file_attributes
    except FileNotFoundError:
        return False
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_point)


def validated_generated_roots(root: Path, config: dict) -> list[Path]:
    validated_config(config)
    resolved_root = root.resolve()
    result: list[Path] = []
    for value in config["generated_roots"]:
        relative = PurePosixPath(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Invalid generated root: {value}")
        lexical = resolved_root.joinpath(*relative.parts)
        ancestor = resolved_root
        for part in relative.parts:
            ancestor = ancestor / part
            if is_link_or_junction(ancestor):
                raise ValueError(f"Generated root ancestor must not be a link or junction: {ancestor}")
        path = lexical.resolve()
        if path == resolved_root or not path.is_relative_to(resolved_root):
            raise ValueError(f"Generated root escapes or equals repository root: {value}")
        if is_link_or_junction(lexical):
            raise ValueError(f"Generated root must not be a link or junction: {value}")
        result.append(path)
    return result


def existing_files(root: Path, generated_roots: list[str]) -> set[str]:
    result: set[str] = set()
    for value in generated_roots:
        path = root / value
        if path.is_dir():
            result.update(item.relative_to(root).as_posix() for item in path.rglob("*") if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc")
        elif path.is_file():
            result.add(path.relative_to(root).as_posix())
    return result


def synchronize(root: Path, check: bool) -> int:
    output, config = build(root)
    expected = set(output)
    actual = existing_files(root, config["generated_roots"])
    stale = sorted(path for path in expected & actual if (root / path).read_bytes() != output[path])
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if check:
        for label, paths in (("MISSING", missing), ("STALE", stale), ("EXTRA", extra)):
            for path in paths:
                print(f"{label}: {path}")
        if missing or stale or extra:
            return 1
        print(f"generated outputs current: {len(expected)} files, {len(discover(root, config))} definitions")
        return 0
    for path in validated_generated_roots(root, config):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    for relative, data in output.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"generated {len(expected)} files from {len(discover(root, config))} definitions")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return synchronize(args.root.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
