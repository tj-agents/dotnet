from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, path: Path):
    loader = SourceFileLoader(name, str(path))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(module)
    return module


generator = load("dotnet_sync_generated", ROOT / ".agents/sync_generated.py")

# The exact stack-free hubs: the naming family, style, and the six generic required hubs kit's
# stack standard needs. Nothing with a real library or architecture prerequisite belongs here —
# that content lives one level down, in a family member that keeps its own profile.
CORE_MEMBERS = {
    "naming",
    "naming-collaborators",
    "naming-payloads",
    "naming-mapping",
    "naming-repositories",
    "style",
    "style-comments",
    "structure",
    "domain-design",
    "errors",
    "testing",
    "build",
    "libraries",
    # compatibility aliases of the above, keeping the same profile as their replacement
    "csharp-naming",
    "csharp-style",
    "comments",
    "naming-data-contracts",
}
ALLOWED_CORE_REQUIRES = {"none", "dotnet"}
PREREQUISITE_BEARING = (
    "http-api",
    "persistence",
    "multitenancy",
    "microservice-boundaries",
    "seeding",
    "proto",
    "dependency-injection",
    "logging",
    "validation",
    "domain-ddd",
    "domain-events",
    "errors-results",
    "errors-carriers",
    "errors-terminals",
    "testing-unit",
    "testing-integration",
    "testing-e2e",
    "structure-modules",
    "libraries-selected",
    "keyed-strategies",
    "keyed-unions",
)


class CoreProfilePinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = generator.load_config(ROOT)
        cls.skills = generator.discover(ROOT, config["namespace"])["dotnet"]

    def test_core_profile_is_exactly_the_stack_free_hubs(self) -> None:
        core = {name for name, skill in self.skills.items() if skill["metadata"]["profile"] == "core"}
        self.assertEqual(CORE_MEMBERS, core)

    def test_core_members_declare_no_real_prerequisite(self) -> None:
        for name in CORE_MEMBERS:
            requires = {item.strip() for item in self.skills[name]["metadata"]["requires"].split(",")}
            self.assertTrue(requires.issubset(ALLOWED_CORE_REQUIRES), f"{name}: {requires}")

    def test_prerequisite_bearing_skills_stay_out_of_core(self) -> None:
        for name in PREREQUISITE_BEARING:
            skill = self.skills[name]
            self.assertNotEqual("core", skill["metadata"]["profile"], name)
            requires = {item.strip() for item in skill["metadata"]["requires"].split(",")}
            self.assertFalse(requires.issubset(ALLOWED_CORE_REQUIRES), f"{name}: {requires}")


if __name__ == "__main__":
    unittest.main()
