from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("sync_generated", ROOT / ".agents" / "sync_generated.py")
sync_generated = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_generated)


class GeneratedRootSafetyTests(unittest.TestCase):
    def config(self) -> dict:
        return json.loads((ROOT / ".agents/plugins/sources.json").read_text(encoding="utf-8"))

    def test_declared_roots_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = sync_generated.validated_generated_roots(Path(temporary), self.config())
        self.assertEqual(6, len(paths))

    def test_generated_root_dangling_link_ancestor_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = Path.is_symlink
            with mock.patch.object(
                Path,
                "is_symlink",
                autospec=True,
                side_effect=lambda path: path.name == ".codex" or original(path),
            ):
                with self.assertRaisesRegex(ValueError, "ancestor"):
                    sync_generated.validated_generated_roots(root, self.config())

    def test_wrapper_fails_when_python_cannot_launch(self) -> None:
        pwsh = shutil.which("pwsh")
        if pwsh is None:
            self.skipTest("PowerShell is unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            environment = os.environ.copy()
            environment["PATH"] = temporary
            result = subprocess.run(
                [
                    pwsh,
                    "-NoProfile",
                    "-NonInteractive",
                    "-File",
                    str(ROOT / ".agents/sync-generated.ps1"),
                    "-Check",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("python", f"{result.stdout}\n{result.stderr}".lower())

    def test_arbitrary_or_reassigned_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config = self.config()
            config["generated_roots"].append("README.md")
            with self.assertRaisesRegex(ValueError, "fixed repository-owned"):
                sync_generated.validated_generated_roots(Path(temporary), config)
            config = self.config()
            config["host_adapter_roots"]["codex"] = "README.md"
            config["generated_roots"] = ["README.md" if item == ".codex/skills" else item for item in config["generated_roots"]]
            with self.assertRaisesRegex(ValueError, "Host adapter roots"):
                sync_generated.validated_generated_roots(Path(temporary), config)
            config = self.config()
            config["generated_roots"] = ["." if item == "plugins" else item for item in config["generated_roots"]]
            with self.assertRaisesRegex(ValueError, "fixed repository-owned"):
                sync_generated.validated_generated_roots(Path(temporary), config)


if __name__ == "__main__":
    unittest.main()
