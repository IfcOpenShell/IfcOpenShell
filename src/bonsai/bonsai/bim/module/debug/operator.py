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

import os
import sys
import bpy
import time
import random
import logging
import subprocess
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.core.debug as core
import bonsai.core.profile
import bonsai.core.type
import bonsai.bim.handler
import bonsai.bim.import_ifc as import_ifc
from pathlib import Path
from bonsai import get_debug_info, format_debug_info
from bonsai.bim.ifc import IfcStore
from typing import get_args


class CopyDebugInformation(bpy.types.Operator):
    bl_idname = "bim.copy_debug_information"
    bl_label = "Copy Debug Information"
    bl_description = "Copies debugging information to your clipboard for use in bug reports"

    def execute(self, context):
        info = get_debug_info()
        if tool.Ifc.get():
            info.update(
                {
                    "ifc": os.path.basename(tool.Ifc.get_path()) if os.path.isfile(tool.Ifc.get_path()) else "Unsaved",
                    "schema": tool.Ifc.get().schema,
                    "preprocessor_version": tool.Ifc.get().wrapped_data.header.file_name.preprocessor_version,
                    "originating_system": tool.Ifc.get().wrapped_data.header.file_name.originating_system,
                }
            )

        text = format_debug_info(info)

        text_with_backticks = f"```\n{text}\n```"

        print("-" * 80)
        print(text_with_backticks)
        print("-" * 80)

        context.window_manager.clipboard = text_with_backticks
        return {"FINISHED"}


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


class ConvertToBlender(bpy.types.Operator):
    bl_idname = "bim.convert_to_blender"
    bl_label = "Convert To Blender File"
    bl_description = "Removes all IFC data and revert to basic Blender objects.\nWarning : Cannot be undone."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.library:
                continue
            if obj.type in {"MESH", "EMPTY"}:
                tool.Ifc.unlink(obj=obj)
                data = obj.data
                if tool.Geometry.has_mesh_properties(data):
                    if data.library:
                        continue
                    data.BIMMeshProperties.ifc_definition_id = 0
        for material in bpy.data.materials:
            if material.library:
                continue
            tool.Ifc.unlink(obj=material)
        context.scene.BIMProperties.ifc_file = ""
        context.scene.BIMDebugProperties.attributes.clear()
        IfcStore.purge()
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class ValidateIfcFile(bpy.types.Operator):
    bl_idname = "bim.validate_ifc_file"
    bl_label = "Validate IFC File"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def execute(self, context):
        import ifcopenshell.validate

        class LogDetectionHandler(logging.Handler):
            message_logged = False

            def emit(self, record):
                if not self.message_logged:
                    self.message_logged = True

        logger = logging.getLogger("validate")
        logger.setLevel(logging.DEBUG)

        # use LogDetectionHandler to check whether there were any validation errors
        # during `ifcopenshell.validate.validate`
        handler = LogDetectionHandler()
        logger.addHandler(handler)
        ifcopenshell.validate.validate(tool.Ifc.get(), logger, express_rules=True)
        logger.removeHandler(handler)

        if handler.message_logged:
            self.report({"INFO"}, "Check validation results in the system console.")
        else:
            self.report({"INFO"}, "No validation issues found.")

        return {"FINISHED"}


