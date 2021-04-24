import json
import requests


class Client:
    def __init__(self):
        self.baseurl = "https://bs-dd-api-prototype.azurewebsites.net/"

    def get(self, endpoint, params=None):
        return requests.get(f"{self.baseurl}{endpoint}", params=params or None).json()

    def post(self):
        pass  # TODO

    def Classification(self, namespaceUri, version="v3", languageCode="", includeChildClassificationReferences=True):
        return self.get(
            f"api/Classification/{version}",
            {
                "namespaceUri": namespaceUri,
                "languageCode": languageCode,
                "includeChildClassificationReferences": includeChildClassificationReferences,
            },
        )

    def Country(self, version="v1"):
        return self.get(f"api/Country/{version}")

    def Domain(self, version="v2"):
        return self.get(f"api/Domain/{version}")

    def graphql(self):
        return  # TODO

    def Language(self, version="v1"):
        return self.get(f"api/Language/{version}")

    def Property(self, namespaceUri, version="v2", languageCode=""):
        return self.get(f"api/Property/{version}", {"namespaceUri": namespaceUri, "languageCode": languageCode})

    def PropertyValue(self, namespaceUri, version="v1", languageCode=""):
        return self.get(f"api/PropertyValue/{version}", {"namespaceUri": namespaceUri, "languageCode": languageCode})

    def ReferenceDocument(self, version="v1"):
        return self.get(f"api/ReferenceDocument/{version}")

    def RequestExportFile(self):
        return  # TODO

    def SearchList(self, DomainNamespaceUri, version="v2", SearchText="", LanguageCode="", RelatedIfcEntity=""):
        # TODO
        return self.get(
            f"api/SearchList/{version}",
            {
                "DomainNamespaceUri": DomainNamespaceUri,
                "SearchText": SearchText,
                "LanguageCode": LanguageCode,
                "RelatedIfcEntity": RelatedIfcEntity,
            },
        )

    def SearchListOpen(self, DomainNamespaceUri, version="v2", SearchText="", LanguageCode="", RelatedIfcEntity=""):
        return self.get(
            f"api/SearchListOpen/{version}",
            {
                "DomainNamespaceUri": DomainNamespaceUri,
                "SearchText": SearchText,
                "LanguageCode": LanguageCode,
                "RelatedIfcEntity": RelatedIfcEntity,
            },
        )

    def TextSearchListOpen(self):
        return  # TODO

    def Unit(self, version="v1"):
        return self.get(f"api/Unit/{version}")

    def UploadImportFile(self):
        return  # TODO


def apply_ifc_classification_properties(ifc_file, element, classificationProperties):
    import ifcopenshell
    import ifcopenshell.api
    import ifcopenshell.util.element

    psets = ifcopenshell.util.element.get_psets(element)
    for prop in classificationProperties:
        predefinedValue = prop.get("predefinedValue")
        if not predefinedValue or prop.get("propertyDomainName") != "IFC":
            continue
        pset = psets.get(prop["propertySet"])
        if pset:
            pset = ifc_file.by_id(pset["id"])
        else:
            pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name=prop["propertySet"])
        if prop["dataType"] == "boolean":
            predefinedValue = predefinedValue == "TRUE"
        ifcopenshell.api.run("pset.edit_pset", pset=pset, properties={prop["name"]: predefinedValue})
