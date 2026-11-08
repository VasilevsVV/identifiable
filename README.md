# identifiable

A mixin for Python 3.10+ that gives objects IDs, keeps them in a registry,
and finds them by ID.

Add `Identifiable` to a class's bases and implement `make_uid()`. Every new
object gets an ID made from its constructor arguments and is registered right
away. A second object with the same ID is rejected. The ID can be any hashable
value: a `str`, an `int`, a tuple, even a class.

Because the ID comes from the constructor arguments, you know it before the
object exists. Other code can hold the ID instead of the object and look the
object up only when it needs it.

> **Status:** 0.1.0, early work in progress. See [Roadmap](#roadmap).

## Why

Picture a set of rules that describe datasets. Every rule has a unique name,
rules come in many classes (`SchemaRule`, `FreshnessRule`, ...), and rules
depend on each other. If each rule holds the rule *objects* it depends on,
everything gets tangled: each rule's module imports the classes it depends on,
rules must be built in dependency order, and a rule can't depend on one that
hasn't been built yet.

With `identifiable`, a rule holds an **ID reference** instead: the other rule's
ID, as a plain value. The rule behind it is looked up only when it's needed.

```python
from identifiable import Identifiable


class Rule(Identifiable[str]):
    @classmethod
    def make_uid(cls, name: str, **settings: object) -> str:
        return name

    def __init__(self, name: str, **settings: object) -> None:
        self.name = name


# freshness.py: doesn't import SchemaRule
class FreshnessRule(Rule):
    def __init__(self, name: str, *, depends_on: str, max_age_hours: int) -> None:
        super().__init__(name)
        self.depends_on = depends_on  # an ID reference
        self.max_age_hours = max_age_hours

    def upstream(self) -> Rule:
        return Rule.get_object(self.depends_on)


# schema.py: doesn't import FreshnessRule
class SchemaRule(Rule):
    def __init__(self, name: str, *, columns: list[str]) -> None:
        super().__init__(name)
        self.columns = columns


# Build in any order: the reference is only looked up when it's used.
fresh = FreshnessRule('orders_fresh', depends_on='orders_schema', max_age_hours=24)
SchemaRule('orders_schema', columns=['id', 'total'])

fresh.upstream()  # the SchemaRule named 'orders_schema'
SchemaRule('orders_fresh', columns=[])  # raises DuplicateUIDError
```

The last line fails because names are unique across all rules, whatever
their class. `identifiable` only finds objects. If an ID reference might point
to an object that doesn't exist yet, use `Rule.find_object()`, which returns
`None` instead of raising, and create the object in your own code.

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

## Use cases

### Named jobs, picked from the command line

Two jobs with the same name fail when the module is imported, not at 2 a.m.

```python
from identifiable import Identifiable


class Job(Identifiable[str]):
    @classmethod
    def make_uid(cls, name: str, schedule: str) -> str:
        return name

    def __init__(self, name: str, schedule: str) -> None:
        self.name = name
        self.schedule = schedule

    def run(self) -> None:
        print(f'running {self.name}')


Job('nightly-report', schedule='0 2 * * *')
Job('cleanup', schedule='0 3 * * *')


def main(job_name: str) -> None:  # e.g. `python jobs.py cleanup`
    Job.get_object(job_name).run()


main('cleanup')
```

### Reference data from a seed file

Objects that use a currency store its code, an ID reference, and look the
currency up when they need it. A repeated row in the seed file raises
`DuplicateUIDError` while loading, instead of quietly replacing the first one.

```python
from identifiable import Identifiable


class Currency(Identifiable[str]):
    @classmethod
    def make_uid(cls, code: str, decimals: int) -> str:
        return code

    def __init__(self, code: str, decimals: int) -> None:
        self.code = code
        self.decimals = decimals


# Rows read from currencies.csv
rows = [{'code': 'EUR', 'decimals': 2}, {'code': 'JPY', 'decimals': 0}]
for row in rows:
    Currency(**row)


class Price:
    def __init__(self, minor_units: int, currency: str) -> None:
        self.minor_units = minor_units
        self.currency = currency  # an ID reference: 'EUR'

    def __str__(self) -> str:
        currency = Currency.get_object(self.currency)
        return f'{self.minor_units / 10**currency.decimals:.{currency.decimals}f} {currency.code}'


print(Price(1999, 'EUR'))  # 19.99 EUR
```

### ID references in a REST API

A response carries the IDs of related objects instead of embedding them. The
client requests them only if it needs them.

```python
from identifiable import Identifiable


class Rule(Identifiable[str]):
    @classmethod
    def make_uid(cls, name: str, depends_on: tuple[str, ...] = ()) -> str:
        return name

    def __init__(self, name: str, depends_on: tuple[str, ...] = ()) -> None:
        self.name = name
        self.depends_on = depends_on


def get_rule(rule_id: str) -> tuple[int, dict]:  # GET /rules/{rule_id}
    rule = Rule.find_object(rule_id)
    if rule is None:
        return 404, {'error': f'no rule {rule_id!r}'}
    return 200, {'id': rule.uid, 'depends_on': list(rule.depends_on)}


Rule('orders_schema')
Rule('orders_fresh', depends_on=('orders_schema',))
get_rule('orders_fresh')
# (200, {'id': 'orders_fresh', 'depends_on': ['orders_schema']})
get_rule('missing')  # (404, {'error': "no rule 'missing'"})
```

### One object per class

The ID can be the class itself. Then each class in the family can have exactly
one object, whatever its settings.

```python
from identifiable import Identifiable


class Connector(Identifiable[type]):
    @classmethod
    def make_uid(cls, **settings: object) -> type:
        return cls

    def __init__(self, **settings: object) -> None:
        self.settings = settings


class PostgresConnector(Connector): ...


class S3Connector(Connector): ...


PostgresConnector(host='db.internal', port=5432)
S3Connector(bucket='exports')
Connector.get_object(S3Connector)  # the only S3Connector
PostgresConnector(host='replica.internal')  # raises DuplicateUIDError
```

## Adding to existing classes

`Identifiable` has no metaclass and doesn't touch `__init__`, so it fits into
classes you already have, including ones with their own metaclass. Two steps:

1. Add `Identifiable[<ID type>]` to the class's bases.
2. Implement `make_uid()` as a classmethod. It receives the same arguments as
   `__init__`, so give it a matching signature.

It works with dataclasses too:

```python
from dataclasses import dataclass

from identifiable import Identifiable


@dataclass
class Sensor(Identifiable[str]):
    serial: str
    location: str = 'unknown'

    @classmethod
    def make_uid(cls, serial: str, location: str = 'unknown') -> str:
        return serial


sensor = Sensor('SN-0042', location='roof')
sensor.uid  # 'SN-0042'
```

**Copying and pickling don't work yet.** `copy.copy`, `copy.deepcopy` and
`pickle` create objects without calling the constructor, so `make_uid()` gets
no arguments and raises `TypeError`. The same goes for anything that pickles
objects, such as `multiprocessing` queues and pools. See [Roadmap](#roadmap).

**An object whose `__init__` raises stays registered.** The object is
registered before `__init__` runs, so the lookups return it half-built, and
its ID can't be used again.

## When not to use it

- **Short-lived objects.** The registry keeps every object for as long as the
  process runs, and nothing is ever removed. Per-request or per-row objects
  pile up.
- **Many objects created fast.** Every construction calls `make_uid()` and
  checks and updates the registry. For thousands to millions of objects, such
  as tree nodes or linked-list items, that overhead is noticeable.
- **More than one registry per family.** The registry lives on the class, so a
  process has exactly one per family. You can't keep a separate registry per
  tenant, and tests that create objects need their own classes or a cleared
  registry.
- **Data behind an ORM.** ORMs such as SQLAlchemy already map primary keys to
  loaded objects. Use their identity map instead.

## Interface

What your class defines:

| Method | Required? | Meaning |
|---|---|---|
| `make_uid(cls, *args, **kwargs) -> ID` | Yes (classmethod) | Return the ID for a new object. It gets the constructor arguments and runs before `__init__`. Creating an object of a class without it raises `TypeError`. |

What the mixin gives you:

| Name | Meaning |
|---|---|
| `obj.uid` | The object's ID (read-only property). |
| `Cls.get_object(id)` | Return the object registered under `id`. On the family base, it finds any object in the family; on a subclass, only objects of that subclass. Typed as the class it's called on. Raises `UnknownUIDError` or `WrongClassUIDError` if there's no such object. |
| `Cls.find_object(id)` | The same lookup, but returns `None` instead of raising. |
| `DuplicateUIDError` | Raised when a new object's ID is already in its family's registry. A `ValueError`. No object is created and the registered one is kept. |
| `UnknownUIDError` | Raised by `get_object()` when no object in the family has the ID. A `KeyError`. |
| `WrongClassUIDError` | Raised by `get_object()` when the ID belongs to an object of another class in the family. A `KeyError`. |

## Families and the registry

The class that lists `Identifiable` in its bases is the **family base**. It
and all of its subclasses form one **family** that shares one registry. As a
result:

- An ID is unique across the whole family. `SchemaRule('orders')` and
  `FreshnessRule('orders')` can't both exist.
- Any member of the family can refer to any other by ID and look it up
  through the family base, without importing its class.
- A lookup on a subclass only finds that subclass's objects. So
  `SchemaRule.find_object(id) or SchemaRule(id, ...)` can still raise
  `DuplicateUIDError` when a `FreshnessRule` holds the ID. On the family base,
  `None` means the ID is free.
- Separate families have separate registries, so they can reuse IDs.

For the reasoning, see
[ADR 0001](docs/adr/0001-one-registry-per-family.md) and
[ADR 0003](docs/adr/0003-lookup-narrows-to-the-called-class.md).

You can set the registry yourself as a class attribute on the family base:

| Attribute | Default | Meaning |
|---|---|---|
| `__class_objects_map__` | a new `dict` | The registry that maps IDs to objects. You can provide your own `dict`; anything else raises `TypeError`. |

## Scope

`identifiable` makes IDs, registers objects under them and finds them by ID.
Your own code stays in charge of:

- creating objects, including creating them lazily on first access;
- resolving ID references: an ID reference is a plain value until you look it
  up.

The terms used here are defined in [GLOSSARY.md](GLOSSARY.md).

## Roadmap

- Remove an object from the registry when its `__init__` raises.
- Support `copy` and `pickle`. The behaviour still needs a design, since a copy
  would be a duplicate.
- Ready-made ID generation (sequential integers, UUIDs) as a separate class,
  for objects without a natural name. A generated ID isn't known before the
  object exists, so it can't be referenced in advance.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# lint, format check, type check, tests
ruff check . && ruff format --check . && pyright && pytest
```

## License

GNU General Public License v3. See [LICENSE](LICENSE).
