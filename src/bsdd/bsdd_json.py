from __future__ import annotations
from dataclasses import dataclass, field, asdict
import datetime
import os
import json

@dataclass
class Dictionary:
    OrganizationCode: str = field(init=True)
    DictionaryCode: str = field(init=True)
    DictionaryName: str = field(init=True)
    DictionaryVersion: str = field(init=True)
    LanguageIsoCode: str = field(init=True)
    LanguageOnly: bool = field(init=True)
    UseOwnUri: bool = field(init=True)
    DictionaryUri: str = field(init=False, default="")
    License: str = field(init=False, default=None)
    LicenseUrl: str = field(init=False, default=None)
    ChangeRequestEmailAddress: str = field(init=False, default=None)
    ModelVersion: str = field(init=False, default="2.0")
    MoreInfoUrl: str = field(init=False, default=None)
    QualityAssuranceProcedure: str = field(init=False, default=None)
    QualityAssuranceProcedureUrl: str = field(init=False, default=None)
    ReleaseDate: datetime = field(init=False, default=None)
    Status: str = field(init=False, default=None)
    Classes: list[Class] = field(init=True, default_factory=list)
    Properties: list[Property] = field(init=True, default_factory=list)

    def base(self) -> str:
        return self.DictionaryUri if self.UseOwnUri else "https://identifier.buildingsmart.org"

    def uri(self) -> str:
        duri = self.base()
        orga_code = self.OrganizationCode
        dict_code = self.DictionaryCode
        version = self.DictionaryVersion
        return "/".join([duri, "uri", orga_code, f"{dict_code}/{version}"])

@dataclass
class Class:
    dictionary: field(init=True)
    Code: str = field(init=True)
    Name: str = field(init=True)
    ClassType: str = field(init=True)
    Definition: str = field(init=False, default=None)
    Description: str = field(init=False, default=None)
    ParentClassCode: str = field(init=False, default=None)
    RelatedIfcEntityNamesList: list[str] = field(init=False, default=None)
    Synonyms: list[str] = field(init=False, default=None)
    ActivationDateUtc: datetime = field(init=False, default=None)
    ReferenceCode: str = field(init=False, default=None)
    CountriesOfUse: list[str] = field(init=False, default=None)
    CountryOfOrigin: str = field(init=False, default=None)
    CreatorLanguageIsoCode: str = field(init=False, default=None)
    DeActivationDateUtc: datetime = field(init=False, default=None)
    DeprecationExplanation: str = field(init=False, default=None)
    DocumentReference: str = field(init=False, default=None)
    OwnedUri: str = field(init=False, default=None)
    ReplacedObjectCodes: list[str] = field(init=False, default=None)
    ReplacingObjectCodes: list[str] = field(init=False, default=None)
    RevisionDateUtc: datetime = field(init=False, default=None)
    RevisionNumber: int = field(init=False, default=None)
    Status: str = field(init=False, default=None)
    SubdivisionsOfUse: list[str] = field(init=False, default=None)
    Uid: str = field(init=False, default=None)
    VersionDateUtc: datetime = field(init=False, default=None)
    VersionNumber: int = field(init=False, default=None)
    VisualRepresentationUri: str = field(init=False, default=None)
    ClassProperties: list[ClassProperty] = field(init=True, default_factory=list)
    ClassRelations: list[ClassRelation] = field(init=True, default_factory=list)

    def __post_init__(self):
        """remove dictionary from fields list else asdict is not working"""
        if "dictionary" in self.__dataclass_fields__:
            self.__dataclass_fields__.pop("dictionary")
        self.dictionary.Classes.append(self)

    def uri(self):
        return "/".join([self.dictionary.uri(), "class", self.Code])

    def __eq__(self, other:Class):
        if not isinstance(other, Class):
            return False
        return asdict(self) == asdict(other)

@dataclass
class ClassRelation:
    RelationType: str = field(init=True)
    RelatedClassUri: str = field(init=True)
    RelatedClassName: str = field(init=False, default=None)
    Fraction: float = field(init=False, default=None)
    OwnedUri: str = field(init=False, default=None)


