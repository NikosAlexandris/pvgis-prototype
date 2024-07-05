"""
# Usage :
# in some other module, some other function

# import :
# from pvgisprototype.validation.context import with_custom_context

# and decorate :
# @with_custom_context
"""

import functools

import click


def with_custom_context(func):
    """Decorator to modify the context of a Typer command."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        # print(f'[yellow]i[/yellow] Context `params`: {ctx.params}')
        params = ctx.params
        params.update(ctx.parent.params)
        params["command"] = ctx.info_name
        # print(f'[yellow]i[/yellow] Context parameters : {params}')
        # print("[yellow]i[/yellow] Executing callback_generate_datetime_series()")
        # print(f'  Input [yellow]timestamps[/yellow] : {timestamps}')
        # print(f'Context : {ctx.params}')
        ctx.meta["function_trace"] = ctx.params.get("function_trace", []) + [
            func.__name__
        ]
        # print(ctx.meta)

        return func(*args, **kwargs)

    return wrapper
