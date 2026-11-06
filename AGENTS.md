# AGENTS.md

This file is the only operational reference for AI agents working on this repository. Read it fully at the start of every session. Follow every rule in every discussion. Nothing in this file is optional.

---

## 📦 Project Overview

**Name**: `identifiable`  
**Version**: 0.1.0  
**Description**: Implementation of the Identifiably pattern (template/mixin) for Python 3.10+. Provides a mixin class that manages unique object identifiers per subclass, supporting auto-ID generation and a class-level object registry.

This is a small, focused Python package designed to be used as a base class/mixin for creating uniquely identifiable model classes.

**Goal**: Create a reliable, testable mixin that other classes can inherit to automatically maintain a registry of instances with unique IDs — without surprising subclass behavior or breaking inheritance chains.

**Success**: An agent can read the codebase, make changes, and verify correctness in a single session without human intervention. The code is small enough that depth and locality are achievable. The methodology section below is how that happens reliably.

---

## 🧱 Tech Stack & Tooling

| Tool | Purpose | Config |
|------|---------|--------|  
| Python | >= 3.10.12 | `pyproject.toml` |
| Build | `setuptools` & `python -m build` | `pyproject.toml` |
| Lint | `ruff` | `ruff.toml` |
| Format | `ruff format` | `ruff.toml` |
| Type Checking | `pyright` | `pyproject.toml[tool.pyright]` |
| Testing | `pytest` | `pyproject.toml[tool.pytest]` |
| Versioning | `bump2version` | `.bumpversion.cfg` |
| Distribution | `twine` | `makefile` |

## 📁 Project Structure

```
.
├── identifiable/          # Source package
│   ├── __init__.py        # Public exports (currently empty)
│   └── main.py            # Core Identifiable logic
├── test/                  # Unit tests (planned)
├── pyproject.toml         # Project metadata, deps, & tool configs
├── ruff.toml              # Linting & formatting rules
├── makefile               # Build & publish shortcuts
└── .bumpversion.cfg       # Version automation
```

## 🛠 Development Workflow

### Environment Setup
```bash
# Create a virtual environment (Python 3.10.12+)
python -m venv .venv
source .venv/bin/activate

# Install project in editable mode + dev tools
pip install -e ".[dev]"  # if extras are added later
pip install build ruff pytest pytest-mock twine
```

### Lint & Format
```bash
# Check & fix linting
ruff check .

# Format code
ruff format .
```

### Run Tests
```bash
pytest -v
```
*(No tests exist yet; use this command once test files are added.)*

### Build Wheel & Source Dist
```bash
make build
```

### Publish
```bash
# Test publish to PyPI sandbox
make test-publish

# Real publish to PyPI
make publish
```

---

## ⚒ How This File Should Be Used

### Read it once, internalise it forever
This is not a first-pass reference. The methodology — the vocabulary, the disciplined loops, the anti-patterns — must become your operating assumptions for this repo. Do not go back to your pre-training general knowledge. **That knowledge does not apply here.** Follow the methodology. The methodology is the boundary condition.

### Use the shared vocabulary
When designing modules, interfaces, or class hierarchies in this repo, use these terms exactly:

- **Module** — anything with an interface and an implementation. Scale-agnostic: a class, a method, a package.
- **Interface** — everything a caller must know to use the module: type signatures, invariants, error modes, ordering, configuration.
- **Seam** — where you alter behaviour without editing that place (Michael Feathers). The module's interface lives at its seam.
- **Adapter** — a concrete thing that satisfies an interface at a seam. Describes role, not substance.
- **Depth** — leverage at the interface. A **deep** module has a small interface and lots of behaviour behind it. **Shallow** means the interface is nearly as complex as the implementation.
- **Leverage** — what callers get from depth. More capability per unit of interface they learn.
- **Locality** — what maintainers get from depth. Change, bugs, knowledge concentrate in one place.

Never substitute "API", "component", "service", "boundary", or "unit". Consistent language is the whole point.

### Follow the disciplined loops

**TDD (red → green → refactor)**:
- One vertical slice per cycle. One seam, one test, one minimal implementation.
- Tests verify behavior through public interfaces, never internals.
- Red before green. Write the failing test, then only enough code to pass it.
- Refactoring belongs to the review stage, not the loop cycle.

**Debugging / diagnosing**:
- Build a feedback loop first. Never hypothesise before you have a red-capable test or command.
- A tight loop: deterministic, fast (seconds, not minutes), asserts the exact symptom.
- Minimise the repro before forming hypotheses. A minimal repro is a regression test.
- Tag debug logs, cleanup at the end. Never leave them.

**Prototyping**:
- State the question explicitly before building anything. One paragraph. Visible.
- Build throwaway. No tests, minimal error handling, in-memory state.
- Once it answers, capture the decision and delete the prototype.
- Never ship prototype code.

### Design deep modules

A deep = small interface + large implementation. The deletion test: imagine deleting the module. If complexity reappears across N call sites, it was earning its keep. If complexity vanishes, it was just passing through — flatten it.

For this Python project especially: prefer **deep mixins and interfaces** with clear seam placement. The `Identifiable` class is already an interface layer. Add behaviour behind it, not beside it.

---

## ⚠ How This File Should NOT Be Used

