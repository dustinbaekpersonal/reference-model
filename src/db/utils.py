from functools import wraps


def raise_if_not_connected(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._conn:
            raise RuntimeError("Not connected to database")
        return func(self, *args, **kwargs)

    return wrapper
