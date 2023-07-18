# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import blenderbim.tool as tool
from mathutils import Vector
from pathlib import Path


VIEWPORT_ATTRIBUTES = [
    "view_matrix",
    "view_distance",
    "view_perspective",
    "use_box_clip",
    "use_clip_planes",
    "is_perspective",
    "show_sync_view",
    "clip_planes",
]


class Blender:
    OBJECT_TYPES_THAT_SUPPORT_EDIT_MODE = ("MESH", "CURVE", "SURFACE", "META", "FONT", "LATTICE", "ARMATURE")
    OBJECT_TYPES_THAT_SUPPORT_EDIT_GPENCIL_MODE = ("GPENCIL",)

    @classmethod
    def set_active_object(cls, obj):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    @classmethod
    def is_tab(cls, context, tab):
        if not len(context.screen.BIMAreaProperties):
            return None
        if context.area.spaces.active.search_filter:
            return True
        screen_areas = context.screen.areas[:]
        current_area = context.area
        # If the user is using the properties panel "Display Filter" search it
        # will create a new area that's not present in context.screen.areas for
        # all property tabs except for the active property tab.
        if current_area not in screen_areas:
            current_area = next(a for a in context.screen.areas if a.x == current_area.x and a.y == current_area.y)
        area_index = screen_areas.index(current_area)
        return context.screen.BIMAreaProperties[area_index].tab == tab

    @classmethod
    def is_default_scene(cls):
        if len(bpy.context.scene.objects) != 3:
            return False
        if {obj.type for obj in bpy.context.scene.objects} == {"MESH", "LIGHT", "CAMERA"}:
            return True
        return False

    @classmethod
    def get_name(cls, ifc_class, name):
        if not bpy.data.objects.get(f"{ifc_class}/{name}"):
            return name
        i = 2
        while bpy.data.objects.get(f"{ifc_class}/{name} {i}"):
            i += 1
        return f"{name} {i}"

    @classmethod
    def get_selected_objects(cls):
        if bpy.context.selected_objects:
            return set(bpy.context.selected_objects + [bpy.context.active_object])
        return set([bpy.context.active_object])

    @classmethod
    def create_ifc_object(cls, ifc_class: str, name: str = None, data=None) -> bpy.types.Object:
        name = name or "My " + ifc_class
        name = cls.get_name(ifc_class, name)
        obj = bpy.data.objects.new(name, data)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=ifc_class)
        return obj

    @classmethod
    def get_obj_ifc_definition_id(cls, obj=None, obj_type=None):
        if obj_type == "Object":
            return bpy.data.objects.get(obj).BIMObjectProperties.ifc_definition_id
        elif obj_type == "Material":
            return bpy.data.materials.get(obj).BIMObjectProperties.ifc_definition_id
        elif obj_type == "MaterialSet":
            return ifcopenshell.util.element.get_material(
                tool.Ifc.get_entity(bpy.data.objects.get(obj)), should_skip_usage=True
            ).id()
        elif obj_type == "MaterialSetItem":
            return bpy.data.objects.get(obj).BIMObjectMaterialProperties.active_material_set_item_id
        elif obj_type == "Task":
            return bpy.context.scene.BIMTaskTreeProperties.tasks[
                bpy.context.scene.BIMWorkScheduleProperties.active_task_index
            ].ifc_definition_id
        elif obj_type == "Cost":
            return bpy.context.scene.BIMCostProperties.cost_items[
                bpy.context.scene.BIMCostProperties.active_cost_item_index
            ].ifc_definition_id
        elif obj_type == "Resource":
            return bpy.context.scene.BIMResourceTreeProperties.resources[
                bpy.context.scene.BIMResourceProperties.active_resource_index
            ].ifc_definition_id
        elif obj_type == "Profile":
            return bpy.context.scene.BIMProfileProperties.profiles[
                bpy.context.scene.BIMProfileProperties.active_profile_index
            ].ifc_definition_id
        elif obj_type == "WorkSchedule":
            return bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id

    @classmethod
    def is_ifc_object(cls, obj):
        return bool(obj.BIMObjectProperties.ifc_definition_id)

    @classmethod
    def is_ifc_class_active(cls, ifc_class):
        if bpy.context.active_object:
            if cls.is_ifc_object(bpy.context.active_object):
                return tool.Ifc.get_entity(bpy.context.active_object).is_a(ifc_class)
            return False
        return False

    @classmethod
    def show_error_message(cls, text):
        """useful for showing error messages outside blender operators"""

        def error(self, context):
            self.layout.label(text=text)

        bpy.context.window_manager.popup_menu(error, title="Error", icon="ERROR")

    @classmethod
    def get_blender_prop_default_value(cls, props, prop_name):
        prop_bl_rna = props.bl_rna.properties[prop_name]
        if getattr(prop_bl_rna, "array_length", 0) > 0:
            prop_value = prop_bl_rna.default_array
        else:
            prop_value = prop_bl_rna.default
        return prop_value

    @classmethod
    def get_viewport_context(cls):
        """Get viewport area context for context overriding.

        Useful for calling operators outside viewport context.

        It's a bit naive since it's just taking the first available `VIEW_3D` area
        when in real life you can have a couple of those but should work for the most cases.
        """
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        context_override = {"area": area}
        return context_override

    @classmethod
    def get_viewport_position(cls):
        region_3d = cls.get_viewport_context()["area"].spaces[0].region_3d
        copy_if_possible = lambda x: x.copy() if hasattr(x, "copy") else x
        viewport_data = {attr: copy_if_possible(getattr(region_3d, attr)) for attr in VIEWPORT_ATTRIBUTES}
        return viewport_data

    @classmethod
    def set_viewport_position(cls, data):
        region_3d = cls.get_viewport_context()["area"].spaces[0].region_3d
        for attr in VIEWPORT_ATTRIBUTES:
            setattr(region_3d, attr, data[attr])

    @classmethod
    def get_shader_editor_context(cls):
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == "NODE_EDITOR":
                    for space in area.spaces:
                        if space.tree_type == "ShaderNodeTree":
                            context_override = {"area": area, "space": space, "screen": screen}
                            return context_override

    @classmethod
    def copy_node_graph(cls, material_to, material_from):
        temp_override = cls.get_shader_editor_context()
        shader_editor = temp_override["space"]

        # remove all nodes from the current material
        for n in material_to.node_tree.nodes[:]:
            material_to.node_tree.nodes.remove(n)

        previous_pin_setting = shader_editor.pin
        # required to be able to change material to something else
        shader_editor.pin = True
        shader_editor.node_tree = material_from.node_tree

        # select all nodes and copy them to clipboard
        for node in material_from.node_tree.nodes:
            node.select = True
        bpy.ops.node.clipboard_copy(temp_override)

        # back to original material
        shader_editor.node_tree = material_to.node_tree
        bpy.ops.node.clipboard_paste(temp_override, offset=(0, 0))

        # restore shader editor settings
        shader_editor.pin = previous_pin_setting

    @classmethod
    def get_material_node(cls, blender_material, node_type, kwargs={}):
        """returns first node from the `blender_material` shader graph with type `node_type`"""
        if not blender_material.use_nodes:
            return
        nodes = blender_material.node_tree.nodes
        for node in nodes:
            if node.type == node_type and all(getattr(node, a) == kwargs[a] for a in kwargs):
                return node

    @classmethod
    def update_screen(cls):
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

    @classmethod
    def update_viewport(cls):
        tool.Blender.get_viewport_context()["area"].tag_redraw()

    @classmethod
    def ensure_unique_name(cls, name, objects, iteration=0):
        """returns a unique name for the given name and dictionary of objects
        blender style name with .001, .002, etc. suffix
        """
        current_iteration = name if not iteration else f"{name}.{iteration:03d}"
        if current_iteration not in objects:
            return current_iteration
        return cls.ensure_unique_name(name, objects, iteration + 1)

    @classmethod
    def blender_path_to_posix(cls, blender_path):
        """Process blender path to be saved as posix.

        If path is relative the method will keep it relative to .ifc file
        """
        if blender_path.startswith("//"):  # detect relative blender path
            ifc_path = Path(tool.Ifc.get_path())
            abs_path = Path(bpy.path.abspath(blender_path))
            path = abs_path.relative_to(ifc_path.parent)
        else:
            path = Path(blender_path)

        return path.as_posix()

    @classmethod
    def get_default_selection_keypmap(cls):
        """keymap to replicate default blender selection behaviour with click and box selection"""
        # code below comes from blender_default.py which is part of default blender scripts licensed under GPL v2
        # https://github.com/blender/blender/blob/master/release/scripts/presets/keyconfig/keymap_data/blender_default.py
        # the code is the data from evaluating km_3d_view_tool_select() and km_3d_view_tool_select_box()
        #
        # You can run the snippet below in Blender console
        # to regenerate those keybindings in case of errors in the future
        # ```
        # import os
        # version = ".".join(bpy.app.version_string.split(".")[:2])
        # fl = os.path.join(os.getcwd(), version, "scripts/presets/keyconfig/keymap_data/blender_default.py")
        # def_keymap = bpy.utils.execfile(fl)
        # params = def_keymap.Params
        # box_keymap = def_keymap.km_3d_view_tool_select_box(def_keymap.Params(), fallback=None)[2]["items"]
        # click_keymap = def_keymap.km_3d_view_tool_select(def_keymap.Params(select_mouse="LEFTMOUSE"), fallback=None)[2]["items"]
        # ```
        # https://docs.blender.org/api/current/bpy.types.KeyMapItems.html
        keymap = (
            # box selection keymap
            ("view3d.select_box", {"type": "LEFTMOUSE", "value": "CLICK_DRAG"}, None),
            (
                "view3d.select_box",
                {"type": "LEFTMOUSE", "value": "CLICK_DRAG", "shift": True},
                {"properties": [("mode", "ADD")]},
            ),
            (
                "view3d.select_box",
                {"type": "LEFTMOUSE", "value": "CLICK_DRAG", "ctrl": True},
                {"properties": [("mode", "SUB")]},
            ),
            (
                "view3d.select_box",
                {"type": "LEFTMOUSE", "value": "CLICK_DRAG", "shift": True, "ctrl": True},
                {"properties": [("mode", "AND")]},
            ),
            # left-click selection keymap
            ("view3d.select", {"type": "LEFTMOUSE", "value": "PRESS"}, {"properties": [("deselect_all", True)]}),
            (
                "view3d.select",
                {"type": "LEFTMOUSE", "value": "PRESS", "shift": True},
                {"properties": [("toggle", True)]},
            ),
        )
        return keymap

    @classmethod
    def add_layout_hotkey_operator(cls, tool_name, layout, text, hotkey, description):
        modifiers = {
            "A": "EVENT_ALT",
            "S": "EVENT_SHIFT",
        }
        modifier, key = hotkey.split("_")

        row = layout.row(align=True)
        row.label(text="", icon=modifiers[modifier])
        row.label(text="", icon=f"EVENT_{key}")

        op = row.operator(f"bim.{tool_name}_hotkey", text=text)
        op.hotkey = hotkey
        op.description = description
        return op, row

    @classmethod
    def get_object_bounding_box(cls, obj):
        """Returns dict with local min and max x, y, z values for the object.

        Careful with using this method for objects in EDIT mode because
        it requires all EDIT mode changes to be applied.
        """
        bound_box = obj.bound_box
        bbox_dict = {
            "min_x": bound_box[0][0],
            "max_x": bound_box[6][0],
            "min_y": bound_box[0][1],
            "max_y": bound_box[6][1],
            "min_z": bound_box[0][2],
            "max_z": bound_box[6][2],
            "center": (Vector(bound_box[6]) + Vector(bound_box[0])) / 2,
        }
        return bbox_dict

    @classmethod
    def select_and_activate_single_object(cls, context, active_object):
        for obj in context.selected_objects:
            obj.select_set(False)
        context.view_layer.objects.active = active_object
        active_object.select_set(True)

    @classmethod
    def set_objects_selection(cls, context, active_object, selected_objects):
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = active_object
        active_object.select_set(True)

    @classmethod
    def enum_property_has_valid_index(cls, props, prop_name, enum_items):
        """method created for readibility and to avoid console warnings like
        `pyrna_enum_to_py: current value '17' matches no enum in 'BIMModelProperties', '', 'relating_type_id'`
        """
        current_value_index = props.get(prop_name, None)
        # assuming the default value is fine
        if current_value_index is None:
            return True
        return current_value_index < len(enum_items)

    @classmethod
    def append_data_block(cls, filepath, data_block_type, name, link=False, relative=False):
        if Path(filepath) == Path(bpy.data.filepath):
            data_block = getattr(bpy.data, data_block_type).get(name, None)
            if not data_block:
                return {"data_block": None, "msg": f"Data-block {data_block_type}/{name} not found in {filepath}"}
            return {"data_block": data_block.copy(), "msg": ""}

        with bpy.data.libraries.load(filepath, link=link, relative=relative) as (data_from, data_to):
            if name not in getattr(data_from, data_block_type):
                return {"data_block": None, "msg": f"Data-block {data_block_type}/{name} not found in {filepath}"}
            getattr(data_to, data_block_type).append(name)
        return {"data_block": getattr(data_to, data_block_type)[0], "msg": ""}

    ## BMESH UTILS ##
    @classmethod
    def apply_bmesh(cls, mesh, bm, obj=None):
        """`obj` argument is not optional if you plan to update mesh in EDIT mode
        and it's possible that that mesh object won't be currenly active."""
        import bmesh

        if mesh.is_editmode:
            # better to be safe because otherwise mesh won't be updated
            # and you won't get any errors
            if not bm.is_wrapped or hash(bmesh.from_edit_mesh(mesh)) != hash(bm):
                raise Exception(
                    f"{bm} is not edit mesh for {mesh}. "
                    "For applying bmesh in edit mode bmesh should be acquired with `bmesh.from_edit_mesh(me)`."
                )
            bmesh.update_edit_mesh(mesh)
            if not obj:
                if not bpy.context.active_object or bpy.context.active_object.data != mesh:
                    raise Exception(
                        "Error applying bmesh in EDIT object - object is "
                        "not provided and can't be acquired from the context. "
                    )
                obj = bpy.context.active_object
            obj.update_from_editmode()
        else:
            bm.to_mesh(mesh)
            # only freeing bmesh if object is in OBJECT mode
            # because if it's in EDIT mode
            # freeing mesh will result in dead bmeshes from `bmesh.from_edit_mesh(mesh)`
            # until you restart EDIT mode
            # which may result in errors when some other scripts will try to get bmesh
            bm.free()

        mesh.update()

    @classmethod
    def get_bmesh_for_mesh(cls, mesh, clean=False):
        import bmesh

        if mesh.is_editmode:
            bm = bmesh.from_edit_mesh(mesh)
            if clean:
                bm.clear()
        else:
            bm = bmesh.new()
            if not clean:
                bm.from_mesh(mesh)
        return bm

    @classmethod
    def bmesh_join(cls, bm_a, bm_b, callback=None):
        """Join two meshes into single one, store it in `bm_a`"""
        import bmesh

        new_verts = [bm_a.verts.new(v.co) for v in bm_b.verts]
        new_edges = [bm_a.edges.new([new_verts[v.index] for v in edge.verts]) for edge in bm_b.edges]
        new_faces = [bm_a.faces.new([new_verts[v.index] for v in face.verts]) for face in bm_b.faces]
        bmesh.ops.recalc_face_normals(bm_a, faces=bm_a.faces[:])

        if callback:
            callback(bm_a, new_verts, new_edges, new_faces)

        return bm_a

    @classmethod
    def toggle_edit_mode(cls, context):
        ao = context.active_object
        if not ao:
            return {"CANCELLED"}
        if ao.type in cls.OBJECT_TYPES_THAT_SUPPORT_EDIT_MODE:
            return bpy.ops.object.mode_set(mode="EDIT", toggle=True)
        elif ao.type in cls.OBJECT_TYPES_THAT_SUPPORT_EDIT_GPENCIL_MODE:
            return bpy.ops.object.mode_set(mode="EDIT_GPENCIL", toggle=True)
        else:
            return {"CANCELLED"}

    class Modifier:
        @classmethod
        def is_railing(cls, element):
            return tool.Pset.get_element_pset(element, "BBIM_Railing")

        @classmethod
        def is_roof(cls, element):
            return tool.Pset.get_element_pset(element, "BBIM_Roof")

        @classmethod
        def is_window(cls, element):
            return tool.Pset.get_element_pset(element, "BBIM_Window")

        @classmethod
        def is_door(cls, element):
            return tool.Pset.get_element_pset(element, "BBIM_Door")

        @classmethod
        def is_stair(cls, element):
            return tool.Pset.get_element_pset(element, "BBIM_Stair")

        @classmethod
        def is_editing_parameters(cls, obj):
            return obj.BIMRailingProperties.is_editing or obj.BIMRoofProperties.is_editing

        @classmethod
        def is_modifier_with_non_editable_path(cls, element):
            return cls.is_stair(element) or cls.is_door(element) or cls.is_window(element)