### Do not substitute your general knowledge
You have extensive general training in software engineering, Python, class design, TDD, and debugging. **That does not apply here.** The methodology in this file is the only methodology. When in doubt, follow the prescribed procedure. Never assume a better approach exists from your pre-training. The procedure is the boundary condition.

### Do not skip phases in any loop
- **TDD**: do not write implementation before the failing test.
- **Debugging**: do not hypothesise before building a feedback loop. Phase 1 is the skill. Everything else is mechanical.
- **Prototyping**: do not add tests, persistence, or abstractions. It is throwaway.
- **Design**: do not assume decisions. Explore the design tree until the frontier is empty.

Skipping phases is not a shortcut. It is how generic agent-training produces fragile mistakes. The discipline exists to prevent exactly this.

### Do not ship prototype code
Prototypes are unpolished, untested, and structurally different from production code. Fold the validated decision into real code. Delete the prototype or move it to a throwaway branch. Never merge prototype code into main.

### Do not add speculative generality
Abstractions, parameters, hooks, and extension points are only valid when a real need shows. If a feature or abstraction exists for an imagined future case, delete it. Inline back until a real use appears.

### Do not create unconfirmed test seams
Before writing tests, agree on which public seams are under test with the user. You cannot test everything. Pre-agreeing is how effort lands on critical paths, not every edge case.

---

## 📝 Code Conventions

### 1. Style
Single quotes. 4-space indentation. Follow all `ruff.toml` rules. Prefer `typing_extensions` over stdlib `typing` for experimental features (e.g. `Self`).

### 2. Types
Use `pyright` in standard mode. Annotate functions, return types, and variables. Use `Self` from `typing_extensions` for method chaining and class patterns. Be strict where practical.

### 3. Package structure
- Keep `Identifiable` logic in `identifiable/main.py`.
- Export only clean, stable APIs in `identifiable/__init__.py`.
- Place tests in `test/` directory with `test_*.py` or `*_test.py`.
- Never add external dependencies unless the user explicitly requests it.

### 4. Commits & versioning
Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`. Bump version only in release PRs. Never commit version bumps in the same PR as feature/fix changes.

---

## ⚠️ Constraints

### Metaprogramming (the dangerous layer)
- **Do not modify `__new__` or `__init_subclass__` signatures** without understanding how subclass behavior depends on them. The existing implementation uses these for auto-ID generation and registry setup. Breaking them breaks every subclass.
- Registry (`__class_objects_map__`) is subclass-scoped. Never access it without `cls.__class_objects_map__`.
- Auto-ID generation uses `'increment'` by default; `'uuid'` is reserved.
- All abstract methods and registries must be properly overridden in subclasses.

### Compatibility
Maintain Python 3.10.12+ only. Do not use 3.11/3.12+ features unless explicitly requested.

### Interface integrity
- The `Identifiable` mixin must maintain **one seam**: the subclass interface. Adding behaviour beside it, not behind it, is shallow.
- **One adapter, hypothetical seam.** Do not introduce a port unless two adapters are justified.
- The interface is the test surface. If you want to test past the interface, the module is the wrong shape.

---

## 🚫 Anti-patterns

| Anti-pattern | Why it fails here | What to do instead |
|-------------|-------------------|-------------------|
| **Horizontal slicing** | Testing all shapes before understanding behaviour. Tests go insensitive. | Vertical slices: one test → one implementation per cycle. |
| **Implementation-coupled tests** | Breaks on refactor. Proves internal structure, not correctness. | Test at public seams only. |
| **Modifying `__new__`/`__init_subclass__` blindly** | Changes subclass registration, auto-ID, and registry — cascading failure. | Understand subclass lifecycle before touching methods of class initialization. |
| **Speculative generality** | Abstraction for imagined future cases complicates the present. | Inline back until a real need shows. |
| **Unconfirmed test seams** | Wastes effort on edge cases, misses critical paths. | Pre-agree which public seams are under test. |
| **Shipping prototype code** | Unpolished, untested, misleading. | Capture the decision. Delete the prototype. |
| **Skipping the feedback loop in debugging** | Guesswork without a signal. Wastes the agent's context. | Build a tight loop before forming hypotheses. |

---

## ✅ Session Checklist

At the start of every session:

1. **Read this file.** Know the methodology, not just the file format.
2. **Read the full skill document** for any tool you invoke. The skill is not a suggestion.
3. **Check for project glossaries or decision records** before adopting terminology.
4. **Identify the seam(s)** under test. Pre-agree with the user before writing tests.
5. **Build a feedback loop** before debugging. Never skip Phase 1.
6. **State the question explicitly** before prototyping. One paragraph. Visible.
7. **Ask clarifying questions** before modifying `__new__`, `__init_subclass__`, or the registry.

---

## ⚠️ Agent Notes

- This file is the **only** operational methodology reference for this repo.
- Do not assume your pre-training on Python class design, mixins, or test-driven development applies beyond the procedures documented here.
- The `identifiable` package uses advanced metaprogramming. Changing `__new__`, `__init_subclass__`, or the registry is **the highest-risk action** in this repo. Proceed through the checklist.
- When unsure, default to **explicit over implicit**, **tests over assumptions**, and **depth over shallow pass-through**.
- If you encounter a design decision that cannot be resolved from the existing code or this file, **ask**.

---

*This file is designed to be read by AI agents. It is not a human-facing document. For humans, see `README.md`.*
