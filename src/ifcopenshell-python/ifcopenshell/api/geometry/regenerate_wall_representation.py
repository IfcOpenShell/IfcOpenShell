# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import json
import numpy as np
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
from collections import namedtuple
from math import sin, cos
from typing import Optional

# https://stackoverflow.com/a/9184560/9627415
# Possible optimisation to linalg.norm?

PrioritisedLayer = namedtuple("PrioritisedLayer", "priority thickness")


def regenerate_wall_representation(
    file: ifcopenshell.file,
    wall: ifcopenshell.entity_instance,
    length: float = 1.0,
    height: float = 1.0,
    angle: Optional[float] = None,
) -> ifcopenshell.entity_instance:
    """
    Regenerate the body representation of a wall taking into account connections.

    IFC defines how a standard (case) wall should behave that has a material
    layer set and connections to other walls using IfcRelConnectsPathElements.
    This function will regenerate the body geometry of a wall taking into
    account the notches, butts, mitres, etc in the wall due to connections with
    other walls.

    A standard wall has a 2D axis line as well as parameters defined in terms
    of layer thicknesses and priorities. The body geometry is defined as a 2D
    XY profile which is extruded in the +Z direction. For this function to
    work, a wall must have these defined and the project must have an axis and
    body representation context.

    For non-sloped walls, a 2D profile is generated and extruded in the +Z
    direction. The profile may be a composite profile, if the wall is split due
    to wall joins along the path of the wall that protrude all the way through
    the wall.

    For sloped walls, a basic rectangular 2D profile is extruded, and then
    additional extrusions are generated for each connection that boolean
    difference the base extrusion.

    This will also update the axis line representation (e.g. trim the axis line
    to any connections).

    The wall's object placement will also be updated such that the placement is
    equivalent to the axis line's start point (which therefore becomes (0.0,
    0.0)). This is a logical, consistent, and useful placement coordinate
    (especially for apps that can pivot using this point).

    All this functionality relies on the Plan/Axis/GRAPH_VIEW representation
    context. It will be created if it does not exist.

    :param wall: The IfcWall for the representation,
        only Model/Body/MODEL_VIEW type of representations are currently supported.
    :param length: If the wall doesn't have an axis length, this is the default
        length in SI units.
    :param height: If the wall doesn't already have a height, this is the
        default height in SI units.
    :param angle: If the wall doesn't already have a slope, this is the default
        angle in radians. Left as none or 0 defines no slope.
    :return: The newly generated body IfcShapeRepresentation
    """
    return Regenerator(file).regenerate(wall, length=length, height=height, angle=angle)


