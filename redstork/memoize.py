import functools

def memoize(func):
    cache = {}

    @functools.wraps(func)
    def f(*args, **kvargs):
        if len(kvargs) == 1:
            raise RuntimeError('Memoize does not support keyword args')
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return f