class ProfileImportIFC(bpy.types.Operator):
    profile_filename = "blender.prof"
    bl_idname = "bim.profile_import_ifc"
    bl_label = "Profile Import IFC"
    bl_description = f"Reload currently loaded project and save cprofile stats for reloading to '{profile_filename}'"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC file loaded.")
            return False
        if not context.scene.BIMProperties.ifc_file:
            cls.poll_message_set("Current IFC file is not saved.")
            return False
        return True

    def execute(self, context):
        import cProfile
        import pstats

        profile_file = Path(profile_filename)
        cProfile.run("import bpy; bpy.ops.bim.load_project_elements()", str(profile_file))
        p = pstats.Stats(str(profile_file))
        p.sort_stats("cumulative").print_stats(50)
        self.report({"INFO"}, f'Profile stats are saved to "{profile_file.absolute()}".')
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
        settings.set("keep-bounding-boxes", True)
        settings_2d = ifcopenshell.geom.settings()
        settings_2d.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        failures = []
        excludes = ()  # For the developer to debug with
        for i, element in enumerate(elements, 1):
            if element.GlobalId in excludes:
                continue
            if not element.Representation:
                continue
            print(f"{i}/{total}:", element)
            start = time.time()
            shape = None
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
            except:
                try:
                    shape = ifcopenshell.geom.create_shape(settings_2d, element)
                except:
                    failures.append(element)
                    print("***** FAILURE *****")
            if shape:
                print(
                    "Success",
                    time.time() - start,
                    len(shape.geometry.verts),
                    len(shape.geometry.edges),
                    len(shape.geometry.faces),
                )
        self.report({"INFO"}, f"Failed shapes: {len(failures)}, check the system console for details.")
        for failure in failures:
            print(failure)
        return {"FINISHED"}


class CreateShapeFromStepId(bpy.types.Operator):
    bl_idname = "bim.create_shape_from_step_id"
    bl_label = "Create Shape From STEP ID"
    bl_description = "Recreate a mesh object from a STEP ID"
    bl_options = {"REGISTER", "UNDO"}
    should_include_curves: bpy.props.BoolProperty()
    step_id: bpy.props.IntProperty(default=0)
    geometry_library: bpy.props.EnumProperty(
        name="Geometry Library",
        items=[(i, i, "") for i in get_args(ifcopenshell.geom.GEOMETRY_LIBRARY)],
        default="opencascade",
    )
    custom_geometry_library: bpy.props.StringProperty(
        name="Custom Geometry Library",
        description="Provide a custom geometry library name, will override the 'geometry library' property.",
    )

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def execute(self, context):
        geometry_library = self.custom_geometry_library or self.geometry_library
        logger = logging.getLogger("ImportIFC")
        self.ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
        self.file = tool.Ifc.get()
        element = self.file.by_id(self.step_id or int(context.scene.BIMDebugProperties.step_id))
        settings = ifcopenshell.geom.settings()
        settings.set("keep-bounding-boxes", True)
        if self.should_include_curves:
            settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, element, geometry_library=geometry_library)
        if shape:
            ifc_importer = import_ifc.IfcImporter(self.ifc_import_settings)
            ifc_importer.file = self.file
            mesh = ifc_importer.create_mesh(element, shape)
        else:
            mesh = None
        obj = bpy.data.objects.new(f"Debug/{element.is_a()}/{element.id()}", mesh)
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
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Print object placement to the system console.\n\n" + "ALT+CLICK create an empty object at that position"
    )
    step_id: bpy.props.IntProperty()
    create_empty_object: bpy.props.BoolProperty(name="Create Empty Object", default=False, options={"SKIP_SAVE"})
    arrow_size: bpy.props.FloatProperty(name="Arrow Size", default=0.2, subtype="DISTANCE")

    def invoke(self, context, event):
        # keep the viewport position on alt+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.alt:
            self.create_empty_object = True
        return self.execute(context)

    def execute(self, context):
        placement = ifcopenshell.util.placement.get_local_placement(IfcStore.get_file().by_id(self.step_id))
        if self.create_empty_object:
            bpy.ops.object.empty_add(type="ARROWS")
            si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            context.active_object.matrix_world = placement.transpose()
            context.active_object.matrix_world.translation *= si_conversion
            context.active_object.empty_display_size = self.arrow_size
        print(placement)
        return {"FINISHED"}


class ParseExpress(bpy.types.Operator):
    bl_idname = "bim.parse_express"
    bl_label = "Parse Express"

    def execute(self, context):
        core.parse_express(tool.Debug, context.scene.BIMDebugProperties.express_file)
        bonsai.bim.handler.refresh_ui_data()
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
    bl_description = "Clean up HDF5 cache files except the ones that currently loaded"

    def execute(self, context):
        core.purge_hdf5_cache(tool.Debug)
        self.report({"INFO"}, "HDF5 cache purged.")
        return {"FINISHED"}


