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

import json
from typing import TYPE_CHECKING, Any, Literal, Optional, Union, get_args

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.pset
import ifcopenshell.api.system
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.system
import ifcopenshell.util.type
import ifcopenshell.util.unit
import numpy as np
from bpy_extras.object_utils import AddObjectHelper
from mathutils import Matrix, Vector

import bonsai.core.aggregate
import bonsai.core.geometry
import bonsai.core.model as core
import bonsai.core.root
import bonsai.core.spatial
import bonsai.core.type
import bonsai.tool as tool
from bonsai.bim.helper import get_enum_items
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.model.data import AuthoringData
from bonsai.bim.module.model.decorator import PolylineDecorator, ProductDecorator
from bonsai.bim.module.model.door import update_door_modifier_representation
from bonsai.bim.module.model.polyline import PolylineOperator

from . import mep, profile, slab, wall


class AddEmptyType(bpy.types.Operator, AddObjectHelper):
    bl_idname = "bim.add_empty_type"
    bl_label = "Add Empty Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.data.objects.new("TYPEX", None)
        context.scene.collection.objects.link(obj)
        rprops = tool.Root.get_root_props()
        rprops.ifc_product = "IfcElementType"
        tool.Blender.select_and_activate_single_object(context, obj)
        return {"FINISHED"}


class AddDefaultType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_default_type"
    bl_label = "Create"
    bl_description = "Create Construction Type"
    bl_options = {"REGISTER", "UNDO"}
    ifc_element_type: bpy.props.StringProperty()

    def _execute(self, context):
        props = tool.Root.get_root_props()
        props.ifc_product = "IfcElementType"
        props.ifc_class = self.ifc_element_type
        if self.ifc_element_type == "IfcWallType":
            if tool.Ifc.get().schema == "IFC2X3":
                props.ifc_predefined_type = "STANDARD"
            else:
                props.ifc_predefined_type = "SOLIDWALL"
            props.representation_template = "LAYERSET_AXIS2"
        elif self.ifc_element_type == "IfcRailingType":
            props.ifc_predefined_type = "BALUSTRADE"
            props.representation_template = "RAILING"

        elif self.ifc_element_type == "IfcRoofType":
            props.ifc_predefined_type = "HIP_ROOF"
            props.representation_template = "ROOF"
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
        elif self.ifc_element_type == "IfcMemberType":
            props.ifc_predefined_type = "CHORD"
            props.representation_template = "PROFILESET"
        elif self.ifc_element_type == "IfcPlateType":
            props.ifc_predefined_type = "SHEET"
            props.representation_template = "LAYERSET_AXIS3"
        elif self.ifc_element_type == "IfcFootingType":
            props.ifc_predefined_type = "FOOTING_BEAM"
            props.representation_template = "PROFILESET"
        elif self.ifc_element_type == "IfcPileType":
            props.ifc_predefined_type = "COHESION"
            props.representation_template = "PROFILESET"

        elif self.ifc_element_type == "IfcDuctSegmentType":
            props.ifc_predefined_type = "RIGIDSEGMENT"
            props.representation_template = "FLOW_SEGMENT_RECTANGULAR"
        elif self.ifc_element_type == "IfcPipeSegmentType":
            props.ifc_predefined_type = "RIGIDSEGMENT"
            props.representation_template = "FLOW_SEGMENT_CIRCULAR"

        elif self.ifc_element_type == "IfcStairFlightType":
            props.ifc_predefined_type = "STRAIGHT"
            props.representation_template = "STAIR"
        elif self.ifc_element_type == "IfcRampFlightType":
            props.ifc_predefined_type = "STRAIGHT"
            props.representation_template = "LAYERSET_AXIS3"

        elif self.ifc_element_type == "IfcFurnitureType":
            props.ifc_predefined_type = "CHAIR"
            props.representation_template = "MESH"
        elif self.ifc_element_type == "IfcSanitaryTerminalType":
            props.ifc_predefined_type = "TOILETPAN"
            props.representation_template = "MESH"
        elif self.ifc_element_type == "IfcLightFixtureType":
            props.ifc_predefined_type = "DIRECTIONSOURCE"
            props.representation_template = "MESH"
        elif self.ifc_element_type == "IfcElectricApplianceType":
            props.ifc_predefined_type = "WASHINGMACHINE"
            props.representation_template = "MESH"
        elif self.ifc_element_type == "IfcGeographicElementType":
            if tool.Ifc.get().schema == "IFC4":
                props.ifc_predefined_type = "USERDEFINED"
                props.ifc_userdefined_type = "VEGETATION"
            elif tool.Ifc.get().schema == "IFC4X3":
                props.ifc_predefined_type = "VEGETATION"
            props.representation_template = "MESH"

        bpy.ops.bim.add_element()


