from abc import abstractmethod
from collections.abc import Hashable
from typing import Any, Generic, TypeVar

from typing_extensions import Self

# Type of the unique ID; IDs are registry keys, so it must be hashable.
_KEY_T = TypeVar('_KEY_T', bound=Hashable)


class DuplicateUIDError(ValueError):
    """Raised when a new object's ID is already in its class's registry.

    Raised by `Identifiable.__new__`; the registered object is kept.
    """


class Identifiable(Generic[_KEY_T]):
    """Mixin that gives every instance a unique ID and a class-level registry.

    Type parameter:
        _KEY_T: The ID type. Must be hashable.

    Attributes (optional, set on a direct subclass):
        __class_objects_map__: Registry mapping IDs to instances. Default: a
            new dict per direct subclass.
    """

    __class_objects_map__: dict
    __uid: _KEY_T

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Create an instance with the ID from `make_uid()` and register it.

        The instance is added to `__class_objects_map__` under its ID before
        `__init__` runs.

        Args:
            *args: Constructor arguments, passed on to `make_uid()`.
            **kwargs: Constructor keyword arguments, passed on to
                `make_uid()`.

        Returns:
            The new instance. Its `uid` is the ID from `make_uid()`.

        Raises:
            TypeError: The class doesn't implement `make_uid()`.
            DuplicateUIDError: The ID is already registered. No instance is
                created.
        """
        if getattr(cls.make_uid, '__isabstractmethod__', False):
            raise TypeError(f'{cls.__name__} must implement make_uid()')
        uid = cls.make_uid(*args, **kwargs)
        if uid in cls.__class_objects_map__:
            raise DuplicateUIDError(f'{cls.__name__}: duplicate uid {uid!r}')
        obj = super().__new__(cls)
        obj.__uid = uid
        cls.__class_objects_map__[uid] = obj
        return obj

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

    @classmethod
    @abstractmethod
    def make_uid(cls, *args: Any, **kwargs: Any) -> _KEY_T:
        """Return the ID for a new instance. Subclasses must implement it.

        Called by `__new__` before `__init__` runs.

        Args:
            *args: The constructor arguments.
            **kwargs: The constructor keyword arguments.

        Returns:
            The new instance's ID, of the class's ID type.
        """
        ...

    @property
    def uid(self) -> _KEY_T:
        """This object's unique ID, as returned by `make_uid()`. Read-only."""
        return self.__uid
