#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "scripts" / "scaffold.py"


def run(command: Sequence[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def terraform_gate(project: Path) -> None:
    for root_name in ("foundation", "instance"):
        root = project / "infra" / root_name
        if not root.is_dir():
            continue
        run(["terraform", "fmt", "-check"], root)
        run(["terraform", "init", "-backend=false"], root)
        run(["terraform", "validate"], root)


def verify(name: str, preset: str, overrides: Sequence[str] = (), azure: bool = False) -> None:
    azure_scaffold = os.environ.get("AZURE_SCAFFOLD")
    with tempfile.TemporaryDirectory(prefix=f"dotnet-scaffold-{name}-") as temporary:
        destination = Path(temporary)
        command = [
            sys.executable, "-B", str(SCAFFOLD), "new",
            "--name", name, "--destination", str(destination), "--preset", preset, "--no-input",
        ]
        for override in overrides:
            command.extend(["--set", override])
        if azure and azure_scaffold:
            command.extend(["--azure-scaffold", azure_scaffold])
        run(
            command,
            ROOT,
        )
        project = destination / name
        solution = project / f"{name}.slnx"
        functions_project = project / "src" / f"{name}.Functions" / f"{name}.Functions.csproj"
        if functions_project.is_file():
            run(["dotnet", "restore", str(functions_project)], project)
        run(["dotnet", "restore", str(solution)], project)
        run(["dotnet", "build", str(solution), "--configuration", "Release", "--no-restore"], project)
        run(["dotnet", "test", str(solution), "--configuration", "Release", "--no-build"], project)
        if azure and azure_scaffold:
            terraform_gate(project)


def main() -> int:
    configurations = (
        ("MinimalSample", "minimal", (), False),
        ("ApiPostgresSample", "api", (), False),
        ("ApiSqlServerSample", "api", ("database=sqlserver",), False),
        ("DapperSqlServerSample", "dapper-sqlserver", (), False),
        (
            "CombinedSample",
            "api",
            ("data=efcore+dapper", "auth=jwt", "telemetry=opentelemetry", "selected-stack=true"),
            False,
        ),
        ("SandboxSample", "sandbox", (), False),
        ("IntegrationSqlServerSample", "api", ("database=sqlserver", 'tests=["integration"]', "auth=jwt"), False),
        ("SandboxAzureSample", "sandbox", ("cloud=azure",), True),
    )
    for name, preset, overrides, azure in configurations:
        verify(name, preset, overrides, azure)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
