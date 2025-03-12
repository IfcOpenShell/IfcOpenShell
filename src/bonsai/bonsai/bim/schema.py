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
import bpy
import bpy_restrict_state


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
        self.psetqto = ifcopenshell.util.pset.get_template(self.schema_identifier)
        # Keep only the first template, which is the official buildingSMART one
        self.psetqto.templates = self.psetqto.templates[0:1]
        self.psetqto.get_applicable.cache_clear()
        self.psetqto.get_applicable_names.cache_clear()
        self.psetqto.get_by_name.cache_clear()

        # During register we cannot access the context either way.
        if isinstance(bpy.context, bpy_restrict_state._RestrictContext):
            return
        for path in tool.Blender.get_data_dir_paths("pset", "*.ifc"):
            self.psetqto.templates.append(ifcopenshell.open(path))


# TODO: do we really need to load it on module import?
# Loading it on IFC load should be enough.
ifc = IfcSchema()


def reload(schema_identifier):
    global ifc
    ifc = IfcSchema(schema_identifier)
