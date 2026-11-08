"""Tests for the public behaviour of the Identifiable mixin.

Each test defines its own classes so registries never leak between tests.
Tests marked `xfail(strict=True)` describe behaviour that isn't implemented
yet. They fail loudly once the behaviour lands, so remove the marker then.
"""

import pytest

from identifiable import Identifiable

NOT_IMPLEMENTED = 'increment strategy, registry and get_object are not implemented yet'


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
    with pytest.raises(AssertionError):

        class A(Identifiable[str]):
            __class_objects_map__ = 'not a dict'  # pyright: ignore[reportAssignmentType]

            def uid(self) -> str:
                return 'a'


# --- uid() requirement ------------------------------------------------------


def test_missing_uid_raises_when_auto_id_is_off() -> None:
    with pytest.raises(Exception):  # noqa: B017

        class A(Identifiable[str]):
            __enable_auto_id__ = False


def test_concrete_uid_is_used() -> None:
    class A(Identifiable[str]):
        def uid(self) -> str:
            return 'fixed'

    assert A().uid() == 'fixed'


# --- Auto-ID ----------------------------------------------------------------


def test_auto_id_instance_has_callable_uid() -> None:
    class A(Identifiable[int]):
        __enable_auto_id__ = True

    assert callable(A().uid)


@pytest.mark.xfail(strict=True, reason=NOT_IMPLEMENTED)
def test_auto_ids_are_increasing_ints() -> None:
    class A(Identifiable[int]):
        __enable_auto_id__ = True

    a, b = A(), A()
    assert isinstance(a.uid(), int)
    assert b.uid() == a.uid() + 1


@pytest.mark.xfail(strict=True, reason=NOT_IMPLEMENTED)
def test_get_object_returns_registered_instance() -> None:
    class A(Identifiable[int]):
        __enable_auto_id__ = True

    a = A()
    assert A.get_object(a.uid()) is a


# --- Inheritance edge cases -------------------------------------------------


def test_indirect_subclass_shares_parent_registry() -> None:
    # Current behaviour; whether it's intended is still undecided.
    class Parent(Identifiable[str]):
        def uid(self) -> str:
            return 'p'

    class Child(Parent):
        pass

    assert Child.__class_objects_map__ is Parent.__class_objects_map__


@pytest.mark.xfail(strict=True, reason='__new__ takes no arguments (known issue)')
def test_subclass_with_init_args_can_be_instantiated() -> None:
    class A(Identifiable[int]):
        __enable_auto_id__ = True

        def __init__(self, x: int) -> None:
            self.x = x

    assert A(1).x == 1  # pyright: ignore[reportCallIssue]
