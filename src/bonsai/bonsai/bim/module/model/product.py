# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
#
# pyright: reportUnnecessaryTypeIgnoreComment=error

import bpy
import bmesh
import mathutils
import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.geometry
import ifcopenshell.util.system
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.type
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.core.aggregate
import bonsai.core.type
import bonsai.core.root
import bonsai.core.geometry
import bonsai.core.spatial
from . import wall, slab, profile, mep
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import get_enum_items
from bonsai.bim.module.model.data import AuthoringData
from bonsai.bim.module.model.polyline import PolylineOperator
from bonsai.bim.module.model.decorator import PolylineDecorator, ProductDecorator
from mathutils import Vector, Matrix
from bpy_extras.object_utils import AddObjectHelper
import json
from typing import Any, Union, Optional, Literal, get_args, assert_never, TYPE_CHECKING


class AddEmptyType(bpy.types.Operator, AddObjectHelper):
    bl_idname = "bim.add_empty_type"
    bl_label = "Add Empty Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.data.objects.new("TYPEX", None)
        context.scene.collection.objects.link(obj)
        context.scene.BIMRootProperties.ifc_product = "IfcElementType"
        tool.Blender.select_and_activate_single_object(context, obj)
        return {"FINISHED"}


class AddDefaultType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_default_type"
    bl_label = "Create"
    bl_description = "Create Construction Type"
    bl_options = {"REGISTER", "UNDO"}
    ifc_element_type: bpy.props.StringProperty()

    def _execute(self, context):
        props = context.scene.BIMRootProperties
        props.ifc_product = "IfcElementType"
        props.ifc_class = self.ifc_element_type
        if self.ifc_element_type == "IfcWallType":
            if tool.Ifc.get().schema == "IFC2X3":
                props.ifc_predefined_type = "STANDARD"
            else:
                props.ifc_predefined_type = "SOLIDWALL"
            props.representation_template = "LAYERSET_AXIS2"
        elif self.ifc_element_type == "IfcSlabType":
            props.ifc_predefined_type = "FLOOR"
            props.representation_template = "LAYERSET_AXIS3"
        elif self.ifc_element_type == "IfcDoorType":
            props.ifc_predefined_type = "DOOR"
            props.representation_template = "DOOR"
        elif self.ifc_element_type == "IfcWindowType":
            props.ifc_predefined_type = "WINDOW"
            props.representation_template = "WINDOW"
        elif self.ifc_element_type == "IfcColumnType":
            props.ifc_predefined_type = "COLUMN"
            props.representation_template = "PROFILESET"
        elif self.ifc_element_type == "IfcBeamType":
            props.ifc_predefined_type = "BEAM"
            props.representation_template = "PROFILESET"
        elif self.ifc_element_type == "IfcDuctSegmentType":
            props.ifc_predefined_type = "RIGIDSEGMENT"
            props.representation_template = "FLOW_SEGMENT_RECTANGULAR"
        elif self.ifc_element_type == "IfcPipeSegmentType":
            props.ifc_predefined_type = "RIGIDSEGMENT"
            props.representation_template = "FLOW_SEGMENT_CIRCULAR"
        bpy.ops.bim.add_element()