class DrawOccurrence(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    bl_idname = "bim.draw_occurrence"
    bl_label = "Draw Occurrence"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)

    def create_occurrence(self, context, event):
        if not self.relating_type:
            return {"FINISHED"}

        result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
        if result:
            self.report({"WARNING"}, result)

        # TODO: when this workflow matures a bit, recode it so it doesn't rely on selection and cursor
        # Select snapped object so we can insert doors and windows
        polyline_props = tool.Model.get_polyline_props()
        snap_prop = polyline_props.snap_mouse_point[0]
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

        point = polyline_props.insertion_polyline[0].polyline_points[0]
        context.scene.cursor.location = Vector((point.x, point.y, point.z))
        tool.Polyline.clear_polyline()

        bpy.ops.bim.add_occurrence("INVOKE_DEFAULT")

        if snap_obj:
            snap_obj.select_set(False)

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        # Ensure state of BIM tool props is valid
        props = tool.Model.get_model_props()
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
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _invoke(self, context, event):
        super().invoke(context, event)
        ProductDecorator.install(context)
        self.tool_state.use_default_container = True
        self.tool_state.plane_method = "XY"
        return {"RUNNING_MODAL"}


class AddOccurrence(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_occurrence"
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
        props = tool.Model.get_model_props()
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
        ifc_file = tool.Ifc.get()
        props = tool.Model.get_model_props()
        relating_type_id = self.relating_type_id or props.relating_type_id

        if not relating_type_id:
            return {"FINISHED"}

        # Check relating_type_id enum_items since it's possible
        # that we're adding e.g. IfcRoofType being in a Slab Tool
        # and roof type id won't be present in the relating_type_id enum.
        if self.from_invoke and str(self.relating_type_id) in AuthoringData.data["relating_type_id"]:
            props.relating_type_id = str(self.relating_type_id)

        building_obj, building_element = None, None
        if len(context.selected_objects) == 1 and context.active_object:
            building_obj = context.active_object
            building_element = tool.Ifc.get_entity(building_obj)

        self.container = None
        self.container_obj = None
        if (
            building_obj
            and building_element
            and (container := ifcopenshell.util.element.get_container(building_element))
        ):
            self.container = container
            self.container_obj = tool.Ifc.get_object(container)
        elif container := tool.Root.get_default_container():
            self.container = container
            self.container_obj = tool.Ifc.get_object(container)

        relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        ifc_class = relating_type.is_a()
        instance_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, tool.Ifc.get().schema)[0]
        material = ifcopenshell.util.element.get_material(relating_type)

        existing_context = None
        for existing_occurrence in ifcopenshell.util.element.get_types(relating_type):
            if existing_obj := tool.Ifc.get_object(existing_occurrence):
                existing_context = tool.Geometry.get_active_representation_context(existing_obj)
                break

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
            bonsai.core.type.assign_type(tool.Ifc, tool.Model, tool.Type, element=element, type=relating_type)

            rprops = tool.Root.get_root_props()
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
                )
            return

        mesh = bpy.data.meshes.new(name="Instance")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(relating_type, instance_class), mesh)

        obj.location = context.scene.cursor.location

        element = bonsai.core.root.assign_class(
            tool.Ifc, tool.Collector, tool.Root, obj=obj, ifc_class=instance_class, should_add_representation=False
        )

        element = tool.Ifc.get_entity(obj)
        bonsai.core.type.assign_type(tool.Ifc, tool.Model, tool.Type, element=element, type=relating_type)

        if existing_context:
            representation = ifcopenshell.util.representation.get_representation(element, existing_context)
        else:
            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not representation and element.Representation:
            representation = element.Representation.Representations[0]

        if representation:
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
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
                        tool.Ifc, tool.Collector, tool.Spatial, container=parent, objs=[obj]
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
            and instance_class in ["IfcWindow", "IfcDoor"]
        ):
            # TODO For now we are hardcoding windows and doors as a prototype
            tool.Model.add_filled_opening(building_obj, obj)
        else:
            if self.container_obj:
                bonsai.core.spatial.assign_container(
                    tool.Ifc, tool.Collector, tool.Spatial, container=self.container, objs=[obj]
                )
                if props.rl_mode == "BOTTOM":
                    obj.location.z = self.container_obj.location.z - tool.Blender.get_object_bounding_box(obj)["min_z"]
                elif props.rl_mode == "CONTAINER":
                    obj.location.z = self.container_obj.location.z
                elif props.rl_mode == "CURSOR":
                    pass

        tool.Model.sync_object_ifc_position(obj)

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for port in ifcopenshell.util.system.get_ports(relating_type):
            mat = Matrix(ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement))
            mat.translation *= unit_scale
            mat = obj.matrix_world @ mat
            new_port = ifcopenshell.api.system.add_port(ifc_file, element=element)
            new_port.PredefinedType = port.PredefinedType
            new_port.SystemType = port.SystemType
            ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=new_port, matrix=mat, is_si=True)

        if ifc_class == "IfcDoorType" and len(context.selected_objects) >= 1:
            pass
        else:
            tool.Blender.select_and_activate_single_object(context, obj)
        return {"FINISHED"}

    def set_flow_segment_rl(self, obj):
        if self.container_obj:
            props = tool.Model.get_model_props()
            obj.location[2] = self.container_obj.location[2] + props.rl2

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

    if TYPE_CHECKING:
        page: int

    def _execute(self, context):
        props = tool.Model.get_model_props()
        props.type_page = self.page
        bpy.ops.bim.load_type_thumbnails()
        return {"FINISHED"}


