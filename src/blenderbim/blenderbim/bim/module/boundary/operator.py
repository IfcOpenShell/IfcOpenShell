# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import logging
import bpy
import ifcopenshell.util.attribute
import ifcopenshell.api
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.boundary.data import Data
import blenderbim.bim.import_ifc as import_ifc


def get_boundaries_collection(blender_space):
    space_collection = bpy.data.collections.get(blender_space.name)
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
        surface = boundary.ConnectionGeometry.SurfaceOnRelatingElement
        # workaround for unvalid geometry provided by Revit. See https://github.com/IfcOpenShell/IfcOpenShell/issues/635#issuecomment-770366838
        if surface.is_a("IfcCurveBoundedPlane") and not getattr(surface, "InnerBoundaries", None):
            surface.InnerBoundaries = ()
        shape = ifcopenshell.geom.create_shape(self.settings, surface)
        mesh = self.ifc_importer.create_mesh(None, shape)
        obj = bpy.data.objects.new(f"{boundary.is_a()}/{boundary_id}", mesh)
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
