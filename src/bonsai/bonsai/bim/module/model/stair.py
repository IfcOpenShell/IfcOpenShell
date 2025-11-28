# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>, @Andrej730
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
import json
import bmesh
import math
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim import gizmo
from bonsai.bim.gizmo import GizmoPropConfig
from mathutils import Vector, Matrix
from bmesh.types import BMVert
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from typing import get_args


def regenerate_stair_mesh(obj: bpy.types.Object) -> None:
    props = tool.Model.get_stair_props(obj)
    props_kwargs = props.get_props_kwargs()
    vertices, edges, faces = tool.Model.generate_stair_2d_profile(**props_kwargs)

    bm = bmesh.new()
    bm.verts.index_update()
    bm.edges.index_update()

    new_verts = [bm.verts.new(v) for v in vertices]
    new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in edges]
    bm.verts.index_update()
    bm.edges.index_update()

    bmesh.ops.contextual_create(bm, geom=new_edges)

    bm.faces.ensure_lookup_table()
    faces = bm.faces
    extruded = bmesh.ops.extrude_face_region(bm, geom=faces)
    extrusion_vector = Vector((0, 1, 0)) * props_kwargs["width"]
    translate_verts = [v for v in extruded["geom"] if isinstance(v, BMVert)]
    bmesh.ops.translate(bm, vec=extrusion_vector, verts=translate_verts)

    assert isinstance(obj.data, bpy.types.Mesh)
    if obj.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()


def update_ifc_stair_props(obj: bpy.types.Object) -> None:
    """should be called after new geometry settled
    since it's going to update ifc representation
    """
    element = tool.Ifc.get_entity(obj)
    assert element
    props = tool.Model.get_stair_props(obj)
    ifc_file = tool.Ifc.get()

    if tool.Ifc.get_schema() != "IFC2X3" and element.is_a("IfcStairFlight"):
        element.PredefinedType = "STRAIGHT"
    number_of_risers = props.number_of_treads + 1
    # update IfcStairFlight properties (seems already deprecated but keep it for now)
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcStairFlight.htm

    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    riser_height = props.height / number_of_risers / si_conversion
    tread_length = props.tread_depth / si_conversion
    nosing_length = props.nosing_length / si_conversion

    if element.is_a("IfcStairFlight"):
        if tool.Ifc.get_schema() == "IFC2X3":
            element.NumberOfRiser = number_of_risers
        else:
            element.NumberOfRisers = number_of_risers

        element.NumberOfTreads = props.number_of_treads
        element.RiserHeight = riser_height
        element.TreadLength = tread_length

    # update pset with ifc properties
    pset_common = tool.Pset.get_element_pset(element, "Pset_StairFlightCommon")
    if not pset_common:
        pset_common = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="Pset_StairFlightCommon")

    ifcopenshell.api.pset.edit_pset(
        ifc_file,
        pset=pset_common,
        properties={
            "NumberOfRiser": number_of_risers,
            "NumberOfTreads": props.number_of_treads,
            "RiserHeight": riser_height,
            "TreadLength": tread_length,
            "NosingLength": nosing_length,
        },
    )

    # update related annotation objects
    def get_elements_from_product(product: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        elements = []
        for rel in product.ReferencedBy:
            if not rel.is_a("IfcRelAssignsToProduct"):
                continue
            elements.extend(rel.RelatedObjects)
        return elements

    stair_obj = obj
    for rel_element in get_elements_from_product(element):
        if not rel_element.is_a("IfcAnnotation") or rel_element.ObjectType != "STAIR_ARROW":
            continue
        if annotation_obj := tool.Ifc.get_object(rel_element):
            tool.Drawing.setup_annotation_object(annotation_obj, "STAIR_ARROW", stair_obj)


class BIM_OT_add_stair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_stair"
    bl_label = "Add Stair"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a stair.")
            return {"CANCELLED"}

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcStairFlight")
        obj = bpy.data.objects.new("StairFlight", mesh)
        obj.location = spawn_location

        element = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcStairFlight",
            should_add_representation=False,
        )
        if tool.Ifc.get_schema() != "IFC2X3":
            element.PredefinedType = "STRAIGHT"

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = obj
        tool.Blender.select_object(obj)
        bpy.ops.bim.add_stair()
        return {"FINISHED"}