class AddOccurrence(bpy.types.Operator, PolylineOperator):
    bl_idname = "bim.add_occurrence"
    bl_label = "Add Occurrence"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self):
        super().__init__()

    def create_occurrence(self, context, event):
        if not self.relating_type:
            return {"FINISHED"}

        result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
        if result:
            self.report({"WARNING"}, result)

        # TODO: when this workflow matures a bit, recode it so it doesn't rely on selection and cursor
        # Select snapped object so we can insert doors and windows
        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
        snap_obj = bpy.data.objects.get(snap_prop.snap_object)
        if snap_obj:
            try:
                # During undo, sometimes objects get invalidated.
                # This is a safe way to check for invalid objects.
                snap_obj.name
                snap_obj = bpy.data.objects.get(snap_obj.name)
                snap_obj.name
                tool.Blender.select_and_activate_single_object(context, snap_obj)
            except:
                pass

        point = context.scene.BIMPolylineProperties.insertion_polyline[0].polyline_points[0]
        context.scene.cursor.location = Vector((point.x, point.y, point.z))
        tool.Polyline.clear_polyline()

        bpy.ops.bim.add_constr_type_instance("INVOKE_DEFAULT")

        if snap_obj:
            snap_obj.select_set(False)

    def modal(self, context, event):
        # Ensure state of BIM tool props is valid
        props = bpy.context.scene.BIMModelProperties
        relating_type_id = tool.Blender.get_enum_safe(props, "relating_type_id")
        relating_type_id_data = AuthoringData.data["relating_type_id"]
        if not relating_type_id and relating_type_id_data:
            props.relating_type_id = relating_type_id_data[0][0]

        self.relating_type = None
        relating_type_id = props.relating_type_id
        if relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))

        if not self.relating_type:
            self.report({"WARNING"}, "You need to select a type.")
            PolylineDecorator.uninstall()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        self.handle_instructions(context)
        self.handle_mouse_move(context, event)
        self.choose_axis(event)
        self.handle_snap_selection(context, event)

        if not self.tool_state.is_input_on and event.value == "RELEASE" and event.type in {"RIGHTMOUSE"}:
            self.tool_state.axis_method = None
            context.workspace.status_text_set(text=None)
            ProductDecorator.uninstall()
            PolylineDecorator.uninstall()
            tool.Polyline.clear_polyline()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        if event.value == "RELEASE" and event.type == "LEFTMOUSE":
            self.create_occurrence(context, event)

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            ProductDecorator.uninstall()
            return cancel

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        super().invoke(context, event)
        ProductDecorator.install(context)
        self.tool_state.use_default_container = True
        self.tool_state.plane_method = "XY"
        return {"RUNNING_MODAL"}