class SetActiveType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_active_type"
    bl_label = "Set Active Type"
    bl_options = {"REGISTER"}
    relating_type: bpy.props.IntProperty()

    def _execute(self, context):
        props = tool.Model.get_model_props()
        props.relating_type_id = str(self.relating_type)


# TODO: not exposed to UI.
class AlignProduct(bpy.types.Operator):
    bl_idname = "bim.align_product"
    bl_label = "Align Product"
    bl_description = "Align the selected objects to the active object"
    bl_options = {"REGISTER", "UNDO"}

    AlignType = Literal["CENTERLINE", "POSITIVE", "NEGATIVE"]
    align_type: bpy.props.EnumProperty(  # pyright: ignore [reportRedeclaration]
        items=[(i, i, "") for i in get_args(AlignType)]
    )

    if TYPE_CHECKING:
        align_type: AlignType

    def execute(self, context):
        try:
            core.align_objects(tool.Blender, tool.Model, self.align_type)
        except core.RequireAtLeastTwoElements as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class LoadTypeThumbnails(bpy.types.Operator):
    bl_idname = "bim.load_type_thumbnails"
    bl_label = "Load Type Thumbnails"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.app.background:
            return {"FINISHED"}

        # Only process at most one paginated class at a time.
        # Large projects have hundreds of types which can lead to unnecessary lag.
        if not AuthoringData.is_loaded:
            AuthoringData.load()
        queue = [tool.Ifc.get().by_id(t["id"]) for t in AuthoringData.data["paginated_relating_types"]]

        # The active type may be in another page than the active one:
        if relating_type_id_current := AuthoringData.data["relating_type_data"].get("id"):
            active_element = tool.Ifc.get_entity_by_id(relating_type_id_current)
            if active_element and active_element not in queue:
                queue.append(active_element)

        while queue:
            # if bpy.app.is_job_running("RENDER_PREVIEW") does not seem to reflect asset preview generation
            element = queue.pop()
            tool.Model.update_thumbnail_for_element(element)
        return {"FINISHED"}


class SharedMappedGeometryError(Exception):
    """Raised when mirroring would mutate geometry shared with sibling occurrences."""


