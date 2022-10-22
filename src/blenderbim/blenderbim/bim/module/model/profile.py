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
import copy
import math
import bmesh
import mathutils.geometry
import ifcopenshell
import ifcopenshell.util.type
import ifcopenshell.util.unit
import ifcopenshell.util.element
import blenderbim.bim.handler
import blenderbim.tool as tool
import blenderbim.core.type
import blenderbim.core.geometry
from blenderbim.bim.ifc import IfcStore
from math import pi, degrees, inf
from mathutils import Vector, Matrix
from ifcopenshell.api.pset.data import Data as PsetData
from ifcopenshell.api.material.data import Data as MaterialData
from blenderbim.bim.module.geometry.helper import Helper


def element_listener(element, obj):
    blenderbim.bim.handler.subscribe_to(obj, "mode", mode_callback)


def mode_callback(obj, data):
    for obj in set(bpy.context.selected_objects + [bpy.context.active_object]):
        if (
            not obj.data
            or not isinstance(obj.data, (bpy.types.Mesh, bpy.types.Curve, bpy.types.TextCurve))
            or not obj.BIMObjectProperties.ifc_definition_id
            or not bpy.context.scene.BIMProjectProperties.is_authoring
        ):
            return
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbProfile":
            return
        if obj.mode == "EDIT":
            IfcStore.edited_objs.add(obj)
            bm = bmesh.from_edit_mesh(obj.data)
            bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
            bmesh.update_edit_mesh(obj.data)
            bm.free()
        else:
            material_usage = ifcopenshell.util.element.get_material(product)
            x, y = obj.dimensions[0:2]
            if not material_usage.CardinalPoint:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[0]) + (Vector((x, y, 0)) / 2))
            elif material_usage.CardinalPoint == 1:
                new_origin = obj.matrix_world @ Vector(obj.bound_box[4])
            elif material_usage.CardinalPoint == 2:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[0]) + (Vector((x, 0, 0)) / 2))
            elif material_usage.CardinalPoint == 3:
                new_origin = obj.matrix_world @ Vector(obj.bound_box[0])
            elif material_usage.CardinalPoint == 4:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[4]) + (Vector((0, y, 0)) / 2))
            elif material_usage.CardinalPoint == 5:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[0]) + (Vector((x, y, 0)) / 2))
            elif material_usage.CardinalPoint == 6:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[0]) + (Vector((0, y, 0)) / 2))
            elif material_usage.CardinalPoint == 7:
                new_origin = obj.matrix_world @ Vector(obj.bound_box[7])
            elif material_usage.CardinalPoint == 8:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[3]) + (Vector((x, 0, 0)) / 2))
            elif material_usage.CardinalPoint == 9:
                new_origin = obj.matrix_world @ Vector(obj.bound_box[3])
            if (obj.matrix_world.translation - new_origin).length < 0.001:
                return
            obj.data.transform(
                Matrix.Translation(
                    (obj.matrix_world.inverted().to_quaternion() @ (obj.matrix_world.translation - new_origin))
                )
            )
            obj.matrix_world.translation = new_origin


class DumbProfileGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    def generate(self, link_to_scene=True):
        self.file = IfcStore.get_file()
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        material = ifcopenshell.util.element.get_material(self.relating_type)
        if material and material.is_a("IfcMaterialProfileSet"):
            self.profile_set = material
        else:
            return

        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Axis", "GRAPH_VIEW")
        props = bpy.context.scene.BIMModelProperties
        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = bpy.data.objects.get(self.collection.name)
        self.depth = props.extrusion_depth * self.unit_scale
        self.rotation = 0
        self.location = Vector((0, 0, 0))
        self.cardinal_point = int(bpy.context.scene.BIMModelProperties.cardinal_point)
        return self.derive_from_cursor(link_to_scene=link_to_scene)

    def derive_from_cursor(self, link_to_scene):
        self.location = bpy.context.scene.cursor.location
        return self.create_profile(link_to_scene)

    def create_profile(self, link_to_scene):
        ifc_classes = ifcopenshell.util.type.get_applicable_entities(self.relating_type.is_a(), self.file.schema)
        # Standard cases are deprecated, so let's cull them
        ifc_class = [c for c in ifc_classes if "StandardCase" not in c][0]

        mesh = bpy.data.meshes.new("Dummy")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)

        matrix_world = Matrix()
        if self.relating_type.is_a() in ["IfcBeamType", "IfcMemberType"]:
            matrix_world = Matrix.Rotation(pi / 2, 4, "Z") @ Matrix.Rotation(pi / 2, 4, "X") @ matrix_world
        matrix_world.col[3] = self.location.to_4d()
        if link_to_scene and self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            matrix_world[2][3] = self.collection_obj.location[2]
        if link_to_scene:
            self.collection.objects.link(obj)

        element = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            should_add_representation=False,
            context=self.body_context,
        )
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=self.relating_type)

        material = ifcopenshell.util.element.get_material(element)
        material.CardinalPoint = self.cardinal_point

        obj.matrix_world = matrix_world
        bpy.context.view_layer.update()
        blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        if self.axis_context:
            representation = ifcopenshell.api.run(
                "geometry.add_axis_representation",
                tool.Ifc.get(),
                context=self.axis_context,
                axis=[(0.0, 0.0, 0.0), (0.0, 0.0, self.depth)],
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
            )

        representation = ifcopenshell.api.run(
            "geometry.add_profile_representation",
            tool.Ifc.get(),
            context=self.body_context,
            profile=self.profile_set.CompositeProfile or self.profile_set.MaterialProfiles[0].Profile,
            cardinal_point=self.cardinal_point,
            depth=self.depth,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
        )
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbProfile"})
        MaterialData.load(self.file)

        if link_to_scene:
            obj.select_set(True)

        return obj


class DumbProfileRegenerator:
    def regenerate_from_profile(self, usecase_path, ifc_file, settings):
        self.file = ifc_file
        objs = []
        profile = settings["profile"].Profile
        if not profile:
            return
        for element in self.get_elements_using_profile(profile):
            obj = tool.Ifc.get_object(element)
            if obj:
                objs.append(obj)
        DumbProfileRecalculator().recalculate(objs)

    def get_elements_using_profile(self, profile):
        results = []
        for profile_set in [
            mp.ToMaterialProfileSet[0] for mp in self.file.get_inverse(profile) if mp.is_a("IfcMaterialProfile")
        ]:
            for inverse in self.file.get_inverse(profile_set):
                if not inverse.is_a("IfcMaterialProfileSetUsage"):
                    continue
                if self.file.schema == "IFC2X3":
                    for rel in self.file.get_inverse(inverse):
                        if not rel.is_a("IfcRelAssociatesMaterial"):
                            continue
                        results.extend(rel.RelatedObjects)
                else:
                    for rel in inverse.AssociatedTo:
                        results.extend(rel.RelatedObjects)
        return results

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        obj = tool.Ifc.get_object(settings["related_object"])
        if not obj or not obj.data or not obj.data.BIMMeshProperties.ifc_definition_id:
            return
        new_material = ifcopenshell.util.element.get_material(settings["relating_type"])
        if not new_material or not new_material.is_a("IfcMaterialProfileSet"):
            return
        DumbProfileRecalculator().recalculate([obj])


class ExtendProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.extend_profile"
    bl_label = "Extend Profile"
    bl_options = {"REGISTER", "UNDO"}
    join_type: bpy.props.StringProperty()

    def _execute(self, context):
        selected_objs = context.selected_objects
        joiner = DumbProfileJoiner()
        if not self.join_type:
            for obj in selected_objs:
                joiner.unjoin(obj)
            return {"FINISHED"}
        if not context.active_object:
            return {"FINISHED"}
        if len(selected_objs) == 1:
            joiner.join_E(context.active_object, context.scene.cursor.location)
            return {"FINISHED"}
        if len(selected_objs) == 2:
            if self.join_type == "L":
                joiner.join_L([o for o in selected_objs if o != context.active_object][0], context.active_object)
            elif self.join_type == "V":
                joiner.join_V([o for o in selected_objs if o != context.active_object][0], context.active_object)
        if len(selected_objs) < 2:
            return {"FINISHED"}
        if self.join_type == "T":
            for obj in selected_objs:
                if obj == context.active_object:
                    continue
                joiner.join_T(obj, context.active_object)
        return {"FINISHED"}


