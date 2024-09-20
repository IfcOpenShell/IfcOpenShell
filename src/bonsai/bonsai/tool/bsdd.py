import bonsai.core.tool
import bonsai.tool as tool
import bpy
import json
import bsdd
from typing import Any, Union, Optional


class Bsdd(bonsai.core.tool.Bsdd):
    @classmethod
    def clear_class_psets(cls) -> None:
        bpy.context.scene.BIMBSDDProperties.classification_psets.clear()

    @classmethod
    def clear_classes(cls) -> None:
        bpy.context.scene.BIMBSDDProperties.classifications.clear()

    @classmethod
    def clear_domains(cls) -> None:
        bpy.context.scene.BIMBSDDProperties.domains.clear()

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
    def create_classes(cls, class_dict: list[bsdd.ClassSearchResponseClassContractV1]) -> None:
        props = bpy.context.scene.BIMBSDDProperties
        for _class in sorted(class_dict, key=lambda c: c["referenceCode"]):
            prop = props.classifications.add()
            prop.name = _class["name"]
            prop.reference_code = _class["referenceCode"]
            prop.uri = _class["uri"]
            prop.domain_name = _class["dictionaryName"]
            prop.domain_namespace_uri = _class["dictionaryUri"]

    @classmethod
    def create_dictionaries(cls, dictionaries: list[bsdd.DictionaryContractV1]) -> None:
        props = bpy.context.scene.BIMBSDDProperties
        for dictionary in sorted(dictionaries, key=lambda d: d["name"]):
            new = props.domains.add()
            new.name = dictionary["name"]
            new.uri = dictionary["uri"]
            new.default_language_code = dictionary["defaultLanguageCode"]
            new.organization_name_owner = dictionary["organizationNameOwner"]
            new.status = dictionary["status"]
            new.version = dictionary["version"]

    @classmethod
    def get_active_class_data(cls, client: bsdd.Client) -> Union[bsdd.ClassContractV1, dict]:
        prop = bpy.context.scene.BIMBSDDProperties
        bsdd_classification = prop.classifications[prop.active_classification_index]
        if not bsdd_classification:
            return {}
        return client.get_class(bsdd_classification.uri)

    @classmethod
    def get_active_dictionary_uri(cls) -> str:
        return bpy.context.scene.BIMBSDDProperties.active_uri

    @classmethod
    def get_dictionaries(cls, client: bsdd.Client, status: Optional[str] = None) -> list[bsdd.DictionaryContractV1]:
        response = client.get_dictionary()
        dicts = response.get("dictionaries") or []
        if status is not None:
            dicts = list(filter(lambda d: d["status"] == status, dicts))
        return dicts

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
            # Prefer propertyCode as it's later will be used to set properties,
            # so name should be exact. Fallback to name as propertyCode is nullable.
            prop_name = prop.get("propertyCode") or prop["name"]
            psets[pset][prop_name] = {
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
            element = tool.Ifc.get_entity(active_object)
            if element:
                related_ifc_entities = [element.is_a()]
        return related_ifc_entities

    @classmethod
    def search_class(
        cls,
        client: bsdd.Client,
        keyword: str,
        dictionary_uris: Union[list[str], None],
        related_ifc_entities: Union[list[str], None],
        offset: int = 0,
    ) -> list[bsdd.ClassSearchResponseClassContractV1]:
        response = client.search_class(
            keyword, dictionary_uris=dictionary_uris, related_ifc_entities=related_ifc_entities, offset=offset
        )
        classes = response.get("classes", [])
        # If count is 100, it might be hitting the limit.
        if response["count"] == 100:
            classes += cls.search_class(client, keyword, dictionary_uris, related_ifc_entities, offset=offset + 100)
        return classes

    @classmethod
    def set_active_bsdd(cls, name: str, uri: str) -> None:
        props = bpy.context.scene.BIMBSDDProperties
        props.active_domain = name
        props.active_uri = uri

    @classmethod
    def should_filter_ifc_class(cls) -> bool:
        return bpy.context.scene.BIMBSDDProperties.should_filter_ifc_class

    @classmethod
    def should_load_preview_domains(cls) -> bool:
        return bpy.context.scene.BIMBSDDProperties.load_preview_domains
