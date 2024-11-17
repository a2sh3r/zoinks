import functools


def requires_lock(lock_name):
    def decorator(func):
        func._requires_lock = lock_name

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def guards_variable(var_name):
    def decorator(func):
        if not hasattr(func, '_guards_variables'):
            func._guards_variables = set()
        func._guards_variables.add(var_name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def shared_variable(var_name):
    def decorator(func):
        if not hasattr(func, '_shared_variables'):
            func._shared_variables = set()
        func._shared_variables.add(var_name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
