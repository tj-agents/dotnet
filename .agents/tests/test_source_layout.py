from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("sync_generated", ROOT / ".agents" / "sync_generated.py")
sync_generated = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_generated)


class SourceLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((ROOT / ".agents/plugins/sources.json").read_text(encoding="utf-8"))
        cls.payloads = json.loads((ROOT / ".agents/plugins/payloads.json").read_text(encoding="utf-8"))
        cls.skills = sync_generated.discover(ROOT, cls.config)

    def test_inventory_and_kinds(self) -> None:
        self.assertEqual(30, len(self.skills))
        operations = {name for name, skill in self.skills.items() if skill["metadata"]["kind"] == "operation"}
        self.assertEqual({"e2e-api-debug", "e2e-debug", "e2e-ui-debug", "integration-debug"}, operations)
        self.assertEqual({"contract", "operation"}, {skill["metadata"]["kind"] for skill in self.skills.values()})

    def test_stack_free_core_and_independent_optional_profiles(self) -> None:
        profiles = self.payloads["profiles"]
        self.assertEqual(["comments", "csharp-naming", "csharp-style"], profiles["core"])
        for name in profiles["core"]:
            self.assertEqual("none", self.skills[name]["metadata"]["requires"])
        for name in ("http-api", "persistence", "multitenancy", "microservice-boundaries", "integration-testing", "e2e-scenarios", "stack", "dotnet-stack"):
            self.assertNotIn(name, profiles["core"])
            self.assertNotEqual("none", self.skills[name]["metadata"]["requires"])
        assigned = [name for names in profiles.values() for name in names]
        self.assertEqual(len(assigned), len(set(assigned)))
        self.assertEqual(set(self.skills), set(assigned))
        self.assertIn("[dotnet:stack](../stack/SKILL.md)", self.skills["dotnet-stack"]["body"])

    def test_consumption_profiles_do_not_imply_unselected_stacks(self) -> None:
        profiles = self.payloads["profiles"]
        self.assertEqual({"http-api"}, set(profiles["aspnet"]))
        self.assertEqual({"persistence", "seeding"}, set(profiles["ef-core"]))
        self.assertEqual({"multitenancy"}, set(profiles["multitenancy"]))
        self.assertEqual({"microservice-boundaries", "proto"}, set(profiles["distributed-services"]))

        aspnet_requires = self.skills["http-api"]["metadata"]["requires"]
        self.assertIn("aspnet-core", aspnet_requires)
        self.assertNotIn("ef-core", aspnet_requires)

        for name in profiles["ef-core"]:
            requires = self.skills[name]["metadata"]["requires"]
            self.assertIn("ef-core", requires)
            self.assertNotIn("aspnet-core", requires)
            self.assertNotIn("multitenancy", requires)

        for name in profiles["distributed-services"]:
            requires = self.skills[name]["metadata"]["requires"]
            self.assertNotIn("ef-core", requires)
            self.assertNotIn("aspnet-core", requires)

    def test_generated_adapters_reference_canonical_and_package_is_self_contained(self) -> None:
        for name, skill in self.skills.items():
            source = ROOT / skill["relative"]
            package = ROOT / "plugins/dotnet/skills" / name / "SKILL.md"
            self.assertEqual(source.read_bytes(), package.read_bytes())
            for adapter_root in (".codex/skills", ".claude/skills"):
                adapter = (ROOT / adapter_root / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("canonical shared definition", adapter)
                self.assertNotEqual(source.read_text(encoding="utf-8"), adapter)

    def test_local_skill_references_resolve_and_product_owner_is_absent(self) -> None:
        identifiers = re.compile(r"(?<![-/\w])(dotnet|engineering):(?!:)([a-z][a-z0-9-]+)")
        offenders = []
        for name, skill in self.skills.items():
            body = skill["body"]
            self.assertNotIn("concertable", body.lower())
            self.assertNotIn("standards/", body.lower())
            for namespace, target in identifiers.findall(body):
                if namespace == "dotnet" and target not in self.skills:
                    offenders.append(f"{name}: {namespace}:{target}")
        self.assertEqual([], offenders)

    def test_host_manifests_reject_drift_and_cache_pinning(self) -> None:
        codex = json.loads((ROOT / ".agents/plugins/manifests/codex/dotnet.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".agents/plugins/manifests/claude/dotnet.json").read_text(encoding="utf-8"))
        codex_marketplace = json.loads((ROOT / ".agents/plugins/manifests/codex/marketplace.json").read_text(encoding="utf-8"))
        claude_marketplace = json.loads((ROOT / ".agents/plugins/manifests/claude/marketplace.json").read_text(encoding="utf-8"))
        sync_generated.validate_host_metadata(codex, claude, codex_marketplace, claude_marketplace)

        changed = dict(claude)
        changed["description"] = "drifted"
        with self.assertRaisesRegex(ValueError, "disagree on description"):
            sync_generated.validate_host_metadata(codex, changed, codex_marketplace, claude_marketplace)
        changed = dict(claude)
        changed["version"] = "1.1.0"
        with self.assertRaisesRegex(ValueError, "omit version"):
            sync_generated.validate_host_metadata(codex, changed, codex_marketplace, claude_marketplace)
        changed_codex, changed_claude = dict(codex), dict(claude)
        changed_codex["name"] = changed_claude["name"] = "other"
        with self.assertRaisesRegex(ValueError, "dotnet identity"):
            sync_generated.validate_host_metadata(changed_codex, changed_claude, codex_marketplace, claude_marketplace)
        changed_codex, changed_claude = dict(codex), dict(claude)
        changed_codex["skills"] = changed_claude["skills"] = "./missing/"
        with self.assertRaisesRegex(ValueError, "packaged skills path"):
            sync_generated.validate_host_metadata(changed_codex, changed_claude, codex_marketplace, claude_marketplace)
        changed = dict(claude)
        changed["version"] = None
        with self.assertRaisesRegex(ValueError, "omit version"):
            sync_generated.validate_host_metadata(codex, changed, codex_marketplace, claude_marketplace)

    def test_canonical_definitions_have_no_embedded_bom(self) -> None:
        for skill in self.skills.values():
            self.assertNotIn("\ufeff", skill["body"])

    def test_generated_selection_matches_metadata(self) -> None:
        selection = json.loads((ROOT / "plugins/dotnet/selection.json").read_text(encoding="utf-8"))
        self.assertEqual(self.payloads["profiles"], selection["profiles"])
        by_name = {item["name"]: item for item in selection["skills"]}
        self.assertEqual(set(self.skills), set(by_name))
        for name, skill in self.skills.items():
            self.assertEqual(skill["metadata"]["profile"], by_name[name]["profile"])


if __name__ == "__main__":
    unittest.main()
