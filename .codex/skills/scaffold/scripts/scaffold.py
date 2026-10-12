#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from string import Template
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


PACKAGE = "dotagents/dotnet"
SKILL = "dotnet:scaffold"
VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent.parent
OPTIONS_PATH = ROOT / "options.json"
PRESETS = ROOT / "presets"
COMPONENTS = ROOT / "components"
TEMPLATES = ROOT / "templates"
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
WINDOWS_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
TOKEN = re.compile(r"\$([A-Z][A-Z0-9_]*)\$")
CSHARP_KEYWORDS = {
    "abstract", "as", "base", "bool", "break", "byte", "case", "catch", "char", "checked", "class",
    "const", "continue", "decimal", "default", "delegate", "do", "double", "else", "enum", "event",
    "explicit", "extern", "false", "finally", "fixed", "float", "for", "foreach", "goto", "if",
    "implicit", "in", "int", "interface", "internal", "is", "lock", "long", "namespace", "new", "null",
    "object", "operator", "out", "override", "params", "private", "protected", "public", "readonly",
    "ref", "return", "sbyte", "sealed", "short", "sizeof", "stackalloc", "static", "string", "struct",
    "switch", "this", "throw", "true", "try", "typeof", "uint", "ulong", "unchecked", "unsafe", "ushort",
    "using", "virtual", "void", "volatile", "while"
}
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
CSHARP_INTRINSICS = {"__arglist", "__makeref", "__reftype", "__refvalue"}


class ScaffoldError(Exception):
    exit_code = 1


class ValidationError(ScaffoldError):
    exit_code = 2


def read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ScaffoldError(f"cannot read {label}: {path}") from error
    except json.JSONDecodeError as error:
        raise ValidationError(f"invalid JSON in {label}: {path}: {error.msg}") from error


def schema() -> Dict[str, Dict[str, Any]]:
    data = read_json(OPTIONS_PATH, "option schema")
    if not isinstance(data, dict):
        raise ScaffoldError("option schema must be an object")
    return data


def preset_values(name: Optional[str]) -> Tuple[Dict[str, Any], Optional[str]]:
    if name is None:
        return {}, None
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValidationError(f"invalid preset name: {name}")
    path = PRESETS / f"{name}.json"
    if not path.is_file():
        raise ValidationError(f"unknown preset: {name}")
    values = read_json(path, "preset")
    if not isinstance(values, dict):
        raise ValidationError(f"preset must be an object: {name}")
    return values, name


def config_values(path: Optional[Path]) -> Dict[str, Any]:
    if path is None:
        return {}
    values = read_json(path, "config")
    if not isinstance(values, dict):
        raise ValidationError("config must be an object")
    return values


def set_values(pairs: Sequence[str]) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValidationError(f"--set requires key=value: {pair}")
        key, raw = pair.split("=", 1)
        if not key:
            raise ValidationError(f"--set requires a key: {pair}")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            if raw.startswith("[") and raw.endswith("]"):
                value = [item.strip() for item in raw[1:-1].split(",") if item.strip()]
            else:
                value = raw
        values[key] = value
    return values


def validate_layer(values: Mapping[str, Any], option_schema: Mapping[str, Any], layer: str) -> None:
    unknown = sorted(set(values) - set(option_schema))
    if unknown:
        raise ValidationError(f"unknown option in {layer}: {', '.join(unknown)}")


def validate_value(key: str, value: Any, definition: Mapping[str, Any]) -> None:
    value_type = definition.get("type")
    if value_type == "string":
        if not isinstance(value, str):
            raise ValidationError(f"option {key} must be a string")
        if value not in definition.get("allowed", []):
            raise ValidationError(f"invalid value for {key}: {value}")
        return
    if value_type == "boolean":
        if not isinstance(value, bool):
            raise ValidationError(f"option {key} must be a boolean")
        if value not in definition.get("allowed", []):
            raise ValidationError(f"invalid value for {key}: {value}")
        return
    if value_type == "array":
        if not isinstance(value, list):
            raise ValidationError(f"option {key} must be an array")
        if definition.get("uniqueItems") and len(value) != len(set(json.dumps(item, sort_keys=True) for item in value)):
            raise ValidationError(f"option {key} contains duplicate items")
        if len(value) < definition.get("minItems", 0):
            raise ValidationError(f"option {key} requires at least {definition['minItems']} item")
        item_definition = definition.get("items", {})
        for item in value:
            if item_definition.get("type") == "string" and not isinstance(item, str):
                raise ValidationError(f"option {key} items must be strings")
            if item not in item_definition.get("allowed", []):
                raise ValidationError(f"invalid item for {key}: {item}")
        return
    raise ScaffoldError(f"unsupported option type for {key}: {value_type}")


