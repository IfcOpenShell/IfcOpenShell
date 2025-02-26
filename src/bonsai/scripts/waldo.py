import numpy as np
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.api.unit
import ifcopenshell.api.project
import ifcopenshell.api.context
import ifcopenshell.api.spatial
import ifcopenshell.api.material
import ifcopenshell.api.geometry
import ifcopenshell.util.shape_builder
import ifcopenshell.util.element

# from ifcopenshell.util.shape_builder import VectorType, SequenceOfVectors
from itertools import cycle
from collections import namedtuple

f = ifcopenshell.api.project.create_file()

project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
meters = ifcopenshell.api.unit.add_si_unit(f)
ifcopenshell.api.unit.assign_unit(f, units=[meters])

model = ifcopenshell.api.context.add_context(f, context_type="Model")
plan = ifcopenshell.api.context.add_context(f, context_type="Plan")
axis = ifcopenshell.api.context.add_context(
    f, context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent=plan
)
body = ifcopenshell.api.context.add_context(
    f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
)
material1 = ifcopenshell.api.material.add_material(f, name="material1", category="material1")
material2 = ifcopenshell.api.material.add_material(f, name="material2", category="material2")
site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite")
ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
builder = ifcopenshell.util.shape_builder.ShapeBuilder(f)

style = ifcopenshell.api.style.add_style(f)
attributes = {"SurfaceColour": {"Name": None, "Red": 1.0, "Green": 0.5, "Blue": 0.5}, "Transparency": 0.0}
ifcopenshell.api.style.add_surface_style(f, style=style, ifc_class="IfcSurfaceStyleShading", attributes=attributes)
ifcopenshell.api.style.assign_material_style(f, material=material1, style=style, context=body)

style = ifcopenshell.api.style.add_style(f)
attributes = {"SurfaceColour": {"Name": None, "Red": 0.5, "Green": 0.5, "Blue": 1.0}, "Transparency": 0.0}
ifcopenshell.api.style.add_surface_style(f, style=style, ifc_class="IfcSurfaceStyleShading", attributes=attributes)
ifcopenshell.api.style.assign_material_style(f, material=material2, style=style, context=body)