class OverrideDisplayType(bpy.types.Operator):
    bl_idname = "bim.override_display_type"
    bl_label = "Override Display Type"
    display: bpy.props.StringProperty()

    def execute(self, context):
        for obj in context.selected_objects:
            obj.display_type = self.display
        return {"FINISHED"}


class PrintUnusedElementStats(bpy.types.Operator):
    bl_idname = "bim.print_unused_elements_stats"
    bl_label = "Print Unused Elements Stats"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Print all unused elements in current IFC project in system console, not limited to the selected class"
    )

    ignore_contexts: bpy.props.BoolProperty(name="Ignore Contexts", default=True)
    ignore_relationships: bpy.props.BoolProperty(name="Ignore Relationships", default=True)
    ignore_types: bpy.props.BoolProperty(name="Ignore Types", default=True)
    ignore_styled_items: bpy.props.BoolProperty(name="Ignore Styled Items", default=True)

    def execute(self, context):
        props = context.scene.BIMDebugProperties
        # ignore some classes that could have zero 0 inverse references by their nature
        ignore_classes = []
        if self.ignore_contexts:
            ignore_classes += ["IfcRepresentationContext"]
        if self.ignore_relationships:
            ignore_classes += ["IfcRelationship"]
        if self.ignore_types:
            ignore_classes += ["IfcTypeProduct"]
        if self.ignore_styled_items:
            ignore_classes += ["IfcStyledItem"]
        ignore_classes += [
            "IfcIndexedColourMap",  # Only referenced by inverse attributes.
            "IfcIndexedTextureMap",  # Only referenced by inverse attributes.
        ]

        unused_elements = tool.Debug.print_unused_elements_stats(props.ifc_class_purge, ignore_classes)
        self.report({"INFO"}, f"{unused_elements} unused elements found, check the system console for the details.")
        return {"FINISHED"}


