import bpy
import json
import lark
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell.guid
import ifcopenshell.util.selector
from ifcopenshell.util.selector import Selector
from blenderbim.bim.prop import BIMFacet
from typing import Union, Literal


class Search(blenderbim.core.tool.Search):
    @classmethod
    def get_group_query(cls, group: ifcopenshell.entity_instance) -> str:
        return json.loads(group.Description)["query"]

    @classmethod
    def get_filter_groups(cls, module: str) -> bpy.types.bpy_prop_collection:
        if module == "search":
            return bpy.context.scene.BIMSearchProperties.filter_groups
        elif module == "csv":
            return bpy.context.scene.CsvProperties.filter_groups
        elif module == "diff":
            return bpy.context.scene.DiffProperties.filter_groups
        elif module == "drawing_include":
            return bpy.context.active_object.data.BIMCameraProperties.include_filter_groups
        elif module == "drawing_exclude":
            return bpy.context.active_object.data.BIMCameraProperties.exclude_filter_groups
        elif module.startswith("clash"):
            _, clash_set_index, ab, clash_source_index = module.split("_")
            return getattr(bpy.context.scene.BIMClashProperties.clash_sets[int(clash_set_index)], ab)[
                int(clash_source_index)
            ].filter_groups

    @classmethod
    def import_filter_query(cls, query: str, filter_groups: bpy.types.bpy_prop_collection) -> None:
        filter_groups.clear()
        transformer = ImportFilterQueryTransformer(filter_groups)
        transformer.transform(ifcopenshell.util.selector.filter_elements_grammar.parse(query))

    @classmethod
    def export_filter_query(cls, filter_groups: bpy.types.bpy_prop_collection) -> str:
        query = []
        for filter_group in filter_groups:
            filter_group_query = []
            has_instance_or_entity_filter = False
            for ifc_filter in filter_group.filters:
                if not ifc_filter.value:
                    continue
                if ifc_filter.type == "instance":
                    has_instance_or_entity_filter = True
                    if "bpy.data.texts" in ifc_filter.value:
                        data_name = ifc_filter.value.split("bpy.data.texts")[1][2:-2]
                        filter_group_query.append(bpy.data.texts[data_name].as_string())
                    else:
                        filter_group_query.append(ifc_filter.value)
                elif ifc_filter.type == "entity":
                    has_instance_or_entity_filter = True
                    filter_group_query.append(ifc_filter.value)
                elif ifc_filter.type == "attribute":
                    if not ifc_filter.name:
                        continue
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"{ifc_filter.name}{comparison}{value}")
                elif ifc_filter.type == "type":
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"type{comparison}{value}")
                elif ifc_filter.type == "material":
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"material{comparison}{value}")
                elif ifc_filter.type == "property":
                    if not ifc_filter.pset or not ifc_filter.name:
                        continue
                    pset = cls.wrap_value(ifc_filter, ifc_filter.pset)
                    name = cls.wrap_value(ifc_filter, ifc_filter.name)
                    comparison = ifc_filter.comparison
                    value = cls.wrap_value(ifc_filter, ifc_filter.value)
                    filter_group_query.append(f"{pset}.{name} {comparison} {value}")
                elif ifc_filter.type == "classification":
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"classification{comparison}{value}")
                elif ifc_filter.type == "location":
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"location{comparison}{value}")
                elif ifc_filter.type == "group":
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"group{comparison}{value}")
                elif ifc_filter.type == "parent":
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"parent{comparison}{value}")
                elif ifc_filter.type == "query":
                    keys = cls.wrap_value(ifc_filter, ifc_filter.name)
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"query:{keys}{comparison}{value}")
            if not has_instance_or_entity_filter:
                filter_group_query.insert(0, "IfcProduct")
                filter_group_query.insert(0, "IfcTypeProduct")
            query.append(", ".join(filter_group_query))
        return " + ".join(query)

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
    def from_selector_query(cls, query: str) -> list[ifcopenshell.entity_instance]:
        """Returns a list of products from a selector query"""
        return Selector().parse(tool.Ifc.get(), query)


class ImportFilterQueryTransformer(lark.Transformer):
    def __init__(self, filter_groups):
        self.filter_groups = filter_groups

    def get_results(self):
        results = set()
        for r in self.results:
            results |= r
        return results

    def facet_list(self, args):
        new = self.filter_groups.add()
        global_ids = []
        for arg in args:
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

    def facet(self, args):
        return args[0]

    def instance(self, args):
        if args[0].data == "not":
            return {"type": "instance", "value": "!" + args[1].children[0].value}
        else:
            return {"type": "instance", "value": args[0].children[0].value}

    def entity(self, args):
        if args[0].data == "not":
            return {"type": "entity", "value": "!" + args[1].children[0].value}
        else:
            return {"type": "entity", "value": args[0].children[0].value}

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
