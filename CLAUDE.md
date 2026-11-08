# CLAUDE.md

@AGENTS.md

## Claude-specific

- Don't paste AGENTS.md content back into replies; reference sections by name.
- Use plan mode before touching anything in the AGENTS.md Danger zone.
- Follow the AGENTS.md step-by-step execution workflow. In plan mode, the plan file must include the steps table.
- Keep in-code docs and comments to a minimum: state only what the class, method or function actually does. Goals, rationale and roadmap belong in README.md.
  - Public names (no leading underscore, including dunder hooks such as `__new__` and `__init_subclass__`) get full interface coverage: what it does, arguments, return value, raised errors, and settings or attributes for classes.
  - Private and protected names (`_name`, `__name`) get a one-line docstring.
