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
from bpy.types import Operator, PropertyGroup, Panel
from mathutils import Vector, Matrix, Euler
from math import radians
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


class SectionCutawayManager:
    @staticmethod
    def get_section_tree():
        return bpy.data.node_groups.get("Section Override")

    @staticmethod
    def get_sections_map():
        section_tree = SectionCutawayManager.get_section_tree()
        return {n: n.object for n in section_tree.nodes if isinstance(n, bpy.types.ShaderNodeTexCoord)}

    @staticmethod
    def purge_all_section_data():
        section_override_mat = bpy.data.materials.get("Section Override")
        if section_override_mat:
            bpy.data.materials.remove(section_override_mat)
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
        bpy.data.node_groups.remove(SectionCutawayManager.get_section_tree())
        bpy.data.node_groups.remove(bpy.data.node_groups.get("Section Compare"))

    @staticmethod
    def clean():
        sections_map = SectionCutawayManager.get_sections_map()
        sections_map_iterator = list(sections_map.items())
        for tex_coord_node, section_obj in sections_map_iterator:
            if section_obj is None or section_obj.users == 1:
                SectionCutawayManager.unplug(tex_coord_node)
                sections_map.pop(tex_coord_node)
        if not any(o for o in sections_map.values() if o.users > 1):
            SectionCutawayManager.purge_all_section_data()

    @staticmethod
    def unplug(tex_coords):
        section_tree = SectionCutawayManager.get_section_tree()
        section_compare = tex_coords.outputs["Object"].links[0].to_node
        if section_compare.inputs[0].links:
            previous_section_compare = section_compare.inputs[0].links[0].from_node
            next_section_compare = section_compare.outputs[0].links[0].to_node
            section_tree.links.new(previous_section_compare.outputs[0], next_section_compare.inputs[0])
            SectionCutawayManager.offset_previous_nodes(section_compare, offset_x=200)
        section_tree.nodes.remove(section_compare)
        section_tree.nodes.remove(tex_coords)

    @staticmethod
    def offset_previous_nodes(section_compare, offset_x=0, offset_y=0):
        if section_compare.inputs[0].links:
            previous_section_compare = section_compare.inputs[0].links[0].from_node
            previous_section_compare.location += Vector((offset_x, offset_y))
            if previous_section_compare.inputs[1].links:
                previous_section_compare.inputs[1].links[0].from_node.location += Vector((offset_x, offset_y))
            SectionCutawayManager.offset_previous_nodes(previous_section_compare, offset_x, offset_y)

    @staticmethod
    def override_materials():
        override = SectionCutawayManager.get_section_tree()
        for material in bpy.data.materials:
            material.use_nodes = True
            if material.node_tree.nodes.get(override.name):
                continue
            material.blend_method = "HASHED"
            material.shadow_method = "HASHED"
            material_output = next((n for n in material.node_tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
            if material_output is None:
                continue
            from_socket = material_output.inputs[0].links[0].from_socket
            section_override = material.node_tree.nodes.new(type="ShaderNodeGroup")
            section_override.name = "Section Override"
            section_override.node_tree = override
            material.node_tree.links.new(from_socket, section_override.inputs[0])
            material.node_tree.links.new(section_override.outputs[0], material_output.inputs[0])

    @staticmethod
    def create_section_obj(from_obj, scene):
        section = bpy.data.objects.new("Section", None)
        section.empty_display_type = "SINGLE_ARROW"
        section.empty_display_size = 5
        section.show_in_front = True
        if from_obj and from_obj.select_get() and isinstance(from_obj.data, bpy.types.Camera):
            section.matrix_world = from_obj.matrix_world @ Euler((radians(180.0), 0.0, 0.0), "XYZ").to_matrix().to_4x4()
        else:
            section.rotation_euler = Euler((radians(180.0), 0.0, 0.0), "XYZ")
            section.location = scene.cursor.location
        collection = bpy.data.collections.get("Sections")
        if not collection:
            collection = bpy.data.collections.new("Sections")
            scene.collection.children.link(collection)
        collection.objects.link(section)
        return section

    @classmethod
    def add_section_plane(cls, context):
        obj = cls.create_section_obj(context.active_object, context.scene)
        if cls.get_section_tree() is not None:
            cls.append_obj_to_section_override_node(obj)
        else:
            cls.create_section_compare_node()
            cls.create_section_override_node(obj, context)
        cls.add_default_material_if_none_exists(context)
        cls.override_materials()

    @classmethod
    def remove_all_section_planes(cls):
        objs = [o for o in cls.get_sections_map().values() if o is not None]
        cls.remove_section_planes(objs)

    @classmethod
    def remove_section_planes(cls, objects):
        sections_map = cls.get_sections_map()
        for obj in objects:
            tex_coords = next((n for n in sections_map if sections_map[n] == obj), None)
            if tex_coords is not None:
                cls.unplug(tex_coords)
                sections_map.pop(tex_coords)
                bpy.data.objects.remove(obj)

    @staticmethod
    def create_section_compare_node():
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

    @staticmethod
    def create_section_override_node(obj, context):
        group = bpy.data.node_groups.new("Section Override", type="ShaderNodeTree")
        links = group.links
        nodes = group.nodes

        group_input = nodes.new(type="NodeGroupInput")
        group_output = nodes.new(type="NodeGroupOutput")
        group_output.location = 600, 250

        hide_mix = group.nodes.new(type="ShaderNodeMixShader")
        hide_mix.name = "Hide Mix"
        hide_mix.inputs[0].default_value = 0
        hide_mix.location = group_output.location - Vector((200, 0))

        backfacing_mix = nodes.new(type="ShaderNodeMixShader")
        backfacing_mix.location = group_output.location - Vector((600, 350))

        backfacing = nodes.new(type="ShaderNodeNewGeometry")
        backfacing.location = backfacing_mix.location + Vector((-400, 200))
        group_input.location = backfacing_mix.location - Vector((400, 50))

        emission = nodes.new(type="ShaderNodeEmission")
        emission.inputs[0].default_value = list(context.scene.SectionProperties.section_plane_colour) + [1]
        emission.location = backfacing_mix.location - Vector((400, 150))

        transparent = nodes.new(type="ShaderNodeBsdfTransparent")
        transparent.location = group_output.location - Vector((600, 100))

        section_mix = group.nodes.new(type="ShaderNodeMixShader")
        section_mix.name = "Section Mix"
        section_mix.inputs[0].default_value = 1  # Directly pass input shader when there is no cutaway
        section_mix.location = group_output.location - Vector((400, 0))

        cut_obj = nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        cut_obj.location = group_output.location - Vector((1000, 150))

        section_compare = nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")
        section_compare.name = "Last Section Compare"
        section_compare.location = group_output.location - Vector((800, 0))

        links.new(cut_obj.outputs["Object"], section_compare.inputs[1])
        links.new(backfacing.outputs["Backfacing"], backfacing_mix.inputs[0])
        links.new(group_input.outputs[""], backfacing_mix.inputs[1])
        links.new(emission.outputs["Emission"], backfacing_mix.inputs[2])
        links.new(section_compare.outputs[0], section_mix.inputs[0])
        links.new(transparent.outputs[0], section_mix.inputs[1])
        links.new(backfacing_mix.outputs[0], section_mix.inputs[2])
        links.new(section_mix.outputs[0], hide_mix.inputs[1])
        links.new(group_input.outputs["Shader"], hide_mix.inputs[2])
        links.new(hide_mix.outputs[0], group_output.inputs[""])

    @staticmethod
    def append_obj_to_section_override_node(obj):
        group = SectionCutawayManager.get_section_tree()
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

    @staticmethod
    def add_default_material_if_none_exists(context):
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


class BIM_OT_section_plane_refresh(Operator):
    bl_idname = "bim.section_plane_refresh"
    bl_label = "Refresh Section Cutaway Shader"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        update_visibility(None, context)
        SectionCutawayManager.add_default_material_if_none_exists(context)
        SectionCutawayManager.clean()
        return {"FINISHED"}


class BIM_OT_section_plane_add(Operator):
    """Add a temporary empty object as a section cutaway. Cull all geometry rendering below the empty's local Z axis"""

    bl_idname = "bim.section_plane_add"
    bl_label = "Add Temporary Section Cutaway"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        SectionCutawayManager.add_section_plane(context)
        SectionCutawayManager.clean()
        return {"FINISHED"}


class BIM_OT_section_plane_remove(Operator):
    bl_idname = "bim.section_plane_remove"
    bl_label = "Remove Temporary Section Cutaway"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove section planes. No effect if executed on a regular object"
    remove_all: BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return SectionCutawayManager.get_section_tree() is not None

    def execute(self, context):
        if self.remove_all:
            SectionCutawayManager.remove_all_section_planes()
        else:
            SectionCutawayManager.remove_section_planes(context.selected_objects)
        SectionCutawayManager.clean()
        return {"FINISHED"}


def update_visibility(self, context):
    tree = SectionCutawayManager.get_section_tree()
    if tree:
        node = tree.nodes.get("Hide Mix")
        if node:
            node.inputs[0].default_value = int(context.scene.SectionProperties.hide)


def update_section_color(self, context):
    section_node_group = SectionCutawayManager.get_section_tree()
    if section_node_group is None:
        return
    try:
        emission_node = next(n for n in section_node_group.nodes if isinstance(n, bpy.types.ShaderNodeEmission))
        emission_node.inputs[0].default_value = list(self.section_plane_colour) + [1]
    except StopIteration:
        pass


class SectionProperties(PropertyGroup):
    should_section_selected_objects: BoolProperty(name="Section Selected Objects", default=False)
    hide: BoolProperty(default=False, name="Toggle", update=update_visibility)
    section_plane_colour: FloatVectorProperty(
        name="Temporary Section Cutaway Colour",
        subtype="COLOR",
        default=(1, 0, 0),
        min=0.0,
        max=1.0,
        update=update_section_color,
    )


class BIM_PT_section_plane(Panel):
    bl_label = "Temporary Section Cutaways"
    bl_idname = "BIM_PT_section_plane"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Section Shader"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.scene.SectionProperties

        layout.prop(props, "should_section_selected_objects", text="Only Selected", icon="RESTRICT_SELECT_OFF")
        layout.prop(props, "section_plane_colour", text="Section Color")
        layout.prop(props, "hide", icon="HIDE_ON" if props.hide else "HIDE_OFF")

        layout.operator("bim.section_plane_refresh", text="Refresh", icon="FILE_REFRESH")
        layout.operator("bim.section_plane_add", text="Add Section Cutaway", icon="ADD")
        layout.operator("bim.section_plane_remove", text="Remove Selected Sections", icon="REMOVE").remove_all = False
        layout.operator("bim.section_plane_remove", text="Remove All Sections", icon="TRASH").remove_all = True


def register():
    bpy.utils.register_class(SectionProperties)
    bpy.utils.register_class(BIM_OT_section_plane_add)
    bpy.utils.register_class(BIM_OT_section_plane_remove)
    bpy.utils.register_class(BIM_PT_section_plane)
    bpy.utils.register_class(BIM_OT_section_plane_refresh)
    bpy.types.Scene.SectionProperties = PointerProperty(type=SectionProperties)


def unregister():
    bpy.utils.unregister_class(BIM_OT_section_plane_add)
    bpy.utils.unregister_class(BIM_OT_section_plane_remove)
    bpy.utils.unregister_class(BIM_PT_section_plane)
    bpy.utils.unregister_class(SectionProperties)
    bpy.utils.unregister_class(BIM_OT_section_plane_refresh)
    del bpy.types.Scene.SectionProperties


if __name__ == "__main__":
    register()