class PurgeUnusedElementsByClass(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.purge_unused_elements_by_class"
    bl_label = "Purge Unused Elements By Class"
    bl_description = (
        "Will find all elements of class that have no inverse references and will remove them, use very carefully.\n"
        "If IFC class is provided in neighbour field, will purge only elemnts of the provided class. Otherwise will purge all white-listed elements.\n"
        "ALT+CLICK to provide a path where to save the IFC file with the removed elements (note changes will be applied to the current IFC too)"
    )
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH", options={"SKIP_SAVE"})
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            context.window_manager.fileselect_add(self)
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        props = context.scene.BIMDebugProperties
        if props.ifc_class_purge:
            purged_elements = core.purge_unused_elements(tool.Ifc, tool.Debug, props.ifc_class_purge)
            self.report({"INFO"}, f"{purged_elements} unused elements found and removed.")
            if self.filepath:
                tool.Ifc.get().write(self.filepath)
            return

        # A whitelisted class is a class that only contains simple data that
        # has no meaning by itself (only has meaning when combined with other
        # data). E.g. a colour by itself has no meaning so is whitelisted, but
        # a material by itself may be part of your materials library.

        # There are classes I don't know enough about to decide. Not whitelisting in case.
        # IfcAlignmentParameterSegment
        # IfcBoundaryCondition
        # IfcStructuralConnectionCondition
        # IfcStructuralLoad

        # Keep list sorted alphabetically.
        whitelisted_classes = [
            "IfcActorRole",
            "IfcAddress",
            "IfcApplication",
            "IfcAppliedValue",
            "IfcConnectionGeometry",
            "IfcCoordinateReferenceSystem",
            "IfcDerivedUnit",
            "IfcDerivedUnitElement",
            "IfcDimensionalExponents",
            "IfcExternalReference",
            "IfcGridAxis",
            "IfcIrregularTimeSeriesValue",
            "IfcLightDistributionData",
            "IfcLightIntensityDistribution",
            "IfcMeasureWithUnit",
            "IfcMonetaryUnit",
            "IfcNamedUnit",
            "IfcObjectPlacement",
            "IfcOrganization",  # Should be referenced as part of an actor
            "IfcOwnerHistory",
            "IfcPerson",  # Should be referenced as part of an actor
            "IfcPersonAndOrganization",  # Should be referenced as part of an actor
            "IfcPhysicalQuantity",
            "IfcPresentationItem",
            "IfcProductDefinitionShape",
            "IfcPropertyAbstraction",
            "IfcPropertyDefinition",  # A bit of a questionable one, and the odd one out from IfcRoot.
            "IfcRecurrencePattern",
            "IfcReference",
            "IfcRepresentation",
            # "IfcRepresentationContext",  # Can be present even in basic empty project.
            "IfcRepresentationItem",
            "IfcRepresentationMap",
            "IfcSchedulingTime",
            "IfcShapeAspect",
            "IfcTable",
            "IfcTableColumn",
            "IfcTableRow",
            "IfcTextureCoordinateIndices",
            "IfcTimePeriod",
            "IfcTimeSeries",
            "IfcTimeSeriesValue",
            "IfcUnitAssignment",
            "IfcVirtualGridIntersection",
        ]

        total_purged = 0
        while True:
            total_batches = 0
            print("*" * 100)
            total_batch_purged = 0
            for ifc_class in whitelisted_classes:
                total_class_purged = 0
                try:
                    elements = tool.Ifc.get().by_type(ifc_class)
                except:
                    continue  # Probably not in this schema?
                to_purge = set()
                for element in elements:
                    try:
                        if ifc_class == "IfcRepresentationItem" and element.is_a("IfcStyledItem") and element.Item:
                            continue
                    except:
                        to_purge.add(element.id())  # It's invalid, definitely purge it.
                    if tool.Ifc.get().get_total_inverses(element) == 0:
                        to_purge.add(element.id())
                for element_id in to_purge:
                    try:
                        element = tool.Ifc.get().by_id(element_id)
                        ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), element)
                        total_class_purged += 1
                    except:
                        continue
                if total_class_purged > 0:
                    total_batch_purged += total_class_purged
                    print(f"Auto purged {total_class_purged} {ifc_class}")
            if total_batch_purged > 0:
                total_purged += total_batch_purged
                print(f"Auto purged in batch: {total_batch_purged}")
            total_batches += 1
            if total_batch_purged == 0:
                break
            elif total_batches > 20:
                print("Finished 20 batches. Manually stopping in case of infinite loop.")
        self.report({"INFO"}, f"Auto purged {total_purged} orphaned elements")
        if self.filepath:
            tool.Ifc.get().write(self.filepath)


