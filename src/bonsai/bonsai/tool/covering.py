# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

import bpy
import ifcopenshell.api.geometry
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import shapely
import shapely.ops
from mathutils import Matrix

import bonsai.core.geometry
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.covering.prop import BIMCoveringProperties


class Covering(bonsai.core.tool.Covering):
    WALL_COVERING_TYPES = ("CLADDING", "INSULATION")

    @classmethod
    def get_covering_props(cls) -> BIMCoveringProperties:
        return bpy.context.scene.BIMCoveringProperties

    @classmethod
    def get_z_from_ceiling_height(cls) -> float:
        props = cls.get_covering_props()
        return props.ceiling_height

    #    def toggle_spaces_visibility_wired_and_textured(cls, spaces):
    #        first_obj = tool.Ifc.get_object(spaces[0])
    #        if bpy.data.objects[first_obj.name].display_type == "TEXTURED":
    #            for space in spaces:
    #                obj = tool.Ifc.get_object(space)
    #                bpy.data.objects[obj.name].show_wire = True
    #                bpy.data.objects[obj.name].display_type = "WIRE"
    #            return
    #
    #        elif bpy.data.objects[first_obj.name].display_type == "WIRE":
    #            for space in spaces:
    #                obj = tool.Ifc.get_object(space)
    #                bpy.data.objects[obj.name].show_wire = False
    #                bpy.data.objects[obj.name].display_type = "TEXTURED"
    #            return

    @classmethod
    def covering_poll_wall_selected(
        cls, operator: type[bpy.types.Operator], context: bpy.types.Context, covering_type: Union[str, tuple[str, ...]]
    ) -> bool:
        if not tool.Ifc.get():
            return False
        if not context.selected_objects or not context.active_object:
            operator.poll_message_set("No objects selected.")
            return False
        element = tool.Ifc.get_entity(context.active_object)
        if not element or not element.is_a("IfcWall") or not tool.Model.get_usage_type(element) == "LAYER2":
            operator.poll_message_set("LAYER2 based IfcWall must be selected.")
            return False
        return cls.covering_poll_relating_type_check(operator, context, covering_type)

    @classmethod
    def covering_poll_relating_type_check(
        cls, operator: type[bpy.types.Operator], context: bpy.types.Context, covering_type: Union[str, tuple[str, ...]]
    ) -> bool:
        if not tool.Ifc.get():
            return False
        covering_types = (covering_type,) if isinstance(covering_type, str) else covering_type
        props = tool.Model.get_model_props()
        relating_type_id = tool.Blender.get_enum_safe(props, "relating_type_id")
        if relating_type_id is not None:
            relating_type = ifcopenshell.util.element.get_predefined_type(tool.Ifc.get().by_id(int(relating_type_id)))
            if relating_type in covering_types:
                return True
        types_str = " or ".join(f"'{t}'" for t in covering_types)
        operator.poll_message_set(f"Select IfcCoveringType with predefined type {types_str}.")
        return False

    @classmethod
    def get_relating_type_layer_thickness(cls) -> float:
        """Total material layer thickness of the active relating type, in project units."""
        props = tool.Model.get_model_props()
        relating_type_id = tool.Blender.get_enum_safe(props, "relating_type_id")
        if relating_type_id is None:
            return 0.0
        relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        material = ifcopenshell.util.element.get_material(relating_type, should_skip_usage=True)
        if material and material.is_a("IfcMaterialLayerSet"):
            return sum(layer.LayerThickness for layer in material.MaterialLayers)
        return 0.0

    @classmethod
    def get_wall_side_facing_cursor(cls, wall_obj: bpy.types.Object) -> float:
        """Get the wall local Y side (1.0 or -1.0) whose face is turned towards the 3D cursor."""
        cursor_local = wall_obj.matrix_world.inverted() @ bpy.context.scene.cursor.location
        center_y = sum(v[1] for v in wall_obj.bound_box) / 8
        return 1.0 if cursor_local.y >= center_y else -1.0

    @classmethod
    def get_wall_side_face(
        cls, wall_obj: bpy.types.Object, side: float
    ) -> Optional[tuple[list[shapely.Polygon], float]]:
        """Get the wall side face net of openings as polygons projected to the wall local XZ plane.

        :param side: 1.0 for the local +Y face, -1.0 for the local -Y face.
        :return: (polygons in wall local XZ in SI units, face Y offset in wall local space) or None.
        """
        mesh = wall_obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        candidates = [p for p in mesh.polygons if p.normal.y * side > 0.99]
        if not candidates:
            return None
        face_y = max(p.center.y * side for p in candidates) * side
        polys = []
        for p in candidates:
            if abs(p.center.y - face_y) > 0.001:
                continue
            points = [(v.x, v.z) for v in (mesh.vertices[i].co for i in p.vertices)]
            poly = shapely.Polygon(points)
            if poly.is_valid and poly.area > 1e-6:
                polys.append(poly)
        if not polys:
            return None
        union = shapely.ops.unary_union(polys)
        geoms = union.geoms if union.geom_type == "MultiPolygon" else [union]
        face_polys = [g.simplify(1e-5) for g in geoms if g.geom_type == "Polygon" and g.area > 1e-6]
        if not face_polys:
            return None
        return face_polys, face_y

    @classmethod
    def create_wall_covering(cls, wall_obj: bpy.types.Object, facing_cursor: bool = True) -> Optional[bpy.types.Object]:
        """Create a wall covering panel on the wall side face, offset outwards by the type layer thickness."""
        side = cls.get_wall_side_facing_cursor(wall_obj)
        if not facing_cursor:
            side = -side
        face = cls.get_wall_side_face(wall_obj, side)
        if face is None:
            return None
        face_polys, face_y = face
        centroid = shapely.ops.unary_union(face_polys).centroid
        cx, cz = centroid.x, centroid.y
        # Covering local frame: XY on the wall face (Y up), +Z is the outward face normal.
        matrix = wall_obj.matrix_world @ Matrix(
            (
                (-side, 0.0, 0.0, cx),
                (0.0, 0.0, side, face_y),
                (0.0, 1.0, 0.0, cz),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        obj = tool.Spatial.create_object("Covering")
        obj.matrix_world = matrix
        tool.Spatial.assign_type_to_obj(obj)
        bpy.context.view_layer.update()
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        cls.set_wall_covering_representation(obj, face_polys, side, cx, cz)
        return obj

    @classmethod
    def set_wall_covering_representation(
        cls, obj: bpy.types.Object, face_polys: list[shapely.Polygon], side: float, cx: float, cz: float
    ) -> None:
        """Create the covering body as face profile extrusions along local +Z by the type layer thickness."""
        element = tool.Ifc.get_entity(obj)
        assert element
        relating_type = ifcopenshell.util.element.get_type(element)
        material = ifcopenshell.util.element.get_material(relating_type, should_skip_usage=True)
        depth = 0.0
        if material and material.is_a("IfcMaterialLayerSet"):
            depth = sum(layer.LayerThickness for layer in material.MaterialLayers)
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file)

        def local_coords(ring: shapely.LinearRing) -> list[list[float]]:
            return [[-side * (x - cx) / unit_scale, (z - cz) / unit_scale] for x, z in ring.coords[:-1]]

        items = []
        for poly in face_polys:
            # Mirroring X for side=1.0 flips ring winding, pre-orient so the outer ring ends up CCW.
            poly = shapely.geometry.polygon.orient(poly, -side)
            outer = builder.polyline(local_coords(poly.exterior), closed=True)
            if poly.interiors:
                inners = [builder.polyline(local_coords(ring), closed=True) for ring in poly.interiors]
                items.append(builder.extrude(builder.profile(outer, inner_curves=inners), magnitude=depth))
            else:
                items.append(builder.extrude(outer, magnitude=depth))

        old_body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if old_body:
            context = old_body.ContextOfItems
            ifcopenshell.api.geometry.unassign_representation(ifc_file, product=element, representation=old_body)
            ifcopenshell.api.geometry.remove_representation(ifc_file, representation=old_body)
        else:
            context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        new_body = builder.get_representation(context, items)
        ifcopenshell.api.geometry.assign_representation(ifc_file, product=element, representation=new_body)
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=new_body)
