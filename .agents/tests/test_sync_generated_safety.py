from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

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
        self.assertEqual(7, len(paths))

    def test_arbitrary_or_reassigned_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config = self.config()
            config["generated_roots"].append("README.md")
            with self.assertRaisesRegex(ValueError, "fixed repository-owned"):
                sync_generated.validated_generated_roots(Path(temporary), config)
            config = self.config()
            config["host_adapter_roots"]["agents"] = "README.md"
            config["generated_roots"] = ["README.md" if item == ".agents/skills" else item for item in config["generated_roots"]]
            with self.assertRaisesRegex(ValueError, "Host adapter roots"):
                sync_generated.validated_generated_roots(Path(temporary), config)
            config = self.config()
            config["generated_roots"] = ["." if item == "plugins" else item for item in config["generated_roots"]]
            with self.assertRaisesRegex(ValueError, "fixed repository-owned"):
                sync_generated.validated_generated_roots(Path(temporary), config)


if __name__ == "__main__":
    unittest.main()
