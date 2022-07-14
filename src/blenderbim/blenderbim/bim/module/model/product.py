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

import bpy
import math
import mathutils
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.system
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.core.type
import blenderbim.core.geometry
from . import wall, slab, profile, mep
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.model.data import AuthoringData
from blenderbim.bim.helper import prop_with_search, col_with_margins
from ifcopenshell.api.pset.data import Data as PsetData
from mathutils import Vector, Matrix
from bpy_extras.object_utils import AddObjectHelper
from . import prop


class AddEmptyType(bpy.types.Operator, AddObjectHelper):
    bl_idname = "bim.add_empty_type"
    bl_label = "Add Empty Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.data.objects.new("TYPEX", None)
        context.scene.collection.objects.link(obj)
        context.scene.BIMRootProperties.ifc_product = "IfcElementType"
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = obj
        obj.select_set(True)
        return {"FINISHED"}


def add_empty_type_button(self, context):
    self.layout.operator(AddEmptyType.bl_idname, icon="FILE_3D")


def close_operator_panel(event):
    x, y = event.mouse_x, event.mouse_y
    bpy.context.window.cursor_warp(10, 10)
    move_back = lambda: bpy.context.window.cursor_warp(x, y)
    bpy.app.timers.register(move_back, first_interval=0.001)


class AddTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_type_instance"
    bl_label = "Add"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Type Instance to the model"
    constr_class: bpy.props.StringProperty()
    constr_type_id: bpy.props.IntProperty()
    from_invoke: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if self.from_invoke:
            close_operator_panel(event)
        return self.execute(context)

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        constr_class = self.constr_class or props.constr_class
        constr_type_id = self.constr_type_id or props.constr_type_id

        if not constr_class or not constr_type_id:
            return {"FINISHED"}

        if self.from_invoke:
            props.constr_class = self.constr_class
            props.constr_type_id = str(self.constr_type_id)

        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(constr_class, self.file.schema)[0]
        constr_type = self.file.by_id(int(constr_type_id))
        material = ifcopenshell.util.element.get_material(constr_type)

        if material and material.is_a("IfcMaterialProfileSet"):
            if profile.DumbProfileGenerator(constr_type).generate():
                return {"FINISHED"}
        elif material and material.is_a("IfcMaterialLayerSet"):
            if self.generate_layered_element(constr_class, constr_type):
                return {"FINISHED"}
        if constr_type.is_a("IfcFlowSegmentType") and not constr_type.RepresentationMaps:
            if mep.MepGenerator(constr_type).generate():
                return {"FINISHED"}

        building_obj = None
        if len(context.selected_objects) == 1 and context.active_object:
            building_obj = context.active_object

        # A cube
        verts = [
            Vector((-1, -1, -1)),
            Vector((-1, -1, 1)),
            Vector((-1, 1, -1)),
            Vector((-1, 1, 1)),
            Vector((1, -1, -1)),
            Vector((1, -1, 1)),
            Vector((1, 1, -1)),
            Vector((1, 1, 1)),
        ]
        edges = []
        faces = [
            [0, 1, 3, 2],
            [2, 3, 7, 6],
            [6, 7, 5, 4],
            [4, 5, 1, 0],
            [2, 6, 4, 0],
            [7, 3, 1, 5],
        ]
        mesh = bpy.data.meshes.new(name="Instance")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(constr_type, instance_class), mesh)
        obj.location = context.scene.cursor.location
        collection = context.view_layer.active_layer_collection.collection
        collection.objects.link(obj)
        collection_obj = bpy.data.objects.get(collection.name)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        element = tool.Ifc.get_entity(obj)
        blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=constr_type)

        if building_obj:
            if instance_class in ["IfcWindow", "IfcDoor"]:
                # TODO For now we are hardcoding windows and doors as a prototype
                bpy.ops.bim.add_element_opening(
                    voided_building_element=building_obj.name, filling_building_element=obj.name
                )
            if instance_class == "IfcDoor":
                obj.location[2] = building_obj.location[2] - min([v[2] for v in obj.bound_box])
        else:
            if collection_obj and collection_obj.BIMObjectProperties.ifc_definition_id:
                obj.location[2] = collection_obj.location[2] - min([v[2] for v in obj.bound_box])

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for port in ifcopenshell.util.system.get_ports(constr_type):
            mat = ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement)
            mat[0][3] *= unit_scale
            mat[1][3] *= unit_scale
            mat[2][3] *= unit_scale
            mat = obj.matrix_world @ mathutils.Matrix(mat)
            new_port = tool.Ifc.run("root.create_entity", ifc_class="IfcDistributionPort")
            tool.Ifc.run("system.assign_port", element=element, port=new_port)
            tool.Ifc.run("geometry.edit_object_placement", product=new_port, matrix=mat, is_si=True)

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {"FINISHED"}

    @staticmethod
    def generate_layered_element(ifc_class, relating_type):
        layer_set_direction = None

        parametric = ifcopenshell.util.element.get_psets(relating_type).get("EPset_Parametric")
        if parametric:
            layer_set_direction = parametric.get("LayerSetDirection", layer_set_direction)
        if layer_set_direction is None:
            if ifc_class in ["IfcSlabType", "IfcRoofType", "IfcRampType", "IfcPlateType"]:
                layer_set_direction = "AXIS3"
            else:
                layer_set_direction = "AXIS2"

        if layer_set_direction == "AXIS3":
            if slab.DumbSlabGenerator(relating_type).generate():
                return True
        elif layer_set_direction == "AXIS2":
            if wall.DumbWallGenerator(relating_type).generate():
                return True
        else:
            pass  # Dumb block generator? Eh? :)


