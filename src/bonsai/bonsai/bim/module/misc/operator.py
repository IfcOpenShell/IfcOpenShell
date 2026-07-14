# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from typing import TYPE_CHECKING, Literal, assert_never, get_args

import bpy
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.unit
import numpy as np
from mathutils import Matrix

import bonsai.core.geometry as core_geometry
import bonsai.core.misc as core
import bonsai.core.root
import bonsai.tool as tool

if TYPE_CHECKING:
    from bpy.stub_internal import rna_enums


class SetOverrideColour(bpy.types.Operator):
    bl_idname = "bim.set_override_colour"
    bl_label = "Set Override Colour"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        props = tool.Misc.get_misc_props()
        for obj in context.selected_objects:
            obj.color = props.override_colour
        assert (space := tool.Blender.get_view3d_space())
        space.shading.color_type = "OBJECT"
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


class ResizeToStorey(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.resize_to_storey"
    bl_label = "Resize To Storey"
    bl_description = (
        "Change object's origin to the bottom, move object to it's storey elevation and scale object to storey height.\n"
        "Storey height is based on the provided number of storeys above object's storey.\n"
        "If object's storey is the last storey, operator will have no effect"
    )
    bl_options = {"REGISTER", "UNDO"}
    total_storeys: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        for obj in context.selected_objects:
            if not (element := tool.Ifc.get_entity(obj)):
                continue
            if element.HasOpenings:
                self.report({"ERROR"}, f"Object '{obj.name}', scaling is not supported.")
                continue
            core.resize_to_storey(tool.Misc, tool.Ifc, obj=obj, total_storeys=self.total_storeys)


SplitAlongEdgeMode = Literal["BOOLEAN", "BISECT"]


class SplitAlongEdge(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.split_along_edge"
    bl_label = "Split Along Edge"
    bl_description = (
        "Split selected objects by the face of the cutter object.\n"
        "Active object is considered to be a cutting object. "
        "It can be a simple Blender object (e.g. a plane), not connected to IFC. "
        "Will unassign element from a type if type has a representation."
    )
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.EnumProperty(
        default="BOOLEAN",
        items=tuple((i, i, "") for i in get_args(SplitAlongEdgeMode)),
    )

    if TYPE_CHECKING:
        mode: SplitAlongEdgeMode

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object) or obj.type != "MESH":
            cls.poll_message_set("No active mesh object is selected.")
            return False
        if not context.selected_objects:
            cls.poll_message_set("No objects selected")
            return False
        return True

    def _execute(self, context):
        cutter = context.active_object
        assert cutter

        objs = [o for o in context.selected_objects if o != cutter and o.type == "MESH"]
        if not objs:
            self.report({"ERROR"}, "No other mesh objects selected besides the cutter object.")
            return {"CANCELLED"}

        if not tool.Ifc.get():
            if self.mode == "BOOLEAN":
                tool.Misc.boolean_objects_with_cutter(objs, cutter)
            elif self.mode == "BISECT":
                tool.Misc.bisect_objects_with_cutter(objs, cutter)
                for obj in objs:
                    bpy.data.objects.remove(obj)
            else:
                assert_never(self.mode)
            return

        objs_to_cut: list[bpy.types.Object] = []
        # Splitting only works on meshes
        for obj in objs:
            # You cannot split meshes if the representation is mapped.
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

            relating_type = tool.Root.get_element_type(element)
            if relating_type and tool.Root.does_type_have_representations(relating_type):
                bpy.ops.bim.unassign_type(related_object=obj.name)

            # refresh representation
            representation = tool.Geometry.get_active_representation(obj)

            # skip empty objects that might get in the way
            if not representation:
                continue

            core_geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                apply_openings=False,
            )

            if not tool.Geometry.is_meshlike(representation):
                bpy.ops.bim.update_representation(obj=obj.name, ifc_representation_class="IfcTessellatedFaceSet")

            objs_to_cut.append(obj)

        if self.mode == "BOOLEAN":
            new_objs = tool.Misc.boolean_objects_with_cutter(objs_to_cut, cutter)
        elif self.mode == "BISECT":
            new_objs = tool.Misc.bisect_objects_with_cutter(objs_to_cut, cutter)
        else:
            assert_never(self.mode)

        for obj in new_objs:
            bonsai.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)
            bpy.ops.bim.update_representation(obj=obj.name)
        for obj in objs_to_cut:
            bpy.ops.bim.update_representation(obj=obj.name)

            representation = tool.Geometry.get_active_representation(obj)
            assert representation
            core_geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                apply_openings=True,
            )

        self.report({"INFO"}, f"Splitting finished, {len(new_objs)} new objects created.")


