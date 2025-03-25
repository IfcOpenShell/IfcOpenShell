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

# https://stackoverflow.com/a/9184560/9627415
# Possible optimisation to linalg.norm?

# from ifcopenshell.util.shape_builder import VectorType, SequenceOfVectors
from itertools import cycle
from collections import namedtuple
from math import sin, cos, radians

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


def test_wall(offset, p1, p2, p3, p4, a1=None, a2=None):
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

            ifcopenshell.api.geometry.regenerate_wall_representation(f, wall=wall_a, angle=a1)
            ifcopenshell.api.geometry.regenerate_wall_representation(f, wall=wall_b, angle=a1)
            ifcopenshell.api.geometry.regenerate_wall_representation(f, wall=wall_c, angle=a1)


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


def test_atpath(offset, angle=None):
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
        ifcopenshell.api.geometry.regenerate_wall_representation(f, wall=wall, angle=angle)

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

    ifcopenshell.api.geometry.regenerate_wall_representation(f, wall=wall_a, angle=angle)


test_wall(0, 1, 1, 1, 1, radians(10))
test_wall(1, 2, 1, 1, 2, radians(10))
test_wall(2, 2, 1, 1, 1, radians(10))
test_wall(3, 1, 2, 1, 1, radians(10))
test_wall(4, 1, 2, 1, 2, radians(10))
test_wall(5, 3, 1, 2, 4, radians(10))
test_atpath(7, radians(10))


f.write("/home/dion/wall.ifc")
