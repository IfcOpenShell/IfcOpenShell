# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Cyril Waechter <cyril@biminsight.ch>
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
import logging
import ifcopenshell.api
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.boundary.data import Data
import blenderbim.bim.import_ifc as import_ifc


def get_boundaries_collection(blender_space):
    space_collection = bpy.data.collections.get(blender_space.name, blender_space.users_collection[0])
    collection_name = f"Boundaries/{blender_space.BIMObjectProperties.ifc_definition_id}"
    boundaries_collection = space_collection.children.get(collection_name)
    if not boundaries_collection:
        boundaries_collection = bpy.data.collections.new(collection_name)
        space_collection.children.link(boundaries_collection)
    return boundaries_collection


class Loader:
    def __init__(self):
        self.ifc_file = None
        self.logger = None
        self.ifc_importer = None
        self.settings = None
        self.load_settings()
        self.load_importer()

    def create_mesh(self, boundary):
        # ConnectionGeometry is optional in IFC schema for some reasons.
        if not boundary.ConnectionGeometry:
            return None
        surface = boundary.ConnectionGeometry.SurfaceOnRelatingElement
        # workaround for invalid geometry provided by Revit. See https://github.com/IfcOpenShell/IfcOpenShell/issues/635#issuecomment-770366838
        if surface.is_a("IfcCurveBoundedPlane") and not getattr(surface, "InnerBoundaries", None):
            surface.InnerBoundaries = ()
        shape = ifcopenshell.geom.create_shape(self.settings, surface)
        mesh = self.ifc_importer.create_mesh(None, shape)
        self.ifc_importer.link_mesh(shape, mesh)
        return mesh

    def load_settings(self):
        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.EXCLUDE_SOLIDS_AND_SURFACES, False)
        self.settings.set(self.settings.USE_BREP_DATA, False)

    def load_importer(self):
        self.ifc_file = tool.Ifc.get()
        self.logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(bpy.context, IfcStore.path, self.logger)
        self.ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        self.ifc_importer.file = self.ifc_file

    def load_boundary(self, boundary_id, blender_space):
        boundary = self.ifc_file.by_id(boundary_id)
        obj = tool.Ifc.get_object(boundary)
        if obj:
            return obj
        mesh = self.create_mesh(boundary)
        obj = bpy.data.objects.new(f"{boundary.is_a()}/{boundary.Name}", mesh)
        obj.matrix_world = blender_space.matrix_world
        boundaries_collection = get_boundaries_collection(blender_space)
        boundaries_collection.objects.link(obj)
        tool.Ifc.link(boundary, obj)
        return obj


class LoadProjectSpaceBoundaries(bpy.types.Operator):
    bl_idname = "bim.load_project_space_boundaries"
    bl_label = "Load all project space boundaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        loader = Loader()
        if not Data.is_loaded:
            Data.load(tool.Ifc.get())
        for space_id, boundaries_id in Data.spaces.items():
            blender_space = tool.Ifc.get_object(tool.Ifc.get().by_id(space_id))
            for boundary_id in boundaries_id:
                loader.load_boundary(boundary_id, blender_space)
        return {"FINISHED"}


class LoadBoundary(bpy.types.Operator):
    bl_idname = "bim.load_boundary"
    bl_label = "Load boundary"
    bl_options = {"REGISTER", "UNDO"}
    boundary_id: bpy.props.IntProperty()

    def execute(self, context):
        loader = Loader()
        blender_space = context.active_object
        for obj in context.visible_objects:
            obj.select_set(False)
        obj = loader.load_boundary(self.boundary_id, blender_space)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return {"FINISHED"}


class LoadSpaceBoundaries(bpy.types.Operator):
    bl_idname = "bim.load_space_boundaries"
    bl_label = "Load selected space boundaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        blender_space = context.active_object
        oprops = context.active_object.BIMObjectProperties
        loader = Loader()
        if not Data.is_loaded:
            Data.load(tool.Ifc.get())
        for boundary_id in Data.spaces.get(oprops.ifc_definition_id, []):
            loader.load_boundary(boundary_id, blender_space)
        return {"FINISHED"}


