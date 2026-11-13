# Python standards baseline

Existing violations at `f7bbed2ac8eea532aa66356a9808d02e66439859` are baselined by exact authored file and rule. New files receive all enabled checks. Remove an exception when repairing its source. The tool configuration owns enforcement; this document records the rollout evidence and rationale.

## Ruff

Reason: preserve existing implementations during the standards rollout. Each row records the existing count and a representative required repair. No wildcard path or whole-rule ignores were added.

| File | Rule | Existing count | Required repair |
| --- | --- | ---: | --- |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `ANN401` | 5 | Dynamically typed expressions (typing.Any) are disallowed in `read_json` |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `C401` | 1 | Unnecessary generator (rewrite as a set comprehension) |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `C405` | 1 | Unnecessary tuple literal (rewrite as a set literal) |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `C420` | 1 | Unnecessary dict comprehension for iterable; use `dict.fromkeys` instead |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `E501` | 83 | Line too long (90 > 88) |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `RUF059` | 1 | Unpacked variable `directory` is never used |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `UP006` | 55 | Use `dict` instead of `Dict` for type annotation |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `UP035` | 4 | Import from `collections.abc` instead: `Callable`, `Iterable`, `Mapping`, `Sequence` |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `UP045` | 8 | Use `X \| None` for type annotations |
| `.agents/dotnet/utility/scaffold/scripts/verify.py` | `E501` | 40 | Line too long (97 > 88) |
| `.agents/dotnet/utility/scaffold/scripts/verify.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/dotnet/utility/scaffold/scripts/verify.py` | `UP012` | 1 | Unnecessary UTF-8 `encoding` argument to `encode` |
| `.agents/dotnet/utility/scaffold/scripts/verify.py` | `UP035` | 1 | Import from `collections.abc` instead: `Sequence` |
| `.agents/dotnet/utility/scaffold/snippets/gen_snippets.py` | `E501` | 7 | Line too long (105 > 88) |
| `.agents/dotnet/utility/scaffold/snippets/gen_snippets.py` | `TID251` | 1 | `sys.path` is banned: Install the declared dependency; do not modify the import search path. |
| `.agents/dotnet/utility/scaffold/snippets/manifest.py` | `A002` | 1 | Function argument `id` is shadowing a Python builtin |
| `.agents/dotnet/utility/scaffold/snippets/manifest.py` | `E501` | 167 | Line too long (90 > 88) |
| `.agents/dotnet/utility/scaffold/snippets/manifest.py` | `UP045` | 2 | Use `X \| None` for type annotations |
| `.agents/tests/test_scaffold.py` | `C420` | 1 | Unnecessary dict comprehension for iterable; use `dict.fromkeys` instead |
| `.agents/tests/test_scaffold.py` | `E501` | 169 | Line too long (89 > 88) |
| `.agents/tests/test_scaffold.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_scaffold.py` | `ICN001` | 1 | `xml.etree.ElementTree` should be imported as `ET` |
| `.agents/tests/test_scaffold.py` | `N818` | 1 | Exception name `StopVerification` should be named with an Error suffix |
| `.agents/tests/test_scaffold.py` | `PT009` | 222 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_scaffold.py` | `SIM117` | 4 | Use a single `with` statement with multiple contexts instead of nested `with` statements |
| `.agents/tests/test_scaffold.py` | `TID251` | 3 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_snippets.py` | `E501` | 20 | Line too long (92 > 88) |
| `.agents/tests/test_snippets.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_snippets.py` | `ICN001` | 1 | `xml.etree.ElementTree` should be imported as `ET` |
| `.agents/tests/test_snippets.py` | `PT009` | 23 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_snippets.py` | `TID251` | 3 | `sys.path` is banned: Install the declared dependency; do not modify the import search path. |
| `.agents/tests/test_source_layout.py` | `E501` | 9 | Line too long (91 > 88) |
| `.agents/tests/test_source_layout.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_source_layout.py` | `PT009` | 9 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_source_layout.py` | `TID251` | 2 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |

## Ruff formatter

Exact existing files requiring formatting are excluded from the formatter during this rollout. Regenerate payloads after formatting authored source and then remove its exception. New files are checked.

- `.agents/dotnet/utility/scaffold/scripts/scaffold.py`
- `.agents/dotnet/utility/scaffold/scripts/verify.py`
- `.agents/dotnet/utility/scaffold/snippets/gen_snippets.py`
- `.agents/dotnet/utility/scaffold/snippets/manifest.py`
- `.agents/tests/test_scaffold.py`
- `.agents/tests/test_snippets.py`
- `.agents/tests/test_source_layout.py`

## Mypy

Existing typing debt is baselined by exact module and diagnostic code, with its source file and count below. Add the missing annotations or fix the indicated type mismatch, then remove the corresponding module/code override. No wildcard modules or whole-module ignore was added.

| File | Module | Rule | Existing count | Required repair |
| --- | --- | --- | ---: | --- |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `scaffold` | `no-any-return` | 1 | Returning Any from function declared to return "Path \| None" |
| `.agents/dotnet/utility/scaffold/scripts/scaffold.py` | `scaffold` | `type-arg` | 2 | Missing type arguments for generic type "set" |
| `.agents/dotnet/utility/scaffold/scripts/verify.py` | `verify` | `type-arg` | 1 | Missing type arguments for generic type "CompletedProcess" |
| `.agents/dotnet/utility/scaffold/snippets/gen_snippets.py` | `gen_snippets` | `no-any-return` | 1 | Returning Any from function declared to return "str" |
| `.agents/tests/test_scaffold.py` | `test_scaffold` | `no-untyped-call` | 2 | Call to untyped function (unknown) in typed context |
| `.agents/tests/test_snippets.py` | `test_snippets` | `no-untyped-def` | 2 | Function is missing a return type annotation |
| `.agents/tests/test_source_layout.py` | `test_source_layout` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/tests/test_source_layout.py` | `test_source_layout` | `attr-defined` | 9 | "type[CoreProfilePinTests]" has no attribute "skills" |
| `.agents/tests/test_source_layout.py` | `test_source_layout` | `no-untyped-def` | 1 | Function is missing a return type annotation |

## Custom checker

Reason: preserve exact pre-existing custom-checker findings during the standards rollout. Each entry maps to one authored path and rule; repair the stated design issue and remove its exception. No generated or vendored path is included.

| File | Rule | Existing count | Required repair |
| --- | --- | ---: | --- |
| .agents/dotnet/utility/scaffold/scripts/scaffold.py | PY016 | 1 | Inject process state or confine the read to an entry-point main. |
| .agents/dotnet/utility/scaffold/scripts/verify.py | PY016 | 2 | Inject process state or confine the read to an entry-point main. |
| .agents/tests/test_scaffold.py | PY016 | 11 | Inject process state or confine the read to an entry-point main. |
| .agents/tests/test_snippets.py | PY016 | 1 | Inject process state or confine the read to an entry-point main. |