def test_wall(offset, p1, p2, p3, p4):
    offset *= 1.5
    wall_type_a = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWallType", name="A")
    wall_type_b = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWallType", name="B")

    set_a = ifcopenshell.api.material.add_material_set(f, set_type="IfcMaterialLayerSet")
    structure = ifcopenshell.api.material.add_layer(f, layer_set=set_a, material=material1, name="structure")
    structure.Priority = p1
    structure.LayerThickness = 0.1
    cladding = ifcopenshell.api.material.add_layer(f, layer_set=set_a, material=material2, name="cladding")
    cladding.Priority = p2
    cladding.LayerThickness = 0.05

    set_b = ifcopenshell.api.material.add_material_set(f, set_type="IfcMaterialLayerSet")
    structure = ifcopenshell.api.material.add_layer(f, layer_set=set_b, material=material1, name="structure")
    structure.Priority = p3
    structure.LayerThickness = 0.1
    cladding = ifcopenshell.api.material.add_layer(f, layer_set=set_b, material=material2, name="cladding")
    cladding.Priority = p4
    cladding.LayerThickness = 0.05

    ifcopenshell.api.material.assign_material(f, products=[wall_type_a], material=set_a)
    ifcopenshell.api.material.assign_material(f, products=[wall_type_b], material=set_b)

    for i, rotation in enumerate((-90, -75, -105, 90, 75, 105)):
        for i2, connection in enumerate(("ATEND", "ATSTART", "MIX")):
            # if rotation != -90:
            #     continue
            # if connection != "ATEND":
            #     continue
            wall_a = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name=f"A{p1}{p2}")
            wall_b = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name=f"B{p3}{p4}")
            wall_c = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name=f"C{p3}{p4}")

            ifcopenshell.api.spatial.assign_container(f, products=[wall_a, wall_b, wall_c], relating_structure=site)

            ifcopenshell.api.type.assign_type(f, related_objects=[wall_a], relating_type=wall_type_a)
            ifcopenshell.api.type.assign_type(f, related_objects=[wall_b], relating_type=wall_type_b)
            ifcopenshell.api.type.assign_type(f, related_objects=[wall_c], relating_type=wall_type_b)

            axis_a = builder.polyline(((0.0, 0.0), (1.0, 0.0)))
            axis_b = builder.polyline(((0.0, 0.0), (1.0, 0.0)))
            axis_c = builder.polyline(((0.0, 0.0), (1.0, 0.0)))
            rep_a = builder.get_representation(axis, [axis_a])
            rep_b = builder.get_representation(axis, [axis_b])
            rep_c = builder.get_representation(axis, [axis_c])

            ifcopenshell.api.geometry.assign_representation(f, product=wall_a, representation=rep_a)
            ifcopenshell.api.geometry.assign_representation(f, product=wall_b, representation=rep_b)
            ifcopenshell.api.geometry.assign_representation(f, product=wall_c, representation=rep_c)

            x_offset = i * 2
            x_offset += i2 * (2 * 6)
            if connection == "ATEND":
                sign_offset = 0 if rotation < 0 else 1
                matrix_a = np.eye(4)
                matrix_a[:, 3][0:3] = (0 + x_offset, 0 + offset + sign_offset, 0)
                matrix_b = np.eye(4)
                matrix_b = ifcopenshell.util.placement.rotation(rotation, "Z") @ matrix_b
                matrix_b[:, 3][0:3] = (1 + x_offset, 1 + offset - sign_offset, 0)
                matrix_c = np.eye(4)
                matrix_c = ifcopenshell.util.placement.rotation(rotation, "Z") @ matrix_c
                matrix_c[:, 3][0:3] = (0.5 + x_offset, 0.5 + offset, 0)
                ifcopenshell.api.geometry.edit_object_placement(f, product=wall_a, matrix=matrix_a)
                ifcopenshell.api.geometry.edit_object_placement(f, product=wall_b, matrix=matrix_b)
                ifcopenshell.api.geometry.edit_object_placement(f, product=wall_c, matrix=matrix_c)

                ifcopenshell.api.geometry.connect_path(
                    f,
                    relating_element=wall_a,
                    related_element=wall_b,
                    relating_connection="ATEND",
                    related_connection="ATEND",
                )
                ifcopenshell.api.geometry.connect_path(
                    f,
                    relating_element=wall_c,
                    related_element=wall_a,
                    relating_connection="ATEND",
                    related_connection="ATPATH",
                )
            elif connection == "ATSTART":
                sign_offset = 0 if rotation < 0 else 1
                matrix_a = np.eye(4)
                matrix_a[:, 3][0:3] = (0 + x_offset, 1 + offset - sign_offset, 0)
                matrix_b = np.eye(4)
                matrix_b = ifcopenshell.util.placement.rotation(rotation, "Z") @ matrix_b
                matrix_b[:, 3][0:3] = (0 + x_offset, 1 + offset - sign_offset, 0)
                ifcopenshell.api.geometry.edit_object_placement(f, product=wall_a, matrix=matrix_a)
                ifcopenshell.api.geometry.edit_object_placement(f, product=wall_b, matrix=matrix_b)

                ifcopenshell.api.geometry.connect_path(
                    f,
                    relating_element=wall_a,
                    related_element=wall_b,
                    relating_connection="ATSTART",
                    related_connection="ATSTART",
                )
            elif connection == "MIX":
                sign_offset = 0 if rotation < 0 else 1
                matrix_a = np.eye(4)
                matrix_a[:, 3][0:3] = (0 + x_offset, 1 + offset - sign_offset, 0)
                matrix_b = np.eye(4)
                matrix_b = ifcopenshell.util.placement.rotation(rotation, "Z") @ matrix_b
                matrix_b[:, 3][0:3] = (1 + x_offset, 1 + offset - sign_offset, 0)
                ifcopenshell.api.geometry.edit_object_placement(f, product=wall_a, matrix=matrix_a)
                ifcopenshell.api.geometry.edit_object_placement(f, product=wall_b, matrix=matrix_b)

                ifcopenshell.api.geometry.connect_path(
                    f,
                    relating_element=wall_a,
                    related_element=wall_b,
                    relating_connection="ATEND",
                    related_connection="ATSTART",
                )

            Foo(f, body, axis).regenerate(wall_a)
            Foo(f, body, axis).regenerate(wall_b)
            Foo(f, body, axis).regenerate(wall_c)