class Regenerator:
    def __init__(self, file):
        self.file = file
        self.body = ifcopenshell.util.representation.get_context(file, "Model", "Body", "MODEL_VIEW")
        self.axis = ifcopenshell.util.representation.get_context(file, "Plan", "Axis", "GRAPH_VIEW")
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
        self.is_angled = False

        if not self.axis:
            if not (plan := ifcopenshell.util.representation.get_context(file, "Plan")):
                plan = ifcopenshell.api.context.add_context(file, context_type="Plan")
            self.axis = ifcopenshell.api.context.add_context(
                file, context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent=plan
            )

    def regenerate(self, wall, length=1.0, height=1.0, angle=None):
        self.fallback_length = length / self.unit_scale
        self.fallback_height = height / self.unit_scale
        self.fallback_angle = angle
        layers = self.get_layers(wall)
        if not layers:
            return
        reference = ifcopenshell.util.representation.get_reference_line(wall, self.fallback_length)
        self.reference_p1, self.reference_p2 = reference
        self.wall_vectors = self.get_wall_vectors(wall)
        axes = self.get_axes(wall, reference, layers, self.wall_vectors["a"])
        self.miny = axes[0][0][1]
        self.maxy = axes[-1][0][1]
        self.end_point = None
        self.start_points = []
        self.start_vector = np.array((0.0, 0.0, 1.0))
        self.start_offset = 0.0
        self.atpath_points = []
        self.split_points = []
        self.maxpath_points = []
        self.minpath_points = []
        self.end_points = []
        self.end_vector = np.array((0.0, 0.0, 1.0))
        self.end_offset = 0.0
        manual_booleans = self.get_manual_booleans(wall)

        for rel in wall.ConnectedTo:
            if rel.is_a("IfcRelConnectsPathElements"):
                wall2 = rel.RelatedElement
                layers1 = self.combine_layers(layers.copy(), rel.RelatingPriorities)
                layers2 = self.combine_layers(self.get_layers(wall2), rel.RelatedPriorities)
                if not layers1 or not layers2:
                    continue
                self.join(wall, wall2, layers1, layers2, rel.RelatingConnectionType, rel.RelatedConnectionType)

        for rel in wall.ConnectedFrom:
            if rel.is_a("IfcRelConnectsPathElements"):
                wall2 = rel.RelatingElement
                layers1 = self.combine_layers(layers.copy(), rel.RelatedPriorities)
                layers2 = self.combine_layers(self.get_layers(wall2), rel.RelatingPriorities)
                if not layers1 or not layers2:
                    continue
                self.join(wall, wall2, layers1, layers2, rel.RelatedConnectionType, rel.RelatingConnectionType)

        miny = axes[-2][0][1]
        maxy = axes[-1][0][1]
        if not self.start_points:
            minx = axes[0][0][0]
            self.start_points = [
                np.array((minx, axes[0][0][1])),
                np.array((minx, axes[-1][0][1])),
            ]
        if not self.end_points:
            maxx = axes[0][1][0]
            self.end_points = [
                np.array((maxx, axes[0][0][1])),
                np.array((maxx, axes[-1][0][1])),
            ]

        if self.start_points[0][1] > self.start_points[-1][1]:  # Canonicalise to the +Y direction
            self.start_points.reverse()
        if self.end_points[0][1] > self.end_points[-1][1]:  # Canonicalise to the +Y direction
            self.end_points.reverse()

        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)

        # Don't offset wall if there are manual booleans, because that'll also shift operands
        offset = None if manual_booleans else self.reference_p1 * -1

        if self.is_angled:
            start_points = [p.copy() for p in self.start_points]
            end_points = [p.copy() for p in self.end_points]
            if self.end_offset > 0:
                for point in end_points:
                    point[0] += self.end_offset
            if self.start_offset < 0:
                for point in start_points:
                    point[0] += self.start_offset
            points = []
            points.extend(start_points)
            end_points.reverse()
            points.extend(end_points)
            item = builder.extrude(
                builder.polyline(points, closed=True, position_offset=offset),
                magnitude=self.wall_vectors["d"],
                extrusion_vector=self.wall_vectors["z"],
            )

            operands = []
            if not np.allclose(self.start_vector, np.array((0.0, 0.0, 1.0))):
                points = self.start_points.copy()
                while ifcopenshell.util.shape_builder.is_x(points[0][1], points[1][1]):
                    points.pop(0)
                while ifcopenshell.util.shape_builder.is_x(points[-1][1], points[-2][1]):
                    points.pop()
                newx = min([p[0] for p in points]) - abs(self.start_offset)
                p1 = points[-1].copy()
                p1[0] = newx
                p2 = p1.copy()
                p2[1] = points[0][1]
                points.extend((p1, p2))
                magnitude = np.linalg.norm(self.start_vector * (self.wall_vectors["h"] / self.start_vector[2]))
                operands.append(
                    builder.extrude(
                        builder.polyline(points, closed=True, position_offset=offset),
                        magnitude=magnitude,
                        extrusion_vector=self.start_vector,
                    )
                )

            if not np.allclose(self.end_vector, np.array((0.0, 0.0, 1.0))):
                points = self.end_points.copy()
                while ifcopenshell.util.shape_builder.is_x(points[0][1], points[1][1]):
                    points.pop(0)
                while ifcopenshell.util.shape_builder.is_x(points[-1][1], points[-2][1]):
                    points.pop()

                newx = max([p[0] for p in points]) + abs(self.end_offset)
                p1 = points[-1].copy()
                p1[0] = newx
                p2 = p1.copy()
                p2[1] = points[0][1]
                points.extend((p1, p2))
                magnitude = np.linalg.norm(self.end_vector * (self.wall_vectors["h"] / self.end_vector[2]))
                operands.append(
                    builder.extrude(
                        builder.polyline(points, closed=True, position_offset=offset),
                        magnitude=magnitude,
                        extrusion_vector=self.end_vector,
                    )
                )

            for atpath_vector, points in self.atpath_points:
                if len(points) <= 2:
                    continue
                magnitude = np.linalg.norm(atpath_vector * (self.wall_vectors["h"] / atpath_vector[2]))
                operands.append(
                    builder.extrude(
                        builder.polyline(points, closed=True, position_offset=offset),
                        magnitude=magnitude,
                        extrusion_vector=atpath_vector,
                    )
                )

            if operands:
                item = ifcopenshell.api.geometry.add_boolean(self.file, first_item=item, second_items=operands)[-1]
        else:
            # A wall footprint may be multiple profiles if the wall is split into two due to an ATPATH connection
            profiles = []
            minx = max([p[0] for p in self.start_points])
            maxx = min([p[0] for p in self.end_points])
            split_points = []
            for points in sorted(self.split_points, key=lambda x: x[0][0]):  # Sort islands in the +X direction
                if any([p[0] > maxx or p[0] < minx for p in points]):  # Can't have anything outside our start/end
                    continue
                split_points.append(points)
            start_points = [p.copy() for p in self.start_points]
            end_points = [p.copy() for p in self.end_points]
            split_points.insert(0, start_points)
            split_points.append(end_points)
            split_points = iter(split_points)

            if maxy < miny:
                self.maxpath_points, self.minpath_points = self.minpath_points, self.maxpath_points
                if self.maxpath_points:
                    self.maxpath_points[0] = list(reversed(self.maxpath_points[0]))
                if self.minpath_points:
                    self.minpath_points[0] = list(reversed(self.minpath_points[0]))

            while True:
                # Draw each profile as clockwise starting from (minx, miny)
                start_split = next(split_points, None)
                if not start_split:
                    break
                end_split = next(split_points, None)
                if not end_split:
                    break
                maxy_minx = start_split[-1][0]
                maxy_maxx = end_split[-1][0]
                miny_minx = start_split[0][0]
                miny_maxx = end_split[0][0]
                # Do more defensive checks here?
                points = start_split

                remaining_path_points = []
                for maxpath_points in self.maxpath_points:
                    if maxpath_points[0][0] > maxy_minx and maxpath_points[-1][0] < maxy_maxx:
                        points.extend(maxpath_points)
                    else:
                        remaining_path_points.append(maxpath_points)
                self.maxpath_points = remaining_path_points

                points.extend(end_split[::-1])

                remaining_path_points = []
                for minpath_points in self.minpath_points:
                    if minpath_points[0][0] < miny_maxx and minpath_points[-1][0] > miny_minx:
                        points.extend(minpath_points)
                    else:
                        remaining_path_points.append(minpath_points)
                self.minpath_points = remaining_path_points

                profiles.append(builder.profile(builder.polyline(points, closed=True, position_offset=offset)))

            for points in self.maxpath_points + self.minpath_points:
                profiles.append(builder.profile(builder.polyline(points, closed=True, position_offset=offset)))

            if len(profiles) > 1:
                profile = self.file.createIfcCompositeProfileDef("AREA", Profiles=profiles)
            else:
                profile = profiles[0]

            item = builder.extrude(profile, magnitude=self.wall_vectors["d"], extrusion_vector=self.wall_vectors["z"])
        for boolean in self.get_manual_booleans(wall):
            boolean.FirstOperand = item
            item = boolean

        body_rep = builder.get_representation(self.body, items=[item])
        if old_rep := ifcopenshell.util.representation.get_representation(wall, self.body):
            ifcopenshell.util.element.replace_element(old_rep, body_rep)
            ifcopenshell.util.element.remove_deep2(self.file, old_rep)
        else:
            ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=body_rep)

        item = builder.polyline([self.reference_p1, self.reference_p2], position_offset=offset)
        axis_rep = builder.get_representation(self.axis, items=[item])
        if old_rep := ifcopenshell.util.representation.get_representation(wall, self.axis):
            ifcopenshell.util.element.replace_element(old_rep, axis_rep)
            ifcopenshell.util.element.remove_deep2(self.file, old_rep)
        else:
            ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=axis_rep)

        if not np.allclose(self.reference_p1, np.array((0.0, 0.0))) and not manual_booleans:
            children = []
            for referenced_placement in wall.ObjectPlacement.ReferencedByPlacements:
                matrix = ifcopenshell.util.placement.get_local_placement(referenced_placement)
                children.append((matrix, referenced_placement.PlacesObject))

            matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
            matrix[:, 3] = matrix @ np.concatenate((self.reference_p1, (0, 1)))
            ifcopenshell.api.geometry.edit_object_placement(
                self.file, product=wall, matrix=matrix, is_si=False, should_transform_children=True
            )

            # Restore children to their previous location
            for matrix, elements in children:
                for element in elements:
                    ifcopenshell.api.geometry.edit_object_placement(
                        self.file, product=element, matrix=matrix, is_si=False, should_transform_children=True
                    )

        return body_rep

    def join(self, wall1, wall2, layers1, layers2, connection1, connection2):
        if connection1 == "NOTDEFINED" or connection2 == "NOTDEFINED":
            return
        if connection1 == "ATPATH" and connection2 == "ATPATH":
            return

        reference1 = ifcopenshell.util.representation.get_reference_line(wall1, self.fallback_length)
        reference2 = ifcopenshell.util.representation.get_reference_line(wall2, self.fallback_length)
        wall_vectors2 = self.get_wall_vectors(wall2)
        axes1 = self.get_axes(wall1, reference1, layers1, self.wall_vectors["a"])
        axes2 = self.get_axes(wall2, reference2, layers2, wall_vectors2["a"])
        matrix1i = np.linalg.inv(ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement))
        matrix2 = ifcopenshell.util.placement.get_local_placement(wall2.ObjectPlacement)

        # Convert wall2 data to wall1 local coordinates
        for axis in axes2:
            axis[0] = (matrix1i @ matrix2 @ np.concatenate((axis[0], (0, 1))))[:2]
            axis[1] = (matrix1i @ matrix2 @ np.concatenate((axis[1], (0, 1))))[:2]
        reference2[0] = (matrix1i @ matrix2 @ np.concatenate((reference2[0], (0, 1))))[:2]
        reference2[1] = (matrix1i @ matrix2 @ np.concatenate((reference2[1], (0, 1))))[:2]
        wall_vectors2["z"] = (matrix1i @ matrix2 @ np.append(wall_vectors2["z"], 0.0))[:3]
        wall_vectors2["y"] = (matrix1i @ matrix2 @ np.append(wall_vectors2["y"], 0.0))[:3]

        axis2 = axes2[0]  # Take an arbitrary axis of wall2
        if ifcopenshell.util.shape_builder.is_x(axis2[0][1], axis2[1][1]):
            return  # Parallel

        # Sort axes from interior to exterior
        if connection1 == "ATEND":
            if axes2[0][0][0] > axes2[-1][0][0]:  # We process layers in a +X direction
                axes2 = list(reversed(axes2))
                layers2 = list(reversed(layers2))
        elif connection1 == "ATSTART":
            if axes2[-1][0][0] > axes2[0][0][0]:  # We process layers in a -X direction
                axes2 = list(reversed(axes2))
                layers2 = list(reversed(layers2))

        axis2 = axes2[0]  # Take an arbitrary axis of wall2
        if connection2 == "ATSTART":
            axis2 = [axis2[1], axis2[0]]  # Flip direction so the axis "points" in the direction of join
        if axis2[0][1] < axis2[1][1]:  # Pointing +Y
            if axes1[-1][0][1] < axes1[0][0][1]:  # We process layers1 in a +Y direction
                axes1 = list(reversed(axes1))
                layers1 = list(reversed(layers1))
        else:  # Pointing -Y
            if axes1[0][0][1] < axes1[-1][0][1]:  # We process layers1 in a -Y direction
                axes1 = list(reversed(axes1))
                layers1 = list(reversed(layers1))

        if connection1 == "ATPATH":
            first_axis2 = axes2[0]
            last_axis2 = axes2[-1]
            first_y = axes1[0][0][1]
            last_y = axes1[-1][0][1]
            p0 = np.array((ifcopenshell.util.shape_builder.intersect_x_axis_2d(*first_axis2, y=first_y), first_y))
            pN = np.array((ifcopenshell.util.shape_builder.intersect_x_axis_2d(*last_axis2, y=first_y), first_y))

            # Generate CurveOnRelating/RelatedElement
            points = [p0]
            axes2 = iter(axes2)
            axis2 = next(axes2)
            for layer2 in layers2:
                ys = iter([a[0][1] for a in axes1])
                y = next(ys)
                for layer1 in layers1:
                    if layer2.priority <= layer1.priority:
                        break
                    y = next(ys)
                p1 = np.array((ifcopenshell.util.shape_builder.intersect_x_axis_2d(*axis2, y=y), y))
                axis2 = next(axes2)
                p2 = np.array((ifcopenshell.util.shape_builder.intersect_x_axis_2d(*axis2, y=y), y))
                if points and np.allclose(points[-1], p1):
                    points[-1] = p2  # Just slide along previous point
                else:
                    points.extend((p1, p2))

            # The curve must end at pN
            if not np.allclose(points[-1], pN):
                points.append(pN)

            # Categorise our points into a segment that either splits or cuts the wall
            split_ys = {first_y, last_y}
            segment = []
            atpath_vector = self.get_join_vector(self.wall_vectors["y"], wall_vectors2["y"])
            self.atpath_points.append((atpath_vector, points))
            for point in points:
                segment.append(point)
                if len(segment) == 1:  # Not enough points to categorise the segment
                    continue
                elif {segment[0][1], segment[-1][1]} == split_ys:  # This segment splits the wall
                    if segment[0][1] > segment[-1][1]:  # Go in the +Y direction
                        segment.reverse()
                    self.split_points.append(segment)
                    segment = []
                elif segment[0][1] == segment[-1][1]:  # This segment cuts some of the wall
                    if segment[0][1] == self.maxy:  # Go in the +X direction
                        if segment[0][0] > segment[-1][0]:
                            segment.reverse()
                        self.maxpath_points.append(segment)
                    elif segment[0][1] == self.miny:  # Go in the -X direction
                        if segment[-1][0] > segment[0][0]:
                            segment.reverse()
                        self.minpath_points.append(segment)
                    segment = []
        elif connection2 == "ATPATH":
            points = []
            ys = iter([a[0][1] for a in axes1])
            y = next(ys)
            for layer1 in layers1:
                axes2_iter = iter(axes2)
                axis2 = next(axes2_iter)
                for layer2 in layers2:
                    if layer1.priority <= layer2.priority:
                        break
                    axis2 = next(axes2_iter)
                x = ifcopenshell.util.shape_builder.intersect_x_axis_2d(*axis2, y=y)
                p1 = np.array((x, y))
                y = next(ys)
                x = ifcopenshell.util.shape_builder.intersect_x_axis_2d(*axis2, y=y)
                p2 = np.array((x, y))
                if points and np.allclose(points[-1], p1):
                    points.append(p2)
                else:
                    points.extend((p1, p2))

            if connection1 == "ATSTART":
                self.start_points = points
                self.start_vector = self.get_join_vector(self.wall_vectors["y"], wall_vectors2["y"])
                self.start_offset = (self.start_vector * (self.wall_vectors["h"] / self.start_vector[2]))[0]
                self.reference_p1[0] = ifcopenshell.util.shape_builder.intersect_x_axis_2d(
                    *reference2, y=reference1[0][1]
                )
            elif connection1 == "ATEND":
                self.end_points = points
                self.end_vector = self.get_join_vector(self.wall_vectors["y"], wall_vectors2["y"])
                self.end_offset = (self.end_vector * (self.wall_vectors["h"] / self.end_vector[2]))[0]
                self.reference_p2[0] = ifcopenshell.util.shape_builder.intersect_x_axis_2d(
                    *reference2, y=reference1[0][1]
                )
        else:  # A connection at either end of both walls
            last_y = axes1[-1][0][1]
            ys = iter([a[0][1] for a in axes1])

            last_axis2 = axes2[-1]
            axes2 = iter(axes2)
            axis2 = next(axes2)
            y = next(ys)
            x = ifcopenshell.util.shape_builder.intersect_x_axis_2d(*axis2, y=y)
            points = [np.array((x, y))]

            layers1 = iter(layers1)
            layers2 = iter(layers2)
            layer1 = next(layers1, None)
            layer2 = next(layers2, None)

            # This creates "mitering" behaviour which is an ambiguity by bSI.
            while layer1 and layer2:
                if layer1.priority > layer2.priority:
                    axis2 = next(axes2)
                    x = ifcopenshell.util.shape_builder.intersect_x_axis_2d(*axis2, y=y)
                    layer2 = next(layers2, None)
                elif layer2.priority > layer1.priority:
                    y = next(ys)
                    x = ifcopenshell.util.shape_builder.intersect_x_axis_2d(*axis2, y=y)
                    layer1 = next(layers1, None)
                else:
                    y = next(ys)
                    x = ifcopenshell.util.shape_builder.intersect_x_axis_2d(*next(axes2), y=y)
                    layer1 = next(layers1, None)
                    layer2 = next(layers2, None)
                points.append(np.array((x, y)))

            if points[-1][1] != last_y:
                points.append(
                    np.array((ifcopenshell.util.shape_builder.intersect_x_axis_2d(*last_axis2, y=last_y), last_y))
                )

            if connection1 == "ATSTART":
                self.start_points = points
                self.start_vector = self.get_join_vector(self.wall_vectors["y"], wall_vectors2["y"])
                self.start_offset = (self.start_vector * (self.wall_vectors["h"] / self.start_vector[2]))[0]
                self.reference_p1[0] = ifcopenshell.util.shape_builder.intersect_x_axis_2d(
                    *reference2, y=reference1[0][1]
                )
            elif connection1 == "ATEND":
                self.end_points = points
                self.end_vector = self.get_join_vector(self.wall_vectors["y"], wall_vectors2["y"])
                self.end_offset = (self.end_vector * (self.wall_vectors["h"] / self.end_vector[2]))[0]
                self.reference_p2[0] = ifcopenshell.util.shape_builder.intersect_x_axis_2d(
                    *reference2, y=reference1[0][1]
                )

    def get_layers(self, wall) -> list:
        material = ifcopenshell.util.element.get_material(wall, should_skip_usage=True)
        if not material or not material.is_a("IfcMaterialLayerSet"):
            return []
        return [PrioritisedLayer(getattr(l, "Priority", 0) or 0, l.LayerThickness) for l in material.MaterialLayers]

    def combine_layers(self, layers, override_priorities):
        results = []
        if override_priorities:
            for i, priority in enumerate(override_priorities[: len(layers)]):
                layers[i][0] = priority
        if not layers:
            return []
        results = [layers.pop(0)]
        for layer in layers:
            if not layer.thickness:
                continue
            if layer.priority == results[-1].priority:
                results[-1] = PrioritisedLayer(layer.priority, results[-1].thickness + layer.thickness)
            else:
                results.append(layer)
        return results

    def get_wall_vectors(self, wall):
        if body := ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW"):
            for item in ifcopenshell.util.representation.resolve_representation(body).Items:
                while item.is_a("IfcBooleanResult"):
                    item = item.FirstOperand
                if item.is_a("IfcExtrudedAreaSolid"):
                    z = np.array(item.ExtrudedDirection.DirectionRatios)
                    z /= np.linalg.norm(z)
                    y = np.cross(z, np.array((1.0, 0.0, 0.0)))
                    d = item.Depth
                    h = (z * d)[2]
                    a = ifcopenshell.util.shape_builder.np_angle_signed(np.array((0.0, 1.0)), z[1:])
                    if not ifcopenshell.util.shape_builder.is_x(a, 0):
                        self.is_angled = True
                    return {"z": z, "y": y, "a": a, "d": d, "h": h}
        elif self.fallback_angle:
            a = self.fallback_angle
            z = np.array([0.0, sin(a), cos(a)])
            y = np.cross(z, np.array((1.0, 0.0, 0.0)))
            h = self.fallback_height
            d = np.linalg.norm(z * (h / z[2]))
            if not ifcopenshell.util.shape_builder.is_x(a, 0):
                self.is_angled = True
            return {"z": z, "y": y, "a": a, "d": d, "h": h}
        return {
            "z": np.array((0.0, 0.0, 1.0)),
            "y": np.array((0.0, 1.0, 0.0)),
            "a": 0.0,
            "d": self.fallback_height,
            "h": self.fallback_height,
        }

    def get_join_vector(self, y1, y2):
        result = np.cross(y1, y2)
        if result[2] < 0:
            return result * -1
        return result

    def get_axes(self, wall: ifcopenshell.entity_instance, reference, layers: list[PrioritisedLayer], angle: float):
        axes = [[p.copy() for p in reference]]
        # Apply usage to convert the Reference line into MlsBase
        sense_factor = 1
        if (usage := ifcopenshell.util.element.get_material(wall)) and usage.is_a("IfcMaterialLayerSetUsage"):
            for point in axes[0]:
                point[1] += usage.OffsetFromReferenceLine
            sense_factor = 1 if usage.DirectionSense == "POSITIVE" else -1

        for layer in layers:
            y_offset = (layer.thickness * sense_factor) / cos(angle)
            axes.append([p.copy() + np.array((0.0, y_offset)) for p in axes[-1]])
        return axes

    def get_manual_booleans(self, element: ifcopenshell.entity_instance):
        if pset := ifcopenshell.util.element.get_pset(element, "BBIM_Boolean"):
            try:
                return [self.file.by_id(boolean_id) for boolean_id in json.loads(pset["Data"])]
            except:
                return []
        return []
