# bSDD - Python bSDD library
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of bSDD.
#
# bSDD is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bSDD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with bSDD.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import annotations

import uuid
import time
import urllib
import requests
import webbrowser
import http.server
from typing import TypedDict, Literal, Optional


__version__ = version = "0.0.0"

Status = Literal["Preview", "Active", "Inactive"]
ClassTypes = Literal["Class", "GroupOfProperties", "AlternativeUse", "Material"]

# NOTE: Some values in TypedDicts are actually not guaranteed to be provided
# and should be typed with NotRequired.


class DictionaryContractV1(TypedDict):
    uri: str
    name: str
    version: str
    organizationCodeOwner: str
    organizationNameOwner: str
    defaultLanguageCode: str
    license: str
    licenseUrl: str
    qualityAssuranceProcedure: str
    qualityAssuranceProcedureUrl: str
    status: str
    moreInfoUrl: str
    releaseDate: str
    lastUpdatedUtc: str


class DictionaryResponseContractV1(TypedDict):
    totalCount: int
    offset: int
    count: int
    dictionaries: list[DictionaryContractV1]


class ClassListItemContractV1(TypedDict):
    uri: str
    code: str
    name: str
    classType: str
    referenceCode: str
    parentClassCode: str
    children: list[ClassListItemContractV1]


class DictionaryClassesResponseContractV1(TypedDict):
    uri: str
    name: str
    version: str
    organizationCodeOwner: str
    organizationNameOwner: str
    defaultLanguageCode: str
    license: str
    licenseUrl: str
    qualityAssuranceProcedure: str
    qualityAssuranceProcedureUrl: str
    status: str
    moreInfoUrl: str
    releaseDate: str
    lastUpdatedUtc: str
    classes: list[ClassListItemContractV1]
    classesTotalCount: int
    classesOffset: int
    classesCount: int


class PropertyListItemContractV1(TypedDict):
    uri: str
    code: str
    name: str


class DictionaryPropertiesResponseContractV1(TypedDict):
    uri: str
    name: str
    version: str
    organizationCodeOwner: str
    organizationNameOwner: str
    defaultLanguageCode: str
    license: str
    licenseUrl: str
    qualityAssuranceProcedure: str
    qualityAssuranceProcedureUrl: str
    status: str
    moreInfoUrl: str
    releaseDate: str
    lastUpdatedUtc: str
    properties: list[PropertyListItemContractV1]
    propertiesTotalCount: int
    propertiesOffset: int
    propertiesCount: int


class ClassReferenceContractV1(TypedDict):
    uri: str
    name: str
    code: str


class ClassPropertyValueContractV1(TypedDict):
    uri: str
    code: str
    value: str
    description: str
    sortNumber: int


class ClassPropertyContractV1(TypedDict):
    name: str
    uri: str
    description: str
    dataType: str
    dimension: str
    dimensionLength: int
    dimensionMass: int
    dimensionTime: int
    dimensionElectricCurrent: int
    dimensionThermodynamicTemperature: int
    dimensionAmountOfSubstance: int
    dimensionLuminousIntensity: int
    dynamicParameterPropertyCodes: list[str]
    example: str
    isDynamic: bool
    isRequired: bool
    isWritable: bool
    maxExclusive: float
    maxInclusive: float
    minExclusive: float
    minInclusive: float
    pattern: str
    physicalQuantity: str
    allowedValues: list[ClassPropertyValueContractV1]
    predefinedValue: str
    propertyCode: str
    propertyDictionaryName: str
    propertyUri: str
    propertySet: str
    propertyStatus: str
    propertyValueKind: str
    symbol: str
    units: list[str]
    qudtCodes: list[str]


class PropertyContractV4(TypedDict):
    dictionaryUri: str
    activationDateUtc: str
    code: str
    creatorLanguageCode: str
    countriesOfUse: list[str]
    countryOfOrigin: str
    deActivationDateUtc: str
    definition: str
    deprecationExplanation: str
    description: str
    documentReference: str
    name: str
    uri: str
    replacedObjectCodes: list[str]
    replacingObjectCodes: list[str]
    revisionDateUtc: str
    revisionNumber: int
    status: str
    subdivisionsOfUse: list[str]
    uid: str
    versionDateUtc: str
    versionNumber: int
    visualRepresentationUri: str
    connectedPropertyCodes: list[str]
    dataType: str
    dimension: str
    dimensionLength: int
    dimensionMass: int
    dimensionTime: int
    dimensionElectricCurrent: int
    dimensionThermodynamicTemperature: int
    dimensionAmountOfSubstance: int
    dimensionLuminousIntensity: int
    dynamicParameterPropertyCodes: list[str]
    example: str
    isDynamic: bool
    maxExclusive: float
    maxInclusive: float
    methodOfMeasurement: str
    minExclusive: float
    minInclusive: float
    pattern: str
    physicalQuantity: str
    allowedValues: list[PropertyValueContractV4]
    propertyValueKind: str
    propertyRelations: list[PropertyRelationContractV4]
    textFormat: str
    units: list[str]
    qudtCodes: list[str]
    propertyClasses: list[PropertyClassContractV4]


