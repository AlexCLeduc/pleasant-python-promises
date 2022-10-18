import graphene
from inspect import isgenerator

from promise import is_thenable

from .core import promise_from_generator

def promised_generator_middleware(next, root, info, **kwargs):
    next_val = next(root, info, **kwargs)

    if not is_thenable(next_val):
        return next_val

    def handler(resolved_next_val):
        if isgenerator(resolved_next_val):
            prom = promise_from_generator(resolved_next_val)
            return prom
        return resolved_next_val

    return next_val.then(handler)
