import functools
import inspect

from promise import is_thenable


def genfunc_to_prom(func):
    """
    turns a function returning a generator into a function returning a promise
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        generator = func(*args, **kwargs)
        if not inspect.isgenerator(generator):
            return generator

        return promise_from_generator(generator)

    return wrapper


def promise_from_generator(generator):
    """
    assumes the generator is not yet started
    """
    try:
        first_val = next(generator)
    except StopIteration as e:
        next_val = e.value
        return next_val

    return _ongoing_gen_to_prom(generator, first_val)


def _ongoing_gen_to_prom(generator, current_val=None):
    """
    recursive helper
    """
    if inspect.isgenerator(current_val):
        current_val = promise_from_generator(current_val)
    if not is_thenable(current_val):
        # this must be the final return
        return current_val

    def resolve_next(resolved_current):
        try:
            next_val = generator.send(resolved_current)
        except StopIteration as e:
            next_val = e.value
            return next_val

        return _ongoing_gen_to_prom(generator, next_val)

    return current_val.then(resolve_next)