class AddConstrTypeInstance(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_constr_type_instance"
    bl_label = "Add Type Occurrence"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Type Instance"
    relating_type_id: bpy.props.IntProperty(default=0, options={"SKIP_SAVE"})
    from_invoke: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})
    representation_template: bpy.props.EnumProperty(
        name="Representation Template",
        items=(
            ("EMPTY", "No Geometry", "Start with an empty object"),
            None,
            (
                "MESH",
                "Custom Tessellation",
                "Create a basic tessellated or faceted cube",
            ),
            (
                "EXTRUSION",
                "Custom Extruded Solid",
                "An extrusion from an arbitrary profile",
            ),
        ),
    )

    def invoke(self, context, event):
        props = context.scene.BIMModelProperties
        relating_type_id = self.relating_type_id or props.relating_type_id
        if (
            relating_type_id
            and (relating_type := tool.Ifc.get().by_id(int(relating_type_id)))
            and not relating_type.RepresentationMaps
        ):
            if (material := ifcopenshell.util.element.get_material(relating_type)) and (
                material.is_a("IfcMaterialProfileSet") or material.is_a("IfcMaterialLayerSet")
            ):
                return self.execute(context)
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "representation_template", text="")

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        relating_type_id = self.relating_type_id or props.relating_type_id

        if not relating_type_id:
            return {"FINISHED"}

        # Check relating_type_id enum_items since it's possible
        # that we're adding e.g. IfcRoofType being in a Slab Tool
        # and roof type id won't be present in the relating_type_id enum.
        if self.from_invoke and str(self.relating_type_id) in AuthoringData.data["relating_type_id"]:
            props.relating_type_id = str(self.relating_type_id)

        self.container = None
        self.container_obj = None
        if container := tool.Root.get_default_container():
            self.container = container
            self.container_obj = tool.Ifc.get_object(container)

        relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        ifc_class = relating_type.is_a()
        instance_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, tool.Ifc.get().schema)[0]
        material = ifcopenshell.util.element.get_material(relating_type)

        if material and material.is_a("IfcMaterialProfileSet"):
            if obj := profile.DumbProfileGenerator(relating_type).generate():
                tool.Blender.select_and_activate_single_object(context, obj)
                if relating_type.is_a("IfcFlowSegmentType"):
                    self.set_flow_segment_rl(obj)
                    mep.MEPGenerator(relating_type).setup_ports(obj)
                return {"FINISHED"}
        elif material and material.is_a("IfcMaterialLayerSet"):
            if self.generate_layered_element(ifc_class, relating_type):
                tool.Blender.select_and_activate_single_object(context, context.selected_objects[-1])
                return {"FINISHED"}
        elif not relating_type.RepresentationMaps:
            mesh = None if self.representation_template == "EMPTY" else bpy.data.meshes.new("Mesh")
            obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(relating_type, instance_class), mesh)
            obj.location = bpy.context.scene.cursor.location
            element = bonsai.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=instance_class,
                should_add_representation=False,
            )
            bonsai.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=relating_type)

            rprops = context.scene.BIMRootProperties
            ifc_context = None
            if get_enum_items(rprops, "contexts", context):
                ifc_context = int(rprops.contexts or "0") or None
                if ifc_context:
                    ifc_context = tool.Ifc.get().by_id(ifc_context)

            if self.representation_template == "EMPTY" or not ifc_context:
                pass
            elif self.representation_template == "MESH":
                builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                bm = bmesh.new()
                bmesh.ops.create_cube(bm, size=0.5)
                verts = [v.co / unit_scale for v in bm.verts]
                faces = [[v.index for v in p.verts] for p in bm.faces]
                item = builder.mesh(verts, faces)
                bm.free()
                representation = builder.get_representation(ifc_context, [item])
                ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=representation,
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
                )
            elif self.representation_template == "EXTRUSION":
                builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                curve = builder.rectangle(size=Vector((0.5, 0.5)) / unit_scale)
                item = builder.extrude(curve, magnitude=0.5 / unit_scale)
                representation = builder.get_representation(ifc_context, [item])
                ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=representation,
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
                )
            return

        building_obj = None
        if len(context.selected_objects) == 1 and context.active_object:
            building_obj = context.active_object
            building_element = tool.Ifc.get_entity(building_obj)

        mesh = bpy.data.meshes.new(name="Instance")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(relating_type, instance_class), mesh)

        obj.location = context.scene.cursor.location

        element = bonsai.core.root.assign_class(
            tool.Ifc, tool.Collector, tool.Root, obj=obj, ifc_class=instance_class, should_add_representation=False
        )

        element = tool.Ifc.get_entity(obj)
        bonsai.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=relating_type)

        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not representation and element.Representation:
            representation = element.Representation.Representations[0]

        if representation:
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )

        # Update required as core.type.assign_type may change obj.data
        context.view_layer.update()

        if (
            building_obj
            and building_element
            and building_element.is_a() in ["IfcWall", "IfcWallStandardCase", "IfcCovering", "IfcElementAssembly"]
            and instance_class in ["IfcWindow", "IfcDoor"]
        ):
            # Fills should be a sibling to the building element
            parent = ifcopenshell.util.element.get_aggregate(building_element)
            if parent:
                parent_obj = tool.Ifc.get_object(parent)
                bonsai.core.aggregate.assign_object(
                    tool.Ifc, tool.Aggregate, tool.Collector, relating_obj=parent_obj, related_obj=obj
                )
            else:
                parent = ifcopenshell.util.element.get_container(building_element)
                if parent:
                    bonsai.core.spatial.assign_container(
                        tool.Ifc, tool.Collector, tool.Spatial, container=parent, element_obj=obj
                    )

        # set occurrences properties for the types defined with modifiers
        if instance_class in ["IfcWindow", "IfcDoor"]:
            pset_name = f"BBIM_{instance_class[3:]}"
            bbim_pset = ifcopenshell.util.element.get_psets(element).get(pset_name, None)
            if bbim_pset:
                bbim_prop_data = json.loads(bbim_pset["Data"])
                element.OverallWidth = bbim_prop_data["overall_width"]
                element.OverallHeight = bbim_prop_data["overall_height"]

        if (
            building_obj
            and building_element
            and building_element.is_a() in ["IfcWall", "IfcWallStandardCase", "IfcCovering", "IfcElementAssembly"]
        ):
            if instance_class in ["IfcWindow", "IfcDoor"]:
                # TODO For now we are hardcoding windows and doors as a prototype
                bpy.ops.bim.add_filled_opening(voided_obj=building_obj.name, filling_obj=obj.name)
        else:
            if self.container_obj:
                if props.rl_mode == "BOTTOM":
                    obj.location.z = self.container_obj.location.z - tool.Blender.get_object_bounding_box(obj)["min_z"]
                elif props.rl_mode == "CONTAINER":
                    obj.location.z = self.container_obj.location.z
                elif props.rl_mode == "CURSOR":
                    pass

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for port in ifcopenshell.util.system.get_ports(relating_type):
            mat = Matrix(ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement))
            mat.translation *= unit_scale
            mat = obj.matrix_world @ mat
            new_port = tool.Ifc.run("root.create_entity", ifc_class="IfcDistributionPort")
            new_port.PredefinedType = port.PredefinedType
            new_port.SystemType = port.SystemType
            tool.Ifc.run("system.assign_port", element=element, port=new_port)
            tool.Ifc.run("geometry.edit_object_placement", product=new_port, matrix=mat, is_si=True)

        if ifc_class == "IfcDoorType" and len(context.selected_objects) >= 1:
            pass
        else:
            tool.Blender.select_and_activate_single_object(context, obj)
        return {"FINISHED"}

    def set_flow_segment_rl(self, obj):
        if self.container_obj:
            obj.location[2] = self.container_obj.location[2] + bpy.context.scene.BIMModelProperties.rl2

    @staticmethod
    def generate_layered_element(ifc_class: str, relating_type: ifcopenshell.entity_instance) -> bool:
        usage = tool.Model.get_usage_type(relating_type)

        obj = None
        if usage == "LAYER3":
            obj = slab.DumbSlabGenerator(relating_type).generate()
        elif usage == "LAYER2":
            obj = wall.DumbWallGenerator(relating_type).generate()
        else:
            pass  # Dumb block generator? Eh? :)

        if obj:
            material = ifcopenshell.util.element.get_material(tool.Ifc.get_entity(obj))
            material.LayerSetDirection = f"AXIS{usage[-1]}"
            return True
        return False


