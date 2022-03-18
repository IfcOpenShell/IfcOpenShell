# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import bpy
import ifcopenshell
import ifcopenshell.util.schema
import blenderbim.tool as tool


def refresh():
    MaterialsData.is_loaded = False


class MaterialsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_materials": cls.total_materials(),
            "material_types": cls.material_types(),
        }
        cls.is_loaded = True

    @classmethod
    def total_materials(cls):
        return (
            len(tool.Ifc.get().by_type("IfcMaterial"))
            + len(tool.Ifc.get().by_type("IfcMaterialConstituentSet"))
            + len(tool.Ifc.get().by_type("IfcMaterialLayerSet"))
            + len(tool.Ifc.get().by_type("IfcMaterialProfileSet"))
            + len(tool.Ifc.get().by_type("IfcMaterialList"))
        )

    @classmethod
    def material_types(cls):
        material_types = [
            "IfcMaterial",
            "IfcMaterialConstituentSet",
            "IfcMaterialLayerSet",
            "IfcMaterialProfileSet",
            "IfcMaterialList",
        ]
        if tool.Ifc.get_schema() == "IFC2X3":
            material_types = ["IfcMaterial", "IfcMaterialLayerSet", "IfcMaterialList"]
        return [(m, m, "") for m in material_types]
