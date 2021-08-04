import typing
import inspect
import collections


def extract_docs(patcher, boilerplate_args=None):
    inputs = collections.OrderedDict()
    function_init = patcher.__init__
    node_data = {"patcher": patcher}

    signature = inspect.signature(function_init)
    for name, parameter in signature.parameters.items():
        if name == "self":
            continue
        inputs[name] = {"name": name}
        if isinstance(parameter.default, (str, float, int, bool)):
            inputs[name]["default"] = parameter.default

    type_hints = typing.get_type_hints(function_init)
    for name, socket_data in inputs.items():
        type_hint = type_hints.get(name, None)
        if type_hint is None: # The argument is not type-hinted. (Or hinted to None ??)
            continue
        if isinstance(type_hint, typing._UnionGenericAlias):
            inputs[name]["type"] = [t.__name__ for t in typing.get_args(type_hint)]
        else:
            inputs[name]["type"] = type_hint.__name__

    description = ""
    doc = function_init.__doc__
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
            elif i >= 2:
                description += line
            
        node_data["description"] = description.strip()
    node_data["inputs"] = inputs

    if boilerplate_args is not None:
        for arg in boilerplate_args: # Remove boilerplate arguments
            node_data["inputs"].pop(arg, None)
    return node_data

