# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Cyril Waechter <cyril@biminsight.ch>
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

import bpy
import bmesh
import logging
import shapely
import shapely.ops
import mathutils
import numpy as np
import multiprocessing
import ifcopenshell.api
import ifcopenshell.geom
import ifcopenshell.util.unit
import ifcopenshell.util.shape
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import bonsai.tool as tool
import bonsai.bim.import_ifc as import_ifc
from math import pi, inf, degrees, acos, radians
from mathutils import Vector, Matrix
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.model.decorator import ProfileDecorator
from bonsai.bim.module.boundary.decorator import BoundaryDecorator
import bonsai.core
import bonsai.core.geometry


def get_boundaries_collection(blender_space):
    space_collection = blender_space.BIMObjectProperties.collection
    collection_name = f"Boundaries/{blender_space.BIMObjectProperties.ifc_definition_id}"
    boundaries_collection = space_collection.children.get(collection_name)
    if not boundaries_collection:
        boundaries_collection = bpy.data.collections.new(collection_name)
        space_collection.children.link(boundaries_collection)
    return boundaries_collection


def disable_editing_boundary_geometry(context):
    ProfileDecorator.uninstall()
    bpy.ops.object.mode_set(mode="OBJECT")

    obj = context.active_object
    element = tool.Ifc.get_entity(obj)

    old_mesh = obj.data
    loader = Loader()
    obj.data = loader.create_mesh(element)
    tool.Geometry.delete_data(old_mesh)
    return {"FINISHED"}


class Loader:
    def __init__(self, operator=None):
        self.operator = operator
        self.ifc_file = None
        self.logger = None
        self.ifc_importer = None
        self.settings = self.load_settings()
        self.fallback_settings = self.load_fallback_settings()
        self.load_importer()

    def create_mesh(self, boundary):
        # ConnectionGeometry is optional in IFC schema for some reasons.
        if not boundary.ConnectionGeometry:
            return None
        surface = boundary.ConnectionGeometry.SurfaceOnRelatingElement
        # Workaround for invalid geometry provided by Revit. See https://github.com/Autodesk/revit-ifc/issues/270
        if surface.is_a("IfcCurveBoundedPlane") and not getattr(surface, "InnerBoundaries", None):
            surface.InnerBoundaries = ()
        try:
            shape = ifcopenshell.geom.create_shape(self.settings, surface)
            mesh = self.ifc_importer.create_mesh(None, shape)
            tool.Loader.link_mesh(shape, mesh)
        except RuntimeError:
            # Fallback solution for invalid geometry provided by Revit. (InnerBoundaries cuting OuterBoundary)
            self.operator.report(
                {"WARNING"},
                (
                    f"IfcRelSpaceBoundary {boundary.id()} mesh creation failed. Geometry might be invalid. Using fallback solution"
                ),
            )
            try:
                shape = ifcopenshell.geom.create_shape(self.fallback_settings, surface.OuterBoundary)
            except RuntimeError:
                self.operator.report(
                    {"WARNING"},
                    f"Skipping IfcRelSpaceBoundary {boundary.id()}. Fallback solution failed. Geometry might be invalid",
                )
                return None
            mesh = bpy.data.meshes.new(str(surface.id()))
            bm = bmesh.new()
            verts = [bm.verts.new(shape.verts[i : i + 3]) for i in range(0, len(shape.verts), 3)]
            bm.faces.new(verts)
            for inner_boundary in surface.InnerBoundaries:
                try:
                    shape = ifcopenshell.geom.create_shape(self.fallback_settings, inner_boundary)
                except RuntimeError:
                    self.operator.report(
                        {"WARNING"},
                        f"Skipping an inner boundary for IfcRelSpaceBoundary with ID {boundary.id()}. Geometry might be invalid",
                    )
                    return None
                verts = [bm.verts.new(shape.verts[i : i + 3]) for i in range(0, len(shape.verts), 3)]
                for i in range(len(verts) - 1):
                    bm.edges.new(verts[i : i + 2])
                bm.edges.new((verts[-1], verts[0]))
            bm.to_mesh(mesh)
            bm.free()
            mesh.BIMMeshProperties.ifc_definition_id = surface.id()
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            matrix = mathutils.Matrix(
                ifcopenshell.util.placement.get_axis2placement(surface.BasisSurface.Position).tolist()
            )
            matrix.translation *= unit_scale
            mesh.transform(matrix)
        return mesh

    def load_settings(self):
        return ifcopenshell.geom.settings()

    def load_fallback_settings(self):
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        return settings

    def load_importer(self):
        self.ifc_file = tool.Ifc.get()
        self.logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(bpy.context, IfcStore.path, self.logger)
        self.ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        self.ifc_importer.file = self.ifc_file

    def load_boundary(
        self, boundary: ifcopenshell.entity_instance, blender_space: bpy.types.Object = None
    ) -> bpy.types.Object:
        if not blender_space:
            if not boundary.RelatingSpace:
                self.operator.report(
                    {"WARNING"},
                    f"Skipping IfcRelSpaceBoundary {boundary.id()} which have no relating space. Invalid boundary.",
                )
                return
            blender_space = tool.Ifc.get_object(boundary.RelatingSpace)
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
    bl_label = "Load All Project Space Boundaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        loader = Loader(self)
        for rel in tool.Ifc.get().by_type("IfcRelSpaceBoundary"):
            loader.load_boundary(rel)
        return {"FINISHED"}


