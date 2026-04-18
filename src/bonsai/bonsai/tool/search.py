# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import json
from itertools import cycle
from typing import TYPE_CHECKING, Any, Literal, Union

import bpy
import ifcopenshell.guid
import ifcopenshell.util.selector
import lark

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim.prop import BIMFacet

if TYPE_CHECKING:
    from bonsai.bim.module.search.prop import BIMSearchProperties
    from bonsai.bim.prop import BIMFilterGroup


class Search(bonsai.core.tool.Search):
    @classmethod
    def get_search_props(cls) -> BIMSearchProperties:
        return bpy.context.scene.BIMSearchProperties

    @classmethod
    def get_group_query(cls, group: ifcopenshell.entity_instance) -> str:
        return json.loads(group.Description)["query"]

    @classmethod
    def get_group_data(cls, group: ifcopenshell.entity_instance) -> dict:
        return json.loads(group.Description)

    @classmethod
    def import_filter_structure(
        cls,
        filter_structure: list[list[dict[str, Any]]],
        filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup],
    ) -> None:
        filter_groups.clear()

        for group_data in filter_structure:
            if not isinstance(group_data, list):
                continue

            filter_group = filter_groups.add()

            for filter_data in group_data:
                if not isinstance(filter_data, dict):
                    continue

                ifc_filter = filter_group.filters.add()
                ifc_filter.type = filter_data.get("type", "")
                ifc_filter.name = filter_data.get("name", "")
                ifc_filter.value = filter_data.get("value", "")
                ifc_filter.pset = filter_data.get("pset", "")
                ifc_filter.comparison = filter_data.get("comparison", "=")
                filter_mode = filter_data.get("filter_mode", "ADD")
                if filter_mode in ["ADD", "SUBTRACT", "FILTER"]:
                    ifc_filter.filter_mode = filter_mode
                else:
                    ifc_filter.filter_mode = "ADD"

    FilterModule = Union[Literal["search", "csv", "diff", "drawing_include", "drawing_exclude"], str]

    @classmethod
    def get_filter_groups(cls, module: FilterModule) -> bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]:
        if module == "search":
            return cls.get_search_props().filter_groups
        elif module == "csv":
            return tool.Blender.get_csv_props().filter_groups
        elif module == "diff":
            return tool.Blender.get_diff_props().filter_groups
        elif module == "drawing_include":
            assert (scene := bpy.context.scene) and (camera_obj := (scene.camera))
            return tool.Drawing.get_camera_props(camera_obj).include_filter_groups
        elif module == "drawing_exclude":
            assert (scene := bpy.context.scene) and (camera_obj := (scene.camera))
            return tool.Drawing.get_camera_props(camera_obj).exclude_filter_groups
        elif module.startswith("clash"):
            _, clash_set_index, ab, clash_source_index = module.split("_")
            props = tool.Clash.get_clash_props()
            return getattr(props.clash_sets[int(clash_set_index)], ab)[int(clash_source_index)].filter_groups
        assert False, f"Unsupported module: {module}"

    @classmethod
    def import_filter_query(
        cls, query: str, filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]
    ) -> None:
        filter_groups.clear()
        transformer = ImportFilterQueryTransformer(filter_groups)
        transformer.transform(ifcopenshell.util.selector.filter_elements_grammar.parse(query))

    @classmethod
    def export_filter_query(cls, filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]) -> str:
        query = []
        for filter_group in filter_groups:
            filter_group_query = []
            for ifc_filter in filter_group.filters:
                if not ifc_filter.value:
                    continue

                query_part = cls._export_single_filter(ifc_filter)
                if query_part:
                    filter_group_query.append(query_part)

            if filter_group_query:
                query.append(", ".join(filter_group_query))
        return " + ".join(query)

    @classmethod
    def _export_single_filter(cls, ifc_filter: BIMFacet) -> str:
        preferences = tool.Blender.get_addon_preferences()

        if ifc_filter.type == "instance":
            if "bpy.data.texts" in ifc_filter.value:
                data_name = ifc_filter.value.split("bpy.data.texts")[1][2:-2]
                value = bpy.data.texts[data_name].as_string()
            else:
                value = ifc_filter.value

            if preferences.chain_filter_with_set_operations:
                value = value.lstrip("!")
                if ifc_filter.filter_mode == "SUBTRACT":
                    value = f"!{value}"
            return value

        elif ifc_filter.type == "entity":
            value = ifc_filter.value

            if preferences.chain_filter_with_set_operations:
                value = value.lstrip("!")
                if ifc_filter.filter_mode == "SUBTRACT":
                    value = f"!{value}"
            return value
        elif ifc_filter.type == "attribute":
            if not ifc_filter.name:
                return ""
            comparison, value = cls.get_comparison_and_value(ifc_filter)
            return f"{ifc_filter.name}{comparison}{value}"
        elif ifc_filter.type == "type":
            comparison, value = cls.get_comparison_and_value(ifc_filter)
            return f"type{comparison}{value}"
        elif ifc_filter.type == "material":
            comparison, value = cls.get_comparison_and_value(ifc_filter)
            return f"material{comparison}{value}"
        elif ifc_filter.type == "property":
            if not ifc_filter.pset or not ifc_filter.name:
                return ""
            pset = cls.wrap_value(ifc_filter, ifc_filter.pset)
            name = cls.wrap_value(ifc_filter, ifc_filter.name)
            comparison = ifc_filter.comparison
            value = cls.wrap_value(ifc_filter, ifc_filter.value)
            return f"{pset}.{name} {comparison} {value}"
        elif ifc_filter.type == "classification":
            comparison, value = cls.get_comparison_and_value(ifc_filter)
            return f"classification{comparison}{value}"
        elif ifc_filter.type == "location":
            comparison, value = cls.get_comparison_and_value(ifc_filter)
            return f"location{comparison}{value}"
        elif ifc_filter.type == "group":
            comparison, value = cls.get_comparison_and_value(ifc_filter)
            return f"group{comparison}{value}"
        elif ifc_filter.type == "parent":
            comparison, value = cls.get_comparison_and_value(ifc_filter)
            return f"parent{comparison}{value}"
        elif ifc_filter.type == "query":
            keys = cls.wrap_value(ifc_filter, ifc_filter.name)
            comparison = ifc_filter.comparison or "="
            value = cls.wrap_value(ifc_filter, ifc_filter.value)
            return f"query:{keys}{comparison}{value}"
        return ""

    @classmethod
    def execute_filter_groups(
        cls, filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]
    ) -> set[ifcopenshell.entity_instance]:
        """
        Execute filter groups with simplified chaining support.
        Within a single group chain, all filters chain sequentially with ADD/SUBTRACT/FILTER modes.
        Groups are combined with union (same as original " + " behavior).
        """
        preferences = tool.Blender.get_addon_preferences()

        all_group_results: list[set[ifcopenshell.entity_instance]] = []

        for filter_group in filter_groups:
            group_results: set[ifcopenshell.entity_instance] = set()

            for filter_index, ifc_filter in enumerate(filter_group.filters):
                if not ifc_filter.value:
                    continue

                query = cls._export_single_filter(ifc_filter)
                if not query:
                    continue

                if filter_index == 0:
                    mode = "ADD"
                else:
                    if preferences.chain_filter_with_set_operations:
                        mode = ifc_filter.filter_mode
                    else:
                        mode = "FILTER" if group_results else "ADD"

                if mode == "ADD":
                    results = ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), query)
                    group_results.update(results)

                elif mode == "SUBTRACT":
                    if group_results:
                        query_without_prefix = query[1:] if query.startswith("!") else query
                        elements_to_remove = ifcopenshell.util.selector.filter_elements(
                            tool.Ifc.get(), query_without_prefix, elements=group_results
                        )
                        group_results -= elements_to_remove
                    else:
                        results = ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), query)
                        group_results.update(results)

                elif mode == "FILTER":
                    if group_results:
                        results = ifcopenshell.util.selector.filter_elements(
                            tool.Ifc.get(), query, elements=group_results
                        )
                        group_results = results
                    else:
                        results = ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), query)
                        group_results.update(results)

            if group_results:
                all_group_results.append(group_results)

        final_results: set[ifcopenshell.entity_instance] = set()
        for group_results in all_group_results:
            final_results.update(group_results)

        return final_results

    @classmethod
    def execute_filter_groups_from_json(
        cls, data: dict, ifc_file: ifcopenshell.file
    ) -> set[ifcopenshell.entity_instance]:
        """Execute filter groups from JSON data with filter_structure

        This is used by drawing include/exclude to properly handle ADD/SUBTRACT/FILTER modes
        without needing to instantiate Blender property groups.
        """
        filter_structure = data.get("filter_structure", [])

        all_group_results: list[set[ifcopenshell.entity_instance]] = []
        for group_data in filter_structure:
            group_results: set[ifcopenshell.entity_instance] = set()

            for filter_data in group_data:
                filter_mode = filter_data.get("filter_mode", "ADD")
                filter_type = filter_data.get("type", "")
                value = filter_data.get("value", "")

                if not filter_type or not value:
                    continue

                query_part = None
                if filter_type == "entity":
                    query_part = value
                elif filter_type == "attribute":
                    name = filter_data.get("name", "")
                    if not name:
                        continue
                    comparison = filter_data.get("comparison", "=")
                    query_part = f"{name}{comparison}{cls._wrap_json_value(value)}"
                elif filter_type == "property":
                    pset = filter_data.get("pset", "")
                    name = filter_data.get("name", "")
                    if not pset or not name:
                        continue
                    comparison = filter_data.get("comparison", " = ")
                    wrapped_pset = cls._wrap_json_value(pset)
                    wrapped_name = cls._wrap_json_value(name)
                    wrapped_value = cls._wrap_json_value(value)
                    query_part = f"{wrapped_pset}.{wrapped_name} {comparison} {wrapped_value}"
                elif filter_type == "type":
                    query_part = f"type={cls._wrap_json_value(value)}"
                elif filter_type == "material":
                    query_part = f"material={cls._wrap_json_value(value)}"
                elif filter_type == "classification":
                    query_part = f"classification={cls._wrap_json_value(value)}"
                elif filter_type == "location":
                    query_part = f"location={cls._wrap_json_value(value)}"
                elif filter_type == "group":
                    query_part = f"group={cls._wrap_json_value(value)}"
                elif filter_type == "parent":
                    query_part = f"parent={cls._wrap_json_value(value)}"
                elif filter_type == "query":
                    name = filter_data.get("name", "")
                    if not name:
                        continue
                    keys = cls._wrap_json_value(name)
                    comparison = filter_data.get("comparison", "=")
                    wrapped_value = cls._wrap_json_value(value)
                    query_part = f"query:{keys}{comparison}{wrapped_value}"
                elif filter_type == "instance":
                    query_part = value

                if not query_part:
                    continue

                if filter_mode == "FILTER" and group_results:
                    results = ifcopenshell.util.selector.filter_elements(ifc_file, query_part, elements=group_results)
                    group_results = results
                elif filter_mode == "SUBTRACT":
                    results = ifcopenshell.util.selector.filter_elements(ifc_file, query_part)
                    group_results -= results
                else:  # ADD
                    results = ifcopenshell.util.selector.filter_elements(ifc_file, query_part)
                    group_results.update(results)

            if group_results:
                all_group_results.append(group_results)

        final_results: set[ifcopenshell.entity_instance] = set()
        for group_results in all_group_results:
            final_results.update(group_results)

        return final_results

    @classmethod
    def _wrap_json_value(cls, value: str) -> str:
        """Wrap value for use in query string"""
        if value.startswith("/") and value.endswith("/"):
            return value
        elif value in ("NULL", "TRUE", "FALSE"):
            return value
        return '"' + value.replace('"', '\\"') + '"'

    @classmethod
    def get_comparison_and_value(
        cls, ifc_filter: BIMFacet
    ) -> Union[tuple[Literal["!="], str], tuple[Literal["="], str]]:
        if ifc_filter.value.startswith("!="):
            return ("!=", cls.wrap_value(ifc_filter, ifc_filter.value[2:].strip()))
        return ("=", cls.wrap_value(ifc_filter, ifc_filter.value.strip()))

    @classmethod
    def wrap_value(cls, ifc_filter: BIMFacet, value: str) -> str:
        if value.startswith("/") and value.endswith("/"):
            return value
        elif value in ("NULL", "TRUE", "FALSE"):
            return value
        return '"' + value.replace('"', '\\"') + '"'

    @classmethod
    def get_qualitative_palette(cls, theme: str = "tab10") -> cycle:
        if theme == "paired":
            return cycle(
                [
                    (0.651, 0.81, 0.892, 1),
                    (0.121, 0.471, 0.706, 1),
                    (0.699, 0.876, 0.54, 1),
                    (0.199, 0.629, 0.174, 1),
                    (0.983, 0.605, 0.602, 1),
                    (0.89, 0.101, 0.112, 1),
                    (0.989, 0.751, 0.427, 1),
                    (0.986, 0.497, 0.1, 1),
                    (0.792, 0.699, 0.839, 1),
                    (0.414, 0.239, 0.603, 1),
                    (0.993, 0.999, 0.6, 1),
                    (0.693, 0.349, 0.157, 1),
                ]
            )
        # tab10
        return cycle(
            [
                (0.122, 0.467, 0.706, 1),
                (1.00, 0.498, 0.055, 1),
                (0.173, 0.627, 0.173, 1),
                (0.839, 0.153, 0.157, 1),
                (0.580, 0.404, 0.741, 1),
                (0.549, 0.337, 0.294, 1),
                (0.890, 0.467, 0.761, 1),
                (0.498, 0.498, 0.498, 1),
                (0.737, 0.741, 0.133, 1),
                (0.090, 0.745, 0.812, 1),
            ]
        )

    @classmethod
    def interpolate_color(cls, c1, c2, factor):
        return tuple((1 - factor) * x + factor * y for x, y in zip(c1, c2))

    @classmethod
    def get_quantitative_palette(cls, theme: str, value, min_val, max_val):
        if theme == "coolwarm":
            palette = [
                (0.227, 0.298, 0.753),
                (0.282, 0.376, 0.820),
                (0.345, 0.463, 0.886),
                (0.412, 0.545, 0.937),
                (0.482, 0.620, 0.973),
                (0.553, 0.686, 0.992),
                (0.616, 0.741, 0.996),
                (0.686, 0.792, 0.984),
                (0.753, 0.827, 0.961),
                (0.812, 0.851, 0.918),
                (0.865, 0.863, 0.863),
                (0.910, 0.835, 0.792),
                (0.945, 0.792, 0.714),
                (0.965, 0.737, 0.635),
                (0.965, 0.671, 0.553),
                (0.957, 0.604, 0.482),
                (0.929, 0.518, 0.404),
                (0.890, 0.424, 0.329),
                (0.839, 0.322, 0.263),
                (0.773, 0.196, 0.200),
                (0.702, 0.012, 0.149),
            ]
        elif theme == "spectral":
            palette = [
                (0.620, 0.004, 0.259),
                (0.718, 0.114, 0.282),
                (0.827, 0.235, 0.306),
                (0.894, 0.333, 0.286),
                (0.957, 0.427, 0.263),
                (0.973, 0.557, 0.322),
                (0.988, 0.675, 0.376),
                (0.992, 0.776, 0.459),
                (0.996, 0.878, 0.545),
                (0.996, 0.937, 0.647),
                (0.996, 0.996, 0.743),
                (0.949, 0.980, 0.671),
                (0.902, 0.961, 0.596),
                (0.780, 0.910, 0.620),
                (0.663, 0.863, 0.643),
                (0.537, 0.812, 0.643),
                (0.400, 0.761, 0.647),
                (0.294, 0.643, 0.694),
                (0.196, 0.525, 0.737),
                (0.286, 0.412, 0.682),
                (0.369, 0.310, 0.635),
            ]

        elif theme == "rocket":
            palette = [
                (0.008, 0.016, 0.098),
                (0.071, 0.047, 0.145),
                (0.145, 0.078, 0.196),
                (0.220, 0.098, 0.247),
                (0.298, 0.110, 0.290),
                (0.380, 0.118, 0.322),
                (0.455, 0.118, 0.345),
                (0.541, 0.114, 0.357),
                (0.631, 0.098, 0.353),
                (0.714, 0.086, 0.341),
                (0.792, 0.100, 0.310),
                (0.855, 0.161, 0.275),
                (0.906, 0.243, 0.243),
                (0.937, 0.341, 0.251),
                (0.949, 0.439, 0.302),
                (0.957, 0.525, 0.369),
                (0.961, 0.612, 0.451),
                (0.965, 0.694, 0.545),
                (0.965, 0.773, 0.647),
                (0.973, 0.847, 0.761),
                (0.980, 0.918, 0.863),
            ]
        elif theme == "mako":
            palette = [
                (0.043, 0.012, 0.020),
                (0.090, 0.047, 0.086),
                (0.141, 0.086, 0.161),
                (0.184, 0.122, 0.243),
                (0.220, 0.165, 0.329),
                (0.243, 0.204, 0.420),
                (0.251, 0.247, 0.502),
                (0.243, 0.302, 0.573),
                (0.224, 0.365, 0.608),
                (0.208, 0.424, 0.624),
                (0.204, 0.476, 0.635),
                (0.204, 0.533, 0.647),
                (0.204, 0.588, 0.663),
                (0.212, 0.647, 0.671),
                (0.239, 0.702, 0.675),
                (0.286, 0.757, 0.678),
                (0.373, 0.808, 0.675),
                (0.522, 0.847, 0.690),
                (0.659, 0.882, 0.741),
                (0.773, 0.922, 0.816),
                (0.871, 0.957, 0.894),
            ]

        if value < min_val:
            value = min_val
        if value > max_val:
            value = max_val

        scale = (value - min_val) / (max_val - min_val) * (len(palette) - 1)
        index = int(scale)
        fraction = scale - index

        if index >= len(palette) - 1:
            return palette[-1]
        return cls.interpolate_color(palette[index], palette[index + 1], fraction)

    @classmethod
    def get_query_for_selected_elements(cls) -> str:
        global_ids = []
        for obj in tool.Blender.get_selected_objects():
            if element := tool.Ifc.get_entity(obj):
                if global_id := getattr(element, "GlobalId", None):
                    global_ids.append(global_id)

        query = ",".join(global_ids)
        if len(global_ids) > 50:
            # Too much to store in a string property.
            name = f"globalid-filter-{ifcopenshell.guid.new()}"
            text_data = bpy.data.texts.new(name)
            text_data.from_string(query)
            query = f"bpy.data.texts['{name}']"
        return query

    @classmethod
    def patch_search_ifcgroups(cls) -> None:
        """Apply a patch trying to convert old search IfcGroups to SEARCH type.

        Previously we were saving search results to IfcGroup with ObjectType None
        and allowing to write results to any IfcGroup by default, which could lead
        to breaking by accident drawings or other internal IfcGroups.

        Added temporarily @25.07.04
        """
        ifc_file = tool.Ifc.get()

        for group in ifc_file.by_type("IfcGroup"):
            # It's unsafe to change any other IfcGroup - e.g. it could be DRAWING.
            if group.ObjectType is not None:
                continue
            try:
                data = json.loads(group.Description)
                if isinstance(data, dict) and data.get("type") == "BBIM_Search":
                    group.ObjectType = "SEARCH"
            except:
                pass


