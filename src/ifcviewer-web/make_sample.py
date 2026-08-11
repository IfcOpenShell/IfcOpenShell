#!/usr/bin/env python3
"""Author the demo model the web viewer embeds (sample.ifcview).

The web build bakes one small sidecar into MEMFS (--embed-file in
CMakeLists.txt) so every example page renders something before the user picks a
file. This script is how that fixture is produced, so it can be regenerated
rather than being an opaque committed blob:

    python3 make_sample.py                 # writes sample.* and georef-a/b.*
    ninja -C ../../build-web               # re-embeds sample.ifcview

Also authors georef-a and georef-b: a pair that pins the federation behaviour.
The two carry DIFFERENT IfcMapConversions over DIFFERENT local coordinates,
chosen so both resolve to the same real-world point. A viewer that applies each
model's coordinate operation draws them on top of each other; one that ignores
it (as the web viewer did before it seeded georef from the sidecar) draws them
~707 m apart. They are small single-box models — the assertion is about where
they land, not what they look like.

It needs ifcopenshell (Python) to author the IFC, and the sidecar_bake tool from
the desktop build to convert it:

    ninja -C ../../build-viewer sidecar_bake

Three elements — a slab, a wall and a beam — deliberately in DIFFERENT places
and different shapes. The scripting examples hide and re-colour objects one at a
time, so coincident geometry would make those calls look like no-ops: whatever
you hid would still be there, drawn by the object behind it.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.georeference
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit

HERE = Path(__file__).parent
# The sidecar baker. Override with SIDECAR_BAKE when it lives outside the
# desktop build tree — there is currently no in-tree `sidecar_bake` target, so
# the default below only resolves if one has been added locally.
BAKE = Path(os.environ.get("SIDECAR_BAKE", HERE / "../../build-viewer/ifcviewer/sidecar_bake"))

# (class, name, footprint w x d in m, height in m, placement x/y/z in m)
ELEMENTS = [
    ("IfcSlab", "Slab", (6.0, 6.0), 0.2, (-3.0, -3.0, 0.0)),
    ("IfcWall", "Wall", (5.0, 0.3), 3.0, (-2.5, -2.5, 0.2)),
    ("IfcBeam", "Beam", (0.3, 5.0), 0.3, (2.0, -2.5, 3.2)),
]


def build_ifc(path: Path) -> None:
    f = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Web viewer sample")
    ifcopenshell.api.unit.assign_unit(f, length={"is_metric": True, "raw": "METERS"})
    body = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=body
    )

    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="Site")
    storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Ground floor")
    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=site)

    for ifc_class, name, (w, d), height, (x, y, z) in ELEMENTS:
        element = ifcopenshell.api.root.create_entity(f, ifc_class=ifc_class, name=name)
        ifcopenshell.api.spatial.assign_container(f, products=[element], relating_structure=storey)

        # A rectangular profile extruded up — enough to be a recognisable,
        # distinctly-placed solid without dragging in a whole modelling stack.
        profile = f.create_entity(
            "IfcRectangleProfileDef",
            ProfileType="AREA",
            XDim=w,
            YDim=d,
            Position=f.create_entity(
                "IfcAxis2Placement2D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(w / 2, d / 2))
            ),
        )
        solid = f.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=profile,
            Depth=height,
            Position=f.create_entity(
                "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
            ),
            ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        )
        representation = f.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[solid],
        )
        ifcopenshell.api.geometry.assign_representation(f, product=element, representation=representation)
        ifcopenshell.api.geometry.edit_object_placement(
            f, product=element, matrix=ifcopenshell.util.placement.a2p((x, y, z), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
        )

    f.write(str(path))


# Two models that must coincide once each one's IfcMapConversion is applied.
#
# With no grid rotation and unit scale 1, the coordinate operation is a pure
# translation, so global = local + (eastings, northings, height). Both entries
# below sum to the same global point:
#
#   a: local (0, 0)     + (1000, 2000) = (1000, 2000)
#   b: local (500, 500) + ( 500, 1500) = (1000, 2000)
#
# The local offset between them (~707 m) is the error a viewer shows when it
# ignores the coordinate operation, which is far larger than the 2 m boxes —
# so the test cannot pass by accident.
GEOREF_MODELS = [
    ("georef-a", (0.0, 0.0), (1000.0, 2000.0)),
    ("georef-b", (500.0, 500.0), (500.0, 1500.0)),
]


def build_georef_ifc(path: Path, local_xy: tuple, map_en: tuple) -> None:
    """One 2 m box at `local_xy`, georeferenced by `map_en` eastings/northings."""
    f = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name=path.stem)
    ifcopenshell.api.unit.assign_unit(f, length={"is_metric": True, "raw": "METERS"})
    body = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=body
    )

    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="Site")
    storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Ground floor")
    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=site)

    ifcopenshell.api.georeference.add_georeferencing(f)
    ifcopenshell.api.georeference.edit_georeferencing(
        f,
        projected_crs={"Name": "EPSG:3857"},
        coordinate_operation={
            "Eastings": map_en[0],
            "Northings": map_en[1],
            "OrthogonalHeight": 0.0,
            # Grid north == project north, and map units == project units, so
            # the operation reduces to the pure translation described above.
            "XAxisAbscissa": 1.0,
            "XAxisOrdinate": 0.0,
            "Scale": 1.0,
        },
    )

    # TWO boxes, deliberately different sizes so they are two distinct meshes.
    # reorderSidecarByMorton bails out at fewer than two meshes and then writes
    # no chunk table at all, and a sidecar with no chunk table can never stream
    # over the web byte-range path — the loader has no locator to fetch with.
    # A one-box model here would load and simply never draw.
    for i, (w, d) in enumerate([(2.0, 2.0), (1.0, 3.0)]):
        element = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name=f"Box{i}")
        ifcopenshell.api.spatial.assign_container(f, products=[element], relating_structure=storey)
        profile = f.create_entity(
            "IfcRectangleProfileDef",
            ProfileType="AREA",
            XDim=w,
            YDim=d,
            Position=f.create_entity(
                "IfcAxis2Placement2D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(w / 2, d / 2))
            ),
        )
        solid = f.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=profile,
            Depth=2.0,
            Position=f.create_entity(
                "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
            ),
            ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        )
        representation = f.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[solid],
        )
        ifcopenshell.api.geometry.assign_representation(f, product=element, representation=representation)
        ifcopenshell.api.geometry.edit_object_placement(
            f,
            product=element,
            matrix=ifcopenshell.util.placement.a2p(
                (local_xy[0] + i * 3.0, local_xy[1], 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)
            ),
        )
    f.write(str(path))


def bake(ifc: Path, out: Path) -> None:
    subprocess.run([str(BAKE), str(ifc)], check=True)
    # sidecar_bake writes <name>.ifcview next to the input.
    baked = ifc.with_suffix(".ifcview")
    if not baked.exists():
        sys.exit(f"sidecar_bake did not produce {baked}")
    shutil.move(baked, out)
    print(f"wrote {out}")


def main() -> int:
    if not BAKE.exists():
        sys.exit(f"{BAKE} not found — point SIDECAR_BAKE at a sidecar_bake binary")

    ifc = HERE / "sample.ifc"
    build_ifc(ifc)
    bake(ifc, HERE / "sample.ifcview")

    for stem, local_xy, map_en in GEOREF_MODELS:
        georef_ifc = HERE / f"{stem}.ifc"
        build_georef_ifc(georef_ifc, local_xy, map_en)
        bake(georef_ifc, HERE / f"{stem}.ifcview")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
