import functools


def debug_if_needed(app):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if app.debug_mode:
                from devtools import debug

                debug(locals())
            result = func(*args, **kwargs)
            if app.debug_mode:
                debug(locals())
            #     debug(result)
            return result

        return wrapper

    return decorator
