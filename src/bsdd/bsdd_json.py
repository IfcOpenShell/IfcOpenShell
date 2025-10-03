from __future__ import annotations

from pydantic import BaseModel
from .type_hints import *
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, PrivateAttr, model_validator, ConfigDict
import json
import weakref


def _lower_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s


class CaseInsensitiveModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_lower_first)


class BsddDictionary(CaseInsensitiveModel):
    OrganizationCode: str
    DictionaryCode: str
    DictionaryVersion: str
    LanguageIsoCode: LANGUAGE_ISO_CODE
    LanguageOnly: bool
    UseOwnUri: bool
    DictionaryName: Optional[str] = None
    DictionaryUri: Optional[str] = None
    License: Optional[str] = "MIT"
    LicenseUrl: Optional[str] = None
    ChangeRequestEmailAddress: Optional[str] = None
    ModelVersion: Optional[str] = "2.0"
    MoreInfoUrl: Optional[str] = None
    QualityAssuranceProcedure: Optional[str] = None
    QualityAssuranceProcedureUrl: Optional[str] = None
    ReleaseDate: Optional[datetime] = None
    Status: Optional[STATUS] = None
    Classes: list[BsddClass] = Field(default_factory=list)
    Properties: list[BsddProperty] = Field(default_factory=list)

    @classmethod
    def load(cls, path) -> BsddDictionary:
        """Load from a JSON file and validate via the normalizer above."""
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # The model_validator(before) handles list/dict/nested shapes
        return cls.model_validate(raw)

    def save(self, path):
        with open(path, "w") as file:
            json.dump(self.model_dump(mode="json", exclude_none=True), file)

    # add Parent to children after loading
    def model_post_init(self, context):
        for c in self.Classes:
            c._set_parent(self)
        for p in self.Properties:
            p._set_parent(self)


class BsddClass(CaseInsensitiveModel):
    Code: str
    Name: str
    ClassType: CLASS_TYPE = "Class"
    Definition: Optional[str] = None
    Description: Optional[str] = None
    ParentClassCode: Optional[str | None] = None
    RelatedIfcEntityNamesList: Optional[list[str]] = None
    Synonyms: Optional[list[str]] = None
    ActivationDateUtc: Optional[datetime] = None
    ReferenceCode: Optional[str] = None
    CountriesOfUse: Optional[list[COUNTRY_CODE]] = None
    CountryOfOrigin: Optional[COUNTRY_CODE] = None
    CreatorLanguageIsoCode: Optional[LANGUAGE_ISO_CODE] = None
    DeActivationDateUtc: Optional[datetime] = None
    DeprecationExplanation: Optional[str] = None
    DocumentReference: Optional[str] = None
    OwnedUri: Optional[str] = None
    ReplacedObjectCodes: Optional[list[str]] = None
    ReplacingObjectCodes: Optional[list[str]] = None
    RevisionDateUtc: Optional[datetime] = None
    RevisionNumber: Optional[int] = None
    Status: Optional[CLASS_STATUS] = None
    SubdivisionsOfUse: Optional[list[str]] = None
    Uid: Optional[str] = None
    VersionDateUtc: Optional[datetime] = None
    VersionNumber: Optional[int] = None
    VisualRepresentationUri: Optional[str] = None
    ClassProperties: list[BsddClassProperty] = Field(default_factory=list)
    ClassRelations: list[BsddClassRelation] = Field(default_factory=list)

    _parent_ref: Optional[weakref.ReferenceType[BsddDictionary]] = PrivateAttr(default=None)

    def _set_parent(self, parent: BsddDictionary) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> Optional[BsddDictionary]:
        return self._parent_ref() if self._parent_ref is not None else None

    def model_post_init(self, context):
        for c in self.ClassProperties:
            c._set_parent(self)
        for cr in self.ClassRelations:
            cr._set_parent(self)


class BsddClassRelation(CaseInsensitiveModel):
    RelationType: CLASS_RELATION_TYPE
    RelatedClassUri: str
    RelatedClassName: Optional[str] = None
    Fraction: Optional[float] = None
    OwnedUri: Optional[str] = None

    def _set_parent(self, parent: BsddClass) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> Optional[BsddClass]:
        return self._parent_ref() if self._parent_ref is not None else None


class BsddAllowedValue(CaseInsensitiveModel):
    Code: str
    Value: str
    Description: Optional[str] = None
    Uri: Optional[str] = None
    SortNumber: Optional[int] = None
    OwnedUri: Optional[str] = None


