import sys
from functools import wraps


def debug_only(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if sys.gettrace():
            func(*args, **kwargs)
    return func_wrapper