def create_type(name, layers):
    wall_type = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWallType", name=name)
    layer_set = ifcopenshell.api.material.add_material_set(f, set_type="IfcMaterialLayerSet")
    materials = cycle((material1, material2))
    for layer in layers:
        material = next(materials)
        item = ifcopenshell.api.material.add_layer(f, layer_set=layer_set, material=material, name="structure")
        item.Priority = layer[0]
        item.LayerThickness = layer[1]
    ifcopenshell.api.material.assign_material(f, products=[wall_type], material=layer_set)
    return wall_type


def test_atpath(offset):
    offset *= 1.5
    wall_type_a = create_type("A", [(1, 0.05), (2, 0.1), (3, 0.05)])
    wall_a = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="A123")
    ifcopenshell.api.spatial.assign_container(f, products=[wall_a], relating_structure=site)
    ifcopenshell.api.type.assign_type(f, related_objects=[wall_a], relating_type=wall_type_a)
    axis_a = builder.polyline(((0.0, 0.0), (30.0, 0.0)))
    rep_a = builder.get_representation(axis, [axis_a])
    ifcopenshell.api.geometry.assign_representation(f, product=wall_a, representation=rep_a)
    matrix_a = np.eye(4)
    matrix_a[:, 3][0:3] = (0, 0 + offset, 0)
    ifcopenshell.api.geometry.edit_object_placement(f, product=wall_a, matrix=matrix_a)

    def create_branch(name, p1, p2, p3, x, y, rotation):
        wall_type = create_type(name, [(p1, 0.05), (p2, 0.1), (p3, 0.05)])
        wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name=f"{name}{p1}{p2}{p3}")
        ifcopenshell.api.spatial.assign_container(f, products=[wall], relating_structure=site)
        ifcopenshell.api.type.assign_type(f, related_objects=[wall], relating_type=wall_type)
        axis_a = builder.polyline(((0.0, 0.0), (1.0, 0.0)))
        rep_a = builder.get_representation(axis, [axis_a])
        ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=rep_a)
        matrix_a = np.eye(4)
        matrix_a = ifcopenshell.util.placement.rotation(rotation, "Z") @ matrix_a
        matrix_a[:, 3][0:3] = (x, y + offset, 0)
        ifcopenshell.api.geometry.edit_object_placement(f, product=wall, matrix=matrix_a)
        ifcopenshell.api.geometry.connect_path(
            f,
            relating_element=wall,
            related_element=wall_a,
            relating_connection="ATEND",
            related_connection="ATPATH",
        )
        Foo(f, body, axis).regenerate(wall)

    create_branch("B", 1, 1, 1, 1, 1, -75)
    create_branch("C", 1, 2, 3, 2, 1, -75)
    create_branch("D", 1, 4, 2, 3, 1, -75)
    create_branch("E", 4, 4, 4, 4, 1, -75)
    create_branch("F", 4, 2, 4, 5, 1, -75)

    create_branch("B", 1, 1, 1, 0.5, -1, 75)
    create_branch("C", 1, 2, 3, 1.5, -1, 75)
    create_branch("D", 1, 4, 2, 2.5, -1, 75)
    create_branch("E", 4, 4, 4, 3.5, -1, 75)
    create_branch("F", 4, 2, 4, 4.5, -1, 75)

    Foo(f, body, axis).regenerate(wall_a)


PrioritisedLayer = namedtuple("PrioritisedLayer", "priority thickness")


