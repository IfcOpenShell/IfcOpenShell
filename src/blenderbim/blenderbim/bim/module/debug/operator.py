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

import os
import bpy
import time
import logging
import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.core.debug as core
import blenderbim.bim.handler
import blenderbim.bim.import_ifc as import_ifc
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


class PrintIfcFile(bpy.types.Operator):
    bl_idname = "bim.print_ifc_file"
    bl_label = "Print IFC File"
    bl_description = "Prints the file contents in the system console.\nAccess it with Window > Toggle System Console"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        print(IfcStore.get_file().wrapped_data.to_string())
        return {"FINISHED"}


class PurgeIfcLinks(bpy.types.Operator):
    bl_idname = "bim.purge_ifc_links"
    bl_label = "Purge IFC Links"
    bl_description = "Purge all definitions and references from the file.\nWarning : Cannot be undone."

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type in {"MESH", "EMPTY"}:
                obj.BIMObjectProperties.ifc_definition_id = 0
                if obj.data:
                    obj.data.BIMMeshProperties.ifc_definition_id = 0
        for material in bpy.data.materials:
            material.BIMMaterialProperties.ifc_style_id = False
        context.scene.BIMProperties.ifc_file = ""
        context.scene.BIMDebugProperties.attributes.clear()
        IfcStore.purge()
        blenderbim.bim.handler.purge_module_data()
        return {"FINISHED"}


class ValidateIfcFile(bpy.types.Operator):
    bl_idname = "bim.validate_ifc_file"
    bl_label = "Validate IFC File"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        import ifcopenshell.validate

        logger = logging.getLogger("validate")
        logger.setLevel(logging.DEBUG)
        ifcopenshell.validate.validate(IfcStore.get_file(), logger)
        return {"FINISHED"}


class ProfileImportIFC(bpy.types.Operator):
    bl_idname = "bim.profile_import_ifc"
    bl_label = "Profile Import IFC"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file() and context.scene.BIMProperties.ifc_file

    def execute(self, context):
        import cProfile
        import pstats

        cProfile.run("import bpy; bpy.ops.bim.load_project_elements()", "blender.prof")
        p = pstats.Stats("blender.prof")
        p.sort_stats("cumulative").print_stats(50)
        return {"FINISHED"}


class CreateAllShapes(bpy.types.Operator):
    bl_idname = "bim.create_all_shapes"
    bl_label = "Test All Shapes"
    bl_description = "Look for errors in all the shapes contained in the file"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        self.file = IfcStore.get_file()
        elements = self.file.by_type("IfcElement") + self.file.by_type("IfcSpace")

        total = len(elements)
        settings = ifcopenshell.geom.settings()
        failures = []
        excludes = ()  # For the developer to debug with
        for i, element in enumerate(elements):
            if element.GlobalId in excludes:
                continue
            print(f"{i}/{total}:", element)
            start = time.time()
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
                print(
                    "Success",
                    time.time() - start,
                    len(shape.geometry.verts),
                    len(shape.geometry.edges),
                    len(shape.geometry.faces),
                )
            except:
                failures.append(element)
                print("***** FAILURE *****")
        print(f"Failures: {len(failures)}")
        for failure in failures:
            print(failure)
        return {"FINISHED"}


class CreateShapeFromStepId(bpy.types.Operator):
    bl_idname = "bim.create_shape_from_step_id"
    bl_label = "Create Shape From STEP ID"
    bl_description = "Recreate a mesh object from a STEP ID"
    bl_options = {"REGISTER", "UNDO"}
    should_include_curves: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        logger = logging.getLogger("ImportIFC")
        self.ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
        self.file = IfcStore.get_file()
        element = self.file.by_id(int(context.scene.BIMDebugProperties.step_id))
        settings = ifcopenshell.geom.settings()
        if self.should_include_curves:
            settings.set(settings.INCLUDE_CURVES, True)
        shape = ifcopenshell.geom.create_shape(settings, element)
        if shape:
            ifc_importer = import_ifc.IfcImporter(self.ifc_import_settings)
            ifc_importer.file = self.file
            mesh = ifc_importer.create_mesh(element, shape)
        else:
            mesh = None
        obj = bpy.data.objects.new("Debug", mesh)
        context.scene.collection.objects.link(obj)
        return {"FINISHED"}


class SelectHighPolygonMeshes(bpy.types.Operator):
    bl_idname = "bim.select_high_polygon_meshes"
    bl_label = "Select High Polygon Meshes"
    bl_description = "Select objects containing more polygons than the specified number"
    bl_options = {"REGISTER", "UNDO"}
    threshold: bpy.props.IntProperty()

    def execute(self, context):
        for obj in context.view_layer.objects:
            if obj.type == "MESH" and len(obj.data.polygons) > self.threshold:
                obj.select_set(True)
        return {"FINISHED"}


