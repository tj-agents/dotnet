#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from string import Template
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


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
AZURE_SET_PREFIX = "azure."
CLOUD_NAME = re.compile(r"^[a-z][a-z0-9]{0,11}$")
SHELL_SPECIAL = re.compile(r"""[\s"'\\$`|&;<>()\[\]{}*?!~#%^]""")
INPUT_FN: Callable[[str], str] = input


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
        if "allowed" in definition and value not in definition["allowed"]:
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


def split_azure_set_overrides(pairs: Sequence[str]) -> Tuple[List[str], Dict[str, str]]:
    dotnet_pairs: List[str] = []
    azure_overrides: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair or not pair.startswith(AZURE_SET_PREFIX):
            dotnet_pairs.append(pair)
            continue
        key, raw = pair.split("=", 1)
        azure_key = key[len(AZURE_SET_PREFIX):]
        if not azure_key:
            raise ValidationError(f"--set requires a key: {pair}")
        azure_overrides[azure_key] = raw
    return dotnet_pairs, azure_overrides


def split_config_azure(config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    remaining = dict(config)
    azure = remaining.pop("azure", {})
    if not isinstance(azure, dict):
        raise ValidationError("config azure must be an object")
    return remaining, azure


def stringify_azure_value(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value)


def resolve_options(preset: Optional[str], config: Dict[str, Any], overrides: Sequence[str]) -> Tuple[Dict[str, Any], Dict[str, str], Optional[str]]:
    option_schema = schema()
    resolved = {key: definition["default"] for key, definition in option_schema.items()}
    sources = {key: "options.json" for key in option_schema}
    layers: List[Tuple[str, Dict[str, Any]]] = []
    preset_layer, preset_name = preset_values(preset)
    layers.append((f"preset:{preset_name}", preset_layer))
    layers.append(("config", config))
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


def prompt_value(key: str, definition: Mapping[str, Any], input_fn: Callable[[str], str]) -> Any:
    allowed = definition.get("allowed")
    default = definition["default"]
    choices = f" ({', '.join(str(item) for item in allowed)})" if allowed is not None else ""
    label = f"{key}{choices} [{default}]: "
    while True:
        raw = input_fn(label).strip()
        if not raw:
            return default
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw
        try:
            validate_value(key, value, definition)
        except ValidationError:
            continue
        return value


def interactive_options(option_schema: Mapping[str, Any], resolved: Dict[str, Any], sources: Mapping[str, str], input_fn: Callable[[str], str]) -> Dict[str, Any]:
    updated = dict(resolved)
    for key in sorted(option_schema):
        if sources[key] != "options.json":
            continue
        updated[key] = prompt_value(key, option_schema[key], input_fn)
    validate_constraints(updated, option_schema)
    return updated


def interactive_azure_options(azure_script: Path, azure_overrides: Dict[str, str], input_fn: Callable[[str], str]) -> Dict[str, str]:
    schema_result = run_azure(azure_script, ["options", "--schema"])
    if schema_result.returncode != 0:
        raise ScaffoldError(f"azure options --schema failed: {schema_result.stderr.strip() or schema_result.stdout.strip()}")
    try:
        azure_schema = json.loads(schema_result.stdout)
    except json.JSONDecodeError as error:
        raise ScaffoldError(f"azure options --schema returned invalid JSON: {error}") from error
    if not isinstance(azure_schema, dict):
        raise ScaffoldError("azure option schema must be an object")

    command_args = ["options"]
    for key, value in azure_overrides.items():
        command_args.extend(["--set", f"{key}={value}"])
    result = run_azure(azure_script, command_args)
    if result.returncode != 0:
        raise ScaffoldError(f"azure options failed: {result.stderr.strip() or result.stdout.strip()}")
    try:
        azure_resolved = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ScaffoldError(f"azure options returned invalid JSON: {error}") from error

    updated = dict(azure_overrides)
    for key in sorted(azure_schema):
        if key in updated:
            continue
        source = azure_resolved.get(key, {}).get("source")
        if source is not None and source != "options.json":
            continue
        updated[key] = stringify_azure_value(prompt_value(key, azure_schema[key], input_fn))
    return updated


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
        "API_PROGRAM_DECLARATIONS": "",
        "FUNCTIONS_INFRASTRUCTURE_USING": "",
        "FUNCTIONS_INFRASTRUCTURE_SETUP": "",
        "FUNCTIONS_INFRASTRUCTURE_PROJECT_REFERENCE": "",
        "FUNCTIONS_TELEMETRY_USING": "",
        "FUNCTIONS_TELEMETRY_REGISTRATION": "",
        "FUNCTIONS_HOST_JSON_PROPERTIES": "",
        "FUNCTIONS_LOCAL_SETTINGS_PROPERTIES": "",
        "FUNCTIONS_DIRECT_RESTORE": "",
        "FUNCTIONS_PACKAGE_REFERENCES": "",
        "FUNCTIONS_CLOUD_PROPERTIES": "",
        "WORKER_INFRASTRUCTURE_USING": "",
        "WORKER_INFRASTRUCTURE_SETUP": "",
        "WORKER_INFRASTRUCTURE_PROJECT_REFERENCE": "",
        "WORKER_TELEMETRY_USING": "",
        "WORKER_TELEMETRY_REGISTRATION": "",
        "WORKER_APPSETTINGS_PROPERTIES": "",
        "WORKER_PACKAGE_REFERENCES": "",
        "WORKER_CLOUD_PROPERTIES": "",
        "FIXTURE_PROVIDER_USING": "",
        "FIXTURE_CONTAINER_TYPE": "",
        "FIXTURE_CONTAINER_CREATION": "",
        "FIXTURE_CONNECTION_TYPE": "",
        "FIXTURE_CONNECTION_CREATION": "",
        "FIXTURE_DB_ADAPTER": "",
        "FIXTURE_EF_USING": "",
        "FIXTURE_SERVICE_CONFIGURATION": "",
        "FIXTURE_DAPPER_FACTORY": "",
        "FIXTURE_AUTH_USINGS": "",
        "FIXTURE_AUTH_CONFIGURATION": "",
        "FIXTURE_AUTH_HANDLER": "",
        "FIXTURE_PACKAGE_REFERENCES": "",
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
        rendered = [substitute(value, variables, f"component append {key}") for value in values]
        if key == "PACKAGE_VERSIONS":
            seen: set = set()
            deduplicated = []
            for item in rendered:
                if item in seen:
                    continue
                seen.add(item)
                deduplicated.append(item)
            rendered = deduplicated
        variables[key] = separators[key].join(rendered)
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
    if options["cloud"] == "azure":
        if "infra/app.json" in files:
            raise ScaffoldError("template collision: infra/app.json")
        cloud_name = derive_cloud_name(name, options["cloud-name"])
        profile = build_azure_profile(name, cloud_name, options)
        files["infra/app.json"] = json.dumps(profile, indent=2) + "\n"
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


def derive_cloud_name(name: str, override: str) -> str:
    if override:
        return override
    derived = re.sub(r"[^a-z0-9]", "", name.lower())[:12]
    if not derived or not derived[0].isalpha():
        raise ValidationError(f"cannot derive an azure app name from {name!r}; set --set cloud-name=<name>")
    return derived


def azure_build_command(project: str, csproj: str) -> str:
    return (
        f"dotnet publish {csproj} -c Release /t:PublishContainer "
        "-p:ContainerRegistry=$REGISTRY -p:ContainerRepository=$REPOSITORY -p:ContainerImageTag=$TAG"
    )


def azure_package_command(csproj: str, identifier: str) -> str:
    return (
        f'dotnet publish {csproj} -c Release -o "$RUNNER_TEMP/{identifier}" '
        f'&& (cd "$RUNNER_TEMP/{identifier}" && zip -qr "$PACKAGE" .)'
    )


def build_azure_profile(name: str, cloud_name: str, options: Mapping[str, Any]) -> Dict[str, Any]:
    hosts = options["hosts"]
    workloads: List[Dict[str, Any]] = []
    if "web" in hosts:
        csproj = f"src/{name}.Web/{name}.Web.csproj"
        workloads.append({
            "id": "web",
            "kind": "http",
            "port": 8080,
            "probes": {"liveness": "/health/live", "readiness": "/health/ready"},
            "runtime": {"name": "dotnet", "version": "10.0"},
            "build": {
                "image": azure_build_command("web", csproj),
                "package": azure_package_command(csproj, "web"),
            },
            "settings": {"OTEL_SERVICE_NAME": f"{cloud_name}-web"},
        })
    if "worker" in hosts:
        csproj = f"src/{name}.Worker/{name}.Worker.csproj"
        workloads.append({
            "id": "worker",
            "kind": "background",
            "build": {"image": azure_build_command("worker", csproj)},
            "settings": {"OTEL_SERVICE_NAME": f"{cloud_name}-worker"},
        })
    if "functions" in hosts:
        csproj = f"src/{name}.Functions/{name}.Functions.csproj"
        workloads.append({
            "id": "functions",
            "kind": "functions",
            "runtime": {"name": "dotnet-isolated", "version": "10.0"},
            "build": {
                "package": azure_package_command(csproj, "functions"),
                "image": azure_build_command("functions", csproj),
            },
            "settings": {"OTEL_SERVICE_NAME": f"{cloud_name}-functions"},
        })
    profile: Dict[str, Any] = {"schema_version": 1, "name": cloud_name, "workloads": workloads}
    settings: Dict[str, str] = {}
    if options["database"] == "postgres":
        settings["ConnectionStrings__Postgres"] = (
            "Host={postgres.host};Database={postgres.database};Username={postgres.user};Ssl Mode=Require"
        )
    if options["telemetry"] == "opentelemetry":
        settings["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "{monitor.connection_string}"
    settings["AZURE_CLIENT_ID"] = "{identity.client_id}"
    profile["settings"] = settings
    if options["database"] == "postgres":
        database: Dict[str, Any] = {"engine": "postgres"}
        if options["data"] in ("efcore", "efcore+dapper"):
            database["migration"] = {
                "build": {
                    "image": (
                        "dotnet tool restore && dotnet ef migrations bundle "
                        f"--project src/{name}.Infrastructure --startup-project src/{name}.Web "
                        '-r linux-x64 --self-contained -o "$RUNNER_TEMP/efbundle" --force '
                        '&& docker build -t "$IMAGE" -f infra/migration.Dockerfile "$RUNNER_TEMP" '
                        '&& docker push "$IMAGE"'
                    ),
                },
                "command": ["/efbundle"],
            }
        profile["database"] = database
    return profile


def resolve_azure_scaffold(args: argparse.Namespace) -> Optional[Path]:
    if args.azure_scaffold is not None:
        return args.azure_scaffold.expanduser()
    env = os.environ.get("AZURE_SCAFFOLD")
    return Path(env).expanduser() if env else None


def run_azure(azure_script: Path, command_args: Sequence[str]) -> subprocess.CompletedProcess:
    command = [sys.executable, "-B", str(azure_script), *command_args]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def quote_for_display(value: str) -> str:
    if value and not SHELL_SPECIAL.search(value):
        return value
    quoted = ['"']
    backslashes = 0
    for character in value:
        if character == "\\":
            backslashes += 1
            continue
        if character == '"':
            quoted.append("\\" * (backslashes * 2 + 1) + '"')
        else:
            quoted.append("\\" * backslashes + character)
        backslashes = 0
    quoted.append("\\" * (backslashes * 2) + '"')
    return "".join(quoted)


def azure_command_line(azure_script: str, project: Path, azure_overrides: Mapping[str, str]) -> str:
    parts = [
        sys.executable, "-B", azure_script, "new",
        "--into", str(project), "--profile", str(project / "infra" / "app.json"),
    ]
    for key, value in azure_overrides.items():
        parts.extend(["--set", f"{key}={value}"])
    return " ".join(quote_for_display(part) for part in parts)


def create(args: argparse.Namespace) -> None:
    validate_name(args.name)
    dotnet_pairs, cli_azure_overrides = split_azure_set_overrides(args.set)
    config_dict = config_values(args.config)
    config_dict, config_azure = split_config_azure(config_dict)
    options, sources, preset = resolve_options(args.preset, config_dict, dotnet_pairs)

    azure_overrides: Dict[str, str] = {key: stringify_azure_value(value) for key, value in config_azure.items()}
    azure_overrides.update(cli_azure_overrides)
    if azure_overrides and options["cloud"] != "azure":
        raise ValidationError("--set azure.* and config azure require cloud=azure")

    azure_script = resolve_azure_scaffold(args)
    interactive = sys.stdin.isatty() and not args.no_input and not args.dry_run
    if interactive:
        options = interactive_options(schema(), options, sources, INPUT_FN)
        if options["cloud"] == "azure" and azure_script is not None:
            azure_overrides = interactive_azure_options(azure_script, azure_overrides, INPUT_FN)

    destination = args.destination.expanduser()
    if not destination.is_dir():
        raise ScaffoldError(f"destination must be an existing directory: {destination}")
    project = destination / args.name
    if project.exists() or project.is_symlink():
        raise ScaffoldError(f"project already exists: {project}")

    files = plan(args.name, options, preset)

    if options["cloud"] == "azure" and azure_script is not None and not args.dry_run:
        with tempfile.TemporaryDirectory(prefix="dotnet-scaffold-azure-dry-") as dry_root:
            dry_into = Path(dry_root) / "into"
            dry_into.mkdir()
            profile_path = Path(dry_root) / "app.json"
            profile_path.write_text(files["infra/app.json"], encoding="utf-8")
            dry_run_args = ["new", "--into", str(dry_into), "--profile", str(profile_path), "--dry-run", "--no-input"]
            for key, value in azure_overrides.items():
                dry_run_args.extend(["--set", f"{key}={value}"])
            result = run_azure(azure_script, dry_run_args)
            if result.returncode != 0:
                raise ValidationError(f"azure dry run failed: {result.stderr.strip() or result.stdout.strip()}")

    output(destination, args.name, files, options, sources, args.dry_run)

    if args.dry_run:
        return

    if options["cloud"] != "azure":
        return

    if azure_script is None:
        print(azure_command_line("<azure-scaffold>", project, azure_overrides))
    else:
        real_run_args = [
            "new", "--into", str(project), "--profile", str(project / "infra" / "app.json"), "--no-input",
        ]
        for key, value in azure_overrides.items():
            real_run_args.extend(["--set", f"{key}={value}"])
        result = run_azure(azure_script, real_run_args)
        if result.returncode != 0:
            raise ScaffoldError(f"azure failed: {result.stderr.strip() or result.stdout.strip()}")

    scaffold_metadata_path = project / ".scaffold.json"
    metadata = json.loads(scaffold_metadata_path.read_text(encoding="utf-8"))
    metadata["azure"] = azure_overrides
    scaffold_metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def show_options(args: argparse.Namespace) -> None:
    config_dict, _ = split_config_azure(config_values(args.config))
    options, sources, _ = resolve_options(args.preset, config_dict, [])
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
    new.add_argument("--no-input", action="store_true")
    new.add_argument("--azure-scaffold", type=Path)
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
