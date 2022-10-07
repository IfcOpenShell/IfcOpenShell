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

import bpy
import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import blenderbim.core.tool
import blenderbim.tool as tool
from mathutils import Matrix
from blenderbim.bim import import_ifc


class Model(blenderbim.core.tool.Model):
    @classmethod
    def generate_occurrence_name(cls, element_type, ifc_class):
        props = bpy.context.scene.BIMModelProperties
        if props.occurrence_name_style == "CLASS":
            return ifc_class[3:]
        elif props.occurrence_name_style == "TYPE":
            return element_type.Name or "Unnamed"
        elif props.occurrence_name_style == "CUSTOM":
            try:
                # Power users gonna power
                return eval(props.occurrence_name_function) or "Instance"
            except:
                return "Instance"

    @classmethod
    def get_extrusion(cls, representation):
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                return item
            elif item.is_a("IfcBooleanResult"):
                item = item.FirstOperand
            else:
                break

    @classmethod
    def load_openings(cls, element, openings):
        if not openings:
            return []
        obj = tool.Ifc.get_object(element)
        ifc_import_settings = import_ifc.IfcImportSettings.factory()
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        openings = set(openings)
        openings -= ifc_importer.create_products(openings)
        for opening in openings or []:
            if tool.Ifc.get_object(opening):
                continue
            opening_obj = ifc_importer.create_product(opening)
            if obj:
                opening_obj.parent = obj
                opening_obj.matrix_parent_inverse = obj.matrix_world.inverted()
        for obj in ifc_importer.added_data.values():
            bpy.context.scene.collection.objects.link(obj)
        return ifc_importer.added_data.values()

    @classmethod
    def clear_scene_openings(cls):
        props = bpy.context.scene.BIMModelProperties
        has_deleted_opening = True
        while has_deleted_opening:
            has_deleted_opening = False
            for i, opening in enumerate(props.openings):
                if not opening.obj:
                    props.openings.remove(i)
                    has_deleted_opening = True

    @classmethod
    def get_manual_booleans(cls, element):
        results = []
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not body:
            return []
        clippings = []
        items = list(body.Items)
        while items:
            item = items.pop()
            if item.is_a() == "IfcBooleanResult":
                clippings.append(item.SecondOperand)
                items.append(item.FirstOperand)
            elif item.is_a("IfcBooleanClippingResult"):
                items.append(item.FirstOperand)
        for clipping in clippings:
            if clipping.is_a("IfcHalfSpaceSolid") and clipping.BaseSurface.is_a("IfcPlane"):
                placement = Matrix(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement).tolist())
                position = clipping.BaseSurface.Position
                position = Matrix(ifcopenshell.util.placement.get_axis2placement(position).tolist())
                results.append(
                    {"type": "IfcBooleanResult", "operand_type": "IfcHalfSpaceSolid", "matrix": position}
                )
        return results
