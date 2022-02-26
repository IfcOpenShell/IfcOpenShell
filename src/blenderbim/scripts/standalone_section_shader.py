bl_info = {
    "name": "Section Shader",
    "author": "IfcOpenShell Contributors",
    "version": (0, 0, 999999),
    "blender": (2, 80, 0),
    "location": "Viewport Side Panel",
    "description": "Generate a shader override that creates a fake but fast section cut.",
    "warning": "",
    "doc_url": "",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "category": "Add Mesh",
}


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from mathutils import Vector, Matrix, Euler
from math import radians
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


def update_section_color(self, context):
    section_node_group = bpy.data.node_groups.get("Section Override")
    if section_node_group is None:
        return
    try:
        emission_node = next(n for n in section_node_group.nodes if isinstance(n, bpy.types.ShaderNodeEmission))
        emission_node.inputs[0].default_value = list(self.section_plane_colour) + [1]
    except StopIteration:
        pass


class BIM_OT_add_section_plane(bpy.types.Operator):
    """Add a temporary empty object as a section cutaway. Cull all geometry rendering below the empty's local Z axis"""

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
        group_input.location = 0, 50

        separate_xyz = group.nodes.new(type="ShaderNodeSeparateXYZ")
        separate_xyz.location = 200, 0

        greater = group.nodes.new(type="ShaderNodeMath")
        greater.operation = "GREATER_THAN"
        greater.inputs[1].default_value = 0
        greater.location = 400, 0

        multiply = group.nodes.new(type="ShaderNodeMath")
        multiply.operation = "MULTIPLY"
        multiply.inputs[0].default_value = 1
        multiply.location = 600, 150

        group_output = group.nodes.new(type="NodeGroupOutput")
        group_output.location = 800, 0

        group.links.new(group_input.outputs[""], multiply.inputs[0])
        group.links.new(group_input.outputs[""], separate_xyz.inputs[0])
        group.links.new(separate_xyz.outputs[2], greater.inputs[0])
        group.links.new(greater.outputs[0], multiply.inputs[1])
        group.links.new(multiply.outputs[0], group_output.inputs[""])

    def create_section_override_node(self, obj, context):
        group = bpy.data.node_groups.new("Section Override", type="ShaderNodeTree")
        links = group.links
        nodes = group.nodes

        group_input = nodes.new(type="NodeGroupInput")
        group_output = nodes.new(type="NodeGroupOutput")
        group_output.location = 600, 250

        backfacing_mix = nodes.new(type="ShaderNodeMixShader")
        backfacing_mix.location = group_output.location - Vector((400, 350))

        backfacing = nodes.new(type="ShaderNodeNewGeometry")
        backfacing.location = backfacing_mix.location + Vector((-200, 200))
        group_input.location = backfacing_mix.location - Vector((200, 50))

        emission = nodes.new(type="ShaderNodeEmission")
        emission.inputs[0].default_value = list(context.scene.SectionProperties.section_plane_colour) + [1]
        emission.location = backfacing_mix.location - Vector((200, 150))

        transparent = nodes.new(type="ShaderNodeBsdfTransparent")
        transparent.location = group_output.location - Vector((400, 100))

        section_mix = group.nodes.new(type="ShaderNodeMixShader")
        section_mix.name = "Section Mix"
        section_mix.inputs[0].default_value = 1  # Directly pass input shader when there is no cutaway
        section_mix.location = group_output.location - Vector((200, 0))

        cut_obj = nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        cut_obj.location = group_output.location - Vector((800, 150))

        section_compare = nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")
        section_compare.name = "Last Section Compare"
        section_compare.location = group_output.location - Vector((600, 0))

        links.new(cut_obj.outputs["Object"], section_compare.inputs[1])
        links.new(backfacing.outputs["Backfacing"], backfacing_mix.inputs[0])
        links.new(group_input.outputs[""], backfacing_mix.inputs[1])
        links.new(emission.outputs["Emission"], backfacing_mix.inputs[2])
        links.new(section_compare.outputs[0], section_mix.inputs[0])
        links.new(transparent.outputs["BSDF"], section_mix.inputs[1])
        links.new(backfacing_mix.outputs["Shader"], section_mix.inputs[2])
        links.new(section_mix.outputs["Shader"], group_output.inputs[""])

    def append_obj_to_section_override_node(self, obj):
        group = bpy.data.node_groups.get("Section Override")
        try:
            last_section_node = next(
                n
                for n in group.nodes
                if isinstance(n, bpy.types.ShaderNodeGroup)
                and n.node_tree.name == "Section Compare"
                and not n.inputs[0].links
            )
            offset = Vector((0, 0))
        except StopIteration:
            last_section_node = group.nodes.get("Section Mix")
            offset = Vector((200, 0))
        section_compare = group.nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")
        section_compare.location = last_section_node.location - Vector((200, 0)) - offset

        cut_obj = group.nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        cut_obj.location = last_section_node.location - Vector((400, 150)) - offset

        group.links.new(section_compare.outputs[0], last_section_node.inputs[0])
        group.links.new(cut_obj.outputs["Object"], section_compare.inputs[1])

        section_compare.name = "Last Section Compare"

    def add_default_material_if_none_exists(self, context):
        material = bpy.data.materials.get("Section Override")
        if not material:
            material = bpy.data.materials.new("Section Override")
            material.use_nodes = True

        if context.scene.SectionProperties.should_section_selected_objects:
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