class MirrorElements(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.mirror_elements"
    bl_label = "Mirror"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Mirrors the selected objects in place by truly inverting their geometry. "
        "Select a single object to mirror it about one of its own local planes. "
        "Select two or more and the active object becomes the mirror plane, passing through "
        "its middle. Mirror Axis picks which local axis of the object, or of the reference, "
        "is mirrored along. Nothing is duplicated: duplicate first to keep the original"
    )

    mirror_axis: bpy.props.EnumProperty(
        name="Mirror Axis",
        description=(
            "Local axis to mirror along. With a single object this is the object's own axis. "
            "With a reference object it is the reference's axis, and the mirror plane is the "
            "plane through the reference's middle at right angles to it"
        ),
        items=(
            ("X", "X", "Mirror along local X, about the local YZ plane"),
            ("Y", "Y", "Mirror along local Y, about the local XZ plane"),
            ("Z", "Z", "Mirror along local Z, about the local XY plane"),
        ),
        default="X",
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    @staticmethod
    def resolve_selection(
        context: bpy.types.Context,
    ) -> tuple[list[bpy.types.Object], Optional[bpy.types.Object]]:
        """Split the selection into the objects to mirror and the mirror plane, if any.

        Clicking a single object leaves the previously active object active but deselected.
        Reflecting across that invisible plane would be surprising, so it is ignored. Once more
        than one object is selected the active object is the user's reference even if Blender's
        selection flag has not caught up with it, which it may not have while the redo panel
        re-runs the operator. Dropping the reference there would quietly fall back to mirroring
        each object about its own axis, and for a wall on Y that is geometrically invisible.
        """
        selected = list(context.selected_objects)
        active_obj = context.active_object
        if active_obj and len(selected) < 2 and not active_obj.select_get():
            active_obj = None
        objs_to_mirror = [obj for obj in selected if obj != active_obj] if active_obj else []
        if objs_to_mirror:
            return objs_to_mirror, active_obj
        return selected, None

    def _execute(self, context):
        objs_to_mirror, mirror_ref = self.resolve_selection(context)
        if mirror_ref is None and len(context.selected_objects) > 1:
            self.report(
                {"WARNING"},
                "No active object to use as the mirror plane. Each object was mirrored about "
                "its own axis instead. Click the object you want as the mirror plane last.",
            )
        axis_index = "XYZ".index(self.mirror_axis)
        self.unsupported_items: set[str] = set()
        self.skipped: list[str] = []
        mirrored = 0
        for obj in objs_to_mirror:
            try:
                mirrored += bool(self.mirror_obj(context, obj, mirror_ref, axis_index))
            except SharedMappedGeometryError as e:
                self.report({"ERROR"}, str(e))
        if self.skipped:
            self.report(
                {"ERROR"} if not mirrored else {"WARNING"},
                f"Cannot invert {', '.join(self.skipped)} along {self.mirror_axis}"
                f" ({', '.join(sorted(self.unsupported_items))}), left untouched."
                " Try a different mirror axis.",
            )
        elif self.unsupported_items:
            self.report({"WARNING"}, f"Could not mirror: {', '.join(sorted(self.unsupported_items))}")
        if mirrored:
            # Say which plane was used. A reflection across a reference that straddles the
            # object's own mirror plane moves nothing, and without this the user cannot tell
            # that the reference was taken into account at all. The status bar flash is gone
            # by the time anyone asks what happened, so this also goes to the console.
            about = (
                f"across the middle of {mirror_ref.name}, along its local {self.mirror_axis}"
                if mirror_ref
                else f"about own local {self.mirror_axis} (no reference object)"
            )
            summary = f"Mirrored {mirrored} object{'s' if mirrored > 1 else ''} {about}"
            self.report({"INFO"}, summary)
            print(f"[bim.mirror_elements] {summary}")
        return {"FINISHED"} if mirrored else {"CANCELLED"}

    def mirror_obj(
        self,
        context: bpy.types.Context,
        obj: bpy.types.Object,
        mirror_ref: Optional[bpy.types.Object] = None,
        axis_index: int = 0,
    ) -> bool:
        """Mirror a single object. False means it was left untouched."""
        element = tool.Ifc.get_entity(obj)
        if not element:
            return False

        active_context = tool.Geometry.get_active_representation_context(obj)
        active_representation = tool.Geometry.get_active_representation(obj)
        bb_data = tool.Blender.get_object_bounding_box(obj)
        mirror_axes = self.get_mirror_axes(obj, mirror_ref, axis_index)

        type_element = ifcopenshell.util.element.get_type(element)
        usage_type = tool.Model.get_usage_type(element)
        # LAYER2 (walls) and LAYER3 (slabs) generate instance specific bodies via
        # DumbWallGenerator / DumbSlabGenerator rather than mapping the type's
        # RepresentationMaps, so they invert their own representation even when typed.
        is_typed_occurrence = bool(
            type_element
            and element.id() != type_element.id()
            and type_element.RepresentationMaps
            and usage_type not in ("LAYER2", "LAYER3")
        )

        # Check before touching anything. Reflecting the placement of an element whose geometry
        # could not be inverted would reproduce the faux mirror this operator exists to replace,
        # so such elements are reported and left exactly as they were.
        if is_typed_occurrence:
            blockers = self.find_uninvertible_items(type_element, (1.0, 0.0, 0.0))
        else:
            blockers = self.find_uninvertible_items(element, mirror_axes)
        if blockers:
            self.skipped.append(obj.name)
            self.unsupported_items.update(blockers)
            return False

        # Snapshot opening world placements AND the host placement BEFORE any geometry or
        # origin change. We work in the host's local space so the mirrored relative offset
        # is correct regardless of when the host's IFC placement gets synced.
        opening_placements_before: dict[int, np.ndarray] = {}
        M_host_before: Optional[np.ndarray] = None
        if getattr(element, "HasOpenings", None):
            M_host_before = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement).copy()
            for rel in element.HasOpenings:
                opening = rel.RelatedOpeningElement
                M = ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement)
                opening_placements_before[opening.id()] = M.copy()

        if is_typed_occurrence:
            # The shared mirrored type is always X flipped, so that is the axis the occurrence's
            # geometry ends up inverted along, whatever the mirror plane's orientation.
            geometry_axes = (1.0, 0.0, 0.0)
            self.assign_inverted_type(element)
        else:
            geometry_axes = mirror_axes
            self.invert_representation(element, mirror_axes)
            # For LAYER2 walls, layers stack along local Y (LayerSetDirection=AXIS2). A Y-axis
            # flip reverses that direction, so DirectionSense and OffsetFromReferenceLine must
            # both invert. X/Z flips do not touch local Y.
            if usage_type == "LAYER2" and mirror_axes[1] > 0.5:
                mat_usage = ifcopenshell.util.element.get_material(element, should_inherit=False)
                if mat_usage and mat_usage.is_a("IfcMaterialLayerSetUsage"):
                    mat_usage.DirectionSense = "NEGATIVE" if mat_usage.DirectionSense == "POSITIVE" else "POSITIVE"
                    mat_usage.OffsetFromReferenceLine = -mat_usage.OffsetFromReferenceLine

        context.view_layer.update()
        self.reflect_placement(obj, mirror_ref, geometry_axes, bb_data, axis_index)
        # reflect_placement may have written obj.location, and matrix_world only picks that up
        # after a depsgraph update. Without this the captured matrix is the pre-mirror one.
        context.view_layer.update()
        mirrored_matrix = obj.matrix_world.copy()

        # Openings are mirrored only now, after the origin has been reflected: they have to be
        # anchored to the host's final placement, and the frame change needs its final rotation.
        if opening_placements_before and M_host_before is not None:
            self.mirror_openings_after_reflection(obj, element, geometry_axes, M_host_before, opening_placements_before)
            tool.Geometry.clear_cache(element)

        # Bonsai does not automatically switch to the representation that should be active in
        # the given context, so an element retyped by assign_inverted_type would come back with
        # the wrong representation.
        representation = self.get_target_representation(element, active_representation, active_context)
        if representation:
            bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=representation)

        # Everything above moved the Blender object. Write that placement to IFC now, or the
        # mirror lives only in the viewport and the saved file keeps the old position. Reloading
        # the representation can snap the object back to the committed placement, so the intended
        # matrix is restored first.
        obj.matrix_world = mirrored_matrix
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj, apply_scale=False)
        return True

    def get_target_representation(
        self,
        element: ifcopenshell.entity_instance,
        active_representation: Optional[ifcopenshell.entity_instance],
        active_context: ifcopenshell.entity_instance,
    ) -> Union[ifcopenshell.entity_instance, None]:
        """Find the representation to display after the mirror.

        Matching on the context alone is not enough: files that put Axis, Body and BoundingBox
        in a single context would come back showing the Axis. The representation identifier has
        to be preserved as well.
        """
        representations = list(ifcopenshell.util.representation.get_representations_iter(element))
        if active_representation is not None:
            if active_representation in representations:
                return active_representation
            identifier = active_representation.RepresentationIdentifier
            context = active_representation.ContextOfItems
            for r in representations:
                if r.ContextOfItems == context and r.RepresentationIdentifier == identifier:
                    return r
            for r in representations:
                if r.RepresentationIdentifier == identifier:
                    return r
        return next((r for r in representations if r.ContextOfItems == active_context), None)

    def get_mirror_axes(
        self, obj: bpy.types.Object, mirror_ref: Optional[bpy.types.Object], axis_index: int = 0
    ) -> tuple[float, float, float]:
        """Return which of the object's local axes the geometry has to be inverted along.

        Without a reference the object is mirrored about its own local plane normal to
        ``axis_index``. With one, that axis of the reference is the mirror plane normal and the
        object's own closest axis is inverted.

        Exactly one axis is ever chosen, the one most parallel to the mirror plane normal.
        Flipping two axes at once would be a 180 degree rotation rather than a reflection, and
        reflect_placement relies on the representation flip having a negative determinant to
        produce an exact world space reflection for an arbitrarily oriented mirror plane.
        """
        if not mirror_ref:
            return tuple(1.0 if i == axis_index else 0.0 for i in range(3))
        mirror_normal_world = mirror_ref.matrix_world.to_3x3().col[axis_index].normalized()
        mirror_normal_local = obj.matrix_world.to_3x3().inverted() @ mirror_normal_world
        axis = max(range(3), key=lambda i: abs(mirror_normal_local[i]))
        return tuple(1.0 if i == axis else 0.0 for i in range(3))

    def find_uninvertible_items(
        self, element: ifcopenshell.entity_instance, mirror_axes: tuple[float, float, float]
    ) -> set[str]:
        """Report the representation items that cannot be inverted along ``mirror_axes``.

        Run before any mutation. ShapeBuilder.mirror works in the XY plane only, so a Z mirror
        is limited to the explicit meshes this operator inverts coordinate by coordinate.
        """
        is_z_mirror = mirror_axes[2] > 0.5
        blockers: set[str] = set()

        def visit(item: ifcopenshell.entity_instance) -> None:
            if item.is_a("IfcBooleanResult"):
                visit(item.FirstOperand)
                visit(item.SecondOperand)
            elif item.is_a("IfcFacetedBrep") or item.is_a("IfcFacetedBrepWithVoids"):
                return
            elif item.is_a("IfcMappedItem"):
                if self.is_type_owned_mapping(item):
                    raise SharedMappedGeometryError(
                        f"{element.is_a()} maps geometry owned by its type. Inverting it would "
                        "mirror every other occurrence of that type as well."
                    )
                for sub in item.MappingSource.MappedRepresentation.Items:
                    visit(sub)
            elif is_z_mirror:
                blockers.add(f"{item.is_a()} along Z")

        for representation in ifcopenshell.util.representation.get_representations_iter(element):
            for item in representation.Items:
                visit(item)
        return blockers

    def reflect_placement(
        self,
        obj: bpy.types.Object,
        mirror_ref: Optional[bpy.types.Object],
        geometry_axes: tuple[float, float, float],
        bb_data: dict[str, Any],
        axis_index: int = 0,
    ) -> None:
        if not mirror_ref:
            # No reference: mirror about the local plane through the bounding box centre so the
            # object stays where it is. Inverting the representation sends the local coordinate
            # on the flipped axis to its negative, so shifting the origin by min + max on that
            # axis turns it into a reflection about the centre. Derived from the pre-mirror
            # bounds on purpose: remeasuring the reloaded mesh would be wrong for a host whose
            # openings have not been mirrored yet.
            axis = max(range(3), key=lambda i: geometry_axes[i])
            name = "xyz"[axis]
            shift = Vector((0.0, 0.0, 0.0, 0.0))
            shift[axis] = bb_data[f"min_{name}"] + bb_data[f"max_{name}"]
            obj.location += (obj.matrix_world @ shift).xyz
            return

        # P_world is the Householder matrix of the mirror plane and P_local the diagonal of the
        # axis flip applied to the representation. For a local point p the new world position
        # is P_world @ R @ P_local @ (P_local @ p) + t' = P_world @ (R @ p + t - t_ref) + t_ref,
        # which is the exact reflection, whatever the plane's orientation. Both determinants
        # are -1, so new_R stays a proper rotation.
        P_local = Matrix.Diagonal(Vector([-1.0 if a > 0.5 else 1.0 for a in geometry_axes]))
        n_world = mirror_ref.matrix_world.to_3x3().col[axis_index].normalized()
        P_world = Matrix.Scale(-1, 4, n_world).to_3x3()
        new_mat = (P_world @ obj.matrix_world.to_3x3() @ P_local).to_4x4()
        t_mr = self.get_mirror_plane_point(mirror_ref)
        new_mat.translation = t_mr + P_world @ (obj.matrix_world.translation - t_mr)
        obj.matrix_world = new_mat

    @staticmethod
    def get_mirror_plane_point(mirror_ref: bpy.types.Object) -> Vector:
        """The point the mirror plane passes through: the middle of the reference object.

        An IFC object's origin is arbitrary and often sits at a corner or even at the model
        origin, so a plane through it lands somewhere the user cannot see and frequently cuts
        straight through the object being mirrored. The visible middle is predictable. An empty
        has an all zero bounding box, so using one as a mirror plane still pivots on its origin,
        which is the whole point of placing an empty.
        """
        centre = tool.Blender.get_object_bounding_box(mirror_ref)["center"]
        return mirror_ref.matrix_world @ Vector(centre)

    def mirror_openings_after_reflection(
        self,
        obj: bpy.types.Object,
        element: ifcopenshell.entity_instance,
        mirror_axes: tuple[float, float, float],
        M_host_before: np.ndarray,
        opening_placements_before: dict[int, np.ndarray],
    ) -> None:
        # Sync the element's IFC placement to its post-reflection Blender position first. The
        # geometry engine converts opening world positions to element local positions using the
        # element placement, so a stale placement lands the void at the wrong offset.
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj, apply_scale=False)
        M_host_new = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        self.apply_opening_mirror(element, mirror_axes, M_host_before, opening_placements_before, M_host_new)
        for rel in element.HasOpenings:
            opening = rel.RelatedOpeningElement
            tool.Geometry.clear_cache(opening)
            if opening_obj := tool.Ifc.get_object(opening):
                tool.Geometry.reload_representation(opening_obj)

    def apply_opening_mirror(
        self,
        element: ifcopenshell.entity_instance,
        mirror_axes: tuple[float, float, float],
        M_host_before: np.ndarray,
        opening_placements_before: dict[int, np.ndarray],
        M_host_new: Optional[np.ndarray] = None,
    ) -> None:
        """Mirror IfcOpeningElement placements and geometry in host local space.

        The host's new placement is by construction Reflect @ M_host_old @ P_local, where
        P_local is the same axis flip applied to its representation. An opening at host local L
        therefore only needs L' = P_local @ L to land on the true reflection: the reflection and
        the host's own movement cancel out. No correction for the host's rotation change is
        needed, and applying one skews openings whenever the mirror plane is not exactly
        parallel to a host local axis.

        M_host_new is the host's IFC world matrix after the mirror. None means it did not move.
        """
        M_host_anchor = M_host_new if M_host_new is not None else M_host_before
        N_local = np.array([1.0 if flip > 0.0 else 0.0 for flip in mirror_axes[:3]])
        norm = np.linalg.norm(N_local)
        if norm > 0:
            N_local /= norm
        H = np.eye(3) - 2 * np.outer(N_local, N_local)

        # A file may declare the same opening through more than one IfcRelVoidsElement.
        # Mirroring it twice would put it back where it started.
        for opening in {
            rel.RelatedOpeningElement.id(): rel.RelatedOpeningElement for rel in element.HasOpenings
        }.values():
            if opening.id() not in opening_placements_before:
                continue
            M_abs_old = opening_placements_before[opening.id()]
            M_rel = np.linalg.inv(M_host_before) @ M_abs_old
            M_rel_new = M_rel.copy()
            M_rel_new[:3, 3] = H @ M_rel[:3, 3]
            # Mirror the rotation by conjugation: H@R@H keeps det=+1 and gives the correct
            # mirrored rotation. A direct Householder on the columns yields det=-1, and IFC's
            # Y=Z*X normalisation then introduces a spurious 180 degree Z error.
            M_rel_new[:3, :3] = H @ M_rel[:3, :3] @ H
            ifcopenshell.api.geometry.edit_object_placement(
                tool.Ifc.get(), product=opening, matrix=M_host_anchor @ M_rel_new, is_si=False
            )

            if not opening.Representation:
                continue
            builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
            for rep in opening.Representation.Representations:
                for item in rep.Items:
                    if item.is_a("IfcExtrudedAreaSolid"):
                        self.mirror_opening_extrusion(builder, item, H)
                    else:
                        builder.mirror(item, mirror_axes[:2], create_copy=False)

    def mirror_opening_extrusion(
        self,
        builder: ifcopenshell.util.shape_builder.ShapeBuilder,
        item: ifcopenshell.entity_instance,
        H: np.ndarray,
    ) -> None:
        """Mirror an opening's extrusion with the host local Householder matrix H.

        Applying H as the geometric transform to opening local coordinates is correct because
        M_rel_new @ T_geom = H @ M_rel with M_rel_new = H@R@H, hence T_geom = H. Conjugating it
        into Position local space gives H_pos = placement.T @ H @ placement.
        """
        placement_mat = ifcopenshell.util.placement.get_axis2placement(item.Position)[:3, :3]
        H_pos = placement_mat.T @ H @ placement_mat

        pos_coords = item.Position.Location.Coordinates
        pos3 = np.array([pos_coords[0], pos_coords[1], pos_coords[2] if len(pos_coords) > 2 else 0.0])
        pos3_new = H @ pos3
        item.Position.Location.Coordinates = tuple(float(v) for v in pos3_new[: len(pos_coords)])

        # H_pos is a reflection (det=-1) so the profile winding has to be reversed.
        profile = item.SweptArea
        curves = [c for c in [getattr(profile, "OuterCurve", None)] if c is not None]
        curves.extend(getattr(profile, "InnerCurves", None) or [])
        for curve in curves:
            coords = builder.get_polyline_coords(curve)
            coords3 = np.hstack([coords, np.zeros((len(coords), 1))])
            builder.set_polyline_coords(curve, (H_pos @ coords3.T).T[:, :2][::-1])

        dir_local = np.array(item.ExtrudedDirection.DirectionRatios)
        item.ExtrudedDirection.DirectionRatios = tuple(float(v) for v in H_pos @ dir_local)

    def is_type_owned_mapping(self, item: ifcopenshell.entity_instance) -> bool:
        """Whether inverting this IfcMappedItem's source would affect sibling occurrences."""
        representation_map = item.MappingSource
        if len(representation_map.MapUsage) > 1:
            return True
        return any(inv.is_a("IfcTypeProduct") for inv in tool.Ifc.get().get_inverse(representation_map))

    def invert_general_object(
        self, element: ifcopenshell.entity_instance, mirror_axes: tuple[float, float, float] = (1.0, 0.0, 0.0)
    ) -> None:
        # ShapeBuilder.mirror works in 2D, so it only gets the XY components.
        mirror_axes_2d = mirror_axes[:2]
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())

        def mirror_item(item: ifcopenshell.entity_instance) -> None:
            if item.is_a("IfcBooleanResult"):
                mirror_item(item.FirstOperand)
                mirror_item(item.SecondOperand)
            elif item.is_a("IfcFacetedBrep") or item.is_a("IfcFacetedBrepWithVoids"):
                mirror_faceted_brep(item)
            elif item.is_a("IfcMappedItem"):
                if self.is_type_owned_mapping(item):
                    raise SharedMappedGeometryError(
                        f"{element.is_a()} maps geometry owned by its type. Inverting it would "
                        "mirror every other occurrence of that type as well."
                    )
                for sub in item.MappingSource.MappedRepresentation.Items:
                    mirror_item(sub)
            else:
                try:
                    builder.mirror(item, mirror_axes_2d, create_copy=False)
                except Exception:
                    # ShapeBuilder has no mirror for every representation item, half spaces in
                    # particular. Leave those alone and tell the user rather than aborting the
                    # whole mirror halfway through.
                    self.unsupported_items.add(item.is_a())

        def mirror_faceted_brep(item: ifcopenshell.entity_instance) -> None:
            shells = [item.Outer]
            if item.is_a("IfcFacetedBrepWithVoids"):
                shells.extend(item.Voids)

            points_done = set()
            for shell in shells:
                for face in shell.CfsFaces:
                    for bound in face.Bounds:
                        if not bound.Bound.is_a("IfcPolyLoop"):
                            continue
                        for pt in bound.Bound.Polygon:
                            if pt.id() in points_done:
                                continue
                            points_done.add(pt.id())
                            coords = list(pt.Coordinates)
                            for i, flip in enumerate(mirror_axes[: len(coords)]):
                                if flip > 0.0:
                                    coords[i] = -coords[i]
                            pt.Coordinates = coords

            # An odd number of flipped axes inverts the faces, so the winding has to be
            # reversed to restore outward normals.
            if sum(1 for v in mirror_axes if v > 0.0) % 2:
                for shell in shells:
                    for face in shell.CfsFaces:
                        for bound in face.Bounds:
                            if bound.Bound.is_a("IfcPolyLoop"):
                                bound.Bound.Polygon = list(reversed(bound.Bound.Polygon))

        if element.is_a("IfcProduct"):
            if not element.Representation:
                return
            for representation in element.Representation.Representations:
                for item in representation.Items:
                    mirror_item(item)
        elif element.is_a("IfcTypeProduct"):
            for representation_map in element.RepresentationMaps or []:
                for item in representation_map.MappedRepresentation.Items:
                    mirror_item(item)

        tool.Geometry.reload_representation(tool.Ifc.get_object(element))

    def invert_door_swing(self, element: ifcopenshell.entity_instance) -> None:
        obj = tool.Ifc.get_object(element)
        pset_data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Door", "Data"))

        if "LEFT" in pset_data["door_type"]:
            pset_data["door_type"] = pset_data["door_type"].replace("LEFT", "RIGHT")
        elif "RIGHT" in pset_data["door_type"]:
            pset_data["door_type"] = pset_data["door_type"].replace("RIGHT", "LEFT")

        pset = tool.Pset.get_element_pset(element, "BBIM_Door")
        pset_data_str = tool.Ifc.get().createIfcText(json.dumps(pset_data, default=list))
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": pset_data_str})

        pset_data.update(pset_data.pop("lining_properties"))
        pset_data.update(pset_data.pop("panel_properties"))
        pset_data.update(tool.Model.get_constituents_props_data(element))

        # set_props_kwargs_from_ifc_data updates the mesh of the active object, which would
        # switch its representation, so the door has to be active while it runs.
        prev_active = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = obj
        tool.Model.get_door_props(obj).set_props_kwargs_from_ifc_data(pset_data)
        bpy.context.view_layer.objects.active = prev_active

        update_door_modifier_representation(obj)
        tool.Model.mark_thumbnail_for_update(element)

    def invert_representation(
        self, element: ifcopenshell.entity_instance, mirror_axes: tuple[float, float, float] = (1.0, 0.0, 0.0)
    ) -> None:
        if ifcopenshell.util.element.get_pset(element, "BBIM_Door", "Data"):
            self.invert_door_swing(element)
        else:
            self.invert_general_object(element, mirror_axes)

    def assign_inverted_type(self, element: ifcopenshell.entity_instance) -> None:
        """Point a typed occurrence at a mirrored copy of its type.

        The type's own geometry is never inverted: that representation is shared with every
        sibling occurrence. Instead the type is duplicated once, the duplicate is inverted, and
        both are cross referenced so later mirrors of the same type reuse it.
        """
        type_element = ifcopenshell.util.element.get_type(element)

        inverted_type = tool.Blender.Modifier.has_mirrored_type(type_element)
        if not inverted_type:
            old_to_new, _ = tool.Geometry.duplicate_ifc_objects([tool.Ifc.get_object(type_element)])
            inverted_type = old_to_new[type_element][0]
            self.invert_representation(inverted_type)  # the cached type is always X flipped
            tool.Blender.Modifier.set_mirrored_type(inverted_type, type_element)
            tool.Blender.Modifier.set_mirrored_type(type_element, inverted_type)
            inverted_type.Name = f"{inverted_type.Name}.Mirror"

        bonsai.core.type.assign_type(tool.Ifc, tool.Model, tool.Type, element, inverted_type)


def generate_box(usecase_path: str, ifc_file: ifcopenshell.file, settings: dict[str, Any]) -> None:
    box_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Box", "MODEL_VIEW")
    if not box_context:
        return
    obj = settings["blender_object"]
    if 0 in list(obj.dimensions):
        return
    product = tool.Ifc.get_entity(obj)
    assert product
    old_box = ifcopenshell.util.representation.get_representation(product, "Model", "Box", "MODEL_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_box:
            bonsai.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_box)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.geometry.add_representation(
            ifc_file,
            should_run_listeners=False,  # ty:ignore[unknown-argument]
            **new_settings,
        )
        ifcopenshell.api.geometry.assign_representation(
            ifc_file,
            should_run_listeners=False,  # ty:ignore[unknown-argument]
            product=product,
            representation=new_box,
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
        obj = tool.Ifc.get_object_by_identifier(element.id())
        if not obj:
            continue
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if representation:
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
            )
