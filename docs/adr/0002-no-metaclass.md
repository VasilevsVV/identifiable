# No metaclass

`Identifiable` is a plain mixin with no metaclass, so it can be added to existing classes,
including classes that already have a metaclass such as Django or SQLAlchemy models. Mixing
bases with unrelated metaclasses raises a metaclass conflict at class creation, which the user
would have to resolve by writing a combined metaclass.

## Considered options

- **`ABCMeta`.** Would make Python and pyright reject a class without `make_uid()`. Rejected
  because of the metaclass conflicts above.
- **`ABCMeta` for pyright only** (behind `TYPE_CHECKING`). Rejected: pyright then reports false
  metaclass conflicts for the same models.

## Consequences

- pyright doesn't flag a missing `make_uid()`. It's only caught at runtime, as a `TypeError`
  when the class is instantiated.