class SelectProjectBoundaries(bpy.types.Operator):
    bl_idname = "bim.select_project_space_boundaries"
    bl_label = "Select all project space boundaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in context.visible_objects:
            obj.select_set(False)
        ifc_file = tool.Ifc.get()
        for boundary_id in Data.boundaries:
            boundary = ifc_file.by_id(boundary_id)
            obj = tool.Ifc.get_object(boundary)
            if obj:
                obj.select_set(True)
        return {"FINISHED"}


def get_colour(ifc_boundary):
    """Return a color depending on IfcClass given"""
    product_colors = {
        "IfcWall": (0.7, 0.3, 0, 1),
        "IfcWindow": (0, 0.7, 1, 1),
        "IfcSlab": (0.7, 0.7, 0.5, 1),
        "IfcRoof": (0, 0.3, 0, 1),
        "IfcDoor": (1, 1, 1, 1),
    }
    if ifc_boundary.PhysicalOrVirtualBoundary == "VIRTUAL":
        return (1, 0, 1, 1)

    element = ifc_boundary.RelatedBuildingElement
    if not element:
        return (1, 0, 0, 1)
    for product, colour in product_colors.items():
        if element.is_a(product):
            return colour
    return (0, 0, 0, 1)


class ColourByRelatedBuildingElement(bpy.types.Operator):
    bl_idname = "bim.colour_by_related_building_element"
    bl_label = "Apply colour based on related building elements"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        self.store_state(context)
        result = self._execute(context)
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.file = tool.Ifc.get()
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if not element.is_a("IfcRelSpaceBoundary"):
                continue
            obj.color = get_colour(element)
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            areas[0].spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}

    def store_state(self, context):
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            self.transaction_data = {"area": areas[0], "color_type": areas[0].spaces[0].shading.color_type}

    def rollback(self, data):
        if data:
            data["area"].spaces[0].shading.color_type = data["color_type"]

    def commit(self, data):
        if data:
            data["area"].spaces[0].shading.color_type = "OBJECT"


EDITABLE_ATTRIBUTES = {
    "RelatingSpace": "relating_space",
    "RelatedBuildingElement": "related_building_element",
    "ParentBoundary": "parent_boundary",
    "CorrespondingBoundary": "corresponding_boundary",
}


class EnableEditingBoundary(bpy.types.Operator):
    bl_idname = "bim.enable_editing_boundary"
    bl_label = "Edit boundary relations"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bprops = context.active_object.bim_boundary_properties
        bprops.is_editing = True
        boundary = tool.Ifc.get_entity(context.active_object)
        for ifc_attribute, blender_property in EDITABLE_ATTRIBUTES.items():
            entity = getattr(boundary, ifc_attribute, None)
            if not entity:
                continue
            obj = tool.Ifc.get_object(entity)
            if entity and obj:
                setattr(bprops, blender_property, obj)
        return {"FINISHED"}


class DisableEditingBoundary(bpy.types.Operator):
    bl_idname = "bim.disable_editing_boundary"
    bl_label = "Disable editing boundary relations"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bprops = context.active_object.bim_boundary_properties
        bprops.is_editing = False
        for ifc_attribute, blender_property in EDITABLE_ATTRIBUTES.items():
            setattr(bprops, blender_property, None)
        return {"FINISHED"}


class EditBoundaryAttributes(bpy.types.Operator):
    bl_idname = "bim.edit_boundary_attributes"
    bl_label = "Disable editing boundary relations"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        bprops = context.active_object.bim_boundary_properties
        boundary = tool.Ifc.get_entity(context.active_object)
        attributes = dict()
        for ifc_attribute, blender_property in EDITABLE_ATTRIBUTES.items():
            obj = getattr(bprops, blender_property, None)
            entity = tool.Ifc.get_entity(obj)
            attributes[blender_property] = entity
        ifcopenshell.api.run("boundary.edit_attributes", tool.Ifc.get(), entity=boundary, **attributes)
        bpy.ops.bim.disable_editing_boundary()
        return {"FINISHED"}


class UpdateBoundaryGeometry(bpy.types.Operator):
    bl_idname = "bim.update_boundary_geometry"
    bl_label = "Update boundary geometry"
    bl_description = """
    Update boundary connection geometry from mesh.
    Mesh must lie on a single plane. It should look like a face or a face with holes.
    """
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        settings = tool.Boundary.get_assign_connection_geometry_settings(context.active_object)
        ifcopenshell.api.run("boundary.assign_connection_geometry", tool.Ifc.get(), **settings)
        return {"FINISHED"}