class DumbProfileJoiner:
    def __init__(self):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Axis", "GRAPH_VIEW")
        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    def unjoin(self, profile1):
        element1 = tool.Ifc.get_entity(profile1)
        if not element1:
            return

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATSTART")
        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATEND")

        axis1 = self.get_profile_axis(profile1)
        axis = copy.deepcopy(axis1)
        body = copy.deepcopy(axis1)
        self.recreate_profile(element1, profile1, axis, body)

    def join_E(self, profile1, target):
        element1 = tool.Ifc.get_entity(profile1)
        if not element1:
            return
        axis1 = self.get_profile_axis(profile1)
        intersect, connection = mathutils.geometry.intersect_point_line(target, *axis1)
        connection = "ATEND" if connection > 0.5 else "ATSTART"

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type=connection)

        axis = copy.deepcopy(axis1)
        body = copy.deepcopy(axis1)
        axis[1 if connection == "ATEND" else 0] = intersect
        body[1 if connection == "ATEND" else 0] = intersect
        self.recreate_profile(element1, profile1, axis, body)

    def set_depth(self, profile1, length):
        element1 = tool.Ifc.get_entity(profile1)
        if not element1:
            return

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATEND")

        axis1 = self.get_profile_axis(profile1)
        axis = copy.deepcopy(axis1)
        body = copy.deepcopy(axis1)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        si_length = unit_scale * length
        end = profile1.matrix_world @ Vector((si_length, 0, 0))
        axis[1] = end
        body[1] = end
        self.recreate_profile(element1, profile1, axis, body)

    def join_T(self, profile1, profile2):
        element1 = tool.Ifc.get_entity(profile1)
        element2 = tool.Ifc.get_entity(profile2)
        axis1 = self.get_profile_axis(profile1)
        axis2 = self.get_profile_axis(profile2)
        intersect = tool.Cad.intersect_edges(axis1, axis2)
        if intersect:
            intersect, _ = intersect
        else:
            return
        connection = "ATEND" if tool.Cad.edge_percent(intersect, axis1) > 0.5 else "ATSTART"

        ifcopenshell.api.run(
            "geometry.connect_path",
            tool.Ifc.get(),
            related_element=element1,
            relating_element=element2,
            relating_connection="ATPATH",
            related_connection=connection,
            description="BUTT",
        )

        self.recreate_profile(element1, profile1, axis1, axis1)

    def join_V(self, profile1, profile2):
        element1 = tool.Ifc.get_entity(profile1)
        element2 = tool.Ifc.get_entity(profile2)
        axis1 = self.get_profile_axis(profile1)
        axis2 = self.get_profile_axis(profile2)
        intersect = tool.Cad.intersect_edges(axis1, axis2)
        if intersect:
            intersect, _ = intersect
        else:
            return
        profile1_end = "ATEND" if tool.Cad.edge_percent(intersect, axis1) > 0.5 else "ATSTART"
        profile2_end = "ATEND" if tool.Cad.edge_percent(intersect, axis2) > 0.5 else "ATSTART"

        ifcopenshell.api.run(
            "geometry.connect_path",
            tool.Ifc.get(),
            relating_element=element1,
            related_element=element2,
            relating_connection=profile1_end,
            related_connection=profile2_end,
            description="MITRE",
        )

        self.recreate_profile(element1, profile1, axis1, axis1)
        self.recreate_profile(element2, profile2, axis2, axis2)

    def join_L(self, profile1, profile2):
        element1 = tool.Ifc.get_entity(profile1)
        element2 = tool.Ifc.get_entity(profile2)
        axis1 = self.get_profile_axis(profile1)
        axis2 = self.get_profile_axis(profile2)
        intersect = tool.Cad.intersect_edges(axis1, axis2)
        if intersect:
            intersect, _ = intersect
        else:
            return
        profile1_end = "ATEND" if tool.Cad.edge_percent(intersect, axis1) > 0.5 else "ATSTART"
        profile2_end = "ATEND" if tool.Cad.edge_percent(intersect, axis2) > 0.5 else "ATSTART"

        ifcopenshell.api.run(
            "geometry.connect_path",
            tool.Ifc.get(),
            relating_element=element1,
            related_element=element2,
            relating_connection=profile1_end,
            related_connection=profile2_end,
            description="BUTT",
        )

        self.recreate_profile(element1, profile1, axis1, axis1)
        self.recreate_profile(element2, profile2, axis2, axis2)

    def recreate_profile(self, element, obj, axis=None, body=None):
        if axis is None or body is None:
            axis = body = self.get_profile_axis(obj)
        self.axis = copy.deepcopy(axis)
        self.body = copy.deepcopy(body)
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=False)
        usage = None
        if material.is_a("IfcMaterialProfileSetUsage"):
            usage = material
            material = material.ForProfileSet
        self.profile = material.CompositeProfile or material.MaterialProfiles[0].Profile
        self.clippings = []

        for rel in element.ConnectedTo:
            connection = rel.RelatingConnectionType
            other = tool.Ifc.get_object(rel.RelatedElement)
            if connection not in ["ATPATH", "NOTDEFINED"]:
                self.join(
                    obj, other, connection, rel.RelatedConnectionType, is_relating=True, description=rel.Description
                )
        for rel in element.ConnectedFrom:
            connection = rel.RelatedConnectionType
            other = tool.Ifc.get_object(rel.RelatingElement)
            if connection not in ["ATPATH", "NOTDEFINED"]:
                self.join(
                    obj, other, connection, rel.RelatingConnectionType, is_relating=False, description=rel.Description
                )

        new_matrix = copy.deepcopy(obj.matrix_world)
        new_matrix.col[3] = self.body[0].to_4d().copy()
        new_matrix.invert()

        for clipping in self.clippings:
            if clipping["operand_type"] == "IfcHalfSpaceSolid":
                clipping["matrix"] = new_matrix @ clipping["matrix"]

        self.clippings.extend(tool.Model.get_manual_booleans(element))

        depth = (self.body[1] - self.body[0]).length

        if self.axis_context:
            axis = [(new_matrix @ a) for a in self.axis]
            new_axis = ifcopenshell.api.run(
                "geometry.add_axis_representation", tool.Ifc.get(), context=self.axis_context, axis=axis
            )
            old_axis = ifcopenshell.util.representation.get_representation(element, "Model", "Axis", "GRAPH_VIEW")
            if old_axis:
                for inverse in tool.Ifc.get().get_inverse(old_axis):
                    ifcopenshell.util.element.replace_attribute(inverse, old_axis, new_axis)
                blenderbim.core.geometry.remove_representation(
                    tool.Ifc, tool.Geometry, obj=obj, representation=old_axis
                )
            else:
                ifcopenshell.api.run(
                    "geometry.assign_representation", tool.Ifc.get(), product=element, representation=new_axis
                )

        new_body = ifcopenshell.api.run(
            "geometry.add_profile_representation",
            tool.Ifc.get(),
            context=self.body_context,
            profile=self.profile,
            depth=depth,
            cardinal_point=usage.CardinalPoint if usage else None,
            clippings=self.clippings,
        )

        old_body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if old_body:
            for inverse in tool.Ifc.get().get_inverse(old_body):
                ifcopenshell.util.element.replace_attribute(inverse, old_body, new_body)
            obj.data.BIMMeshProperties.ifc_definition_id = int(new_body.id())
            obj.data.name = f"{self.body_context.id()}/{new_body.id()}"
            blenderbim.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_body)
        else:
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=new_body
            )

        previous_matrix = obj.matrix_world.copy()
        previous_origin = obj.location.copy()
        obj.location[0], obj.location[1], obj.location[2] = self.body[0]
        bpy.context.view_layer.update()
        if tool.Ifc.is_moved(obj):
            # Openings should move with the host overall ...
            # ... except their position should stay the same along the local Z axis of the wall
            for opening in [r.RelatedOpeningElement for r in element.HasOpenings]:
                percent = tool.Cad.edge_percent(
                    self.body[0], (previous_origin, (previous_matrix @ Vector((0, 0, 1))))
                )
                is_z_offset_increased = True if percent < 0 else False

                change_in_z = (self.body[0] - previous_origin).length / self.unit_scale
                coordinates = list(opening.ObjectPlacement.RelativePlacement.Location.Coordinates)
                if is_z_offset_increased:
                    coordinates[2] += change_in_z
                else:
                    coordinates[2] -= change_in_z
                opening.ObjectPlacement.RelativePlacement.Location.Coordinates = coordinates
            blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=new_body,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        tool.Geometry.record_object_materials(obj)

    def join(self, profile1, profile2, connection1, connection2, is_relating=True, description="BUTT"):
        element1 = tool.Ifc.get_entity(profile1)
        element2 = tool.Ifc.get_entity(profile2)
        axis1 = self.get_profile_axis(profile1)
        axis2 = self.get_profile_axis(profile2)

        angle = tool.Cad.angle_edges(axis1, axis2, signed=False, degrees=True)
        if tool.Cad.is_x(angle, (0, 180), tolerance=0.001):
            return False

        intersect, _ = tool.Cad.intersect_edges(axis1, axis2)

        proposed_axis = [self.axis[0], intersect] if connection1 == "ATEND" else [intersect, self.axis[1]]

        if tool.Cad.is_x(tool.Cad.angle_edges(self.axis, proposed_axis, degrees=True), 180):
            # The user has moved the element into an invalid position that cannot connect at the desired end
            return False

        self.axis[1 if connection1 == "ATEND" else 0] = intersect

        # Work out body extents

        if connection1 == "ATEND":
            axisl = (profile2.matrix_world.inverted() @ axis1[1]) - (profile2.matrix_world.inverted() @ axis1[0])
        elif connection1 == "ATSTART":
            axisl = (profile2.matrix_world.inverted() @ axis1[0]) - (profile2.matrix_world.inverted() @ axis1[1])
        xy_angle = degrees(Vector((1, 0)).angle_signed(axisl.normalized().to_2d()))
        if xy_angle >= -135 and xy_angle <= -45:
            closest_plane = "bottom"
            furthest_plane = "top"
        elif xy_angle >= 45 and xy_angle <= 135:
            closest_plane = "top"
            furthest_plane = "bottom"
        elif xy_angle >= -45 and xy_angle <= 45:
            closest_plane = "left"
            furthest_plane = "right"
        else:
            closest_plane = "right"
            furthest_plane = "left"

        is_orthogonal = tool.Cad.is_x(tool.Cad.angle_edges(axis1, axis2, degrees=True), 90, tolerance=0.001)

        if description == "MITRE":
            # Mitre joints are an unofficial convention

            # Check the closest plane from the perspective of the other element
            if connection2 == "ATEND":
                axisl = (profile1.matrix_world.inverted() @ axis2[1]) - (profile1.matrix_world.inverted() @ axis2[0])
            elif connection2 == "ATSTART":
                axisl = (profile1.matrix_world.inverted() @ axis2[0]) - (profile1.matrix_world.inverted() @ axis2[1])
            xy_angle2 = degrees(Vector((1, 0)).angle_signed(axisl.normalized().to_2d()))
            if xy_angle2 >= -135 and xy_angle2 <= -45:
                closest_plane2 = "bottom"
                furthest_plane2 = "top"
            elif xy_angle2 >= 45 and xy_angle2 <= 135:
                closest_plane2 = "top"
                furthest_plane2 = "bottom"
            elif xy_angle2 >= -45 and xy_angle2 <= 45:
                closest_plane2 = "left"
                furthest_plane2 = "right"
            else:
                closest_plane2 = "right"
                furthest_plane2 = "left"

            if connection1 == "ATEND":
                if tool.Cad.is_x(abs(xy_angle), (0, 90, 180), tolerance=0.001) and is_orthogonal:
                    plane = self.get_profile_plane(profile2, furthest_plane)
                    intersect = mathutils.geometry.intersect_line_plane(
                        *axis1, plane.col[3].to_3d(), plane.col[2].to_3d()
                    )
                    self.body[1] = intersect
                else:
                    plane = self.get_profile_plane(profile2, furthest_plane, z_inwards=False)
                    intersect = mathutils.geometry.intersect_line_plane(
                        *axis1, plane.col[3].to_3d(), plane.col[2].to_3d()
                    )
                    max_dim = self.get_max_bound_box_dimension(profile1)
                    self.body[1] = intersect + profile1.matrix_world.to_quaternion() @ Vector((0, 0, max_dim))

                # Mitre clip
                if connection1 == connection2:
                    plane1 = self.get_profile_plane(profile1, furthest_plane2)
                    plane2 = self.get_profile_plane(profile2, furthest_plane)
                    clip1, direction1 = mathutils.geometry.intersect_plane_plane(
                        plane1.col[3].to_3d(), plane1.col[2].to_3d(), plane2.col[3].to_3d(), plane2.col[2].to_3d()
                    )

                    plane1 = self.get_profile_plane(profile1, closest_plane2)
                    plane2 = self.get_profile_plane(profile2, closest_plane)
                    clip2, direction2 = mathutils.geometry.intersect_plane_plane(
                        plane1.col[3].to_3d(), plane1.col[2].to_3d(), plane2.col[3].to_3d(), plane2.col[2].to_3d()
                    )
                else:
                    plane1 = self.get_profile_plane(profile1, furthest_plane2)
                    plane2 = self.get_profile_plane(profile2, furthest_plane)
                    clip1, direction1 = mathutils.geometry.intersect_plane_plane(
                        plane1.col[3].to_3d(), plane1.col[2].to_3d(), plane2.col[3].to_3d(), plane2.col[2].to_3d()
                    )

                    plane1 = self.get_profile_plane(profile1, closest_plane2)
                    plane2 = self.get_profile_plane(profile2, closest_plane)
                    clip2, direction2 = mathutils.geometry.intersect_plane_plane(
                        plane1.col[3].to_3d(), plane1.col[2].to_3d(), plane2.col[3].to_3d(), plane2.col[2].to_3d()
                    )

                y_axis = direction2
                x_axis = (clip2 - clip1).normalized().to_3d()
                z_axis = x_axis.cross(y_axis)
                self.clippings.append(
                    {
                        "type": "IfcBooleanClippingResult",
                        "operand_type": "IfcHalfSpaceSolid",
                        "matrix": self.create_matrix(clip1, x_axis, y_axis, z_axis),
                    }
                )
            elif connection1 == "ATSTART":
                if tool.Cad.is_x(abs(xy_angle), (0, 90, 180), tolerance=0.001) and is_orthogonal:
                    plane = self.get_profile_plane(profile2, furthest_plane)
                    intersect = mathutils.geometry.intersect_line_plane(
                        *axis1, plane.col[3].to_3d(), plane.col[2].to_3d()
                    )
                    self.body[0] = intersect
                else:
                    plane = self.get_profile_plane(profile2, furthest_plane, z_inwards=False)
                    intersect = mathutils.geometry.intersect_line_plane(
                        *axis1, plane.col[3].to_3d(), plane.col[2].to_3d()
                    )
                    max_dim = self.get_max_bound_box_dimension(profile1)
                    self.body[0] = intersect - profile1.matrix_world.to_quaternion() @ Vector((0, 0, max_dim))

                if connection1 == connection2:
                    plane1 = self.get_profile_plane(profile1, furthest_plane2)
                    plane2 = self.get_profile_plane(profile2, furthest_plane)
                    clip1, direction1 = mathutils.geometry.intersect_plane_plane(
                        plane1.col[3].to_3d(), plane1.col[2].to_3d(), plane2.col[3].to_3d(), plane2.col[2].to_3d()
                    )

                    plane1 = self.get_profile_plane(profile1, closest_plane2)
                    plane2 = self.get_profile_plane(profile2, closest_plane)
                    clip2, direction2 = mathutils.geometry.intersect_plane_plane(
                        plane1.col[3].to_3d(), plane1.col[2].to_3d(), plane2.col[3].to_3d(), plane2.col[2].to_3d()
                    )
                else:
                    plane1 = self.get_profile_plane(profile1, furthest_plane2)
                    plane2 = self.get_profile_plane(profile2, furthest_plane)
                    clip1, direction1 = mathutils.geometry.intersect_plane_plane(
                        plane1.col[3].to_3d(), plane1.col[2].to_3d(), plane2.col[3].to_3d(), plane2.col[2].to_3d()
                    )

                    plane1 = self.get_profile_plane(profile1, closest_plane2)
                    plane2 = self.get_profile_plane(profile2, closest_plane)
                    clip2, direction2 = mathutils.geometry.intersect_plane_plane(
                        plane1.col[3].to_3d(), plane1.col[2].to_3d(), plane2.col[3].to_3d(), plane2.col[2].to_3d()
                    )

                y_axis = direction2
                x_axis = (clip2 - clip1).normalized().to_3d()
                z_axis = x_axis.cross(y_axis)
                self.clippings.append(
                    {
                        "type": "IfcBooleanClippingResult",
                        "operand_type": "IfcHalfSpaceSolid",
                        "matrix": self.create_matrix(clip1, x_axis, y_axis, z_axis),
                    }
                )
        else:
            # This is the standard L and T joints described by IFC
            if connection1 == "ATEND":
                if tool.Cad.is_x(abs(xy_angle), (0, 90, 180), tolerance=0.001) and is_orthogonal:
                    plane = self.get_profile_plane(profile2, furthest_plane if is_relating else closest_plane)
                    intersect = mathutils.geometry.intersect_line_plane(
                        *axis1, plane.col[3].to_3d(), plane.col[2].to_3d()
                    )
                    self.body[1] = intersect
                else:
                    plane = self.get_profile_plane(
                        profile2,
                        furthest_plane if is_relating else closest_plane,
                        z_inwards=False if is_relating else True,
                    )
                    intersect = mathutils.geometry.intersect_line_plane(
                        *axis1, plane.col[3].to_3d(), plane.col[2].to_3d()
                    )
                    max_dim = self.get_max_bound_box_dimension(profile1)
                    self.body[1] = intersect + profile1.matrix_world.to_quaternion() @ Vector((0, 0, max_dim))
                    self.clippings.append(
                        {
                            "type": "IfcBooleanClippingResult",
                            "operand_type": "IfcHalfSpaceSolid",
                            "matrix": plane,
                        }
                    )
            elif connection1 == "ATSTART":
                if tool.Cad.is_x(abs(xy_angle), (0, 90, 180), tolerance=0.001) and is_orthogonal:
                    plane = self.get_profile_plane(profile2, furthest_plane if is_relating else closest_plane)
                    intersect = mathutils.geometry.intersect_line_plane(
                        *axis1, plane.col[3].to_3d(), plane.col[2].to_3d()
                    )
                    self.body[0] = intersect
                else:
                    plane = self.get_profile_plane(
                        profile2,
                        furthest_plane if is_relating else closest_plane,
                        z_inwards=False if is_relating else True,
                    )
                    intersect = mathutils.geometry.intersect_line_plane(
                        *axis1, plane.col[3].to_3d(), plane.col[2].to_3d()
                    )
                    max_dim = self.get_max_bound_box_dimension(profile1)
                    self.body[0] = intersect - profile1.matrix_world.to_quaternion() @ Vector((0, 0, max_dim))
                    self.clippings.append(
                        {
                            "type": "IfcBooleanClippingResult",
                            "operand_type": "IfcHalfSpaceSolid",
                            "matrix": plane,
                        }
                    )

    def get_max_bound_box_dimension(self, obj):
        x = [v[0] for v in obj.bound_box]
        y = [v[1] for v in obj.bound_box]
        x_dim = max(x) - min(x)
        y_dim = max(y) - min(y)
        return x_dim if x_dim > y_dim else y_dim

    def get_profile_plane(self, obj, plane, z_inwards=True):
        # Get a matrix for one of the bounding planes of the profile to be used as cutting plane
        # Here's an example of looking at the end of an I-Beam profile with a +Z extrusion out of the screen
        #        top
        #      +-----+           Y
        #      |=====|           ^
        #      |  |  |           |
        # left |  |  | right     Z->X
        #      |  |  |
        #      |=====|
        #      +-----+
        #      bottom
        if plane == "top":
            max_y = max([v[1] for v in obj.bound_box])
            p = obj.matrix_world @ Vector((0, max_y, 0))
            x_axis = obj.matrix_world.to_quaternion() @ Vector((0, 0, 1))
            if z_inwards:
                y_axis = obj.matrix_world.to_quaternion() @ Vector((-1, 0, 0))
                z_axis = obj.matrix_world.to_quaternion() @ Vector((0, -1, 0))
            else:
                y_axis = obj.matrix_world.to_quaternion() @ Vector((1, 0, 0))
                z_axis = obj.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        elif plane == "bottom":
            min_y = min([v[1] for v in obj.bound_box])
            p = obj.matrix_world @ Vector((0, min_y, 0))
            x_axis = obj.matrix_world.to_quaternion() @ Vector((0, 0, 1))
            if z_inwards:
                y_axis = obj.matrix_world.to_quaternion() @ Vector((1, 0, 0))
                z_axis = obj.matrix_world.to_quaternion() @ Vector((0, 1, 0))
            else:
                y_axis = obj.matrix_world.to_quaternion() @ Vector((-1, 0, 0))
                z_axis = obj.matrix_world.to_quaternion() @ Vector((0, -1, 0))
        elif plane == "right":
            max_x = max([v[0] for v in obj.bound_box])
            p = obj.matrix_world @ Vector((max_x, 0, 0))
            x_axis = obj.matrix_world.to_quaternion() @ Vector((0, 0, 1))
            if z_inwards:
                y_axis = obj.matrix_world.to_quaternion() @ Vector((0, 1, 0))
                z_axis = obj.matrix_world.to_quaternion() @ Vector((-1, 0, 0))
            else:
                y_axis = obj.matrix_world.to_quaternion() @ Vector((0, -1, 0))
                z_axis = obj.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        elif plane == "left":
            min_x = min([v[0] for v in obj.bound_box])
            p = obj.matrix_world @ Vector((min_x, 0, 0))
            x_axis = obj.matrix_world.to_quaternion() @ Vector((0, 0, 1))
            if z_inwards:
                y_axis = obj.matrix_world.to_quaternion() @ Vector((0, -1, 0))
                z_axis = obj.matrix_world.to_quaternion() @ Vector((1, 0, 0))
            else:
                y_axis = obj.matrix_world.to_quaternion() @ Vector((0, 1, 0))
                z_axis = obj.matrix_world.to_quaternion() @ Vector((-1, 0, 0))
        return self.create_matrix(p, x_axis, y_axis, z_axis)

    def create_matrix(self, p, x, y, z):
        return Matrix(
            (
                (x[0], y[0], z[0], p[0]),
                (x[1], y[1], z[1], p[1]),
                (x[2], y[2], z[2], p[2]),
                (0.0, 0.0, 0.0, 1.0),
            )
        )

    def get_profile_axis(self, obj):
        z_values = [v[2] for v in obj.bound_box]
        return [
            (obj.matrix_world @ Vector((0.0, 0.0, min(z_values)))),
            (obj.matrix_world @ Vector((0.0, 0.0, max(z_values)))),
        ]


class RecalculateProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_profile"
    bl_label = "Recalculate Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        DumbProfileRecalculator().recalculate(context.selected_objects)
        return {"FINISHED"}


class DumbProfileRecalculator:
    def recalculate(self, profiles):
        queue = set()
        for profile in profiles:
            element = tool.Ifc.get_entity(profile)
            queue.add((element, profile))
            for rel in getattr(element, "ConnectedTo", []):
                queue.add((rel.RelatedElement, tool.Ifc.get_object(rel.RelatedElement)))
            for rel in getattr(element, "ConnectedFrom", []):
                queue.add((rel.RelatingElement, tool.Ifc.get_object(rel.RelatingElement)))
        joiner = DumbProfileJoiner()
        for element, profile in queue:
            if element.is_a() in ("IfcColumn", "IfcBeam", "IfcMember") and profile:
                joiner.recreate_profile(element, profile)


class ChangeProfileDepth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_profile_depth"
    bl_label = "Change Profile Length"
    bl_options = {"REGISTER", "UNDO"}
    depth: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        joiner = DumbProfileJoiner()
        for obj in context.selected_objects:
            joiner.set_depth(obj, self.depth)
        return {"FINISHED"}


class ChangeCardinalPoint(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_cardinal_point"
    bl_label = "Change Cardinal Point"
    bl_options = {"REGISTER", "UNDO"}
    cardinal_point: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        objs = []
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            material = ifcopenshell.util.element.get_material(element, should_skip_usage=False)
            if material.is_a("IfcMaterialProfileSetUsage"):
                material.CardinalPoint = self.cardinal_point
                objs.append(obj)
        DumbProfileRecalculator().recalculate(objs)
        return {"FINISHED"}


class Rotate90(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.rotate_90"
    bl_label = "Rotate 90"
    bl_options = {"REGISTER", "UNDO"}
    axis: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        objs = []
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element.ConnectedTo or element.ConnectedFrom:
                objs.append(obj)
            rotate_matrix = Matrix.Rotation(pi / 2, 4, self.axis)
            obj.matrix_world @= rotate_matrix
        bpy.context.view_layer.update()
        DumbProfileRecalculator().recalculate(objs)
        return {"FINISHED"}
