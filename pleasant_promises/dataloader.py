from inspect import isgeneratorfunction

from promise import Promise, is_thenable

from promise.dataloader import DataLoader as BaseDataLoader

from .core import genfunc_to_prom, promise_from_generator


class Dataloader(BaseDataLoader):
    """
        Allows using generator syntax in batch_load, or returning non-promises from batch_load
    """

    # shortcut for instance methods to turn generator instances into promises
    def batch_load_fn(self, keys):
        func = self.batch_load
        if isgeneratorfunction(func):
            func = genfunc_to_prom(func)

        result = func(keys)

        if not is_thenable(result):
            # batch_load_fn must always return a promise
            return Promise.resolve(result)

        return result

    def batch_load(self, keys):
        raise NotImplementedError("must override batch_load, did you use batch_load_fn?")


class SingletonDataLoader(Dataloader):
    """
    Factory for creating composable dataloaders
    must pass a dict-like instance cache to the constructor
    """

    dataloader_instance_cache = None

    def __new__(cls, dataloader_instance_cache):
        if cls not in dataloader_instance_cache:
            dataloader_instance_cache[cls] = super().__new__(cls)
        loader = dataloader_instance_cache[cls]
        assert isinstance(loader, cls)
        return loader

    def __init__(self, dataloader_instance_cache):
        if self.dataloader_instance_cache != dataloader_instance_cache:
            self.dataloader_instance_cache = dataloader_instance_cache
            super().__init__()

