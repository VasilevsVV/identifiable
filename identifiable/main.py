from abc import abstractmethod
from collections.abc import Hashable
from typing import Any, Generic, Literal, TypeVar

from typing_extensions import Self

# Type of the unique ID; IDs are registry keys, so it must be hashable.
_KEY_T = TypeVar('_KEY_T', bound=Hashable)


def _has_concrete_uid(cls: type) -> bool:
    """Return True if `cls` has a non-abstract `uid()`."""
    uid_method = getattr(cls, 'uid', None)
    return uid_method is not None and not getattr(
        uid_method, '__isabstractmethod__', False
    )


class Identifiable(Generic[_KEY_T]):
    """Mixin that gives every instance a unique ID and a class-level registry.

    Type parameter:
        _KEY_T: The ID type. Must be hashable.

    Attributes (optional, set on a direct subclass):
        __enable_auto_id__: Generate an ID for every new instance. Default
            True; turned off automatically when the subclass defines `uid()`.
        __id_generation_strategy__: How auto IDs are generated: 'increment'
            (default) or 'uuid'.
        __class_objects_map__: Registry mapping IDs to instances. Default: a
            new dict per direct subclass.
    """

    __class_objects_map__: dict
    __enable_auto_id__: bool = True
    __id_generation_strategy__: Literal['increment', 'uuid'] = 'increment'

    def __new__(cls) -> Self:
        """Create an instance; with auto-ID on, assign it a generated ID.

        Returns:
            The new instance. With auto-ID on, its `uid()` returns the ID.
        """
        obj = super().__new__(cls)
        if cls.__enable_auto_id__:
            obj.__unique_id = cls.__gen_unique_id()  # type: ignore
            obj.uid = lambda: obj.__unique_id  # type: ignore
        return obj

    def __init_subclass__(cls, **kw: Any) -> None:
        """Set up a direct subclass: its registry and auto-ID setting.

        Deeper subclasses are left as they are and share their parent's
        registry. A subclass with its own `uid()` gets auto-ID turned off.

        Args:
            **kw: Passed on to `super().__init_subclass__`.

        Raises:
            TypeError: `__class_objects_map__` isn't a dict, or auto-ID is off
                and `uid()` isn't implemented.
        """
        if Identifiable not in cls.__bases__:
            super().__init_subclass__(**kw)
            return

        if hasattr(cls, '__class_objects_map__'):
            if not isinstance(cls.__class_objects_map__, dict):
                raise TypeError(
                    f'{cls.__name__}.__class_objects_map__ must be a dict, '
                    f'got {type(cls.__class_objects_map__).__name__}'
                )
        else:
            cls.__class_objects_map__ = {}

        if _has_concrete_uid(cls):
            cls.__enable_auto_id__ = False
        elif not cls.__enable_auto_id__:
            raise TypeError(
                f'{cls.__name__} must implement uid() or enable __enable_auto_id__'
            )
        super().__init_subclass__(**kw)

    # TODO: not implemented.
    @classmethod
    def __register_unique_id(cls, id: _KEY_T) -> None:
        """Add `id` to the class's registry."""

    # TODO: not implemented; returns None.
    @classmethod
    def __gen_unique_id(cls) -> _KEY_T:
        """Return a new, unregistered ID made with the class's strategy."""
        ...  # noqa: PIE790 (pyright needs it for a stub)

    # TODO: not implemented; returns None.
    @classmethod
    def get_object(cls, id: _KEY_T) -> Self:
        """Look up an instance in the class's registry.

        Args:
            id: The ID of the instance.

        Returns:
            The instance registered under `id`.
        """
        ...  # noqa: PIE790 (pyright needs it for a stub)

    @abstractmethod
    def uid(self) -> _KEY_T:
        """Return this object's unique ID.

        Returns:
            The ID, of the class's ID type.
        """
        ...
