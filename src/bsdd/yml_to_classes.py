import yaml
import sys
from pathlib import Path
from typing import Any


type_to_python_type = {
    "string": "str",
    "boolean": "bool",
    "array": "list",
    "integer": "int",
}


def get_python_type(prop_data: dict[str, Any]) -> str:
    prop_type = prop_data.get("type")

    if prop_type is None:
        ref = format_class(prop_data["$ref"].split("/")[-1])
        return ref
    elif prop_type == "number" and prop_data["format"] == "double":
        python_type = "float"
    else:
        python_type = type_to_python_type[prop_type]

    if python_type == "list":
        array_type = get_python_type(prop_data["items"])
        return f"{python_type}[{array_type}]"
    return python_type


def format_class(class_str: str) -> str:
    if "." not in class_str:
        return class_str
    class_name, version = class_str.split(".")
    return f"{class_name}{version.upper()}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'Usage: python {Path(__file__).name} "path/to/bSDD OpenAPI.yaml"')
        print(
            ".yml file available in https://github.com/buildingSMART/bSDD/blob/master/Documentation/bSDD%20OpenAPI.yaml"
        )
        exit()

    path = sys.argv[1]
    with open(path, "r") as file:
        yaml_file = yaml.safe_load(file)

    class_strings: dict[str, str] = {}
    for schema_name, schema_data in yaml_file["components"]["schemas"].items():
        props = schema_data.get("properties", {})
        if not props:
            continue
        class_name = format_class(schema_name)
        class_header = f"class {class_name}(TypedDict):"
        required = schema_data.get("required", [])
        props_str = ""
        for prop_name, prop_data in props.items():
            python_type = get_python_type(prop_data)
            if prop_name not in required:
                python_type = f"NotRequired[{python_type}]"
            props_str += f"    {prop_name}: {python_type}\n"
        class_strings[class_header] = props_str

    # Sort classes according to bsdd.py to reduce git diff noise.
    bsdd_contents = Path(__file__).with_name("bsdd.py").read_text()
    # Skipping not yet implemented classes for now.
    filtered_classes = list(filter(lambda x: x in bsdd_contents, class_strings))
    for class_header in sorted(
        filtered_classes,
        key=lambda x: bsdd_contents.index(x),
    ):
        print(class_header)
        print(class_strings[class_header])
    print(f"{len(filtered_classes)} classes printed ({len(class_strings)-len(filtered_classes)} skipped).")