class PropertyValueContractV4(TypedDict):
    uri: str
    code: str
    value: str
    description: str
    sortNumber: int


class PropertyRelationContractV4(TypedDict):
    uri: str
    relationType: str
    relatedPropertyUri: str
    relatedPropertyName: str


class PropertyClassContractV4(TypedDict):
    uri: str
    code: str
    name: str
    definition: str
    description: str
    propertySet: str


class ClassRelationContractV1(TypedDict):
    uri: str
    relationType: str
    relatedClassUri: str
    relatedClassName: str
    fraction: float


class TextSearchResponseContractV1(TypedDict):
    totalCount: int
    offset: int
    count: int
    classes: list[TextSearchResponseClassContractV1]
    dictionaries: list[TextSearchResponseDictionaryContractV1]
    properties: list[TextSearchResponsePropertyContractV1]


class TextSearchResponseClassContractV1(TypedDict):
    dictionaryUri: str
    dictionaryName: str
    name: str
    referenceCode: str
    uri: str
    classType: str
    description: str
    parentClassName: str
    relatedIfcEntityNames: list[str]


class TextSearchResponseDictionaryContractV1(TypedDict):
    uri: str
    name: str


class TextSearchResponsePropertyContractV1(TypedDict):
    dictionaryUri: str
    dictionaryName: str
    uri: str
    name: str
    description: str


class ClassContractV1(TypedDict):
    dictionaryUri: str
    activationDateUtc: str
    code: str
    creatorLanguageCode: str
    countriesOfUse: list[str]
    countryOfOrigin: str
    deActivationDateUtc: str
    definition: str
    deprecationExplanation: str
    description: str
    documentReference: str
    name: str
    uri: str
    replacedObjectCodes: list[str]
    replacingObjectCodes: list[str]
    revisionDateUtc: str
    revisionNumber: int
    status: str
    subdivisionsOfUse: list[str]
    uid: str
    versionDateUtc: str
    versionNumber: int
    visualRepresentationUri: str
    classType: str
    referenceCode: str
    synonyms: list[str]
    relatedIfcEntityNames: list[str]
    parentClassReference: ClassReferenceContractV1
    classProperties: list[ClassPropertyContractV1]
    classRelations: list[ClassRelationContractV1]
    childClassReferences: list[ClassReferenceContractV1]


class SearchInDictionaryResponseContractV1(TypedDict):
    totalCount: int
    offset: int
    count: int
    dictionary: DictionarySearchResultContractV1


class DictionarySearchResultContractV1(TypedDict):
    name: str
    uri: str
    classes: list[ClassSearchResultContractV1]


class ClassSearchResultContractV1(TypedDict):
    name: str
    uri: str
    referenceCode: str
    classType: str
    definition: str
    synonyms: list[str]


class ClassSearchResponseContractV1(TypedDict):
    totalCount: int
    offset: int
    count: int
    classes: list[ClassSearchResponseClassContractV1]


class ClassSearchResponseClassContractV1(TypedDict):
    dictionaryUri: str
    dictionaryName: str
    name: str
    referenceCode: str
    uri: str
    classType: str
    description: str
    parentClassName: str
    relatedIfcEntityNames: list[str]


class CountryContractV1(TypedDict):
    code: str
    name: str


class LanguageContractV1(TypedDict):
    isoCode: str
    name: str


class ReferenceDocumentContractV1(TypedDict):
    title: str
    name: str
    date: str


class UnitContractV1(TypedDict):
    code: str
    name: str
    symbol: str
    qudtUri: str


