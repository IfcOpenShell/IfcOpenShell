# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import mathutils
from functools import reduce
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
from blenderbim.bim.module.model.prop import store_cursor_position
from ifcopenshell.api.pset.data import Data as PsetData
from mathutils import Vector, Matrix
from bpy_extras.object_utils import AddObjectHelper
from . import prop


def select_and_activate_single_object(context, obj):
    bpy.ops.object.select_all(action="DESELECT")
    context.view_layer.objects.active = obj
    obj.select_set(True)


class AddEmptyType(bpy.types.Operator, AddObjectHelper):
    bl_idname = "bim.add_empty_type"
    bl_label = "Add Empty Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.data.objects.new("TYPEX", None)
        context.scene.collection.objects.link(obj)
        context.scene.BIMRootProperties.ifc_product = "IfcElementType"
        select_and_activate_single_object(context, obj)
        return {"FINISHED"}


def add_empty_type_button(self, context):
    self.layout.operator(AddEmptyType.bl_idname, icon="FILE_3D")


class AddConstrTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_constr_type_instance"
    bl_label = "Add"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Type Instance to the model"
    ifc_class: bpy.props.StringProperty()
    relating_type_id: bpy.props.IntProperty()
    from_invoke: bpy.props.BoolProperty(default=False)
    link_to_scene: bpy.props.BoolProperty(default=True)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        ifc_class = self.ifc_class or props.ifc_class
        relating_type_id = self.relating_type_id or props.relating_type_id

        if not ifc_class or not relating_type_id:
            return {"FINISHED"}

        if self.from_invoke:
            props.ifc_class = self.ifc_class
            props.relating_type_id = str(self.relating_type_id)

        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, self.file.schema)[0]
        relating_type = self.file.by_id(int(relating_type_id))
        material = ifcopenshell.util.element.get_material(relating_type)

        if material and material.is_a("IfcMaterialProfileSet"):
            if profile.DumbProfileGenerator(relating_type).generate(link_to_scene=self.link_to_scene):
                return {"FINISHED"}
        elif material and material.is_a("IfcMaterialLayerSet"):
            if self.generate_layered_element(ifc_class, relating_type, link_to_scene=self.link_to_scene):
                select_and_activate_single_object(context, context.selected_objects[-1])
                return {"FINISHED"}
        if relating_type.is_a("IfcFlowSegmentType") and not relating_type.RepresentationMaps:
            if mep.MepGenerator(relating_type).generate(link_to_scene=self.link_to_scene):
                return {"FINISHED"}

        building_obj = None
        if len(context.selected_objects) == 1 and context.active_object:
            building_obj = context.active_object
            building_element = tool.Ifc.get_entity(building_obj)

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
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(relating_type, instance_class), mesh)
        if self.link_to_scene:
            obj.location = context.scene.cursor.location
            collection = context.view_layer.active_layer_collection.collection
            collection.objects.link(obj)
            collection_obj = bpy.data.objects.get(collection.name)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        element = tool.Ifc.get_entity(obj)
        blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=relating_type)
        if self.link_to_scene:
            # Update required as core.type.assign_type may change obj.data
            context.view_layer.update()

        if (
            building_obj
            and building_element
            and building_element.is_a() in ["IfcWall", "IfcWallStandardCase", "IfcCovering"]
        ):
            if instance_class in ["IfcWindow", "IfcDoor"]:
                # TODO For now we are hardcoding windows and doors as a prototype
                bpy.ops.bim.add_filled_opening(voided_obj=building_obj.name, filling_obj=obj.name)
        elif self.link_to_scene:
            if collection_obj and collection_obj.BIMObjectProperties.ifc_definition_id:
                obj.location[2] = collection_obj.location[2] - min([v[2] for v in obj.bound_box])

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for port in ifcopenshell.util.system.get_ports(relating_type):
            mat = ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement)
            mat[0][3] *= unit_scale
            mat[1][3] *= unit_scale
            mat[2][3] *= unit_scale
            mat = obj.matrix_world @ mathutils.Matrix(mat)
            new_port = tool.Ifc.run("root.create_entity", ifc_class="IfcDistributionPort")
            tool.Ifc.run("system.assign_port", element=element, port=new_port)
            tool.Ifc.run("geometry.edit_object_placement", product=new_port, matrix=mat, is_si=True)

        select_and_activate_single_object(context, obj)
        return {"FINISHED"}

    @staticmethod
    def generate_layered_element(ifc_class, relating_type, link_to_scene=True):
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
            if slab.DumbSlabGenerator(relating_type).generate(link_to_scene=link_to_scene):
                return True
        elif layer_set_direction == "AXIS2":
            if wall.DumbWallGenerator(relating_type).generate(link_to_scene=link_to_scene):
                return True
        else:
            pass  # Dumb block generator? Eh? :)


