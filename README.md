# Pleasant python promises

Python promises are a thing, really! But they get ugly quickly. This package lets you handle promises using generator syntax.

Here's what using 3 sequential promises looks like without this package:

```python
def resolve_greatgrandparent(person,info):
    parent_prom = person_loader.load(person.parent_id)
    def handle_parent(parent):
        grandparent_prom = person_loader.load(parent.parent_id)

        def handle_grandparent(grandparent):
            return person_loader.load(grandparent.parent_id)

        return grandparent_prom.then(handle_grandparent)

    return parent_prom.then(handle_parent)

```

And now with this package,


```python
from pleasant_promises import genfunc_to_prom

@genfunc_to_prom
def resolve_greatgrandparent_name(person,info):
    parent = await person_loader.load(person.parent_id)
    grandparent = await person_loader.load(parent.parent_id)
    great_grandparent = await person_loader.load(grandparent.parent_id)
    return great_grandparent
```

## Usage with Graphql/Graphene

If you're using promises, you're probably also using graphene or at least graphql. There are a few other helpers in here to help with your graphql schema,

### Dataloaders

This package has a useful subclass wrapper of the promise package's `Dataloader`. You can overload its `batch_load` method with a generator function. This is useful if you want call another dataloader within batch_load. This class will also convert non-promise values to promises, which is required by the API we're wrapping. 

```python

from pleasant_promises.dataloader import Dataloader

class GrandparentLoader(DataLoader):
    def batch_load(self,keys):
        parents = await person_loader.load_many(keys)
        grandparents = await person_loader.load_many(parent.parent_id for parent in parents)
        # ...
```

You'll still have to decorate other dataloader methods with `@genfunc_to_prom`, though:

```python
from pleasant_promises import genfunc_to_prom

class GrandparentLoader(DataLoader):
    @genfunc_to_prom
    def get_grandparent_for_single_key(self,key):
        parent = await person_loader.load(key)
        return await person_loader.load(parent.parent_id)

    def batch_load(self,keys):
        return Promise.all([self.get_grandparent_for_single_key(key) for key in keys])
```



### Graphene middleware

Without the middleware, you'll have to decorate all your resolvers that want to use the generator syntax. 

```python
from pleasant_promises import genfunc_to_prom

class MyPersonType(graphene.ObjectType):
    # ...
    @genfunc_to_prom
    def resolve_grandparent(self,info):
        parent = await person_loader.load(person.parent_id)
        grandparent = await person_loader.load(parent.parent_id)
        return grandparent

```

To avoid repeating this decorator on all your resolvers, use our pleasant middleware

```python
from pleasant_promises.graphene import promised_generator_middleware


my_graphene_schema.execute('THE QUERY', middleware=[promised_generator_middleware])


```