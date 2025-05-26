import bonsai.core.tool
import bonsai.tool as tool
import bpy
import json
import bsdd
import ifcopenshell.util.type
import ifcopenshell.util.element
from typing import Any, Union, Optional, TYPE_CHECKING


class Bsdd(bonsai.core.tool.Bsdd):
    client = bsdd.Client()

    @classmethod
    def get_bsdd_props(cls):
        return bpy.context.scene.BIMBSDDProperties

    @classmethod
    def clear_class_psets(cls) -> None:
        bpy.context.scene.BIMBSDDProperties.classification_psets.clear()

    @classmethod
    def clear_classes(cls) -> None:
        bpy.context.scene.BIMBSDDProperties.classifications.clear()

    @classmethod
    def clear_dictionaries(cls) -> None:
        bpy.context.scene.BIMBSDDProperties.dictionaries.clear()

    @classmethod
    def create_class_psets(cls, pset_dict: dict[str, dict[str, Any]]) -> None:
        props = bpy.context.scene.BIMBSDDProperties
        data_type_map = {
            "String": "string",
            "Real": "float",
            "Boolean": "boolean",
        }
        for pset_name, pset in pset_dict.items():
            new = props.classification_psets.add()
            new.name = pset_name
            for name, data in pset.items():
                new2 = new.properties.add()
                new2.name = name
                if data["possible_values"]:
                    new2.enum_items = json.dumps(data["possible_values"])
                    new2.data_type = "enum"
                else:
                    new2.data_type = data_type_map.get(data["data_type"], "string")
                new2.description = data["description"]
                new2.ifc_class = data["ifc_class"]
                new2.metadata = data["dictionary"]

    @classmethod
    def create_dictionaries(cls, dictionaries: list[bsdd.DictionaryContractV1]) -> None:
        props = bpy.context.scene.BIMBSDDProperties
        for dictionary in sorted(dictionaries, key=lambda d: d["name"]):
            new = props.dictionaries.add()
            new.name = dictionary["name"]
            new.uri = dictionary["uri"]
            new.default_language_code = dictionary["defaultLanguageCode"]
            new.organization_name_owner = dictionary["organizationNameOwner"]
            new.status = dictionary["status"]
            new.version = dictionary["version"]

    @classmethod
    def get_active_class_data(cls) -> Union[bsdd.ClassContractV1, dict]:
        prop = bpy.context.scene.BIMBSDDProperties
        bsdd_classification = prop.classifications[prop.active_classification_index]
        if not bsdd_classification:
            return {}
        return cls.client.get_class(bsdd_classification.uri)

    @classmethod
    def get_active_dictionary_uri(cls) -> str:
        return bpy.context.scene.BIMBSDDProperties.active_uri

    @classmethod
    def get_dictionary(cls, uri: str) -> bsdd.DictionaryContractV1:
        props = bpy.context.scene.BIMBSDDProperties
        response = cls.client.get_dictionary(dictionary_uri=uri, include_test_dictionaries=props.load_test_dictionaries)
        if dicts := response.get("dictionaries"):
            return dicts[0]

    @classmethod
    def get_dictionaries(cls) -> list[bsdd.DictionaryContractV1]:
        props = bpy.context.scene.BIMBSDDProperties
        response = cls.client.get_dictionary(include_test_dictionaries=props.load_test_dictionaries)
        dicts = response.get("dictionaries") or []
        statuses = ["Active"]
        if props.load_preview_dictionaries:
            statuses.append("Preview")
        if props.load_inactive_dictionaries:
            statuses.append("Inactive")
        return list(filter(lambda d: d["status"] in statuses, dicts))

    @classmethod
    def get_property_dict(cls, class_data: Union[bsdd.ClassContractV1, dict]) -> Union[dict[str, dict[str, Any]], None]:
        properties = class_data.get("classProperties", None)
        if not properties:
            return None

        ifc_class = class_data.get("relatedIfcEntityNames") or ""
        if ifc_class:
            ifc_class = ifc_class[0]

        psets = {}
        for prop in properties:
            prop_dictionary = prop.get("propertyDictionaryName") or ""
            pset = prop.get("propertySet", None)
            if not pset:
                continue
            psets.setdefault(pset, {})

            predefined_value = prop.get("predefinedValue")
            if predefined_value:
                possible_values = [predefined_value]
            else:
                possible_values = prop.get("allowedValues", []) or []
                possible_values = [v["value"] for v in possible_values]

            description = prop.get("description", "")
            psets[pset][prop["name"]] = {
                "data_type": prop.get("dataType"),
                "possible_values": possible_values,
                "description": description,
                "ifc_class": ifc_class,
                "dictionary": prop_dictionary,
            }
        return psets

    @classmethod
    def get_related_ifc_entities(cls) -> list[str]:
        active_object = bpy.context.active_object
        related_ifc_entities = []
        if cls.should_filter_ifc_class() and active_object:
            if element := tool.Ifc.get_entity(active_object):
                ifc_class = element.is_a()
                if element.is_a("IfcElementType"):
                    ifc_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, schema=tool.Ifc.get().schema)[
                        0
                    ]
                related_ifc_entities = [ifc_class]
                if (
                    predefined_type := ifcopenshell.util.element.get_predefined_type(element)
                ) and predefined_type != "NOTDEFINED":
                    related_ifc_entities.append(ifc_class + predefined_type)
        return related_ifc_entities

    @classmethod
    def search_class(
        cls,
        keyword: str,
        related_ifc_entities: Union[list[str], None],
        offset: int = 0,
        limit: int = 100,
        should_paginate: bool = True,
    ):
        props = cls.get_bsdd_props()
        dictionary_uris = (
            [d.uri for d in props.dictionaries if d.is_active]
            if props.active_dictionary == "ALL"
            else [props.active_dictionary]
        )
        for dictionary_uri in dictionary_uris:
            for related_ifc_entity in related_ifc_entities or [None]:
                response = cls.client.get_classes(
                    dictionary_uri=dictionary_uri,
                    use_nested_classes=False,
                    search_text=keyword,
                    related_ifc_entity=related_ifc_entity,
                    offset=offset,
                    limit=limit,
                )
                dictionary_name = response.get("name", "")
                dictionary_namespace_uri = response.get("uri", "")
                for _class in sorted(response.get("classes", []), key=lambda c: c["referenceCode"]):
                    prop = props.classifications.add()
                    prop.name = _class["name"]
                    prop.reference_code = _class["referenceCode"]
                    prop.uri = _class["uri"]
                    prop.dictionary_name = dictionary_name
                    prop.dictionary_namespace_uri = dictionary_namespace_uri

        total_results = response.get("count", response.get("classesCount"))
        # For now, hard limit at 1000 results because any more and Blender
        # starts getting slow and they really should filter better
        if offset < 1000 and should_paginate and total_results == limit:
            cls.search_class(keyword, related_ifc_entities, offset=offset + limit, should_paginate=False)

        return offset + total_results

    @classmethod
    def set_active_bsdd(cls, name: str, uri: str) -> None:
        props = bpy.context.scene.BIMBSDDProperties
        props.active_dictionary = name
        props.active_uri = uri

    @classmethod
    def should_filter_ifc_class(cls) -> bool:
        return bpy.context.scene.BIMBSDDProperties.should_filter_ifc_class
