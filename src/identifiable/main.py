from typing import Any


class Identifiable:
    __class_objects_map__: dict
    
    def __init_subclass__(cls, **kw: Any) -> None:
        if hasattr(cls, '__class_objects_map__'):
            assert isinstance(cls.__class_objects_map__, dict), \
                f'"__class_objects_map__" attribute must be a dict! Got: {cls.__class_objects_map__}'
        else:
            cls.__class_objects_map__: dict = {}
        super().__init_subclass__(**kw)


class IdentifiableNested:
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()