class OAuthReceiver(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        self.server.auth_code = query.get("code", [""])[0]
        self.server.auth_state = query.get("state", [""])[0]
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("You have now authenticated :) You may now close this browser window.".encode("utf-8"))


class Client:
    def __init__(self):
        self.baseurl = "https://api.bsdd.buildingsmart.org/api/"
        self.access_token = ""
        self.refresh_token = ""
        self.access_token_expires_on = time.time()
        self.refresh_token_expires_on = time.time()
        self.auth_endpoint = "https://buildingsmartservices.b2clogin.com/tfp/buildingsmartservices.onmicrosoft.com/b2c_1_signupsignin/oauth2/v2.0/authorize"
        self.token_endpoint = "https://buildingsmartservices.b2clogin.com/tfp/buildingsmartservices.onmicrosoft.com/b2c_1_signupsignin/oauth2/v2.0/token"
        self.client_id = "4aba821f-d4ff-498b-a462-c2837dbbba70"

    def get(self, endpoint, params=None, is_auth_required=False):
        headers = {"User-Agent": "IfcOpenShell.bSDD.py/0.8.0"}
        if is_auth_required:
            headers["Authorization"] = "Bearer " + self.get_access_token()
        return requests.get(f"{self.baseurl}{endpoint}", timeout=10, headers=headers, params=params or None).json()

    def _get_deprecated(self, endpoint, params=None, is_auth_required=False):
        headers = {"User-Agent": "IfcOpenShell.bSDD.py/0.8.0"}
        old_baseurl = "https://bs-dd-api-prototype.azurewebsites.net/"
        if is_auth_required:
            headers["Authorization"] = "Bearer " + self.get_access_token()
        return requests.get(f"{old_baseurl}{endpoint}", timeout=10, headers=headers, params=params or None).json()

    def post(self):
        pass  # TODO

    def get_access_token(self):
        if self.access_token and self.access_token_expires_on > time.time():
            return self.access_token
        elif self.refresh_token and self.refresh_token_expires_on > time.time():
            self.get_new_access_token()
        else:
            self.login()
        return self.access_token

    def login(self):
        with http.server.HTTPServer(("", 0), OAuthReceiver) as server:
            state = str(uuid.uuid4())
            query = urllib.parse.urlencode(
                {
                    "client_id": self.client_id,
                    "response_type": "code",
                    # offline_access required to get a refresh_token
                    "scope": "https://buildingsmartservices.onmicrosoft.com/api/read offline_access",
                    "state": state,
                    "redirect_uri": f"http://localhost:{server.server_address[1]}",
                }
            )
            webbrowser.open(f"{self.auth_endpoint}?{query}")
            server.timeout = 75
            server.state = state
            server.handle_request()
            if server.auth_code and server.auth_state == state:
                self.set_tokens_from_response(
                    requests.post(
                        "https://buildingsmartservices.b2clogin.com/tfp/buildingsmartservices.onmicrosoft.com/b2c_1_signupsignin/oauth2/v2.0/token",
                        params={
                            "grant_type": "authorization_code",
                            "code": server.auth_code,
                        },
                    ).json()
                )

    def get_new_access_token(self):
        self.set_tokens_from_response(
            requests.post(
                self.token_endpoint,
                params={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            ).json()
        )

    def set_tokens_from_response(self, response):
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]
        self.access_token_expires_on = time.time() + response["expires_in"]
        self.refresh_token_expires_on = time.time() + response["refresh_token_expires_in"]

    # deprecated
    def Classification(self, namespaceUri, version="v3", languageCode="", includeChildClassificationReferences=True):
        print(f"function 'Client.Classification' is deprecated, use 'Client.get_class' instead")
        return self._get_deprecated(
            f"api/Classification/{version}",
            {
                "namespaceUri": namespaceUri,
                "languageCode": languageCode,
                "includeChildClassificationReferences": includeChildClassificationReferences,
            },
        )

    # deprecated
    def ClassificationSearchOpen(self, SearchText, version="v1", DomainNamespaceUris=None, RelatedIfcEntities=None):
        print(f"function 'Client.ClassificationSearchOpen' is deprecated, use 'Client.search_class' instead")
        if DomainNamespaceUris is None:
            DomainNamespaceUris = []
        if RelatedIfcEntities is None:
            RelatedIfcEntities = []
        return self._get_deprecated(
            f"api/ClassificationSearchOpen/{version}",
            {
                "SearchText": SearchText,
                "DomainNamespaceUris": DomainNamespaceUris,
                "RelatedIfcEntities": RelatedIfcEntities,
            },
        )

    # deprecated
    def Country(self, version="v1"):
        print(f"function 'Client.Country' is deprecated, use 'Client.get_countries' instead")
        return self._get_deprecated(f"api/Country/{version}")

    # deprecated
    def Domain(self, version="v2"):
        print(f"function 'Client.Domain' is deprecated, use 'Client.get_dictionary' and 'Client.get_classes' instead")
        return self._get_deprecated(f"api/Domain/{version}")

    # deprecated
    def Language(self, version="v1"):
        print(f"function 'Client.Language' is deprecated, use 'Client.get_languages' instead")
        return self._get_deprecated(f"api/Language/{version}")

    # deprecated
    def Property(self, namespaceUri, version="v2", languageCode=""):
        print(f"function 'Client.Property' is deprecated, use 'Client.get_property' instead")
        return self._get_deprecated(
            f"api/Property/{version}", {"namespaceUri": namespaceUri, "languageCode": languageCode}
        )

    # deprecated
    def PropertyValue(self, namespaceUri, version="v1", languageCode=""):
        print(f"function 'Client.PropertyValue' is deprecated, use 'Client.get_property_value' instead")
        return self._get_deprecated(
            f"api/PropertyValue/{version}", {"namespaceUri": namespaceUri, "languageCode": languageCode}
        )

    # deprecated
    def ReferenceDocument(self, version="v1"):
        print(f"function 'Client.ReferenceDocument' is deprecated, use 'Client.get_reference_documents' instead")
        return self._get_deprecated(f"api/ReferenceDocument/{version}")

    # deprecated
    def SearchList(self, DomainNamespaceUri, version="v2", SearchText="", LanguageCode="", RelatedIfcEntity=""):
        print(f"function 'Client.SearchList' is deprecated, use 'Client.search_in_dictionary' instead")
        return self._get_deprecated(
            f"api/SearchList/{version}",
            {
                "DomainNamespaceUri": DomainNamespaceUri,
                "SearchText": SearchText,
                "LanguageCode": LanguageCode,
                "RelatedIfcEntity": RelatedIfcEntity,
            },
            is_auth_required=True,
        )

    # deprecated
    def SearchListOpen(self, DomainNamespaceUri, version="v2", SearchText="", LanguageCode="", RelatedIfcEntity=""):
        print(f"function 'Client.SearchListOpen' is deprecated, use 'Client.search_in_dictionary' instead")
        return self.get(
            f"api/SearchListOpen/{version}",
            {
                "DomainNamespaceUri": DomainNamespaceUri,
                "SearchText": SearchText,
                "LanguageCode": LanguageCode,
                "RelatedIfcEntity": RelatedIfcEntity,
            },
        )

    # deprecated
    def Unit(self, version="v1"):
        print(f"function 'Client.Unit' is deprecated, use 'Client.get_units' instead")
        return self.get(f"api/Unit/{version}")

    def get_dictionary(self, dictionary_uri: str = "", version: int = 1) -> DictionaryResponseContractV1:
        """
        Get list of available Dictionaries
        This API replaces Domain
        """
        endpoint = f"Dictionary/v{version}"
        params = {
            "Uri": dictionary_uri,
        }
        return self.get(endpoint, params)

    def get_classes(
        self,
        dictionary_uri: str,
        use_nested_classes: bool = True,
        class_type: ClassTypes = "Class",
        language_code: str = "",
        version: int = 1,
        offset=0,
        limit=1000,
    ) -> DictionaryClassesResponseContractV1:
        """
        Get Dictionary with tree of classes
        This API replaces Domain
        """
        endpoint = f"Dictionary/v{version}/Classes"
        params = {
            "Uri": dictionary_uri,
            "UseNestedClasses": use_nested_classes,
            "ClassType": class_type,
            "languageCode": language_code,
            "offset": offset,
            "limit": limit,
        }
        return self.get(endpoint, params)

    def get_properties(
        self, dictionary_uri: str, offset: int = 0, limit: int = 100, language_code: str = "", version: int = 1
    ) -> DictionaryPropertiesResponseContractV1:
        """
        Get Dictionary with its properties
        """
        endpoint = f"Dictionary/v{version}/Properties"
        params = {"Uri": dictionary_uri, "languageCode": language_code, "offset": offset, "limit": limit}
        return self.get(endpoint, params)

    def get_class(
        self,
        class_uri: str,
        include_class_properties: bool = True,
        include_child_class_reference: bool = True,
        include_class_relations: bool = True,
        include_reverse_relations: bool = False,
        reverse_relation_dictionary_uris: Optional[list[str]] = None,
        language_code: str = "",
        version: int = 1,
    ) -> ClassContractV1:
        """
        Get Class details
        this API replaces Classification
        """
        endpoint = f"Class/v{version}"
        params = {
            "Uri": class_uri,
            "includeClassProperties": include_class_properties,
            "includeChildClassReferences": include_child_class_reference,
            "includeClassRelations": include_class_relations,
            "IncludeReverseRelations": include_reverse_relations,
            "ReverseRelationDictionaryUris": reverse_relation_dictionary_uris,
            "languageCode": language_code,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self.get(endpoint, params)

    def get_property(self, uri, include_classes=False, language_code="", version: int = 4) -> PropertyContractV4:
        """
        Get Property Detail
        this API replaces Property
        """

        endpoint = f"Property/v{version}"
        params = {
            "uri": uri,
            "includeClasses": include_classes,
            "LanguageCode": language_code,
        }
        return self.get(endpoint, params)

    def get_property_value(self, uri, language_code="", version: int = 2) -> PropertyValueContractV4:
        """
        Get Property Value details
        this API replaces PropertyValue
        """
        endpoint = f"PropertyValue/v{version}"
        params = {
            "uri": uri,
            "LanguageCode": language_code,
        }
        return self.get(endpoint, params)

    def search_text(
        self,
        search_text: str,
        type_filter="All",
        dictionary_uris=None,
        version: int = 1,
        offset: int = 0,
        limit: int = 100,
    ) -> TextSearchResponseContractV1:
        """
        Search the bSDD database using free text, get list of Classes and/or Properties matching the text.
        Pagination options are for Classes and Properties combined.
        So if result consists of 10 classes and 5 properties, TotalCount will be 15.
        Classes will be listed first, so if you then use Offset=10 and Limit=5, you will get the 5 properties.
        """
        if dictionary_uris is None:
            dictionary_uris = []
        endpoint = f"TextSearch/v{version}"
        params = {
            "SearchText": search_text,
            "TypeFilter": type_filter,
            "DictionaryUris": dictionary_uris,
            "offset": offset,
            "limit": limit,
        }
        return self.get(endpoint, params)
        pass

    def search_in_dictionary(
        self,
        dictionary_uri: str,
        search_text: str = "",
        language_code: str = "",
        related_ifc_entity: str = "",
        version: int = 1,
        offset: int = 0,
        limit: int = 100,
    ) -> SearchInDictionaryResponseContractV1:
        """
        Search the bSDD database, get list of Classes without details.
        This version uses new naming and returns one Dictionary instead of a list with always one Dictionary.
        This API replaces SearchList.
        """
        endpoint = f"SearchInDictionary/v{version}"
        params = {
            "DictionaryUri": dictionary_uri,
            "SearchText": search_text,
            "LanguageCode": language_code,
            "RelatedIfcEntity": related_ifc_entity,
            "offset": offset,
            "limit": limit,
        }
        return self.get(endpoint, params)

    def search_class(
        self,
        search_text: str,
        dictionary_uris: Optional[list[str]] = None,
        related_ifc_entities: Optional[list[str]] = None,
        version: int = 1,
        offset: int = 0,
        limit: int = 100,
    ) -> ClassSearchResponseContractV1:
        """
        Search the bSDD database using free text, get list of Classes matching the text and optional additional filters.
        this API replaces ClassificationSearch
        """

        if related_ifc_entities is None:
            related_ifc_entities = []
        if dictionary_uris is None:
            dictionary_uris = []
        endpoint = f"Class/Search/v{version}"
        params = {
            "SearchText": search_text,
            "DictionaryUris": dictionary_uris,
            "RelatedIfcEntities": related_ifc_entities,
            "offset": offset,
            "limit": limit,
        }
        return self.get(endpoint, params)

    def get_countries(self, version: int = 1) -> list[CountryContractV1]:
        """
        Get list of all Countries
        this API replaces Country
        """
        endpoint = f"Country/v{version}"
        params = {}
        return self.get(endpoint, params)

    def get_languages(self, version: int = 1) -> list[LanguageContractV1]:
        """
        Get list of available Languages
        this API replaces Language
        """
        endpoint = f"Language/v{version}"
        params = {}
        return self.get(endpoint, params)

    def get_reference_documents(self, version: int = 1) -> list[ReferenceDocumentContractV1]:
        """
        Get list of all ReferenceDocuments
        this API replaces Country
        """
        endpoint = f"ReferenceDocument/v{version}"
        params = {}
        return self.get(endpoint, params)

    def get_units(self, version: int = 1) -> list[UnitContractV1]:
        """
        Get list of all Units
        this API replaces Unit
        """
        endpoint = f"Unit/v{version}"
        params = {}
        return self.get(endpoint, params)


def apply_ifc_classification_properties(ifc_file, element, classificationProperties):
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
        ifcopenshell.api.run("pset.edit_pset", ifc_file, pset=pset, properties={prop["name"]: predefinedValue})
