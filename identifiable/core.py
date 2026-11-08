from abc import abstractmethod
from collections.abc import Hashable
from typing import Any, Generic, TypeVar

from typing_extensions import Self

# Type of the unique ID; IDs are registry keys, so it must be hashable.
_KEY_T = TypeVar('_KEY_T', bound=Hashable)


class Identifiable(Generic[_KEY_T]):
    """Mixin that gives every instance a unique ID and a class-level registry.

    Type parameter:
        _KEY_T: The ID type. Must be hashable.

    Attributes (optional, set on a direct subclass):
        __class_objects_map__: Registry mapping IDs to instances. Default: a
            new dict per direct subclass.
    """

    __class_objects_map__: dict

    def __init_subclass__(cls, **kw: Any) -> None:
        """Set up a direct subclass's registry.

        Deeper subclasses are left as they are and share their parent's
        registry.

        Args:
            **kw: Passed on to `super().__init_subclass__`.

        Raises:
            TypeError: `__class_objects_map__` isn't a dict.
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
        super().__init_subclass__(**kw)

    # TODO: not implemented.
    @classmethod
    def __register_unique_id(cls, id: _KEY_T) -> None:
        """Add `id` to the class's registry."""

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
