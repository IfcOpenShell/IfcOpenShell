# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 @Andrej730
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

import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
from math import cos, tan, pi
from pathlib import Path
from itertools import chain
from ifcopenshell.util.shape_builder import ShapeBuilder, V, np_to_3d, np_normalized
from typing import Optional, Union

GeneratorOutput = Union[list[ifcopenshell.entity_instance], list[list[ifcopenshell.entity_instance]]]


class LibraryGenerator:
    def generate(self, library_name, output_filename="IFC4 EU Steel.ifc"):
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}
        np_X, np_Y, np_Z = 0, 1, 2

        self.materials = {}

        self.file = ifcopenshell.api.run("project.create_file")
        self.project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject", name=library_name)
        self.library = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProjectLibrary", name=library_name
        )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[self.library], relating_context=self.project
        )
        unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit])

        model = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        plan = ifcopenshell.api.run("context.add_context", self.file, context_type="Plan")
        self.representations = {
            "model_body": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="MODEL_VIEW",
                parent=model,
            ),
            "plan_body": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Plan",
                context_identifier="Body",
                target_view="PLAN_VIEW",
                parent=plan,
            ),
        }

        builder = ShapeBuilder(self.file)

        def create_box_objects(
            width: float,
            depth: float,
            height: float,
            shift_to_center: bool = False,
            return_representations: bool = False,
        ) -> Union[list[ifcopenshell.entity_instance], list[list[ifcopenshell.entity_instance]]]:
            output = []

            rectangle = builder.rectangle(size=(width, depth))
            box = builder.extrude(builder.profile(rectangle), height)

            if return_representations:
                representation_3d = builder.get_representation(context=self.representations["model_body"], items=box)
                output.append(representation_3d)
            else:
                output.append([box])

            rectangle = builder.rectangle(size=V(width, depth))
            if return_representations:
                representation_2d = builder.get_representation(self.representations["plan_body"], rectangle)
                output.append(representation_2d)
            else:
                output.append([rectangle])

            if shift_to_center:
                shift_to_center = V(-width / 2, -depth / 2)
                builder.translate(output[0], np_to_3d(shift_to_center))
                builder.translate(output[1], shift_to_center)

            return output

        def create_fillet_rectangle(
            size: Optional[np.ndarray] = None, position: Optional[np.ndarray] = None, fillet_radius: float = 50.0
        ) -> ifcopenshell.entity_instance:
            """`fillet_radius` is either float or list of floats for each corner
            in counter-clockwise order starting from bottom left"""
            kwargs = dict()
            if size is not None:
                kwargs["size"] = size
            if position is not None:
                kwargs["position"] = position

            _, _, rectangle = builder.get_simple_2dcurve_data(
                coords=builder.get_rectangle_coords(**kwargs),
                fillets=(0, 1, 2, 3),
                fillet_radius=fillet_radius,
                closed=True,
                create_ifc_curve=True,
            )
            return rectangle

        # beds
        representation_3d, representation_2d = create_box_objects(680.0, 1300.0, 550.0, return_representations=True)
        self.create_explicit_type("IfcFurnitureType", "Cot mattress", representation_3d, representation_2d)

        def create_fancy_bed_representations(overall_width, overall_depth, overall_height, blanket_tan=tan(pi / 8)):
            # 0.85h - blanket starts
            # 0.7w - blanket shifts
            # 0.25h - blanket shift ends
            # o.2w - pillow starts
            bed = builder.rectangle(size=V(overall_width, overall_depth))
            blanket_pillow = builder.polyline(
                (
                    [0.0, overall_depth * 0.85],
                    # pillow
                    [overall_width * 0.2, overall_depth * 0.85],
                    [overall_width * 0.2, overall_depth],
                    [overall_width * 0.2, overall_depth * 0.85],
                    [overall_width * 0.7, overall_depth * 0.85],
                    # pillow
                    [overall_width * 0.8, overall_depth * 0.85 - overall_width * (0.8 - 0.7) * blanket_tan],
                    [overall_width * 0.8, overall_depth],
                    [overall_width * 0.8, overall_depth * 0.85 - overall_width * (0.8 - 0.7) * blanket_tan],
                    [overall_width, overall_depth * 0.85 - overall_width * (1 - 0.7) * blanket_tan],
                )
            )
            representation_2d = builder.get_representation(self.representations["plan_body"], [bed, blanket_pillow])

            curve = builder.rectangle(size=V(overall_width, overall_depth))
            mesh = builder.extrude(builder.profile(curve), overall_height)
            representation_3d = builder.get_representation(context=self.representations["model_body"], items=mesh)
            return representation_3d, representation_2d

        representation_3d, representation_2d = create_fancy_bed_representations(920.0, 1880.0, 550.0)
        self.create_explicit_type("IfcFurnitureType", "Single bed", representation_3d, representation_2d)
        representation_3d, representation_2d = create_fancy_bed_representations(920.0, 2030.0, 550.0)
        self.create_explicit_type("IfcFurnitureType", "Long single bed", representation_3d, representation_2d)
        representation_3d, representation_2d = create_fancy_bed_representations(1070.0, 2030.0, 550.0)
        self.create_explicit_type("IfcFurnitureType", "King single bed", representation_3d, representation_2d)
        representation_3d, representation_2d = create_fancy_bed_representations(1380.0, 1880.0, 550.0)
        self.create_explicit_type("IfcFurnitureType", "Double bed", representation_3d, representation_2d)
        representation_3d, representation_2d = create_fancy_bed_representations(1530.0, 2030.0, 550.0)
        self.create_explicit_type("IfcFurnitureType", "Queen bed", representation_3d, representation_2d)
        representation_3d, representation_2d = create_fancy_bed_representations(1830.0, 2030.0, 550.0)
        self.create_explicit_type("IfcFurnitureType", "King bed", representation_3d, representation_2d)
        representation_3d, representation_2d = create_fancy_bed_representations(2030.0, 2030.0, 550.0)
        self.create_explicit_type("IfcFurnitureType", "Super King bed", representation_3d, representation_2d)

        # wardrobes
        def create_fancy_wardrobe_representations(overall_width, overall_depth, overall_height):
            curve = builder.rectangle(size=V(overall_width, overall_depth))
            mesh = builder.extrude(builder.profile(curve), overall_height)
            representation_3d = builder.get_representation(context=self.representations["model_body"], items=mesh)

            rect = builder.rectangle(size=V(overall_width, overall_depth))
            cloth = []

            # 1 cloth every 200 mm
            # cloth step = 200m
            # cloth height offset = 0.1h
            # cloth width offset = 0.5step
            cloths_amount = int(overall_width) // 200 + ((int(overall_width) % 200) > 200 * (0.5 + 0.1 + 0.05))
            for i in range(cloths_amount):
                tilt_offset = 0 if i % 2 == 0 else 200 * 0.2
                c = builder.polyline(
                    [
                        (i * 200 + 200 * 0.5 - tilt_offset, 0.1 * overall_depth),
                        (i * 200 + 200 * 0.5 + tilt_offset, (1 - 0.1) * overall_depth),
                    ]
                )
                cloth.append(c)
            representation_2d = builder.get_representation(self.representations["plan_body"], items=[rect, *cloth])
            return representation_3d, representation_2d

        representation_3d, representation_2d = create_fancy_wardrobe_representations(1800.0, 600.0, 2100.0)
        self.create_explicit_type("IfcFurnitureType", "ADG Main Bedroom Wardrobe", representation_3d, representation_2d)

        representation_3d, representation_2d = create_fancy_wardrobe_representations(1000.0, 600.0, 2500.0)
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Single Person Wardrobe", representation_3d, representation_2d
        )

        # chairs
        def create_fancy_chair(
            width: float, depth: float, height: float, seat_level: float, return_representations: bool = False
        ) -> GeneratorOutput:
            thickness = 50.0
            shift_to_center = V(-width / 2, 0)
            mirror_axis = V(0, 1)
            output: GeneratorOutput = []

            items_to_adjust = []
            items_3d = []
            chair_back = None
            items_to_adjust.append(seat := builder.rectangle(size=V(width, depth)))

            leg = builder.rectangle(size=V(thickness, thickness))
            legs = [leg] + builder.mirror(
                leg, mirror_axes=[V(1, 0), V(0, 1), V(1, 1)], mirror_point=V(width / 2, depth / 2), create_copy=True
            )
            items_to_adjust.extend(legs)

            if height > seat_level:
                items_to_adjust.append(chair_back := builder.rectangle(size=V(width, thickness)))

            builder.translate(items_to_adjust, shift_to_center)
            builder.mirror(items_to_adjust, mirror_axis)

            items_3d.append(
                builder.extrude(
                    builder.profile(seat), thickness, position=V(0, 0, seat_level), extrusion_vector=V(0, 0, -1)
                )
            )

            if chair_back:
                items_3d.append(
                    builder.extrude(
                        builder.profile(chair_back),
                        height - seat_level,
                        position=V(0, 0, height),
                        extrusion_vector=V(0, 0, -1),
                    )
                )

            items_3d.extend([builder.extrude(leg, seat_level - thickness) for leg in legs])
            if return_representations:
                representation_3d = builder.get_representation(
                    context=self.representations["model_body"], items=items_3d
                )
                output.append(representation_3d)
            else:
                output.append(items_3d)

            second_arc_depth = depth * (1 - 0.10)
            second_arc_width = width - (depth - second_arc_depth) * 2
            polyline = builder.polyline((V(0, 0), V(width, 0)))
            _, _, first_semicircle = builder.create_transition_arc_ifc(width, depth, create_ifc_curve=True)

            _, _, second_semicircle = builder.create_transition_arc_ifc(
                second_arc_width, second_arc_depth, create_ifc_curve=True
            )
            builder.translate(second_semicircle, V((width - second_arc_width) / 2, 0))

            builder.translate([polyline, first_semicircle, second_semicircle], shift_to_center)
            builder.translate([polyline, first_semicircle, second_semicircle], V(0, -depth))

            items_2d = [polyline, first_semicircle, second_semicircle]

            if return_representations:
                representation_2d = builder.get_representation(self.representations["plan_body"], items_2d)
                output.append(representation_2d)
            else:
                output.append(items_2d)

            return output

        representation_3d, representation_2d = create_fancy_chair(600.0, 400.0, 900.0, 450.0, True)
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail Dining Chair", representation_3d, representation_2d
        )

        representation_3d, representation_2d = create_fancy_chair(300.0, 300.0, 800.0, 800.0, True)
        self.create_explicit_type("IfcFurnitureType", "Neufert Retail Bar Stool", representation_3d, representation_2d)

        # table
        representation_3d, representation_2d = create_box_objects(
            700.0, 500.0, 550.0, shift_to_center=True, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic Large Bedside Table", representation_3d, representation_2d
        )

        representation_3d, representation_2d = create_box_objects(
            600.0, 450.0, 550.0, shift_to_center=True, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic Medium Bedside Table", representation_3d, representation_2d
        )

        representation_3d, representation_2d = create_box_objects(
            500.0, 380.0, 500.0, shift_to_center=True, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic Small Bedside Table", representation_3d, representation_2d
        )

        def create_fancy_rectangle_table(
            width: float, depth: float, height: float, return_representations=False
        ) -> GeneratorOutput:
            output = []
            leg_size = 50.0
            countertop_thickness = 50.0
            shift_to_center = V(-width / 2, -depth / 2)
            rectangle = builder.rectangle(size=V(width, depth))
            countertop = builder.extrude(
                builder.profile(rectangle), countertop_thickness, V(0, 0, height - countertop_thickness)
            )

            leg_curve = builder.rectangle(size=V(leg_size, leg_size))
            legs_curves = [leg_curve] + builder.mirror(
                leg_curve,
                mirror_axes=[V(1, 0), V(0, 1), V(1, 1)],
                mirror_point=V(width / 2, depth / 2),
                create_copy=True,
            )
            legs_profiles = [builder.profile(leg) for leg in legs_curves]
            legs = [builder.extrude(leg, height - countertop_thickness) for leg in legs_profiles]
            items = [countertop] + legs
            builder.translate(items, np_to_3d(shift_to_center))

            if return_representations:
                representation_3d = builder.get_representation(context=self.representations["model_body"], items=items)
                output.append(representation_3d)
            else:
                output.append(items)

            rectangle = builder.rectangle(position=shift_to_center, size=V(width, depth))
            if return_representations:
                representation_2d = builder.get_representation(self.representations["plan_body"], rectangle)
                output.append(representation_2d)
            else:
                output.append([rectangle])

            return output

        representation_3d, representation_2d = create_fancy_rectangle_table(750.0, 750.0, 450.0, True)
        self.create_explicit_type(
            "IfcFurnitureType", "Generic Medium Coffee Table", representation_3d, representation_2d
        )

        # tables
        def create_rectangle_table_with_chairs(
            table_width: float,
            table_depth: float,
            table_height: float,
            chair_width: float,
            chair_depth: float,
            chair_height: float,
            seat_level: float,
            table_chair_gap: float,
            number_of_seats: int,
            side_seats: bool = False,
        ) -> tuple[ifcopenshell.entity_instance, ifcopenshell.entity_instance]:
            items_table_3d, items_table_2d = create_fancy_rectangle_table(table_width, table_depth, table_height)
            items_chair_3d, items_chair_2d = create_fancy_chair(chair_width, chair_depth, chair_height, seat_level)

            if side_seats:
                number_of_seats -= 2
            seats_per_side = number_of_seats // 2
            per_chair_gap = (table_width - chair_width * seats_per_side) / (seats_per_side + 1)

            # 3d representation
            items_chairs_3d = []
            if side_seats:
                items_chair_3d_transformed = builder.rotate(items_chair_3d, angle=90, create_copy=True)
                builder.translate(items_chair_3d_transformed, V(table_width / 2 + table_chair_gap + chair_depth, 0, 0))
                items_chairs_3d.append(items_chair_3d_transformed)
                items_chairs_3d.append(
                    builder.mirror(items_chair_3d_transformed, mirror_axes=V(1, 0), create_copy=True)
                )

            # create_copy condiition is needed to avoid having one unused chair in ifc
            for i in range(seats_per_side):
                coords = V(
                    -table_width / 2 + per_chair_gap + i * (chair_width + per_chair_gap) + chair_width / 2,
                    table_depth / 2 + table_chair_gap + chair_depth,
                    0,
                )
                cur_items_chair_3d = builder.translate(items_chair_3d, coords, create_copy=i != seats_per_side - 1)
                items_chairs_3d.append(cur_items_chair_3d)
                items_chairs_3d.append(builder.mirror(cur_items_chair_3d, mirror_axes=V(0, 1), create_copy=True))

            items_chairs_3d = list(chain(*items_chairs_3d))
            representation_3d = builder.get_representation(
                self.representations["model_body"], items=items_table_3d + items_chairs_3d
            )

            # 2d representation
            items_chairs_2d = []
            if side_seats:
                items_chair_2d_transformed = builder.rotate(items_chair_2d, angle=90, create_copy=True)
                builder.translate(items_chair_2d_transformed, V(table_width / 2 + table_chair_gap + chair_depth, 0))
                items_chairs_2d.append(items_chair_2d_transformed)
                items_chairs_2d.append(
                    builder.mirror(items_chair_2d_transformed, mirror_axes=V(1, 0), create_copy=True)
                )

            # create_copy condiition is needed to avoid having one unused chair in ifc
            for i in range(seats_per_side):
                coords = V(
                    -table_width / 2 + per_chair_gap + i * (chair_width + per_chair_gap) + chair_width / 2,
                    table_depth / 2 + table_chair_gap + chair_depth,
                )
                cur_items_chair_2d = builder.translate(items_chair_2d, coords, create_copy=i != seats_per_side - 1)
                items_chairs_2d.append(cur_items_chair_2d)
                items_chairs_2d.append(builder.mirror(cur_items_chair_2d, mirror_axes=V(0, 1), create_copy=True))

            items_chairs_2d = list(chain(*items_chairs_2d))

            representation_2d = builder.get_representation(
                self.representations["plan_body"], items=items_table_2d + items_chairs_2d
            )

            return representation_3d, representation_2d

        # short 4-seater table
        overall_width, overall_depth, overall_height = (1750.0, 1750.0, 900.0)
        table_width, table_depth, table_height = (850.0, 850.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_rectangle_table_with_chairs(
            table_width,
            table_depth,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=4,
            side_seats=True,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 4-Seater Square Table", representation_3d, representation_2d
        )

        # wide 4-seater table
        overall_width, overall_depth, overall_height = (1300.0, 2000.0, 900.0)
        table_width, table_depth, table_height = (1300.0, 800.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (450.0, 450.0, 900.0, 450.0)
        representation_3d, representation_2d = create_rectangle_table_with_chairs(
            table_width,
            table_depth,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=4,
            side_seats=False,
        )

        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Residential 4-Seater Rectangular Table", representation_3d, representation_2d
        )

        # 2-seater table
        overall_width, overall_depth, overall_height = (625.0, 1750.0, 900.0)
        table_width, table_depth, table_height = (625.0, 800.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_rectangle_table_with_chairs(
            table_width,
            table_depth,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=2,
        )

        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 2-Seater Rectangular Table", representation_3d, representation_2d
        )

        # 4-seater table
        overall_width, overall_depth, overall_height = (1250.0, 1750.0, 900.0)
        table_width, table_depth, table_height = (1250.0, 800.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_rectangle_table_with_chairs(
            table_width,
            table_depth,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=4,
        )

        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 4-Seater Rectangular Table", representation_3d, representation_2d
        )

        # 6-seater table
        overall_width, overall_depth, overall_height = (1875.0, 1750.0, 900.0)
        table_width, table_depth, table_height = (1875.0, 800.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_rectangle_table_with_chairs(
            table_width,
            table_depth,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=6,
        )

        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 6-Seater Rectangular Table", representation_3d, representation_2d
        )

        # 8-seater table
        overall_width, overall_depth, overall_height = (2500.0, 1750.0, 900.0)
        table_width, table_depth, table_height = (2500.0, 800.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_rectangle_table_with_chairs(
            table_width,
            table_depth,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=8,
        )

        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 8-Seater Rectangular Table", representation_3d, representation_2d
        )

        # 12-seater table
        overall_width, overall_depth, overall_height = (3750.0, 1750.0, 900.0)
        table_width, table_depth, table_height = (3750.0, 800.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_rectangle_table_with_chairs(
            table_width,
            table_depth,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=12,
        )

        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 12-Seater Rectangular Table", representation_3d, representation_2d
        )

        def create_fancy_circular_table(diameter, height, return_representations=False):
            radius = diameter / 2
            width, depth = radius, radius
            output = []
            leg_size = 50.0
            countertop_thickness = 50.0
            shift_to_center = V(-width / 2, -depth / 2)
            circle = builder.circle(radius=radius)
            countertop = builder.extrude(
                builder.profile(circle), countertop_thickness, V(0, 0, height - countertop_thickness)
            )

            leg_curve = builder.circle(radius=leg_size)
            leg = builder.extrude(builder.profile(leg_curve), height - countertop_thickness)
            items = [countertop, leg]

            if return_representations:
                representation_3d = builder.get_representation(context=self.representations["model_body"], items=items)
                output.append(representation_3d)
            else:
                output.append(items)

            circle = builder.circle(radius=radius)
            if return_representations:
                representation_2d = builder.get_representation(self.representations["plan_body"], circle)
                output.append(representation_2d)
            else:
                output.append([circle])

            return output

        def create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats,
            side_seats=False,
        ):
            items_table_3d, items_table_2d = create_fancy_circular_table(table_diameter, table_height)
            items_chair_3d, items_chair_2d = create_fancy_chair(chair_width, chair_depth, chair_height, seat_level)

            per_chair_angle = 360 / number_of_seats
            table_radius = table_diameter / 2

            # 3d rerpresentation
            items_chairs_3d = []

            # create_copy condiition is needed to avoid having one unused chair in ifc
            for i in range(number_of_seats):
                last_seat = i == number_of_seats - 1
                cur_items_chair_3d = builder.translate(
                    items_chair_3d, V(0, table_radius + table_chair_gap + chair_depth, 0), create_copy=not last_seat
                )
                builder.rotate(cur_items_chair_3d, per_chair_angle * i)
                items_chairs_3d.append(cur_items_chair_3d)

            items_chairs_3d = list(chain(*items_chairs_3d))
            representation_3d = builder.get_representation(
                self.representations["model_body"], items=items_table_3d + items_chairs_3d
            )

            # 2d representation
            items_chairs_2d = []

            # create_copy condiition is needed to avoid having one unused chair in ifc
            for i in range(number_of_seats):
                last_seat = i == number_of_seats - 1
                cur_items_chair_2d = builder.translate(
                    items_chair_2d, V(0, table_radius + table_chair_gap + chair_depth), create_copy=not last_seat
                )
                builder.rotate(cur_items_chair_2d, per_chair_angle * i)
                items_chairs_2d.append(cur_items_chair_2d)

            items_chairs_2d = list(chain(*items_chairs_2d))

            representation_2d = builder.get_representation(
                self.representations["plan_body"], items=items_table_2d + items_chairs_2d
            )

            return representation_3d, representation_2d

        # circular 2-seater table
        overall_width, overall_depth, overall_height = (1500.0, 1500.0, 900.0)
        table_diameter, table_height = (600.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=2,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 2-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 3-seater table
        overall_width, overall_depth, overall_height = (1700.0, 1700.0, 900.0)
        table_diameter, table_height = (800.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=3,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 3-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 4-seater table
        overall_width, overall_depth, overall_height = (1800.0, 1800.0, 900.0)
        table_diameter, table_height = (900.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=4,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 4-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 5-seater table
        overall_width, overall_depth, overall_height = (2000.0, 2000.0, 900.0)
        table_diameter, table_height = (1100.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=5,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 5-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 6-seater table
        overall_width, overall_depth, overall_height = (2150.0, 2150.0, 900.0)
        table_diameter, table_height = (1250.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=6,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 6-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 8-seater table
        overall_width, overall_depth, overall_height = (2300.0, 2300.0, 900.0)
        table_diameter, table_height = (1400.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=8,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 8-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 10-seater table
        overall_width, overall_depth, overall_height = (2450.0, 2450.0, 900.0)
        table_diameter, table_height = (1550.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=10,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 10-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 12-seater table
        overall_width, overall_depth, overall_height = (2750.0, 2750.0, 900.0)
        table_diameter, table_height = (1850.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=12,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 12-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 14-seater table
        overall_width, overall_depth, overall_height = (3100.0, 3100.0, 900.0)
        table_diameter, table_height = (2200.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=14,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 14-Seater Circular Table", representation_3d, representation_2d
        )

        # circular 16-seater table
        overall_width, overall_depth, overall_height = (3400.0, 3400.0, 900.0)
        table_diameter, table_height = (2500.0, 780.0)
        table_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_circular_table_with_chairs(
            table_diameter,
            table_height,
            chair_width,
            chair_depth,
            chair_height,
            seat_level,
            table_chair_gap,
            number_of_seats=16,
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Retail 16-Seater Circular Table", representation_3d, representation_2d
        )

        # sofas

        def create_sofa(width, depth, height, seat_level, number_of_seats=1):
            thickness = 175
            armrest_height = height * 0.7
            shift_to_center = V(-width / 2, -depth)
            mirror_axis = V(0, 1)
            seat_width = (width - thickness * 2) / number_of_seats

            # 3d representation
            armrest = builder.rectangle(size=V(thickness, depth))
            armrest = builder.extrude(armrest, armrest_height)
            armrests = [armrest, builder.translate(armrest, V(width - thickness, 0, 0), create_copy=True)]

            seats = []
            for i in range(number_of_seats):
                seat = builder.rectangle(
                    size=V(seat_width, depth - thickness), position=V(thickness + seat_width * i, 0)
                )
                seat = builder.extrude(seat, seat_level)
                seats.append(seat)

            seat_back = builder.rectangle(
                size=V(width - thickness * 2, thickness), position=V(thickness, depth - thickness)
            )
            seat_back = builder.extrude(seat_back, height)

            items = armrests + seats + [seat_back]
            builder.translate(items, np_to_3d(shift_to_center))
            # builder.mirror(items, mirror_axis)
            representation_3d = builder.get_representation(self.representations["model_body"], items=items)

            # 2d representation
            armrest = builder.rectangle(size=V(thickness, depth))
            armrests = [armrest, builder.translate(armrest, V(width - thickness, 0), create_copy=True)]

            seats = []
            for i in range(number_of_seats):
                seat = builder.rectangle(
                    size=V(seat_width, depth - thickness), position=V(thickness + seat_width * i, 0)
                )
                seats.append(seat)

            seat_back = builder.rectangle(
                size=V(width - thickness * 2, thickness), position=V(thickness, depth - thickness)
            )

            items = armrests + seats + [seat_back]
            builder.translate(items, shift_to_center)
            representation_2d = builder.get_representation(self.representations["plan_body"], items=items)

            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height, seat_level = (900.0, 900.0, 900.0, 450.0)
        representation_3d, representation_2d = create_sofa(overall_width, overall_depth, overall_height, seat_level)
        self.create_explicit_type("IfcFurnitureType", "Generic 1-Seater Sofa", representation_3d, representation_2d)

        overall_width, overall_depth, overall_height, seat_level, number_of_seats = (1500.0, 900.0, 900.0, 450.0, 2)
        representation_3d, representation_2d = create_sofa(
            overall_width, overall_depth, overall_height, seat_level, number_of_seats
        )
        self.create_explicit_type("IfcFurnitureType", "Generic 2-Seater Sofa", representation_3d, representation_2d)

        overall_width, overall_depth, overall_height, seat_level, number_of_seats = (2100.0, 900.0, 900.0, 450.0, 3)
        representation_3d, representation_2d = create_sofa(
            overall_width, overall_depth, overall_height, seat_level, number_of_seats
        )
        self.create_explicit_type("IfcFurnitureType", "Generic 3-Seater Sofa", representation_3d, representation_2d)

        # showers

        def create_shower_or_bathtube(width, depth, height, bathtube=False):
            items_box, items_rectangle = create_box_objects(width, depth, height)
            rect_offset = 50.0
            fillets_radius = 50.0
            sink_radius = 25.0
            coords = [
                (rect_offset, rect_offset),
                (rect_offset, depth - rect_offset),
                (width - rect_offset, depth - rect_offset),
                (width - rect_offset, rect_offset),
            ]
            if bathtube:
                fillets_radius = [fillets_radius * 5] * 2 + [fillets_radius] * 2
            else:
                fillets_radius = [fillets_radius] * 4
            _, _, fillet_rectangle = builder.get_simple_2dcurve_data(
                coords=coords, fillets=(0, 1, 2, 3), fillet_radius=fillets_radius, closed=True, create_ifc_curve=True
            )

            circle_position = V(
                width - rect_offset * 2 - sink_radius,
                (depth - rect_offset * 2 - sink_radius) if not bathtube else depth / 2,
            )
            sink_circle = builder.circle(circle_position, radius=sink_radius)

            items_2d = items_rectangle + [fillet_rectangle, sink_circle]
            representation_2d = builder.get_representation(self.representations["plan_body"], items=items_2d)
            representation_3d = builder.get_representation(self.representations["model_body"], items=items_box)

            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height = (900.0, 750.0, 2100.0)
        representation_3d, representation_2d = create_shower_or_bathtube(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Shower 75x90", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (800.0, 800.0, 2100.0)
        representation_3d, representation_2d = create_shower_or_bathtube(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Shower 80x80", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (900.0, 900.0, 2100.0)
        representation_3d, representation_2d = create_shower_or_bathtube(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Shower 90x90", representation_3d, representation_2d
        )

        # bathtubs
        overall_width, overall_depth, overall_height = (1600.0, 700.0, 550.0)
        representation_3d, representation_2d = create_shower_or_bathtube(
            overall_width, overall_depth, overall_height, bathtube=True
        )
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Small Bathtub", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (1700.0, 750.0, 550.0)
        representation_3d, representation_2d = create_shower_or_bathtube(
            overall_width, overall_depth, overall_height, bathtube=True
        )
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Medium Bathtub", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (1800.0, 800.0, 550.0)
        representation_3d, representation_2d = create_shower_or_bathtube(
            overall_width, overall_depth, overall_height, bathtube=True
        )
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Large Bathtub", representation_3d, representation_2d
        )

        def create_toilet(width, depth, height, seat_level=0):
            shift_to_center = V(-width / 2, 0)
            mirror_axis = V(0, 1)

            cistern_used = not bool(seat_level)
            if cistern_used:
                cistern_height = 0
                cistern_depth = 0
                seat_level = height
            else:
                cistern_height = height - seat_level
                cistern_depth = 200.0

            # 2d representation
            depth_offset = depth * 0.1
            width_offset = width * 0.1
            items_2d = []
            items_2d_to_mirror = []
            coords = [
                (0.0, 0.0),
                (0.0, depth - depth_offset - cistern_depth),
                (width_offset, depth - depth_offset - cistern_depth),
                (width_offset, depth - cistern_depth),
                (width - width_offset, depth - cistern_depth),
                (width - width_offset, depth - depth_offset - cistern_depth),
                (width, depth - depth_offset - cistern_depth),
                (width, 0.0),
            ]
            fillets = (0, 1, 6, 7)
            fillet_radius = (width / 2, width / 5, width / 5, width / 2)
            _, _, seat = builder.get_simple_2dcurve_data(
                coords, fillets, fillet_radius=fillet_radius, closed=True, create_ifc_curve=True
            )
            seat_first_part = ifcopenshell.util.element.copy_deep(self.file, seat)

            seat_depth_offset = (depth - cistern_depth) * 0.3
            seat_width_offset = 0.7 * width / 2 if cistern_depth else width / 2
            seat_start_width_offset = 0.6 * width

            if cistern_height:
                cistern = builder.rectangle(size=V(width, cistern_depth), position=shift_to_center)
                cistern_3d = ifcopenshell.util.element.copy_deep(self.file, cistern)
                items_2d_to_mirror.append(cistern)
            else:
                back_wall_polyline = builder.polyline(
                    ((-seat_start_width_offset / 2, 0.0), (seat_start_width_offset / 2, 0.0))
                )
                items_2d.append(back_wall_polyline)

            # seat
            seat_polyline = builder.polyline(
                ((seat_start_width_offset / 2, 0.0), (seat_width_offset, seat_depth_offset)),
                position_offset=V(0, cistern_depth),
            )

            seat_curve = builder.create_ellipse_curve(
                seat_width_offset, depth - seat_depth_offset - cistern_depth, trim_points_mask=(0, 2)
            )
            builder.translate(seat_curve, V(0, cistern_depth + seat_depth_offset))

            items_2d_to_mirror.extend([seat_polyline, seat_curve])
            items_2d_to_mirror.append(builder.mirror(seat_polyline, mirror_axes=V(1, 0), create_copy=True))

            # seat_second_line
            second_line_height = (depth - cistern_depth) * 0.7
            second_line_width = (width - cistern_depth) * 0.75
            second_curve_y = cistern_depth + second_line_height / 2 * 1.6
            seat_second_curve = builder.create_ellipse_curve(second_line_width / 2, second_line_height / 2)
            builder.translate(seat_second_curve, V(0, second_curve_y))
            items_2d_to_mirror.append(seat_second_curve)

            # bowl
            bowl_width = width / 2 * 0.25
            bowl_depth = (depth - cistern_depth) * 0.1
            bowl_points = (
                (-bowl_width / 2, 0.0),
                (-bowl_width / 2, -bowl_depth / 2),
                (bowl_width / 2, -bowl_depth / 2),
                (bowl_width / 2, 0.0),
            )
            bowl_polyline = builder.polyline(bowl_points)
            bowl_curve = builder.create_ellipse_curve(bowl_width / 2, bowl_depth / 2, trim_points_mask=(0, 2))
            builder.translate([bowl_polyline, bowl_curve], V(0, second_curve_y))
            items_2d_to_mirror.extend([bowl_polyline, bowl_curve])

            builder.mirror(items_2d_to_mirror, mirror_axes=mirror_axis)
            items_2d += items_2d_to_mirror

            representation_2d = builder.get_representation(context=self.representations["plan_body"], items=items_2d)

            # 3d representation
            items_3d = []
            items_3d_to_mirror = []

            # seat
            seat_main_curve_points = builder.get_rectangle_coords(
                size=V(width, depth - cistern_depth), position=V(0, cistern_depth) + shift_to_center
            )
            fillet_radius = min(width / 2, (depth - cistern_depth) / 2)
            _, _, seat_main_curve = builder.get_simple_2dcurve_data(
                seat_main_curve_points, fillets=(2, 3), fillet_radius=fillet_radius, closed=True, create_ifc_curve=True
            )
            seat_main_curve_mask = builder.circle(center=V(0, depth - fillet_radius), radius=fillet_radius * 0.75)
            seat_main_curve_profile = builder.profile(seat_main_curve, inner_curves=seat_main_curve_mask)

            seat_level_offset = seat_level / 2 / 4
            seat_first_part = builder.extrude(
                seat_main_curve_profile, seat_level / 2 - seat_level_offset, V(0, 0, seat_level / 2 + seat_level_offset)
            )

            seat_main_curve = ifcopenshell.util.element.copy_deep(self.file, seat_main_curve)
            seat_second_part = builder.extrude(seat_main_curve, seat_level_offset, V(0, 0, seat_level / 2))

            items_3d_to_mirror.extend([seat_first_part, seat_second_part])

            seat_leg = builder.rectangle(size=V(width, depth / 3), position=V(0, depth / 3) + shift_to_center)
            seat_leg = builder.extrude(seat_leg, seat_level / 2)
            items_3d_to_mirror.append(seat_leg)

            # cistern
            if cistern_height:
                cistern_3d = builder.extrude(
                    cistern_3d, cistern_height + seat_level / 2, position=V(0, 0, seat_level / 2)
                )
                items_3d_to_mirror.append(cistern_3d)

            builder.translate(items_3d, np_to_3d(shift_to_center))

            builder.mirror(items_3d_to_mirror, mirror_axes=mirror_axis)
            items_3d += items_3d_to_mirror

            representation_3d = builder.get_representation(context=self.representations["model_body"], items=items_3d)

            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height, seat_level = (550.0, 650.0, 770.0, 400)
        representation_3d, representation_2d = create_toilet(overall_width, overall_depth, overall_height, seat_level)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Toilet with Cistern", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (400.0, 530.0, 400.0)
        representation_3d, representation_2d = create_toilet(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Generic Toilet without Cistern", representation_3d, representation_2d
        )

        def create_urinal(width, depth, height):
            shift_to_center = V(-width / 2, 0)
            mirror_axis = V(0, 1)

            back_wall_depth = depth * 0.1
            back_wall_border_mask_height = height * 0.1
            back_wall_border_mask_depth = depth * 0.1
            back_wall_border_mask_width = width * 0.2

            bottom_height = back_wall_border_mask_height / 2
            bottom_mask_depth = depth * 0.1
            bottom_mask_width = width * 0.2
            bottom_mask_height = height * 0.2

            items_3d_to_center = []

            # back wall
            back_wall = builder.rectangle(V(width, height))
            # example of rotating and extruding by Y axis btw
            back_wall_extruded = builder.extrude(
                back_wall, back_wall_depth + back_wall_border_mask_depth, **builder.extrude_kwargs("Y")
            )
            items_3d_to_center.append(back_wall_extruded)

            # bottom part
            base_curve = builder.create_ellipse_curve(
                width / 2, depth - (back_wall_depth + bottom_mask_depth), trim_points_mask=(0, 2)
            )
            builder.translate(base_curve, V(0, back_wall_depth + bottom_mask_depth))
            triangle_bottom_extruded = builder.extrude(base_curve, bottom_height)

            second_curve = builder.create_ellipse_curve(
                (width - bottom_mask_width) / 2,
                depth - (back_wall_depth + bottom_mask_depth) - bottom_mask_depth,
                trim_points_mask=(0, 2),
            )
            builder.translate(second_curve, V(0, back_wall_depth + bottom_mask_depth))
            base_curve = ifcopenshell.util.element.copy_deep(self.file, base_curve)
            mask_curve_profile = builder.profile(base_curve, inner_curves=second_curve)
            triangle_bottom_wall_mask = builder.extrude(
                mask_curve_profile, bottom_mask_height, position=V(0, 0, bottom_height)
            )

            builder.translate(items_3d_to_center, np_to_3d(shift_to_center))
            items_3d = items_3d_to_center + [triangle_bottom_extruded, triangle_bottom_wall_mask]
            builder.mirror(items_3d, mirror_axis)

            representation_3d = builder.get_representation(self.representations["model_body"], items_3d)

            # 2d representation
            curve_offset_depth = depth * 0.1
            curve_offset_width = width * 0.2
            items_2d = []
            trim_points = builder.get_trim_points_from_mask(width / 2, 0.0, (0, 2))

            base_curve = builder.create_ellipse_curve(
                width / 2, depth, trim_points=((width / 2, 0.0), (-width / 2, 0.0))
            )

            items_2d.append(base_curve)
            items_2d.append(builder.polyline(trim_points))

            items_2d.append(builder.circle(radius=back_wall_depth * 0.5, center=V(0, back_wall_depth * 2.5)))

            second_curve = builder.create_ellipse_curve(
                (width - bottom_mask_width) / 2,
                depth - (back_wall_depth + bottom_mask_depth) - bottom_mask_depth,
                trim_points_mask=(0, 2),
            )
            builder.translate(second_curve, V(0, 2 * curve_offset_depth))
            items_2d.append(second_curve)

            curve_coords = builder.get_trim_points_from_mask(curve_offset_width / 2, curve_offset_depth, (3, 2))
            second_curve = builder.curve_between_two_points(curve_coords)
            builder.translate(second_curve, V(-width / 2 + curve_offset_width, 2 * curve_offset_depth))
            polyline = builder.polyline(
                ((-width / 2 + curve_offset_width, 0.0), (width / 2 - curve_offset_width, 0.0)),
                position_offset=V(0, curve_offset_depth),
            )
            items_2d.extend([second_curve, polyline])
            items_2d.append(builder.mirror(second_curve, V(1, 0), create_copy=True))

            builder.mirror(items_2d, mirror_axis)

            representation_2d = builder.get_representation(self.representations["plan_body"], items_2d)

            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height = (350.0, 350.0, 650.0)
        representation_3d, representation_2d = create_urinal(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Small Urinal", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (400.0, 400.0, 650.0)
        representation_3d, representation_2d = create_urinal(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Medium Urinal", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (450.0, 450.0, 650.0)
        representation_3d, representation_2d = create_urinal(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Large Urinal", representation_3d, representation_2d
        )

        def create_basin(width, depth, height):
            second_width = 0.9 * width
            second_depth = 0.7 * depth
            faucet_depth = depth - (depth - second_depth) / 2 / 2
            faucet_length = 120.0
            shift_to_center = V(-width / 2, -depth)

            # representation 2d
            rectangle_main = create_fillet_rectangle(size=V(width, depth))
            rectangle_main_3d = ifcopenshell.util.element.copy_deep(self.file, rectangle_main)

            rectangle_second = create_fillet_rectangle(
                size=V(second_width, second_depth),
                position=V((width - second_width) / 2, (depth - second_depth) * 0.3),
                fillet_radius=(150.0, 150.0, 50.0, 50.0),
            )
            rectangle_second_3d = ifcopenshell.util.element.copy_deep(self.file, rectangle_second)

            faucet = builder.polyline(((width / 2, faucet_depth), (width / 2, faucet_depth - faucet_length)))
            items_2d = [rectangle_main, rectangle_second, faucet]
            builder.translate(items_2d, shift_to_center)
            representation_2d = builder.get_representation(self.representations["plan_body"], items_2d)

            # representation 3d
            basin_downside_thickness = 100.0

            rectangle_profile = builder.profile(rectangle_main_3d, inner_curves=rectangle_second_3d)
            main_basin = builder.extrude(
                rectangle_profile, height - basin_downside_thickness, position=V(0, 0, basin_downside_thickness)
            )
            basin_downside = builder.extrude(rectangle_second_3d, basin_downside_thickness)

            items_3d = [main_basin, basin_downside]
            builder.translate(items_3d, np_to_3d(shift_to_center))
            representation_3d = builder.get_representation(self.representations["model_body"], items_3d)
            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height = (450.0, 400.0, 250.0)
        representation_3d, representation_2d = create_basin(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Extra Small Basin", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (500.0, 450.0, 250.0)
        representation_3d, representation_2d = create_basin(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Small Basin", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (550.0, 500.0, 250.0)
        representation_3d, representation_2d = create_basin(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Medium Basin", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (600.0, 550.0, 250.0)
        representation_3d, representation_2d = create_basin(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcSanitaryTerminalType", "Neufert Large Basin", representation_3d, representation_2d
        )

        def create_desk(width, depth, height, return_representations=False):
            leg_width = 50.0
            countertop_height = 50.0
            backside_offset = 50.0
            back_side_height = 0.6 * height
            output = []

            # 3d representation
            items_3d = []
            leg = builder.rectangle(size=V(leg_width, depth))
            leg = builder.extrude(leg, height - countertop_height)
            items_3d.append(leg)
            items_3d.append(builder.translate(leg, V(width - leg_width, 0, 0), create_copy=True))

            countertop = builder.rectangle(size=V(width, depth))
            countertop = builder.extrude(countertop, countertop_height, V(0, 0, height - countertop_height))
            items_3d.append(countertop)

            backside = builder.rectangle(
                size=V(width - leg_width * 2, backside_offset),
                position=V(backside_offset, height - backside_offset * 4),
            )
            backside = builder.extrude(
                backside, back_side_height, position=V(0, 0, height - back_side_height - backside_offset)
            )
            items_3d.append(backside)

            if return_representations:
                representation_3d = builder.get_representation(self.representations["model_body"], items_3d)
                output.append(representation_3d)
            else:
                output.append(items_3d)

            # 2d representation
            rectangle = builder.rectangle(V(width, depth))
            if return_representations:
                representation_2d = builder.get_representation(self.representations["plan_body"], rectangle)
                output.append(representation_2d)
            else:
                output.append([rectangle])

            return output

        overall_width, overall_depth, overall_height = (1560.0, 780.0, 780.0)
        representation_3d, representation_2d = create_desk(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Commercial Writing Desk", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (1400.0, 700.0, 760.0)
        representation_3d, representation_2d = create_desk(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Commercial Office Desk", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (1000.0, 600.0, 730.0)
        representation_3d, representation_2d = create_desk(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type("IfcFurnitureType", "Generic Small Desk", representation_3d, representation_2d)

        overall_width, overall_depth, overall_height = (1200.0, 700.0, 750.0)
        representation_3d, representation_2d = create_desk(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type("IfcFurnitureType", "Generic Medium Desk", representation_3d, representation_2d)

        overall_width, overall_depth, overall_height = (1500.0, 800.0, 750.0)
        representation_3d, representation_2d = create_desk(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type("IfcFurnitureType", "Generic Large Desk", representation_3d, representation_2d)

        def create_desk_with_chair(
            desk_width, desk_depth, desk_height, chair_width, chair_depth, chair_height, seat_level, desk_chair_gap
        ):
            desk_items_3d, desk_items_2d = create_desk(desk_width, desk_depth, desk_height)
            chair_items_3d, chair_items_2d = create_fancy_chair(chair_width, chair_depth, chair_height, seat_level)

            # 2d representation
            builder.translate(desk_items_2d, V(0, chair_depth + desk_chair_gap))
            builder.translate(chair_items_2d, V(desk_width / 2, 0))
            builder.mirror(chair_items_2d, mirror_axes=V(0, 1))
            items_2d = desk_items_2d + chair_items_2d

            # 3d representation
            builder.translate(desk_items_3d, V(0, chair_depth + desk_chair_gap, 0))
            builder.translate(chair_items_3d, V(desk_width / 2, 0, 0))
            builder.mirror(chair_items_3d, mirror_axes=V(0, 1))
            items_3d = desk_items_3d + chair_items_3d

            representation_3d = builder.get_representation(self.representations["model_body"], items_3d)
            representation_2d = builder.get_representation(self.representations["plan_body"], items_2d)
            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height = (
            1560.0,
            1630.0,
            900.0,
        )
        desk_width, desk_depth, desk_height = (
            1560.0,
            780.0,
            780.0,
        )
        desk_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_desk_with_chair(
            desk_width, desk_depth, desk_height, chair_width, chair_depth, chair_height, seat_level, desk_chair_gap
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Commercial Writing Desk and Chair", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (1400.0, 1450.0, 900.0)
        desk_width, desk_depth, desk_height = (
            1400.0,
            700.0,
            760.0,
        )
        desk_chair_gap = 50.0
        chair_width, chair_depth, chair_height, seat_level = (400.0, 400.0, 900.0, 450.0)
        representation_3d, representation_2d = create_desk_with_chair(
            desk_width, desk_depth, desk_height, chair_width, chair_depth, chair_height, seat_level, desk_chair_gap
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Commercial Office Desk and Chair", representation_3d, representation_2d
        )

        def create_dishwasher(
            width: float, depth: float, height: float
        ) -> tuple[ifcopenshell.entity_instance, ifcopenshell.entity_instance]:
            items_3d, items_2d = create_box_objects(width, depth, height)
            circle_first_r = width * 0.1
            circle_second_r = width * 0.3
            center = V(width / 2, depth / 2)
            k = center[np_Y] / center[np_X]

            circle_first = builder.circle(center=center, radius=circle_second_r)
            circle_second = builder.circle(center=center, radius=circle_first_r)

            polyline = builder.polyline([(0.0, 0.0), center - np_normalized(center) * circle_second_r])
            mirrored_polylines = builder.mirror(
                polyline, mirror_axes=[(1, 0), (0, 1), (1, 1)], mirror_point=center, create_copy=True
            )
            items_2d.extend([circle_first, circle_second, polyline] + mirrored_polylines)

            representation_3d = builder.get_representation(self.representations["model_body"], items_3d)
            representation_2d = builder.get_representation(self.representations["plan_body"], items_2d)

            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height = (500.0, 570.0, 820.0)
        representation_3d, representation_2d = create_dishwasher(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcElectricApplianceType", "Neufert Dishwasher", representation_3d, representation_2d
        )

        def create_cooktop(width, depth, height):
            items_3d, items_2d = create_box_objects(width, depth, height)
            ring_radius = width * 0.1
            ring_offset = V(width * 0.2, depth * 0.2)
            center = V(width / 2, depth / 2)

            ring = builder.circle(ring_offset, ring_radius)
            mirrored_rings = builder.mirror(
                ring, mirror_axes=[V(1, 0), V(0, 1), V(1, 1)], mirror_point=center, create_copy=True
            )
            items_2d.extend([ring] + mirrored_rings)

            representation_3d = builder.get_representation(self.representations["model_body"], items_3d)
            representation_2d = builder.get_representation(self.representations["plan_body"], items_2d)

            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height = (580.0, 510.0, 50.0)
        representation_3d, representation_2d = create_cooktop(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcElectricApplianceType", "Neufert Cooktop 58x51", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (750.0, 510.0, 50.0)
        representation_3d, representation_2d = create_cooktop(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcElectricApplianceType", "Neufert Cooktop 75x51", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (890.0, 510.0, 50.0)
        representation_3d, representation_2d = create_cooktop(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcElectricApplianceType", "Neufert Cooktop 89x51", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (1750.0, 600.0, 850.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Small Kitchen Bench", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (1950.0, 600.0, 850.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Medium Kitchen Bench", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (2200.0, 600.0, 850.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Large Kitchen Bench", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (450.0, 400.0, 2030.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Small Full Height Cupboard", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (550.0, 500.0, 2030.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Medium Full Height Cupboard", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (600.0, 600.0, 2030.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Neufert Large Full Height Cupboard", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (600.0, 700.0, 900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic Kitchen Floor Module", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (600.0, 600.0, 2400.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic Full Height Cupboard", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (750.0, 650.0, 1900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcElectricApplianceType", "Generic Small Fridge Zone", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (900.0, 700.0, 1900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcElectricApplianceType", "Generic Medium Fridge Zone", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (1000.0, 750.0, 1900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcElectricApplianceType", "Generic Large Fridge Zone", representation_3d, representation_2d
        )

        def create_sink(width, depth, height, add_table):
            shift_to_center = V(-width / 2, -depth)
            rect_offset = 50.0
            sink_offset = V(width / 2, 0) if add_table else V(0, 0)

            # 2d representation
            main_rectangle = builder.rectangle(size=V(width, depth))
            sink_radius = 25.0

            faucet_depth = depth - rect_offset / 4
            faucet_length = 120.0

            fillet_rectangle = create_fillet_rectangle(
                size=V(width - rect_offset, depth - rect_offset) - sink_offset,
                position=V(rect_offset / 2, rect_offset / 2) + sink_offset,
            )

            circle_position = sink_offset + V((width - sink_offset[np_X]) / 2, depth - rect_offset * 2 - sink_radius)
            sink_circle = builder.circle(circle_position, radius=sink_radius)

            faucet = builder.polyline(
                (
                    ((width - sink_offset[np_X]) / 2, faucet_depth),
                    ((width - sink_offset[np_X]) / 2, faucet_depth - faucet_length),
                )
            )
            builder.translate(faucet, sink_offset)

            items_2d = [main_rectangle, fillet_rectangle, sink_circle, faucet]
            builder.translate(items_2d, shift_to_center)

            # 3d representation
            items_3d = []

            sink_height = 0.8 * height

            if add_table:
                table = builder.rectangle(size=V(width, depth) - sink_offset)
                table = builder.extrude(table, height)
                items_3d.append(table)

            sink_table = builder.rectangle(size=V(width, depth) - sink_offset, position=sink_offset)
            sink_mask = create_fillet_rectangle(
                size=V(width - rect_offset, depth - rect_offset) - sink_offset,
                position=V(rect_offset / 2, rect_offset / 2) + sink_offset,
            )
            sink_profile = builder.profile(sink_table, inner_curves=sink_mask)
            sink_table_extruded = builder.extrude(sink_profile, sink_height, position=V(0, 0, height - sink_height))
            items_3d.append(sink_table_extruded)

            sink_table_bottom = builder.extrude(sink_table, height - sink_height)
            items_3d.append(sink_table_bottom)
            builder.translate(items_3d, np_to_3d(shift_to_center))

            representation_2d = builder.get_representation(self.representations["plan_body"], items=items_2d)
            representation_3d = builder.get_representation(self.representations["model_body"], items=items_3d)

            return representation_3d, representation_2d

        sinks_data = {
            "Neufert Sink 86x44": (860, 440, 180, False),
            "Neufert Sink 110x44": (1110, 440, 180, True),
            "Neufert Sink 124x44": (1240, 440, 180, True),
            "Generic Small Sink": (450, 460, 210, False),
            "Generic Medium Sink": (800, 460, 210, True),
            "Generic Large Sink": (1100, 490, 220, True),
        }

        for sink_name in sinks_data:
            parameters = [float(i) for i in sinks_data[sink_name][:3]]
            add_table = sinks_data[sink_name][3]

            overall_width, overall_depth, overall_height = parameters
            representation_3d, representation_2d = create_sink(overall_width, overall_depth, overall_height, add_table)
            self.create_explicit_type("IfcSanitaryTerminalType", sink_name, representation_3d, representation_2d)

        overall_width, overall_depth, overall_height = (2200.0, 600.0, 900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic 1-Bedroom Island Bench", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (2400.0, 700.0, 900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic 2-Bedroom Island Bench", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (3000.0, 700.0, 900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic 3-Bedroom Island Bench", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (400.0, 500.0, 900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic Small Laundry Tub With Cupboard", representation_3d, representation_2d
        )

        overall_width, overall_depth, overall_height = (600.0, 500.0, 900.0)
        representation_3d, representation_2d = create_box_objects(
            overall_width, overall_depth, overall_height, return_representations=True
        )
        self.create_explicit_type(
            "IfcFurnitureType", "Generic Medium Laundry Tub With Cupboard", representation_3d, representation_2d
        )

        def create_washing_machine(width, depth, height):
            items_3d, items_2d = create_box_objects(width, depth, height)
            circle_first_r = width * 0.1
            circle_second_r = width * 0.3
            center = V(width / 2, depth / 2)

            circle_first = builder.circle(center=center, radius=circle_second_r)
            circle_second = builder.circle(center=center, radius=circle_first_r)

            items_2d.extend([circle_first, circle_second])

            representation_3d = builder.get_representation(self.representations["model_body"], items_3d)
            representation_2d = builder.get_representation(self.representations["plan_body"], items_2d)

            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height = (595.0, 680.0, 850.0)
        representation_3d, representation_2d = create_washing_machine(overall_width, overall_depth, overall_height)
        self.create_explicit_type(
            "IfcElectricApplianceType", "Neufert Washing Machine", representation_3d, representation_2d
        )

        def create_dryer_machine(width, depth, height):
            items_3d, items_2d = create_box_objects(width, depth, height)
            circle_first_r = width * 0.1
            circle_second_r = width * 0.25
            center_second_circle = V(width / 2, height - circle_second_r * 2.5)

            circle_first = builder.circle(center=V(width / 2, circle_first_r * 1.5), radius=circle_first_r)
            circle_second = builder.circle(center=center_second_circle, radius=circle_second_r)

            polyline = builder.polyline(
                [
                    V(-circle_second_r * 0.6, -((circle_second_r**2 - (circle_second_r * 0.6) ** 2) ** 0.5))
                    + center_second_circle,
                    V(-circle_second_r * 0.1, (circle_second_r**2 - (circle_second_r * 0.1) ** 2) ** 0.5)
                    + center_second_circle,
                ]
            )
            mirrored_polyline = builder.mirror(
                polyline, mirror_point=center_second_circle, mirror_axes=V(1, 0), create_copy=True
            )
            items_2d.extend([circle_first, circle_second, polyline, mirrored_polyline])

            representation_3d = builder.get_representation(self.representations["model_body"], items_3d)
            representation_2d = builder.get_representation(self.representations["plan_body"], items_2d)

            return representation_3d, representation_2d

        overall_width, overall_depth, overall_height = (595.0, 680.0, 850.0)
        representation_3d, representation_2d = create_dryer_machine(overall_width, overall_depth, overall_height)
        self.create_explicit_type("IfcElectricApplianceType", "Neufert Drier", representation_3d, representation_2d)

        parking_lots_data = {
            "30 Deg Bay Class 1/1A No Overhang": (2100, 5400, 2000),
            "30 Deg Bay Class 1/1A With Overhang": (2100, 5400, 2000),
            "30 Deg Bay Class 1/1A With Wheelstop": (2100, 5400, 2000),
            "30 Deg Bay Class 2 No Overhang": (2300, 5400, 2000),
            "30 Deg Bay Class 2 With Overhang": (2300, 5400, 2000),
            "30 Deg Bay Class 2 With Wheelstop": (2300, 5400, 2000),
            "30 Deg Bay Class 3 No Overhang": (2500, 5400, 2000),
            "30 Deg Bay Class 3 With Overhang": (2500, 5400, 2000),
            "30 Deg Bay Class 3 With Wheelstop": (2500, 5400, 2000),
            "30 Deg Bay Class 3A No Overhang": (2500, 5400, 2000),
            "30 Deg Bay Class 3A With Overhang": (2500, 5400, 2000),
            "30 Deg Bay Class 3A With Wheelstop": (2500, 5400, 2000),
            "45 Deg Bay Class 1/1A No Overhang": (2400, 5400, 2000),
            "45 Deg Bay Class 1/1A With Overhang": (2400, 5400, 2000),
            "45 Deg Bay Class 1/1A With Wheelstop": (2400, 5400, 2000),
            "45 Deg Bay Class 2 No Overhang": (2500, 5400, 2000),
            "45 Deg Bay Class 2 With Overhang": (2500, 5400, 2000),
            "45 Deg Bay Class 2 With Wheelstop": (2500, 5400, 2000),
            "45 Deg Bay Class 3 No Overhang": (2600, 5400, 2000),
            "45 Deg Bay Class 3 With Overhang": (2600, 5400, 2000),
            "45 Deg Bay Class 3 With Wheelstop": (2600, 5400, 2000),
            "45 Deg Bay Class 3A No Overhang": (2600, 5400, 2000),
            "45 Deg Bay Class 3A With Overhang": (2600, 5400, 2000),
            "45 Deg Bay Class 3A With Wheelstop": (2600, 5400, 2000),
            "60 Deg Bay Class 1/1A No Overhang": (2400, 5400, 2000),
            "60 Deg Bay Class 1/1A With Overhang": (2400, 5400, 2000),
            "60 Deg Bay Class 1/1A With Wheelstop": (2400, 5400, 2000),
            "60 Deg Bay Class 2 No Overhang": (2500, 5400, 2000),
            "60 Deg Bay Class 2 With Overhang": (2500, 5400, 2000),
            "60 Deg Bay Class 2 With Wheelstop": (2500, 5400, 2000),
            "60 Deg Bay Class 3 No Overhang": (2600, 5400, 2000),
            "60 Deg Bay Class 3 With Overhang": (2600, 5400, 2000),
            "60 Deg Bay Class 3 With Wheelstop": (2600, 5400, 2000),
            "60 Deg Bay Class 3A No Overhang": (2600, 5400, 2000),
            "60 Deg Bay Class 3A With Overhang": (2600, 5400, 2000),
            "60 Deg Bay Class 3A With Wheelstop": (2600, 5400, 2000),
            "90 Deg Bay Class 1 No Overhang": (2400, 5400, 2000),
            "90 Deg Bay Class 1 With Overhang": (2400, 4800, 2000),
            "90 Deg Bay Class 1 With Wheelstop": (2400, 5400, 2000),
            "90 Deg Bay Class 1A No Overhang": (2400, 5400, 2000),
            "90 Deg Bay Class 1A With Overhang": (2400, 4800, 2000),
            "90 Deg Bay Class 1A With Wheelstop": (2400, 5400, 2000),
            "90 Deg Bay Class 2 No Overhang": (2500, 5400, 2000),
            "90 Deg Bay Class 2 With Overhang": (2500, 4800, 2000),
            "90 Deg Bay Class 2 With Wheelstop": (2500, 5400, 2000),
            "90 Deg Bay Class 3 No Overhang": (2600, 5400, 2000),
            "90 Deg Bay Class 3 With Overhang": (2600, 4800, 2000),
            "90 Deg Bay Class 3 With Wheelstop": (2600, 5400, 2000),
            "90 Deg Bay Class 3A Option 1 No Overhang": (2600, 5400, 2000),
            "90 Deg Bay Class 3A Option 1 With Overhang": (2600, 4800, 2000),
            "90 Deg Bay Class 3A Option 1 With Wheelstop": (2600, 5400, 2000),
            "90 Deg Bay Class 3A Option 2 No Overhang": (2700, 5400, 2000),
            "90 Deg Bay Class 3A Option 2 With Overhang": (2700, 4800, 2000),
            "90 Deg Bay Class 3A Option 2 With Wheelstop": (2700, 5400, 2000),
            "90 Deg Bay Motorcycle": (1200, 2500, 2000),
            "3000 Aisle Parallel Bay": (2100, 6300, 2000),
            "3300 Aisle Parallel Bay": (2100, 6100, 2000),
            "3600 Aisle Parallel Bay": (2100, 5900, 2000),
            "3000 Aisle Parallel Obstructed End Bay": (2100, 6600, 2000),
            "3300 Aisle Parallel Obstructed End Bay": (2100, 6400, 2000),
            "3600 Aisle Parallel Obstructed End Bay": (2100, 6200, 2000),
            "3000 Aisle Parallel Unobstructed End Bay": (2100, 5400, 2000),
            "3300 Aisle Parallel Unobstructed End Bay": (2100, 5400, 2000),
            "3600 Aisle Parallel Unobstructed End Bay": (2100, 5400, 2000),
            "3000 Aisle Parallel Unobstructed End Bay": (2100, 5000, 2000),
            "3300 Aisle Parallel Unobstructed End Bay": (2100, 5000, 2000),
            "3600 Aisle Parallel Unobstructed End Bay": (2100, 5000, 2000),
        }

        for parking_lot_name in parking_lots_data:
            parameters = [float(i) for i in parking_lots_data[parking_lot_name]]

            overall_width, overall_depth, overall_height = parameters
            representation_3d, representation_2d = create_box_objects(
                overall_width, overall_depth, overall_height, return_representations=True
            )
            self.create_explicit_type(
                "IfcSpaceType", parking_lot_name, representation_3d, representation_2d, PredefinedType="PARKING"
            )

        self.file.write(output_filename)

    def create_explicit_type(self, ifc_class, name, representation_3d, representation_2d, **params):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        for param, value in params.items():
            setattr(element, param, value)

        ifcopenshell.api.run(
            "geometry.assign_representation", self.file, product=element, representation=representation_3d
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", self.file, product=element, representation=representation_2d
        )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element], relating_context=self.library
        )
        return element

    def create_layer_set_type(self, name, data):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=data["type"], name=name)
        element.Description = data["Description"]
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element], type="IfcMaterialLayerSet"
        )
        layer_set = rel.RelatingMaterial
        for layer_data in data["Layers"]:
            layer = ifcopenshell.api.run(
                "material.add_layer", self.file, layer_set=layer_set, material=self.materials[layer_data[1]]["ifc"]
            )
            layer.Name = layer_data[0]
            layer.LayerThickness = layer_data[2]
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element], relating_context=self.library
        )
        return element

    def create_layer_type(self, ifc_class, name, thickness):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element], type="IfcMaterialLayerSet"
        )
        layer_set = rel.RelatingMaterial
        layer = ifcopenshell.api.run(
            "material.add_layer", self.file, layer_set=layer_set, material=self.materials["TBD"]["ifc"]
        )
        layer.LayerThickness = thickness
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element], relating_context=self.library
        )
        return element

    def create_profile_type(self, ifc_class, name, profile):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, products=[element], type="IfcMaterialProfileSet"
        )
        profile_set = rel.RelatingMaterial
        material_profile = ifcopenshell.api.run(
            "material.add_profile",
            self.file,
            profile_set=profile_set,
            material=self.material,
            # material=self.materials["TBD"]["ifc"]
        )
        ifcopenshell.api.run("material.assign_profile", self.file, material_profile=material_profile, profile=profile)
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element], relating_context=self.library
        )

    def create_type(self, ifc_class, name, representations):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        for rep_name, obj_name in representations.items():
            obj = bpy.data.objects.get(obj_name)
            representation = ifcopenshell.api.run(
                "geometry.add_representation",
                self.file,
                context=self.representations[rep_name],
                blender_object=obj,
                geometry=obj.data,
                total_items=max(1, len(obj.material_slots)),
            )
            styles = []
            for slot in obj.material_slots:
                style = ifcopenshell.api.run("style.add_style", self.file, name=slot.material.name)
                ifcopenshell.api.run(
                    "style.add_surface_style",
                    self.file,
                    style=style,
                    ifc_class="IfcSurfaceStyleRendering",
                    attributes=tool.Style.get_surface_rendering_attributes(slot.material),
                )
                styles.append(style)
            if styles:
                ifcopenshell.api.run(
                    "style.assign_representation_styles", self.file, shape_representation=representation, styles=styles
                )
            ifcopenshell.api.run(
                "geometry.assign_representation", self.file, product=element, representation=representation
            )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element], relating_context=self.library
        )


if __name__ == "__main__":
    path = Path(__file__).parents[1] / "bonsai/bim/data/libraries"
    LibraryGenerator().generate(
        "Non-structural assets library", output_filename=str(path / "IFC4 Furniture Library.ifc")
    )
