from pydantic import BaseModel
from functools import wraps
from typing import Callable
from typing import Type


def validate_with_pydantic(input_model: Type[BaseModel]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], input_model):
                # If the passed argument is already an instance of the expected model, skip validation
                validated_input = args[0]
            else:
                input_data = {**kwargs, **dict(zip(func.__annotations__.keys(), args))}
                validated_input = input_model(**input_data)

            dictionary_input = {}
            for k,v in validated_input:
                dictionary_input[k] = v
            return func(**dictionary_input)
        
        return wrapper
    return decorator
