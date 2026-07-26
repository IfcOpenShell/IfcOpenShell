#!/usr/bin/env python3
"""Author the demo model the web viewer embeds (sample.ifcview).

The web build bakes one small sidecar into MEMFS (--embed-file in
CMakeLists.txt) so every example page renders something before the user picks a
file. This script is how that fixture is produced, so it can be regenerated
rather than being an opaque committed blob:

    python3 make_sample.py                 # writes sample.ifc + sample.ifcview
    ninja -C ../../build-web               # re-embeds it

It needs ifcopenshell (Python) to author the IFC, and the sidecar_bake tool from
the desktop build to convert it:

    ninja -C ../../build-viewer sidecar_bake

Three elements — a slab, a wall and a beam — deliberately in DIFFERENT places
and different shapes. The scripting examples hide and re-colour objects one at a
time, so coincident geometry would make those calls look like no-ops: whatever
you hid would still be there, drawn by the object behind it.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit

HERE = Path(__file__).parent
BAKE = HERE / "../../build-viewer/ifcviewer/sidecar_bake"

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


def main() -> int:
    if not BAKE.exists():
        sys.exit(f"{BAKE} not found — build it with: ninja -C ../../build-viewer sidecar_bake")

    ifc = HERE / "sample.ifc"
    build_ifc(ifc)
    subprocess.run([str(BAKE), str(ifc)], check=True)

    # sidecar_bake writes <name>.ifcview next to the input.
    baked = ifc.with_suffix(".ifcview")
    if not baked.exists():
        sys.exit(f"sidecar_bake did not produce {baked}")
    shutil.move(baked, HERE / "sample.ifcview")
    print(f"wrote {HERE / 'sample.ifcview'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