class BIM_OT_remove_section_plane(bpy.types.Operator):
    """Remove selected section plane. No effect if executed on a regular object"""

    bl_idname = "bim.remove_section_plane"
    bl_label = "Remove Temporary Section Cutaway"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object and bpy.data.node_groups.get("Section Override")

    def execute(self, context):
        name = context.active_object.name
        section_override = bpy.data.node_groups.get("Section Override")
        tex_coords = next(
            (
                n
                for n in section_override.nodes
                if isinstance(n, bpy.types.ShaderNodeTexCoord) and n.object.name == name
            ),
            None,
        )
        if tex_coords is not None:
            section_compare = tex_coords.outputs["Object"].links[0].to_node
            if section_compare.inputs[0].links:
                previous_section_compare = section_compare.inputs[0].links[0].from_node
                next_section_compare = section_compare.outputs[0].links[0].to_node
                section_override.links.new(previous_section_compare.outputs[0], next_section_compare.inputs[0])
                self.offset_previous_nodes(section_compare, offset_x=200)
            section_override.nodes.remove(section_compare)
            section_override.nodes.remove(tex_coords)
            bpy.data.objects.remove(context.active_object)

        return {"FINISHED"}

    def offset_previous_nodes(self, section_compare, offset_x=0, offset_y=0):
        if section_compare.inputs[0].links:
            previous_section_compare = section_compare.inputs[0].links[0].from_node
            previous_section_compare.location += Vector((offset_x, offset_y))
            if previous_section_compare.inputs[1].links:
                previous_section_compare.inputs[1].links[0].from_node.location += Vector((offset_x, offset_y))
            self.offset_previous_nodes(previous_section_compare, offset_x, offset_y)

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


class SectionProperties(PropertyGroup):
    should_section_selected_objects: BoolProperty(name="Section Selected Objects", default=False)
    section_plane_colour: FloatVectorProperty(
        name="Temporary Section Cutaway Colour",
        subtype="COLOR",
        default=(1, 0, 0),
        min=0.0,
        max=1.0,
        update=update_section_color,
    )


class BIM_PT_section_plane(bpy.types.Panel):
    bl_label = "Temporary Section Cutaways"
    bl_idname = "BIM_PT_section_plane"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Section Shader"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.scene.SectionProperties

        row = layout.row()
        row.prop(props, "should_section_selected_objects")

        row = layout.row()
        row.prop(props, "section_plane_colour")

        row = layout.row(align=True)
        row.operator("bim.add_section_plane")
        row.operator("bim.remove_section_plane")


def register():
    bpy.utils.register_class(SectionProperties)
    bpy.utils.register_class(BIM_OT_add_section_plane)
    bpy.utils.register_class(BIM_OT_remove_section_plane)
    bpy.utils.register_class(BIM_PT_section_plane)
    bpy.types.Scene.SectionProperties = bpy.props.PointerProperty(type=SectionProperties)


def unregister():
    bpy.utils.unregister_class(BIM_OT_add_section_plane)
    bpy.utils.unregister_class(BIM_OT_remove_section_plane)
    bpy.utils.unregister_class(BIM_PT_section_plane)
    bpy.utils.unregister_class(SectionProperties)
    del bpy.types.Scene.SectionProperties


if __name__ == "__main__":
    register()