class GetConnectedSystemElements(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.get_connected_system_elements"
    bl_label = "Get Connected System Elements"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        # Just dumped here for now before the system module gets properly planned
        def pprint_element(e):
            return "{} ({})".format(e.Name, e.GlobalId)

        start = tool.Ifc.get_entity(bpy.context.active_object)

        connected_elements = []

        # Note: this code is for IFC2X3. IFC4 has a different approach.
        print("Investigating element:", pprint_element(start))
        for rel in start.HasPorts:
            for rel2 in rel.RelatingPort.ConnectedTo:
                print(
                    "{} is connected as via {} ({}) TO {} ({}), contained in {}".format(
                        pprint_element(start),
                        rel.RelatingPort.FlowDirection,
                        rel.RelatingPort.GlobalId,
                        rel2.RelatedPort.FlowDirection,
                        rel2.RelatedPort.GlobalId,
                        [pprint_element(r.RelatedElement) for r in rel2.RelatedPort.ContainedIn],
                    )
                )
                connected_elements.extend([r.RelatedElement for r in rel2.RelatedPort.ContainedIn])
            for rel2 in rel.RelatingPort.ConnectedFrom:
                print(
                    "{} is connected as via {} ({}) FROM {} ({}), contained in {}".format(
                        pprint_element(start),
                        rel.RelatingPort.FlowDirection,
                        rel.RelatingPort.GlobalId,
                        rel2.RelatingPort.FlowDirection,
                        rel2.RelatingPort.GlobalId,
                        [pprint_element(r.RelatedElement) for r in rel2.RelatingPort.ContainedIn],
                    )
                )
                connected_elements.extend([r.RelatedElement for r in rel2.RelatingPort.ContainedIn])

        for element in connected_elements:
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)


class DrawSystemArrows(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.draw_system_arrows"
    bl_label = "Draw System Arrows"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and tool.Ifc.get()

    def _execute(self, context):
        sinks = []
        sources = []

        for obj in bpy.context.selected_objects:
            if not tool.Blender.get_ifc_definition_id(obj):
                continue

            element = tool.Ifc.get_entity(obj)
            sources_current = []
            sinks_current = []

            for port in tool.System.get_ports(element):
                local_placement = ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement)
                m = self.get_absolute_matrix(local_placement)
                if port.FlowDirection == "SOURCE":
                    sources_current.append(m)
                elif port.FlowDirection == "SINK":
                    sinks_current.append(m)
                else:
                    sources_current.append(m)
                    sinks_current.append(m)

                if sinks_current or sources_current:
                    sinks.append(sinks_current)
                    sources.append(sources_current)

        if not sinks:
            self.report({"INFO"}, "No sinks/sources found for selected objects.")
            return {"FINISHED"}

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        curve = bpy.data.objects.new("System Arrows", bpy.data.curves.new("System Arrows", "CURVE"))
        curve.data.dimensions = "3D"
        curve.show_in_front = True
        context.scene.collection.objects.link(curve)

        for i in range(len(sinks)):
            for sink in sinks[i]:
                for source in sources[i]:
                    polyline = curve.data.splines.new("POLY")
                    polyline.points.add(1)
                    polyline.points[0].co = (Matrix(sink).translation * unit_scale).to_4d()
                    polyline.points[1].co = (Matrix(source).translation * unit_scale).to_4d()
        tool.Blender.select_and_activate_single_object(context, curve)

    def get_absolute_matrix(self, matrix):
        props = tool.Georeference.get_georeference_props()
        if props.has_blender_offset:
            matrix = np.array(
                ifcopenshell.util.geolocation.global2local(
                    matrix,
                    float(props.blender_offset_x),
                    float(props.blender_offset_y),
                    float(props.blender_offset_z),
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )
            )
        return matrix


