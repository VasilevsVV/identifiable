"""Tests for the public behaviour of the Identifiable mixin.

Each test defines its own classes so registries never leak between tests.
Tests marked `xfail(strict=True)` describe behaviour that isn't implemented
yet. They fail loudly once the behaviour lands, so remove the marker then.
"""

import pytest

from identifiable import DuplicateUIDError, Identifiable

# --- Registry setup ---------------------------------------------------------


def test_each_direct_subclass_gets_own_empty_registry() -> None:
    class A(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'a'

    class B(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'b'

    assert A.__class_objects_map__ == {}
    assert B.__class_objects_map__ == {}
    assert A.__class_objects_map__ is not B.__class_objects_map__


def test_user_provided_dict_registry_is_kept() -> None:
    registry: dict = {}

    class A(Identifiable[str]):
        __class_objects_map__ = registry

        @classmethod
        def make_uid(cls) -> str:
            return 'a'

    assert A.__class_objects_map__ is registry


def test_non_dict_registry_is_rejected() -> None:
    with pytest.raises(TypeError, match='must be a dict'):

        class A(Identifiable[str]):
            __class_objects_map__ = 'not a dict'  # pyright: ignore[reportAssignmentType]

            @classmethod
            def make_uid(cls) -> str:
                return 'a'


# --- make_uid() and uid -----------------------------------------------------


def test_uid_returns_id_made_by_make_uid() -> None:
    class A(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'fixed'

    assert A().uid == 'fixed'


def test_make_uid_gets_constructor_args() -> None:
    class Country(Identifiable[str]):
        @classmethod
        def make_uid(cls, code: str, *, suffix: str = '') -> str:
            return code + suffix

        def __init__(self, code: str, *, suffix: str = '') -> None:
            self.code = code

    country = Country('UA', suffix='-1')
    assert country.uid == 'UA-1'
    assert country.code == 'UA'


def test_uid_is_read_only() -> None:
    class A(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'a'

    a = A()
    with pytest.raises(AttributeError):
        a.uid = 'b'  # pyright: ignore[reportAttributeAccessIssue]
    assert a.uid == 'a'


def test_missing_make_uid_raises_on_instantiation() -> None:
    class A(Identifiable[str]):
        pass

    with pytest.raises(TypeError, match=r'must implement make_uid\(\)'):
        A()


def test_make_uid_can_come_from_indirect_subclass() -> None:
    class Base(Identifiable[str]):
        pass

    class Child(Base):
        @classmethod
        def make_uid(cls) -> str:
            return 'child'

    assert Child().uid == 'child'
    with pytest.raises(TypeError, match=r'must implement make_uid\(\)'):
        Base()


# --- Registration -----------------------------------------------------------


def test_new_objects_are_registered_under_their_uid() -> None:
    class A(Identifiable[str]):
        @classmethod
        def make_uid(cls, code: str) -> str:
            return code

        def __init__(self, code: str) -> None:
            self.code = code

    a, b = A('a'), A('b')
    assert A.__class_objects_map__.keys() == {'a', 'b'}
    assert A.__class_objects_map__['a'] is a
    assert A.__class_objects_map__['b'] is b


# --- Lookup -----------------------------------------------------------------


def test_get_object_returns_registered_instance() -> None:
    class A(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'a'

    a = A()
    assert A.get_object(a.uid) is a


# --- Duplicate keys ---------------------------------------------------------


def test_duplicate_key_in_same_registry_is_rejected() -> None:
    class Country(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'UA'

    first = Country()
    with pytest.raises(DuplicateUIDError, match='duplicate'):
        Country()
    assert Country.__class_objects_map__ == {'UA': first}


def test_duplicate_uid_error_is_a_value_error() -> None:
    assert issubclass(DuplicateUIDError, ValueError)


def test_same_key_in_separate_registries_is_allowed() -> None:
    class A(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'same'

    class B(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'same'

    assert A().uid == B().uid == 'same'


# --- Inheritance edge cases -------------------------------------------------


def test_indirect_subclass_shares_parent_registry() -> None:
    class Parent(Identifiable[str]):
        @classmethod
        def make_uid(cls) -> str:
            return 'p'

    class Child(Parent):
        pass

    assert Child.__class_objects_map__ is Parent.__class_objects_map__


def test_sibling_subclasses_share_id_namespace() -> None:
    class Rule(Identifiable[str]):
        @classmethod
        def make_uid(cls, name: str) -> str:
            return name

        def __init__(self, name: str) -> None:
            self.name = name

    class SchemaRule(Rule):
        pass

    class FreshnessRule(Rule):
        pass

    schema = SchemaRule('orders')
    with pytest.raises(DuplicateUIDError, match='duplicate'):
        FreshnessRule('orders')
    assert Rule.__class_objects_map__ == {'orders': schema}


def test_subclass_with_init_args_can_be_instantiated() -> None:
    class A(Identifiable[int]):
        @classmethod
        def make_uid(cls, x: int) -> int:
            return x

        def __init__(self, x: int) -> None:
            self.x = x

    a = A(1)
    assert a.x == 1
    assert a.uid == 1