class DisplayConstrTypes(bpy.types.Operator):
    bl_idname = "bim.display_constr_types"
    bl_label = "Browse Construction Types"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Display all available Construction Types to add new instances"

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        return {"FINISHED"}

    def invoke(self, context, event):
        if not AuthoringData.is_loaded:
            AuthoringData.load()
        AuthoringData.setup_constr_type_browser()
        props = context.scene.BIMModelProperties
        if props.unfold_relating_type:
            constr_class = props.constr_class_browser
            constr_type_info = AuthoringData.constr_type_info(constr_class)
            if constr_type_info is None or not constr_type_info.fully_loaded:
                AuthoringData.assetize_constr_class(constr_class)
        else:
            prop.update_constr_type(props, context)
        min_width = 250
        width_scaling = 5 ** -1
        width = max([min_width, int(width_scaling * context.region.width)])
        return context.window_manager.invoke_popup(self, width=width)

    def draw(self, context):
        props = context.scene.BIMModelProperties
        if props.unfold_relating_type:
            self.draw_by_constr_class(props)
        else:
            self.draw_by_constr_class_and_type(props)

    def draw_header(self, props):
        layout = self.layout
        inner_layout = col_with_margins(layout, margin_left=0.004)
        inner_layout.row().separator(factor=0.75)
        split = inner_layout.split(align=True, factor=2./3)
        col1 = split.column(align=True)
        row = col1.row()
        row.prop(data=props, property="unfold_relating_type", text="Preview All Construction Types")
        col1.row().separator(factor=1)
        row = col1.row()
        row.label(text="Select Construction Type:")
        col1.row().separator(factor=1.5)
        enabled = True
        if AuthoringData.data["constr_classes"]:
            subsplit = col1.split(factor=1./3)
            subsplit.column().row().label(text="Construction Class:", icon="FILE_VOLUME")
            prop_with_search(subsplit.column(), props, "constr_class_browser", text="")
            col1.row().separator()
        else:
            enabled = False
        col2 = split.column(align=True)
        subsplit = col2.split(factor=0.9)
        subcol = [subsplit.column() for _ in range(2)][-1]
        subcol.operator("bim.type_instance_help", text="", icon="QUESTION")
        col2.row().separator(factor=1)
        return {"enabled": enabled, "layout": inner_layout, "col1": col1, "col2": col2}

    def draw_by_constr_class(self, props):
        header_data = self.draw_header(props)
        enabled, layout = [header_data[key] for key in ["enabled", "layout"]]
        constr_class_browser = props.constr_class_browser
        num_cols = 3
        layout.row().separator(factor=0.25)
        layout.row().label(text="Construction Types:", icon="FILE_3D")
        layout.row().separator(factor=0.25)
        flow = layout.grid_flow(row_major=True, columns=num_cols, even_columns=True, even_rows=True, align=True)
        constr_types_browser = AuthoringData.constr_types_browser()
        num_types = len(constr_types_browser)
        for idx, (constr_type_id_browser, name, desc) in enumerate(constr_types_browser):
            outer_col = flow.column()
            box = outer_col.box()
            row = box.row()
            row.label(text=name, icon="FILE_3D")
            row.alignment = "CENTER"
            row = box.row()
            if enabled:
                preview_constr_types = AuthoringData.data["preview_constr_types"]
                if constr_class_browser in preview_constr_types:
                    preview_constr_class = preview_constr_types[constr_class_browser]
                    if constr_type_id_browser in preview_constr_class:
                        icon_id = preview_constr_class[constr_type_id_browser]["icon_id"]
                        row.template_icon(icon_value=icon_id, scale=6.)
            box.row().separator(factor=0.2)
            row = box.row()
            split = row.split(factor=0.5)
            col = split.column()
            op = col.operator("bim.select_type_instance", icon="RIGHTARROW_THIN")
            op.constr_class = constr_class_browser
            op.constr_type_id = constr_type_id_browser
            col = split.column()
            op = col.operator("bim.add_type_instance", icon="ADD")
            op.from_invoke = True
            op.constr_class = constr_class_browser
            if constr_type_id_browser.isnumeric():
                op.constr_type_id = int(constr_type_id_browser)
            factor = 2 if idx + 1 < math.ceil(num_types / num_cols) else 1.5
            outer_col.row().separator(factor=factor)
        last_row_cols = num_types % num_cols
        if last_row_cols != 0:
            for _ in range(num_cols - last_row_cols):
                flow.column()

    def draw_by_constr_class_and_type(self, props):
        header_data = self.draw_header(props)
        enabled, col1, col2 = [header_data[key] for key in ["enabled", "col1", "col2"]]
        constr_class_browser = props.constr_class_browser
        constr_type_id_browser = props.constr_type_id_browser
        if AuthoringData.data["constr_types_ids_browser"]:
            subsplit = col1.split(factor=1. / 3)
            subsplit.column().row().label(text="Construction Type:", icon="FILE_3D")
            prop_with_search(subsplit.column(), props, "constr_type_id_browser", text="")
            col1.row().separator()
        else:
            enabled = False
        col1.row().separator(factor=4.75)
        row = col1.row()
        row.enabled = enabled
        op = row.operator("bim.select_type_instance", icon="RIGHTARROW_THIN")
        op.constr_class = constr_class_browser
        op.constr_type_id = constr_type_id_browser
        op = row.operator("bim.add_type_instance", icon="ADD")
        op.from_invoke = True
        op.constr_class = constr_class_browser
        if constr_type_id_browser.isnumeric():
            op.constr_type_id = int(constr_type_id_browser)
        col2.row().separator(factor=1.25)
        split = col2.split(factor=0.025)
        col = [split.column() for _ in range(2)][-1]
        box = col.box()
        if enabled:
            box.template_icon(icon_value=props.icon_id, scale=5.6)
        col1.row().separator(factor=1)


