#!/usr/bin/env python3
"""Generate .NET consumer skill-route tables and the registry of routed repositories."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CS_PATH = r"(?i:\.cs$)"
COLLABORATOR_FIELD_DENY = {
    "pattern": (
        r"\bprivate\s+(?:static\s+)?readonly\s+I"
        r"(?!(?:ReadOnly|Async)?(?:Enumerable|Collection|List|Set|Dictionary)\b|(?:Equality)?Comparer\b)"
        r"(?P<subject>[A-Z][A-Za-z0-9]*)(?:<[^;=()]*>)?\s+"
        r"(?i:(?!\w*(?P=subject)\s*[;=])\w+)\s*[;=]"
    ),
    "reason": "A field holding a collaborator is named for that collaborator's subject and role without the `I`: "
    "`private readonly IUserService userService;` (dotnet:naming).",
}
# Textually distinct from CS_PATH: skill_router keys its per-session seen-state on the path string,
# so a row reusing the floor's exact pattern is never enforced after the floor first fires.
LOGGING_CS_PATH = r"(?i:\.(cs)$)"
ERRORS_CS_PATH = r"(?i:(\.cs)$)"
BUILD_PATH = r"(?i:(^|/)([^/]+\.(csproj|sln|slnx)|Directory\.(Build|Packages)\.props|Directory\.Build\.targets|global\.json|nuget\.config))$"
TEST_PATH = r"(?i:(^|/)tests?/|\.tests[./]|\.feature$)"
TEST_PROJECT_CONTENT = r"(?i:<istestproject>\s*true|microsoft\.net\.test\.sdk)"
UNIT_TEST_PATH = r"(?i:(tests\.unit|unittests)[./])"
INTEGRATION_TEST_PATH = r"(?i:(tests\.integration|integrationtests)[./])"
E2E_TEST_PATH = r"(?i:(tests\.e2e|e2etests)[./]|\.feature$)"
DOMAIN_LAYER_PATH = r"(?i:\.domain/.*\.cs$)"
MODULE_LAYER_PATH = r"(?i:\.(application|infrastructure)/.*\.cs$)"
HTTP_EDGE_PATH = r"(?i:(controller|endpoint)s?\.cs$)"
DTO_PATH = r"(?i:\.(application|contracts)/.*\.cs$)|(?-i:[a-z0-9](Dto|DTO|Summary|Summaries|Page)s?\.cs$)"
REQUEST_RESPONSE_PATH = r"(?i:(request|response)s?\.cs$)"
REPOSITORY_PATH = r"(?i:(repository|repositories|stores?|projections?)\.cs$)"
PERSISTENCE_PATH = r"(?i:dbcontext\.cs$|(^|/)(migrations|persistence)/.*\.cs$)"
COMPOSITION_PATH = r"(?i:(^|/)program\.cs$|(servicecollection|dependencyinjection)[^/]*\.cs$)"
LOG_FILE_PATH = r"(?i:(^|/)log\.cs$)"
LOGGING_CONTENT = r"(?i:\bilogger|loggermessage)"
ERRORS_CONTENT = r"(?i:\bresult<|\bunitresult<|\boption<|\bierror\b)"
VALIDATOR_PATH = r"(?i:validators?\.cs$)"
MAPPER_PATH = r"(?i:mappers?\.cs$)"
SEEDING_PATH = r"(?i:seeders?\.cs$|(^|/)seeding/.*\.cs$)"
PROTO_PATH = r"(?i:\.proto$)"
DOMAIN_EVENTS_CS_PATH = r"(?i:\.c(s)$)"
DOMAIN_EVENTS_CONTENT = r"(?i:\bidomainevent\b|\bieventraiser\b|domaineventhandler|integrationeventhandler)"
PUBLISHER_CONSUMER_PATH = r"(?i:(publisher|consumer|handler)s?\.cs$)"
MESSAGING_PATH = r"(?i:(publisher|processor)s?\.cs$)"
MESSAGING_CS_PATH = r"(?i:\.c[s]$)"
MESSAGING_CONTENT = r"(?i:\biintegrationeventpublisher\b|\bservicebusprocessor\b)"
COMMENTS_CS_PATH = r"(?i:\.[c]s$)"
COMMENTS_CONTENT = r"(?m:^[ \t]*//)"
EXTENSIONS_PATH = r"(?i:extensions?\.cs$)"
DEPENDENCY_INJECTION_CS_PATH = r"(?i:(\.c)s$)"
DEPENDENCY_INJECTION_CONTENT = r"(?i:\biservicecollection\b|\.add(scoped|singleton|transient)\b)"
UNIT_OF_WORK_PATH = r"(?i:unitofworks?\.cs$)"
UNIT_OF_WORK_CONTENT = r"(?i:\biunitofwork\b)"
SPECIFICATION_PATH = r"(?i:specifications?\.cs$)"
QUERY_BUILDER_PATH = r"(?i:querybuilders?\.cs$)"
EF_PERSISTENCE_CONTENT = r"(?i:\b(dbcontext|dbset|savechangesasync|savechangesinterceptor)\b|microsoft\.entityframeworkcore|\.(tolistasync|singleordefaultasync|asnotracking)\()"
EF_EVENT_DISPATCH_CONTENT = r"(?i:\bsavechangesinterceptor\b|\b(savingchanges|savedchanges)(async)?\b)"
DDD_CONTENT = r"(?i:\b(iaggregateroot|aggregateroot|valueobject)\b|\bclass\s+\w+(?:<[^<>]{0,100}>)?(?:\([^()]{0,300}\))?\s*:\s*(?:[\w.]+(?:<[^<>]{0,100}>)?\s*,\s*){0,5}(?:i|base|auditable)?entity<)"
VALUES_CONTENT = r"(?i:\brecord\s+struct\b|\bbool\s+try[a-z]\w*\s*\((?:[^()]|\([^()]{0,200}\)){0,400}?\bout\s)"
CARRIERS_CONTENT = r"(?i:\b(result|unitresult|option)<|\.(trygeterror|maperror|valueor|tooption|orfailure|bindasync)\()"
RESULTS_CONTENT = r"(?i:\bierror\b|errordefinition\.)"
TERMINALS_CONTENT = r"(?i:\.(tookorproblem|tonocontentorproblem|tocreatedorproblem|tocreatedatactionorproblem|tocreatedatrouteorproblem|toactionresult|toresults|tookornotfound|tookornocontent|tookor)\()"
KEYED_STRATEGIES_CONTENT = r"(?i:\[fromkeyedservices|\.(try)?addkeyed(scoped|singleton|transient)\b|\bget(required)?keyedservice\b|\bikeyedserviceprovider\b|\.require(all|exactly)<)"
KEYED_UNIONS_CONTENT = r"(?i:\.case<[\w.]+>\(|\bkeyedunion\w*|unionfactory\b)"
MICROSERVICE_CONTENT = r"(?i:\.add(grpcclient|servicediscovery|refitclient|grpc)\b|\.mapgrpcservice<|\bgrpcchannel\.foraddress\b)"
MULTITENANCY_CONTENT = r"(?i:\b(itenantcontext|imultitenantcontextaccessor|icurrenttenant)\b|\.hasqueryfilter\([^)]{0,300}?tenant|\.ignorequeryfilters\()"
PACKAGES_PATH = r"(?i:(^|/)directory\.packages\.props$)"
SELECTED_STACK_CONTENT = r"(?i:meziantou\.analyzer|\breunion\b)"
SCAFFOLD_PATH = r"(?i:(^|/)\.scaffold\.json$)"
SINGLE_SERVICE_CONTENT = r'"architecture"\s*:\s*"single-service"'
SOLUTION_PATH = r"(?i:\.slnx?$)"
SINGLE_SERVICE_SOLUTION_CONTENT = r"(?is:\A(?!.*[\\/]modules[\\/])(?!(?:.*?\.application[\\/]){2}).*\.application[\\/])"


def cs_content_path(skill: str) -> str:
    return rf"(?i:\.cs$)(?#{skill})"


KINDS = ("dotnet-service", "efcore-service")
DESIGN_TIME = {
    "dotnet:explanation": "Governs how C# is quoted in a chat explanation; no file write reveals it.",
}
REGISTRY = {
    "infonetica/cris-authz": "dotnet-service",
}
IDENTITY = re.compile(r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*$")


def routes(kind: str) -> dict:
    if kind not in KINDS:
        raise ValueError(f"unknown kind: {kind}")
    rows = [
        {"path": r"^plans/", "skills": ["engineering:plans"]},
        {"path": r"^reviews/", "skills": ["engineering:review-lifecycle"]},
        {"path": r"(^|/)(AGENTS|CLAUDE)\.md$", "skills": ["engineering:docs"]},
        {"path": CS_PATH, "skills": ["dotnet:style", "dotnet:naming", "dotnet:fields"], "deny": [COLLABORATOR_FIELD_DENY]},
        {"path": COMMENTS_CS_PATH, "content_requires": COMMENTS_CONTENT, "skills": ["dotnet:comments"]},
        {"path": BUILD_PATH, "skills": ["dotnet:build", "dotnet:libraries", "dotnet:structure"]},
        {"path": TEST_PATH, "skills": ["dotnet:testing"]},
        {"path": r"(?i:\.csproj$)", "content_requires": TEST_PROJECT_CONTENT, "skills": ["dotnet:testing"]},
        {"path": UNIT_TEST_PATH, "skills": ["dotnet:testing-unit"]},
        {"path": INTEGRATION_TEST_PATH, "skills": ["dotnet:testing-integration"]},
        {"path": E2E_TEST_PATH, "skills": ["dotnet:testing-e2e"]},
        {"path": DOMAIN_LAYER_PATH, "skills": ["dotnet:domain-design"]},
        {"path": MODULE_LAYER_PATH, "skills": ["dotnet:structure-modules"]},
        {"path": HTTP_EDGE_PATH, "skills": ["dotnet:http-api"]},
        {"path": DTO_PATH, "skills": ["dotnet:dtos"]},
        {"path": REQUEST_RESPONSE_PATH, "skills": ["dotnet:http-api"]},
        {"path": REPOSITORY_PATH, "skills": ["dotnet:repositories"]},
        {"path": PERSISTENCE_PATH, "skills": ["efcore:persistence"]},
        {"path": cs_content_path("efcore-persistence"), "content_requires": EF_PERSISTENCE_CONTENT, "skills": ["efcore:persistence"]},
        {"path": SPECIFICATION_PATH, "skills": ["efcore:specification"]},
        {"path": QUERY_BUILDER_PATH, "skills": ["efcore:query-building"]},
        {"path": cs_content_path("efcore-event-dispatch"), "content_requires": EF_EVENT_DISPATCH_CONTENT, "skills": ["efcore:event-dispatch"]},
        {"path": COMPOSITION_PATH, "skills": ["dotnet:dependency-injection"]},
        {"path": LOG_FILE_PATH, "skills": ["dotnet:logging"]},
        {"path": LOGGING_CS_PATH, "content_requires": LOGGING_CONTENT, "skills": ["dotnet:logging"]},
        {"path": ERRORS_CS_PATH, "content_requires": ERRORS_CONTENT, "skills": ["dotnet:errors"]},
        {"path": VALIDATOR_PATH, "skills": ["dotnet:validation"]},
        {"path": MAPPER_PATH, "skills": ["dotnet:mapping"]},
        {"path": EXTENSIONS_PATH, "skills": ["dotnet:mapping"]},
        {"path": SEEDING_PATH, "skills": ["dotnet:seeding"]},
        {"path": PROTO_PATH, "skills": ["dotnet:proto"]},
        {"path": DOMAIN_EVENTS_CS_PATH, "content_requires": DOMAIN_EVENTS_CONTENT, "skills": ["dotnet:domain-events"]},
        {"path": PUBLISHER_CONSUMER_PATH, "skills": ["dotnet:domain-events"]},
        {"path": MESSAGING_PATH, "skills": ["dotnet:messaging"]},
        {"path": MESSAGING_CS_PATH, "content_requires": MESSAGING_CONTENT, "skills": ["dotnet:messaging"]},
        {"path": DEPENDENCY_INJECTION_CS_PATH, "content_requires": DEPENDENCY_INJECTION_CONTENT, "skills": ["dotnet:dependency-injection"]},
        {"path": UNIT_OF_WORK_PATH, "skills": ["dotnet:unit-of-work"]},
        {"path": cs_content_path("unit-of-work"), "content_requires": UNIT_OF_WORK_CONTENT, "skills": ["dotnet:unit-of-work"]},
        {"path": cs_content_path("domain-ddd"), "content_requires": DDD_CONTENT, "skills": ["dotnet:domain-ddd"]},
        {"path": cs_content_path("domain-values"), "content_requires": VALUES_CONTENT, "skills": ["dotnet:domain-values"]},
        {"path": cs_content_path("errors-carriers"), "content_requires": CARRIERS_CONTENT, "skills": ["dotnet:errors-carriers"]},
        {"path": cs_content_path("errors-results"), "content_requires": RESULTS_CONTENT, "skills": ["dotnet:errors-results"]},
        {"path": cs_content_path("errors-terminals"), "content_requires": TERMINALS_CONTENT, "skills": ["dotnet:errors-terminals"]},
        {"path": cs_content_path("keyed-strategies"), "content_requires": KEYED_STRATEGIES_CONTENT, "skills": ["dotnet:keyed-strategies"]},
        {"path": cs_content_path("keyed-unions"), "content_requires": KEYED_UNIONS_CONTENT, "skills": ["dotnet:keyed-unions"]},
        {"path": cs_content_path("microservice-boundaries"), "content_requires": MICROSERVICE_CONTENT, "skills": ["dotnet:microservice-boundaries"]},
        {"path": cs_content_path("multitenancy"), "content_requires": MULTITENANCY_CONTENT, "skills": ["efcore:multitenancy"]},
        {"path": PACKAGES_PATH, "content_requires": SELECTED_STACK_CONTENT, "skills": ["dotnet:libraries-selected"]},
        {"path": SCAFFOLD_PATH, "content_requires": SINGLE_SERVICE_CONTENT, "skills": ["dotnet:structure-single-service"]},
        {"path": SOLUTION_PATH, "content_requires": SINGLE_SERVICE_SOLUTION_CONTENT, "skills": ["dotnet:structure-single-service"]},
    ]
    if kind == "dotnet-service":
        rows = [{**row, "skills": [skill for skill in row["skills"] if not skill.startswith("efcore:")]} for row in rows]
        rows = [row for row in rows if row["skills"]]
    return {
        "_comment": [
            "Generated by tj-agents/dotnet dotnet:skill-routes gen_skill_routes.py; do not edit by hand.",
            "Architecture-keyed rows: every matching route fires, and the .cs floor always applies.",
        ],
        "kind": kind,
        "layers": ["engineering", "dotnet", *(["efcore"] if kind == "efcore-service" else [])],
        "routes": rows,
    }


TIER_LAYERS = {"dotnet": ("dotnet-service", "dotnet:"), "efcore": ("efcore-service", "efcore:")}


def tier_routes(tier: str) -> list[dict]:
    kind, prefix = TIER_LAYERS[tier]
    rows = []
    for row in routes(kind)["routes"]:
        skills = [skill for skill in row["skills"] if skill.startswith(prefix)]
        if skills:
            rows.append({**row, "skills": skills})
    return rows


def tier_files(root: Path) -> dict[Path, str]:
    files = {}
    for tier in TIER_LAYERS:
        path = root / ".agents" / "tiers" / f"{tier}.json"
        declaration = json.loads(path.read_text(encoding="utf-8"))
        declaration["routes"] = tier_routes(tier)
        files[path] = rendered(declaration)
    return files


def registry_document() -> dict:
    for identity, kind in REGISTRY.items():
        if not IDENTITY.match(identity):
            raise ValueError(f"registry identity must be a lowercase owner/name: {identity}")
        if kind not in KINDS:
            raise ValueError(f"{identity} is registered for an unknown kind: {kind}")
    return {
        "_comment": [
            "Generated by tj-agents/dotnet dotnet:skill-routes gen_skill_routes.py; do not edit by hand.",
            "skill_router.py reads this only when shipped beside it as routes/registry.json; a repo's own .agents/skill-routes.json always wins.",
        ],
        "repos": dict(sorted(REGISTRY.items())),
    }


def rendered(document: dict) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def emitted_files(directory: Path) -> dict[Path, str]:
    files = {directory / "registry.json": rendered(registry_document())}
    for kind in sorted(set(REGISTRY.values())):
        files[directory / f"{kind}.json"] = rendered(routes(kind))
    return files


def skills_for(kind: str, path: str, content: str = "") -> set[str]:
    matched: set[str] = set()
    for route in routes(kind)["routes"]:
        if not re.search(route["path"], path):
            continue
        needle = route.get("content_requires")
        if needle and not re.search(needle, content):
            continue
        matched.update(route.get("skills") or [])
    return matched


def write_or_check(files: dict[Path, str], check: bool) -> int:
    stale = False
    for target, expected in files.items():
        if check:
            try:
                actual = target.read_text(encoding="utf-8")
            except OSError:
                actual = None
            if actual != expected:
                print(f"STALE: {target}")
                stale = True
            else:
                print(f"current: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected, encoding="utf-8", newline="\n")
            print(f"generated: {target}")
    return 1 if stale else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=KINDS)
    parser.add_argument("--into", type=Path)
    parser.add_argument("--emit-registry", type=Path)
    parser.add_argument("--emit-tiers", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit_registry and (args.kind or args.into):
        parser.error("--emit-registry cannot be combined with --kind/--into")
    if args.emit_tiers and (args.kind or args.into or args.emit_registry):
        parser.error("--emit-tiers cannot be combined with --kind/--into/--emit-registry")
    if args.emit_registry:
        return write_or_check(emitted_files(args.emit_registry.resolve()), args.check)
    if args.emit_tiers:
        return write_or_check(tier_files(args.emit_tiers.resolve()), args.check)
    if not args.kind or not args.into:
        parser.error("--kind and --into are required without --emit-registry")
    target = args.into.resolve() / ".agents" / "skill-routes.json"
    return write_or_check({target: rendered(routes(args.kind))}, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