@dataclass
class Property:
    Code: str = field(init=True)
    Name: str = field(init=True)
    Definition: str = field(init=False, default=None)
    Description: str = field(init=False, default=None)
    DataType: str = field(init=False, default=None)
    Units: list[str] = field(init=False, default=None)
    Example: str = field(init=False, default=None)
    ActivationDateUtc: datetime = field(init=False, default=None)
    ConnectedPropertyCodes: list[str] = field(init=False, default=None)
    CountriesOfUse: list[str] = field(init=False, default=None)
    CountryOfOrigin: str = field(init=False, default=None)
    CreatorLanguageIsoCode: str = field(init=False, default=None)
    DeActivationDateUtc: datetime = field(init=False, default=None)
    DeprecationExplanation: str = field(init=False, default=None)
    Dimension: str = field(init=False, default=None)
    DimensionLength: int = field(init=False, default=None)
    DimensionMass: int = field(init=False, default=None)
    DimensionTime: int = field(init=False, default=None)
    DimensionElectricCurrent: int = field(init=False, default=None)
    DimensionThermodynamicTemperature: int = field(init=False, default=None)
    DimensionAmountOfSubstance: int = field(init=False, default=None)
    DimensionLuminousIntensity: int = field(init=False, default=None)
    DocumentReference: str = field(init=False, default=None)
    DynamicParameterPropertyCodes: list[str] = field(init=False, default=None)
    IsDynamic: bool = field(init=False, default=None)
    MaxExclusive: float = field(init=False, default=None)
    MaxInclusive: float = field(init=False, default=None)
    MinExclusive: float = field(init=False, default=None)
    MinInclusive: float = field(init=False, default=None)
    MethodOfMeasurement: str = field(init=False, default=None)
    OwnedUri: str = field(init=False, default=None)
    Pattern: str = field(init=False, default=None)
    PhysicalQuantity: str = field(init=False, default=None)
    PropertyValueKind: str = field(init=False, default=None)
    ReplacedObjectCodes: list[str] = field(init=False, default=None)
    ReplacingObjectCodes: list[str] = field(init=False, default=None)
    RevisionDateUtc: datetime = field(init=False, default=None)
    RevisionNumber: int = field(init=False, default=None)
    Status: str = field(init=False, default=None)
    SubdivisionsOfUse: list[str] = field(init=False, default=None)
    TextFormat: str = field(init=False, default=None)
    Uid: str = field(init=False, default=None)
    VersionDateUtc: datetime = field(init=False, default=None)
    VersionNumber: int = field(init=False, default=None)
    VisualRepresentationUri: str = field(init=False, default=None)
    PropertyRelations: list[PropertyRelation] = field(init=True, default_factory=list)
    AllowedValues: list[AllowedValue] = field(init=True, default_factory=list)

    def __hash__(self) -> int:
        return hash(str(asdict(self)))


@dataclass
class ClassProperty:
    Code: str = field(init=True)
    PropertyCode: str = field(init=True)
    PropertyUri: str = field(init=True)
    Description: str = field(init=False, default=None)
    PropertySet: str = field(init=False, default=None)
    Unit: str = field(init=False, default=None)
    PredefinedValue: str = field(init=False, default=None)
    IsRequired: bool = field(init=False, default=None)
    IsWritable: bool = field(init=False, default=None)
    MaxExclusive: float = field(init=False, default=None)
    MaxInclusive: float = field(init=False, default=None)
    MinExclusive: float = field(init=False, default=None)
    MinInclusive: float = field(init=False, default=None)
    Pattern: str = field(init=False, default=None)
    OwnedUri: str = field(init=False, default=None)
    PropertyType: str = field(init=False, default=None)
    SortNumber: int = field(init=False, default=None)
    Symbol: str = field(init=False, default=None)
    AllowedValues: list[AllowedValue] = field(init=False, default_factory=list)


@dataclass
class PropertyRelation:
    RelatedPropertyName: str = field(init=False, default=None)
    RelatedPropertyUri: str = field(init=True)
    RelationType: str = field(init=True)
    OwnedUri: str = field(init=False, default=None)


@dataclass
class AllowedValue:
    Code: str = field(init=True)
    Value: str = field(init=True)
    Description: str = field(init=False, default=None)
    Uri: str = field(init=False, default=None)
    SortNumber: int = field(init=False, default=None)
    OwnedUri: str = field(init=False, default=None)


def export(dictionary: Dictionary, path: str | os.PathLike):
    with open(path, "w") as file:
        d = asdict(dictionary, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
        json.dump(d , file, indent=2)
