from typing import Any, Generic, Hashable, Literal, TypeVar
from abc import abstractmethod
from typing_extensions import Self

CT = TypeVar('CT')
_KEY_T = TypeVar('_KEY_T', bound=Hashable)

class Identifiable(Generic[_KEY_T]):
    __class_objects_map__: dict
    __enable_auto_id__: bool = False
    __id_generation_strategy__: Literal['increment', 'uuid'] = 'increment'
    
    
    def __new__(cls) -> Self:
        obj = super().__new__(cls)
        if cls.__enable_auto_id__:
            obj.__unique_id = cls.__gen_unique_id() # type: ignore
            obj.uid = lambda: obj.__unique_id # type: ignore
        return obj
    
    
    def __init_subclass__(cls, **kw: Any) -> None:
        if Identifiable not in cls.__bases__:
            super().__init_subclass__(**kw)
            return
        if hasattr(cls, '__class_objects_map__'):
            assert isinstance(cls.__class_objects_map__, dict), \
                f'"__class_objects_map__" attribute must be a dict! Got: {cls.__class_objects_map__}'
        else:
            cls.__class_objects_map__: dict = {}
        
        if not cls.__enable_auto_id__:    
            uid_method = getattr(cls, "uid", None)
            # Checking if class has def uid() implemented
            if (uid_method is None
                or (hasattr(uid_method, '__isabstractmethod__')
                    and uid_method.__isabstractmethod__ == True)
                ):
                raise Exception(f'Profiling {cls.__name__} has not implementation for method "execute()"!!!')
        super().__init_subclass__(**kw)

    @classmethod
    def __register_unique_id(cls, id: _KEY_T): ...
    
    @classmethod
    def __gen_unique_id(cls) -> _KEY_T: ...
    
    @classmethod
    def get_object(cls: CT, id: _KEY_T) -> CT: ...
    
    @abstractmethod
    def uid(self) -> _KEY_T: ...
    
    


# class IdentifiableNested:
#     def __init_subclass__(cls) -> None:
#         super().__init_subclass__()