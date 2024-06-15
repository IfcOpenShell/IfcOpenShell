# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import re
import pathlib
import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.type
from ifcopenshell.entity_instance import entity_instance
from functools import lru_cache
from typing import List, Optional

templates: dict[str, "PsetQto"] = {}


def get_template(schema: str) -> "PsetQto":
    global templates
    if schema not in templates:
        templates[schema] = PsetQto(schema)
    return templates[schema]


class PsetQto:
    # fmt: off
    templates_path = {
        "IFC2X3": "Pset_IFC2X3.ifc",
        "IFC4": "Pset_IFC4_ADD2.ifc",
        "IFC4X3_ADD2": "Pset_IFC4X3.ifc"
    }
    # fmt: on

    def __init__(self, schema_identifier: str, templates=None) -> None:
        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_identifier)
        if not templates:
            folder_path = pathlib.Path(__file__).parent.absolute()
            path = str(folder_path.joinpath("schema", self.templates_path[schema_identifier]))
            templates = [ifcopenshell.open(path)]
            # See bug 3583. We backport this change from IFC4X3 because it just makes sense.
            # Users aren't forced to use it.
            if schema_identifier == "IFC4":
                for element in templates[0].by_type("IfcPropertySetTemplate"):
                    if element.TemplateType == "QTO_OCCURRENCEDRIVEN":
                        element.TemplateType = "QTO_TYPEDRIVENOVERRIDE"
        self.templates = templates

    @lru_cache()
    def get_applicable(
        self, ifc_class="", predefined_type="", pset_only=False, qto_only=False
    ) -> List[entity_instance]:
        any_class = not ifc_class
        if not any_class:
            entity = self.schema.declaration_by_name(ifc_class)
        result = []
        for template in self.templates:
            for prop_set in template.by_type("IfcPropertySetTemplate"):
                if pset_only:
                    if prop_set.TemplateType and prop_set.TemplateType.startswith("QTO_"):
                        continue
                if qto_only:
                    if prop_set.TemplateType and prop_set.TemplateType.startswith("PSET_"):
                        continue
                if any_class or self.is_applicable(
                    entity, prop_set.ApplicableEntity or "IfcRoot", predefined_type, prop_set.TemplateType
                ):
                    result.append(prop_set)
        return result

    @lru_cache()
    def get_applicable_names(self, ifc_class: str, predefined_type="", pset_only=False, qto_only=False) -> List[str]:
        """Return names instead of objects for other use eg. enum"""
        return [prop_set.Name for prop_set in self.get_applicable(ifc_class, predefined_type, pset_only, qto_only)]

    def is_applicable(
        self, entity: entity_instance, applicables: str, predefined_type="", template_type="NOTDEFINED"
    ) -> bool:
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
            matched_type = match.group(3)
            if matched_type and not predefined_type:
                continue
            # Case insensitive to handle things like material categories
            elif matched_type and predefined_type.lower() != match.group(3).lower():
                continue

            applicable_class = match.group(1)
            if ifcopenshell.util.schema.is_a(entity, applicable_class):
                return True
            # There is an implementer agreement that if the template type is
            # type based, the type need not be explicitly mentioned
            # https://github.com/buildingSMART/IFC4.3.x-development/issues/22
            # This will be fixed in IFC4.3
            template_type = template_type or ""
            if "TYPE" in template_type and ifcopenshell.util.schema.is_a(entity, "IfcTypeObject"):
                types = ifcopenshell.util.type.get_applicable_types(applicable_class, "IFC4")
                if not types:
                    # Abstract classes will not have an "applicable type" but
                    # the implementer agreement still applies to them.
                    occurrence_class = None
                    try:
                        occurrence_class = self.schema.declaration_by_name(applicable_class + "Type")
                    except:
                        try:
                            occurrence_class = self.schema.declaration_by_name("IfcType" + applicable_class[3:])
                        except:
                            pass
                    if occurrence_class:
                        types = [occurrence_class.name()]
                for ifc_type in types:
                    if ifcopenshell.util.schema.is_a(entity, ifc_type):
                        return True
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