class SelectTypeInstance(bpy.types.Operator):
    bl_idname = "bim.select_type_instance"
    bl_label = "Select"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Pick Type Instance as selection for subsequent operations"
    constr_class: bpy.props.StringProperty()
    constr_type_id: bpy.props.StringProperty()

    def invoke(self, context, event):
        close_operator_panel(event)
        return self.execute(context)

    def execute(self, context):
        props = context.scene.BIMModelProperties
        if self.constr_class != "":
            props.constr_class = self.constr_class
            AuthoringData.load_constr_types()
        if self.constr_type_id != "":
            props.constr_type_id = self.constr_type_id
        return {"FINISHED"}


class TypeInstanceHelp(bpy.types.Operator):
    bl_idname = "bim.type_instance_help"
    bl_label = "Construction Types Help"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Click to read some contextual help"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=510)

    def draw(self, context):
        layout = self.layout
        layout.row().separator(factor=0.5)
        row = layout.row()
        row.alignment = "CENTER"
        row.label(text="BlenderBIM Help", icon="BLENDER")
        layout.row().separator(factor=0.5)

        row = col_with_margins(layout.row()).row()
        row.label(text="Overview:", icon="KEYTYPE_MOVING_HOLD_VEC")
        self.draw_lines(layout, self.message_summary)
        layout.row().separator()

        row = col_with_margins(layout.row()).row()
        row.label(text="Further support:", icon="KEYTYPE_MOVING_HOLD_VEC")
        layout.row().separator(factor=0.5)
        row = col_with_margins(layout).row()
        op = row.operator("bim.open_upstream", text="Homepage", icon="HOME")
        op.page = "home"
        op = row.operator("bim.open_upstream", text="Docs", icon="DOCUMENTS")
        op.page = "docs"
        op = row.operator("bim.open_upstream", text="Wiki", icon="CURRENT_FILE")
        op.page = "wiki"
        op = row.operator("bim.open_upstream", text="Community", icon="COMMUNITY")
        op.page = "community"
        layout.row().separator()

    def draw_lines(self, layout, lines):
        box = col_with_margins(layout).box()
        for line in lines:
            row = box.row()
            row.label(text=f"  {line}")

    @property
    def message_summary(self):
        return [
            'The Construction Type Browser allows to preview and add new instances to the model.',
            'For further support, please click on the Documentation link below.'
        ]


