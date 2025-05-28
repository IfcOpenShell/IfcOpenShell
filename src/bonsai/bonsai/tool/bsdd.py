import bonsai.core.tool
import bonsai.tool as tool
import bpy
import json
import bsdd
import ifcopenshell.util.type
import ifcopenshell.util.element
import ifcopenshell.util.classification
from typing import Any, Union, Optional, TYPE_CHECKING


class Bsdd(bonsai.core.tool.Bsdd):
    identifier_url = "https://identifier.buildingsmart.org"
    client = bsdd.Client()
    bsdd_classes: dict[str, dict] = {}
    bsdd_properties: dict[str, dict] = {}

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
    def clear_properties(cls) -> None:
        bpy.context.scene.BIMBSDDProperties.properties.clear()

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
    def get_class_properties(
        cls, class_data: Union[bsdd.ClassContractV1, dict]
    ) -> Union[dict[str, dict[str, Any]], None]:
        properties = class_data.get("classProperties", None)
        if not properties:
            return {}

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
        cprops = bpy.context.scene.BIMClassificationProperties
        bprops = cls.get_bsdd_props()
        dictionary_uris = (
            [d.uri for d in bprops.dictionaries if d.is_active]
            if cprops.classification_source == "BSDD"
            else [cprops.classification_source]
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
                    prop = bprops.classifications.add()
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

    @classmethod
    def get_bsdd_class(cls, uri: str) -> dict:
        if not (bsdd_class := cls.bsdd_classes.get(uri, {})):
            bsdd_class = cls.client.get_class(uri)
            cls.bsdd_classes[uri] = bsdd_class
        return bsdd_class

    @classmethod
    def get_bsdd_property(cls, uri: str) -> dict:
        if not (bsdd_property := cls.bsdd_properties.get(uri, {})):
            bsdd_property = cls.client.get_property(uri, include_classes=True)
            cls.bsdd_properties[uri] = bsdd_property
        return bsdd_property

    @classmethod
    def import_classes(cls, obj, obj_type) -> None:
        pprops = tool.Pset.get_pset_props(obj, obj_type)
        props = cls.get_bsdd_props()
        props.classes.clear()

        classes = set()
        for obj in tool.Blender.get_selected_objects(include_active=True):
            if element := tool.Ifc.get_entity(obj):
                for reference in ifcopenshell.util.classification.get_references(element):
                    if (uri := reference.Location) and uri.startswith(cls.identifier_url):
                        classes.add((reference[1] or reference[2] or "Unnamed", uri))

        dictionary_uris = (
            [d.uri for d in props.dictionaries if d.is_active]
            if pprops.pset_name == "BBIM_BSDD"
            else [pprops.pset_name]
        )
        related_ifc_entities = cls.get_related_ifc_entities()
        for dictionary_uri in dictionary_uris:
            for related_ifc_entity in related_ifc_entities or [None]:
                bsdd_classes = cls.client.get_classes(
                    dictionary_uri=dictionary_uri,
                    class_type="GroupOfProperties",
                    use_nested_classes=False,
                    related_ifc_entity=related_ifc_entity,
                )
                for bsdd_class in bsdd_classes["classes"]:
                    classes.add((bsdd_class["name"], bsdd_class["uri"]))

        for bsdd_class in classes:
            new = props.classes.add()
            new.name = bsdd_class[0]
            new.uri = bsdd_class[1]

    @classmethod
    def import_class_properties(cls) -> None:
        props = cls.get_bsdd_props()
        props.properties.clear()
        if not (active_class := props.active_class):
            return
        if not (bsdd_class := cls.get_bsdd_class(active_class.uri)):
            return
        for bsdd_prop in bsdd_class.get("classProperties", []):
            if not bsdd_prop.get("propertySet", None):
                continue
            cls.bsdd_properties[bsdd_prop["uri"]] = bsdd_prop
            new = props.properties.add()
            new.name = bsdd_prop["name"]
            new.pset = bsdd_prop["propertySet"]
            new.uri = bsdd_prop["uri"]

    @classmethod
    def import_properties(cls, obj, obj_type, keyword) -> None:
        props = cls.get_bsdd_props()
        props.properties.clear()
        pprops = tool.Pset.get_pset_props(obj, obj_type)
        dictionary_uris = (
            [d.uri for d in props.dictionaries if d.is_active]
            if pprops.pset_name == "BBIM_BSDD"
            else [pprops.pset_name]
        )
        for dictionary_uri in dictionary_uris:
            for bsdd_prop in cls.client.get_properties(dictionary_uri, keyword)["properties"]:
                new = props.properties.add()
                new.name = bsdd_prop["name"]
                new.uri = bsdd_prop["uri"]

    @classmethod
    def import_selected_properties(cls) -> None:
        props = cls.get_bsdd_props()
        data_type_map = {
            "String": "string",
            "Real": "float",
            "Boolean": "boolean",
        }
        imported_props = set()
        for bsdd_prop in props.properties:
            if not bsdd_prop.is_selected:
                continue
            if not (pset_name := bsdd_prop.pset):
                prop_data = cls.get_bsdd_property(bsdd_prop.uri)
                pset_name = prop_data.get("propertyClasses", [{}])[0].get("propertySet", "")

            imported_props.add((pset_name, bsdd_prop.name))
            if (
                selected_property := props.selected_properties.get(bsdd_prop.name)
            ) and selected_property.metadata == pset_name:
                continue

            data = cls.bsdd_properties[bsdd_prop.uri]

            predefined_value = data.get("predefinedValue")
            if predefined_value:
                possible_values = [predefined_value]
            else:
                possible_values = data.get("allowedValues", []) or []
                possible_values = [v["value"] for v in possible_values]

            new = props.selected_properties.add()
            new.name = bsdd_prop.name
            if possible_values:
                new.enum_items = json.dumps(possible_values)
                new.data_type = "enum"
            else:
                new.data_type = data_type_map.get(data["dataType"], "string")
            new.description = data.get("description", "")
            new.metadata = pset_name

        to_remove = []
        for i, selected_property in enumerate(props.selected_properties):
            if (selected_property.metadata, selected_property.name) not in imported_props:
                to_remove.append(i)

        for i in to_remove[::-1]:
            props.selected_properties.remove(i)

    @classmethod
    def get_applicable_psets(cls, element: ifcopenshell.entity_instance):
        uris = set()
        for reference in ifcopenshell.util.classification.get_references(element):
            if (uri := reference.Location) and uri.startswith(cls.identifier_url):
                uris.add(uri)
        psets = set()
        for uri in uris:
            if not (bsdd_class := cls.bsdd_classes.get(uri, None)):
                continue
            for class_pset in bsdd_class.get("classProperties", []):
                if not (pset_name := class_pset.get("propertySet", None)):
                    continue
                psets.add((uri, bsdd_class["name"], pset_name))
        return psets

    @classmethod
    def is_applicable(cls, pset_uri: str, element: ifcopenshell.entity_instance) -> bool:
        uris = set()
        for reference in ifcopenshell.util.classification.get_references(element):
            if (uri := reference.Location) and uri.startswith(cls.identifier_url):
                uris.add(uri)
        class_uri, pset_name = pset_uri.rsplit("#", 1)
        return class_uri in uris