class ImportFilterQueryTransformer(lark.Transformer):
    def __init__(self, filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]):
        self.filter_groups = filter_groups

    def get_results(self):
        results = set()
        for r in self.results:
            results |= r
        return results

    def facet_list(self, args):
        new = self.filter_groups.add()
        global_ids = []
        is_first_group = len(self.filter_groups) == 1
        for filter_index, arg in enumerate(args):
            if arg["type"] == "instance" and global_ids:
                if "bpy.data.texts" in new2.value:
                    data_name = new2.value.split("bpy.data.texts")[1][2:-2]
                    bpy.data.texts[data_name].write("," + arg["value"])
                elif len(new2.value) > (23 * 50):
                    name = "globalid-filter-" + ifcopenshell.guid.new()
                    text_data = bpy.data.texts.new(name)
                    text_data.from_string(new2.value + "," + arg["value"])
                    new2.value = f"bpy.data.texts['{name}']"
                else:
                    new2.value += "," + arg["value"]
                continue
            global_ids = []
            if arg["type"] == "instance":
                global_ids.append(arg["value"])
            new2 = new.filters.add()
            new2.type = arg["type"]
            new2.value = arg["value"]
            if "name" in arg:
                new2.name = arg["name"]
            if "pset" in arg:
                new2.pset = arg["pset"]
            if "comparison" in arg:
                new2.comparison = arg["comparison"] or "="
            if "filter_mode" in arg:
                new2.filter_mode = arg["filter_mode"]
            elif not is_first_group and filter_index == 0 and arg["type"] in ("entity", "instance"):
                if arg.get("filter_mode", "ADD") != "SUBTRACT":
                    new2.filter_mode = "FILTER"

    def facet(self, args):
        return args[0]

    def instance(self, args):
        if args[0].data == "not":
            return {"type": "instance", "value": args[1].children[0].value, "filter_mode": "SUBTRACT"}
        else:
            return {"type": "instance", "value": args[0].children[0].value, "filter_mode": "ADD"}

    def entity(self, args):
        if args[0].data == "not":
            return {"type": "entity", "value": args[1].children[0].value, "filter_mode": "SUBTRACT"}
        else:
            return {"type": "entity", "value": args[0].children[0].value, "filter_mode": "ADD"}

    def attribute(self, args):
        name, comparison, value = args
        name = name.children[0].value
        return {"type": "attribute", "name": name, "value": f"{comparison}{value}"}

    def type(self, args):
        comparison, value = args
        return {"type": "type", "value": f"{comparison}{value}"}

    def material(self, args):
        comparison, value = args
        return {"type": "material", "value": f"{comparison}{value}"}

    def property(self, args):
        pset, prop, comparison, value = args
        return {"type": "property", "pset": pset, "name": prop, "comparison": comparison, "value": f"{value}"}

    def classification(self, args):
        comparison, value = args
        return {"type": "classification", "value": f"{comparison}{value}"}

    def location(self, args):
        comparison, value = args
        return {"type": "location", "value": f"{comparison}{value}"}

    def group(self, args):
        comparison, value = args
        return {"type": "group", "value": f"{comparison}{value}"}

    def parent(self, args):
        comparison, value = args
        return {"type": "parent", "value": f"{comparison}{value}"}

    def query(self, args):
        keys, comparison, value = args
        return {"type": "query", "name": keys, "value": f"{comparison}{value}"}

    def comparison(self, args):
        if args[0].data == "not":
            comparison = args[1].data
            is_not = "!"
        else:
            comparison = args[0].data
            is_not = ""

        return (
            is_not
            + {
                "equals": "=" if is_not else "",  # Blank because it's the default situation
                "morethanequalto": ">=",
                "lessthanequalto": "<=",
                "morethan": ">",
                "lessthan": "<",
                "contains": "*=",
            }[comparison]
        )

    def keys(self, args):
        return self.value(args)

    def pset(self, args):
        return self.value(args)

    def prop(self, args):
        return self.value(args)

    def value(self, args):
        if args[0].data == "unquoted_string":
            return args[0].children[0].value
        elif args[0].data == "quoted_string":
            return args[0].children[0].value[1:-1].replace('\\"', '"')
        elif args[0].data == "regex_string":
            return "/" + args[0].children[0].value + "/"
        elif args[0].data == "special":
            if args[0].children[0].data == "null":
                return "NULL"
            elif args[0].children[0].data == "true":
                return "TRUE"
            elif args[0].children[0].data == "false":
                return "FALSE"