class PurgeUnusedObjects(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.purge_unused_objects"
    bl_label = "Purge Unused Objects"
    bl_options = {"REGISTER", "UNDO"}

    object_type: bpy.props.EnumProperty(
        name="Object Type",
        items=(
            ("TYPE", "Type", ""),
            ("PROFILE", "Profile", ""),
            ("STYLE", "Style", ""),
            ("MATERIAL", "Material", ""),
        ),
    )

    def _execute(self, context):
        object_type = self.object_type
        if object_type == "TYPE":
            purged = bonsai.core.type.purge_unused_types(tool.Ifc, tool.Type, tool.Geometry)
        elif object_type == "PROFILE":
            purged = bonsai.core.profile.purge_unused_profiles(tool.Ifc, tool.Profile)
        elif object_type == "STYLE":
            purged = tool.Style.purge_unused_styles()
        elif object_type == "MATERIAL":
            purged = tool.Material.purge_unused_materials()
        else:
            self.report({"ERROR"}, f"Invalid object type {object_type}.")
            return {"CANCELLED"}

        self.report({"INFO"}, f"{purged} unused {object_type.lower()}s were purged.")

        if purged == 0:
            return

        scene = context.scene
        if object_type == "PROFILE":
            if scene.BIMProfileProperties.is_editing:
                bpy.ops.bim.load_profiles()
        elif object_type == "STYLE":
            if scene.BIMStylesProperties.is_editing:
                bpy.ops.bim.load_styles()
        elif object_type == "MATERIAL":
            if scene.BIMMaterialProperties.is_editing:
                bpy.ops.bim.load_materials()


class MergeIdenticalObjects(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.merge_identical_objects"
    bl_label = "Merge Identical Objects"
    bl_description = "For materials currently only IfcMaterials are supported"
    bl_options = {"REGISTER", "UNDO"}

    object_type: bpy.props.EnumProperty(
        name="Object Type",
        items=(
            ("TYPE", "Type", ""),
            ("PROFILE", "Profile", ""),
            ("STYLE", "Style", ""),
            ("MATERIAL", "Material", ""),
        ),
    )

    def _execute(self, context):
        object_type: str = self.object_type
        if object_type in ("STYLE", "MATERIAL"):
            merged_data = tool.Debug.merge_identical_objects(object_type)
        else:
            self.report({"ERROR"}, f"Invalid object type {object_type}.")
            return {"CANCELLED"}
        plural_object_type = f"{object_type.lower()}s"
        if merged_data:
            print(f"Merged {plural_object_type}:")
            for element_type, element_names in merged_data.items():
                print(f"- {element_type}: {', '.join(element_names)}")
        merged = sum(len(v) for v in merged_data.values())

        msg = " See system console for details." if merged else ""
        self.report({"INFO"}, f"{merged} identical {plural_object_type} were merged.{msg}")

        if merged == 0:
            return

        scene = context.scene
        if object_type == "PROFILE":
            if scene.BIMProfileProperties.is_editing:
                bpy.ops.bim.load_profiles()
        elif object_type == "STYLE":
            if scene.BIMStylesProperties.is_editing:
                bpy.ops.bim.load_styles()
        elif object_type == "MATERIAL":
            if scene.BIMMaterialProperties.is_editing:
                bpy.ops.bim.load_materials()


class PipInstall(bpy.types.Operator):
    bl_idname = "bim.pip_install"
    bl_label = "Pip Install"
    bl_description = "Installs a package from PyPI"
    name: bpy.props.StringProperty()

    def execute(self, context):
        blender_path = Path(bpy.app.binary_path).parent
        target = next(
            path for p in sys.path if (path := Path(p)).name == "site-packages" and path.is_relative_to(blender_path)
        ).__str__()
        py_exec = str(sys.executable)

        print("Detected executable:", py_exec)
        print("Installing to:", target)

        subprocess.call([py_exec, "-m", "ensurepip", "--user"])
        subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip"])
        # Trusted host to make things simpler due to some enterprise network restrictions
        return_code = subprocess.call(
            [
                py_exec,
                "-m",
                "pip",
                "install",
                f"--target={target}",
                "--upgrade",
                self.name,
                "--trusted-host",
                "pypi.org",
                "--trusted-host",
                "files.pythonhosted.org",
            ]
        )
        if return_code == 0:
            self.report({"INFO"}, f"'{self.name}' was successfully installed.")
        else:
            self.report(
                {"ERROR"},
                f"Error installing '{self.name}', see system console for details (return code '{return_code}').",
            )
        return {"FINISHED"}


class DebugActiveDrawing(bpy.types.Operator):
    bl_idname = "bim.debug_active_drawing"
    bl_label = "Search Active Drawing For Failing Elements"
    bl_description = (
        "Will iterate over all visible drawing's objects, trying to narrow down the list of possible failing objects"
    )

    def execute(self, context: bpy.types.Context):
        props = context.scene.DocProperties
        drawing_item = props.drawings[props.active_drawing_index]
        drawing = tool.Ifc.get().by_id(drawing_item.ifc_definition_id)

        GREEN = "\033[92m"
        CYAN = "\033[96m"
        END = "\033[0m"
        ATTEMPS = 10

        # run create drawing with sync for once
        # to make sure everything is actually in sync
        try:
            bpy.ops.bim.create_drawing(sync=True)
        except:
            pass
        else:
            self.report({"INFO"}, "No errors creating drawing, nothing to investigate.")
            return {"FINISHED"}

        all_elements = [e for obj in context.visible_objects if (e := tool.Ifc.get_entity(obj))]
        all_elements = set(all_elements)

        original_exclude = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", "Exclude")
        pset = tool.Pset.get_element_pset(drawing, "EPset_Drawing")

        def drawing_fails_to_load(chunk_to_include: set) -> bool:
            current_elements = all_elements - chunk_to_include
            excluded_guids = ", ".join([e.GlobalId for e in current_elements if hasattr(e, "GlobalId")])
            new_exclude = "" if not original_exclude else f"{original_exclude}, "
            new_exclude += excluded_guids
            tool.Ifc.run("pset.edit_pset", pset=pset, properties={"Exclude": new_exclude})

            try:
                bpy.ops.bim.create_drawing(sync=False)
                result = False
            except Exception as e:
                # print(e)
                result = True

            tool.Ifc.run("pset.edit_pset", pset=pset, properties={"Exclude": original_exclude})
            return result

        def test_elements(elements: list[ifcopenshell.entity_instance], attempts: int = ATTEMPS) -> None:
            print(f"{CYAN}processing {len(elements)} elements{END}")
            if not elements:
                print(f"Empty list of elements, will stop...")
                return

            n_elements = len(elements)
            middle = int(n_elements / 2)
            chunk1, chunk2 = elements[:middle], elements[middle:]
            test_chunk_1 = drawing_fails_to_load(set(chunk1))
            test_chunk_2 = drawing_fails_to_load(set(chunk2))

            if (
                # both chunks do not fail anymore
                (not test_chunk_1 and not test_chunk_2)
                # or we have 1 element chunk that is still failing
                or (test_chunk_1 and not chunk2)
                or (test_chunk_2 and not chunk1)
            ):
                if attempts == 0 or n_elements in (1, 2):
                    print(f"{GREEN}Couldn't narrow it down any further.{END}")
                    print(f"It's some of the {n_elements} elements:")
                    print(elements)

                    print("Let's test excluding them...")
                    for element in elements:
                        test = drawing_fails_to_load(all_elements - {element})
                        if test:
                            print(f"{CYAN}Excluding element didn't fixed the drawing: {END}")
                            print(element)
                        else:
                            print(f"{GREEN}Excluding element fixed the drawing: {END}")
                            print(element)
                else:
                    print(f"{CYAN}Will try to reshuffle elements and try again, attempt {ATTEMPS-attempts+1}/{ATTEMPS}")
                    attempts -= 1
                    random.shuffle(elements)
                    test_elements(elements, attempts)
                return

            # if chunk fails we need to investigate it further
            if test_chunk_1:
                test_elements(chunk1)

            if test_chunk_2:
                test_elements(chunk2)

        test_elements(list(all_elements))

        self.report({"INFO"}, "See system console for the results")
        return {"FINISHED"}


class ToggleDetailedIOSLogs(bpy.types.Operator):
    bl_idname = "bim.toggle_detailed_ios_logs"
    bl_label = "Toggle Detailed IfcOpenShell Logs"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Turn on detailed IfcOpenShell logs in the system console.\n"
        + "Could be useful debugging issues "
        + "loading IFC representations / serializing IFC geometry."
        + "\n\nALT+CLICK to disable the logs"
    )
    # NOTE: No idea if it's possible to check from Python
    # whether detailed logs are currently enabled or not.
    # Therefore we just distinguish between click
    # and alt-click to allow enabling/disabling the logs.
    turn_on_logs: bpy.props.BoolProperty(name="Turn On Logs", default=True, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.turn_on_logs = False
        return self.execute(context)

    def execute(self, context):
        import ifcopenshell.ifcopenshell_wrapper as wrapper

        if self.turn_on_logs:
            wrapper.turn_on_detailed_logging()
            self.report({"INFO"}, "Detailed IfcOpenShell logs turned on.")
        else:
            wrapper.turn_off_detailed_logging()
            self.report({"INFO"}, "Detailed IfcOpenShell logs turned off.")
        return {"FINISHED"}


class RestartBlender(bpy.types.Operator):
    bl_idname = "bim.restart_blender"
    bl_label = "Restart Blender"
    bl_description = "Blender will be immediately restarted, save your data first before running this operator"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import os

        path = bpy.app.binary_path
        os.execv(path, sys.argv)