class ConfirmQuickFavoriteOperator(bpy.types.Operator):
    bl_idname = "bim.confirm_quick_favorite_operator"
    bl_label = "Confirm Operator"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    if TYPE_CHECKING:
        index: int

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Misc.get_misc_props()
        fav = props.quick_favorites[self.index]
        rna = fav.get_searched_operator()

        if rna is None:
            self.report({"INFO"}, "No operator entered for search.")
            return {"CANCELLED"}

        fav.operator_id = tool.Blender.operator_idname_to_py(rna.identifier)
        fav.label = rna.name
        fav.properties.clear()
        has_skipped = False
        for p in rna.properties:
            # skip silently, e.g. `rna_type` is a PointerProperty
            if isinstance(p, bpy.types.PointerProperty):
                continue
            if isinstance(p, (bpy.types.FloatProperty, bpy.types.BoolProperty, bpy.types.IntProperty)) and p.is_array:
                print(f"Array property '{p.identifier}' is not supported, skipping.")
                has_skipped = True
                continue
            item = fav.properties.add()
            item.name = p.identifier
            item.display_name = p.name
            if isinstance(p, bpy.types.FloatProperty):
                item.value_prop = "float_value"
                item.float_value = p.default
            elif isinstance(p, bpy.types.BoolProperty):
                item.value_prop = "bool_value"
                item.bool_value = p.default
            elif isinstance(p, bpy.types.IntProperty):
                item.value_prop = "int_value"
                item.int_value = p.default
            elif isinstance(p, bpy.types.EnumProperty):
                item.value_prop = "enum_value"
                item.set_enum_items([(e.identifier, e.name, e.description) for e in p.enum_items])
                item.enum_value = p.default
            elif isinstance(p, bpy.types.StringProperty):
                item.value_prop = "string_value"
                item.string_value = p.default
            else:
                print(f"Unhandled property type {type(p).__name__} for '{p.identifier}', skipping.")
                has_skipped = True
        if has_skipped:
            self.report({"WARNING"}, "Some properties were skipped, see the system console for details.")
        return {"FINISHED"}


class ImportQuickFavorites(bpy.types.Operator):
    bl_idname = "bim.import_quick_favorites"
    bl_label = "Import Quick Favorites"
    bl_description = "Import operators from Blender's Quick Favorites menu, including their configured properties"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version[:2] not in tool.Misc.QuickFavorites.OFFSET_USER_MENUS:
            cls.poll_message_set(f"Blender version {bpy.app.version_string} is not supported.")
            return False
        return True

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Misc.get_misc_props()
        props.quick_favorites.clear()

        has_missing_props = False
        for i, qf in enumerate(tool.Misc.QuickFavorites.get_quick_favorites()):
            fav = props.quick_favorites.add()
            fav.label = qf.ui_name
            fav.search = qf.op_idname_py
            bpy.ops.bim.confirm_quick_favorite_operator(index=i)
            fav.label = qf.ui_name or fav.label

            for prop in fav.properties:
                prop.is_active = prop.name in qf.props

            for key, value in qf.props.items():
                if key not in fav.properties:
                    print(f"Property '{key}' not found in operator '{qf.op_idname_py}'.")
                    has_missing_props = True
                    continue
                item = fav.properties[key]
                item.set_value(value)

        if has_missing_props:
            self.report(
                {"WARNING"}, "Some properties were not found during import, see the system console for details."
            )
        return {"FINISHED"}


class MoveQuickFavoritesItem(bpy.types.Operator):
    bl_idname = "bim.move_quick_favorites_item"
    bl_label = "Move Quick Favorites Item"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()
    direction: bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")])

    if TYPE_CHECKING:
        index: int
        direction: Literal["UP", "DOWN"]

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Misc.get_misc_props()
        total = len(props.quick_favorites)
        new_index = self.index - 1 if self.direction == "UP" else self.index + 1
        if 0 <= new_index < total:
            props.quick_favorites.move(self.index, new_index)
        return {"FINISHED"}


class RemoveQuickFavoritesItem(bpy.types.Operator):
    bl_idname = "bim.remove_quick_favorites_item"
    bl_label = "Remove Quick Favorites Item"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    if TYPE_CHECKING:
        index: int

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Misc.get_misc_props()
        props.quick_favorites.remove(self.index)
        return {"FINISHED"}


class AddQuickFavoritesItem(bpy.types.Operator):
    bl_idname = "bim.add_quick_favorites_item"
    bl_label = "Add Quick Favorites Item"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Misc.get_misc_props()
        fav = props.quick_favorites.add()
        fav.search = "bim.select_query_elements"
        index = len(props.quick_favorites) - 1
        bpy.ops.bim.confirm_quick_favorite_operator(index=index)
        fav.properties["query"].string_value = "IfcWall"
        return {"FINISHED"}


class IfcSverchokUseBonsaiFile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.ifcsverchok_use_bonsai_file"
    bl_label = "Use Bonsai IFC File"
    bl_description = "Apply current IfcSverchok tree to the active Bonsai file."
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        import sverchok.node_tree

        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            self.report({"ERROR"}, "No active IFC file.")
            return {"CANCELLED"}

        space_data = context.space_data
        assert isinstance(space_data, bpy.types.SpaceNodeEditor)
        node_tree = space_data.node_tree
        assert isinstance(node_tree, sverchok.node_tree.SverchCustomTree)
        tool.Model.run_ifcsverchok_graph_on_bonsai_file(node_tree)