class Foo:
    def __init__(self, file, body, axis):
        self.file = file
        self.body = body
        self.axis = axis

    def regenerate(self, wall):
        print("-" * 100)
        print(wall)
        layers = self.get_layers(wall)
        if not layers:
            return
        reference = self.get_reference_line(wall)
        self.reference_p1, self.reference_p2 = reference
        axes = self.get_axes(wall, reference, layers)
        self.miny = axes[0][0][1]
        self.maxy = axes[-1][0][1]
        self.end_point = None
        self.start_points = []
        self.split_points = []
        self.maxpath_points = []
        self.minpath_points = []
        self.end_points = []
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
        print("FINISHED")
        print(self.start_points)
        print(self.end_points)

        if self.start_points[0][1] > self.start_points[-1][1]:  # Canonicalise to the +Y direction
            self.start_points.reverse()
        if self.end_points[0][1] > self.end_points[-1][1]:  # Canonicalise to the +Y direction
            self.end_points.reverse()

        builder = ifcopenshell.util.shape_builder.ShapeBuilder(wall.file)
        # A wall footprint may be multiple profiles if the wall is split into two due to an ATPATH connection
        profiles = []
        split_points = sorted(self.split_points, key=lambda x: x[0][0])  # Sort islands in the +X direction
        split_points.insert(0, self.start_points)
        split_points.append(self.end_points)
        split_points = iter(split_points)

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
            # Do more defensive checks here
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

            profiles.append(builder.profile(builder.polyline(points, closed=True)))

        for points in self.maxpath_points + self.minpath_points:
            profiles.append(builder.profile(builder.polyline(points, closed=True)))

        if len(profiles) > 1:
            profile = wall.file.createIfcCompositeProfileDef("AREA", Profiles=profiles)
        else:
            profile = profiles[0]

        item = builder.extrude(profile, magnitude=1.0)
        rep = builder.get_representation(self.body, items=[item])
        if old_rep := ifcopenshell.util.representation.get_representation(wall, self.body):
            ifcopenshell.util.element.replace_element(old_rep, rep)
        else:
            ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=rep)

        item = builder.polyline([self.reference_p1, self.reference_p2])
        rep = builder.get_representation(self.axis, items=[item])
        if old_rep := ifcopenshell.util.representation.get_representation(wall, self.axis):
            ifcopenshell.util.element.replace_element(old_rep, rep)
        else:
            ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=rep)

    def join(self, wall1, wall2, layers1, layers2, connection1, connection2):
        if connection1 == "NOTDEFINED" or connection2 == "NOTDEFINED":
            return
        if connection1 == "ATPATH" and connection2 == "ATPATH":
            return
        print("joining", wall1, layers1, connection1)
        print("to", wall2, layers2, connection2)

        # axes = self.get_axes(wall2, layers2)
        reference1 = self.get_reference_line(wall1)
        reference2 = self.get_reference_line(wall2)
        axes1 = self.get_axes(wall1, reference1, layers1)
        axes2 = self.get_axes(wall2, reference2, layers2)
        matrix1i = np.linalg.inv(ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement))
        matrix2 = ifcopenshell.util.placement.get_local_placement(wall2.ObjectPlacement)
        print(axes1)
        print(axes2)

        # Convert wall2 data to wall1 local coordinates
        for axis in axes2:
            axis[0] = (matrix1i @ matrix2 @ np.concatenate((axis[0], (0, 1))))[:2]
            axis[1] = (matrix1i @ matrix2 @ np.concatenate((axis[1], (0, 1))))[:2]
        reference2[0] = (matrix1i @ matrix2 @ np.concatenate((reference2[0], (0, 1))))[:2]
        reference2[1] = (matrix1i @ matrix2 @ np.concatenate((reference2[1], (0, 1))))[:2]

        # Sort axes from interior to exterior
        if connection1 == "ATEND":
            if axes2[0][0][0] > axes2[-1][0][0]:  # We process layers in a +X direction
                axes2 = list(reversed(axes2))
                layers2 = list(reversed(layers2))
        elif connection1 == "ATSTART":
            if axes2[-1][0][0] > axes2[0][0][0]:  # We process layers in a -X direction
                axes2 = list(reversed(axes2))
                layers2 = list(reversed(layers2))

        # wall2_x = matrix2[:,0][:2]
        axis2 = axes2[0]  # Take an arbitrary axis
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

        print("modified")
        print(axes1)
        print(axes2)
        # Checked
        if connection1 == "ATPATH":
            first_axis2 = axes2[0]
            last_axis2 = axes2[-1]
            first_y = axes1[0][0][1]
            last_y = axes1[-1][0][1]
            p0 = np.array((self.intersect_axis(*first_axis2, y=first_y), first_y))
            pN = np.array((self.intersect_axis(*last_axis2, y=first_y), first_y))

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
                p1 = np.array((self.intersect_axis(*axis2, y=y), y))
                axis2 = next(axes2)
                p2 = np.array((self.intersect_axis(*axis2, y=y), y))
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
            for point in points:
                segment.append(point)
                if len(segment) == 1: # Not enough points to categorise the segment
                    continue
                elif {segment[0][1], segment[-1][1]} == split_ys: # This segment splits the wall
                    if segment[0][1] > segment[-1][1]:  # Go in the +Y direction
                        segment.reverse()
                    self.split_points.append(segment)
                    segment = []
                elif segment[0][1] == segment[-1][1]: # This segment cuts some of the wall
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
                x = self.intersect_axis(*axis2, y=y)
                p1 = np.array((x, y))
                y = next(ys)
                x = self.intersect_axis(*axis2, y=y)
                p2 = np.array((x, y))
                if points and np.allclose(points[-1], p1):
                    points.append(p2)
                else:
                    points.extend((p1, p2))

            if connection1 == "ATSTART":
                self.start_points = points
                self.reference_p1[0] = self.intersect_axis(*reference2, y=reference1[0][1])
            elif connection1 == "ATEND":
                self.end_points = points
                self.reference_p2[0] = self.intersect_axis(*reference2, y=reference1[0][1])
        else:
            last_y = axes1[-1][0][1]
            ys = iter([a[0][1] for a in axes1])

            last_axis2 = axes2[-1]
            axes2 = iter(axes2)
            axis2 = next(axes2)
            y = next(ys)
            x = self.intersect_axis(*axis2, y=y)
            points = [np.array((x, y))]

            layers1 = iter(layers1)
            layers2 = iter(layers2)
            layer1 = next(layers1, None)
            layer2 = next(layers2, None)

            # This creates "mitering" behaviour which is an ambiguity by bSI.
            while layer1 and layer2:
                print("considering", layer1, layer2)
                if layer1.priority > layer2.priority:
                    axis2 = next(axes2)
                    x = self.intersect_axis(*axis2, y=y)
                    layer2 = next(layers2, None)
                elif layer2.priority > layer1.priority:
                    y = next(ys)
                    x = self.intersect_axis(*axis2, y=y)
                    layer1 = next(layers1, None)
                else:
                    y = next(ys)
                    x = self.intersect_axis(*next(axes2), y=y)
                    layer1 = next(layers1, None)
                    layer2 = next(layers2, None)
                points.append(np.array((x, y)))

            print("points", points)
            if points[-1][1] != last_y:
                points.append(np.array((self.intersect_axis(*last_axis2, y=last_y), last_y)))

            if connection1 == "ATSTART":
                self.start_points = points
                self.reference_p1[0] = self.intersect_axis(*reference2, y=reference1[0][1])
            elif connection1 == "ATEND":
                self.end_points = points
                self.reference_p2[0] = self.intersect_axis(*reference2, y=reference1[0][1])

    def get_layers(self, wall) -> list:
        material = ifcopenshell.util.element.get_material(wall, should_skip_usage=True)
        if not material or not material.is_a("IfcMaterialLayerSet"):
            return []
        return [PrioritisedLayer(l.Priority or 0, l.LayerThickness) for l in material.MaterialLayers]

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

    def intersect_axis(self, p1, p2, y=0):
        # Assumes lines are horizontal
        x1, y1 = p1
        x2, y2 = p2
        t = (y - y1) / (y2 - y1)
        return x1 + t * (x2 - x1)

    def get_reference_line(self, wall):
        if axis := ifcopenshell.util.representation.get_representation(wall, "Plan", "Axis", "GRAPH_VIEW"):
            for item in ifcopenshell.util.representation.resolve_representation(axis).Items:
                if item.is_a("IfcPolyline"):
                    points = item.Points
                elif item.is_a("IfcIndexedPolyCurve"):
                    points = item.Points.CoordList
                else:
                    continue
                if points[0][0] < points[1][0]:  # An axis always goes in the +X direction
                    return [np.array(points[0]), np.array(points[1])]
                return [np.array(points[1]), np.array(points[0])]
        return [np.array((0.0, 0.0)), np.array((1.0, 0.0))]

    def get_axes(self, wall, reference, layers: list[PrioritisedLayer]):
        axes = [[p.copy() for p in reference]]
        # Apply usage to convert the Reference line into MlsBase
        sense_factor = 1
        if (usage := ifcopenshell.util.element.get_material(wall)) and usage.is_a("IfcMaterialLayerSetUage"):
            for point in axes[0]:
                point[1] += usage.OffsetFromReferenceLine
            sense_factor = 1 if usage.DirectionSense == "POSITIVE" else -1

        for layer in layers:
            axes.append([p.copy() + np.array((0.0, layer.thickness * sense_factor)) for p in axes[-1]])
        return axes


test_wall(0, 1, 1, 1, 1)
test_wall(1, 2, 1, 1, 2)
test_wall(2, 2, 1, 1, 1)
test_wall(3, 1, 2, 1, 1)
test_wall(4, 1, 2, 1, 2)
test_wall(5, 3, 1, 2, 4)
test_atpath(7)


f.write("/home/dion/wall.ifc")
