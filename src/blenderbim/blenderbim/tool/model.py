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
from mathutils import Matrix, Vector
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
        ifc_importer.material_creator.load_existing_materials()
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
    def get_material_layer_parameters(cls, element):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        offset = 0.0
        thickness = 0.0
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialLayerSetUsage"):
                offset = material.OffsetFromReferenceLine * unit_scale
                material = material.ForLayerSet
            if material.is_a("IfcMaterialLayerSet"):
                thickness = sum([l.LayerThickness for l in material.MaterialLayers]) * unit_scale
        return {"thickness": thickness, "offset": offset}

    @classmethod
    def get_manual_booleans(cls, element):
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not body:
            return []
        booleans = []
        items = list(body.Items)
        while items:
            item = items.pop()
            if item.is_a() == "IfcBooleanResult":
                booleans.append(item)
                items.append(item.FirstOperand)
            elif item.is_a("IfcBooleanClippingResult"):
                items.append(item.FirstOperand)
        return booleans

    @classmethod
    def get_wall_axis(cls, obj, layers=None):
        x_values = [v[0] for v in obj.bound_box]
        min_x = min(x_values)
        max_x = max(x_values)
        axes = {}
        if layers:
            axes = {
                "base": [
                    (obj.matrix_world @ Vector((min_x, layers["offset"], 0.0))).to_2d(),
                    (obj.matrix_world @ Vector((max_x, layers["offset"], 0.0))).to_2d(),
                ],
                "side": [
                    (obj.matrix_world @ Vector((min_x, layers["offset"] + layers["thickness"], 0.0))).to_2d(),
                    (obj.matrix_world @ Vector((max_x, layers["offset"] + layers["thickness"], 0.0))).to_2d(),
                ],
            }
        axes["reference"] = [
            (obj.matrix_world @ Vector((min_x, 0.0, 0.0))).to_2d(),
            (obj.matrix_world @ Vector((max_x, 0.0, 0.0))).to_2d(),
        ]
        return axes

    @classmethod
    def regenerate_array(cls, parent, data):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj_stack = [parent]
        for array in data:
            child_i = 0
            existing_children = set(array["children"])
            total_existing_children = len(array["children"])
            children_elements = []
            children_objs = []
            for i in range(0, array["count"]):
                if i == 0:
                    continue
                offset = Vector((i * array["x"] * unit_scale, i * array["y"] * unit_scale, i * array["z"] * unit_scale))
                for obj in obj_stack:
                    if child_i >= total_existing_children:
                        child_obj = tool.Spatial.duplicate_object_and_data(obj)
                        child_element = tool.Spatial.run_root_copy_class(obj=child_obj)
                    else:
                        global_id = array["children"][child_i]
                        try:
                            child_element = tool.Ifc.get().by_guid(global_id)
                            child_obj = tool.Ifc.get_object(child_element)
                            assert child_obj
                        except:
                            child_obj = tool.Spatial.duplicate_object_and_data(obj)
                            child_element = tool.Spatial.run_root_copy_class(obj=child_obj)

                    child_psets = ifcopenshell.util.element.get_psets(child_element)
                    child_pset = child_psets.get("BBIM_Array")
                    if child_pset:
                        ifcopenshell.api.run(
                            "pset.edit_pset",
                            tool.Ifc.get(),
                            product=child_element,
                            pset=tool.Ifc.get().by_id(child_pset["id"]),
                            properties={"Data": None},
                        )

                    new_matrix = obj.matrix_world.copy()
                    new_matrix.col[3] = (obj.matrix_world.col[3].to_3d() + offset).to_4d()
                    child_obj.matrix_world = new_matrix
                    children_objs.append(child_obj)
                    children_elements.append(child_element)
                    child_i += 1
            obj_stack.extend(children_objs)
            array["children"] = [e.GlobalId for e in children_elements]

            removed_children = set(existing_children) - set(array["children"])
            for removed_child in removed_children:
                element = tool.Ifc.get().by_guid(removed_child)
                obj = tool.Ifc.get_object(element)
                if obj:
                    bpy.data.objects.remove(obj)
                # TODO: Not sufficient, refactor OverrideDeleteTrait

            bpy.context.view_layer.update()
