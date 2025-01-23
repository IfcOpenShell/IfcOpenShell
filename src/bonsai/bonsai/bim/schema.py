# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import ifcopenshell.util.pset
import bonsai.tool as tool


class IfcSchema:
    def __init__(self, schema_identifier="IFC4"):
        if schema_identifier not in ("IFC2X3", "IFC4", "IFC4X3_ADD2"):
            schema_identifier = "IFC4"
        self.schema_identifier = schema_identifier
        self.products = [
            "IfcElement",
            "IfcSpatialElement",
            "IfcGroup",
            "IfcStructural",
            "IfcPositioningElement",
            "IfcMaterialDefinition",
            "IfcParameterizedProfileDef",
            "IfcBoundaryCondition",
            "IfcElementType",
            "IfcAnnotation",
        ]
        self.load_pset_templates()

    def load_pset_templates(self):
        property_paths = tool.Blender.get_data_dir_path("pset").glob("*.ifc")
        self.psetqto = ifcopenshell.util.pset.get_template(self.schema_identifier)
        # Keep only the first template, which is the official buildingSMART one
        self.psetqto.templates = self.psetqto.templates[0:1]
        self.psetqto.get_applicable.cache_clear()
        self.psetqto.get_applicable_names.cache_clear()
        self.psetqto.get_by_name.cache_clear()
        for path in property_paths:
            self.psetqto.templates.append(ifcopenshell.open(path))


ifc = IfcSchema()


def reload(schema_identifier):
    global ifc
    ifc = IfcSchema(schema_identifier)
