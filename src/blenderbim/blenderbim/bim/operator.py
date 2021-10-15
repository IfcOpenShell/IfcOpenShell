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
import json
import tempfile
import logging
import webbrowser
import ifcopenshell
import blenderbim.bim.handler
from . import schema
from blenderbim.bim.ifc import IfcStore
from mathutils import Vector, Matrix, Euler
from math import radians


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

    @classmethod
    def poll(cls, context):
        return context.active_object and bpy.data.node_groups.get("Section Override")

    def execute(self, context):
        name = context.active_object.name
        section_override = bpy.data.node_groups.get("Section Override")
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

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        for obj in context.selected_objects:
            obj.color = context.scene.BIMProperties.override_colour
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class SetViewportShadowFromSun(bpy.types.Operator):
    bl_idname = "bim.set_viewport_shadow_from_sun"
    bl_label = "Set Viewport Shadow from Sun"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        # The vector used for the light direction is a bit funny
        mat = Matrix(((-1.0, 0.0, 0.0, 0.0), (0.0, 0, 1.0, 0.0), (-0.0, -1.0, 0, 0.0), (0.0, 0.0, 0.0, 1.0)))
        context.scene.display.light_direction = mat.inverted() @ (
            context.active_object.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        )
        return {"FINISHED"}


class SnapSpacesTogether(bpy.types.Operator):
    bl_idname = "bim.snap_spaces_together"
    bl_label = "Snap Spaces Together"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        threshold = 0.5
        processed_polygons = set()
        selected_mesh_objects = [o for o in context.selected_objects if o.type == "MESH"]
        for obj in selected_mesh_objects:
            for polygon in obj.data.polygons:
                center = obj.matrix_world @ polygon.center
                distance = None
                for obj2 in selected_mesh_objects:
                    if obj2 == obj:
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
      
      
class ConfigureVisibility(bpy.types.Operator):
    bl_idname = "bim.configure_visibility"
    bl_label = "Select which modules are available in the UI"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        modules = bpy.context.preferences.addons["blenderbim"].preferences.module_visibility

        grid = layout.column_flow(columns=3)
        for module in modules.__annotations__.keys():
            grid.prop(modules, module)

    def execute(self, context):
        return {'FINISHED'} 