class BsddClassProperty(CaseInsensitiveModel):
    Code: str
    PropertyCode: Optional[str] = None
    PropertyUri: Optional[str] = None
    Description: Optional[str] = None
    PropertySet: Optional[str] = None
    Unit: Optional[str] = None
    PredefinedValue: Optional[str] = None
    IsRequired: Optional[bool] = None
    IsWritable: Optional[bool] = None
    MaxExclusive: Optional[float] = None
    MaxInclusive: Optional[float] = None
    MinExclusive: Optional[float] = None
    MinInclusive: Optional[float] = None
    Pattern: Optional[str] = None
    OwnedUri: Optional[str] = None
    PropertyType: Optional[Literal["Property", "Dependency"]] = None
    SortNumber: Optional[int] = None
    Symbol: Optional[str] = None
    AllowedValues: list[BsddAllowedValue] = Field(default_factory=list)
    _parent_ref: Optional[weakref.ReferenceType[BsddClass]] = PrivateAttr(default=None)

    def _set_parent(self, parent: BsddClass) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> Optional[BsddClass]:
        return self._parent_ref() if self._parent_ref is not None else None

    @model_validator(mode="after")
    def _validate_property_code_or_uri(self):
        """
        only one of PropertyCode or PropertyUri must be set (XOR)
        """
        # normalize whitespace
        code = self.PropertyCode.strip() if self.PropertyCode and isinstance(self.PropertyCode, str) else None
        uri = self.PropertyUri.strip() if self.PropertyUri and isinstance(self.PropertyUri, str) else None

        # XOR: exactly one must be provided
        if bool(code) == bool(uri):
            raise ValueError("Exactly one of PropertyCode or PropertyUri must be provided (not both, not neither)")

        # assign normalized values back
        object.__setattr__(self, "PropertyCode", code)
        object.__setattr__(self, "PropertyUri", uri)
        return self


class BsddProperty(CaseInsensitiveModel):
    Code: str
    Name: str
    Definition: Optional[str] = None
    Description: Optional[str] = None
    DataType: Optional[DATATYPE_TYPE] = None
    Units: Optional[list[UNITS_TYPE]] = None
    Example: Optional[str] = None
    ActivationDateUtc: Optional[datetime] = None
    ConnectedPropertyCodes: Optional[list[str]] = None
    CountriesOfUse: Optional[list[COUNTRY_CODE]] = None
    CountryOfOrigin: Optional[COUNTRY_CODE] = None
    CreatorLanguageIsoCode: Optional[LANGUAGE_ISO_CODE] = None
    DeActivationDateUtc: Optional[datetime] = None
    DeprecationExplanation: Optional[str] = None
    Dimension: Optional[str] = None
    DimensionLength: Optional[int] = None
    DimensionMass: Optional[int] = None
    DimensionTime: Optional[int] = None
    DimensionElectricCurrent: Optional[int] = None
    DimensionThermodynamicTemperature: Optional[int] = None
    DimensionAmountOfSubstance: Optional[int] = None
    DimensionLuminousIntensity: Optional[int] = None
    DocumentReference: Optional[DOCUMENT_TYPE] = None
    DynamicParameterPropertyCodes: Optional[list[str]] = None
    IsDynamic: Optional[bool] = None
    MaxExclusive: Optional[float] = None
    MaxInclusive: Optional[float] = None
    MinExclusive: Optional[float] = None
    MinInclusive: Optional[float] = None
    MethodOfMeasurement: Optional[str] = None
    OwnedUri: Optional[str] = None
    Pattern: Optional[str] = None
    PhysicalQuantity: Optional[str] = None
    PropertyValueKind: Optional[PROPERTY_VALUE_KIND_TYPE] = None
    ReplacedObjectCodes: Optional[list[str]] = None
    ReplacingObjectCodes: Optional[list[str]] = None
    RevisionDateUtc: Optional[datetime] = None
    RevisionNumber: Optional[int] = None
    Status: Optional[PROPERTY_STATUS] = None
    SubdivisionsOfUse: Optional[list[str]] = None
    TextFormat: Optional[str] = None
    Uid: Optional[str] = None
    VersionDateUtc: Optional[datetime] = None
    VersionNumber: Optional[int] = None
    VisualRepresentationUri: Optional[str] = None
    PropertyRelations: list[BsddPropertyRelation] = Field(default_factory=list)
    AllowedValues: list[BsddAllowedValue] = Field(default_factory=list)
    _parent_ref: Optional[weakref.ReferenceType[BsddDictionary]] = PrivateAttr(default=None)

    def _set_parent(self, parent: BsddDictionary) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> Optional[BsddDictionary]:
        return self._parent_ref() if self._parent_ref is not None else None

    def model_post_init(self, context):
        for pr in self.PropertyRelations:
            pr._set_parent(self)


class BsddPropertyRelation(CaseInsensitiveModel):
    RelatedPropertyName: Optional[str] = None
    RelatedPropertyUri: str
    RelationType: PROPERTY_RELATION_TYPE
    OwnedUri: Optional[str] = None

    def _set_parent(self, parent: BsddProperty) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> Optional[BsddProperty]:
        return self._parent_ref() if self._parent_ref is not None else None
