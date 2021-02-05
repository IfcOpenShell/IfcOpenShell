import pathlib
import re
from functools import lru_cache
from typing import List, Generator, Optional

import ifcopenshell
from ifcopenshell.entity_instance import entity_instance


class PsetQto:
    templates_path = {
        "IFC4": "Pset_IFC4_ADD2.ifc",
    }

    def __init__(self, schema: str, templates=None) -> None:
        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema)
        if not templates:
            folder_path = pathlib.Path(__file__).parent.absolute()
            path = folder_path.joinpath("schema", self.templates_path[schema])
            templates = [ifcopenshell.open(path)]
        self.templates = templates

    @lru_cache()
    def get_applicable(
        self, ifc_class="", predefined_type="", pset_only=False, qto_only=False
    ) -> Generator[entity_instance, entity_instance, None]:
        any_class = not ifc_class
        if not any_class:
            entity = self.schema.declaration_by_name(ifc_class)
        for template in self.templates:
            for prop_set in template.by_type("IfcPropertySetTemplate"):
                if pset_only:
                    if prop_set.Name.startswith("Qto_"):
                        continue
                if qto_only:
                    if not prop_set.Name.startswith("Qto_"):
                        continue
                if any_class or self.is_applicable(entity, prop_set.ApplicableEntity or "IfcRoot", predefined_type):
                    yield prop_set

    def get_applicable_names(self, ifc_class: str, predefined_type="", pset_only=False, qto_only=False) -> List[str]:
        """Return names instead of objects for other use eg. enum"""
        return [prop_set.Name for prop_set in self.get_applicable(ifc_class, predefined_type, pset_only, qto_only)]

    def is_applicable(self, entity: entity_instance, applicables: str, predefined_type="") -> bool:
        """applicables can have multiple possible patterns :
        IfcBoilerType                               (IfcClass)
        IfcBoilerType/STEAM                         (IfcClass/PREDEFINEDTYPE)
        IfcBoilerType[PerformanceHistory]           (IfcClass[PerformanceHistory])
        IfcBoilerType/STEAM[PerformanceHistory]     (IfcClass/PREDEFINEDTYPE[PerformanceHistory])
        """
        for applicable in applicables.split(","):
            match = re.match(r"(\w+)(\[\w+\])*/*(\w+)*(\[\w+\])*", applicable)
            if not match:
                continue
            # Uncomment if usage found
            # applicable_perf_history = match.group(2) or match.group(4)
            if predefined_type and predefined_type != match.group(3):
                continue

            applicable_class = match.group(1)
            if entity.name() == applicable_class:
                return True
            if entity.supertype():
                return self.is_applicable(entity.supertype(), applicable_class)
        return False

    @lru_cache()
    def get_by_name(self, name: str) -> Optional[entity_instance]:
        for template in self.templates:
            for prop_set in template.by_type("IfcPropertySetTemplate"):
                if prop_set.Name == name:
                    return prop_set
        return None

    def is_templated(self, name: str) -> bool:
        return bool(self.get_by_name(name))
