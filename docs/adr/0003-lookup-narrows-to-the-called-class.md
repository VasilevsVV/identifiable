# Lookup narrows to the class it's called on

`Cls.get_object(id)` returns the object registered under `id` only if it's an instance of
`Cls`, and is typed `-> Self`. Python's type system can't name the family base from a subclass,
so this is how the declared type stays true without extra syntax. Called on the family base, a
lookup finds any family member. Called on a subclass, it finds only that subclass's objects.

A failed lookup raises one of two `KeyError` subclasses, so callers can tell the cases apart:
`UnknownUIDError` (no object in the family has the ID) and `WrongClassUIDError` (another class
in the family holds it). `find_object(id)` does the same lookup but returns `None` in both
cases, so code that only needs "is there one?" never has to catch an error.

## Considered options

- **A second type parameter** (`Identifiable[str, 'Rule']`), typed to the family base from any
  class. Rejected: users would repeat the class name in the bases, against the "add to the
  bases and implement `make_uid()`" goal, and it needs `typing_extensions>=4.12`.
- **`Self` with an unfiltered lookup.** Rejected: `SchemaRule.get_object()` could return a
  `FreshnessRule` typed as `SchemaRule`.
- **A `default=` argument on the lookup.** Rejected: any default is ambiguous, and the mixin
  doesn't create objects.

## Consequences

- An ID can be in the registry while `SchemaRule.get_object(id)` raises `WrongClassUIDError`.
- To look up across the family, call the lookup on the family base.
- `SchemaRule.find_object(id) or SchemaRule(id)` can still raise `DuplicateUIDError` when
  another class in the family holds the ID. On the family base, `None` means the ID is free.
