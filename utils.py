import logging
from time import sleep


def retry_connect(_func=None, *, retries=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for retry in range(retries):
                res = func(*args, **kwargs)
                if res.status_code == 200:
                    return res.json()
                else:
                    logging.info(
                        f"Request failed {res.status_code}: {res.json()}, retry number: {retry + 1}"
                    )
                    if res.status_code == 429:
                        sleep(5)
            return None

        return wrapper

    return decorator(_func) if _func else decorator


def coroutine(func):
    def wrapper(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return wrapper
