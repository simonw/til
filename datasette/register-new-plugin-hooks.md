# Registering new Datasette plugin hooks by defining them in other plugins

I'm experimenting with a Datasette plugin that itself adds new plugin hooks which other plugins can then interact with.

It's called [datasette-low-disk-space-hook](https://github.com/simonw/datasette-low-disk-space-hook), and it adds a new plugin hook called `low_disk_space(datasette)`, defined in the [datasette_low_disk_space_hook/hookspecs.py](https://github.com/simonw/datasette-low-disk-space-hook/blob/0.1a0/datasette_low_disk_space_hook/hookspecs.py) module.

The hook is registered by this code in [datasette_low_disk_space_hook/\_\_init\_\_.py](https://github.com/simonw/datasette-low-disk-space-hook/blob/0.1a0/datasette_low_disk_space_hook/__init__.py)

```python
from datasette.utils import await_me_maybe
from datasette.plugins import pm
from . import hookspecs

pm.add_hookspecs(hookspecs)
```
This imports the plugin manager directly from Datasette and uses it to add the new hooks.

I was worried that the `pm.add_hookspects(hookspecs)` line was not guaranteed to be executed if that module had not been imported.

It turns out that having this `entrpoints=` line in [setup.py](https://github.com/simonw/datasette-low-disk-space-hook/blob/0.1a0/setup.py) is enough to ensure that the module is imported and the `pm.add_hookspecs()` line is executed:

```python
from setuptools import setup

setup(
    name="datasette-low-disk-space-hook",
    # ...
    entry_points={"datasette": ["low_disk_space_hook = datasette_low_disk_space_hook"]},
    # ...
)
```
