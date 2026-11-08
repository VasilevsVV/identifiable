from abc import abstractmethod
from collections.abc import Hashable
from typing import Any, Generic, Literal, TypeVar

from typing_extensions import Self

# Type of the unique ID. It must be hashable because IDs are registry keys.
_KEY_T = TypeVar('_KEY_T', bound=Hashable)


def _has_concrete_uid(cls: type) -> bool:
    """Return True if `cls` provides a non-abstract `uid()` method."""
    uid_method = getattr(cls, 'uid', None)
    return uid_method is not None and not getattr(
        uid_method, '__isabstractmethod__', False
    )


class Identifiable(Generic[_KEY_T]):
    """Mixin that gives every instance a unique ID and a class-level registry.

    Add it to a class's bases to use it. Optional class-level settings:

    - `__enable_auto_id__` (default True): an ID is generated for every new
      instance and exposed through `uid()`. A direct subclass that defines
      its own `uid()` gets this turned off automatically. Setting it to False
      without defining `uid()` is an error.
    - `__id_generation_strategy__`: how auto IDs are generated. Only
      'increment' is planned for now; 'uuid' is reserved.
    - `__class_objects_map__`: the registry mapping IDs to instances. Each
      direct subclass gets a fresh `dict` unless it provides its own.

    Note: names with two leading underscores and no trailing ones (such as
    `__gen_unique_id`) are name-mangled to `_Identifiable__*`, so subclasses
    can't override them by their plain names.
    """

    __class_objects_map__: dict
    __enable_auto_id__: bool = True
    __id_generation_strategy__: Literal['increment', 'uuid'] = 'increment'

    def __new__(cls) -> Self:
        obj = super().__new__(cls)
        if cls.__enable_auto_id__:
            # Store the generated ID on the instance and expose it via uid().
            obj.__unique_id = cls.__gen_unique_id()  # type: ignore
            obj.uid = lambda: obj.__unique_id  # type: ignore
        return obj

    def __init_subclass__(cls, **kw: Any) -> None:
        # Only direct subclasses are set up. Deeper subclasses skip this and
        # inherit (share) their direct parent's registry and settings.
        if Identifiable not in cls.__bases__:
            super().__init_subclass__(**kw)
            return

        # A real `raise`, not `assert`: asserts are stripped under `python -O`.
        if hasattr(cls, '__class_objects_map__'):
            if not isinstance(cls.__class_objects_map__, dict):
                raise TypeError(
                    f'{cls.__name__}.__class_objects_map__ must be a dict, '
                    f'got {type(cls.__class_objects_map__).__name__}'
                )
        else:
            cls.__class_objects_map__ = {}

        # Identifiable has no ABCMeta, so @abstractmethod isn't enforced by
        # Python; uid() is checked by hand. A custom uid() means the user owns
        # IDs, so auto-ID is turned off (otherwise __new__ would hide uid()).
        if _has_concrete_uid(cls):
            cls.__enable_auto_id__ = False
        elif not cls.__enable_auto_id__:
            raise TypeError(
                f'{cls.__name__} must implement uid() or enable __enable_auto_id__'
            )
        super().__init_subclass__(**kw)

    # TODO: stub, not implemented yet.
    @classmethod
    def __register_unique_id(cls, id: _KEY_T) -> None: ...

    # TODO: stub, not implemented yet. Returns None for now.
    @classmethod
    def __gen_unique_id(cls) -> _KEY_T: ...

    # TODO: stub, not implemented yet. Returns None for now.
    @classmethod
    def get_object(cls, id: _KEY_T) -> Self: ...

    @abstractmethod
    def uid(self) -> _KEY_T:
        """Return this object's unique ID."""
        ...
