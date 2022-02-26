from functools import wraps
from typing import Any, Callable

from tiktokpy.utils.logger import logger


def login_required(empty_result: Any = None):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            async def empty():
                return empty_result

            self_ = args[0]

            if not getattr(self_, "is_logged_in", False):
                logger.error(
                    f'😡 You cannot use function "{func.__name__}" without login! '
                    'Run "tiktokpy login" first and do login',
                )
                return empty()

            return func(*args, **kwargs)

        return wrapper

    return decorator