class ChangeTypePage(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_type_page"
    bl_label = "Change Type Page"
    bl_options = {"REGISTER"}
    page: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        bpy.ops.bim.load_type_thumbnails(ifc_class=props.type_class, offset=9 * (self.page - 1), limit=9)
        props.type_page = self.page
        return {"FINISHED"}


class DisplayConstrTypes(bpy.types.Operator):
    bl_idname = "bim.display_constr_types"
    bl_label = "Browse Construction Types"
    bl_options = {"REGISTER"}
    bl_description = "Display all available Construction Types to add new instances"

    def invoke(self, context, event):
        if not AuthoringData.is_loaded:
            AuthoringData.load()
        props = context.scene.BIMModelProperties
        ifc_class = props.ifc_class
        constr_class_info = AuthoringData.constr_class_info(ifc_class)
        if constr_class_info is None or not constr_class_info.fully_loaded:
            AuthoringData.assetize_constr_class(ifc_class)
        bpy.ops.bim.display_constr_types_ui("INVOKE_DEFAULT")
        return {"FINISHED"}


class ReinvokeOperator(bpy.types.Operator):
    bl_idname = "bim.reinvoke_operator"
    bl_label = "Reinvoke Popup Operator"
    bl_options = {"REGISTER"}
    bl_description = "Reinvoke a popup operator"
    operator: bpy.props.StringProperty()

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        browser_state = context.scene.BIMModelProperties.constr_browser_state
        store_cursor_position(context, event, window=False)
        cursor_x, cursor_y = browser_state.cursor_x, browser_state.cursor_y
        window_x, window_y = browser_state.window_x, browser_state.window_y
        window = context.window
        operator = self.operator
        self.move_cursor_away(context, window)

        def move_cursor_to_window():
            window.cursor_warp(window_x, window_y)

        def run_operator(operator, *args, **kwargs):
            reduce(lambda x, arg: getattr(x, arg), operator.split("."), bpy.ops)(*args, **kwargs)

        def reinvoke():
            run_operator(operator, "INVOKE_DEFAULT", reinvoked=True)
            window.cursor_warp(cursor_x, cursor_y)

        bpy.app.timers.register(move_cursor_to_window, first_interval=browser_state.update_delay)
        bpy.app.timers.register(reinvoke, first_interval=3 * browser_state.update_delay)
        return {"FINISHED"}

    def move_cursor_away(self, context, window):  # closes current popup
        browser_state = context.scene.BIMModelProperties.constr_browser_state
        window.cursor_warp(browser_state.far_away_x, browser_state.far_away_y)

    @staticmethod
    def run_operator(operator, *args, **kwargs):
        reduce(lambda x, arg: getattr(x, arg), operator.split("."), bpy.ops)(*args, **kwargs)


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


class LoadTypeThumbnails(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_type_thumbnails"
    bl_label = "Load Type Thumbnails"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    limit: bpy.props.IntProperty()
    offset: bpy.props.IntProperty()

    def _execute(self, context):
        from PIL import Image, ImageDraw

        if bpy.app.background:
            return

        props = bpy.context.scene.BIMModelProperties
        processing = set()
        # Only process at most one paginated class at a time.
        # Large projects have hundreds of types which can lead to unnecessary lag.
        queue = sorted(tool.Ifc.get().by_type(self.ifc_class), key=lambda e: e.Name or "Unnamed")
        if self.limit:
            queue = queue[self.offset:self.offset + self.limit]
        else:
            offset = 9 * (props.type_page - 1)
            if offset < 0:
                offset = 0
            queue = queue[offset:offset + 9]

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        while queue:
            # if bpy.app.is_job_running("RENDER_PREVIEW") does not seem to reflect asset preview generation
            element = queue.pop()
            obj = tool.Ifc.get_object(element)

            if not obj:
                continue  # Nothing to process
            elif AuthoringData.type_thumbnails.get(element.id(), None):
                continue  # Already processed
            elif obj.preview and obj.preview.icon_id:
                AuthoringData.type_thumbnails[element.id()] = obj.preview.icon_id
                continue

            if obj.data:
                obj.asset_generate_preview()
                while not obj.preview:
                    pass
            else:
                size = 128
                img = Image.new("RGBA", (size, size))
                draw = ImageDraw.Draw(img)

                material = ifcopenshell.util.element.get_material(element)
                if material and material.is_a("IfcMaterialProfileSet"):
                    profile = material.MaterialProfiles[0].Profile
                    settings = ifcopenshell.geom.settings()
                    settings.set(settings.INCLUDE_CURVES, True)
                    shape = ifcopenshell.geom.create_shape(settings, profile)
                    verts = shape.verts
                    edges = shape.edges
                    grouped_verts = [[verts[i], verts[i + 1]] for i in range(0, len(verts), 3)]
                    grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]

                    max_x = max([v[0] for v in grouped_verts])
                    min_x = min([v[0] for v in grouped_verts])
                    max_y = max([v[1] for v in grouped_verts])
                    min_y = min([v[1] for v in grouped_verts])

                    dim_x = max_x - min_x
                    dim_y = max_y - min_y
                    max_dim = max([dim_x, dim_y])
                    scale = 100 / max_dim

                    for vert in grouped_verts:
                        vert[0] = round(scale * (vert[0] - min_x)) + ((size / 2) - scale * (dim_x / 2))
                        vert[1] = round(scale * (vert[1] - min_y)) + ((size / 2) - scale * (dim_y / 2))

                    for e in grouped_edges:
                        draw.line((tuple(grouped_verts[e[0]]), tuple(grouped_verts[e[1]])), fill="white", width=2)
                elif material and material.is_a("IfcMaterialLayerSet"):
                    thicknesses = [l.LayerThickness for l in material.MaterialLayers]
                    total_thickness = sum(thicknesses)
                    si_total_thickness = total_thickness * unit_scale
                    if si_total_thickness <= 0.051:
                        width = 10
                    elif si_total_thickness <= 0.11:
                        width = 20
                    elif si_total_thickness <= 0.21:
                        width = 30
                    elif si_total_thickness <= 0.31:
                        width = 40
                    else:
                        width = 50

                    height = 100

                    if element.is_a("IfcSlabType"):
                        width, height = height, width

                    x_offset = (size / 2) - (width / 2)
                    y_offset = (size / 2) - (height / 2)
                    draw.rectangle([x_offset, y_offset, width + x_offset, height + y_offset], outline="white", width=5)
                    current_thickness = 0
                    del thicknesses[-1]
                    for thickness in thicknesses:
                        current_thickness += thickness
                        if element.is_a("IfcSlabType"):
                            y = (current_thickness / total_thickness) * height
                            line = [x_offset, y_offset + y, x_offset + width, y_offset + y]
                        else:
                            x = (current_thickness / total_thickness) * width
                            line = [x_offset + x, y_offset, x_offset + x, y_offset + height]
                        draw.line(line, fill="white", width=2)
                elif False:
                    # TODO: things like parametric duct segments
                    pass
                elif not element.RepresentationMaps:
                    # Empties are represented by a generic thumbnail
                    width = height = 100
                    x_offset = (size / 2) - (width / 2)
                    y_offset = (size / 2) - (height / 2)
                    draw.line([x_offset, y_offset, width + x_offset, height + y_offset], fill="white", width=2)
                    draw.line([x_offset, y_offset + height, width + x_offset, y_offset], fill="white", width=2)
                    draw.rectangle([x_offset, y_offset, width + x_offset, height + y_offset], outline="white", width=5)
                else:
                    draw.line([0, 0, size, size], fill="red", width=2)
                    draw.line([0, size, size, 0], fill="red", width=2)

                pixels = [item for sublist in img.getdata() for item in sublist]

                obj.asset_generate_preview()
                while not obj.preview:
                    pass

                obj.preview.image_size = size, size
                obj.preview.image_pixels_float = pixels

            queue.append(element)
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

        if material and material[0].id() in object_material_ids:
            continue

        if len(obj.data.materials) == 1:
            obj.data.materials.clear()

        if not material:
            continue

        obj.data.materials.append(IfcStore.get_element(material[0].id()))
