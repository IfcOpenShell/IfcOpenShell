import json
import numpy
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
            listener(usecase_path, ifc_file, settings)

        if None in registered_ifcs and ifc_key != registered_ifcs[None]:
            global_key = registered_ifcs[None]
            for listener in pre_listeners.get(".".join([global_key, usecase_path]), []):
                listener(usecase_path, ifc_file, settings)

    def serialise_entity_instance(entity):
        return {"cast_type": "entity_instance", "value": entity.id(), "Name": getattr(entity, "Name", None)}

    vcs_settings = settings.copy()
    for key, value in settings.items():
        if isinstance(value, ifcopenshell.entity_instance):
            vcs_settings[key] = serialise_entity_instance(value)
        elif isinstance(value, numpy.ndarray):
            vcs_settings[key] = {"cast_type": "ndarray", "value": value.tolist()}
        elif isinstance(value, list) and value and isinstance(value[0], ifcopenshell.entity_instance):
            vcs_settings[key] = [serialise_entity_instance(i) for i in value]
    if "add_representation" in usecase_path:
        pass
        # print(ifc_key, usecase_path, "{ ... settings too complex right now ... }")
    elif "owner." in usecase_path:
        pass
    else:
        pass
        # print(vcs_settings)
        # try:
        #    print(ifc_key, usecase_path, json.dumps(vcs_settings))
        # except:
        #    print(ifc_key, usecase_path, vcs_settings)

    importlib.import_module(f"ifcopenshell.api.{usecase_path}")
    module, usecase = usecase_path.split(".")
    usecase_class = getattr(getattr(getattr(ifcopenshell.api, module), usecase), "Usecase")

    if ifc_file:
        result = usecase_class(ifc_file, **settings).execute()
    else:
        result = usecase_class(**settings).execute()

    if should_run_listeners:
        for listener in post_listeners.get(".".join([ifc_key, usecase_path]), []):
            listener(usecase_path, ifc_file, settings)

        if None in registered_ifcs and ifc_key != registered_ifcs[None]:
            global_key = registered_ifcs[None]
            for listener in post_listeners.get(".".join([global_key, usecase_path]), []):
                listener(usecase_path, ifc_file, settings)

    return result


def add_pre_listener(usecase_path, ifc_file, callback):
    """Add a pre listener
    There are 2 kind of listeners:
    when ifc file is defined the listener will only run for specified file
    when ifc file is None, the listener will run globally only based on usecase
    :param usecase_path: string, ifcopenshell api use case path
    :param ifc_file: ifc file object or None for global listener
    :param callback: callback function
    :return: ifc_key, uuid of listener, this is the prefix only, postfix is the usecase_path dot separated.
    """
    ifc_key = registered_ifcs.setdefault(ifc_file, ifcopenshell.guid.new())
    pre_listeners.setdefault(".".join([ifc_key, usecase_path]), set()).add(callback)
    return ifc_key


def add_post_listener(usecase_path, ifc_file, callback):
    """Add a post listener
    There are 2 kind of listeners:
    when ifc file is defined the listener will only run for specified file
    when ifc file is None, the listener will run globally only based on usecase
    :param usecase_path: string, ifcopenshell api use case path
    :param ifc_file: ifc file object or None for global listener
    :param callback: callback function
    :return: ifc_key, uuid of listener, this is the prefix only, postfix is the usecase_path dot separated.
    """
    ifc_key = registered_ifcs.setdefault(ifc_file, ifcopenshell.guid.new())
    post_listeners.setdefault(".".join([ifc_key, usecase_path]), set()).add(callback)
    return ifc_key


def remove_pre_listener(callback, usecase_path=""):
    """Remove a pre listener
    :param callback: callback function to remove
    :param usecase_path: string, optional, ifcopenshell api usecase path, may be prefixed with ifc_key, dot separated.
    :return:
    """
    for listener_key, callbacks in pre_listeners.items():
        if not listener_key.endswith(usecase_path):
            continue
        to_remove = set()
        for fun in callbacks:
            if fun == callback:
                to_remove.add(callback)
        for callback in to_remove:
            pre_listeners[listener_key].remove(callback)


def remove_post_listener(callback, usecase_path=""):
    """Remove a post listener
    :param callback: callback function to remove
    :param usecase_path: string, optional ifcopenshell api usecase path, may be prefixed with ifc_key, dot separated.
    :return:
    """
    for listener_key, callbacks in post_listeners.items():
        if not listener_key.endswith(usecase_path):
            continue
        to_remove = set()
        for fun in callbacks:
            if fun == callback:
                to_remove.add(callback)
        for callback in to_remove:
            post_listeners[listener_key].remove(callback)


def remove_all_listeners():
    registered_ifcs.clear()
    pre_listeners.clear()
    post_listeners.clear()