def matches(options: Mapping[str, Any], conditions: Mapping[str, Any]) -> bool:
    for key, expected in conditions.items():
        if key not in options:
            raise ScaffoldError(f"unknown option in condition: {key}")
        actual = options.get(key)
        if not isinstance(expected, dict):
            if actual != expected:
                return False
            continue
        if set(expected) == {"contains"}:
            if not isinstance(actual, list) or expected["contains"] not in actual:
                return False
            continue
        if set(expected) == {"oneOf"}:
            values = expected["oneOf"]
            if not isinstance(values, list):
                raise ScaffoldError(f"condition {key}.oneOf must be an array")
            if actual not in values:
                return False
            continue
        raise ScaffoldError(f"condition for {key} must use contains or oneOf")
    return True


def validate_constraints(options: Mapping[str, Any], option_schema: Mapping[str, Any]) -> None:
    for key, definition in option_schema.items():
        value = options[key]
        rules_key = value if isinstance(value, (str, bool, int, float)) else None
        requires = definition.get("requires", {}).get(rules_key, {})
        conflicts = definition.get("conflicts", {}).get(rules_key, {})
        if not matches(options, requires):
            raise ValidationError(f"option {key}={value!r} requires {json.dumps(requires, sort_keys=True)}")
        if conflicts and matches(options, conflicts):
            raise ValidationError(f"option {key}={value!r} conflicts with {json.dumps(conflicts, sort_keys=True)}")
        rules = definition.get("constraints", [])
        if not isinstance(rules, list):
            raise ScaffoldError(f"option {key} constraints must be an array")
        for rule in rules:
            if not isinstance(rule, dict):
                raise ScaffoldError(f"option {key} constraint must be an object")
            when = rule.get("when", {})
            required = rule.get("requires", {})
            forbidden = rule.get("conflicts", {})
            if not isinstance(when, dict) or not isinstance(required, dict) or not isinstance(forbidden, dict):
                raise ScaffoldError(f"option {key} constraint conditions must be objects")
            if not matches(options, when):
                continue
            if not matches(options, required):
                raise ValidationError(f"option {key} requires {json.dumps(required, sort_keys=True)}")
            if forbidden and matches(options, forbidden):
                raise ValidationError(f"option {key} conflicts with {json.dumps(forbidden, sort_keys=True)}")


def resolve_options(preset: Optional[str], config: Optional[Path], overrides: Sequence[str]) -> Tuple[Dict[str, Any], Dict[str, str], Optional[str]]:
    option_schema = schema()
    resolved = {key: definition["default"] for key, definition in option_schema.items()}
    sources = {key: "options.json" for key in option_schema}
    layers: List[Tuple[str, Dict[str, Any]]] = []
    preset_layer, preset_name = preset_values(preset)
    layers.append((f"preset:{preset_name}", preset_layer))
    layers.append(("config", config_values(config)))
    layers.append(("--set", set_values(overrides)))
    for layer, values in layers:
        validate_layer(values, option_schema, layer)
        for key, value in values.items():
            resolved[key] = value
            sources[key] = layer
    for key, definition in option_schema.items():
        validate_value(key, resolved[key], definition)
    validate_constraints(resolved, option_schema)
    return resolved, sources, preset_name


