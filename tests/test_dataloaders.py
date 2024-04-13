import pytest
from promise import Promise


from unittest.mock import MagicMock

from pleasant_promises.dataloader import SingletonDataLoader


def test_loader_singleton_behavioru():
    class TestDataloader(SingletonDataLoader):
        def batch_load(self, keys):
            return [f"test_{key}" for key in keys]

    cache1 = {}
    cache2 = {}
    assert TestDataloader(cache1) is TestDataloader(cache1)
    assert TestDataloader(cache1) is not TestDataloader(cache2)


def test_basic_loader(dataloader_test):

    dataloader_cache = {}

    spy = MagicMock()

    class TestDataloader(SingletonDataLoader):
        def batch_load(self, keys):
            spy(keys)
            return [f"test_{key}" for key in keys]

    loader = TestDataloader(dataloader_cache)

    loader.load(1)
    loader.load(2)
    loader.load(3)

    assert loader.load(1).get() == "test_1"
    assert loader.load(2).get() == "test_2"
    assert loader.load(3).get() == "test_3"
    assert spy.call_count == 1


def test_loader_that_returns_promise(dataloader_test):
    cache = {}

    spy = MagicMock()

    class TestDataloader(SingletonDataLoader):
        def batch_load(self, keys):
            spy(keys)
            return Promise.resolve([f"test_{key}" for key in keys])

    loader = TestDataloader(cache)

    loader.load(1)
    loader.load(2)
    loader.load(3)

    assert loader.load(1).get() == "test_1"
    assert loader.load(2).get() == "test_2"
    assert loader.load(3).get() == "test_3"
    assert spy.call_count == 1


def test_loader_that_returns_generator(dataloader_test):
    cache = {}

    spy = MagicMock()

    class TestDataloader(SingletonDataLoader):
        def batch_load(self, keys):
            spy(keys)
            prom = Promise.resolve([f"test_{key}" for key in keys])
            yield prom
            return prom.get()

    loader = TestDataloader(cache)

    loader.load(1)
    loader.load(2)
    loader.load(3)

    assert loader.load(1).get() == "test_1"
    assert loader.load(2).get() == "test_2"
    assert loader.load(3).get() == "test_3"
    assert spy.call_count == 1


def test_composed_loaders(dataloader_test):
    cache = {}

    loader1_spy = MagicMock()
    loader2_spy = MagicMock()

    class Loader1(SingletonDataLoader):
        def batch_load(self, keys):
            loader1_spy(keys)
            return [f"loader1_{key}" for key in keys]

    class Loader2(SingletonDataLoader):
        def batch_load(self, keys):
            loader2_spy(keys)
            loader1_vals = yield Loader1(self.dataloader_instance_cache).load_many(keys)
            vals_by_key = {key: val for key, val in zip(keys, loader1_vals)}
            return [f"loader2_{key}_{vals_by_key[key]}" for key in keys]

    loader2 = Loader2(cache)

    loader2.load(1)
    loader2.load(2)
    loader2.load(3)

    assert loader2.load(1).get() == "loader2_1_loader1_1"
    assert loader2.load(2).get() == "loader2_2_loader1_2"
    assert loader2.load(3).get() == "loader2_3_loader1_3"

    assert loader1_spy.call_count == 1
    assert loader2_spy.call_count == 1
