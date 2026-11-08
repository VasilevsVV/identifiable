# AGENTS.md

Operational guide for AI agents working on this repository. Read it at the start of every session. Where it conflicts with general practice, this file wins. If a design decision can't be settled from the code, this file or `docs/adr/`, ask the user.

---

## Project

- **Name**: `identifiable` (version 0.1.0, early WIP)
- **What it is**: a mixin for Python 3.10+. It gives a family of classes one interface to make an ID for each object (`make_uid()`), register the object under it, reject duplicates and look objects up by ID.
- **Goal**: easy to add to existing classes: add `Identifiable` to the bases and implement `make_uid()`. It must stay reliable and testable, and must not surprise subclasses or break inheritance chains.
- **Scope**: user code owns creating objects, lazy creation and resolving ID references. The mixin only makes, registers and looks up IDs.
- **Docs**: `README.md` holds the purpose, use cases and public interface (including planned features). `GLOSSARY.md` holds the domain terms; use them when naming things in code, docs and commits. `docs/adr/` records design decisions; read it before changing registry sharing or lookup, or adding a metaclass.

## How the code works

Everything lives in `identifiable/core.py`.

- `Identifiable(Generic[_KEY_T])` is the mixin. `_KEY_T` is the ID type (must be `Hashable`). No metaclass (ADR 0002).
- `make_uid(cls, *args, **kwargs)` is an abstract **classmethod** that subclasses implement. It gets the constructor arguments and returns the new object's ID.
- `uid` is a read-only property that returns the stored ID (`_Identifiable__uid`).
- `__class_objects_map__: dict` is the registry, the only class setting.
- `__new__(cls, *args, **kwargs)`, in order:
  1. Raises `TypeError` if `make_uid` is still abstract.
  2. Calls `make_uid(*args, **kwargs)`.
  3. Raises `DuplicateUIDError` (a `ValueError`) if the ID is already registered. No object is created.
  4. Creates the object, stores the ID, registers it in `cls.__class_objects_map__`.
  `__init__` then runs as usual with the same arguments.
- `__init_subclass__` only acts on **direct** subclasses (`Identifiable in cls.__bases__`): it creates a fresh `__class_objects_map__`, or checks that a user-provided one is a `dict`. Deeper subclasses **share their parent's registry** on purpose: the direct subclass is the family base, and the whole family has one ID namespace (ADR 0001).
- `get_object(id) -> Self` looks `id` up in `cls.__class_objects_map__` and narrows to `cls` (ADR 0003). It raises `UnknownUIDError` if the ID isn't registered and `WrongClassUIDError` if its object isn't an instance of `cls`; both are `KeyError` subclasses whose message prints unquoted. On the family base it finds any family member.
- `find_object(id) -> Self | None` calls `get_object` and returns `None` in place of either error.
- There is no built-in ID generation. It may come back later as a separate class.
- Names that start with two underscores and don't end with two (for example `__uid`) are name-mangled to `_Identifiable__*`. Subclasses can't override them by their plain names.

## Danger zone

Changing `__new__`, `__init_subclass__` or the registry affects every subclass: registration, ID creation, duplicate checks and lookups all depend on them.

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
  __init__.py      # public exports: Identifiable and the three errors
  core.py          # Identifiable mixin, DuplicateUIDError, UnknownUIDError, WrongClassUIDError
test/              # unit tests: test_*.py or *_test.py
docs/adr/          # design decisions
GLOSSARY.md        # domain terms
pyproject.toml  ruff.toml  makefile  .bumpversion.cfg
```

## Vocabulary

Domain terms (ID, family, registry, ID reference, ...) live in `GLOSSARY.md`. Use these design terms in design discussions:

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

- An object is registered before `__init__` runs. If `__init__` raises, the registry still holds it and the lookups return the half-built object. `__new__` alone can't fix this (it returns before `__init__` runs); the planned fix wraps `__init__` in `__init_subclass__`.
- `copy.copy`, `copy.deepcopy` and `pickle` fail with `TypeError`: they call `cls.__new__(cls)` without arguments, so `make_uid()` gets none. A fix still needs a design (a copy would also be a duplicate).
- pyright doesn't flag a missing `make_uid()`; it's only a runtime `TypeError`. This follows from staying metaclass-free (ADR 0002).

## Session checklist

1. Read this file.
2. Identify the seams involved, and agree the test targets with the user before writing tests.
3. When debugging, build the feedback loop first. When prototyping, state the question first.
4. Ask before touching anything in the Danger zone.
5. For plans, follow the step-by-step execution rules: small steps, a status/commit table, one step at a time, wait for "go", commit after "go".
6. Run the Definition of done before reporting completion.
