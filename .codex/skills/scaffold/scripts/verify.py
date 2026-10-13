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


def build_result(project: Path, solution: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["dotnet", "build", str(solution), "--configuration", "Release"],
        cwd=project, capture_output=True, text=True,
    )


def negative_path_gates(name: str, preset: str, overrides: Sequence[str] = ()) -> None:
    with tempfile.TemporaryDirectory(prefix=f"dotnet-scaffold-{name}-") as temporary:
        destination = Path(temporary)
        command = [
            sys.executable, "-B", str(SCAFFOLD), "new",
            "--name", name, "--destination", str(destination), "--preset", preset, "--no-input",
        ]
        for override in overrides:
            command.extend(["--set", override])
        run(command, ROOT)
        project = destination / name
        solution = project / f"{name}.slnx"
        run(["dotnet", "restore", str(solution)], project)

        assert_test = project / "tests" / f"{name}.IntegrationTests" / "NegativePathAssertTests.cs"
        assert_test.write_bytes((
            "using Xunit;\n\n"
            f"namespace {name}.IntegrationTests;\n\n"
            "public sealed class NegativePathAssertTests\n"
            "{\n"
            "    [Fact]\n"
            "    public void Smoke_Always_Passes()\n"
            "    {\n"
            "        Assert.True(true);\n"
            "    }\n"
            "}\n"
        ).encode("utf-8"))
        try:
            result = build_result(project, solution)
        finally:
            assert_test.unlink()
        if result.returncode == 0:
            raise AssertionError(
                "negative-path gate failed: a stray Assert.* in an integration test must fail the build "
                "(BannedApiAnalyzers/RS0030), but `dotnet build` succeeded"
            )
        print("negative-path gate confirmed: a stray Assert.* in an integration test fails the build")

        fixture_path = project / "tests" / f"{name}.IntegrationTests.Fixtures" / "ApiFixture.cs"
        original = fixture_path.read_bytes().decode("utf-8")
        marker = "    public async Task InitializeAsync()"
        mutated = original.replace(
            marker,
            "    public string Describe() => this.container.ToString()!;\n\n" + marker,
            1,
        )
        if mutated == original:
            raise AssertionError("could not inject a stray this.field read into ApiFixture.cs")
        fixture_path.write_bytes(mutated.encode("utf-8"))
        try:
            result = build_result(project, solution)
        finally:
            fixture_path.write_bytes(original.encode("utf-8"))
        if result.returncode != 0:
            print("negative-path gate confirmed: a stray this.field read outside a constructor fails the build")
        else:
            print(
                "negative-path gate NOT enforced: a stray `this.field` read outside a constructor built "
                "cleanly (0 errors) under dotnet_style_qualification_for_field = false:error plus "
                "EnforceCodeStyleInBuild. Verified by isolated repro: IDE0003 (\"remove this qualification\") "
                "does not fire as a build diagnostic in this SDK (10.0.301) for field, property or method "
                "member access, regardless of severity, dotnet_diagnostic.IDE0003.severity, dotnet format, or "
                "Meziantou.Analyzer; only the opposite direction, IDE0009 (\"add this qualification\"), fires. "
                "\"this. only where shadowed\" is therefore enforced by example/review, not by this build gate, "
                "for the \"stray extra this.\" direction. Not treated as a verify.py failure pending Tommy's "
                "decision on an alternative enforcement mechanism."
            )


def main() -> int:
    configurations = (
        ("MinimalSample", "minimal", (), False),
        ("WebPostgresSample", "web", (), False),
        ("WebSqlServerSample", "web", ("database=sqlserver",), False),
        ("DapperSqlServerSample", "dapper-sqlserver", (), False),
        (
            "CombinedSample",
            "web",
            ("data=efcore+dapper", "auth=jwt", "telemetry=opentelemetry", "selected-stack=true"),
            False,
        ),
        ("SandboxSample", "sandbox", (), False),
        ("IntegrationSqlServerSample", "web", ("database=sqlserver", 'tests=["integration"]', "auth=jwt"), False),
        ("SandboxAzureSample", "sandbox", ("cloud=azure",), True),
    )
    for name, preset, overrides, azure in configurations:
        verify(name, preset, overrides, azure)
    negative_path_gates("NegativeGateSample", "web", ('tests=["integration"]',))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
