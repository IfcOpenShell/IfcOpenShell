import json
import numpy
import importlib
import ifcopenshell
import ifcopenshell.api


pre_listeners = {}
post_listeners = {}


def run(usecase_path, ifc_file=None, should_run_listeners=True, **settings):
    if should_run_listeners:
        for listener in pre_listeners.get(usecase_path, {}).values():
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
        # print(usecase_path, "{ ... settings too complex right now ... }")
    elif "owner." in usecase_path:
        pass
    else:
        pass
        # print(vcs_settings)
        # try:
        #    print(usecase_path, json.dumps(vcs_settings))
        # except:
        #    print(usecase_path, vcs_settings)

    importlib.import_module(f"ifcopenshell.api.{usecase_path}")
    module, usecase = usecase_path.split(".")
    usecase_class = getattr(getattr(getattr(ifcopenshell.api, module), usecase), "Usecase")

    if ifc_file:
        result = usecase_class(ifc_file, **settings).execute()
    else:
        result = usecase_class(**settings).execute()

    if should_run_listeners:
        for listener in post_listeners.get(usecase_path, {}).values():
            listener(usecase_path, ifc_file, settings)

    return result


def add_pre_listener(usecase_path, name, callback):
    """Add a pre listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function
    """
    pre_listeners.setdefault(usecase_path, {})[name] = callback


def add_post_listener(usecase_path, name, callback):
    """Add a post listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function
    """
    post_listeners.setdefault(usecase_path, {})[name] = callback


def remove_pre_listener(usecase_path, name, callback):
    """Remove a pre listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function
    """
    pre_listeners.get(usecase_path, {}).pop(name, None)


def remove_post_listener(usecase_path, name, callback):
    """Remove a post listener

    :param usecase_path: string, ifcopenshell api use case path
    :param name: string, name of listener
    :param callback: callback function
    """
    post_listeners.get(usecase_path, {}).pop(name, None)


def remove_all_listeners():
    pre_listeners.clear()
    post_listeners.clear()
