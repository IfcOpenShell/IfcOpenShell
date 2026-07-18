# This file was generated with the assistance of an AI coding tool.
#
# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
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

"""Generate a large, synthetic, IFC-valid model for performance testing.

This is a standalone generator: it only depends on ``ifcopenshell`` (no
``bpy``), so it can be run with plain Python to produce a throwaway ``.ifc``
fixture for benchmarking. See ``test/performance/README.md`` in this
directory for the full workflow (including the headless-Blender benchmark
harness that consumes the files this script produces).

The model has a real spatial hierarchy (Project > Site > Building > N
Storeys), each storey is a grid of load-bearing/partition walls forming
actual rooms, some of those rooms are represented as IfcSpaces, and a
fraction of the walls have a door or window filling. All elements have real
3D body geometry (via ``ifcopenshell.api.geometry``), so operations that
touch representations or object placements are not exercising empty shells.

Do not commit generated ``.ifc`` files: regenerate them from this script
whenever a heavy fixture is needed. Nothing here is hardcoded to a
particular element count; pass ``--walls`` (CLI) or ``wall_count``
(function call) to scale the model up or down.

Usage::

    python generate_heavy_model.py --walls 3000 --out /tmp/heavy.ifc

or programmatically::

    from generate_heavy_model import generate_heavy_model
    stats = generate_heavy_model("/tmp/heavy.ifc", wall_count=3000)
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass, field

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.owner
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
from ifcopenshell.api.geometry.create_2pt_wall import create_2pt_wall

BAY_SIZE = 4.0  # metres, length of one wall segment / grid cell edge
WALL_HEIGHT = 3.0
WALL_THICKNESS = 0.2
STOREY_HEIGHT = 3.5
DOOR_HEIGHT = 2.0
DOOR_WIDTH = 0.9
WINDOW_HEIGHT = 1.2
WINDOW_WIDTH = 1.2
WINDOW_SILL = 0.9


@dataclass
class ModelStats:
    storeys: int = 0
    walls: int = 0
    spaces: int = 0
    doors: int = 0
    windows: int = 0
    grid_rows: int = 0
    grid_cols: int = 0
    generation_seconds: float = 0.0
    segments: list = field(default_factory=list)


def _grid_dims_for_wall_count(walls_per_storey: int) -> tuple[int, int]:
    """Pick a (rows, cols) grid whose edge-segment count is close to walls_per_storey.

    A rows x cols grid of square cells has (rows + 1) horizontal wall-runs of
    `cols` segments each, and (cols + 1) vertical wall-runs of `rows`
    segments each: total segments = 2*rows*cols + rows + cols.
    """
    if walls_per_storey < 4:
        return 1, 1
    best = (1, 1)
    best_diff = None
    approx = max(1, int(math.sqrt(walls_per_storey / 2)))
    for rows in range(max(1, approx - 3), approx + 4):
        for cols in range(max(1, approx - 3), approx + 4):
            total = 2 * rows * cols + rows + cols
            diff = abs(total - walls_per_storey)
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best = (rows, cols)
    return best


def _iter_grid_segments(rows: int, cols: int):
    """Yield (p1, p2, is_perimeter) for every wall segment in a rows x cols grid."""
    # Horizontal runs (constant y), at y = 0..rows, each split into `cols` segments.
    for r in range(rows + 1):
        y = r * BAY_SIZE
        is_perimeter_run = r == 0 or r == rows
        for c in range(cols):
            x1, x2 = c * BAY_SIZE, (c + 1) * BAY_SIZE
            yield (x1, y), (x2, y), is_perimeter_run
    # Vertical runs (constant x), at x = 0..cols, each split into `rows` segments.
    for c in range(cols + 1):
        x = c * BAY_SIZE
        is_perimeter_run = c == 0 or c == cols
        for r in range(rows):
            y1, y2 = r * BAY_SIZE, (r + 1) * BAY_SIZE
            yield (x, y1), (x, y2), is_perimeter_run


def generate_heavy_model(
    out_path: str,
    wall_count: int = 3000,
    storeys: int = 10,
    schema: str = "IFC4",
    spaces_per_storey: int = 4,
    door_every: int = 6,
    window_every: int = 4,
    seed: int = 0,
) -> ModelStats:
    """Build and save a large synthetic IFC model.

    :param out_path: Where to write the generated ``.ifc`` file.
    :param wall_count: Target total number of IfcWall elements across the
        whole model (split evenly across storeys). Not hit exactly, since
        walls are laid out on a rectangular grid per storey; the actual
        count is returned in the stats.
    :param storeys: Number of IfcBuildingStorey elements.
    :param schema: IFC schema version, e.g. "IFC4" or "IFC4X3".
    :param spaces_per_storey: How many IfcSpace elements to add per storey
        (one per interior grid cell, capped by however many cells exist).
    :param door_every: Insert an IfcDoor filling on every Nth interior
        (non-perimeter) wall segment. Use 0 to disable doors entirely.
    :param window_every: Insert an IfcWindow filling on every Nth perimeter
        wall segment. Use 0 to disable windows entirely.
    :param seed: Unused placeholder for reproducibility of future random
        variation; the layout is currently fully deterministic.
    :return: A ModelStats summary of what was actually generated.
    """
    t0 = time.time()
    stats = ModelStats(storeys=storeys)

    model = ifcopenshell.api.project.create_file(version=schema)
    project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="Heavy Perf Test Model")
    ifcopenshell.api.unit.assign_unit(model, length={"is_metric": True, "raw": "METERS"})

    model3d = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d
    )

    site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name="Building")
    ifcopenshell.api.aggregate.assign_object(model, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(model, products=[building], relating_object=site)

    walls_per_storey = max(4, wall_count // max(1, storeys))
    rows, cols = _grid_dims_for_wall_count(walls_per_storey)
    stats.grid_rows, stats.grid_cols = rows, cols

    for storey_index in range(storeys):
        elevation = storey_index * STOREY_HEIGHT
        storey = ifcopenshell.api.root.create_entity(
            model, ifc_class="IfcBuildingStorey", name=f"Storey {storey_index}"
        )
        ifcopenshell.api.aggregate.assign_object(model, products=[storey], relating_object=building)

        storey_walls = []
        interior_i = 0
        perimeter_i = 0
        for p1, p2, is_perimeter in _iter_grid_segments(rows, cols):
            wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall", name="Wall")
            wall_rep = create_2pt_wall(model, wall, body, p1, p2, elevation, WALL_HEIGHT, WALL_THICKNESS)
            ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=wall_rep)
            storey_walls.append(wall)
            stats.walls += 1

            if is_perimeter:
                perimeter_i += 1
                if window_every and perimeter_i % window_every == 0:
                    _add_window_filling(model, body, wall, p1, p2, elevation)
                    stats.windows += 1
            else:
                interior_i += 1
                if door_every and interior_i % door_every == 0:
                    _add_door_filling(model, body, wall, p1, p2, elevation)
                    stats.doors += 1

        ifcopenshell.api.spatial.assign_container(model, products=storey_walls, relating_structure=storey)

        n_spaces = min(spaces_per_storey, rows * cols)
        space_products = []
        placed = 0
        for r in range(rows):
            if placed >= n_spaces:
                break
            for c in range(cols):
                if placed >= n_spaces:
                    break
                space = _create_space(model, body, r, c, elevation)
                space_products.append(space)
                placed += 1
                stats.spaces += 1
        if space_products:
            ifcopenshell.api.aggregate.assign_object(model, products=space_products, relating_object=storey)

    model.write(out_path)
    stats.generation_seconds = time.time() - t0
    return stats


def _create_space(model, body, row: int, col: int, elevation: float):
    space = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSpace", name=f"Room {row}-{col}")
    profile = model.create_entity(
        "IfcRectangleProfileDef", ProfileType="AREA", XDim=BAY_SIZE * 0.9, YDim=BAY_SIZE * 0.9
    )
    solid = model.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=profile,
        Position=model.create_entity(
            "IfcAxis2Placement3D", Location=model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        ),
        ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=WALL_HEIGHT,
    )
    rep = model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=body,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=(solid,),
    )
    space.Representation = model.create_entity("IfcProductDefinitionShape", Representations=(rep,))
    cx = col * BAY_SIZE + BAY_SIZE / 2
    cy = row * BAY_SIZE + BAY_SIZE / 2
    ifcopenshell.api.geometry.edit_object_placement(
        model,
        product=space,
        matrix=[[1, 0, 0, cx], [0, 1, 0, cy], [0, 0, 1, elevation], [0, 0, 0, 1]],
    )
    return space


def _midpoint_matrix(p1, p2, elevation, cx_offset=0.0):
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    return [[1, 0, 0, mx], [0, 1, 0, my], [0, 0, 1, elevation + cx_offset], [0, 0, 0, 1]]


def _add_door_filling(model, body, wall, p1, p2, elevation):
    opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement", name="Opening")
    opening_rep = ifcopenshell.api.geometry.add_wall_representation(
        model, context=body, length=DOOR_WIDTH, height=DOOR_HEIGHT, thickness=WALL_THICKNESS * 2
    )
    ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=opening_rep)
    ifcopenshell.api.geometry.edit_object_placement(model, product=opening, matrix=_midpoint_matrix(p1, p2, elevation))
    ifcopenshell.api.feature.add_feature(model, feature=opening, element=wall)

    door = ifcopenshell.api.root.create_entity(model, ifc_class="IfcDoor", name="Door")
    door_rep = ifcopenshell.api.geometry.add_door_representation(
        model, context=body, overall_height=DOOR_HEIGHT, overall_width=DOOR_WIDTH
    )
    if door_rep is not None:
        ifcopenshell.api.geometry.assign_representation(model, product=door, representation=door_rep)
    ifcopenshell.api.geometry.edit_object_placement(model, product=door, matrix=_midpoint_matrix(p1, p2, elevation))
    ifcopenshell.api.feature.add_filling(model, opening=opening, element=door)
    return door


def _add_window_filling(model, body, wall, p1, p2, elevation):
    opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement", name="Opening")
    opening_rep = ifcopenshell.api.geometry.add_wall_representation(
        model, context=body, length=WINDOW_WIDTH, height=WINDOW_HEIGHT, thickness=WALL_THICKNESS * 2
    )
    ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=opening_rep)
    ifcopenshell.api.geometry.edit_object_placement(
        model, product=opening, matrix=_midpoint_matrix(p1, p2, elevation, cx_offset=WINDOW_SILL)
    )
    ifcopenshell.api.feature.add_feature(model, feature=opening, element=wall)

    window = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWindow", name="Window")
    window_rep = ifcopenshell.api.geometry.add_window_representation(
        model, context=body, overall_height=WINDOW_HEIGHT, overall_width=WINDOW_WIDTH
    )
    if window_rep is not None:
        ifcopenshell.api.geometry.assign_representation(model, product=window, representation=window_rep)
    ifcopenshell.api.geometry.edit_object_placement(
        model, product=window, matrix=_midpoint_matrix(p1, p2, elevation, cx_offset=WINDOW_SILL)
    )
    ifcopenshell.api.feature.add_filling(model, opening=opening, element=window)
    return window


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Output .ifc path")
    parser.add_argument("--walls", type=int, default=3000, help="Target total wall count (default: 3000)")
    parser.add_argument("--storeys", type=int, default=10, help="Number of building storeys (default: 10)")
    parser.add_argument("--schema", default="IFC4", help="IFC schema version (default: IFC4)")
    parser.add_argument("--spaces-per-storey", type=int, default=4, help="IfcSpace count per storey (default: 4)")
    parser.add_argument("--door-every", type=int, default=6, help="Add a door every Nth interior wall (0=disable)")
    parser.add_argument("--window-every", type=int, default=4, help="Add a window every Nth perimeter wall (0=disable)")
    args = parser.parse_args()

    stats = generate_heavy_model(
        args.out,
        wall_count=args.walls,
        storeys=args.storeys,
        schema=args.schema,
        spaces_per_storey=args.spaces_per_storey,
        door_every=args.door_every,
        window_every=args.window_every,
    )
    print(f"Wrote {args.out}")
    print(
        f"storeys={stats.storeys} walls={stats.walls} spaces={stats.spaces} "
        f"doors={stats.doors} windows={stats.windows} grid={stats.grid_rows}x{stats.grid_cols} "
        f"generation_seconds={stats.generation_seconds:.2f}"
    )


if __name__ == "__main__":
    main()
