#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "scripts" / "scaffold.py"


def run(command: Sequence[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def verify(name: str, preset: str, overrides: Sequence[str] = ()) -> None:
    with tempfile.TemporaryDirectory(prefix=f"dotnet-scaffold-{name}-") as temporary:
        destination = Path(temporary)
        command = [sys.executable, "-B", str(SCAFFOLD), "new", "--name", name, "--destination", str(destination), "--preset", preset]
        for override in overrides:
            command.extend(["--set", override])
        run(
            command,
            ROOT,
        )
        project = destination / name
        solution = project / f"{name}.slnx"
        run(["dotnet", "restore", str(solution)], project)
        run(["dotnet", "build", str(solution), "--configuration", "Release", "--no-restore"], project)
        run(["dotnet", "test", str(solution), "--configuration", "Release", "--no-build"], project)


def main() -> int:
    configurations = (
        ("MinimalSample", "minimal", ()),
        ("ApiPostgresSample", "api", ()),
        ("ApiSqlServerSample", "api", ("database=sqlserver",)),
        ("DapperSqlServerSample", "dapper-sqlserver", ()),
        (
            "CombinedSample",
            "api",
            ("data=efcore+dapper", "auth=jwt", "telemetry=opentelemetry", "selected-stack=true"),
        ),
    )
    for name, preset, overrides in configurations:
        verify(name, preset, overrides)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