class ChangeTypePage(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_type_page"
    bl_label = "Change Type Page"
    bl_options = {"REGISTER"}
    page: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        bpy.ops.bim.load_type_thumbnails(ifc_class=props.ifc_class, offset=9 * (self.page - 1), limit=9)
        props.type_page = self.page
        return {"FINISHED"}


class SetActiveType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_active_type"
    bl_label = "Set Active Type"
    bl_options = {"REGISTER"}
    relating_type: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        props.relating_type_id = str(self.relating_type)
        context.window.screen = context.window.screen  # Closes the type manager popup


class AlignProduct(bpy.types.Operator):
    bl_idname = "bim.align_product"
    bl_label = "Align Product"
    bl_description = "Align the selected objects to the active object"
    bl_options = {"REGISTER", "UNDO"}

    AlignType = Literal["CENTERLINE", "POSITIVE", "NEGATIVE"]
    align_type: bpy.props.EnumProperty(  # type: ignore [reportRedeclaration]
        items=[(i, i, "") for i in get_args(AlignType)]
    )

    if TYPE_CHECKING:
        align_type: AlignType

    def execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) < 2 or not context.active_object:
            self.report({"ERROR"}, "Please select atleast 2 objects.")
            return {"FINISHED"}
        if self.align_type == "CENTERLINE":
            point = context.active_object.matrix_world @ (
                Vector(context.active_object.bound_box[0]) + (context.active_object.dimensions / 2)
            )
        elif self.align_type == "POSITIVE":
            point = context.active_object.matrix_world @ Vector(context.active_object.bound_box[6])
        elif self.align_type == "NEGATIVE":
            point = context.active_object.matrix_world @ Vector(context.active_object.bound_box[0])
        else:
            assert_never(self.align_type)

        active_x_axis = context.active_object.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        active_y_axis = context.active_object.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        active_z_axis = context.active_object.matrix_world.to_quaternion() @ Vector((0, 0, 1))

        x_distances = self.get_axis_distances(point, active_x_axis, context)
        y_distances = self.get_axis_distances(point, active_y_axis, context)
        if abs(sum(x_distances)) < abs(sum(y_distances)):
            for i, obj in enumerate(selected_objs):
                obj.matrix_world = Matrix.Translation(active_x_axis * -x_distances[i]) @ obj.matrix_world
        else:
            for i, obj in enumerate(selected_objs):
                obj.matrix_world = Matrix.Translation(active_y_axis * -y_distances[i]) @ obj.matrix_world
        return {"FINISHED"}

    def get_axis_distances(self, point: Vector, axis: Vector, context: bpy.types.Context) -> list[float]:
        results = []
        for obj in context.selected_objects:
            if self.align_type == "CENTERLINE":
                obj_point = obj.matrix_world @ (Vector(obj.bound_box[0]) + (obj.dimensions / 2))
            elif self.align_type == "POSITIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[6])
            elif self.align_type == "NEGATIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[0])
            else:
                assert_never(self.align_type)
            results.append(mathutils.geometry.distance_point_to_plane(obj_point, point, axis))
        return results


