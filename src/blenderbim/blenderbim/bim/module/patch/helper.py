import typing
import inspect
import collections
import importlib
from types import ModuleType

def extract_docs(
    module: ModuleType,
    submodule_name: str,
    cls_name: str,
    method_name: str,
    boilerplate_args : typing.Iterable[str]=None):
    """Extract class docstrings and method arguments
    
    :param module: Parent module from which to extract the submodule class
    :param submodule_name: Submodule from which to extract the class
    :param cls_name: Class from which to extract the docstring and method arguments
    :param method_name: Class Method name from which to extract arguments
    :param boilerplate_args: String iterable containing arguments that shall not be parsed
    """
    spec = importlib.util.spec_from_file_location(submodule_name, f"{module.__path__[0]}/recipes/{submodule_name}.py")
    submodule = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(submodule)
        try:
            return _extract_docs(getattr(submodule, cls_name), method_name, boilerplate_args)
        except AttributeError as e:
            print(e)
    except ModuleNotFoundError as e:
        print("Error : " + str(e) + "in " + str(submodule))

def _extract_docs(cls, method_name, boilerplate_args):
    inputs = collections.OrderedDict()
    method = getattr(cls, method_name)
    node_data = {"class": cls}

    signature = inspect.signature(method)
    for name, parameter in signature.parameters.items():
        if name == "self":
            continue
        inputs[name] = {"name": name}
        if isinstance(parameter.default, (str, float, int, bool)):
            inputs[name]["default"] = parameter.default

    type_hints = typing.get_type_hints(method)
    for name, socket_data in inputs.items():
        type_hint = type_hints.get(name, None)
        if type_hint is None: # The argument is not type-hinted. (Or hinted to None ??)
            continue
        if isinstance(type_hint, typing._UnionGenericAlias):
            inputs[name]["type"] = [t.__name__ for t in typing.get_args(type_hint)]
        else:
            inputs[name]["type"] = type_hint.__name__

    description = ""
    doc = method.__doc__
    if doc is not None:
        for i, line in enumerate(doc.split("\n")):
            line = line.strip()
            if i == 0:
                node_data["name"] = line
            elif line.startswith(":return:"):
                node_data["output"] = {"name": line.split(":")[2].strip(), "description": line.split(":")[3].strip()}
            elif line.startswith(":param"):
                param_name = line.split(":")[1].strip().replace("param ", "")
                inputs[param_name]["description"] = line.split(":")[2].strip()
            elif i == 2:
                description += line
            elif i > 2:
                description += "\n" + line
            
        node_data["description"] = description.strip()
    node_data["inputs"] = inputs

    if boilerplate_args is not None:
        for arg in boilerplate_args: # Remove boilerplate arguments
            node_data["inputs"].pop(arg, None)
    return node_data

