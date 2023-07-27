from pydantic import BaseModel
from functools import wraps
from typing import Callable, Type


def validate_with_pydantic(input_model: Type[BaseModel]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            input_data = {**kwargs, **dict(zip(func.__annotations__.keys(), args))}
            validated_input = input_model(**input_data)
            return func(**validated_input.dict())
        return wrapper
    return decorator