class LoadTypeThumbnails(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_type_thumbnails"
    bl_label = "Load Type Thumbnails"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    limit: bpy.props.IntProperty()
    offset: bpy.props.IntProperty()

    def _execute(self, context):
        if bpy.app.background:
            return

        props = bpy.context.scene.BIMModelProperties
        processing = set()
        # Only process at most one paginated class at a time.
        # Large projects have hundreds of types which can lead to unnecessary lag.
        queue = sorted(tool.Ifc.get().by_type(self.ifc_class), key=lambda e: e.Name or "Unnamed")
        if self.limit:
            queue = queue[self.offset : self.offset + self.limit]
        else:
            offset = 9 * (props.type_page - 1)
            if offset < 0:
                offset = 0
            queue = queue[offset : offset + 9]

        while queue:
            # if bpy.app.is_job_running("RENDER_PREVIEW") does not seem to reflect asset preview generation
            element = queue.pop()
            if tool.Model.update_thumbnail_for_element(element):
                queue.append(element)
        return {"FINISHED"}


class MirrorElements(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.mirror_elements"
    bl_label = "Mirror Elements"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Faux-mirrors the selected objects by an active empty along a mirror plane"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        # This is not a true mirror operation. In BIM, objects that are
        # mirrored are not the same type. (i.e. a mirrored asymmetric desk is a
        # completely different product). To preserve types, we calculate
        # bounding box centroids, and mirror the position of the object.  The
        # mirrored object performs the necessary rotation to preserve the
        # mirrored intention, but never actually truly mirror anything (i.e.
        # scale = -1).

        # Objects are mirrored along the YZ plane of the mirror object.
        # Mirrored objects have their relative local Y and Z axes preserved,
        # and the new X axis is calculated.

        # In theory, untyped objects may be truly mirrored, but this is not yet
        # implemented.
        mirror = context.active_object
        reflection = Matrix()
        reflection[0][0] = -1

        mirror.select_set(False)

        if not context.selected_objects:
            self.report(
                {"INFO"},
                "At least two objects must be selected: an object to be mirrored, and a mirror axis as the active object.",
            )
            return {"FINISHED"}

        bpy.ops.bim.override_object_duplicate_move(is_interactive=False)

        for obj in context.selected_objects:
            if obj == mirror:
                continue

            objmat = mirror.matrix_world.inverted() @ obj.matrix_world.copy()
            x, y, z = objmat.to_3x3().col
            centroid = Vector(obj.bound_box[0]).lerp(Vector(obj.bound_box[6]), 0.5)
            c = mirror.matrix_world.inverted() @ obj.matrix_world @ centroid
            newy = mirror.matrix_world.to_quaternion() @ (y @ reflection)
            newz = mirror.matrix_world.to_quaternion() @ (z @ reflection)
            newx = newy.cross(newz)
            newc = mirror.matrix_world @ (c @ reflection)

            newmat = Matrix((newx.to_4d(), newy.to_4d(), newz.to_4d(), newc.to_4d())).transposed()
            newmat.translation = Vector(newmat.translation) - (newmat.to_quaternion() @ centroid)

            obj.matrix_world = newmat


def generate_box(usecase_path, ifc_file, settings):
    box_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Box", "MODEL_VIEW")
    if not box_context:
        return
    obj = settings["blender_object"]
    if 0 in list(obj.dimensions):
        return
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    old_box = ifcopenshell.util.representation.get_representation(product, "Model", "Box", "MODEL_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_box:
            bonsai.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_box)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_box},
        )


def regenerate_profile_usage(usecase_path, ifc_file, settings):
    elements = []
    if ifc_file.schema == "IFC2X3":
        for rel in ifc_file.get_inverse(settings["usage"]):
            if not rel.is_a("IfcRelAssociatesMaterial"):
                continue
            for element in rel.RelatedObjects:
                elements.append(element)
    else:
        for rel in settings["usage"].AssociatedTo:
            for element in rel.RelatedObjects:
                elements.append(element)

    for element in elements:
        obj = IfcStore.get_element(element.id())
        if not obj:
            continue
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if representation:
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )
