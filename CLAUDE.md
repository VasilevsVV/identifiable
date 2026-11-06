# CLAUDE.md

Claude Code reads this file. It provides repository-specific context and instructions.

## Instructions

1. **Always read `AGENTS.md` at the start of every session.** It is the complete methodology, conventions, and operational rules for this repo. Read it in full. Follow every rule. Nothing is optional.

2. **Do not repeat content from `AGENTS.md` in your messages.** It lives in the workspace and you can always re-read it. Do not paste it back.

3. **If you encounter a design decision you cannot resolve from the existing code or AGENTS.md, ask.**

## Quick Context

- **Project**: `identifiable` — Python 3.10+ mixin pattern for uniquely identifying objects with auto-ID generation per subclass.
- **Core file**: `identifiable/main.py` (~80 lines)
- **Stack**: Python, ruff, pyright, pytest, setuptools
- **Danger zone**: Modifying `__new__`, `__init_subclass__`, or the subclass registry. These affect every subclass. Always go through the checklist.
