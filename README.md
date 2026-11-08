# identifiable

A mixin for Python 3.10+ that gives every object a unique ID and keeps a
class-level registry of instances.

Add `Identifiable` to a class's bases and it works with no further setup.
Settings are optional.

> **Status:** 0.1.0, early work in progress. ID generation and object lookup
> are not implemented yet. Until they are, auto-generated IDs are `None` and
> `get_object()` returns `None`. See [Roadmap](#roadmap).

## Installation

```bash
pip install git+https://github.com/VasilevsVV/identifiable
```

The only runtime dependency is `typing_extensions`.

## Quick start

Auto IDs, no settings needed:

```python
from identifiable import Identifiable


class User(Identifiable[int]):
    pass


user = User()
user.uid()  # the generated ID (None until 'increment' lands)
```

Your own IDs: define `uid()` and the mixin stops generating IDs for that
class.

```python
from identifiable import Identifiable


class Country(Identifiable[str]):
    def uid(self) -> str:
        return 'UA'


Country().uid()  # 'UA'
```

The type parameter (`Identifiable[int]`, `Identifiable[str]`, ...) is the ID
type. It must be hashable.

## Optional settings

Set these as class attributes on a direct subclass of `Identifiable`:

| Attribute | Default | Meaning |
|---|---|---|
| `__enable_auto_id__` | `True` | Generate an ID for every new instance. It's set to `False` automatically when the class defines `uid()`. Setting it to `False` without a `uid()` raises `TypeError`. |
| `__id_generation_strategy__` | `'increment'` | How auto IDs are generated. See [Roadmap](#roadmap). |
| `__class_objects_map__` | a new `dict` | The registry that maps IDs to instances. You can provide your own `dict`; anything else raises `TypeError`. |

Each direct subclass of `Identifiable` gets its own registry. Subclasses of
that class share it.

## Roadmap

ID generation strategies:

- **`increment`** (next, and the default): sequential integer IDs, separate
  for each registry.
- **`uuid`** (planned): random UUIDs.
- **`named`** (planned): string IDs that you supply, with uniqueness checked
  against the registry.

Other planned work:

- Register instances and look them up with `get_object(id)`.
- Support subclasses whose `__init__` takes arguments. Today, creating an
  instance of such a class fails.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# lint, format check, type check, tests
ruff check . && ruff format --check . && pyright && pytest
```

## License

GNU General Public License v3. See [LICENSE](LICENSE).
