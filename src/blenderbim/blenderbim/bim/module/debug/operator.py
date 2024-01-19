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
import platform
import subprocess
import addon_utils
import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.core.debug as core
import blenderbim.bim.handler
import blenderbim.bim.import_ifc as import_ifc
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


class CopyDebugInformation(bpy.types.Operator):
    bl_idname = "bim.copy_debug_information"
    bl_label = "Copy Debug Information"
    bl_description = "Copies debugging information to your clipboard for use in bugreports"

    def execute(self, context):
        version = ".".join(
            [
                str(x)
                for x in [
                    addon.bl_info.get("version", (-1, -1, -1))
                    for addon in addon_utils.modules()
                    if addon.bl_info["name"] == "BlenderBIM"
                ][0]
            ]
        )
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "blender_version": bpy.app.version_string,
            "blenderbim_version": version,
            "ifc": False,
        }

        if tool.Ifc.get():
            info.update(
                {
                    "ifc": os.path.basename(tool.Ifc.get_path()) if os.path.isfile(tool.Ifc.get_path()) else "Unsaved",
                    "schema": tool.Ifc.get().schema,
                    "preprocessor_version": tool.Ifc.get().wrapped_data.header.file_name.preprocessor_version,
                    "originating_system": tool.Ifc.get().wrapped_data.header.file_name.originating_system,
                }
            )

        # Format it in a readable way
        text = "\n".join(f"{k}: {v}" for k, v in info.items())
        print(text)

        if platform.system() == "Windows":
            command = "echo | set /p nul=" + text.strip()
        elif platform.system() == "Darwin":  # for MacOS
            command = 'printf "' + text.strip().replace("\n", "\\n").replace('"', "") + '" | pbcopy'
        else:  # Linux
            command = 'printf "' + text.strip().replace("\n", "\\n").replace('"', "") + '" | xclip -selection clipboard'
        subprocess.run(command, shell=True, check=True)
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
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class ConvertToBlender(bpy.types.Operator):
    bl_idname = "bim.convert_to_blender"
    bl_label = "Convert To Blender File"
    bl_description = "Removes all IFC data, and converts the file to a simple Blender file."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for o in bpy.data.objects:
            if o.type in {"MESH", "EMPTY"}:
                o.BIMObjectProperties.ifc_definition_id = 0
                if o.data:
                    o.data.BIMMeshProperties.ifc_definition_id = 0
        for m in bpy.data.materials:
            m.BIMMaterialProperties.ifc_style_id = False
        bpy.context.scene.BIMProperties.ifc_file = ""
        IfcStore.purge()
        blenderbim.bim.handler.refresh_ui_data()
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
        settings_2d = ifcopenshell.geom.settings()
        settings_2d.set(settings_2d.INCLUDE_CURVES, True)
        failures = []
        excludes = ()  # For the developer to debug with
        for i, element in enumerate(elements, 1):
            if element.GlobalId in excludes:
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

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        logger = logging.getLogger("ImportIFC")
        self.ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
        self.file = IfcStore.get_file()
        element = self.file.by_id(self.step_id or int(context.scene.BIMDebugProperties.step_id))
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


class OverrideDisplayType(bpy.types.Operator):
    bl_idname = "bim.override_display_type"
    bl_label = "Override Display Type"
    display: bpy.props.StringProperty()

    def execute(self, context):
        for obj in context.selected_objects:
            obj.display_type = self.display
        return {"FINISHED"}


class PrintUnusedElementStats(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.print_unused_elements_stats"
    bl_label = "Print Unused Elements Stats"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Print all unused elements in current IFC project in system console, not limited to the selected class"
    )

    ignore_contexts: bpy.props.BoolProperty(name="Ignore Contexts", default=True)
    ignore_relationships: bpy.props.BoolProperty(name="Ignore Relationships", default=True)
    ignore_types: bpy.props.BoolProperty(name="Ignore Types", default=True)
    ignore_styled_items: bpy.props.BoolProperty(name="Ignoer Styled Items", default=True)

    def _execute(self, context):
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

        unused_elements = tool.Debug.print_unused_elements_stats(props.ifc_class_purge, ignore_classes)
        self.report({"INFO"}, f"{unused_elements} unused elements found, check the system console for the details.")


class PurgeUnusedElementsByClass(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.purge_unused_elements_by_class"
    bl_label = "Purge Unused Elements By Class"
    bl_description = (
        "Will find all elements of class that have no inverse refernces and will remove them, use very carefully"
    )
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def _execute(self, context):
        props = context.scene.BIMDebugProperties
        if props.ifc_class_purge:
            purged_elements = core.purge_unused_elements(tool.Ifc, tool.Debug, props.ifc_class_purge)
            self.report({"INFO"}, f"{purged_elements} unused elements found and removed.")
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
            "IfcRecurrencePattern",
            "IfcReference",
            "IfcRepresentation",
            "IfcRepresentationContext",
            "IfcRepresentationItem",
            "IfcRepresentationMap",
            "IfcPropertyDefinition",  # A bit of a questionable one, and the odd one out from IfcRoot.
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
        tool.Ifc.get().write(self.filepath)
