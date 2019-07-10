from sys import gettrace
from functools import wraps


def debug_only(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if gettrace():
            func(*args, **kwargs)
    return func_wrapper
