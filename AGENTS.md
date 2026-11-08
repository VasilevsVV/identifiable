# AGENTS.md

Operational guide for AI agents working on this repository. Read it at the start of every session. Where it conflicts with general practice, this file wins. If a design decision can't be settled from the code or this file, ask the user.

---

## Project

- **Name**: `identifiable` (version 0.1.0, early WIP on the `prototype` branch)
- **What it is**: a mixin for Python 3.10+. Subclasses get unique per-object IDs (optionally auto-generated) and a class-level registry of instances.
- **Goal**: a reliable, testable mixin that doesn't surprise subclasses or break inheritance chains.

## How the code works

Everything lives in `identifiable/core.py`.

- `Identifiable(Generic[_KEY_T])` is the mixin. `_KEY_T` is the ID type (must be `Hashable`).
- Class flags:
  - `__enable_auto_id__: bool = True`: when True, `__new__` assigns an ID. Adding the mixin needs no settings.
  - `__id_generation_strategy__: 'increment' | 'uuid' = 'increment'` (`'uuid'` is reserved and not implemented).
  - `__class_objects_map__: dict` is the registry.
- `__init_subclass__` only acts on **direct** subclasses (`Identifiable in cls.__bases__`):
  - It creates a fresh `__class_objects_map__`, or checks that a user-provided one is a `dict`.
  - If the subclass defines a concrete `uid()`, auto-ID is turned off for it. If auto-ID is set to False without a `uid()`, it raises `TypeError`.
  - Deeper subclasses skip all of this and **share their parent's registry**.
- `__new__` runs when auto-ID is on: it calls `__gen_unique_id()` and attaches a `uid` lambda to the instance.
- `__register_unique_id`, `__gen_unique_id` and `get_object` are **stubs** (`...`).
- Names that start with two underscores and don't end with two (for example `__gen_unique_id` and `__unique_id`) are name-mangled to `_Identifiable__*`. Subclasses can't override them by their plain names.

## Danger zone

Changing `__new__`, `__init_subclass__` or the registry affects every subclass: registration, auto-ID and lookups all depend on them.

- Ask the user before changing their signatures or behaviour, and use plan mode.
- Always access the registry as `cls.__class_objects_map__`, never through `Identifiable` directly.
- Write a test for the current subclass behaviour first, then change it.

## Plans and step-by-step execution

**Plan format**
- Split every plan into small steps. Each step is one reviewable change: one concern, a few files, a small diff.
- Every plan includes a steps table:

  | # | Step | Status | Commit |
  |---|------|--------|--------|
  | 1 | Short description | ⬜ pending | — |

  Statuses are ⬜ pending, 🔄 in progress and ✅ done. Commit is the short hash, filled in once the step is committed.

**Execution loop**: run this for each step.
1. Implement **one** step only.
2. Update its status in the table, report what changed, then **stop and wait** for the developer's "go".
3. On "go", commit the step with a short conventional-commit message, record the hash in the table, then start the next step.
4. Any other reply (feedback or a question) means revise the current step. Don't commit and don't continue.

**Tests**: if the project has tests, offer to run them every couple of steps, or once at the end for a short plan. Before declaring the plan finished, run the full Definition of done.

**Autonomous mode**: work through all steps without stopping **only** when the developer explicitly says to. Use the same loop and treat each step as having received "go": still one commit per step, and the table is still updated. Never assume autonomous mode.

## Tooling

| Purpose | Tool | Config |
|---|---|---|
| Python | >= 3.10.12 (no 3.11+ features unless asked) | `pyproject.toml` |
| Build | `setuptools`, `python -m build` | `pyproject.toml`, `makefile` |
| Lint / format | `ruff` | `ruff.toml` |
| Types | `pyright` (standard mode) | `pyproject.toml [tool.pyright]` |
| Tests | `pytest` | `pyproject.toml [tool.pytest.ini_options]` |
| Versioning | `bump2version` | `.bumpversion.cfg` |
| Publishing | `twine` | `makefile` |

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

**Definition of done**: run this before reporting work as finished, and report any failures.

```bash
ruff check . && ruff format --check . && pyright && pytest
```

Build and publish with `make build`, `make test-publish` or `make publish`, and only when the user asks.

## Structure

```
identifiable/
  __init__.py      # public exports: Identifiable
  core.py          # Identifiable mixin
test/              # unit tests: test_*.py or *_test.py
pyproject.toml  ruff.toml  makefile  .bumpversion.cfg
```

## Vocabulary

Use these terms in design discussions:

- **Module**: anything with an interface and an implementation (a class, a method, a package).
- **Interface**: everything a caller must know: signatures, invariants, error modes, ordering, configuration.
- **Seam**: a place where behaviour can be changed without editing that place (Feathers). A module's interface sits at its seam.
- **Adapter**: a concrete thing that satisfies an interface at a seam.
- **Depth**: behaviour per unit of interface. A deep module has a small interface over a lot of behaviour. A shallow one is about as complex as what it wraps.
- **Leverage / Locality**: what depth gives callers (more capability for less learning) and maintainers (changes and bugs stay in one place).

## Working loops

**TDD (red → green → refactor)**
- One vertical slice per cycle: one seam, one failing test, the minimal code to pass it.
- Test behaviour through public interfaces, not internals. Tests coupled to the implementation break when you refactor.
- Don't write all the tests up front (horizontal slicing).
- Refactor at review, not mid-cycle.

**Debugging**
- Build a feedback loop before forming any hypothesis: a deterministic, fast test or command that reproduces the exact symptom.
- Shrink the repro to the minimum, then keep it as a regression test.
- Tag debug output and remove it before finishing.

**Prototyping**
- Before building, state the question the prototype should answer in one visible paragraph.
- Keep it throwaway: no tests, minimal error handling, in-memory state.
- Once it answers the question, record the decision, put it into real code, and delete the prototype. Prototype code never merges into `main`.

## Design rules

- Prefer deep modules. Use the deletion test: if deleting a module would spread complexity across its callers, it earns its keep. If the complexity would vanish, flatten it.
- Add behaviour *behind* the `Identifiable` interface, not beside it.
- Don't add speculative generality. Abstractions, parameters and hooks need a real current use. Don't introduce a port unless at least two adapters justify it.
- Before writing tests, agree with the user on which public seams they cover.

## Conventions

- **Style**: single quotes, 4-space indent, and the `ruff.toml` rules.
- **Types**: annotate functions, return types and non-obvious variables. Import `Self` and other newer typing features from `typing_extensions`.
- **Package**: core logic stays in `core.py`. Export only stable public names from `__init__.py`.
- **Dependencies**: runtime needs only `typing_extensions`. Ask before adding any other dependency.
- **Commits**: use conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`). Bump versions only in dedicated release PRs.

## Known issues

These are documented so they don't get rediscovered. Fix them only when the task calls for it.

- `__new__(cls)` takes no arguments, so a subclass whose `__init__` takes arguments fails to instantiate.
- `__register_unique_id`, `__gen_unique_id` and `get_object` are unimplemented. With auto-ID on, the generated ID is `None`.
- Indirect subclasses share their direct parent's registry. It's undecided whether this is intended.

## Session checklist

1. Read this file.
2. Identify the seams involved, and agree the test targets with the user before writing tests.
3. When debugging, build the feedback loop first. When prototyping, state the question first.
4. Ask before touching anything in the Danger zone.
5. For plans, follow the step-by-step execution rules: small steps, a status/commit table, one step at a time, wait for "go", commit after "go".
6. Run the Definition of done before reporting completion.