class LoadBoundary(bpy.types.Operator):
    bl_idname = "bim.load_boundary"
    bl_label = "Load Boundary"
    bl_options = {"REGISTER", "UNDO"}
    boundary_id: bpy.props.IntProperty()

    def execute(self, context):
        loader = Loader(self)
        for obj in context.visible_objects:
            obj.select_set(False)
        obj = loader.load_boundary(tool.Ifc.get().by_id(self.boundary_id), context.active_object)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return {"FINISHED"}


class LoadSpaceBoundaries(bpy.types.Operator):
    bl_idname = "bim.load_space_boundaries"
    bl_label = "Load Selected Space Boundaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        loader = Loader(self)
        element = tool.Ifc.get_entity(context.active_object)
        for rel in element.BoundedBy or []:
            loader.load_boundary(rel, context.active_object)
        return {"FINISHED"}


def get_element_boundaries(element):
    if not element:
        return ()
    if element.is_a("IfcSpace"):
        return (b for b in element.BoundedBy or ())
    return (b for b in element.ProvidesBoundaries)


class SelectRelatedElementBoundaries(bpy.types.Operator):
    bl_idname = "bim.select_related_element_boundaries"
    bl_label = "Select Related Element Space Boundaries"
    bl_options = {"REGISTER", "UNDO"}
    related_element: bpy.props.IntProperty()

    def execute(self, context):
        for obj in context.visible_objects:
            obj.select_set(False)
        element = tool.Ifc.get().by_id(self.related_element)
        for rel in get_element_boundaries(element):
            obj = tool.Ifc.get_object(rel)
            if obj:
                obj.select_set(True)
        return {"FINISHED"}


class SelectRelatedElementTypeBoundaries(bpy.types.Operator):
    bl_idname = "bim.select_related_element_type_boundaries"
    bl_label = "Select Related Element Type Space Boundaries"
    bl_options = {"REGISTER", "UNDO"}
    related_element: bpy.props.IntProperty()

    def execute(self, context):
        for obj in context.visible_objects:
            obj.select_set(False)
        element = tool.Ifc.get().by_id(self.related_element)
        if not element:
            return {"FINISHED"}
        element_type = tool.Root.get_element_type(element)
        if not element_type:
            return {"FINISHED"}
        for child in tool.Type.get_type_occurrences(element_type):
            for rel in get_element_boundaries(child):
                obj = tool.Ifc.get_object(rel)
                if obj:
                    obj.select_set(True)
        return {"FINISHED"}


class SelectSpaceBoundaries(bpy.types.Operator):
    bl_idname = "bim.select_space_boundaries"
    bl_label = "Select All Space Boundaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in context.visible_objects:
            obj.select_set(False)
        element = tool.Ifc.get_entity(context.active_object)
        for rel in element.BoundedBy or []:
            obj = tool.Ifc.get_object(rel)
            if obj:
                obj.select_set(True)
        return {"FINISHED"}


class SelectProjectBoundaries(bpy.types.Operator):
    bl_idname = "bim.select_project_space_boundaries"
    bl_label = "Select All Project Space Boundaries"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in context.visible_objects:
            obj.select_set(False)
        for rel in tool.Ifc.get().by_type("IfcRelSpaceBoundary"):
            obj = tool.Ifc.get_object(rel)
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
    bl_label = "Apply Colour Based on Related Building Elements"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        self.store_state(context)
        result = self._execute(context)
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = tool.Ifc.get_entity(obj)
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
    bl_label = "Edit Boundary Relations"
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
    bl_label = "Disable Editing Boundary Relations"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bprops = context.active_object.bim_boundary_properties
        bprops.is_editing = False
        for ifc_attribute, blender_property in EDITABLE_ATTRIBUTES.items():
            setattr(bprops, blender_property, None)
        return {"FINISHED"}