class AlignProduct(bpy.types.Operator):
    bl_idname = "bim.align_product"
    bl_label = "Align Product"
    bl_options = {"REGISTER", "UNDO"}
    align_type: bpy.props.StringProperty()

    def execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) < 2 or not context.active_object:
            return {"FINISHED"}
        if self.align_type == "CENTERLINE":
            point = context.active_object.matrix_world @ (
                Vector(context.active_object.bound_box[0]) + (context.active_object.dimensions / 2)
            )
        elif self.align_type == "POSITIVE":
            point = context.active_object.matrix_world @ Vector(context.active_object.bound_box[6])
        elif self.align_type == "NEGATIVE":
            point = context.active_object.matrix_world @ Vector(context.active_object.bound_box[0])

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

    def get_axis_distances(self, point, axis, context):
        results = []
        for obj in context.selected_objects:
            if self.align_type == "CENTERLINE":
                obj_point = obj.matrix_world @ (Vector(obj.bound_box[0]) + (obj.dimensions / 2))
            elif self.align_type == "POSITIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[6])
            elif self.align_type == "NEGATIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[0])
            results.append(mathutils.geometry.distance_point_to_plane(obj_point, point, axis))
        return results


class DynamicallyVoidProduct(bpy.types.Operator):
    bl_idname = "bim.dynamically_void_product"
    bl_label = "Dynamically Void Product"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj)
        if obj is None:
            return {"FINISHED"}
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        if not product.HasOpenings:
            return {"FINISHED"}
        if [m for m in obj.modifiers if m.type == "BOOLEAN"]:
            return {"FINISHED"}
        representation = ifcopenshell.util.representation.get_representation(product, "Model", "Body", "MODEL_VIEW")
        if not representation:
            return {"FINISHED"}
        was_edit_mode = obj.mode == "EDIT"
        if was_edit_mode:
            bpy.ops.object.mode_set(mode="OBJECT")
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            enable_dynamic_voids=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        if was_edit_mode:
            bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


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
            blenderbim.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_box)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_box}
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
            blenderbim.core.geometry.switch_representation(
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                enable_dynamic_voids=True,
                is_global=True,
                should_sync_changes_first=False,
            )


def ensure_material_assigned(usecase_path, ifc_file, settings):
    if usecase_path == "material.assign_material":
        if not settings.get("material", None):
            return
        elements = [settings["product"]]
    else:
        elements = []
        for rel in ifc_file.by_type("IfcRelAssociatesMaterial"):
            if rel.RelatingMaterial == settings["material"] or [
                e for e in ifc_file.traverse(rel.RelatingMaterial) if e == settings["material"]
            ]:
                elements.extend(rel.RelatedObjects)

    for element in elements:
        obj = IfcStore.get_element(element.GlobalId)
        if not obj or not obj.data:
            continue

        element_material = ifcopenshell.util.element.get_material(element)
        material = [m for m in ifc_file.traverse(element_material) if m.is_a("IfcMaterial")]

        object_material_ids = [
            om.BIMObjectProperties.ifc_definition_id
            for om in obj.data.materials
            if om is not None and om.BIMObjectProperties.ifc_definition_id
        ]

        if material[0].id() in object_material_ids:
            continue

        if len(obj.data.materials) == 1:
            obj.data.materials.clear()

        obj.data.materials.append(IfcStore.get_element(material[0].id()))
