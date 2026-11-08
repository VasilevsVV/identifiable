# One registry per family

A family base (the class that mixes in `Identifiable` directly) and all of its subclasses share
one registry, so they share one ID namespace. Family members can then refer to each other by ID
without importing each other's classes, and a lookup searches the whole family. This came from a
system of rules describing datasets: rules of many classes referenced each other by name, often
before the referenced rule existed.

## Considered options

- **A registry per class.** Rejected: an ID reference would have to name the concrete class it
  points to, which brings back the imports and creation-order coupling this design removes.

## Consequences

- Sibling classes can't reuse an ID: `SchemaRule('orders')` followed by `FreshnessRule('orders')`
  raises `DuplicateUIDError`.
- `get_object()` is typed to return the family base, not the class it's called on, because a
  lookup through any class in the family can return any family member.