class SelectHighestPolygonMeshes(bpy.types.Operator):
    bl_idname = "bim.select_highest_polygon_meshes"
    bl_label = "Select Highest Polygon Meshes"
    bl_description = "Select objects with a number of polygons superior to the specified percentile"
    bl_options = {"REGISTER", "UNDO"}
    percentile: bpy.props.IntProperty()

    def execute(self, context):
        objects = [obj for obj in context.view_layer.objects if obj.type == "MESH"]
        if objects:
            percentile = len(max(objects, key=lambda o: len(o.data.polygons)).data.polygons) * self.percentile / 100
            print(f"Selected all Meshes with more than {int(percentile)} polygons")
            [obj.select_set(True) for obj in objects if len(obj.data.polygons) > percentile]
        return {"FINISHED"}


class RewindInspector(bpy.types.Operator):
    bl_idname = "bim.rewind_inspector"
    bl_label = "Rewind Inspector"
    bl_description = "Rewind the Inspector to the previously inspected element"

    def execute(self, context):
        props = context.scene.BIMDebugProperties
        total_breadcrumbs = len(props.step_id_breadcrumb)
        if total_breadcrumbs < 2:
            return {"FINISHED"}
        previous_step_id = int(props.step_id_breadcrumb[total_breadcrumbs - 2].name)
        props.step_id_breadcrumb.remove(total_breadcrumbs - 1)
        props.step_id_breadcrumb.remove(total_breadcrumbs - 2)
        bpy.ops.bim.inspect_from_step_id(step_id=previous_step_id)
        return {"FINISHED"}


class InspectFromStepId(bpy.types.Operator):
    bl_idname = "bim.inspect_from_step_id"
    bl_label = "Inspect From STEP ID"
    bl_description = "Inspect the attributes and references by looking up the specified STEP ID"
    step_id: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        self.file = IfcStore.get_file()
        debug_props = context.scene.BIMDebugProperties
        debug_props.active_step_id = self.step_id
        crumb = context.scene.BIMDebugProperties.step_id_breadcrumb.add()
        crumb.name = str(self.step_id)
        element = self.file.by_id(self.step_id)
        debug_props.attributes.clear()
        debug_props.inverse_attributes.clear()
        debug_props.inverse_references.clear()
        for key, value in element.get_info().items():
            self.add_attribute(debug_props.attributes, key, value)
        for key in dir(element):
            if (
                not key[0].isalpha()
                or key[0] != key[0].upper()
                or key in element.get_info()
                or not getattr(element, key)
            ):
                continue
            self.add_attribute(debug_props.inverse_attributes, key, getattr(element, key))
        for inverse in self.file.get_inverse(element):
            new = debug_props.inverse_references.add()
            new.string_value = str(inverse)
            new.int_value = inverse.id()
        return {"FINISHED"}

    def add_attribute(self, prop, key, value):
        if isinstance(value, tuple) and len(value) < 10:
            for i, item in enumerate(value):
                self.add_attribute(prop, key + f"[{i}]", item)
            return
        elif isinstance(value, tuple) and len(value) >= 10:
            key = key + "({})".format(len(value))
        new = prop.add()
        new.name = key
        new.string_value = str(value)
        if isinstance(value, ifcopenshell.entity_instance):
            new.int_value = int(value.id())


class InspectFromObject(bpy.types.Operator):
    bl_idname = "bim.inspect_from_object"
    bl_label = "Inspect From Object"
    bl_description = "Inspect the Active Object's attributes and references"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            if bpy.app.version >= (3, 0, 0):
                cls.poll_message_set("No Active Object")
        elif not context.active_object.BIMObjectProperties.ifc_definition_id:
            if bpy.app.version >= (3, 0, 0):
                cls.poll_message_set("Active Object doesn't have an IFC definition")
        else:
            return True

    def execute(self, context):
        bpy.ops.bim.inspect_from_step_id(step_id=context.active_object.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class PrintObjectPlacement(bpy.types.Operator):
    bl_idname = "bim.print_object_placement"
    bl_label = "Print Object Placement"
    step_id: bpy.props.IntProperty()

    def execute(self, context):
        print(ifcopenshell.util.placement.get_local_placement(IfcStore.get_file().by_id(self.step_id)))
        return {"FINISHED"}


class ParseExpress(bpy.types.Operator):
    bl_idname = "bim.parse_express"
    bl_label = "Parse Express"

    def execute(self, context):
        core.parse_express(tool.Debug, context.scene.BIMDebugProperties.express_file)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class SelectExpressFile(bpy.types.Operator):
    bl_idname = "bim.select_express_file"
    bl_label = "Select Express File"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select an IFC EXPRESS definition"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.exp", options={"HIDDEN"})

    def execute(self, context):
        if os.path.exists(self.filepath) and "exp" in os.path.splitext(self.filepath)[1]:
            context.scene.BIMDebugProperties.express_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class PurgeHdf5Cache(bpy.types.Operator):
    bl_idname = "bim.purge_hdf5_cache"
    bl_label = "Purge HDF5 Cache"

    def execute(self, context):
        core.purge_hdf5_cache(tool.Debug)
        return {"FINISHED"}
