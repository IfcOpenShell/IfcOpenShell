import blenderbim.core.tool
import json


class Bsdd(blenderbim.core.tool.Bsdd):
    @classmethod
    def get_dictionaries(cls, client, status=None) -> list:
        response = client.get_dictionary()
        dicts = response.get("dictionaries") or []
        if status is not None:
            dicts = filter(lambda d: d["status"] == status, dicts)
        return dicts

    @classmethod
    def fill_dictionary_prop(cls, prop, dictionary):
        prop.name = dictionary["name"]
        prop.uri = dictionary["uri"]
        prop.default_language_code = dictionary["defaultLanguageCode"]
        prop.organization_name_owner = dictionary["organizationNameOwner"]
        prop.status = dictionary["status"]
        prop.version = dictionary["version"]

    @classmethod
    def get_related_ifc_entities(cls, keyword, filter_ifc_class: bool, active_object, ifc):
        related_ifc_entities = []
        if len(keyword) < 3:
            return {"FINISHED"}
        if filter_ifc_class and active_object:
            element = ifc.get_entity(active_object)
            if element:
                related_ifc_entities = [element.is_a()]
        return related_ifc_entities

    @classmethod
    def fill_class_prop(cls, prop, _class: dict):
        prop.name = _class["name"]
        prop.reference_code = _class["referenceCode"]
        prop.description = _class.get("description", "")
        prop.uri = _class["uri"]
        prop.domain_name = _class["dictionaryName"]
        prop.domain_namespace_uri = _class["dictionaryUri"]

    @classmethod
    def get_active_class_data(cls, prop, client):
        prop.classification_psets.clear()
        bsdd_classification = prop.classifications[prop.active_classification_index]
        return client.get_class(bsdd_classification.uri)

    @classmethod
    def get_property_dict(cls, class_data: dict):
        properties = class_data.get("classProperties", None)
        if not properties:
            return None

        psets = {}
        for prop in properties:
            if prop.get("propertyDictionaryName") == "IFC":
                continue
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

            psets[pset][prop["name"]] = {"data_type": prop["dataType"], "possible_values": possible_values}
        return psets

    @classmethod
    def create_classification_psets(cls, props, pset_dict: dict):
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
                    new2.data_type = data_type_map[data["data_type"]]
