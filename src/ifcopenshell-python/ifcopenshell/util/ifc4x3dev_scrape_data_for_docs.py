# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 @Andrej730
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

try:
    from server import get_resource_path, resource_documentation_builder, process_markdown, R
except ModuleNotFoundError as e:
    print(
        "ERROR. Failed to import `server.py`.\n"
        "Make sure you run this script from `/code` folder of https://github.com/buildingSMART/IFC4.3.x-development\n"
    )
    raise e

import itertools
import operator
import json
import ifcopenshell
from collections import Counter
from bs4 import BeautifulSoup
from typing import Any, Union


# Hacky modified functions from server.py to make parser work
def get_definition_from_md(resource: str, mdc: str) -> str:
    # Only match up to the first h2
    lines = []
    for line in mdc.split("\n"):
        if line.startswith("## "):
            break
        if line.startswith("### "):
            words = line.split(" ")
            line = " ".join((words[0], "", *words[1:]))
        lines.append(line)
    mdc = "\n".join(lines)
    mdc_splitted = mdc.split("\n\n")
    return mdc_splitted[1] if len(mdc_splitted) > 1 else ""


def get_type_values(resource: str, mdc: str) -> dict[str, Any]:
    values = R.type_values.get(resource)
    if not values:
        return
    has_description = values[0] == values[0].upper()
    if has_description:
        soup = BeautifulSoup(process_markdown(resource, mdc), features="lxml")
        described_values = []
        for value in values:
            description = None
            for h in soup.findAll("h3"):
                if h.text != value:
                    continue
                description = BeautifulSoup(features="lxml")
                for sibling in h.find_next_siblings():
                    if sibling.name == "h3":
                        break
                    description.append(sibling)
                description = str(description)
            described_values.append({"name": value, "description": description})
        values = described_values
    return {"number": 0, "has_description": has_description, "schema_values": values}


def get_attributes_keep_md(resource, builder):
    attrs = builder.attributes
    supertype_counts = Counter()
    supertype_counts.update([a[0] for a in attrs])
    attrs = [a[1:] for a in attrs]
    supertype_counts = list(supertype_counts.items())[::-1]
    insertion_points = [0] + list(itertools.accumulate(map(operator.itemgetter(1), supertype_counts[::-1])))[:-1]
    group_data = supertype_counts[::-1]

    groups = []
    for i, attr in enumerate(attrs):
        if i in insertion_points:
            name, total_attributes = group_data[insertion_points.index(i)]
            group = {
                "name": name,
                "attributes": [],
                "is_inherited": insertion_points[-1] != i,
                "total_attributes": total_attributes,
            }
            groups.append(group)

        attribute = {
            "number": attr[0],
            "name": attr[1],
            "type": attr[2][0] if isinstance(attr[2], list) else attr[2],
            "formal": attr[2][1] if isinstance(attr[2], list) else None,
            # @nb we're not really talking about markdown anymore
            # since the new attribute parser operates on a converted
            # dom, but it appears to work nonetheless.
            "description": attr[3],
            "is_inverse": not attr[0],
        }
        if attribute["name"] == "PredefinedType" and not attribute["description"]:
            description = "A list of types to further identify the object. Some property sets may be specifically applicable to one of these types."
            if "Type" not in group["name"]:
                description += "\n> NOTE  If the object has an associated IfcTypeObject with a _PredefinedType_, then this attribute shall not be used."
            attribute["description"] = description
        group["attributes"].append(attribute)

    total_inherited_attributes = sum([g["total_attributes"] for g in groups if g["is_inherited"]])

    inherited_groups_with_attributes = [g for g in groups if g["is_inherited"] and g["total_attributes"]]
    if inherited_groups_with_attributes:
        inherited_groups_with_attributes[-1]["is_last_inherited_group"] = True

    return {
        "number": None,
        "groups": groups,
        "total_inherited_attributes": total_inherited_attributes,
    }


# -------------------------

# Temporary fix for https://github.com/buildingSMART/IFC4.3.x-development/issues/754.
_original_get_resource_path = get_resource_path


def get_resource_path(resource: str, abort_on_error=False) -> Union[str, None]:
    md = _original_get_resource_path(resource, abort_on_error)
    if md and resource == "IfcURIReference":
        md = md.replace("IfcMeasureResource", "IfcExternalReferenceResource")
    return md


def get_description_json(resource: str) -> str:
    md = get_resource_path(resource, abort_on_error=False)
    if not md:
        raise Exception(f"No resource path found for '{resource}'.")
    mdc = open(md, "r", encoding="utf-8").read()
    description = get_definition_from_md(resource, mdc)
    return description


def get_attributes_json(resource):
    builder = resource_documentation_builder(resource)
    attrs = get_attributes_keep_md(resource, builder)
    if not attrs["groups"]:
        return []
    attrs = [a for a in attrs["groups"] if a["name"] == resource]
    if not attrs:
        return []

    return attrs[0]["attributes"]


def get_predefined_type_values_json(resource):
    md = get_resource_path(resource, abort_on_error=False)
    if not md:
        raise Exception(f"No resource path found for '{resource}'.")
    mdc = open(md, "r", encoding="utf-8").read()
    return get_type_values(resource, mdc)["schema_values"]


def save_entities_data(entities: list[str]) -> None:
    entities_description = dict()
    for entity in entities:
        entity_data = dict()

        try:
            entity_data["description"] = get_description_json(entity)
        except Exception as e:
            md = get_resource_path(entity, abort_on_error=False)
            if md:
                print(f"server returned markdown file path ('{md}') but there was some other parsing error, see below.")
                raise e
            print(
                f"WARNING. Cannot find resource path for `{entity}` in DEV DOCUMENTATION even though it's present in ifcopenshell schema. It will be skipped."
            )
            continue

        attrs = get_attributes_json(entity)
        attributes_data = dict()
        predefined_types_data = dict()
        for a in attrs:
            if a["name"] == "PredefinedType":
                predefined_type_name_enum = a["type"].split()[-1]
                predef_values = get_predefined_type_values_json(predefined_type_name_enum)
                for v in predef_values:
                    description = v["description"]
                    description = description.strip() if description else ""
                    if description:
                        description = BeautifulSoup(description, features="lxml").find("p").text
                    predefined_types_data[v["name"]] = description
                continue

            description = a["description"]
            description = description.strip() if description else ""
            if description:
                description = BeautifulSoup(description, features="lxml").find("p").text
            attributes_data[a["name"]] = description
        entity_data["attributes"] = attributes_data
        entity_data["predefined_types"] = predefined_types_data
        entities_description[entity] = entity_data

    with open("entities_description.json", "w") as fo:
        json.dump(entities_description, fo, sort_keys=True, indent=4)


if __name__ == "__main__":
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4X3_ADD2")
    entities: list[str] = [e.name() for e in schema.declarations()]
    save_entities_data(entities)