def validate_name(name: str) -> None:
    if not name or WINDOWS_INVALID.search(name) or name.endswith((".", " ")):
        raise ValidationError(f"invalid project name: {name}")
    if name in {".", ".."} or "/" in name or "\\" in name:
        raise ValidationError(f"invalid project name: {name}")
    reserved = name.split(".", 1)[0].upper()
    if reserved in WINDOWS_RESERVED:
        raise ValidationError(f"invalid project name: {name}")
    parts = name.split(".")
    if any(not IDENTIFIER.fullmatch(part) or part in CSHARP_KEYWORDS or part in CSHARP_INTRINSICS for part in parts):
        raise ValidationError(f"project name must be a valid C# namespace: {name}")
    if parts[0] == "Program":
        raise ValidationError(f"project name cannot use Program as its root namespace: {name}")


def component_manifests() -> Iterable[Tuple[str, Dict[str, Any], Path]]:
    for directory in sorted(path for path in COMPONENTS.iterdir() if path.is_dir()):
        manifest = read_json(directory / "component.json", f"component {directory.name}")
        if not isinstance(manifest, dict):
            raise ScaffoldError(f"component manifest must be an object: {directory.name}")
        yield directory.name, manifest, directory


def selected_components(options: Mapping[str, Any]) -> List[Tuple[str, Dict[str, Any], Path]]:
    selected: List[Tuple[str, Dict[str, Any], Path]] = []
    for component in component_manifests():
        name, manifest, directory = component
        when = manifest.get("when", {})
        if not isinstance(when, dict):
            raise ScaffoldError(f"component {name} has invalid when")
        if not matches(options, when):
            continue
        requires = manifest.get("requires", {})
        conflicts = manifest.get("conflicts", {})
        if not matches(options, requires):
            raise ValidationError(f"component {name} requirements are not met")
        if conflicts and matches(options, conflicts):
            raise ValidationError(f"component {name} conflicts with resolved options")
        selected.append(component)
    return selected


def substitute(value: str, variables: Mapping[str, str], source: str) -> str:
    try:
        result = Template(TOKEN.sub(r"${\1}", value)).substitute(variables)
    except (KeyError, ValueError) as error:
        raise ScaffoldError(f"unresolved template token in {source}: {error}") from error
    return result.replace("\r\n", "\n").replace("\r", "\n")


def safe_relative(path: str) -> str:
    relative = Path(path)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ScaffoldError(f"unsafe template path: {path}")
    return relative.as_posix()


def plan(name: str, options: Mapping[str, Any], preset: Optional[str]) -> Dict[str, str]:
    selected = selected_components(options)
    variables = {
        "NAME": name,
        "FRAMEWORK": options["framework"],
        "INFRASTRUCTURE_PROJECT_REFERENCE": "",
        "INFRASTRUCTURE_SETUP": "",
        "INFRASTRUCTURE_USING": "",
        "INFRASTRUCTURE_USINGS": "",
        "INFRASTRUCTURE_PACKAGE_REFERENCES": "",
        "INFRASTRUCTURE_REGISTRATIONS": "",
        "PERSISTENCE_CONFIGURATION": "",
        "API_PACKAGE_REFERENCES": "",
        "API_USINGS": "",
        "API_SERVICE_REGISTRATIONS": "",
        "API_PIPELINE": "",
        "APPSETTINGS_PROPERTIES": "",
        "PACKAGE_VERSIONS": "",
        "SELECTED_STACK_ITEMS": "",
        "SCAFFOLD_GUIDANCE": "",
    }
    variable_owners: Dict[str, str] = {}
    appended: Dict[str, List[str]] = {}
    separators: Dict[str, str] = {}
    project_paths: List[str] = []
    for component_name, manifest, _ in selected:
        contributions = manifest.get("variables", {})
        if not isinstance(contributions, dict):
            raise ScaffoldError(f"component {component_name} has invalid variables")
        for key, value in contributions.items():
            if not isinstance(value, str):
                raise ScaffoldError(f"component {component_name} variable {key} must be a string")
            if key in variable_owners:
                raise ScaffoldError(f"component variable collision: {key}")
            variables[key] = substitute(value, variables, f"component {component_name}")
            variable_owners[key] = component_name
        additions = manifest.get("append", {})
        if not isinstance(additions, dict):
            raise ScaffoldError(f"component {component_name} append must be an object")
        for key, value in additions.items():
            separator = "\n"
            if isinstance(value, dict):
                if set(value) != {"value", "separator"}:
                    raise ScaffoldError(f"component {component_name} append {key} is invalid")
                value, separator = value["value"], value["separator"]
            if not isinstance(value, str) or not isinstance(separator, str):
                raise ScaffoldError(f"component {component_name} append {key} must contain strings")
            if key in separators and separators[key] != separator:
                raise ScaffoldError(f"component append separator collision: {key}")
            appended.setdefault(key, []).append(value)
            separators[key] = separator
        for project in manifest.get("projects", []):
            if not isinstance(project, str):
                raise ScaffoldError(f"component {component_name} project must be a string")
            project_paths.append(substitute(project, variables, f"component {component_name}"))
    for key, values in appended.items():
        variables[key] = separators[key].join(substitute(value, variables, f"component append {key}") for value in values)
    variables["SOLUTION_PROJECTS"] = "\n".join(f'  <Project Path="{path}" />' for path in project_paths)
    files: Dict[str, str] = {}
    source_files: List[Tuple[Path, Path]] = []
    source_files.extend((path, TEMPLATES) for path in sorted(TEMPLATES.rglob("*")) if path.is_file())
    for _, _, directory in selected:
        files_root = directory / "files"
        if files_root.is_dir():
            source_files.extend((path, files_root) for path in sorted(files_root.rglob("*")) if path.is_file())
    for source, source_root in source_files:
        relative = safe_relative(substitute(source.relative_to(source_root).as_posix(), variables, str(source)))
        if relative in files:
            raise ScaffoldError(f"template collision: {relative}")
        text = substitute(source.read_text(encoding="utf-8"), variables, str(source))
        if not text.endswith("\n"):
            text += "\n"
        files[relative] = text
    metadata = {
        "package": PACKAGE,
        "skill": SKILL,
        "version": VERSION,
        "preset": preset,
        "options": options,
    }
    if ".scaffold.json" in files:
        raise ScaffoldError("template collision: .scaffold.json")
    files[".scaffold.json"] = json.dumps(metadata, indent=2) + "\n"
    return {relative: files[relative] for relative in sorted(files)}


