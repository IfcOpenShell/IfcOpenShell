import importlib
import ifcopenshell
import ifcopenshell.api


registered_ifcs = {}
pre_listeners = {}
post_listeners = {}


def run(usecase_path, ifc_file=None, should_run_listeners=True, **settings):
    ifc_key = registered_ifcs.setdefault(ifc_file, ifcopenshell.guid.new())

    if should_run_listeners:
        for listener in pre_listeners.get(".".join([ifc_key, usecase_path]), []):
            listener(usecase_path, ifc_file, **settings)
    importlib.import_module(f"ifcopenshell.api.{usecase_path}")
    module, usecase = usecase_path.split(".")
    usecase_class = getattr(getattr(getattr(ifcopenshell.api, module), usecase), "Usecase")

    if ifc_file:
        result = usecase_class(ifc_file, **settings).execute()
    else:
        result = usecase_class(**settings).execute()

    if should_run_listeners:
        for listener in post_listeners.get(".".join([ifc_key, usecase_path]), []):
            listener(usecase_path, ifc_file, **settings)
    return result


def add_pre_listener(usecase_path, ifc_file, callback):
    ifc_key = registered_ifcs.setdefault(ifc_file, ifcopenshell.guid.new())
    pre_listeners.setdefault(".".join([ifc_key, usecase_path]), set()).add(callback)

def add_post_listener(usecase_path, ifc_file, callback):
    ifc_key = registered_ifcs.setdefault(ifc_file, ifcopenshell.guid.new())
    post_listeners.setdefault(".".join([ifc_key, usecase_path]), set()).add(callback)
    
def remove_pre_listener(callback):
    for ifc_key, callbacks in pre_listeners.items():
        for fun in callbacks:
            if fun == callback:
                pre_listeners[ifc_key].remove(callback)
                return

def remove_post_listener(callback):
    for ifc_key, callbacks in post_listeners.items():
        for fun in callbacks:
            if fun == callback:
                post_listeners[ifc_key].remove(callback)
                return

def remove_all_listeners():
    registered_ifcs.clear()
    pre_listeners.clear()
    post_listeners.clear()


