import os
import bpy
import time
import json
import tempfile
import logging
import webbrowser
import ifcopenshell
from . import export_ifc
from . import import_ifc
from . import schema
from blenderbim.bim.ifc import IfcStore
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector, Matrix, Euler, geometry
from math import radians, degrees, atan, tan, cos, sin


class ExportIFC(bpy.types.Operator):
    bl_idname = "export_ifc.bim"
    bl_label = "Export IFC"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml;*.ifcjson", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    json_version: bpy.props.EnumProperty(items=[("4", "4", ""), ("5a", "5a", "")], name="IFC JSON Version")
    json_compact: bpy.props.BoolProperty(name="Export Compact IFCJSON", default=False)

    def invoke(self, context, event):
        if not IfcStore.get_file():
            self.report({"ERROR"}, "No IFC project is available for export - create or import a project first.")
            return {"FINISHED"}
        if context.scene.BIMProperties.ifc_file:
            self.filepath = context.scene.BIMProperties.ifc_file
            return self.execute(context)
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".ifc")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        start = time.time()
        logger = logging.getLogger("ExportIFC")
        path_log = os.path.join(bpy.context.scene.BIMProperties.data_dir, "process.log"),
        if not os.access(bpy.context.scene.BIMProperties.data_dir, os.W_OK):
            path_log = os.path.join(tempfile.mkdtemp(), "process.log")
        logging.basicConfig(
            filename=path_log,
            filemode="a",
            level=logging.DEBUG,
        )
        extension = self.filepath.split(".")[-1]
        if extension == "ifczip":
            output_file = bpy.path.ensure_ext(self.filepath, ".ifczip")
        elif extension == "ifcjson":
            output_file = bpy.path.ensure_ext(self.filepath, ".ifcjson")
        else:
            output_file = bpy.path.ensure_ext(self.filepath, ".ifc")

        settings = export_ifc.IfcExportSettings.factory(context, output_file, logger)
        settings.json_version = self.json_version
        settings.json_compact = self.json_compact

        ifc_exporter = export_ifc.IfcExporter(settings)
        settings.logger.info("Starting export")
        ifc_exporter.export()
        settings.logger.info("Export finished in {:.2f} seconds".format(time.time() - start))
        print("Export finished in {:.2f} seconds".format(time.time() - start))
        scene = context.scene
        if not scene.DocProperties.ifc_files:
            new = scene.DocProperties.ifc_files.add()
            new.name = output_file
        if not scene.BIMProperties.ifc_file:
            scene.BIMProperties.ifc_file = output_file
        if bpy.data.is_saved and bpy.data.is_dirty and bpy.data.filepath:
            bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)
        return {"FINISHED"}


