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
from bonsai.bim.ifc import IfcStore
from math import pi, radians
from mathutils import Vector, Matrix
from bpy.types import Operator
from bpy.types import SpaceView3D
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from gpu_extras.batch import batch_for_shader
from typing import Union, Optional, Any, cast


class AddFilledOpening(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_filled_opening"
    bl_label = "Add Filled Opening"
    bl_options = {"REGISTER", "UNDO"}
    voided_obj: bpy.props.StringProperty()
    filling_obj: bpy.props.StringProperty()

    def _execute(self, context):
        FilledOpeningGenerator().generate(bpy.data.objects.get(self.filling_obj), bpy.data.objects.get(self.voided_obj))
        return {"FINISHED"}


class FilledOpeningGenerator:
    def generate(
        self,
        filling_obj: Union[bpy.types.Object, None],
        voided_obj: Union[bpy.types.Object, None],
        target: Optional[Vector] = None,
    ) -> None:
        props = bpy.context.scene.BIMModelProperties
        opening_thickness_si = 0.0

        filling = tool.Ifc.get_entity(filling_obj)
        element = tool.Ifc.get_entity(voided_obj)

        if not voided_obj or not filling_obj:
            return

        if filling.FillsVoids:
            ifcopenshell.api.run(
                "void.remove_opening", tool.Ifc.get(), opening=filling.FillsVoids[0].RelatingOpeningElement
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
                    return

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
                        new_matrix.translation.z = voided_obj.matrix_world.translation.z
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

        ifcopenshell.api.run("void.add_opening", tool.Ifc.get(), opening=opening, element=element)
        ifcopenshell.api.run("void.add_filling", tool.Ifc.get(), opening=opening, element=filling)

        voided_objs = [voided_obj]
        # Openings affect all subelements of an aggregate
        for subelement in ifcopenshell.util.element.get_decomposition(element):
            subobj = tool.Ifc.get_object(subelement)
            if subobj:
                voided_objs.append(subobj)

        for voided_obj in voided_objs:
            if voided_obj.data:
                voided_element = tool.Ifc.get_entity(voided_obj)
                context = tool.Geometry.get_active_representation_context(voided_obj)
                representation = tool.Geometry.get_representation_by_context(voided_element, context)

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
                bpy.data.objects.remove(opening_obj)

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
            if not voided_obj.data:
                continue
            representation = tool.Ifc.get().by_id(voided_obj.data.BIMMeshProperties.ifc_definition_id)
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

        if profile:
            profile = ifcopenshell.util.representation.resolve_representation(profile)

            def get_curve_2d_from_3d(profile):
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
        for opening in [r.RelatedOpeningElement for r in element.HasOpenings]:
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


class AddPotentialOpening(Operator, AddObjectHelper):
    bl_idname = "bim.add_potential_opening"
    bl_label = "Add Opening"
    bl_description = "Add an Opening object which can be applied on an Element"
    bl_options = {"REGISTER", "UNDO"}
    x: FloatProperty(name="X", default=0.5)
    y: FloatProperty(name="Y", default=0.5)
    z: FloatProperty(name="Z", default=0.5)

    def draw_settings(context, layout, tool):
        row = self.layout.row()
        row.prop(data=self, property="x", label="Size X")
        row = self.layout.row()
        row.prop(data=self, property="y")
        row = self.layout.row()
        row.prop(data=self, property="z")

    def execute(self, context):
        props = context.scene.BIMModelProperties

        new_matrix = None
        if context.selected_objects and context.active_object:
            new_matrix = context.active_object.matrix_world.copy()
            new_matrix.translation = context.scene.cursor.location

        x = self.x / 2
        y = self.y / 2
        z = self.z / 2
        verts = [
            Vector((-x, -y, -z)),
            Vector((-x, -y, z)),
            Vector((-x, y, -z)),
            Vector((-x, y, z)),
            Vector((x, -y, -z)),
            Vector((x, -y, z)),
            Vector((x, y, -z)),
            Vector((x, y, z)),
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
        mesh = bpy.data.meshes.new(name="Opening")
        mesh.from_pydata(verts, edges, faces)
        obj = object_data_add(context, mesh, operator=self)
        obj.name = "Opening"

        if new_matrix:
            obj.matrix_world = new_matrix

        tool.Model.clear_scene_openings()

        new = props.openings.add()
        new.obj = obj

        DecorationsHandler.install(context)
        return {"FINISHED"}


class AddPotentialHalfSpaceSolid(Operator, AddObjectHelper):
    bl_idname = "bim.add_potential_half_space_solid"
    bl_label = "Add Potential Half Space Solid"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMModelProperties
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, size=0.5)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        mesh = bpy.data.meshes.new(name="Dumb Opening")
        bm.to_mesh(mesh)
        bm.free()
        obj = object_data_add(context, mesh, operator=self)
        obj.name = "HalfSpaceSolid"

        tool.Model.clear_scene_openings()

        new = props.openings.add()
        new.obj = obj

        DecorationsHandler.install(context)
        return {"FINISHED"}


class AddBoolean(Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_boolean"
    bl_label = "Add Boolean"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Applies a boolean to the selected IFC object using the other selected blender object as a void"

    @classmethod
    def poll(cls, context):
        if not len(context.selected_objects) == 2:
            cls.poll_message_set("Exactly 2 objects need to be selected.")
            return False
        return True

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        obj1, obj2 = context.selected_objects
        element1 = tool.Ifc.get_entity(obj1)
        element2 = tool.Ifc.get_entity(obj2)
        if not (bool(element1) ^ bool(element2)):
            self.report({"INFO"}, "One of the selected objects should be blender object and another IFC object.")
            return {"FINISHED"}

        # element1 - IFC object, element2 - blender object.
        if element2 and not element1:
            obj1, obj2 = obj2, obj1
            element1, element2 = element2, element1

        representation = tool.Geometry.get_active_representation(obj1)
        if not representation:
            self.report({"INFO"}, "No representation found for the selected IFC object.")
            return {"FINISHED"}

        if not obj2.data or len(obj2.data.polygons) <= 4:  # It takes 4 faces to create a closed solid
            mesh_data = {"type": "IfcHalfSpaceSolid", "matrix": obj1.matrix_world.inverted() @ obj2.matrix_world}
        else:
            mesh_data = {"type": "Mesh", "blender_obj": obj1, "blender_void": obj2}

        booleans = ifcopenshell.api.run(
            "geometry.add_boolean", tool.Ifc.get(), representation=representation, operator="DIFFERENCE", **mesh_data
        )

        tool.Model.mark_manual_booleans(element1, booleans)
        tool.Model.clear_scene_openings()

        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj1,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

        bpy.data.objects.remove(obj2)
        return {"FINISHED"}


class ShowBooleans(Operator, tool.Ifc.Operator, AddObjectHelper):
    bl_idname = "bim.show_booleans"
    bl_label = "Show Booleans"
    bl_description = "Show active object booleans.\nCan be used to reset booleans positions"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.data
            and hasattr(obj.data, "BIMMeshProperties")
            and obj.data.BIMMeshProperties.ifc_definition_id
        )

    def _execute(self, context):
        obj = context.active_object
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        representation = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        booleans: list[ifcopenshell.entity_instance] = []
        for item in representation.Items:
            booleans.extend(self.get_booleans(item))

        props = bpy.context.scene.BIMModelProperties
        tool.Model.clear_scene_openings()

        existing_booleans = {
            boolean_obj.data.BIMMeshProperties.ifc_boolean_id: boolean_obj
            for opening in props.openings
            if (boolean_obj := opening.obj).data.BIMMeshProperties.obj == obj
        }

        for boolean in booleans:
            boolean_obj = None

            if boolean.is_a() == "IfcHalfSpaceSolid":
                surface = boolean.BaseSurface
                if surface.is_a("IfcPlane"):
                    boolean_obj = self.create_half_space_solid()
                    position = surface.Position
                    position = Matrix(ifcopenshell.util.placement.get_axis2placement(position).tolist())
                    position.translation *= unit_scale
                    boolean_obj.matrix_world = obj.matrix_world @ position
                else:
                    self.report(
                        {"INFO"},
                        f"Showing boolean using non-IfcPlane IfcSurface ({surface.is_a()}) is not supported.",
                    )
            else:
                settings = ifcopenshell.geom.settings()
                logger = logging.getLogger("ImportIFC")
                ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
                shape = ifcopenshell.geom.create_shape(settings, boolean)
                if shape:
                    ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
                    ifc_importer.file = tool.Ifc.get()
                    mesh = ifc_importer.create_mesh(boolean, shape)
                else:
                    mesh = None
                boolean_obj = object_data_add(bpy.context, mesh, operator=self)
                boolean_obj.name = "BooleanMesh"
                boolean_obj.matrix_world = obj.matrix_world

            if boolean_obj:
                boolean_id = boolean.id()
                # Remove existing boolean as it will be reloaded.
                if boolean_id in existing_booleans:
                    bpy.data.objects.remove(existing_booleans[boolean_id])
                boolean_obj.data.BIMMeshProperties.ifc_boolean_id = boolean_id
                boolean_obj.data.BIMMeshProperties.obj = obj
                new = props.openings.add()
                new.obj = boolean_obj

        if booleans:
            DecorationsHandler.install(bpy.context)
        return {"FINISHED"}

    def get_booleans(self, item: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        results = []
        if item.is_a("IfcBooleanResult"):
            results.extend(self.get_booleans(item.FirstOperand))
            results.append(item.SecondOperand)
        return results

    def create_half_space_solid(self) -> bpy.types.Object:
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, size=0.5)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        mesh = bpy.data.meshes.new(name="Dumb Opening")
        bm.to_mesh(mesh)
        bm.free()
        obj = object_data_add(bpy.context, mesh, operator=self)
        obj.name = "HalfSpaceSolid"
        return obj


class HideBooleans(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_booleans"
    bl_label = "Hide Booleans"
    bl_description = (
        "Hide boolean objects and apply their changed transforms.\n"
        "If boolean object is active, hide it, otherwise hide all boolean objects"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file)

        set_active_obj = None
        boolean_objs: list[bpy.types.Object]
        active_boolean_obj = (obj := context.active_object) and tool.Model.is_boolean_obj(obj)
        if active_boolean_obj:
            boolean_objs = [obj]
            set_active_obj = obj.data.BIMMeshProperties.obj
        else:
            props = bpy.context.scene.BIMModelProperties
            boolean_objs = [obj for o in props.openings if (obj := o.obj)]

        for obj in boolean_objs:
            ifc_boolean_id = obj.data.BIMMeshProperties.ifc_boolean_id
            boolean = tool.Ifc.get_entity_by_id(ifc_boolean_id)

            # Update boolean transform.
            if boolean:
                main_obj = cast(bpy.types.Object, obj.data.BIMMeshProperties.obj)
                if boolean.is_a("IfcHalfSpaceSolid"):
                    surface = boolean.BaseSurface

                    # Only IfcPlane is supported currently.
                    position = surface.Position
                    m = Matrix(ifcopenshell.util.placement.get_axis2placement(position).tolist())
                    m.translation *= unit_scale

                    # Only update if transform was changed.
                    if not np.allclose(m, obj.matrix_world):
                        new_m = main_obj.matrix_world.inverted() @ obj.matrix_world
                        new_m.normalize()
                        new_m.translation /= unit_scale
                        new_m = np.array(new_m)
                        ifcopenshell.util.element.remove_deep2(ifc_file, position)
                        surface.Position = builder.create_axis2_placement_3d_from_matrix(new_m)
                        tool.Geometry.reload_representation(main_obj)

            bpy.data.objects.remove(obj)
        tool.Model.clear_scene_openings()

        if set_active_obj:
            tool.Blender.set_active_object(set_active_obj)
        return {"FINISHED"}


class RemoveBooleans(Operator, tool.Ifc.Operator, AddObjectHelper):
    bl_idname = "bim.remove_booleans"
    bl_label = "Remove Booleans"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        upstream_obj = None
        bbim_boolean_updates = {}
        for obj in context.selected_objects:
            if (
                not obj.data
                or not hasattr(obj.data, "BIMMeshProperties")
                or not obj.data.BIMMeshProperties.ifc_boolean_id
            ):
                continue
            try:
                item = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_boolean_id)
            except:
                continue

            boolean_id = None
            for inverse in tool.Ifc.get().get_inverse(item):
                if inverse.is_a("IfcBooleanResult"):
                    boolean_id = inverse.id()
                    break
            ifcopenshell.api.run("geometry.remove_boolean", tool.Ifc.get(), item=item)

            if obj.data.BIMMeshProperties.obj:
                upstream_obj = obj.data.BIMMeshProperties.obj
                element = tool.Ifc.get_entity(upstream_obj)
                bbim_boolean_updates.setdefault(element, []).append(boolean_id)
                body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
                if body:
                    bonsai.core.geometry.switch_representation(
                        tool.Ifc,
                        tool.Geometry,
                        obj=upstream_obj,
                        representation=body,
                        should_reload=True,
                        is_global=True,
                        should_sync_changes_first=False,
                    )
            bpy.data.objects.remove(obj)

        for element, boolean_ids in bbim_boolean_updates.items():
            tool.Model.unmark_manual_booleans(element, boolean_ids)

        tool.Blender.set_active_object(upstream_obj)
        return {"FINISHED"}


class ShowOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.show_openings"
    bl_label = "Show"
    bl_description = "Show Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMModelProperties
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not getattr(element, "HasOpenings", None):
                continue
            if tool.Ifc.is_moved(obj):
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
            openings = tool.Model.load_openings(
                [
                    r.RelatedOpeningElement
                    for r in element.HasOpenings
                    if not tool.Ifc.get_object(r.RelatedOpeningElement)
                ],
            )
            for opening in openings:
                new = props.openings.add()
                new.obj = opening
                opening.display_type = "WIRE"
        DecorationsHandler.install(bpy.context)
        return {"FINISHED"}


class HideOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.hide_openings"
    bl_label = "Hide"
    bl_description = "Hide Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        to_delete = set()
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if element.is_a("IfcOpeningElement"):
                element = element.VoidsElements[0].RelatingBuildingElement
                obj = tool.Ifc.get_object(element)
            openings = [r.RelatedOpeningElement for r in element.HasOpenings]
            for opening in openings:
                opening_obj = tool.Ifc.get_object(opening)
                if opening_obj:
                    to_delete.add((opening, opening_obj))
        for opening, opening_obj in to_delete:
            tool.Ifc.unlink(element=opening)
            bpy.data.objects.remove(opening_obj)
        tool.Model.clear_scene_openings()
        return {"FINISHED"}


class EditOpenings(Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_openings"
    bl_label = "Edit"
    bl_description = "Edit Openings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMModelProperties
        building_objs = set()

        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if element.is_a("IfcOpeningElement"):
                element = element.VoidsElements[0].RelatingBuildingElement
                obj = tool.Ifc.get_object(element)
            openings = [r.RelatedOpeningElement for r in element.HasOpenings]
            for opening in openings:
                opening_obj = tool.Ifc.get_object(opening)
                building_objs.add(obj)

                similar_openings = bonsai.core.geometry.get_similar_openings(tool.Ifc, opening)
                similar_openings_building_objs = bonsai.core.geometry.get_similar_openings_building_objs(
                    tool.Ifc, similar_openings
                )
                building_objs.update(similar_openings_building_objs)

                if opening_obj:
                    if tool.Ifc.is_edited(opening_obj):
                        tool.Geometry.run_geometry_update_representation(obj=opening_obj)
                        bonsai.core.geometry.edit_similar_opening_placement(tool.Geometry, opening, similar_openings)
                    elif tool.Ifc.is_moved(opening_obj):
                        bonsai.core.geometry.edit_object_placement(
                            tool.Ifc, tool.Geometry, tool.Surveyor, obj=opening_obj
                        )
                        bonsai.core.geometry.edit_similar_opening_placement(tool.Geometry, opening, similar_openings)

                    building_objs.update(
                        self.get_all_building_objects_of_similar_openings(opening)
                    )  # NB this has nothing to do with clone similar_opening
                    tool.Ifc.unlink(element=opening)
                    if bpy.context.scene.BIMGeometryProperties.representation_obj == opening_obj:
                        bpy.context.scene.BIMGeometryProperties.representation_obj = None
                    bpy.data.objects.remove(opening_obj)

        tool.Model.reload_body_representation(building_objs)
        return {"FINISHED"}

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
    bl_description = "Clone the selected Opening and assign to the selected Element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        objects = bpy.context.selected_objects

        for obj in objects:
            entity = tool.Ifc.get_entity(obj)
            if entity.is_a() == "IfcWall":
                wall = entity
                continue
            if entity.is_a() == "IfcOpeningElement":
                opening = entity
                continue

        opening_placement = opening.ObjectPlacement
        opening_representation = opening.Representation

        new_opening = ifcopenshell.api.run("root.create_entity", tool.Ifc.get(), ifc_class="IfcOpeningElement")
        new_opening.Representation = opening_representation

        ifcopenshell.api.run("void.add_opening", tool.Ifc.get(), opening=new_opening, element=wall)
        new_opening.ObjectPlacement = opening_placement
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
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def __call__(self, context):
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

        for opening in context.scene.BIMModelProperties.openings:
            obj = opening.obj
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
                edges = [tuple([v.index for v in e.verts]) for e in bm.edges]
                color = selected_elements_color if obj in context.selected_objects else special_elements_color
                self.draw_batch("LINES", verts, color, edges)

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
