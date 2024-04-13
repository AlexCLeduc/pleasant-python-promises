from promise import is_thenable, Promise

from pleasant_promises.core import genfunc_to_prom


def test_genfunc_to_promise():

    def promfunc(x):
        return Promise.resolve(x * 2)

    @genfunc_to_prom
    def genfunc(x):
        # return 4x
        y = yield promfunc(x)
        return y * 2

    prom = genfunc(5)
    assert is_thenable(prom)
    assert prom.get() == 20


def test_regular_func_to_promise():
    """
    For non-generator functions returning regular values,
    the decorated func should return the value directly
    """

    @genfunc_to_prom
    def func(x):
        return x * 2

    val = func(5)
    assert not is_thenable(val)
    assert val == 10


def test_regular_func_returning_prom():
    def promfunc(x):
        return Promise.resolve(x * 2)

    @genfunc_to_prom
    def func(x):
        return promfunc(x)

    val = func(5)
    assert is_thenable(val)
    assert val.get() == 10