class EditBoundaryAttributes(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_boundary_attributes"
    bl_label = "Disable Editing Boundary Relations"
    bl_options = {"REGISTER", "UNDO"}

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


class UpdateBoundaryGeometry(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_boundary_geometry"
    bl_label = "Update Boundary Geometry"
    bl_description = """
    Update boundary connection geometry from mesh.
    Mesh must lie on a single plane. It should look like a face or a face with holes.
    """
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        tool.Boundary.move_origin_to_space_origin(context.active_object)
        settings = tool.Boundary.get_assign_connection_geometry_settings(context.active_object)
        ifcopenshell.api.run("boundary.assign_connection_geometry", tool.Ifc.get(), **settings)
        return {"FINISHED"}


class EnableEditingBoundaryGeometry(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_boundary_geometry"
    bl_label = "Enable Editing Boundary Geometry"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        if element.ConnectionGeometry.is_a("IfcConnectionSurfaceGeometry"):
            surface = element.ConnectionGeometry.SurfaceOnRelatingElement
            tool.Model.import_surface(surface, obj)

        bpy.ops.object.mode_set(mode="EDIT")
        ProfileDecorator.install(context, exit_edit_mode_callback=lambda: disable_editing_boundary_geometry(context))
        if not bpy.app.background:
            tool.Blender.set_viewport_tool("bim.cad_tool")
        return {"FINISHED"}


class EditBoundaryGeometry(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_boundary_geometry"
    bl_label = "Edit Boundary Geometry"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        ProfileDecorator.uninstall()
        bpy.ops.object.mode_set(mode="OBJECT")

        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        if element.ConnectionGeometry.is_a("IfcConnectionSurfaceGeometry"):
            surface = tool.Model.export_surface(obj)

            if not surface:

                def msg(self, context):
                    self.layout.label(text="INVALID PROFILE")

                bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
                ProfileDecorator.install(
                    context, exit_edit_mode_callback=lambda: disable_editing_boundary_geometry(context)
                )
                bpy.ops.object.mode_set(mode="EDIT")
                return

            old_surface = element.ConnectionGeometry.SurfaceOnRelatingElement
            for inverse in tool.Ifc.get().get_inverse(old_surface):
                ifcopenshell.util.element.replace_attribute(inverse, old_surface, surface)
            ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_surface)

            old_mesh = obj.data
            loader = Loader(self)
            obj.data = loader.create_mesh(element)
            tool.Geometry.delete_data(old_mesh)


class DisableEditingBoundaryGeometry(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_boundary_geometry"
    bl_label = "Disable Editing Boundary Geometry"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        return disable_editing_boundary_geometry(context)


class ShowBoundaries(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.show_boundaries"
    bl_label = "Show Boundaries"
    bl_description = "Load selected objects boundaries if they are not loaded"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        loader = Loader(self)
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not getattr(element, "BoundedBy", None):
                continue
            if tool.Ifc.is_moved(obj):
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
            element = tool.Ifc.get_entity(obj)
            for rel in element.BoundedBy or []:
                boundary_obj = loader.load_boundary(rel, obj)
                tool.Boundary.decorate_boundary(boundary_obj)
        BoundaryDecorator.install(context)
        return {"FINISHED"}


class HideBoundaries(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_boundaries"
    bl_label = "Hide Boundaries"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        to_delete = set()
        spaces = set()
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if element.is_a("IfcSpace"):
                spaces.add(element)
            elif element.is_a("IfcRelSpaceBoundary"):
                spaces.add(element.RelatingSpace)

        for element in spaces:
            for boundary in element.BoundedBy or []:
                boundary_obj = tool.Ifc.get_object(boundary)
                if boundary_obj:
                    to_delete.add((boundary, boundary_obj))
        for boundary, boundary_obj in to_delete:
            tool.Ifc.unlink(element=boundary)
            bpy.data.objects.remove(boundary_obj)
        context.scene.BIMBoundaryProperties.boundaries.clear()
        return {"FINISHED"}


class DecorateBoundaries(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.decorate_boundaries"
    bl_label = "Toggle Boundaries Decorations"
    bl_description = "Add special decorations for all boundaries in the scene or hide them if they are already added"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMBoundaryProperties
        # filter not decorated boundaries and add decorations for them
        decorated_boundaries = set([i.obj for i in props.boundaries])
        active_boundaries = set()
        for element in tool.Ifc.get().by_type("IfcRelSpaceBoundary"):
            obj = tool.Ifc.get_object(element)
            if obj is not None:
                active_boundaries.add(obj)

        boundaries_to_decorate = active_boundaries - decorated_boundaries
        if boundaries_to_decorate:
            for obj in boundaries_to_decorate:
                tool.Boundary.decorate_boundary(obj)
            BoundaryDecorator.install(context)
        else:
            for obj in decorated_boundaries:
                tool.Boundary.undecorate_boundary(obj)
            props.boundaries.clear()
            BoundaryDecorator.uninstall()
            tool.Blender.update_viewport()
        return {"FINISHED"}


class AddBoundary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_boundary"
    bl_label = "Add Boundary"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        relating_space = None
        related_building_element = None
        relating_space_obj = None
        related_building_element_obj = None
        parent_boundaries = []

        objs = context.selected_objects

        if not any((element := tool.Ifc.get_entity(obj)) and element.is_a("IfcSpace") for obj in objs):
            self.report({"INFO"}, "No IfcSpace elements selected.")
            return {"FINISHED"}

        if len(objs) == 2:
            # The user may select two objects, a space and its related building element
            for obj in objs:
                element = tool.Ifc.get_entity(obj)
                if not element:
                    continue
                if element.is_a("IfcSpace"):
                    relating_space = element
                    relating_space_obj = obj
                else:
                    related_building_element = element
                    related_building_element_obj = obj
            parent_boundary = self.create_element_boundary(
                context, relating_space, relating_space_obj, related_building_element, related_building_element_obj
            )
            if parent_boundary:
                parent_boundaries.append(parent_boundary)
        elif len(objs) == 1:
            # New prototype, old code not yet removed. Still testing.
            space = tool.Ifc.get_entity(objs[0])
            if space.is_a("IfcSpace"):
                self.auto_generate_boundaries(space, objs[0])
        elif len(objs) == 1:
            # Optionally the user may select just the space, and the building element shall be auto-detected
            # TODO : refactor to be able to generate all boundaries for selected space automatically or with an option

            def msg(self, context):
                self.layout.label(text="Please set an active container to detect space boundaries from.")

            element = tool.Ifc.get_entity(objs[0])
            if element.is_a("IfcSpace"):
                relating_space = element
                relating_space_obj = objs[0]

            if not (container := tool.Root.get_default_container()):
                bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
                return

            for subelement in ifcopenshell.util.element.get_decomposition(container):
                if not (
                    subelement.is_a("IfcWall") or subelement.is_a("IfcSlab") or subelement.is_a("IfcVirtualElement")
                ):
                    continue
                obj = tool.Ifc.get_object(subelement)
                if obj:
                    related_building_element = subelement
                    related_building_element_obj = obj
                    parent_boundary = self.create_element_boundary(
                        context,
                        relating_space,
                        relating_space_obj,
                        related_building_element,
                        related_building_element_obj,
                    )
                    if parent_boundary:
                        parent_boundaries.append(parent_boundary)

        bpy.ops.bim.show_boundaries()
        for parent_boundary in parent_boundaries:
            obj = tool.Ifc.get_object(parent_boundary)
            obj.select_set(True)

    def auto_generate_boundaries(self, space, space_obj):
        # Identify all potential building elements
        # TODO: don't select everything, use AABB culling in Blender
        building_elements = (
            tool.Ifc.get().by_type("IfcWall")
            + tool.Ifc.get().by_type("IfcSlab")
            + tool.Ifc.get().by_type("IfcVirtualElement")
        )

        # Don't generate boundaries of building elements that we've already got bounaries for.
        for boundary in space.BoundedBy:
            if boundary.RelatedBuildingElement in building_elements:
                building_elements.remove(boundary.RelatedBuildingElement)

        # Create tree of gross shapes of all potential related building elements
        include = building_elements + [space]
        tree = ifcopenshell.geom.tree()
        shapes = {}
        settings = ifcopenshell.geom.settings()
        settings.set("disable-opening-subtractions", True)
        iterator = ifcopenshell.geom.iterator(settings, tool.Ifc.get(), multiprocessing.cpu_count(), include=include)
        if iterator.initialize():
            while True:
                tree.add_element(iterator.get_native())
                shape = iterator.get()
                shapes[shape.id] = shape
                if not iterator.next():
                    break

        # Spatially query all potential boundary elements via a 100mm extension of the space
        building_elements = [e for e in tree.select(space, extend=0.1) if e != space]

        if not building_elements:
            return

        # Create a dissolved bmesh for the space
        space_bm = bmesh.new()
        space_bm.from_mesh(space_obj.data)
        bmesh.ops.dissolve_limit(space_bm, angle_limit=pi * 2 / 360, verts=space_bm.verts, edges=space_bm.edges)

        # Create dissolved bmeshes for all boundary elements
        building_element_bms = {}
        for building_element in building_elements:
            bm = bmesh.new()
            shape = shapes[building_element.id()]

            verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
            for vert in verts:
                bm.verts.new(Vector(vert))
            bm.verts.ensure_lookup_table()

            faces = ifcopenshell.util.shape.get_faces(shape.geometry)
            for face in faces:
                bm.faces.new([bm.verts[i] for i in face])
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
            bm.normal_update()  # Needed so that dissolve_limit will work.
            bmesh.ops.dissolve_limit(bm, angle_limit=radians(1), verts=bm.verts[:], edges=bm.edges[:])
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
            building_element_bms[building_element.id()] = bm

        # Compare space faces and building element faces to see if they relate to one another
        for space_face in space_bm.faces:
            space_face_normal = space_obj.matrix_world.to_3x3() @ space_face.normal
            space_face_vert = space_obj.matrix_world @ space_face.verts[0].co
            for building_element in building_elements:
                for face in building_element_bms[building_element.id()].faces:
                    building_obj = tool.Ifc.get_object(building_element)
                    face_normal = building_obj.matrix_world.to_3x3() @ face.normal
                    angle = degrees(acos(max(min(space_face_normal.dot(face_normal), 1), -1)))
                    if tool.Cad.is_x(angle, 180, tolerance=2):
                        pass  # Faces need to be parallel and have opposite normals to be related.
                    elif building_element.is_a("IfcVirtualElement") and tool.Cad.is_x(angle, 0, tolerance=2):
                        pass  # Virtual elements only need to be parallel to be related, since they are planes.
                    else:
                        continue

                    # Both faces should be close to one another. Say within 50mm.
                    space_vert = building_obj.matrix_world.inverted() @ space_face_vert
                    dist = mathutils.geometry.distance_point_to_plane(space_vert, face.verts[0].co, face.normal)
                    if abs(dist) > 0.05:
                        continue

                    # Project the building element face onto the space face
                    space_face_verts = [v.co.copy() for v in space_face.verts]
                    space_face_matrix = self.get_face_matrix(*[v.copy() for v in space_face_verts[0:3]])
                    space_face_matrix_i = space_face_matrix.inverted()

                    space_face_polygon = shapely.Polygon(
                        [tuple((space_face_matrix_i @ v).xy) for v in space_face_verts]
                    )

                    space_matrix_world_i = space_obj.matrix_world.inverted()
                    face_verts = [space_matrix_world_i @ building_obj.matrix_world @ v.co.copy() for v in face.verts]
                    face_polygon = shapely.Polygon([tuple((space_face_matrix_i @ v).xy) for v in face_verts])

                    gross_boundary_polygon = space_face_polygon.intersection(face_polygon)

                    if type(gross_boundary_polygon) == shapely.GeometryCollection:
                        for geom in gross_boundary_polygon.geoms:
                            if type(geom) == shapely.Polygon:
                                gross_boundary_polygon = geom
                                break

                    if (
                        not (isinstance(gross_boundary_polygon, shapely.Polygon) and gross_boundary_polygon.is_valid)
                        or gross_boundary_polygon.is_empty
                    ):
                        continue

                    # The gross boundary polygon may not be a true gross boundary since it
                    # may have openings already removed, such as in IFC4 Reference View. So
                    # we cheat by using the exterior boundary to mean "gross".
                    exterior_boundary_polygon = shapely.Polygon(gross_boundary_polygon.exterior.coords)

                    parent_boundary = tool.Ifc.run(
                        "root.create_entity", ifc_class=bpy.context.scene.BIMModelProperties.boundary_class
                    )
                    if building_element.is_a("IfcVirtualElement"):
                        parent_boundary.PhysicalOrVirtualBoundary = "VIRTUAL"
                    else:
                        parent_boundary.PhysicalOrVirtualBoundary = "PHYSICAL"
                    parent_boundary.InternalOrExternalBoundary = "NOTDEFINED"
                    if building_element.is_a("IfcWall"):
                        is_external = ifcopenshell.util.element.get_pset(
                            building_element, "Pset_WallCommon", "IsExternal"
                        )
                        if is_external is True:
                            parent_boundary.InternalOrExternalBoundary = "EXTERNAL"
                        elif is_external is False:
                            parent_boundary.InternalOrExternalBoundary = "INTERNAL"
                    elif building_element.is_a("IfcSlab"):
                        predefined_type = ifcopenshell.util.element.get_predefined_type(building_element)
                        if predefined_type == "BASESLAB":
                            parent_boundary.InternalOrExternalBoundary = "EXTERNAL_EARTH"
                        else:
                            is_external = ifcopenshell.util.element.get_pset(
                                building_element, "Pset_SlabCommon", "IsExternal"
                            )
                            if is_external is True:
                                parent_boundary.InternalOrExternalBoundary = "EXTERNAL"
                            elif is_external is False:
                                parent_boundary.InternalOrExternalBoundary = "INTERNAL"
                    parent_boundary.RelatingSpace = space
                    parent_boundary.RelatedBuildingElement = building_element
                    parent_boundary.ConnectionGeometry = self.create_connection_geometry_from_polygon(
                        exterior_boundary_polygon, space_face_matrix
                    )
                    self.set_boundary_name(parent_boundary)

                    for rel in getattr(building_element, "HasOpenings", []):
                        opening = rel.RelatedOpeningElement
                        filling = opening.HasFillings[0].RelatedBuildingElement if opening.HasFillings else None

                        # Create shape of opening as a dissolved BMesh
                        settings = ifcopenshell.geom.settings()
                        shape = ifcopenshell.geom.create_shape(settings, opening)
                        m = shape.transformation.matrix
                        mat = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape))
                        mat.translation = (0, 0, 0)
                        opening_bm = bmesh.new()
                        verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
                        for vert in verts:
                            opening_bm.verts.new(Vector(vert))
                        opening_bm.verts.ensure_lookup_table()
                        faces = ifcopenshell.util.shape.get_faces(shape.geometry)
                        for face in faces:
                            opening_bm.faces.new([opening_bm.verts[i] for i in face])
                        opening_bm.verts.ensure_lookup_table()
                        opening_bm.faces.ensure_lookup_table()
                        opening_bm.normal_update()  # Needed so that dissolve_limit will work.
                        bmesh.ops.dissolve_limit(
                            opening_bm, angle_limit=radians(1), verts=opening_bm.verts[:], edges=opening_bm.edges[:]
                        )
                        opening_bm.verts.ensure_lookup_table()
                        opening_bm.faces.ensure_lookup_table()

                        # Get relevant faces of BMesh that can turn into boundaries
                        opening_polygons = []
                        for opening_face in opening_bm.faces:
                            opening_face_normal = mat.to_3x3() @ opening_face.normal
                            angle = degrees(acos(max(min(opening_face_normal.dot(face_normal), 1), -1)))
                            if not tool.Cad.is_x(angle, 180, tolerance=2):
                                continue  # Any non-parallel faces are not relevant
                            opening_face_verts = [space_matrix_world_i @ mat @ v.co.copy() for v in opening_face.verts]
                            polygon = shapely.Polygon([tuple((space_face_matrix_i @ v).xy) for v in opening_face_verts])
                            opening_polygons.append(polygon)

                        # Merge them all into a single opening polygon for our boundary
                        opening_polygon = shapely.ops.unary_union(opening_polygons)

                        # Only openings that are projected onto our exterior boundary are relevant.
                        if opening_polygon.intersection(exterior_boundary_polygon).area == 0:
                            continue

                        boundary = tool.Ifc.run(
                            "root.create_entity", ifc_class=bpy.context.scene.BIMModelProperties.boundary_class
                        )
                        boundary.RelatingSpace = space
                        boundary.RelatedBuildingElement = filling or opening
                        boundary.ConnectionGeometry = self.create_connection_geometry_from_polygon(
                            opening_polygon, space_face_matrix
                        )
                        if filling:
                            boundary.PhysicalOrVirtualBoundary = "PHYSICAL"
                        else:
                            boundary.PhysicalOrVirtualBoundary = "VIRTUAL"
                        boundary.InternalOrExternalBoundary = parent_boundary.InternalOrExternalBoundary
                        if boundary.is_a() != "IfcRelSpaceBoundary":
                            boundary.ParentBoundary = parent_boundary
                        self.set_boundary_name(boundary)

    def create_element_boundary(
        self, context, relating_space, relating_space_obj, related_building_element, related_building_element_obj
    ):
        if not relating_space or not related_building_element:
            return

        # Find which face on space should be bounded to related building element
        # TODO: Handle round wall where multiple faces need to be bound to the same related building element
        bm = bmesh.new()
        bm.from_mesh(relating_space_obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi * 2 / 360, verts=bm.verts, edges=bm.edges)

        target_distance = inf
        target_face = None
        for face in bm.faces:
            centroid = relating_space_obj.matrix_world @ face.calc_center_median()
            raycast = related_building_element_obj.closest_point_on_mesh(
                related_building_element_obj.matrix_world.inverted() @ centroid, distance=1
            )
            if raycast[0]:
                distance = (related_building_element_obj.matrix_world @ raycast[1] - centroid).length
                if distance < target_distance:
                    target_face = face
                    target_distance = distance

        if not target_face:
            return

        # Is this right? Or should I use loop?
        target_face_verts = [v.co.copy() for v in target_face.verts]
        target_face_matrix = self.get_face_matrix(*[v.copy() for v in target_face_verts[0:3]])
        target_face_matrix_i = target_face_matrix.inverted()

        target_face_polygon = shapely.Polygon([tuple((target_face_matrix_i @ v).xy) for v in target_face_verts])

        related_building_element_polygon = self.get_flattened_polygon(
            related_building_element, relating_space_obj, target_face_matrix_i
        )

        gross_boundary_polygon = target_face_polygon.intersection(related_building_element_polygon)

        if type(gross_boundary_polygon) == shapely.GeometryCollection:
            for geom in gross_boundary_polygon.geoms:
                if type(geom) == shapely.Polygon:
                    gross_boundary_polygon = geom
                    break

        if (
            not (isinstance(gross_boundary_polygon, shapely.Polygon) and gross_boundary_polygon.is_valid)
            or gross_boundary_polygon.is_empty
        ):
            return

        parent_boundary = tool.Ifc.run("root.create_entity", ifc_class=context.scene.BIMModelProperties.boundary_class)
        parent_boundary.PhysicalOrVirtualBoundary = "PHYSICAL"
        # Set to EXTERNAL by default and turn later to internal if there is a corresponding boundary relating to an
        # internal space
        parent_boundary.InternalOrExternalBoundary = "EXTERNAL"

        # The gross boundary polygon may not be a true gross boundary since it
        # may have openings already removed, such as in IFC4 Reference View. So
        # we cheat by using the exterior boundary to mean "gross". Later, we
        # can use this to check whether or not the opening is relevant to our
        # space.
        exterior_boundary_polygon = shapely.Polygon(gross_boundary_polygon.exterior.coords)

        inner_boundaries = []

        for rel in getattr(related_building_element, "HasOpenings", []):
            opening = rel.RelatedOpeningElement
            if not opening.HasFillings:
                continue
            # TODO: HasFilling is a zero to many relationship. How to handle many ?
            filling = opening.HasFillings[0].RelatedBuildingElement

            opening_polygon = self.get_flattened_polygon(opening, relating_space_obj, target_face_matrix_i)

            # An inner boundary is supposed to overlap its parent boundary according to IFC4 documentation
            # so we extend our exterior boundary with all opening which has a filling
            # Also see Implementation aggreement SB 1.1 for IFC 2x3 TC1 Space Boundary Addon View
            # https://standards.buildingsmart.org/MVD/RELEASE/IFC2x3/TC1/SB1_1/IFC%20Space%20Boundary%20Implementation%20Agreement%20Addendum%202010-03-22.pdf
            unionised_object = exterior_boundary_polygon.union(opening_polygon)
            if isinstance(unionised_object, shapely.Polygon):
                exterior_boundary_polygon = unionised_object

            # Only openings that are projected onto our exterior boundary are relevant.
            if opening_polygon.intersection(exterior_boundary_polygon).area == 0:
                continue

            connection_geometry = self.create_connection_geometry_from_polygon(opening_polygon, target_face_matrix)
            boundary = tool.Ifc.run("root.create_entity", ifc_class=context.scene.BIMModelProperties.boundary_class)
            boundary.RelatingSpace = relating_space
            boundary.RelatedBuildingElement = filling
            boundary.ConnectionGeometry = connection_geometry
            if related_building_element.is_a("IfcVirtualElement"):
                boundary.PhysicalOrVirtualBoundary = "VIRTUAL"
            else:
                boundary.PhysicalOrVirtualBoundary = "PHYSICAL"
            boundary.InternalOrExternalBoundary = parent_boundary.InternalOrExternalBoundary
            self.set_boundary_name(boundary)
            if boundary.is_a("IfcRelSpaceBoundary2ndLevel"):
                boundary.ParentBoundary = parent_boundary

        connection_geometry = self.create_connection_geometry_from_polygon(
            exterior_boundary_polygon, target_face_matrix
        )
        parent_boundary.RelatingSpace = relating_space
        parent_boundary.RelatedBuildingElement = related_building_element
        parent_boundary.ConnectionGeometry = connection_geometry
        self.set_boundary_name(parent_boundary)
        return parent_boundary

    def get_face_matrix(self, p1, p2, p3):
        edge1 = p2 - p1
        edge2 = p3 - p1
        normal = edge1.cross(edge2)
        z_axis = normal.normalized()
        x_axis = p2 - p1
        x_axis.normalize()
        y_axis = z_axis.cross(x_axis)

        mat = Matrix()
        mat.col[0][:3] = x_axis
        mat.col[1][:3] = y_axis
        mat.col[2][:3] = z_axis
        mat.translation = p1

        return mat

    def get_flattened_polygon(self, element, relating_space_obj, target_face_matrix_i):
        obj = tool.Ifc.get_object(element)
        if obj and tool.Ifc.is_moved(obj):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        space_matrix_i = relating_space_obj.matrix_world.inverted()

        settings = ifcopenshell.geom.settings()
        if not element.is_a("IfcOpeningElement"):
            settings.set("disable-opening-subtractions", True)
        # geometry = ifcopenshell.geom.create_shape(settings, body)
        shape = ifcopenshell.geom.create_shape(settings, element)
        mat = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape))
        verts = [space_matrix_i @ mat @ Vector(v) for v in ifcopenshell.util.shape.get_vertices(shape.geometry)]
        faces = ifcopenshell.util.shape.get_faces(shape.geometry)
        polygons = []
        for face in faces:
            polygon = shapely.Polygon([tuple((target_face_matrix_i @ verts[vi]).xy) for vi in face])
            polygons.append(polygon)
        return shapely.ops.unary_union(polygons)

    def create_connection_geometry_from_polygon(self, polygon, target_face_matrix):
        surface = self.export_surface(polygon, target_face_matrix)
        return tool.Ifc.get().createIfcConnectionSurfaceGeometry(surface)

    def export_surface(self, polygon, target_face_matrix):
        x_axis = target_face_matrix.col[0][:3]
        z_axis = target_face_matrix.col[2][:3]
        p1 = target_face_matrix.translation

        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        tool.Model.unit_scale = self.unit_scale

        surface = tool.Ifc.get().createIfcCurveBoundedPlane()
        surface.BasisSurface = tool.Ifc.get().createIfcPlane(
            tool.Ifc.get().createIfcAxis2Placement3D(
                tool.Ifc.get().createIfcCartesianPoint([o / self.unit_scale for o in p1]),
                tool.Ifc.get().createIfcDirection([float(o) for o in z_axis]),
                tool.Ifc.get().createIfcDirection([float(o) for o in x_axis]),
            )
        )

        if tool.Ifc.get().schema != "IFC2X3":
            points = [tool.Model.convert_si_to_unit(list(co)) for co in polygon.exterior.coords]
            point_list = tool.Ifc.get().createIfcCartesianPointList2D(points)
            outer_boundary = tool.Ifc.get().createIfcIndexedPolyCurve(point_list, None, False)

            inner_boundaries = []
            for interior in polygon.interiors:
                points = [tool.Model.convert_si_to_unit(list(co)) for co in interior.coords]
                point_list = tool.Ifc.get().createIfcCartesianPointList2D(points)
                inner_boundaries.append(tool.Ifc.get().createIfcIndexedPolyCurve(point_list, None, False))
        else:
            pass  # TODO

        surface.OuterBoundary = outer_boundary
        surface.InnerBoundaries = inner_boundaries

        return surface

    def set_boundary_name(self, boundary):
        """
        By convention 1stLevel and 2ndLevel boundary have specific name and description
        See https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelSpaceBoundary.htm
        Warning: IfcRelSpaceBoundary2ndLevel is a subclass of IfcRelSpaceBoundary1stLevel test order matter
        """
        if boundary.is_a("IfcRelSpaceBoundary2ndLevel"):
            boundary.Name = "2ndLevel"
            if boundary.CorrespondingBoundary:
                boundary.Description = "2a"
            else:
                boundary.Description = "2b"
        elif boundary.is_a("IfcRelSpaceBoundary1stLevel"):
            boundary.Name = "1stLevel"