class ImportIFC(bpy.types.Operator, ImportHelper):
    bl_idname = "import_ifc.bim"
    bl_label = "Import IFC"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})

    should_auto_set_workarounds: bpy.props.BoolProperty(name="Automatically Set Vendor Workarounds", default=True)
    should_use_cpu_multiprocessing: bpy.props.BoolProperty(name="Import with CPU Multiprocessing", default=True)
    should_merge_by_class: bpy.props.BoolProperty(name="Import and Merge by Class", default=False)
    should_merge_by_material: bpy.props.BoolProperty(name="Import and Merge by Material", default=False)
    should_merge_materials_by_colour: bpy.props.BoolProperty(name="Import and Merge Materials by Colour", default=False)
    should_clean_mesh: bpy.props.BoolProperty(name="Import and Clean Mesh", default=True)
    deflection_tolerance: bpy.props.FloatProperty(name="Import Deflection Tolerance", default=0.001)
    angular_tolerance: bpy.props.FloatProperty(name="Import Angular Tolerance", default=0.5)
    should_offset_model: bpy.props.BoolProperty(name="Import and Offset Model", default=False)
    model_offset_coordinates: bpy.props.StringProperty(name="Model Offset Coordinates", default="0,0,0")
    ifc_import_filter: bpy.props.EnumProperty(
        items=[
            ("NONE", "None", ""),
            ("WHITELIST", "Whitelist", ""),
            ("BLACKLIST", "Blacklist", ""),
        ],
        name="Import Filter",
    )
    ifc_selector: bpy.props.StringProperty(default="", name="IFC Selector")

    def execute(self, context):
        start = time.time()
        logger = logging.getLogger("ImportIFC")
        path_log = os.path.join(context.scene.BIMProperties.data_dir, "process.log"),
        if not os.access(context.scene.BIMProperties.data_dir, os.W_OK):
            path_log = os.path.join(tempfile.mkdtemp(), "process.log")
        logging.basicConfig(
            filename=path_log,
            filemode="a",
            level=logging.DEBUG,
        )

        settings = import_ifc.IfcImportSettings.factory(context, self.filepath, logger)
        settings.should_auto_set_workarounds = self.should_auto_set_workarounds
        settings.should_use_cpu_multiprocessing = self.should_use_cpu_multiprocessing
        settings.should_merge_by_class = self.should_merge_by_class
        settings.should_merge_by_material = self.should_merge_by_material
        settings.should_merge_materials_by_colour = self.should_merge_materials_by_colour
        settings.should_clean_mesh = self.should_clean_mesh
        settings.deflection_tolerance = self.deflection_tolerance
        settings.angular_tolerance = self.angular_tolerance
        settings.should_offset_model = self.should_offset_model
        settings.model_offset_coordinates = (
            [float(o) for o in self.model_offset_coordinates.split(",")] if self.model_offset_coordinates else (0, 0, 0)
        )
        settings.ifc_import_filter = self.ifc_import_filter
        settings.ifc_selector = self.ifc_selector

        settings.logger.info("Starting import")
        ifc_importer = import_ifc.IfcImporter(settings)
        ifc_importer.execute()
        settings.logger.info("Import finished in {:.2f} seconds".format(time.time() - start))
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class OpenUri(bpy.types.Operator):
    bl_idname = "bim.open_uri"
    bl_label = "Open URI"
    uri: bpy.props.StringProperty()

    def execute(self, context):
        webbrowser.open(self.uri)
        return {"FINISHED"}


class SelectIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_ifc_file"
    bl_label = "Select IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})

    def execute(self, context):
        if os.path.exists(self.filepath) and "ifc" in os.path.splitext(self.filepath)[1]:
            context.scene.BIMProperties.ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectDataDir(bpy.types.Operator):
    bl_idname = "bim.select_data_dir"
    bl_label = "Select Data Directory"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BIMProperties.data_dir = os.path.dirname(self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectSchemaDir(bpy.types.Operator):
    bl_idname = "bim.select_schema_dir"
    bl_label = "Select Schema Directory"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BIMProperties.schema_dir = os.path.dirname(self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class OpenUpstream(bpy.types.Operator):
    bl_idname = "bim.open_upstream"
    bl_label = "Open Upstream Reference"
    page: bpy.props.StringProperty()

    def execute(self, context):
        if self.page == "home":
            webbrowser.open("https://blenderbim.org/")
        elif self.page == "docs":
            webbrowser.open("https://blenderbim.org/docs/")
        elif self.page == "wiki":
            webbrowser.open("https://wiki.osarch.org/index.php?title=Category:BlenderBIM_Add-on")
        elif self.page == "community":
            webbrowser.open("https://community.osarch.org/")
        return {"FINISHED"}


class AddSectionPlane(bpy.types.Operator):
    bl_idname = "bim.add_section_plane"
    bl_label = "Add Temporary Section Cutaway"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = self.create_section_obj(context)
        if not self.has_section_override_node():
            self.create_section_compare_node()
            self.create_section_override_node(obj, context)
        else:
            self.append_obj_to_section_override_node(obj)
        self.add_default_material_if_none_exists(context)
        self.override_materials()
        return {"FINISHED"}

    def create_section_obj(self, context):
        section = bpy.data.objects.new("Section", None)
        section.empty_display_type = "SINGLE_ARROW"
        section.empty_display_size = 5
        section.show_in_front = True
        if (
            context.active_object
            and context.active_object.select_get()
            and isinstance(context.active_object.data, bpy.types.Camera)
        ):
            section.matrix_world = (
                context.active_object.matrix_world @ Euler((radians(180.0), 0.0, 0.0), "XYZ").to_matrix().to_4x4()
            )
        else:
            section.rotation_euler = Euler((radians(180.0), 0.0, 0.0), "XYZ")
            section.location = context.scene.cursor.location
        collection = bpy.data.collections.get("Sections")
        if not collection:
            collection = bpy.data.collections.new("Sections")
            context.scene.collection.children.link(collection)
        collection.objects.link(section)
        return section

    def has_section_override_node(self):
        return bpy.data.node_groups.get("Section Override")

    def create_section_compare_node(self):
        group = bpy.data.node_groups.new("Section Compare", type="ShaderNodeTree")
        group_input = group.nodes.new(type="NodeGroupInput")
        group_output = group.nodes.new(type="NodeGroupOutput")
        separate_xyz_a = group.nodes.new(type="ShaderNodeSeparateXYZ")
        separate_xyz_b = group.nodes.new(type="ShaderNodeSeparateXYZ")
        gt_a = group.nodes.new(type="ShaderNodeMath")
        gt_a.operation = "GREATER_THAN"
        gt_a.inputs[1].default_value = 0
        gt_b = group.nodes.new(type="ShaderNodeMath")
        gt_b.operation = "GREATER_THAN"
        gt_b.inputs[1].default_value = 0
        add = group.nodes.new(type="ShaderNodeMath")
        compare = group.nodes.new(type="ShaderNodeMath")
        compare.operation = "COMPARE"
        compare.inputs[1].default_value = 2
        group.links.new(group_input.outputs[""], separate_xyz_a.inputs[0])
        group.links.new(group_input.outputs[""], separate_xyz_b.inputs[0])
        group.links.new(separate_xyz_a.outputs[2], gt_a.inputs[0])
        group.links.new(separate_xyz_b.outputs[2], gt_b.inputs[0])
        group.links.new(gt_a.outputs[0], add.inputs[0])
        group.links.new(gt_b.outputs[0], add.inputs[1])
        group.links.new(add.outputs[0], compare.inputs[0])
        group.links.new(compare.outputs[0], group_output.inputs[""])

    def create_section_override_node(self, obj, context):
        group = bpy.data.node_groups.new("Section Override", type="ShaderNodeTree")

        group_input = group.nodes.new(type="NodeGroupInput")
        group_output = group.nodes.new(type="NodeGroupOutput")

        backfacing = group.nodes.new(type="ShaderNodeNewGeometry")
        backfacing_mix = group.nodes.new(type="ShaderNodeMixShader")
        emission = group.nodes.new(type="ShaderNodeEmission")
        emission.inputs[0].default_value = list(context.scene.BIMProperties.section_plane_colour) + [1]

        group.links.new(backfacing.outputs["Backfacing"], backfacing_mix.inputs[0])
        group.links.new(group_input.outputs[""], backfacing_mix.inputs[1])
        group.links.new(emission.outputs["Emission"], backfacing_mix.inputs[2])

        transparent = group.nodes.new(type="ShaderNodeBsdfTransparent")
        section_mix = group.nodes.new(type="ShaderNodeMixShader")
        section_mix.name = "Section Mix"

        group.links.new(transparent.outputs["BSDF"], section_mix.inputs[1])
        group.links.new(backfacing_mix.outputs["Shader"], section_mix.inputs[2])

        group.links.new(section_mix.outputs["Shader"], group_output.inputs[""])

        cut_obj = group.nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        section_compare = group.nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")
        section_compare.name = "Last Section Compare"
        value = group.nodes.new(type="ShaderNodeValue")
        value.name = "Mock Section"
        group.links.new(cut_obj.outputs["Object"], section_compare.inputs[0])
        group.links.new(value.outputs[0], section_compare.inputs[1])
        group.links.new(section_compare.outputs[0], section_mix.inputs[0])

    def append_obj_to_section_override_node(self, obj):
        group = bpy.data.node_groups.get("Section Override")
        cut_obj = group.nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        section_compare = group.nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")

        last_compare = group.nodes.get("Last Section Compare")
        last_compare.name = "Section Compare"
        mock_section = group.nodes.get("Mock Section")
        section_mix = group.nodes.get("Section Mix")

        group.links.new(last_compare.outputs[0], section_compare.inputs[0])
        group.links.new(mock_section.outputs[0], section_compare.inputs[1])
        group.links.new(cut_obj.outputs["Object"], last_compare.inputs[1])
        group.links.new(section_compare.outputs[0], section_mix.inputs[0])

        section_compare.name = "Last Section Compare"

    def add_default_material_if_none_exists(self, context):
        material = bpy.data.materials.get("Section Override")
        if not material:
            material = bpy.data.materials.new("Section Override")
            material.use_nodes = True

        if context.scene.BIMProperties.should_section_selected_objects:
            objects = list(context.selected_objects)
        else:
            objects = list(context.visible_objects)

        for obj in objects:
            aggregate = obj.instance_collection
            if aggregate and "IfcRelAggregates/" in aggregate.name:
                for part in aggregate.objects:
                    objects.append(part)
            if not (obj.data and hasattr(obj.data, "materials") and obj.data.materials and obj.data.materials[0]):
                if obj.data and hasattr(obj.data, "materials"):
                    if len(obj.material_slots):
                        obj.material_slots[0].material = material
                    else:
                        obj.data.materials.append(material)

    def override_materials(self):
        override = bpy.data.node_groups.get("Section Override")
        for material in bpy.data.materials:
            material.use_nodes = True
            if material.node_tree.nodes.get("Section Override"):
                continue
            material.blend_method = "HASHED"
            material.shadow_method = "HASHED"
            material_output = self.get_node(material.node_tree.nodes, "OUTPUT_MATERIAL")
            if not material_output:
                continue
            from_socket = material_output.inputs[0].links[0].from_socket
            section_override = material.node_tree.nodes.new(type="ShaderNodeGroup")
            section_override.name = "Section Override"
            section_override.node_tree = override
            material.node_tree.links.new(from_socket, section_override.inputs[0])
            material.node_tree.links.new(section_override.outputs[0], material_output.inputs[0])

    def get_node(self, nodes, node_type):
        for node in nodes:
            if node.type == node_type:
                return node


class RemoveSectionPlane(bpy.types.Operator):
    bl_idname = "bim.remove_section_plane"
    bl_label = "Remove Temporary Section Cutaway"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        name = context.active_object.name
        section_override = bpy.data.node_groups.get("Section Override")
        if not section_override:
            return {"FINISHED"}
        for node in section_override.nodes:
            if node.type != "TEX_COORD" or node.object.name != name:
                continue
            section_compare = node.outputs["Object"].links[0].to_node
            # If the tex coord links to section_compare.inputs[1], it is called 'Input_3'
            if node.outputs["Object"].links[0].to_socket.identifier == "Input_3":
                section_override.links.new(
                    section_compare.inputs[0].links[0].from_socket, section_compare.outputs[0].links[0].to_socket
                )
            else:  # If it links to section_compare.inputs[0]
                if section_compare.inputs[1].links[0].from_node.name == "Mock Section":
                    # Then it is the very last section. Purge everything.
                    self.purge_all_section_data(context)
                    return {"FINISHED"}
                section_override.links.new(
                    section_compare.inputs[1].links[0].from_socket, section_compare.outputs[0].links[0].to_socket
                )
            section_override.nodes.remove(section_compare)
            section_override.nodes.remove(node)

            old_last_compare = section_override.nodes.get("Last Section Compare")
            old_last_compare.name = "Section Compare"
            section_mix = section_override.nodes.get("Section Mix")
            new_last_compare = section_mix.inputs[0].links[0].from_node
            new_last_compare.name = "Last Section Compare"
        bpy.ops.object.delete({"selected_objects": [context.active_object]})
        return {"FINISHED"}

    def purge_all_section_data(self, context):
        bpy.data.materials.remove(bpy.data.materials.get("Section Override"))
        for material in bpy.data.materials:
            if not material.node_tree:
                continue
            override = material.node_tree.nodes.get("Section Override")
            if not override:
                continue
            material.node_tree.links.new(
                override.inputs[0].links[0].from_socket, override.outputs[0].links[0].to_socket
            )
            material.node_tree.nodes.remove(override)
        bpy.data.node_groups.remove(bpy.data.node_groups.get("Section Override"))
        bpy.data.node_groups.remove(bpy.data.node_groups.get("Section Compare"))
        bpy.ops.object.delete({"selected_objects": [context.active_object]})


class ReloadIfcFile(bpy.types.Operator):
    bl_idname = "bim.reload_ifc_file"
    bl_label = "Reload IFC File"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # TODO: reimplement. See #1222.
        return {"FINISHED"}


class AddIfcFile(bpy.types.Operator):
    bl_idname = "bim.add_ifc_file"
    bl_label = "Add IFC File"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.DocProperties.ifc_files.add()
        return {"FINISHED"}


class RemoveIfcFile(bpy.types.Operator):
    bl_idname = "bim.remove_ifc_file"
    bl_label = "Remove IFC File"
    index: bpy.props.IntProperty()
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.DocProperties.ifc_files.remove(self.index)
        return {"FINISHED"}


class SetOverrideColour(bpy.types.Operator):
    bl_idname = "bim.set_override_colour"
    bl_label = "Set Override Colour"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        result = 0
        for obj in context.selected_objects:
            obj.color = context.scene.BIMProperties.override_colour
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class SetViewportShadowFromSun(bpy.types.Operator):
    bl_idname = "bim.set_viewport_shadow_from_sun"
    bl_label = "Set Viewport Shadow from Sun"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # The vector used for the light direction is a bit funny
        mat = Matrix(((-1.0, 0.0, 0.0, 0.0), (0.0, 0, 1.0, 0.0), (-0.0, -1.0, 0, 0.0), (0.0, 0.0, 0.0, 1.0)))
        context.scene.display.light_direction = mat.inverted() @ (
            context.active_object.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        )
        return {"FINISHED"}


class LinkIfc(bpy.types.Operator):
    bl_idname = "bim.link_ifc"
    bl_label = "Link IFC"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # context.active_object.active_material.BIMMaterialProperties.location = self.filepath
        # coll_name = "MyCollection"

        with bpy.data.libraries.load(self.filepath, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes

        for scene in bpy.data.scenes:
            if not scene.library or scene.library.filepath != self.filepath:
                continue
            for child in scene.collection.children:
                if "IfcProject" not in child.name:
                    continue
                bpy.data.scenes[0].collection.children.link(child)

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SnapSpacesTogether(bpy.types.Operator):
    bl_idname = "bim.snap_spaces_together"
    bl_label = "Snap Spaces Together"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        threshold = 0.5
        processed_polygons = set()
        for obj in context.selected_objects:
            if obj.type != "MESH":
                continue
            for polygon in obj.data.polygons:
                center = obj.matrix_world @ polygon.center
                distance = None
                for obj2 in context.selected_objects:
                    if obj2 == obj or obj.type != "MESH":
                        continue
                    result = obj2.ray_cast(obj2.matrix_world.inverted() @ center, polygon.normal, distance=threshold)
                    if not result[0]:
                        continue
                    hit = obj2.matrix_world @ result[1]
                    distance = (hit - center).length / 2
                    if distance < 0.01:
                        distance = None
                        break

                    if (obj2.name, result[3]) in processed_polygons:
                        distance *= 2
                        continue

                    offset = polygon.normal * distance * -1
                    processed_polygons.add((obj2.name, result[3]))
                    for v in obj2.data.polygons[result[3]].vertices:
                        obj2.data.vertices[v].co += offset
                    break
                if distance:
                    offset = polygon.normal * distance
                    processed_polygons.add((obj.name, polygon.index))
                    for v in polygon.vertices:
                        obj.data.vertices[v].co += offset
        return {"FINISHED"}


class SelectExternalMaterialDir(bpy.types.Operator):
    bl_idname = "bim.select_external_material_dir"
    bl_label = "Select Material File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # TODO: this is dead code, awaiting reimplementation. See #1222.
        context.active_object.active_material.BIMMaterialProperties.location = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class FetchExternalMaterial(bpy.types.Operator):
    bl_idname = "bim.fetch_external_material"
    bl_label = "Fetch External Material"

    def execute(self, context):
        # TODO: this is dead code, awaiting reimplementation. See #1222.
        location = context.active_object.active_material.BIMMaterialProperties.location
        if location[-6:] != ".mpass":
            return {"FINISHED"}
        if not os.path.isabs(location):
            location = os.path.join(context.scene.BIMProperties.data_dir, location)
        with open(location) as f:
            self.material_pass = json.load(f)
        if context.scene.render.engine == "BLENDER_EEVEE" and "eevee" in self.material_pass:
            self.fetch_eevee_or_cycles("eevee", context)
        elif context.scene.render.engine == "CYCLES" and "cycles" in self.material_pass:
            self.fetch_eevee_or_cycles("cycles", context)
        return {"FINISHED"}

    def fetch_eevee_or_cycles(self, name, context):
        identification = context.active_object.active_material.BIMMaterialProperties.identification
        uri = self.material_pass[name]["uri"]
        if not os.path.isabs(uri):
            uri = os.path.join(context.scene.BIMProperties.data_dir, uri)
        bpy.ops.wm.link(filename=identification, directory=os.path.join(uri, "Material"))
        for material in bpy.data.materials:
            if material.name == identification and material.library:
                context.active_object.material_slots[0].material = material
                return


class FetchObjectPassport(bpy.types.Operator):
    bl_idname = "bim.fetch_object_passport"
    bl_label = "Fetch Object Passport"

    def execute(self, context):
        # TODO: this is dead code, awaiting reimplementation. See #1222.
        for reference in context.active_object.BIMObjectProperties.document_references:
            reference = context.scene.BIMProperties.document_references[reference.name]
            if reference.location[-6:] == ".blend":
                self.fetch_blender(reference, context)
        return {"FINISHED"}

    def fetch_blender(self, reference, context):
        bpy.ops.wm.link(filename=reference.name, directory=os.path.join(reference.location, "Mesh"))
        context.active_object.data = bpy.data.meshes[reference.name]


class CopyPropertyToSelection(bpy.types.Operator):
    bl_idname = "bim.copy_property_to_selection"
    bl_label = "Copy Property To Selection"
    pset_name: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()
    prop_value: bpy.props.StringProperty()

    def execute(self, context):
        # TODO: this is dead code, awaiting reimplementation. See #1222.
        for obj in context.selected_objects:
            if "/" not in obj.name:
                continue
            pset = obj.BIMObjectProperties.psets.get(self.pset_name)
            if not pset:
                applicable_psets = schema.ifc.psetqto.get_applicable(obj.name.split("/")[0], pset_only=True)
                for pset_template in applicable_psets:
                    if pset_template.Name == self.pset_name:
                        break
                else:
                    continue
                pset = obj.BIMObjectProperties.psets.add()
                pset.name = self.pset_name
                for template_prop_name in (p.Name for p in pset_template.HasPropertyTemplates):
                    prop = pset.properties.add()
                    prop.name = template_prop_name
            prop = pset.properties.get(self.prop_name)
            if prop:
                prop.string_value = self.prop_value
        return {"FINISHED"}


class CopyAttributeToSelection(bpy.types.Operator):
    bl_idname = "bim.copy_attribute_to_selection"
    bl_label = "Copy Attribute To Selection"
    attribute_name: bpy.props.StringProperty()
    attribute_value: bpy.props.StringProperty()

    def execute(self, context):
        # TODO: this is dead code, awaiting reimplementation. See #1222.
        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(context.scene.BIMProperties.export_schema)
        self.applicable_attributes_cache = {}
        for obj in context.selected_objects:
            if "/" not in obj.name:
                continue
            attribute = obj.BIMObjectProperties.attributes.get(self.attribute_name)
            if not attribute:
                applicable_attributes = self.get_applicable_attributes(obj.name.split("/")[0])
                if self.attribute_name not in applicable_attributes:
                    continue
                attribute = obj.BIMObjectProperties.attributes.add()
                attribute.name = self.attribute_name
            attribute.string_value = self.attribute_value
        return {"FINISHED"}

    def get_applicable_attributes(self, ifc_class):
        if ifc_class not in self.applicable_attributes_cache:
            self.applicable_attributes_cache[ifc_class] = [
                a.name() for a in self.schema.declaration_by_name(ifc_class).all_attributes()
            ]
        return self.applicable_attributes_cache[ifc_class]
