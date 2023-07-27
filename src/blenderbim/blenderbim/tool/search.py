import bpy
import json
import lark
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell.util.selector
from ifcopenshell.util.selector import Selector


class Search(blenderbim.core.tool.Search):
    @classmethod
    def import_filter_query(cls, group, filter_groups):
        query = json.loads(group.Description)["query"]
        filter_groups.clear()
        transformer = ImportFilterQueryTransformer(filter_groups)
        transformer.transform(ifcopenshell.util.selector.filter_elements_grammar.parse(query))

    @classmethod
    def export_filter_query(cls, filter_groups):
        query = []
        for filter_group in filter_groups:
            filter_group_query = []
            has_instance_or_entity_filter = False
            for ifc_filter in filter_group.filters:
                if not ifc_filter.value:
                    continue
                if ifc_filter.type == "instance":
                    has_instance_or_entity_filter = True
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
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"{pset}.{name}{comparison}{value}")
                elif ifc_filter.type == "classification":
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"classification{comparison}{value}")
                elif ifc_filter.type == "location":
                    comparison, value = cls.get_comparison_and_value(ifc_filter)
                    filter_group_query.append(f"location{comparison}{value}")
            if not has_instance_or_entity_filter:
                filter_group_query.insert(0, "IfcElement")
            query.append(", ".join(filter_group_query))
        return " + ".join(query)

    @classmethod
    def get_comparison_and_value(cls, ifc_filter):
        if ifc_filter.value.startswith("!="):
            return ("!=", cls.wrap_value(ifc_filter, ifc_filter.value[2:].strip()))
        return ("=", cls.wrap_value(ifc_filter, ifc_filter.value.strip()))

    @classmethod
    def wrap_value(cls, ifc_filter, value):
        if value.startswith("/") and value.endswith("/"):
            return value
        elif value in ("NULL", "TRUE", "FALSE"):
            return value
        return '"' + value.replace('"', '\\"') + '"'

    @classmethod
    def from_selector_query(cls, query):
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
        for arg in args:
            new2 = new.filters.add()
            new2.type = arg["type"]
            new2.value = arg["value"]
            if "name" in arg:
                new2.name = arg["name"]
            if "pset" in arg:
                new2.pset = arg["pset"]

    def facet(self, args):
        return args[0]

    def instance(self, args):
        return {"type": "instance", "value": " ".join([a.children[0].value for a in args])}

    def entity(self, args):
        return {"type": "entity", "value": " ".join([a.children[0].value for a in args])}

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
        return {"type": "property", "pset": pset, "name": prop, "value": f"{comparison}{value}"}

    def classification(self, args):
        comparison, value = args
        return {"type": "classification", "value": f"{comparison}{value}"}

    def location(self, args):
        comparison, value = args
        return {"type": "location", "value": f"{comparison}{value}"}

    def comparison(self, args):
        return "" if args[0].data == "equals" else "!="

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
            return args[0].children[0].value
        elif args[0].data == "special":
            if args[0].children[0].data == "null":
                return "NULL"
            elif args[0].children[0].data == "true":
                return "TRUE"
            elif args[0].children[0].data == "false":
                return "FALSE"

    def compare(self, element_value, comparison, value):
        if isinstance(value, str):
            if isinstance(element_value, int):
                value = int(value)
            elif isinstance(element_value, float):
                value = float(value)
            result = element_value == value
        elif isinstance(value, re.Pattern):
            result = bool(value.match(element_value))
        elif value in (None, True, False):
            result = element_value is value
        return result if comparison == "=" else not result
