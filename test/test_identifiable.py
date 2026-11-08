"""Tests for the public behaviour of the Identifiable mixin.

Each test defines its own classes so registries never leak between tests.
Tests marked `xfail(strict=True)` describe behaviour that isn't implemented
yet. They fail loudly once the behaviour lands, so remove the marker then.
"""

import pytest

from identifiable import Identifiable

NOT_IMPLEMENTED = 'registry and get_object are not implemented yet'


# --- Registry setup ---------------------------------------------------------


def test_each_direct_subclass_gets_own_empty_registry() -> None:
    class A(Identifiable[str]):
        def uid(self) -> str:
            return 'a'

    class B(Identifiable[str]):
        def uid(self) -> str:
            return 'b'

    assert A.__class_objects_map__ == {}
    assert B.__class_objects_map__ == {}
    assert A.__class_objects_map__ is not B.__class_objects_map__


def test_user_provided_dict_registry_is_kept() -> None:
    registry: dict = {}

    class A(Identifiable[str]):
        __class_objects_map__ = registry

        def uid(self) -> str:
            return 'a'

    assert A.__class_objects_map__ is registry


def test_non_dict_registry_is_rejected() -> None:
    with pytest.raises(TypeError, match='must be a dict'):

        class A(Identifiable[str]):
            __class_objects_map__ = 'not a dict'  # pyright: ignore[reportAssignmentType]

            def uid(self) -> str:
                return 'a'


# --- Lookup -----------------------------------------------------------------


@pytest.mark.xfail(strict=True, reason=NOT_IMPLEMENTED)
def test_get_object_returns_registered_instance() -> None:
    class A(Identifiable[str]):
        def uid(self) -> str:
            return 'a'

    a = A()
    assert A.get_object(a.uid()) is a


# --- Duplicate keys ---------------------------------------------------------


@pytest.mark.xfail(strict=True, reason=NOT_IMPLEMENTED)
def test_duplicate_key_in_same_registry_is_rejected() -> None:
    class Country(Identifiable[str]):
        def uid(self) -> str:
            return 'UA'

    Country()
    with pytest.raises(ValueError, match='duplicate'):
        Country()


def test_same_key_in_separate_registries_is_allowed() -> None:
    class A(Identifiable[str]):
        def uid(self) -> str:
            return 'same'

    class B(Identifiable[str]):
        def uid(self) -> str:
            return 'same'

    assert A().uid() == B().uid() == 'same'


# --- Inheritance edge cases -------------------------------------------------


def test_indirect_subclass_shares_parent_registry() -> None:
    # Current behaviour; whether it's intended is still undecided.
    class Parent(Identifiable[str]):
        def uid(self) -> str:
            return 'p'

    class Child(Parent):
        pass

    assert Child.__class_objects_map__ is Parent.__class_objects_map__


def test_subclass_with_init_args_can_be_instantiated() -> None:
    class A(Identifiable[str]):
        def __init__(self, x: int) -> None:
            self.x = x

        def uid(self) -> str:
            return 'a'

    assert A(1).x == 1
