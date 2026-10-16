#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "scripts" / "scaffold.py"
SNIPPETS_DIR = ROOT / "snippets"
DUNET_VERSION = "1.16.2"

SNIPPET_PROJECT_FOLDERS = {
    "infrastructure": ("src", "Infrastructure"),
    "web": ("src", "Web"),
    "unit-tests": ("tests", "UnitTests"),
    "integration-tests": ("tests", "IntegrationTests"),
    "e2e-tests": ("tests", "E2ETests"),
}

SNIPPET_SHARED_FILES = {
    "infrastructure": (
        "GlobalUsings.cs", "SharedGlobalUsing.cs", "EventContracts.Stubs.cs", "Reunion.Stubs.cs",
        "DataAccess.Stubs.cs", "DataAccessUnitOfWork.Stubs.cs", "DataAccessUnitOfWorkInfrastructure.Stubs.cs",
        "AzureServiceBus.Stubs.cs",
        "Hosting.Stubs.cs", "Grpc.Stubs.cs", "GrpcCore.Stubs.cs", "GrpcClientFactory.Stubs.cs",
    ),
    "web": ("GlobalUsings.cs", "SharedGlobalUsing.cs"),
    "unit-tests": ("GlobalUsings.cs", "SharedGlobalUsing.cs", "DataAccess.Stubs.cs"),
    "integration-tests": ("GlobalUsings.cs",),
    "e2e-tests": ("GlobalUsings.cs", "E2E.Stubs.cs"),
}


def run(command: Sequence[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def standards_arguments() -> list[str]:
    adopter = os.environ.get("PLUGIN_LOCK_ADOPTER")
    revision = os.environ.get("MARKETPLACE_REVISION")
    if not adopter or not revision:
        raise RuntimeError("PLUGIN_LOCK_ADOPTER and MARKETPLACE_REVISION are required")
    adopter_path = Path(adopter)
    if not adopter_path.is_file():
        raise RuntimeError("PLUGIN_LOCK_ADOPTER must be a file")
    return ["--plugin-lock-adopter", str(adopter_path), "--marketplace-revision", revision]


def scaffold_command(destination: Path, name: str, preset: str, overrides: Sequence[str] = ()) -> list[str]:
    command = [
        sys.executable, "-B", str(SCAFFOLD), "new",
        "--name", name, "--destination", str(destination), "--preset", preset, "--no-input",
        *standards_arguments(),
    ]
    for override in overrides:
        command.extend(["--set", override])
    return command


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
        command = scaffold_command(destination, name, preset, overrides)
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
        command = scaffold_command(destination, name, preset, overrides)
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


def _add_package_version(packages_props: Path, package: str, version: str) -> None:
    text = packages_props.read_text(encoding="utf-8")
    if package in text:
        return
    anchor = "</Project>"
    if anchor not in text:
        raise AssertionError(f"snippet gate: {packages_props} has no </Project> to anchor on")
    addition = f'  <ItemGroup>\n    <PackageVersion Include="{package}" Version="{version}" />\n  </ItemGroup>\n'
    packages_props.write_text(text.replace(anchor, addition + anchor, 1), encoding="utf-8")


def _add_package_reference(csproj: Path, package: str, private_assets: str | None = None) -> None:
    text = csproj.read_text(encoding="utf-8")
    if package in text:
        return
    anchor = "</Project>"
    if anchor not in text:
        raise AssertionError(f"snippet gate: {csproj} has no </Project> to anchor on")
    attribute = f' PrivateAssets="{private_assets}"' if private_assets else ""
    addition = f'  <ItemGroup>\n    <PackageReference Include="{package}"{attribute} />\n  </ItemGroup>\n'
    csproj.write_text(text.replace(anchor, addition + anchor, 1), encoding="utf-8")


def snippet_compile_gate(name: str) -> None:
    with tempfile.TemporaryDirectory(prefix=f"dotnet-scaffold-{name}-") as temporary:
        destination = Path(temporary)
        command = scaffold_command(destination, name, "sandbox")
        run(command, ROOT)
        project = destination / name
        solution = project / f"{name}.slnx"

        packages_props = project / "Directory.Packages.props"
        infra_csproj = project / "src" / f"{name}.Infrastructure" / f"{name}.Infrastructure.csproj"
        _add_package_version(packages_props, "Dunet", DUNET_VERSION)
        _add_package_reference(infra_csproj, "Dunet", private_assets="all")

        unit_tests_csproj = project / "tests" / f"{name}.UnitTests" / f"{name}.UnitTests.csproj"
        _add_package_reference(unit_tests_csproj, "Microsoft.EntityFrameworkCore")

        e2e_tests_dir = project / "tests" / f"{name}.E2ETests"
        e2e_tests_dir.mkdir(parents=True)
        e2e_tests_csproj = e2e_tests_dir / f"{name}.E2ETests.csproj"
        e2e_tests_csproj.write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            '  <PropertyGroup>\n    <IsTestProject>true</IsTestProject>\n  </PropertyGroup>\n'
            '</Project>\n',
            encoding="utf-8",
        )
        for package, version in (
            ("Reqnroll", "3.3.4"),
            ("Reqnroll.xUnit", "3.3.4"),
            ("Microsoft.Playwright", "1.63.0"),
            ("Shouldly", "4.3.0"),
        ):
            _add_package_version(packages_props, package, version)
            _add_package_reference(e2e_tests_csproj, package)
        _add_package_reference(e2e_tests_csproj, "Microsoft.NET.Test.Sdk")
        _add_package_reference(e2e_tests_csproj, "xunit.runner.visualstudio", private_assets="all")
        solution_text = solution.read_text(encoding="utf-8")
        solution.write_text(
            solution_text.replace(
                "</Solution>",
                f'  <Project Path="tests/{name}.E2ETests/{name}.E2ETests.csproj" />\n</Solution>',
                1,
            ),
            encoding="utf-8",
        )

        for project_kind, (top, suffix) in SNIPPET_PROJECT_FOLDERS.items():
            target = project / top / f"{name}.{suffix}" / "Snippets"
            target.mkdir(parents=True, exist_ok=True)
            for filename in SNIPPET_SHARED_FILES[project_kind]:
                shutil.copy2(SNIPPETS_DIR / "_shared" / filename, target / filename)
            shutil.copy2(SNIPPETS_DIR / "_shared" / "Snippets.editorconfig", target / ".editorconfig")
            source_dir = SNIPPETS_DIR / project_kind
            for item in sorted(source_dir.glob("*.cs")):
                shutil.copy2(item, target / item.name)

        functions_project = project / "src" / f"{name}.Functions" / f"{name}.Functions.csproj"
        if functions_project.is_file():
            run(["dotnet", "restore", str(functions_project)], project)
        run(["dotnet", "restore", str(solution)], project)
        run(["dotnet", "build", str(solution), "--configuration", "Release", "--no-restore"], project)
        print("snippet compile gate confirmed: every compilable contract snippet builds under the scaffold's own analyzers")


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
        ("SandboxAzureSample", "sandbox", ("cloud=azure", "azure.workflows=false"), True),
    )
    for name, preset, overrides, azure in configurations:
        verify(name, preset, overrides, azure)
    snippet_compile_gate("SnippetGateSample")
    negative_path_gates("NegativeGateSample", "web", ('tests=["integration"]',))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
