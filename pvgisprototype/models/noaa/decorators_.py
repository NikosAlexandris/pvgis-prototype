from pydantic import BaseModel
from functools import wraps
from typing import Callable, Type


# def validate_with_pydantic(input_model: Type[BaseModel]) -> Callable:
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             input_data = {**kwargs, **dict(zip(func.__annotations__.keys(), args))}
#             validated_input = input_model(**input_data)
#             return func(**validated_input.model_dump())
#         return wrapper
#     return decorator



def validate_with_pydantic(input_model: Type[BaseModel], expand_args: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], input_model):
                # If the passed argument is already an instance of the expected model, skip validation
                validated_input = args[0]
            else:
                input_data = {**kwargs, **dict(zip(func.__annotations__.keys(), args))}
                validated_input = input_model(**input_data)
            if expand_args:
                return func(**validated_input.pydantic_model_to_dict())
            else:
                return func(validated_input)  # Pass the entire instance instead of expanding it
        return wrapper
    return decorator



def cache_result(func):
    """Decorator to cache function results"""

    def wrapper(*args, **kwargs):
        cache_key = (func.__name__, args, frozenset(kwargs.items()))
        if cache_key not in calculation_cache:
            calculation_cache[cache_key] = func(*args, **kwargs)
        return calculation_cache[cache_key]

    return wrapper
