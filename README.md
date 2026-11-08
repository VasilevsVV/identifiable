# identifiable

A mixin for Python 3.10+ that gives every object a unique ID and keeps a
class-level registry of instances.

The main goal is one universal interface that makes any family of classes
identifiable by an ID of some type: an `int`, a `str`, or any other hashable
type.

Add `Identifiable` to a class's bases and implement `make_uid()`. Every new
object gets its ID from `make_uid()` and is registered right away.

> **Status:** 0.1.0, early work in progress. Object lookup is not implemented
> yet: `get_object()` returns `None`. See [Roadmap](#roadmap).

## Installation

```bash
pip install git+https://github.com/VasilevsVV/identifiable
```

The only runtime dependency is `typing_extensions`.

## Quick start

`make_uid()` is a classmethod. It gets the same arguments as `__init__`:

```python
from identifiable import DuplicateUIDError, Identifiable


class Country(Identifiable[str]):
    @classmethod
    def make_uid(cls, code: str) -> str:
        return code

    def __init__(self, code: str) -> None:
        self.code = code


ua = Country('UA')
ua.uid  # 'UA'
Country.__class_objects_map__  # {'UA': ua}

try:
    Country('UA')
except DuplicateUIDError:
    ...  # 'UA' is already registered
```

The type parameter (`Identifiable[int]`, `Identifiable[str]`, ...) is the ID
type. It must be hashable.

## Interface

What your class defines:

| Method | Required? | Meaning |
|---|---|---|
| `make_uid(cls, *args, **kwargs) -> ID` | Yes (classmethod) | Return the ID for a new object. It gets the constructor arguments and runs before `__init__`. Creating an object of a class without it raises `TypeError`. |

What the mixin gives you:

| Name | Meaning |
|---|---|
| `obj.uid` | The object's ID (read-only property). |
| `Cls.get_object(id)` | Look up an instance by ID in the class's registry (not implemented yet). |
| `DuplicateUIDError` | Raised when a new object's ID is already registered. A `ValueError`. No object is created and the registered one is kept. |

## Optional settings

Set this as a class attribute on a direct subclass of `Identifiable`:

| Attribute | Default | Meaning |
|---|---|---|
| `__class_objects_map__` | a new `dict` | The registry that maps IDs to instances. You can provide your own `dict`; anything else raises `TypeError`. |

Each direct subclass of `Identifiable` gets its own registry. Subclasses of
that class share it.

## Roadmap

- Look up instances with `get_object(id)`.
- Ready-made ID generation (sequential integers, UUIDs) as a separate class,
  so a subclass doesn't have to write `make_uid()` itself.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# lint, format check, type check, tests
ruff check . && ruff format --check . && pyright && pytest
```

## License

GNU General Public License v3. See [LICENSE](LICENSE).
