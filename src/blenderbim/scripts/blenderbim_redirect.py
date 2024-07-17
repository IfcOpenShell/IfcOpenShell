import importlib
import bpy
import types
from typing import Any


BBIM = None
MODULE_CACHE = {}


def __getattr__(name: str):
    bbim = find_blenderbim_package()
    return getattr(bbim, name)


class Wrapper:
    def __init__(self, module):
        self.module = module

    def __getattribute__(self, name: str):
        module = object.__getattribute__(self, "module")
        try:
            attr = getattr(module, name)
            return attr
        except AttributeError:
            pass

        # I guess it's a submodule.
        name = f"{module.__name__}.{name}"
        return get_wrapped_module(name)

    def __dir__(self):
        return dir(self.module)


def get_wrapped_module(name: str) -> Wrapper:
    module = MODULE_CACHE.get(name)
    if module:
        return module
    return Wrapper(importlib.import_module(name))


def find_blenderbim_package() -> types.ModuleType:
    global BBIM
    if BBIM is not None:
        return BBIM
    for package_name in bpy.context.preferences.addons.keys():
        if package_name.endswith(".blenderbim"):
            BBIM = Wrapper(importlib.import_module(package_name))
            return BBIM
    raise Exception("blenderbim is not found.")