# UI operators
class AddStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_stair"
    bl_label = "Add Stair"
    bl_description = "Add Bonsai parametric stair to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_stair_props(obj)
        ifc_file = tool.Ifc.get()

        tool.Blender.get_addon_preferences().default_parameters.stair.copy_to(props)

        # Use the special method that includes custom_tread_lock for IFC storage
        stair_data = props.get_props_kwargs_for_ifc_export(convert_to_project_units=True)
        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="BBIM_Stair")

        ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=pset,
            properties={"Data": tool.Ifc.get().createIfcText(json.dumps(stair_data))},
        )

        if obj.type == "EMPTY":
            obj = tool.Geometry.recreate_object_with_data(obj, data=bpy.data.meshes.new("temp"), is_global=True)
            tool.Blender.set_active_object(obj)

        regenerate_stair_mesh(obj)
        update_ifc_stair_props(obj)
        tool.Model.add_body_representation(obj)


class CancelEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_stair"
    bl_label = "Cancel Editing Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Stair", "Data"))
        props = tool.Model.get_stair_props(obj)
        # restore previous settings since editing was canceled
        props.set_props_kwargs_from_ifc_data(data)
        regenerate_stair_mesh(obj)

        props.is_editing = False

        return {"FINISHED"}


class FinishEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_stair"
    bl_label = "Finish Editing Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        props = tool.Model.get_stair_props(obj)

        # Use the special method that includes custom_tread_lock for IFC storage
        data = props.get_props_kwargs_for_ifc_export(convert_to_project_units=True)
        props.is_editing = False
        regenerate_stair_mesh(obj)
        tool.Model.add_body_representation(obj)

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        data = tool.Ifc.get().createIfcText(json.dumps(data))
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": data})

        # update IfcStairFlight properties
        update_ifc_stair_props(obj)
        return {"FINISHED"}


class EnableEditingStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_stair"
    bl_label = "Enable Editing Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Model.get_stair_props(obj)
        element = tool.Ifc.get_entity(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Stair", "Data"))
        # required since we could load pset from .ifc and BIMStairProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)
        props.is_editing = True
        return {"FINISHED"}


class RemoveStair(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_stair"
    bl_label = "Remove Stair"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Model.get_stair_props(obj)
        element = tool.Ifc.get_entity(obj)
        assert element
        props.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Stair")
        ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)

        return {"FINISHED"}


class ToggleStairTotalLengthLock(bpy.types.Operator):
    """Toggle the total length lock for stair editing"""

    bl_idname = "bim.toggle_stair_total_length_lock"
    bl_label = "Toggle Stair Total Length Lock"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        props.total_length_lock = not props.total_length_lock

        return {"FINISHED"}


class AdjustStairTreads(bpy.types.Operator):
    """Adjust the number of treads"""

    bl_idname = "bim.adjust_stair_treads"
    bl_label = "Adjust Stair Treads"
    bl_options = {"REGISTER", "UNDO"}

    increment: IntProperty(name="Increment", default=1)

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        new_value = props.number_of_treads + self.increment
        if new_value >= 1:
            props.number_of_treads = new_value

        return {"FINISHED"}


class CycleStairType(bpy.types.Operator):
    """Cycle through stair types. Shift+click to cycle in reverse."""

    bl_idname = "bim.cycle_stair_type"
    bl_label = "Cycle Stair Type"
    bl_options = {"REGISTER", "UNDO"}

    reverse: bpy.props.BoolProperty(name="Reverse", default=False, options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context, event):
        self.reverse = event.shift
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Model.get_stair_props(obj)
        stair_types = get_args(tool.Model.StairType)
        current_idx = stair_types.index(props.stair_type) if props.stair_type in stair_types else 0
        direction = -1 if self.reverse else 1
        props.stair_type = stair_types[(current_idx + direction) % len(stair_types)]

        return {"FINISHED"}


class GizmoStairEdition(bpy.types.GizmoGroup, gizmo.BaseParametricGizmoGroup):
    bl_idname = "OBJECT_GGT_bim_stair_edition"
    bl_label = "Stair Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    # Gizmo layout offsets (meters)
    GIZMO_X_OFFSET = 0.5  # Horizontal offset from stair end
    GIZMO_PLUS_X_OFFSET = 0.25  # Additional X offset for plus button
    GIZMO_MINUS_X_OFFSET = 0.5  # Additional X offset for minus button
    GIZMO_BUTTON_Z_OFFSET = 0.15  # Vertical offset for +/- buttons above lock
    GIZMO_CYCLE_Z_OFFSET = 0.5  # Vertical offset for cycle gizmo above lock

    enable_editing_operator = "bim.enable_editing_stair"
    finish_editing_operator = "bim.finish_editing_stair"
    cancel_editing_operator = "bim.cancel_editing_stair"

    gizmo_props = [
        GizmoPropConfig("width", (0, 1, 0)),
        GizmoPropConfig("height", (0, 0, 1)),
        GizmoPropConfig("tread_run", (1, 0, 0)),
        GizmoPropConfig("tread_depth", (0, 0, -1)),
        GizmoPropConfig("nosing_length", (-1, 0, 0)),
        GizmoPropConfig("nosing_depth", (0, 0, -1)),
        GizmoPropConfig("total_length_target", (1, 0, 0)),
        GizmoPropConfig("base_slab_depth", (0, 0, -1)),
        GizmoPropConfig("top_slab_depth", (0, 0, -1)),
    ]

    @classmethod
    def is_element_type(cls, element) -> bool:
        return tool.Blender.Modifier.is_stair(element)

    def get_props(self, obj):
        return tool.Model.get_stair_props(obj)

    def get_gizmo_prefs(self):
        prefs = tool.Blender.get_addon_preferences()
        return prefs.gizmos.stair

    def should_hide_gizmo(self, attr_name, props):
        """Stair-specific visibility rules for gizmos."""
        if not props.is_editing:
            return True
        # Hide concrete-specific gizmos for non-concrete stairs
        if attr_name in ("base_slab_depth", "top_slab_depth") and props.stair_type != "CONCRETE":
            return True
        # Hide tread_depth for generic stairs (has no tread geometry)
        if attr_name == "tread_depth" and props.stair_type == "GENERIC":
            return True
        # Hide nosing_depth when nosing_length is 0 or for Wood/Steel stair types
        if attr_name == "nosing_depth" and (props.nosing_length == 0.0 or props.stair_type == "WOOD/STEEL"):
            return True
        return False

    @staticmethod
    def _get_stair_total_run(props) -> float:
        """Calculate the total horizontal run of the stair."""
        return props.tread_run * props.number_of_treads

    @staticmethod
    def _get_first_riser_height(props) -> float:
        """Calculate the height of the first riser."""
        return props.height / (props.number_of_treads + 1)

    def get_gizmo_matrix_width(self, props):
        translation = Matrix.Translation(Vector((0, props.width, 0)))
        rotation = self.get_axis_rotation_matrix((0, 1, 0))
        return translation @ rotation

    def get_gizmo_matrix_width_top(self, props):
        """Position for the secondary width gizmo at the top of the stairs."""
        total_run = self._get_stair_total_run(props)
        translation = Matrix.Translation(Vector((total_run, props.width, props.height)))
        rotation = self.get_axis_rotation_matrix((0, 1, 0))
        return translation @ rotation

    def get_gizmo_matrix_height(self, props):
        total_run = self._get_stair_total_run(props)
        translation = Matrix.Translation(Vector((total_run, props.width / 2, props.height)))
        rotation = self.get_axis_rotation_matrix((0, 0, 1))
        return translation @ rotation

    def get_gizmo_matrix_tread_run(self, props):
        riser_height = self._get_first_riser_height(props)
        translation = Matrix.Translation(Vector((props.tread_run, props.width / 2, riser_height)))
        rotation = self.get_axis_rotation_matrix((1, 0, 0))
        return translation @ rotation

    def get_gizmo_matrix_tread_depth(self, props):
        riser_height = self._get_first_riser_height(props)
        translation = Matrix.Translation(
            Vector((props.tread_run / 2, props.width / 2, riser_height - props.tread_depth))
        )
        rotation = self.get_axis_rotation_matrix((0, 0, -1))
        return translation @ rotation

    def get_gizmo_matrix_nosing_length(self, props):
        riser_height = self._get_first_riser_height(props)
        translation = Matrix.Translation(Vector((-props.nosing_length, props.width / 2, riser_height)))
        rotation = self.get_axis_rotation_matrix((-1, 0, 0))
        return translation @ rotation

    def get_gizmo_matrix_nosing_depth(self, props):
        riser_height = self._get_first_riser_height(props)
        translation = Matrix.Translation(
            Vector((-props.nosing_length, props.width / 2, riser_height - props.nosing_depth))
        )
        rotation = self.get_axis_rotation_matrix((0, 0, -1))
        return translation @ rotation

    def get_gizmo_matrix_total_length_target(self, props):
        translation = Matrix.Translation(Vector((props.total_length_target, props.width / 2, props.height)))
        rotation = self.get_axis_rotation_matrix((1, 0, 0))
        return translation @ rotation

    def get_gizmo_matrix_base_slab_depth(self, props):
        translation = Matrix.Translation(Vector((0, props.width / 2, -props.base_slab_depth)))
        rotation = self.get_axis_rotation_matrix((0, 0, -1))
        return translation @ rotation

    def get_gizmo_matrix_top_slab_depth(self, props):
        total_run = self._get_stair_total_run(props)
        translation = Matrix.Translation(Vector((total_run, props.width / 2, props.height - props.top_slab_depth)))
        rotation = self.get_axis_rotation_matrix((0, 0, -1))
        return translation @ rotation

    def setup(self, context):
        self.setup_property_gizmos(context)
        self.setup_editing_gizmos(context)

        # Stair-specific gizmos
        prefs = tool.Blender.get_addon_preferences()
        highlight_color = prefs.decorator_color_selected[:3]

        # Secondary width gizmo at the top of the stairs (linked to same width property)
        self.gizmo_width_top = self.gizmos.new("BIM_GT_gizmo_arrow_2d")

        def make_width_get():
            def move_get():
                obj = bpy.context.active_object
                if not obj:
                    return 0.0
                props = self.get_props(obj)
                return props.width
            return move_get

        def make_width_set():
            def move_set(value):
                obj = bpy.context.active_object
                if not obj:
                    return
                props = self.get_props(obj)
                props.width = max(0.0, value)
            return move_set

        self.gizmo_width_top.move_get_cb = make_width_get()
        self.gizmo_width_top.move_set_cb = make_width_set()
        self.gizmo_width_top.axis = Vector((0, 1, 0))
        self.gizmo_width_top.local_axis = Vector((0, 1, 0))
        self.gizmo_width_top.invert_delta = False
        self.gizmo_width_top.delta_scale = 1.0
        self.gizmo_width_top.prop_name = "Width"
        self.gizmo_width_top.gizmo_group = self
        self.gizmo_width_top.color = self.COLOR_GREEN
        self.gizmo_width_top.color_highlight = highlight_color
        self.gizmo_width_top.alpha = 0.99
        self.gizmo_width_top.use_draw_modal = True
        self.gizmo_width_top.use_draw_scale = True

        # Total length lock gizmo
        self.lock_gizmo = self.gizmos.new("VIEW3D_GT_lock")
        self.lock_gizmo.use_draw_scale = False
        self.lock_gizmo.color = self.COLOR_BLUE
        self.lock_gizmo.color_highlight = highlight_color
        self.lock_gizmo.alpha = 0.8
        self.lock_gizmo.prop_path = "BIMStairProperties.total_length_lock"
        self.lock_gizmo.target_set_operator("bim.toggle_stair_total_length_lock")

        # Plus gizmo for increasing treads
        self.plus_gizmo = self.gizmos.new("VIEW3D_GT_plus")
        self.plus_gizmo.use_draw_scale = False
        self.plus_gizmo.color = self.COLOR_GREEN
        self.plus_gizmo.color_highlight = highlight_color
        self.plus_gizmo.alpha = 0.8
        op = self.plus_gizmo.target_set_operator("bim.adjust_stair_treads")
        op.increment = 1

        # Minus gizmo for decreasing treads
        self.minus_gizmo = self.gizmos.new("VIEW3D_GT_minus")
        self.minus_gizmo.use_draw_scale = False
        self.minus_gizmo.color = self.COLOR_RED
        self.minus_gizmo.color_highlight = highlight_color
        self.minus_gizmo.alpha = 0.8
        op = self.minus_gizmo.target_set_operator("bim.adjust_stair_treads")
        op.increment = -1

        # Cycle gizmo for stair type
        default_color = prefs.decorations_colour[:3]
        self.cycle_gizmo = self.gizmos.new("VIEW3D_GT_cycle")
        self.cycle_gizmo.use_draw_scale = False
        self.cycle_gizmo.color = default_color
        self.cycle_gizmo.color_highlight = highlight_color
        self.cycle_gizmo.alpha = 0.8
        self.cycle_gizmo.target_set_operator("bim.cycle_stair_type")

    def refresh(self, context):
        obj = context.active_object
        if not obj:
            return

        props = self.get_props(obj)
        mw = obj.matrix_world
        billboard_rot = gizmo.get_billboard_rotation(context)
        self.update_property_gizmos(mw, props)
        self.update_editing_gizmos(context, mw, props)
        self.update_width_top_gizmo(mw, props)
        self.update_lock_gizmo(mw, props, billboard_rot)
        self.update_tread_count_gizmos(mw, props, billboard_rot)
        self.update_cycle_gizmo(mw, props, billboard_rot)

    def update_width_top_gizmo(self, mw, props):
        """Update the secondary width gizmo at the top of the stairs."""
        gizmo_prefs = self.get_gizmo_prefs()
        # Use same visibility as the main width gizmo
        self.gizmo_width_top.hide = not props.is_editing or not getattr(gizmo_prefs, "width", True)

        if self.gizmo_width_top.hide:
            return

        self.gizmo_width_top.matrix_basis = mw @ self.get_gizmo_matrix_width_top(props)
        self.gizmo_width_top.matrix_offset = Matrix.Scale(self.ARROW_SCALE, 4)

    def update_lock_gizmo(self, mw, props, billboard_rot):
        gizmo_prefs = self.get_gizmo_prefs()
        self.lock_gizmo.hide = not props.is_editing or not gizmo_prefs.lock

        if self.lock_gizmo.hide:
            return

        self.lock_gizmo.color = self.COLOR_RED if props.total_length_lock else self.COLOR_GREEN

        total_run = self._get_stair_total_run(props)
        lock_x = total_run + props.tread_run + self.GIZMO_X_OFFSET
        local_transform = (
            Matrix.Translation(Vector((lock_x, props.width / 2, props.height)))
            @ billboard_rot
            @ Matrix.Scale(0.2, 4)
        )
        self.lock_gizmo.matrix_basis = mw @ local_transform

    def update_tread_count_gizmos(self, mw, props, billboard_rot):
        gizmo_prefs = self.get_gizmo_prefs()

        self.plus_gizmo.hide = not props.is_editing or not gizmo_prefs.plus
        self.minus_gizmo.hide = not props.is_editing or props.number_of_treads <= 1 or not gizmo_prefs.minus

        if self.plus_gizmo.hide and self.minus_gizmo.hide:
            return

        total_run = self._get_stair_total_run(props)
        base_x = total_run + props.tread_run + self.GIZMO_X_OFFSET

        if not self.plus_gizmo.hide:
            plus_local_transform = (
                Matrix.Translation(Vector((
                    base_x + self.GIZMO_PLUS_X_OFFSET,
                    props.width / 2,
                    props.height + self.GIZMO_BUTTON_Z_OFFSET
                )))
                @ billboard_rot
                @ Matrix.Scale(0.2, 4)
            )
            self.plus_gizmo.matrix_basis = mw @ plus_local_transform

        if not self.minus_gizmo.hide:
            minus_local_transform = (
                Matrix.Translation(Vector((
                    base_x + self.GIZMO_MINUS_X_OFFSET,
                    props.width / 2,
                    props.height + self.GIZMO_BUTTON_Z_OFFSET
                )))
                @ billboard_rot
                @ Matrix.Scale(0.2, 4)
            )
            self.minus_gizmo.matrix_basis = mw @ minus_local_transform

    def update_cycle_gizmo(self, mw, props, billboard_rot):
        gizmo_prefs = self.get_gizmo_prefs()
        self.cycle_gizmo.hide = not props.is_editing or not gizmo_prefs.cycle

        if self.cycle_gizmo.hide:
            return

        total_run = self._get_stair_total_run(props)
        cycle_x = total_run + props.tread_run + self.GIZMO_X_OFFSET
        local_transform = (
            Matrix.Translation(Vector((
                cycle_x,
                props.width / 2,
                props.height + self.GIZMO_CYCLE_Z_OFFSET
            )))
            @ billboard_rot
            @ Matrix.Scale(0.2, 4)
        )
        self.cycle_gizmo.matrix_basis = mw @ local_transform

    def draw_prepare(self, context):
        """Called before drawing - updates gizmos to face camera."""
        # Call base class implementation
        super().draw_prepare(context)

        # Also update the secondary width gizmo to face camera
        if hasattr(self, "gizmo_width_top") and not self.gizmo_width_top.hide:
            self.gizmo_width_top.draw_prepare(context)
