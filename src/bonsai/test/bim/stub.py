# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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


from typing import Union, Any, Optional


class bSDDClientStub:
    def get_dictionary(self, dictionary_uri=None, include_test_dictionaries=False):
        dicts = {
            "dictionaries": [
                {
                    "availableLanguages": [{"code": "EN", "name": "English"}],
                    "code": "LCA",
                    "uri": "https://identifier.buildingsmart.org/uri/LCA",
                    "name": "LCA indicators and modules",
                    "version": "3.0",
                    "organizationCodeOwner": "LCA",
                    "organizationNameOwner": "buildingSMART Sustainability Strategic Group",
                    "defaultLanguageCode": "EN",
                    "isLatestVersion": True,
                    "isVerified": False,
                    "isPrivate": False,
                    "license": "No license (rights reserved)",
                    "licenseUrl": "https://technical.buildingsmart.org/services/bsdd/license/",
                    "qualityAssuranceProcedure": "EN ISO 23386:2020",
                    "status": "Active",
                    "moreInfoUrl": "https://www.lignum.ch/leistungen/projekte/buildingsmart-data-dictionary-bsdd/",
                    "releaseDate": "2023-12-01T14:14:19Z",
                    "lastUpdatedUtc": "2023-12-01T14:17:53Z",
                },
                {
                    "availableLanguages": [{"code": "EN", "name": "English"}],
                    "code": "BonsaiTestDict",
                    "uri": "https://identifier.buildingsmart.org/uri/BonsaiTestDict",
                    "name": "BonsaiTestDict",
                    "version": "3.0",
                    "organizationCodeOwner": "LCA",
                    "organizationNameOwner": "buildingSMART Sustainability Strategic Group",
                    "defaultLanguageCode": "EN",
                    "isLatestVersion": True,
                    "isVerified": False,
                    "isPrivate": False,
                    "license": "No license (rights reserved)",
                    "licenseUrl": "https://technical.buildingsmart.org/services/bsdd/license/",
                    "qualityAssuranceProcedure": "EN ISO 23386:2020",
                    "status": "Active",
                    "moreInfoUrl": "https://www.lignum.ch/leistungen/projekte/buildingsmart-data-dictionary-bsdd/",
                    "releaseDate": "2023-12-01T14:14:19Z",
                    "lastUpdatedUtc": "2023-12-01T14:17:53Z",
                },
            ],
            "totalCount": 2,
            "offset": 0,
            "count": 2,
        }
        if not dictionary_uri:
            return dicts
        for dictionary in dicts["dictionaries"]:
            if dictionary["uri"] == dictionary_uri:
                dicts["dictionaries"] = [dictionary]
                return dicts
        assert False, f"Could not find dictionary uri {dictionary_uri}"

    def get_classes(
        self,
        dictionary_uri: str,
        use_nested_classes: bool = True,
        class_type="Class",
        search_text: str = "",
        related_ifc_entity: str = "",
        language_code: str = "",
        version: int = 1,
        offset=0,
        limit=1000,
    ):
        classes = {
            "classes": [],
            "classesTotalCount": 2,
            "classesOffset": 0,
            "classesCount": 2,
            "code": "LCA",
            "uri": "https://identifier.buildingsmart.org/uri/LCA/LCA/3.0",
            "name": "LCA indicators and modules",
            "version": "3.0",
            "organizationCodeOwner": "LCA",
            "organizationNameOwner": "buildingSMART Sustainability Strategic Group",
            "defaultLanguageCode": "EN",
            "isLatestVersion": True,
            "isVerified": False,
            "isPrivate": False,
            "license": "No license (rights reserved)",
            "licenseUrl": "https://technical.buildingsmart.org/services/bsdd/license/",
            "qualityAssuranceProcedure": "EN ISO 23386:2020",
            "status": "Preview",
            "moreInfoUrl": "https://www.lignum.ch/leistungen/projekte/buildingsmart-data-dictionary-bsdd/",
            "releaseDate": "2023-12-01T14:14:19Z",
            "lastUpdatedUtc": "2023-12-01T14:17:53Z",
        }
        if dictionary_uri == "https://identifier.buildingsmart.org/uri/LCA":
            classes["classes"].extend(
                [
                    {
                        "uri": "https://identifier.buildingsmart.org/uri/LCA/LCA/3.0/class/Acidification",
                        "code": "Acidification",
                        "name": "Acidification",
                        "classType": "Class",
                        "referenceCode": "Acidification",
                        "descriptionPart": "",
                    },
                    {
                        "uri": "https://identifier.buildingsmart.org/uri/LCA/LCA/3.0/class/Biogeniccarboncontentatthefactorygate",
                        "code": "Biogeniccarboncontentatthefactorygate",
                        "name": "Biogenic carbon content at the factory gate",
                        "classType": "Class",
                        "referenceCode": "Biogeniccarboncontentatthefactorygate",
                        "descriptionPart": "",
                    },
                ]
            )
        elif dictionary_uri == "https://identifier.buildingsmart.org/uri/BonsaiTestDict":
            classes["classes"].extend(
                [
                    {
                        "uri": "https://identifier.buildingsmart.org/uri/BonsaiTestDict/class/BonsaiReferenceA",
                        "code": "BonsaiReferenceA",
                        "name": "BonsaiReferenceA",
                        "classType": "Class",
                        "referenceCode": "BonsaiReferenceA",
                        "descriptionPart": "",
                    },
                    {
                        "uri": "https://identifier.buildingsmart.org/uri/BonsaiTestDict/class/BonsaiReferenceB",
                        "code": "BonsaiReferenceB",
                        "name": "BonsaiReferenceB",
                        "classType": "Class",
                        "referenceCode": "BonsaiReferenceB",
                        "descriptionPart": "",
                    },
                ]
            )
        if offset != 0:
            classes["classes"].clear()
            classes["classesTotalCount"] = 0
            classes["classesCount"] = 0
        return classes

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
    ):
        result = {
            "classType": "Class",
            "referenceCode": "apple",
            "relatedIfcEntityNames": ["IfcCommunicationsAppliance"],
            "parentClassReference": {
                "uri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1/class/fruit",
                "name": "Fruit",
                "code": "fruit",
            },
            "hierarchy": [
                {
                    "level": 1,
                    "name": "Fruit",
                    "code": "fruit",
                    "uri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1/class/fruit",
                },
                {
                    "level": 2,
                    "name": "Apple",
                    "code": "apple",
                    "uri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1/class/apple",
                },
            ],
            "classProperties": [
                {
                    "name": "Height",
                    "uri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1/class/apple/prop/SizeSet/height",
                    "description": "The height of an apple",
                    "definition": "Distance from bottom to top of something standing upright",
                    "dataType": "Real",
                    "dimension": "1 0 0 0 0 0 0",
                    "dimensionLength": 1,
                    "dimensionMass": 0,
                    "dimensionTime": 0,
                    "dimensionElectricCurrent": 0,
                    "dimensionThermodynamicTemperature": 0,
                    "dimensionAmountOfSubstance": 0,
                    "dimensionLuminousIntensity": 0,
                    "isRequired": True,
                    "isWritable": True,
                    "maxInclusive": 25,
                    "minExclusive": 1,
                    "physicalQuantity": "Height",
                    "propertyCode": "height",
                    "propertyDictionaryName": "Fruit and vegetables",
                    "propertyDictionaryUri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1",
                    "propertyUri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1/prop/height",
                    "propertySet": "SizeSet",
                    "propertyStatus": "Active",
                    "propertyValueKind": "Single",
                    "units": ["cm"],
                    "qudtCodes": ["CentiM"],
                },
                {
                    "name": "Volume",
                    "uri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1/class/apple/prop/SizeSet/volume",
                    "description": "The volume of an apple",
                    "definition": "Volume is a scalar quantity expressing the amount of three-dimensional space enclosed by a closed surface. Volume is often quantified numerically using the SI derived unit, the cubic metre",
                    "dataType": "Real",
                    "dimension": "3 0 0 0 0 0 0",
                    "dimensionLength": 3,
                    "dimensionMass": 0,
                    "dimensionTime": 0,
                    "dimensionElectricCurrent": 0,
                    "dimensionThermodynamicTemperature": 0,
                    "dimensionAmountOfSubstance": 0,
                    "dimensionLuminousIntensity": 0,
                    "example": "For example, the space that a substance or 3D shape occupies or contains.",
                    "isRequired": True,
                    "isWritable": True,
                    "maxInclusive": 20,
                    "minExclusive": 1,
                    "physicalQuantity": "Volume",
                    "propertyCode": "volume",
                    "propertyDictionaryName": "Fruit and vegetables",
                    "propertyDictionaryUri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1",
                    "propertyUri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1/prop/volume",
                    "propertySet": "SizeSet",
                    "propertyStatus": "Active",
                    "propertyValueKind": "Single",
                    "units": ["cm³"],
                    "qudtCodes": ["CentiM3"],
                },
            ],
            "dictionaryUri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1",
            "activationDateUtc": "2022-09-26T00:00:00Z",
            "code": "apple",
            "creatorLanguageCode": "en-GB",
            "countriesOfUse": [],
            "definition": "The round fruit of a tree of the rose family, which typically has thin green or red skin and crisp flesh",
            "name": "Apple",
            "uri": "https://identifier.buildingsmart.org/uri/bs-agri/fruitvegs/1.1/class/apple",
            "replacedObjectCodes": [],
            "replacingObjectCodes": [],
            "revisionNumber": 0,
            "status": "Active",
            "subdivisionsOfUse": [],
            "versionDateUtc": "2022-09-26T00:00:00Z",
            "versionNumber": 1,
        }
        return result
