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

import bpy
import gpu
import json
import bmesh
import shapely
import logging
import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.geometry
import ifcopenshell.api.feature
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.element
import ifcopenshell.util.shape_builder
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.core.geometry
import bonsai.bim.import_ifc as import_ifc
from collections import defaultdict
from math import pi, radians
from mathutils import Vector, Matrix
from bpy.types import Operator
from bpy.types import SpaceView3D
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from gpu_extras.batch import batch_for_shader
from typing import Union, Optional, Any, cast, Sequence


class FilledOpeningGenerator:
    def generate(
        self,
        filling_obj: bpy.types.Object,
        voided_obj: bpy.types.Object,
        target: Optional[Vector] = None,
    ) -> Union[None, str]:
        """
        :param target: Target opening position. If ommited, cursor position is used.
        :return: None if there was no errors, otherwise returns a string with error message.
        """
        props = tool.Model.get_model_props()
        opening_thickness_si = 0.0

        filling = tool.Ifc.get_entity(filling_obj)
        element = tool.Ifc.get_entity(voided_obj)

        assert filling and element
        if filling.FillsVoids:
            ifcopenshell.api.run(
                "feature.remove_feature", tool.Ifc.get(), feature=filling.FillsVoids[0].RelatingOpeningElement
            )

        if target is None:
            should_set_z_level = True
            target = bpy.context.scene.cursor.location.copy()
        else:
            should_set_z_level = False

        # Sometimes, the voided_obj may be an aggregate, which won't have any representation.
        if voided_obj.data:
            raycast = voided_obj.closest_point_on_mesh(voided_obj.matrix_world.inverted() @ target, distance=0.01)
            if not raycast[0]:
                target = filling_obj.matrix_world.translation.copy()
                raycast = voided_obj.closest_point_on_mesh(voided_obj.matrix_world.inverted() @ target, distance=0.5)
                if not raycast[0]:
                    return "TARGET is too far away from the voided object's mesh."

            # In this prototype, we assume openings are only added to axis-based elements
            layers = tool.Model.get_material_layer_parameters(element)
            if layers["layer_set_direction"] == "AXIS2":
                opening_thickness_si = layers["thickness"] * 2
                axis = tool.Model.get_wall_axis(voided_obj, layers=layers)["base"]
                new_matrix = voided_obj.matrix_world.copy()
                point_on_axis = tool.Cad.point_on_edge(target, axis)
                new_matrix.translation.x = point_on_axis.x
                new_matrix.translation.y = point_on_axis.y

                if should_set_z_level:
                    if filling.is_a("IfcDoor"):
                        new_matrix.translation.z = voided_obj.matrix_world.translation.z + props.rl1
                    else:
                        new_matrix.translation.z = voided_obj.matrix_world.translation.z + props.rl2
                else:
                    new_matrix.translation.z = filling_obj.matrix_world.copy().translation.z
            elif layers["layer_set_direction"] == "AXIS3":
                new_matrix = voided_obj.matrix_world.copy()
                local_position_on_voided_obj = raycast[1]
                # Equivalent to "side Z" for a wall axis, so that stuff like skylights appear on the top.
                local_position_on_voided_obj.z = layers["offset"] + layers["thickness"]
                new_matrix.translation.xyz = voided_obj.matrix_world @ local_position_on_voided_obj
                rotation_matrix = Matrix.Rotation(radians(-90), 4, "X")
                new_matrix @= rotation_matrix
            else:
                assert False, f"Unexpected layer set direction: {layers['layer_set_direction']}"

            filling_obj.matrix_world = new_matrix
            bpy.context.view_layer.update()

        if tool.Ifc.is_moved(voided_obj):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=voided_obj)

        existing_opening_occurrence = self.get_existing_opening_occurrence_if_any(filling)

        opening = ifcopenshell.api.run(
            "root.create_entity",
            tool.Ifc.get(),
            ifc_class="IfcOpeningElement",
            predefined_type="OPENING",
            name="Opening",
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement",
            tool.Ifc.get(),
            product=opening,
            matrix=np.array(filling_obj.matrix_world),
            is_si=True,
        )

        if existing_opening_occurrence:
            representation = ifcopenshell.util.representation.get_representation(
                existing_opening_occurrence, "Model", "Body", "MODEL_VIEW"
            )
            assert representation
            representation = ifcopenshell.util.representation.resolve_representation(representation)
        else:
            representation = self.generate_opening_from_filling(
                filling, filling_obj, opening_thickness_si=opening_thickness_si
            )

        mapped_representation = ifcopenshell.api.run(
            "geometry.map_representation", tool.Ifc.get(), representation=representation
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", tool.Ifc.get(), product=opening, representation=mapped_representation
        )

        ifcopenshell.api.run("feature.add_feature", tool.Ifc.get(), feature=opening, element=element)
        ifcopenshell.api.run("feature.add_filling", tool.Ifc.get(), opening=opening, element=filling)

        voided_objs = [voided_obj]
        # Openings affect all subelements of an aggregate
        for subelement in tool.Aggregate.get_parts_recursively(element):
            subobj = tool.Ifc.get_object(subelement)
            if subobj:
                voided_objs.append(subobj)

        for voided_obj in voided_objs:
            if voided_obj.data:
                voided_element = tool.Ifc.get_entity(voided_obj)
                assert voided_element
                context = tool.Geometry.get_active_representation_context(voided_obj)
                representation = tool.Geometry.get_representation_by_context(voided_element, context)
                assert representation

                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=voided_obj,
                    representation=representation,
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
                )

    def regenerate_from_type(self, usecase_path: str, ifc_file: ifcopenshell.file, settings: dict[str, Any]) -> None:
        relating_type = settings["relating_type"]

        for related_object in settings["related_objects"]:
            self._regenerate_from_type(related_object)

    def _regenerate_from_type(self, related_object: ifcopenshell.entity_instance) -> None:
        filling = related_object
        if not getattr(filling, "FillsVoids", None):
            return

        opening = filling.FillsVoids[0].RelatingOpeningElement
        voided_element = opening.VoidsElements[0].RelatingBuildingElement

        opening_rep = ifcopenshell.util.representation.get_representation(opening, "Model", "Body", "MODEL_VIEW")
        ifcopenshell.api.run(
            "geometry.unassign_representation", tool.Ifc.get(), product=opening, representation=opening_rep
        )
        ifcopenshell.api.run("geometry.remove_representation", tool.Ifc.get(), representation=opening_rep)

        existing_opening_occurrence = self.get_existing_opening_occurrence_if_any(filling)

        if existing_opening_occurrence:
            representation = ifcopenshell.util.representation.get_representation(
                existing_opening_occurrence, "Model", "Body", "MODEL_VIEW"
            )
            representation = ifcopenshell.util.representation.resolve_representation(representation)
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", tool.Ifc.get(), representation=representation
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=opening, representation=mapped_representation
            )
        else:
            opening_obj = tool.Ifc.get_object(opening)
            if opening_obj:
                tool.Ifc.unlink(element=opening)
                tool.Blender.remove_data_blocks([opening_obj], remove_unused_data=True)

            filling_obj = tool.Ifc.get_object(filling)
            representation = self.generate_opening_from_filling(filling, filling_obj)
            mapped_representation = ifcopenshell.api.run(
                "geometry.map_representation", tool.Ifc.get(), representation=representation
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=opening, representation=mapped_representation
            )

        # update voided object representation or all it's parts if it's an aggregate
        voided_elements = ifcopenshell.util.element.get_parts(voided_element) or [voided_element]
        for voided_element in voided_elements:
            voided_obj = tool.Ifc.get_object(voided_element)
            representation = tool.Geometry.get_active_representation(voided_obj)
            if not representation:
                continue
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=voided_obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )

    def generate_opening_from_filling(
        self,
        filling: ifcopenshell.entity_instance,
        filling_obj: bpy.types.Object,
        opening_thickness_si: float = 0.0,
    ) -> ifcopenshell.entity_instance:
        # Since openings are reused later, we give a default thickness of 1.2m
        # which should cover the majority of curved, or super thick walls.
        thickness = max(1.2, opening_thickness_si)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        shape_builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())

        profile = None
        filling_type = ifcopenshell.util.element.get_type(filling)
        if filling_type:
            profile = ifcopenshell.util.representation.get_representation(
                filling_type, "Model", "Profile", "ELEVATION_VIEW"
            )
            filling_obj = tool.Ifc.get_object(filling_type)
        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        assert context

        if profile:
            profile = ifcopenshell.util.representation.resolve_representation(profile)

            def get_curve_2d_from_3d(profile: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
                if len(profile.Items) == 1:
                    curve_3d = profile.Items[0]
                    if tool.Ifc.get_schema() == "IFC2X3":
                        coords = [Vector(p).xz for p in shape_builder.get_polyline_coords(curve_3d)]
                        return shape_builder.polyline(coords, closed=True)
                    # using different algorithm to keep arc segments possible in the future
                    ifc_segments = [shape_builder.deep_copy(s) for s in curve_3d.Segments]
                    ifc_points = tool.Ifc.get().createIfcCartesianPointList2D(
                        [Vector(p).xz for p in curve_3d.Points.CoordList]
                    )
                    return tool.Ifc.get().createIfcIndexedPolyCurve(Points=ifc_points, Segments=ifc_segments)

                settings = ifcopenshell.geom.settings()
                settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
                geometry = ifcopenshell.geom.create_shape(settings, profile)
                verts = ifcopenshell.util.shape.get_vertices(geometry)
                # [0, 2] represents X and Z ordinates
                verts = [(np.around(v[[0, 2]], decimals=3) / unit_scale).tolist() for v in verts]
                edges = ifcopenshell.util.shape.get_edges(geometry)

                boundary_lines = [shapely.LineString([verts[v] for v in e]) for e in edges]
                unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
                closed_polygons = shapely.polygonize(boundary_lines)
                polygon = max(closed_polygons.geoms, key=lambda polygon: polygon.area)
                return shape_builder.polyline(list(polygon.exterior.coords))

            extrusion = shape_builder.extrude(
                get_curve_2d_from_3d(profile),
                magnitude=thickness / unit_scale,
                position=Vector([0.0, -thickness * 0.5 / unit_scale, 0.0]),
                **shape_builder.extrude_kwargs("Y"),
            )
            return shape_builder.get_representation(context, [extrusion])

        if (
            filling_rep := tool.Geometry.get_active_representation(filling_obj)
        ) and filling_rep.ContextOfItems == context:
            x, y, z = filling_obj.dimensions
        else:
            # The filling_obj's mesh data is not the body geometry.
            settings = ifcopenshell.geom.settings()
            filling_element = tool.Ifc.get_entity(filling_obj)
            filling_body = ifcopenshell.util.representation.get_representation(filling_element, context)
            filling_geometry = ifcopenshell.geom.create_shape(settings, filling_body)
            x = ifcopenshell.util.shape.get_x(filling_geometry)
            y = ifcopenshell.util.shape.get_y(filling_geometry)
            z = ifcopenshell.util.shape.get_z(filling_geometry)
        opening_position = Vector([0.0, -thickness * 0.5 / unit_scale, 0.0])
        opening_size = Vector([x, z]) / unit_scale

        # Windows and doors can have a casing that overlaps the wall
        # but shouldn't affect the size of the opening.
        # So we shouldn't use object dimensions in that case. More: #2784
        # Just keeping it for windows and doors for now to be safe
        has_width_attribute, has_height_attribute = False, False
        if filling.is_a() in ["IfcWindow", "IfcDoor"]:
            if filling.OverallWidth:
                opening_size.x = filling.OverallWidth
                has_width_attribute = True
            if filling.OverallHeight:
                opening_size.y = filling.OverallHeight
                has_height_attribute = True

        # making sure if min_x or min_z != 0 to shift the opening accordingly
        # to prevent something like #2784
        if not has_width_attribute:
            opening_position.x = min(v[0] for v in filling_obj.bound_box)

        if not has_height_attribute:
            opening_position.z = min(v[2] for v in filling_obj.bound_box)

        extrusion = shape_builder.extrude(
            shape_builder.rectangle(size=opening_size),
            magnitude=thickness / unit_scale,
            position=opening_position,
            **shape_builder.extrude_kwargs("Y"),
        )

        return shape_builder.get_representation(context, [extrusion])

    def has_visible_openings(self, element):
        for opening in [r.RelatedOpeningElement for r in tool.Geometry.get_openings(element)]:
            if tool.Ifc.get_object(opening):
                return True
        return False

    def get_existing_opening_occurrence_if_any(
        self, filling: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        filling_type = ifcopenshell.util.element.get_type(filling)
        if filling_type:
            filling_occurrences = ifcopenshell.util.element.get_types(filling_type)
            for filling_occurrence in filling_occurrences:
                if filling_occurrence != filling and filling_occurrence.FillsVoids:
                    return filling_occurrence.FillsVoids[0].RelatingOpeningElement


class RecalculateFill(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_fill"
    bl_label = "Recalculate Fill"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.FillsVoids:
                continue
            openings = [r.RelatingOpeningElement for r in element.FillsVoids or []]
            building_elements = []
            for opening in openings:
                building_elements.extend([r.RelatingBuildingElement for r in opening.VoidsElements or []])
            for building_element in building_elements:
                building_obj = tool.Ifc.get_object(building_element)
                if tool.Ifc.is_moved(building_obj):
                    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=building_obj)
            for opening in openings:
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                ifcopenshell.api.run(
                    "geometry.edit_object_placement", tool.Ifc.get(), product=opening, matrix=obj.matrix_world
                )

            decomposed_building_elements = set()
            for building_element in building_elements:
                decomposed_building_elements.add(building_element)
                decomposed_building_elements.update(ifcopenshell.util.element.get_decomposition(building_element))

            for building_element in decomposed_building_elements:
                building_obj = tool.Ifc.get_object(building_element)
                if building_obj and building_obj.data:
                    representation = tool.Geometry.get_active_representation(building_obj)
                    if representation:
                        bonsai.core.geometry.switch_representation(
                            tool.Ifc,
                            tool.Geometry,
                            obj=building_obj,
                            representation=representation,
                            should_reload=True,
                            is_global=True,
                            should_sync_changes_first=False,
                        )
        return {"FINISHED"}


class FlipFill(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.flip_fill"
    bl_label = "Flip Fill"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.FillsVoids:
                continue
            tool.Geometry.flip_object(obj, "XY")
        return {"FINISHED"}


class AddBoolean(Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_boolean"
    bl_label = "Add Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Applies a boolean to the selected IFC object using the other selected blender object as a void"

    @classmethod
    def poll(cls, context):
        if not len(context.selected_objects) >= 2:
            cls.poll_message_set("At least 2 objects need to be selected.")
            return False
        return True

    def _execute(self, context):
        first_obj = tool.Blender.get_active_object()
        if not first_obj or not tool.Geometry.is_boolean_operand(first_obj):
            self.report({"INFO"}, "At least two valid objects must be selected to add a boolean.")
            return {"CANCELLED"}
        second_objs = [
            o for o in tool.Blender.get_selected_objects() if o != first_obj and tool.Geometry.is_boolean_operand(o)
        ]
        if not second_objs:
            self.report({"INFO"}, "At least two representation items must be selected to add a boolean.")
            return {"CANCELLED"}

        props = tool.Feature.get_boolean_props()

        first_item = tool.Geometry.get_active_representation(first_obj)
        assert first_item
        second_items = [
            representation for o in second_objs if (representation := tool.Geometry.get_active_representation(o))
        ]
        booleans = ifcopenshell.api.geometry.add_boolean(tool.Ifc.get(), first_item, second_items, props.operator)

        rep_obj = tool.Geometry.get_geometry_props().representation_obj
        rep_element = tool.Ifc.get_entity(rep_obj)
        tool.Model.mark_manual_booleans(rep_element, booleans)
        tool.Geometry.reload_representation(rep_obj)
        if props.is_editing:
            bpy.ops.bim.enable_editing_booleans()
        tool.Root.reload_item_decorator()


class ShowOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.show_openings"
    bl_label = "Show"
    bl_description = "Show Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        objs = list(context.selected_objects)
        # If several parts of an aggregation are selected, the aggregate openings may be queried more than once
        objects_element_map: set[tuple[bpy.types.Object, ifcopenshell.entity_instance]] = set()
        while objs:
            obj = objs.pop(0)
            element = tool.Ifc.get_entity(obj)
            if element:
                if getattr(element, "Decomposes", None):
                    # Select aggregate recursively
                    if element.Decomposes and (aggregate := element.Decomposes[0].RelatingObject):
                        aggregate_obj = tool.Ifc.get_object(aggregate)
                        assert isinstance(aggregate_obj, bpy.types.Object)
                        objs.append(aggregate_obj)
                objects_element_map.add((obj, element))

        for obj, element in objects_element_map:
            self.show_object_openings(obj, element)
        DecorationsHandler.install(bpy.context)
        bpy.ops.bim.update_openings_focus()
        return {"FINISHED"}

    def show_object_openings(self, obj: bpy.types.Object, element: ifcopenshell.entity_instance) -> None:
        openings_elements = [rel.RelatedOpeningElement for rel in tool.Geometry.get_openings(element)]
        if not openings_elements:
            return
        if tool.Ifc.is_moved(obj):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        openings_elements_to_load = [o for o in openings_elements if not tool.Ifc.get_object(o)]
        openings_objects = tool.Model.load_openings(openings_elements_to_load)
        for obj in openings_objects:
            tool.Root.add_tracked_opening(obj, "OPENING")


class UpdateOpeningsFocus(Operator):
    bl_idname = "bim.update_openings_focus"
    bl_label = "Update Openings Focus"
    bl_description = "Show objects that are not part of the object or its openings as transparent"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        preferences = tool.Blender.get_addon_preferences()
        if preferences.opening_focus_opacity == 100:
            return {"FINISHED"}
        openings: set[bpy.types.Object] = set()
        building_objects: set[bpy.types.Object] = set()
        props = tool.Model.get_model_props()
        for opening in props.openings:
            if opening.obj:
                openings.add(opening.obj)
                opening_element = tool.Ifc.get_entity(opening.obj)
                assert opening_element
                building_element = opening_element.VoidsElements[0].RelatingBuildingElement
                building_obj = tool.Ifc.get_object(building_element)
                assert isinstance(building_obj, bpy.types.Object)
                building_objects.add(building_obj)

        for obj in context.scene.objects:
            obj.color = [
                obj.color[0],
                obj.color[1],
                obj.color[2],
                (
                    1
                    if not props.openings
                    or not building_objects
                    or obj in openings
                    or obj in building_objects
                    or obj in context.selected_objects
                    else preferences.opening_focus_opacity / 100
                ),
            ]
        return {"FINISHED"}


def hide_openings(context: bpy.types.Context, objects: Sequence[bpy.types.Object]) -> None:
    objects_to_remove = set()
    props = tool.Model.get_model_props()
    for opening_prop in props.openings:
        opening_obj = opening_prop.obj
        if not opening_obj:
            continue
        opening_element = tool.Ifc.get_entity(opening_obj)
        if opening_element:
            if not opening_element.is_a("IfcOpeningElement"):
                # This opening has been assigned to another ifc class. Remove it from the openings pool. See #3854
                opening_prop.obj = None
                continue
            building_element = opening_element.VoidsElements[0].RelatingBuildingElement
            if building_element:
                building_obj = tool.Ifc.get_object(building_element)
                if building_obj in objects:
                    tool.Ifc.unlink(element=opening_element)
                    objects_to_remove.add(opening_obj)
        if opening_obj in objects:
            objects_to_remove.add(opening_obj)

    tool.Blender.remove_data_blocks(objects_to_remove, remove_unused_data=True)
    tool.Model.purge_scene_openings()
    bpy.ops.bim.update_openings_focus()


class HideAllOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_all_openings"
    bl_label = "Hide All Openings"
    bl_description = "Hide every single opening"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        hide_openings(context, context.scene.objects[:])
        return {"FINISHED"}


class HideOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_openings"
    bl_label = "Hide"
    bl_description = "Hide Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        hide_openings(context, context.selected_objects[:])
        return {"FINISHED"}


class EditOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_openings"
    bl_label = "Edit"
    bl_description = "Edit Openings"
    bl_options = {"REGISTER", "UNDO"}
    apply_all: bpy.props.BoolProperty(default=False)

    def _execute(self, context):
        building_objs, opening_elements = self.get_buildings_and_openings(context)
        self.edit_openings(building_objs, opening_elements)

        tool.Model.purge_scene_openings()
        tool.Model.reload_body_representation(building_objs)
        bpy.ops.bim.update_openings_focus()
        return {"FINISHED"}

    def get_buildings_and_openings(
        self, context: bpy.types.Context
    ) -> tuple[set[bpy.types.Object], set[ifcopenshell.entity_instance]]:
        props = tool.Model.get_model_props()
        building_objs: set[bpy.types.Object] = set()
        opening_elements: set[ifcopenshell.entity_instance] = set()
        objects_to_remove = set()
        if self.apply_all:
            for opening_prop in props.openings:
                opening_obj = opening_prop.obj
                if opening_obj is None:
                    continue
                opening_element = tool.Ifc.get_entity(opening_obj)
                if opening_element is None:
                    objects_to_remove.add(opening_obj)
                    continue
                opening_elements.add(opening_element)
                building_element = opening_element.VoidsElements[0].RelatingBuildingElement
                building_objs.add(tool.Ifc.get_object(building_element))
        else:
            for obj in context.selected_objects:
                element = tool.Ifc.get_entity(obj)
                if element.is_a("IfcOpeningElement"):
                    opening_element = element
                    opening_elements.add(opening_element)
                    if opening_element.VoidsElements:
                        building_element = opening_element.VoidsElements[0].RelatingBuildingElement
                        building_obj = tool.Ifc.get_object(building_element)
                        if building_obj:
                            building_objs.add(building_obj)
                else:
                    for relation in tool.Geometry.get_openings(element):
                        opening_element = relation.RelatedOpeningElement
                        if tool.Ifc.get_object(opening_element):
                            opening_elements.add(opening_element)
                        building_objs.add(obj)
        tool.Blender.remove_data_blocks(objects_to_remove, remove_unused_data=True)
        return building_objs, opening_elements

    def edit_openings(
        self, building_objs: set[bpy.types.Object], opening_elements: set[ifcopenshell.entity_instance]
    ) -> None:
        props = tool.Geometry.get_geometry_props()
        objects_to_remove: set[bpy.types.Object] = set()
        for opening_element in opening_elements:
            opening_obj = tool.Ifc.get_object(opening_element)

            similar_openings = bonsai.core.geometry.get_similar_openings(tool.Ifc, opening_element)
            similar_openings_building_objs = bonsai.core.geometry.get_similar_openings_building_objs(
                tool.Ifc, similar_openings
            )
            building_objs.update(similar_openings_building_objs)

            if opening_obj:
                if tool.Ifc.is_edited(opening_obj):
                    tool.Geometry.run_geometry_update_representation(obj=opening_obj)
                    bonsai.core.geometry.edit_similar_opening_placement(
                        tool.Geometry, opening_element, similar_openings
                    )
                elif tool.Ifc.is_moved(opening_obj):
                    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=opening_obj)
                    bonsai.core.geometry.edit_similar_opening_placement(
                        tool.Geometry, opening_element, similar_openings
                    )

                building_objs.update(
                    self.get_all_building_objects_of_similar_openings(opening_element)
                )  # NB this has nothing to do with clone similar_opening
                tool.Ifc.unlink(element=opening_element)
                if props.representation_obj == opening_obj:
                    props.representation_obj = None
                objects_to_remove.add(opening_obj)
        tool.Blender.remove_data_blocks(objects_to_remove, remove_unused_data=True)

    def get_all_building_objects_of_similar_openings(self, opening):
        if not opening.is_a("IfcOpeningElement") or not opening.HasFillings:
            return []
        results = set()
        for rel in opening.HasFillings:
            filling_type = ifcopenshell.util.element.get_type(rel.RelatedBuildingElement)
            if not filling_type:
                continue
            for occurrence in ifcopenshell.util.element.get_types(filling_type):
                for rel2 in occurrence.FillsVoids:
                    for rel3 in rel2.RelatingOpeningElement.VoidsElements:
                        obj = tool.Ifc.get_object(rel3.RelatingBuildingElement)
                        if obj:
                            results.add(obj)
        return results


class CloneOpening(Operator, tool.Ifc.Operator):
    bl_idname = "bim.clone_opening"
    bl_label = "Clone Opening"
    bl_description = "Clone the active Opening object and assign to the selected Element"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) != 2:
            cls.poll_message_set("Exactly 2 objects must be selected.")
            return False
        return True

    def _execute(self, context):
        # NOTE: Operator displayed in UI only with IfcOpeningElement being active.
        ifc_file = tool.Ifc.get()
        objects = bpy.context.selected_objects
        opening_obj = context.active_object
        assert opening_obj
        opening = tool.Ifc.get_entity(opening_obj)
        assert opening and opening.is_a("IfcOpeningElement")

        voided_obj = next(o for o in objects if o != opening_obj)
        voided_element = tool.Ifc.get_entity(voided_obj)
        assert voided_element

        opening_placement = opening.ObjectPlacement
        opening_representation = opening.Representation

        new_opening = ifcopenshell.api.run("root.create_entity", tool.Ifc.get(), ifc_class="IfcOpeningElement")
        new_opening.Representation = opening_representation

        ifcopenshell.api.feature.add_feature(ifc_file, feature=new_opening, element=voided_element)
        new_opening.ObjectPlacement = opening_placement

        # Update affected representations.
        elements_to_update = tool.Aggregate.get_parts_recursively(voided_element)
        for element in elements_to_update:
            obj = tool.Ifc.get_object(element)
            if not isinstance(obj, bpy.types.Object) or not isinstance(obj.data, bpy.types.Mesh):
                continue
            representation = tool.Geometry.get_active_representation(obj)
            assert representation
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )

        return {"FINISHED"}


class PurgeUnusedOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.purge_unused_openings"
    bl_label = "Purge Unused Openings"
    bl_description = "Purge Openings that do not intersect with their related building element"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        poll = any(
            tool.Geometry.has_openings(element)
            for element in [tool.Ifc.get_entity(obj) for obj in context.selected_objects]
            if element
        )
        if not poll:
            cls.poll_message_set("No objects with openings selected.")
            return False
        return True

    def _execute(self, context):
        bpy.ops.bim.show_openings()
        objects = context.selected_objects[:]
        [o.select_set(False) for o in objects]
        active_object = context.active_object
        purged = 0
        for obj in objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not tool.Geometry.has_openings(element):
                continue
            obj_bvh_tree = tool.Geometry.get_bvh_tree(obj)
            for opening_rel in tool.Geometry.get_openings(element):
                opening_elt = opening_rel.RelatedOpeningElement
                opening_obj = tool.Ifc.get_object(opening_elt)
                opening_bvh_tree = tool.Geometry.get_bvh_tree(opening_obj)
                if not opening_bvh_tree.overlap(obj_bvh_tree):
                    opening_obj.select_set(True)
                    purged += 1
        if context.selected_objects:
            bpy.ops.bim.override_object_delete(is_batch=False)
        bpy.ops.bim.edit_openings(apply_all=True)
        [o.select_set(True) for o in objects]
        context.view_layer.objects.active = active_object
        self.report({"INFO"}, f"{purged} unused openings were purged.")
        return {"FINISHED"}


class RemoveBoolean(Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_boolean"
    bl_label = "Remove Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Removes the actively selected boolean"

    @classmethod
    def poll(cls, context):
        props = tool.Feature.get_boolean_props()
        return props.active_boolean

    def _execute(self, context):
        props = tool.Feature.get_boolean_props()
        ifcopenshell.api.geometry.remove_boolean(
            tool.Ifc.get(), tool.Ifc.get().by_id(props.active_boolean.ifc_definition_id)
        )
        bpy.ops.bim.enable_editing_booleans()
        rep_obj = tool.Geometry.get_geometry_props().representation_obj
        assert rep_obj
        tool.Geometry.reload_representation(rep_obj)
        tool.Root.reload_item_decorator()


class SelectBoolean(Operator):
    bl_idname = "bim.select_boolean"
    bl_label = "Select Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Selects operands of the active boolean\nSHIFT-CLICK to select all operands recursively"
    is_recursive: bpy.props.BoolProperty(name="Is Recursive", default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        props = tool.Feature.get_boolean_props()
        return props.active_boolean

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.shift:
            self.is_recursive = True
        return self.execute(context)

    def execute(self, context):
        props = tool.Feature.get_boolean_props()
        queue = [tool.Ifc.get().by_id(props.active_boolean.ifc_definition_id)]
        items = {i.ifc_definition_id: i.obj for i in tool.Geometry.get_geometry_props().item_objs}
        while queue:
            item = queue.pop()
            if item.is_a("IfcBooleanResult"):
                if self.is_recursive:
                    queue.append(item.FirstOperand)
                    queue.append(item.SecondOperand)
                else:
                    if obj := items.get(item.FirstOperand.id()):
                        tool.Blender.select_object(obj)
                    if obj := items.get(item.SecondOperand.id()):
                        tool.Blender.select_object(obj)
            elif obj := items.get(item.id()):
                tool.Blender.select_object(obj)
        return {"FINISHED"}


# TODO: merge with ProfileDecorator?
class DecorationsHandler:
    installed = None

    @classmethod
    def install(cls, context):
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_VIEW")

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, "WINDOW")
        except ValueError:
            pass
        cls.installed = None

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def __call__(self, context):
        props = tool.Model.get_model_props()
        if not props.openings:
            return
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special

        def transparent_color(color, alpha=0.1):
            color = [i for i in color]
            color[3] = alpha
            return color

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        gprops = tool.Geometry.get_geometry_props()
        for opening in props.openings:
            obj = opening.obj
            if gprops.representation_obj == obj:
                # We are editing the representation of the opening :
                for item in gprops.item_objs:
                    if item.obj.mode == "EDIT":
                        obj = item.obj
                        break
            if not obj:
                continue

            self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
            self.line_shader.bind()  # required to be able to change uniforms of the shader
            # POLYLINE_UNIFORM_COLOR specific uniforms
            self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
            self.line_shader.uniform_float("lineWidth", 2.0)

            # general shader
            self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

            verts = []
            selected_edges = []
            unselected_edges = []
            selected_vertices = []
            unselected_vertices = []

            if obj.mode == "EDIT":
                bm = bmesh.from_edit_mesh(obj.data)

                for vertex in bm.verts:
                    co = tuple(obj.matrix_world @ vertex.co)
                    verts.append(co)
                    if vertex.hide:
                        continue

                    if vertex.select:
                        selected_vertices.append(co)
                    else:
                        unselected_vertices.append(co)

                for edge in bm.edges:
                    edge_indices = [v.index for v in edge.verts]
                    if edge.hide:
                        continue
                    if edge.select:
                        selected_edges.append(edge_indices)
                    else:
                        unselected_edges.append(edge_indices)

                self.draw_batch("LINES", verts, transparent_color(unselected_elements_color, 0.5), unselected_edges)
                self.draw_batch("LINES", verts, selected_elements_color, selected_edges)
                self.draw_batch("POINTS", unselected_vertices, unselected_elements_color)
                self.draw_batch("POINTS", selected_vertices, selected_elements_color)
            else:
                bm = bmesh.new()
                bm.from_mesh(obj.data)

                verts = [tuple(obj.matrix_world @ v.co) for v in bm.verts]
                if ios_edges_attribute := obj.data.attributes.get("ios_edges"):
                    edges = [e for i, e in enumerate(bm.edges) if ios_edges_attribute.data[i].value]
                else:
                    edges = bm.edges
                edges_indices = [tuple([v.index for v in e.verts]) for e in edges]

                color = selected_elements_color if obj in context.selected_objects else special_elements_color
                self.draw_batch("LINES", verts, color, edges_indices)

            obj.data.calc_loop_triangles()
            tris = [tuple(t.vertices) for t in obj.data.loop_triangles]
            self.draw_batch("TRIS", verts, transparent_color(special_elements_color), tris)

            if "HalfSpaceSolid" in obj.name:
                # Arrow shape
                verts = [
                    tuple(obj.matrix_world @ Vector((0, 0, 0))),
                    tuple(obj.matrix_world @ Vector((0, 0, 0.5))),
                    tuple(obj.matrix_world @ Vector((0.05, 0, 0.45))),
                    tuple(obj.matrix_world @ Vector((-0.05, 0, 0.45))),
                    tuple(obj.matrix_world @ Vector((0, 0.05, 0.45))),
                    tuple(obj.matrix_world @ Vector((0, -0.05, 0.45))),
                ]
                edges = [(0, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
                color = selected_elements_color if obj in context.selected_objects else special_elements_color
                self.draw_batch("LINES", verts, color, edges)

            if obj.mode != "EDIT":
                bm.free()