def output(destination: Path, name: str, files: Mapping[str, str], options: Mapping[str, Any], sources: Mapping[str, str], dry_run: bool) -> None:
    project = destination / name
    if dry_run:
        print(json.dumps({
            "destination": str(project),
            "files": list(files),
            "options": {key: {"value": options[key], "source": sources[key]} for key in options},
        }, indent=2))
        return
    try:
        project.mkdir()
    except FileExistsError as error:
        raise ScaffoldError(f"project already exists: {project}") from error
    except OSError as error:
        raise ScaffoldError(f"cannot create project directory: {project}: {error}") from error
    try:
        for relative, text in files.items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(text.encode("utf-8"))
    except OSError as error:
        raise ScaffoldError(f"cannot write project: {project}: {error}") from error
    print(json.dumps({"project": str(project), "files": list(files)}, indent=2))


def create(args: argparse.Namespace) -> None:
    validate_name(args.name)
    options, sources, preset = resolve_options(args.preset, args.config, args.set)
    destination = args.destination.expanduser()
    if not destination.is_dir():
        raise ScaffoldError(f"destination must be an existing directory: {destination}")
    project = destination / args.name
    if project.exists() or project.is_symlink():
        raise ScaffoldError(f"project already exists: {project}")
    output(destination, args.name, plan(args.name, options, preset), options, sources, args.dry_run)


def show_options(args: argparse.Namespace) -> None:
    options, sources, _ = resolve_options(args.preset, args.config, [])
    print(json.dumps({key: {"value": options[key], "source": sources[key]} for key in options}, indent=2))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Create a .NET solution in the agreed single-service layout.")
    commands = result.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new")
    new.add_argument("--name", required=True)
    new.add_argument("--destination", required=True, type=Path)
    new.add_argument("--preset")
    new.add_argument("--config", type=Path)
    new.add_argument("--set", action="append", default=[])
    new.add_argument("--dry-run", action="store_true")
    options = commands.add_parser("options")
    options.add_argument("--preset")
    options.add_argument("--config", type=Path)
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "new":
            create(args)
        else:
            show_options(args)
    except ScaffoldError as error:
        print(f"error: {error}", file=sys.stderr)
        return error.exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
