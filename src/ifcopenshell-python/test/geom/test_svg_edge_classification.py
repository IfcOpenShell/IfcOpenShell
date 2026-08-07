"""Regression tests for the SVG serializer's edge classification (issue #3742):
cross-coplanar / mat-style-change classification, the coincident-edge paint-order
dedup pass, and restore_coincident_hidden_edges()'s HLR depth-tie restoration.

All geometry here is synthetic and minimal, built directly via low-level IFC
construction rather than realistic wall/slab authoring, so that the exact
geometric relationship each bug depends on (an exact touching plane, a specific
offset) is fully controlled and doesn't drift if higher-level authoring helpers
change their defaults.

Every scenario in this file was cross-checked against the real Bonsai/Blender
`bim.create_drawing` pipeline (not just this module's own direct-serializer
path) before being written here, using a matching camera (an `ELEVATION_VIEW`/
`SOUTH` drawing, i.e. a camera at negative Y looking towards +Y, positioned
outside all test geometry so it never bisects a product -- an early version of
this suite's manual verification did exactly that by accident and produced a
subtly different, invalid result). See `.spike_notes/svg_test_dev/` (outside
this repo) for the saved `.ifc`/`.svg` artifacts from that cross-check, not
committed here.

Two non-obvious requirements this suite discovered the hard way, both
confirmed by reading `find_cross_coplanar_matches()` in `SvgSerializer.h`
directly rather than assumed:

- Project length units must be explicitly set to metres. `ifcopenshell.api.unit
  .assign_unit()` defaults to millimetres, while `ShapeBuilder`'s own numeric
  arguments are *not* unit-converted -- leaving the default silently produces a
  1000x mismatch between a product's shape size and its placement offset.
- Cross-coplanar (and therefore mat-style-change Case A) matching is skipped
  entirely for a product pair where *neither* side has a resolved material AND
  *either* side lacks a style -- both scenario products need at least a shared
  material (or, if no material, a shared style) or the pair is never even
  considered, regardless of how their geometry is arranged.
"""

import xml.dom.minidom
from dataclasses import dataclass

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.geom
from ifcopenshell.util.shape_builder import ShapeBuilder

W = ifcopenshell.ifcopenshell_wrapper


def _make_project() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance, ifcopenshell.entity_instance]:
    """Minimal project + Body/Model context + spatial structure, metre units."""
    ifc_file = ifcopenshell.file(schema="IFC4")
    project = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
    ifcopenshell.api.unit.assign_unit(ifc_file, length={"is_metric": True, "raw": "METERS"})
    context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")
    body_context = ifcopenshell.api.context.add_context(
        ifc_file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey", name="Storey")
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=project, products=[site])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=site, products=[building])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=building, products=[storey])
    return ifc_file, body_context, storey


def _add_box(
    ifc_file: ifcopenshell.file,
    body_context: ifcopenshell.entity_instance,
    storey: ifcopenshell.entity_instance,
    name: str,
    size: tuple[float, float, float],
    translation: tuple[float, float, float],
    ifc_class: str = "IfcWall",
    material: ifcopenshell.entity_instance | None = None,
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> ifcopenshell.entity_instance:
    """A simple box product (size=(x,y,z) in the box's own local axes), placed
    at an exact world translation, with an optional rotated placement (for a
    sloped/rotated box; `x_axis`/`z_axis` become the placement's own axes, in
    world space) and an optional shared material.
    """
    builder = ShapeBuilder(ifc_file)
    product = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=ifc_class, name=name)
    ifcopenshell.api.spatial.assign_container(ifc_file, relating_structure=storey, products=[product])
    profile = builder.rectangle(size=(size[0], size[1]))
    extrusion = builder.extrude(profile, magnitude=size[2])
    representation = builder.get_representation(body_context, extrusion)
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=product, representation=representation)
    x = np.array(x_axis, dtype=float)
    z = np.array(z_axis, dtype=float)
    y = np.cross(z, x)
    matrix = np.eye(4)
    matrix[:3, 0] = x
    matrix[:3, 1] = y
    matrix[:3, 2] = z
    matrix[:3, 3] = translation
    ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=product, matrix=matrix)
    if material is not None:
        ifcopenshell.api.material.assign_material(ifc_file, products=[product], material=material)
    return product


def _axis_refdir_to_matrix(
    location: tuple[float, float, float],
    axis: tuple[float, float, float],
    ref_direction: tuple[float, float, float],
) -> np.ndarray:
    z = np.array(axis, dtype=float)
    z /= np.linalg.norm(z)
    x = np.array(ref_direction, dtype=float)
    x = x - np.dot(x, z) * z
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    matrix = np.eye(4)
    matrix[:3, 0] = x
    matrix[:3, 1] = y
    matrix[:3, 2] = z
    matrix[:3, 3] = location
    return matrix


def _add_arbitrary_profile_slab(
    ifc_file: ifcopenshell.file,
    body_context: ifcopenshell.entity_instance,
    storey: ifcopenshell.entity_instance,
    name: str,
    points_2d: list[tuple[float, float]],
    depth: float,
    location: tuple[float, float, float],
    axis: tuple[float, float, float],
    ref_direction: tuple[float, float, float],
    ifc_class: str = "IfcRoof",
    extruded_direction: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> ifcopenshell.entity_instance:
    """A product with an arbitrary closed polygon profile (an
    `IfcIndexedPolyCurve`, built via raw low-level entity creation rather than
    `ShapeBuilder`) extruded along `extruded_direction` (local to the item's
    own, identity `Position`; defaults to local +Z), placed at an exact world
    location/orientation. Used for scenarios that need a specific irregular
    footprint and slope, where `_add_box`'s rectangular profile isn't enough.
    `location`/`axis`/`ref_direction` are project-unit coordinates applied
    with `is_si=False` -- `ShapeBuilder`/`edit_object_placement`'s usual
    SI-metres convention doesn't apply here since callers may want non-metre
    project units (see `test_cluster_b_depth_tie_restoration`).
    """
    product = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=ifc_class, name=name)
    ifcopenshell.api.spatial.assign_container(ifc_file, relating_structure=storey, products=[product])
    point_list = ifc_file.createIfcCartesianPointList2D(points_2d)
    poly_curve = ifc_file.createIfcIndexedPolyCurve(point_list, None, None)
    profile = ifc_file.createIfcArbitraryClosedProfileDef("AREA", None, poly_curve)
    direction = ifc_file.createIfcDirection(extruded_direction)
    solid = ifc_file.createIfcExtrudedAreaSolid(profile, None, direction, depth)
    shape_rep = ifc_file.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [solid])
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=product, representation=shape_rep)
    matrix = _axis_refdir_to_matrix(location, axis, ref_direction)
    ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=product, matrix=matrix, is_si=False)
    return product


@dataclass(frozen=True)
class Edge:
    guid: str
    cls: str
    p0: tuple[float, float]
    p1: tuple[float, float]

    def near(self, other_p0: tuple[float, float], other_p1: tuple[float, float], tol: float = 1e-3) -> bool:
        """Endpoint match within `tol`, order-independent."""

        def close(a, b):
            return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol

        return (close(self.p0, other_p0) and close(self.p1, other_p1)) or (
            close(self.p0, other_p1) and close(self.p1, other_p0)
        )


def render_svg(
    ifc_file: ifcopenshell.file,
    camera_pos: tuple[float, float, float],
    camera_dir: tuple[float, float, float],
    camera_ref: tuple[float, float, float] = (1.0, 0.0, 0.0),
    use_cross_coplanar: bool = False,
    use_mat_style_change: bool = False,
    render_cross_coplanar: bool = False,
    scale: float = 1.0,
    bounding_rectangle: tuple[float, float] = (20000.0, 20000.0),
) -> str:
    """Drive `SvgSerializer` directly (no Blender), matching the pattern
    `ifcopenshell/draw.py` uses. `camera_dir` is the direction *from the scene
    towards the camera* (not the camera's own view direction) -- matching
    `SvgSerializer.h`'s own `@nb negative z in accordance with occt projector
    convention` comment and confirmed empirically: a camera at
    `(x, -10, z)` "looking" into the scene along +Y needs `camera_dir=(0,-1,0)`,
    not `(0,1,0)`, to produce any visible geometry at all.
    """
    geom_settings = ifcopenshell.geom.settings(ELEMENT_HIERARCHY=True)
    geom_settings.set("dimensionality", W.SURFACES_AND_SOLIDS)
    geom_settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)
    geom_settings.set("apply-default-materials", True)
    geom_settings.set("svg-use-edge-classification", True)
    geom_settings.set("svg-use-cross-coplanar-classification", use_cross_coplanar)
    geom_settings.set("svg-use-mat-style-change-classification", use_mat_style_change)
    geom_settings.set("svg-render-cross-coplanar-edges", render_cross_coplanar)

    buffer = ifcopenshell.geom.serializers.buffer()
    serializer_settings = ifcopenshell.geom.serializer_settings()
    sr = ifcopenshell.geom.serializers.svg(buffer, geom_settings, serializer_settings)
    sr.setFile(ifc_file)
    sr.setPolygonal(True)
    sr.setUseNamespace(True)
    sr.setUseHlrPoly(True)
    sr.setUsePrefiltering(True)
    sr.setAlwaysProject(True)
    sr.setBoundingRectangle(*bounding_rectangle)
    sr.setScale(scale)
    sr.addDrawing(camera_pos, camera_dir, camera_ref, "Test", True)

    it = ifcopenshell.geom.iterator(geom_settings, ifc_file)
    for elem in it:
        sr.write(elem)
    sr.finalize()
    return buffer.get_value()


def parse_edges(svg: str) -> list[Edge]:
    """Parse an SVG string into a flat list of (owning product guid, class,
    endpoints) for every `<path>`, tracking the enclosing `<g ifc:guid=...>`
    the same way this whole branch's manual verification has all session.
    Only handles the simple "M x,y L x,y" polyline paths this suite's own
    synthetic geometry produces -- not a general SVG path parser.
    """
    dom = xml.dom.minidom.parseString(svg)
    edges: list[Edge] = []

    def walk(node, guid_stack):
        if node.nodeType != node.ELEMENT_NODE:
            return
        if node.tagName == "g":
            guid = node.getAttribute("ifc:guid") or None
            guid_stack = guid_stack + [guid] if guid else guid_stack
        elif node.tagName == "path" and node.hasAttribute("d") and node.hasAttribute("class"):
            d = node.getAttribute("d")
            cls = node.getAttribute("class")
            tokens = d.replace("M", "").replace("L", "").strip().split()
            if len(tokens) == 2:
                p0 = tuple(float(v) for v in tokens[0].split(","))
                p1 = tuple(float(v) for v in tokens[1].split(","))
                guid = guid_stack[-1] if guid_stack else ""
                edges.append(Edge(guid, cls, p0, p1))
        for child in node.childNodes:
            walk(child, guid_stack)

    walk(dom.documentElement, [])
    return edges


def has_edge(edges: list[Edge], guid: str, cls: str, p0: tuple[float, float], p1: tuple[float, float]) -> bool:
    return any(e.guid == guid and e.cls == cls and e.near(p0, p1) for e in edges)


def has_any_edge(edges: list[Edge], guid: str, p0: tuple[float, float], p1: tuple[float, float]) -> bool:
    """Same coordinates, any class -- for "must be absent entirely" checks."""
    return any(e.guid == guid and e.near(p0, p1) for e in edges)


def test_cross_coplanar_basic_touching_boundary():
    """Two walls of identical size, pushed flush together side-by-side, with a
    SHARED material -- confirmed via `find_cross_coplanar_matches()` that a
    matching material (or, absent that, a matching style) is a precondition
    for cross-coplanar matching to even be attempted, regardless of geometry.
    Without a shared material this exact scenario instead classifies the
    shared boundary as a genuine `outline` on both sides (also confirmed via
    the real Bonsai pipeline) -- not a bug, just not what this test targets.
    """
    ifc_file, body_context, storey = _make_project()
    material = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    wall_a = _add_box(
        ifc_file, body_context, storey, "WallA", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0), material=material
    )
    wall_b = _add_box(
        ifc_file, body_context, storey, "WallB", (2.0, 0.2, 2.0), (2.0, 0.0, 0.0), material=material
    )

    svg = render_svg(
        ifc_file,
        camera_pos=(2.0, -5.0, 1.0),
        camera_dir=(0.0, -1.0, 0.0),
        use_cross_coplanar=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    # Viewed from a Y-axis elevation, the visible plane is world-X (horizontal)
    # and world-Z (vertical, height) -- world-Y (wall thickness) is the view
    # axis itself and isn't represented. Scale 1000, offset 8000 in X and 9000
    # in Z comes from setBoundingRectangle(20000, 20000) centring the drawing.
    shared_p0, shared_p1 = (10000.0, 9000.0), (10000.0, 11000.0)
    assert has_edge(edges, wall_a.GlobalId, "cross-coplanar", shared_p0, shared_p1)
    assert has_edge(edges, wall_b.GlobalId, "cross-coplanar", shared_p0, shared_p1)
    # The two walls' own OUTER silhouette edges must still be plain outline.
    assert has_edge(edges, wall_a.GlobalId, "outline", (8000.0, 9000.0), (8000.0, 11000.0))
    assert has_edge(edges, wall_b.GlobalId, "outline", (12000.0, 9000.0), (12000.0, 11000.0))


def test_cross_coplanar_match_must_not_steal_edge_from_occluded_neighbour():
    """`find_cross_coplanar_matches()` (`SvgSerializer.h`) can genuinely,
    validly confirm two products are coplanar-and-touching in 3D while a
    wholly separate third product sits directly in front of one of them from
    the current camera -- classifying the touching boundary as this pair's
    relationship then misrepresents what's actually visible. Reported by the
    user from a real isometric drawing: two same-material stacked walls with
    a slab, where the lower wall (hidden behind the upper wall from that
    camera) was coplanar-matched with the slab, producing a wrongly-
    classified `cross-coplanar`/`mat-style-change` edge where a plain
    `outline` corner between the (actually visible) upper wall and slab
    should have been shown instead.

    `Slab` (large) and `LowerWall` (small) share a touching boundary at
    X=4 (same material, same top-face plane Z=0.2 -- a genuine, valid
    cross-coplanar match, confirmed by the control case below). `UpperWall`
    sits directly above `LowerWall`'s own far portion and centroid (nearer
    the camera, which looks straight down) WITHOUT covering the X=4 shared
    edge itself -- so that edge stays genuinely HLR-visible (not just
    occluded outright, which would trivially hide it regardless of class and
    prove nothing -- confirmed this distinction matters directly: an earlier
    attempt at this test, where the occluder also covered the shared edge,
    produced byte-identical output whether or not the fix was present, since
    HLR's own real occlusion hid the whole region regardless of
    classification either way).

    Confirmed via direct before/after comparison against unfixed code
    (temporarily reverted, rebuilt, tested, then restored): pre-fix, the
    shared edge is classified `cross-coplanar` on both `Slab` and
    `LowerWall` despite `LowerWall` being substantially occluded -- exactly
    the reported bug. Post-fix, the occlusion check runs per accepted
    sub-interval (see `point_near_edge_interior()`) rather than once for the
    whole face, so the result is a genuine partial split rather than an
    all-or-nothing verdict: the portion of the shared edge actually behind
    `UpperWall` stays `outline`, while the remaining portion -- genuinely
    unoccluded, since `UpperWall` doesn't cover the entire shared edge --
    correctly still shows `cross-coplanar`. (A whole-face occlusion check was
    tried first and rejected: confirmed directly against a real building
    file that it wrongly rejects an ENTIRE multi-metre-long face over a
    single unrelated object partially in front of one small portion of it,
    days after the whole-face version of this fix first shipped -- see
    project_cross_coplanar_known_issues.md item 4d's follow-up.)
    """
    ifc_file, body_context, storey = _make_project()
    material = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    slab = _add_box(ifc_file, body_context, storey, "Slab", (4.0, 4.0, 0.2), (0.0, 0.0, 0.0), material=material)
    lower_wall = _add_box(
        ifc_file, body_context, storey, "LowerWall", (1.0, 1.0, 0.2), (4.0, 0.0, 0.0), material=material
    )
    _add_box(ifc_file, body_context, storey, "UpperWall", (0.9, 1.3, 0.5), (4.3, -0.1, 0.5))

    svg = render_svg(
        ifc_file,
        camera_pos=(2.0, 2.0, 10.0),
        camera_dir=(0.0, 0.0, 1.0),
        camera_ref=(1.0, 0.0, 0.0),
        use_cross_coplanar=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    # The portion of the shared X=4 boundary nearer UpperWall must stay plain
    # outline -- LowerWall being occluded there means its relationship with
    # Slab isn't what's actually shown for that portion, regardless of how
    # geometrically valid it is in 3D. The remaining portion, genuinely
    # unoccluded, must still show cross-coplanar on both sides.
    occluded_p0, occluded_p1 = (11400.0, 7950.0), (11400.0, 10950.0)
    visible_p0, visible_p1 = (11400.0, 10950.0), (11400.0, 11950.0)
    assert has_edge(edges, slab.GlobalId, "outline", occluded_p0, occluded_p1)
    assert has_edge(edges, slab.GlobalId, "cross-coplanar", visible_p0, visible_p1)
    assert not has_edge(edges, slab.GlobalId, "cross-coplanar", occluded_p0, occluded_p1)
    assert has_edge(edges, lower_wall.GlobalId, "cross-coplanar", visible_p0, visible_p1)


def test_cross_coplanar_match_control_without_occluder():
    """Control for `test_cross_coplanar_match_must_not_steal_edge_from_
    occluded_neighbour()` -- same `Slab`/`LowerWall` pair, no `UpperWall`.
    Confirms the occlusion-awareness fix doesn't just unconditionally reject
    every match: the genuine cross-coplanar relationship must still be found
    and classified correctly when nothing occludes it.
    """
    ifc_file, body_context, storey = _make_project()
    material = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    slab = _add_box(ifc_file, body_context, storey, "Slab", (4.0, 4.0, 0.2), (0.0, 0.0, 0.0), material=material)
    lower_wall = _add_box(
        ifc_file, body_context, storey, "LowerWall", (1.0, 1.0, 0.2), (4.0, 0.0, 0.0), material=material
    )

    svg = render_svg(
        ifc_file,
        camera_pos=(2.0, 2.0, 10.0),
        camera_dir=(0.0, 0.0, 1.0),
        camera_ref=(1.0, 0.0, 0.0),
        use_cross_coplanar=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    shared_p0, shared_p1 = (11500.0, 12000.0), (11500.0, 11000.0)
    assert has_edge(edges, slab.GlobalId, "cross-coplanar", shared_p0, shared_p1)
    assert has_edge(edges, lower_wall.GlobalId, "cross-coplanar", shared_p0, shared_p1)


def test_cross_coplanar_match_stacked_same_footprint_must_not_self_occlude():
    """Regression for a follow-up bug in the occlusion-awareness fix added for
    `test_cross_coplanar_match_must_not_steal_edge_from_occluded_neighbour()`
    above. Reported by the user from a real isometric drawing: two
    same-material walls stacked directly on top of each other at the
    *identical* footprint (confirmed via extracted world-placement matrices --
    same X/Y placement, differing only in Z, meeting exactly at the boundary)
    were wrongly classified `outline` instead of `cross-coplanar` at their
    shared seam, immediately after the occlusion-awareness fix landed.

    Root cause: `is_occluded_by_other()` (`SvgSerializer.h`) ray-cast each
    face's own interior point toward the camera against *every* item's
    intersector, with no exclusion at all. For two products stacked directly
    on the same footprint, a ray from the lower product's own top-face
    interior point toward the camera immediately re-enters the *upper*
    product's own solid -- which is one of the two products the match is
    being evaluated *for*, not a genuinely separate third-party occluder. The
    fix excludes both products of the pair currently under test from the
    ray-cast.

    `LowerBox` and `UpperBox` share the exact same (2.0, 2.0) X/Y footprint,
    stacked directly on top of each other in Z with a shared material -- no
    third product involved at all, isolating this from the original
    third-party-occlusion scenario the earlier fix targeted (still covered,
    unchanged, by the two tests above).
    """
    ifc_file, body_context, storey = _make_project()
    material = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    lower_box = _add_box(
        ifc_file, body_context, storey, "LowerBox", (2.0, 2.0, 1.0), (0.0, 0.0, 0.0), material=material
    )
    upper_box = _add_box(
        ifc_file, body_context, storey, "UpperBox", (2.0, 2.0, 1.0), (0.0, 0.0, 1.0), material=material
    )

    svg = render_svg(
        ifc_file,
        camera_pos=(10.0, 10.0, 10.0),
        camera_dir=(0.5773502691896258, 0.5773502691896258, 0.5773502691896258),
        camera_ref=(0.7071067811865475, -0.7071067811865475, 0.0),
        use_cross_coplanar=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    # The shared seam at Z=1 (world) must be classified cross-coplanar on
    # both boxes -- the two products standing directly on one another is the
    # touching relationship itself, not evidence that it's hidden.
    cross_coplanar_edges_lower = [e for e in edges if e.guid == lower_box.GlobalId and e.cls == "cross-coplanar"]
    cross_coplanar_edges_upper = [e for e in edges if e.guid == upper_box.GlobalId and e.cls == "cross-coplanar"]
    assert cross_coplanar_edges_lower, "LowerBox has no cross-coplanar edges at all -- self-occlusion regression"
    assert cross_coplanar_edges_upper, "UpperBox has no cross-coplanar edges at all -- self-occlusion regression"
    for edge in cross_coplanar_edges_lower + cross_coplanar_edges_upper:
        assert edge.cls != "outline"


def test_cross_coplanar_match_excludes_whole_object_hidden_neighbour():
    """Regression for issue #3742's real-file follow-up (a real-world project
    file used for QA): a product that is itself almost entirely hidden behind
    OTHER products in a given view must not be allowed to donate its one
    surviving, same-material seam to a cross-coplanar match -- doing so wrongly
    steals classification of an unrelated, genuinely-visible neighbour's own
    edge, which should instead just be a plain `outline` corner between two
    separate, non-coplanar objects.

    Real-file diagnosis: wall #70370 (`HiddenWall` here) sat almost entirely
    hidden behind wall #70168 (`VisibleWall`) and slab #82574 (`Slab`) from an
    isometric camera. `HiddenWall` and `VisibleWall` share the same material
    and a genuinely coplanar left face (X=6); `HiddenWall` also happens to sit
    exactly in `Slab`'s own top-face plane (Z=0.2) at a touching (not
    overlapping) footprint. `find_cross_coplanar_matches()`'s whole-object
    visibility pre-filter (`SvgSerializer.h`) is supposed to exclude
    `HiddenWall` from matching entirely once it determines the product
    contributes essentially nothing to this view -- but an earlier version of
    that filter's own occlusion test, `touching_foreign_face()`, returned only
    the FIRST coincident face it found by item index. Since `Slab` (created
    first, lower item index) is ALSO genuinely coincident with `HiddenWall`'s
    own top edge (both sit in the same Z=0.2 plane), the filter nudged toward
    `Slab`'s own (huge, distant, irrelevant here) face centroid instead of
    `VisibleWall`'s -- missing the real, nearby occluder standing directly on
    top of `HiddenWall`, and wrongly judging `HiddenWall` still "visible".
    Fixed by trying every genuinely-touching candidate face's own centroid
    (OR-combined), not just the first found.

    `HiddenWall` and `VisibleWall` share the exact same (X, Y) footprint,
    stacked directly in Z (`VisibleWall` on top) -- deliberately the same
    stacking pattern as `test_cross_coplanar_match_stacked_same_footprint_
    must_not_self_occlude()` above, so this test also confirms the new
    whole-object filter doesn't reintroduce that already-fixed self-occlusion
    bug for the *matched* pair itself (`HiddenWall`/`VisibleWall`) while still
    correctly excluding `HiddenWall` from view because of the *third* object
    (`Slab`) it also happens to sit in-plane with.

    This exercises the overall whole-object-exclusion mechanism end to end
    (confirmed red without the pre-filter at all, green with it) but does NOT
    specifically discriminate the "wrong first candidate" sub-bug on its own --
    a top-down camera makes VisibleWall's plain (unnudged) occlusion of
    HiddenWall sufficient by itself, so the nudge/multi-candidate logic never
    actually gets exercised by this camera choice. An oblique camera is needed
    to reproduce the real grazing-ray gap that made the wrong-candidate nudge
    observable in the first place, but changing only the camera (same
    geometry) exposed a genuinely-visible OTHER edge of HiddenWall instead
    (an real, correct silhouette-offset effect from viewing two same-footprint,
    different-Z-height boxes obliquely under parallel projection, not a bug) --
    several attempts at reshaping the geometry to isolate the specific
    "grazing ray, ambiguous coincident candidate" scenario cleanly ran out of
    time without succeeding. Per this suite's own established precedent (see
    e.g. `test_cross_coplanar_match_partial_occlusion_within_one_raw_interval`'s
    own note on this), relying on the real-file verification for that specific
    mechanism instead: traced directly against the same real-world project file,
    confirmed `touching_foreign_face()` matching the slab's face first (at
    `p=(6.20001, *, 0)`, `match_idx` pointing at the slab, not wall #70168)
    before the fix, and confirmed the real file's own wall #70168/slab #82574
    corner renders plain `outline` after it.
    """
    ifc_file, body_context, storey = _make_project()
    material = ifcopenshell.api.material.add_material(ifc_file, name="Stone")
    slab = _add_box(ifc_file, body_context, storey, "Slab", (6.0, 6.0, 0.2), (0.0, 0.0, 0.0))
    hidden_wall = _add_box(
        ifc_file, body_context, storey, "HiddenWall", (1.0, 1.0, 0.2), (6.0, 0.0, 0.0), material=material
    )
    visible_wall = _add_box(
        ifc_file, body_context, storey, "VisibleWall", (1.0, 1.0, 1.0), (6.0, 0.0, 0.2), material=material
    )

    svg = render_svg(
        ifc_file,
        camera_pos=(3.0, 0.5, 10.0),
        camera_dir=(0.0, 0.0, 1.0),
        camera_ref=(1.0, 0.0, 0.0),
        use_cross_coplanar=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    # HiddenWall must contribute no cross-coplanar/mat-style-change edges at
    # all -- it's excluded from matching entirely, not just partially split.
    assert not any(e.guid == hidden_wall.GlobalId and e.cls in ("cross-coplanar", "mat-style-change") for e in edges)
    # VisibleWall and Slab must never coplanar-match with EACH OTHER (their
    # faces are perpendicular) -- their shared corner must be plain outline,
    # not contaminated by VisibleWall's own coplanar relationship with the
    # (excluded) HiddenWall.
    assert not any(e.guid == visible_wall.GlobalId and e.cls in ("cross-coplanar", "mat-style-change") for e in edges)
    assert not any(e.guid == slab.GlobalId and e.cls in ("cross-coplanar", "mat-style-change") for e in edges)
    assert any(e.guid == visible_wall.GlobalId and e.cls == "outline" for e in edges)
    assert any(e.guid == slab.GlobalId and e.cls == "outline" for e in edges)


def test_cross_coplanar_match_partial_occlusion_within_one_raw_interval():
    """`accumulate_edge_coverage()` (`SvgSerializer.h`) accepts or rejects an
    entire raw matched interval from a SINGLE occlusion test at its own
    midpoint (`SvgSerializer.h` ~line 681: `t_mid = 0.5 * (cursor +
    piece_end)`, tested once via `is_occluded(mid)`) -- there is no
    sub-splitting based on where occlusion actually starts/stops within that
    interval, unlike `restore_coincident_hidden_edges()`'s own
    `restorable_intervals()`/`refine_transition()` (added in P1-4e), which
    bisection-splits at the real occlusion transition instead of trusting one
    coarse sample.

    Reported by the user from real project drawings (`coplanar join.ifc`'s
    own PLAN_VIEW/ORTHOGRAPHIC-X): a large sub-edge that's only PARTLY
    genuinely occluded by an unrelated third product falls back to `outline`
    in its ENTIRETY, including the genuinely-unoccluded portions -- while a
    neighbouring tiny fragment (its own, separately-tested raw interval)
    happens to land outside the occluder and survives correctly, producing
    an outcome that looks arbitrarily inconsistent until you realise each
    fragment only ever gets ONE sample point.

    `WallA`/`WallB` share the exact same (2.0, 0.2, 2.0) footprint touching
    at X=2 (verbatim `test_cross_coplanar_basic_touching_boundary` geometry,
    confirmed via that test to classify as one single, whole `cross-coplanar`
    edge with no occluder present). A small `Occluder` box sits directly in
    front of the camera's view (smaller Y, nearer the camera which looks
    along +Y) straddling X=2, covering only the MIDDLE third
    (world Z=[0.8, 1.2]) of the shared edge's Z=[0, 2] extent -- confirmed via
    direct debug tracing (temporary, reverted) that occlusion genuinely
    varies within this SINGLE raw interval (occluded at the interval's own
    midpoint Z=1.0, clear at both Z=0.1 and Z=1.9), i.e. this is not a
    multi-raw-interval case like
    `test_cross_coplanar_match_must_not_steal_edge_from_occluded_neighbour()`
    above (that test's partial split works via separate raw contributions,
    each individually uniform -- it does not exercise this bug at all).

    Confirmed directly against unfixed code: the whole Z=[0,2] edge -- both
    genuinely-unoccluded outer thirds included -- degrades to `outline`, with
    no `cross-coplanar` edge for this boundary anywhere.

    Post-fix, the two genuinely-unoccluded outer thirds correctly show
    `cross-coplanar` again. Exact coordinates below were captured empirically
    from this exact scene (fixed code), not hand-derived -- same convention
    as `test_restore_coincident_hidden_edges_partial_occlusion`.

    Re-captured (issue #3742 follow-up) after gating the occlusion-awareness
    nudge on `touches_foreign_face()` -- the transition points shifted by
    ~0.01 world units (now landing almost exactly on the Occluder's own true
    Z=[0.8, 1.2] edge, rather than the old ungated nudge's slight overshoot
    past it), and the small transitional `outline` sliver this test used to
    also carry disappeared entirely once the nudge no longer overshoots.
    Neither is a regression in this test's own logic.
    """
    ifc_file, body_context, storey = _make_project()
    material = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    wall_a = _add_box(
        ifc_file, body_context, storey, "WallA", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0), material=material
    )
    wall_b = _add_box(
        ifc_file, body_context, storey, "WallB", (2.0, 0.2, 2.0), (2.0, 0.0, 0.0), material=material
    )
    _add_box(ifc_file, body_context, storey, "Occluder", (0.4, 0.3, 0.4), (1.8, -0.5, 0.8))

    svg = render_svg(
        ifc_file,
        camera_pos=(2.0, -5.0, 1.0),
        camera_dir=(0.0, -1.0, 0.0),
        use_cross_coplanar=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    # Same X/scale/offset convention as test_cross_coplanar_basic_touching_boundary
    # (shared boundary at world X=2 -> svg x=10000). far_p1/near_p0 are the
    # bisection-refined occlusion-clear boundaries (not the occluder's own
    # hand-placed Z=[0.8,1.2] extent) -- captured empirically from this exact
    # scene, not hand-derived.
    far_p0, far_p1 = (10000.0, 11000.0), (10000.0, 10200.004577636719)
    near_p0, near_p1 = (10000.0, 9799.995422363281), (10000.0, 9000.0)
    assert has_edge(edges, wall_a.GlobalId, "cross-coplanar", far_p0, far_p1)
    assert has_edge(edges, wall_a.GlobalId, "cross-coplanar", near_p0, near_p1)
    assert has_edge(edges, wall_b.GlobalId, "cross-coplanar", far_p0, far_p1)
    assert has_edge(edges, wall_b.GlobalId, "cross-coplanar", near_p0, near_p1)
    # No edge may cross into the genuinely-occluded middle band, and no
    # wrongly-unified single edge may span the whole original extent.
    assert not has_any_edge(edges, wall_a.GlobalId, far_p1, near_p0)
    assert not has_any_edge(edges, wall_a.GlobalId, far_p0, near_p1)
    assert not has_any_edge(edges, wall_b.GlobalId, far_p0, near_p1)


def test_mat_style_change_case_a_material_mismatch():
    """Same touching-wall geometry as the cross-coplanar baseline, but the two
    walls have DIFFERENT materials -- `find_cross_coplanar_matches()` only
    considers a mismatched-material pair at all when mat-style-change
    classification is enabled, and classifies their shared boundary as
    `mat-style-change` rather than `cross-coplanar`.
    """
    ifc_file, body_context, storey = _make_project()
    concrete = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    timber = ifcopenshell.api.material.add_material(ifc_file, name="Timber")
    wall_a = _add_box(
        ifc_file, body_context, storey, "WallA", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0), material=concrete
    )
    wall_b = _add_box(
        ifc_file, body_context, storey, "WallB", (2.0, 0.2, 2.0), (2.0, 0.0, 0.0), material=timber
    )

    svg = render_svg(
        ifc_file,
        camera_pos=(2.0, -5.0, 1.0),
        camera_dir=(0.0, -1.0, 0.0),
        use_cross_coplanar=True,
        use_mat_style_change=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    shared_p0, shared_p1 = (10000.0, 9000.0), (10000.0, 11000.0)
    assert has_edge(edges, wall_a.GlobalId, "mat-style-change", shared_p0, shared_p1)
    assert has_edge(edges, wall_b.GlobalId, "mat-style-change", shared_p0, shared_p1)
    # Must NOT also be classified cross-coplanar (materials genuinely differ).
    assert not has_edge(edges, wall_a.GlobalId, "cross-coplanar", shared_p0, shared_p1)
    assert not has_edge(edges, wall_b.GlobalId, "cross-coplanar", shared_p0, shared_p1)


def test_mat_style_change_case_a_requires_cross_coplanar_too():
    """Case A (cross-product mismatch, see `test_mat_style_change_case_a_material_mismatch`
    above) must NOT fire from `use_mat_style_change` alone -- unlike Case B
    (intra-product layer boundary), which is independent of the cross-coplanar
    flag, Case A reuses cross-coplanar's own cross-product matching pass
    (`find_cross_coplanar_matches()`) and requires `use_cross_coplanar` to
    also be enabled. Confirmed as the user's own intended behaviour, not
    assumed: the full matrix is (coplanar, mat-style) -> (off,off)=neither,
    (off,on)=Case B only, (on,off)=cross-coplanar only, (on,on)=both.

    Same touching, mismatched-material geometry as
    `test_mat_style_change_case_a_material_mismatch`, but with
    `use_cross_coplanar` left at its default `False` -- the shared boundary
    must classify as plain `outline` on both sides (an ordinary silhouette,
    since no cross-product matching ran at all), not `mat-style-change`.
    """
    ifc_file, body_context, storey = _make_project()
    concrete = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    timber = ifcopenshell.api.material.add_material(ifc_file, name="Timber")
    wall_a = _add_box(
        ifc_file, body_context, storey, "WallA", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0), material=concrete
    )
    wall_b = _add_box(
        ifc_file, body_context, storey, "WallB", (2.0, 0.2, 2.0), (2.0, 0.0, 0.0), material=timber
    )

    svg = render_svg(
        ifc_file,
        camera_pos=(2.0, -5.0, 1.0),
        camera_dir=(0.0, -1.0, 0.0),
        use_mat_style_change=True,
    )
    edges = parse_edges(svg)

    shared_p0, shared_p1 = (10000.0, 9000.0), (10000.0, 11000.0)
    assert not has_edge(edges, wall_a.GlobalId, "mat-style-change", shared_p0, shared_p1)
    assert not has_edge(edges, wall_b.GlobalId, "mat-style-change", shared_p0, shared_p1)
    assert has_edge(edges, wall_a.GlobalId, "outline", shared_p0, shared_p1)
    assert has_edge(edges, wall_b.GlobalId, "outline", shared_p0, shared_p1)


def test_mat_style_change_case_a_requires_cross_coplanar_too_when_layered():
    """Same requirement as `test_mat_style_change_case_a_requires_cross_coplanar_too`
    above, but with LAYERED (2+-layer `IfcMaterialLayerSetUsage`) walls rather
    than plain-material ones -- specifically added because the two aren't
    equivalent regression coverage.

    With plain (non-layered) materials, `find_cross_coplanar_matches()`'s own
    per-pair gate (`SvgSerializer.h`, `if (!proj_i && !proj_j) { ...material/
    style null check... }`) happens to reject an unresolved-material pair
    anyway when cross-coplanar is off, since resolving `cross_coplanar_
    material_instance`/`style_instance` at all is *itself* separately gated on
    `svg_use_cross_coplanar_classification_` (`SvgSerializer.cpp`, just above
    `resolve_layer_projection()`) -- so the plain-material test alone doesn't
    distinguish a correctly-narrowed entry gate from an accidental side effect
    of that unrelated gate.

    Confirmed directly: applying ONLY the Case B fix (widening
    `resolve_layer_projection()`'s gate at `SvgSerializer.cpp:846`) without
    ALSO narrowing `find_cross_coplanar_matches()`'s entry gate back to
    requiring cross-coplanar causes THIS exact layered scenario to newly
    regress -- `proj_i`/`proj_j` populate (bypassing the `!proj_i && !proj_j`
    material-null gate entirely, since layer materials resolve from the
    projection itself, not from the gated `cross_coplanar_material_instance`),
    letting Case A wrongly fire with coplanar off. Both fixes are needed
    together; this test is what proves it.
    """
    ifc_file, body_context, storey = _make_project()
    concrete = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    timber = ifcopenshell.api.material.add_material(ifc_file, name="Timber")
    insulation = ifcopenshell.api.material.add_material(ifc_file, name="Insulation")
    wall_a = _add_box(ifc_file, body_context, storey, "WallA", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0))
    wall_b = _add_box(ifc_file, body_context, storey, "WallB", (2.0, 0.2, 2.0), (2.0, 0.0, 0.0))
    for wall, top_material in ((wall_a, concrete), (wall_b, timber)):
        layer_set = ifcopenshell.api.material.add_material_set(ifc_file, set_type="IfcMaterialLayerSet")
        layer1 = ifcopenshell.api.material.add_layer(ifc_file, layer_set=layer_set, material=top_material)
        ifcopenshell.api.material.edit_layer(ifc_file, layer=layer1, attributes={"LayerThickness": 0.15})
        layer2 = ifcopenshell.api.material.add_layer(ifc_file, layer_set=layer_set, material=insulation)
        ifcopenshell.api.material.edit_layer(ifc_file, layer=layer2, attributes={"LayerThickness": 0.05})
        ifcopenshell.api.material.assign_material(
            ifc_file, products=[wall], type="IfcMaterialLayerSetUsage", material=layer_set
        )

    svg = render_svg(
        ifc_file,
        camera_pos=(2.0, -5.0, 1.0),
        camera_dir=(0.0, -1.0, 0.0),
        use_mat_style_change=True,
    )
    edges = parse_edges(svg)

    shared_p0, shared_p1 = (10000.0, 9000.0), (10000.0, 11000.0)
    assert not has_edge(edges, wall_a.GlobalId, "mat-style-change", shared_p0, shared_p1)
    assert not has_edge(edges, wall_b.GlobalId, "mat-style-change", shared_p0, shared_p1)


def test_cluster_a_exact_match_dedup_outline_beats_sharp():
    """Cluster A (`a08873af07`): when two DIFFERENT products produce an edge at
    the exact same 3D location but with different class priorities, only the
    best-priority class should survive -- previously this was
    non-deterministic paint order (whichever product's SVG group happened to
    be written later simply painted over the other), not a correctness
    decision.

    Not hand-designed -- an earlier attempt at this scenario (a 3rd wall
    offset in Y to land its silhouette at the same *2D-projected* location as
    a touching pair's boundary) turned out to just be genuine HLR 3D
    occlusion, not a coincident-duplicate-edge case at all (see git history
    of this function/module for that dead end). The real trigger only
    reproduced once identified in the actual primary test fixture: two walls
    (GUIDs `3Dt1Chn$DDgxkP6LNUvmEB`/`21z$tr7Hj9YRCib0bGUX1_`) meeting at an
    angled corner, each rotated by a different amount -- their shared vertical
    corner edge is the exact same physical line in 3D, but each wall's own
    independent `classify_edge_from_faces()` disagrees on what it is: one
    sees a true silhouette (`outline`), the other `sharp`. This test's
    profile points, extrusion depth, and placement (location/axis/
    ref-direction, verbatim, in the original file's own FEET project units)
    are copied exactly from that real fixture -- not a real project *file*
    (no `.ifc` is read here or committed anywhere), just its bare numeric
    geometry, reconstructed via low-level entity creation, matching the same
    recipe as `test_cluster_b_depth_tie_restoration`.

    Verified two ways before being written as an assertion:
    - Rendering this exact synthetic geometry byte-for-byte reproduces the
      real fixture's own extracted-pair SVG output (12 outline + 5 sharp
      edges, identical coordinates).
    - Reverting both `compute_coincident_edge_best_priority()` and
      `compute_coincident_edge_overlap_coverage()` (commenting out their
      calls in `SvgSerializer.cpp`) raises the sharp count from 5 to 7 --
      WallB's `sharp` duplicate at WallA's `outline` location wrongly
      reappears -- confirming this test would actually have caught the
      original bug.

    Builds its own project (not the shared `_make_project()` helper) since
    the extracted geometry's literal numbers are in FEET, matching the real
    fixture's own project units -- `_make_project()` uses METERS, which
    silently produced a completely different (and non-reproducing) geometry
    the first time this test was written, caught by the target edge simply
    being absent (wrong coordinates, not a real failure of the fix).
    """
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
    ifcopenshell.api.unit.assign_unit(ifc_file, length={"is_metric": False, "raw": "FEET"})
    context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")
    body_context = ifcopenshell.api.context.add_context(
        ifc_file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey", name="Storey")
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=ifc_file.by_type("IfcProject")[0], products=[site])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=site, products=[building])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=building, products=[storey])

    profile = [
        (0.0, 0.0),
        (0.0, 1.000000029802323),
        (1.6404194043377256, 1.000000029802323),
        (1.6404194043377256, 0.0),
    ]
    depth = 2.0000000247179366
    axis = (0.0, 0.0, 1.0)

    wall_a = _add_arbitrary_profile_slab(
        ifc_file, body_context, storey, "WallA",
        points_2d=profile,
        depth=depth,
        location=(-34.15430311768699, 0.3383361692894788, 11.32700152284517),
        axis=axis,
        ref_direction=(0.9663057411039859, -0.2573969982526535, 0.0),
        ifc_class="IfcWall",
    )
    wall_b = _add_arbitrary_profile_slab(
        ifc_file, body_context, storey, "WallB",
        points_2d=profile,
        depth=depth,
        location=(-35.74319711820347, -0.06958368060782825, 11.32700152284517),
        axis=axis,
        ref_direction=(0.9685886719581167, 0.2486684229137502, 0.0),
        ifc_class="IfcWall",
    )

    # Camera matches the real fixture's own ORTHOGRAPHIC drawing.
    svg = render_svg(
        ifc_file,
        camera_pos=(-4.301992893218994, -4.959714889526367, 6.503134250640869),
        camera_dir=(0.5899107456207275, -0.7030283808708191, 0.39718562364578247),
        camera_ref=(0.7660444974899292, 0.6427875757217407, -7.652545264136279e-10),
        scale=31.25 / 1000.0,
        use_cross_coplanar=True,
        use_mat_style_change=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    target_p0 = (9998.6578298785953, 10009.248959683862)
    target_p1 = (9998.6578300775, 9991.7660449053692)
    assert has_edge(edges, wall_a.GlobalId, "outline", target_p0, target_p1)
    # WallB's own independently-classified `sharp` duplicate at this exact
    # location must be gone entirely, not just painted under the outline.
    assert not has_any_edge(edges, wall_b.GlobalId, target_p0, target_p1)


def test_cluster_b_depth_tie_restoration():
    """Cluster B (`0078c94872`): `restore_coincident_hidden_edges()` restores a
    single-object edge that HLR hid due to an exact view-depth tie with a
    foreign product's coincident face.

    This geometry is not hand-designed: two hand-built attempts at this
    scenario (a flat slab+box, then a sloped slab+box) both failed to actually
    reproduce the depth-tie -- HLR simply resolved them as ordinary, correctly
    visible edges. The real trigger only reproduced when extracted from a
    genuine bug report fixture (two sloped `IfcRoof` slabs, GUIDs
    `2CH9svq8r2gfCQ$eEjlBKa`/`2u$gvViprDheArJeaHzt$M`). This test's profile
    points, extrusion depths and placement (location/axis/ref-direction,
    verbatim, in the original file's own FEET project units) are copied
    exactly from that real extraction -- not a real project *file* (no `.ifc`
    is read here or committed anywhere), just its bare numeric geometry,
    reconstructed via low-level entity creation.

    Verified two ways before being written as an assertion:
    - Rendering this exact synthetic geometry byte-for-byte reproduces the
      real extraction's own SVG output (17 paths, same coordinates, same
      classes, including a same-product duplicate outline edge).
    - Reverting `restore_coincident_hidden_edges()` (commenting out its call
      in `SvgSerializer.h`) drops the output from 14 to 12 outline edges,
      missing exactly the target edge asserted below plus one copy of the
      duplicate -- confirming this test would actually have caught the
      original bug, not just that it passes against current code.

    No material/style is assigned to either product (matching the real
    fixture) -- this restoration pass is independent of the cross-coplanar
    material/style gate.
    """
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
    ifcopenshell.api.unit.assign_unit(ifc_file, length={"is_metric": False, "raw": "FEET"})
    context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")
    body_context = ifcopenshell.api.context.add_context(
        ifc_file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey", name="Storey")
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=ifc_file.by_type("IfcProject")[0], products=[site])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=site, products=[building])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=building, products=[storey])

    # Both slabs share the same sloped-roof-plane orientation -- that shared
    # normal is what puts their coincident faces at an exact HLR depth tie.
    axis = (0.0, -0.24259928227576613, 0.9701265836164285)
    ref_direction = (1.0, 0.0, 0.0)

    slab_a = _add_arbitrary_profile_slab(
        ifc_file, body_context, storey, "SlabA",
        points_2d=[
            (-4.08607816696167, 2.661661148071289),
            (-4.08607816696167, 1.2422367334365845),
            (-2.0000345706939697, 1.2422367334365845),
            (-2.0000345706939697, 2.661661148071289),
            (-4.08607816696167, 2.661661148071289),
        ],
        depth=0.0644245835111433,
        location=(-44.95270296031721, 2.998521165272069, 14.503785944360446),
        axis=axis,
        ref_direction=ref_direction,
    )
    _add_arbitrary_profile_slab(
        ifc_file, body_context, storey, "SlabB",
        points_2d=[
            (4.086053371429443, -1.0950984687951859e-05),
            (2.086031198501587, -1.0950984687951859e-05),
            (2.086031198501587, -1.4194228649139404),
            (-1.2515411071944982e-05, -1.419427514076233),
            (-1.2515411071944982e-05, -2.6616580486297607),
            (4.086053371429443, -2.6616580486297607),
            (4.086053371429443, -1.0950984687951859e-05),
        ],
        depth=0.128849165102285,
        location=(-49.038768753292054, 5.596308257636123, 15.087005660289854),
        axis=axis,
        ref_direction=ref_direction,
    )

    # Camera matches the real fixture's own SOUTH SECTION drawing (a section,
    # not an elevation, so intentionally sits between the two slabs in Y --
    # unlike this file's other elevation-view tests, that's correct here).
    svg = render_svg(
        ifc_file,
        camera_pos=(0.0, 3.296240, 0.0),
        camera_dir=(0.0, 1.0, 0.0),
        camera_ref=(-1.0, 0.0, 0.0),
        scale=31.25 / 1000.0,
    )
    edges = parse_edges(svg)

    target_p0, target_p1 = (10019.459887439012, 10000.204735060386), (9999.590322184562, 10000.204735060386)
    assert has_edge(edges, slab_a.GlobalId, "outline", target_p0, target_p1)


def test_restore_coincident_hidden_edges_partial_occlusion():
    """`restore_coincident_hidden_edges()` (`SvgSerializer.h:1413-1638`)
    restores a single-object edge HLR hid due to a depth-tie with a coincident
    foreign face -- but decides whole-edge-or-nothing from only 3 fixed
    interior sample points (mid/q1@0.25/q3@0.75). When only PART of an edge is
    a genuine depth-tie and the rest is genuinely occluded by a nearer,
    unrelated object, this all-or-nothing decision is wrong either way: if
    none of the 3 fixed samples land in the occluded portion, the WHOLE
    original edge (occluded portion included) is wrongly restored,
    overshooting past where it should be clipped; if ANY of the 3 samples
    lands in the occluded portion, `is_genuinely_occluded()` rejects the
    WHOLE edge, wrongly dropping the genuinely-restorable outer portions too.

    User-reported real examples (a real-project outline edge extending over
    3-4 separate occluding products along its length, and this project's own
    "coplanar join.ifc" synthetic fixture's EAST SECTION drawing) show the first
    (overshoot) failure mode. This test reproduces the second (whole-edge
    drop) failure mode instead, since it's the one that reproduces reliably
    from this suite's own already-proven depth-tie geometry -- both are the
    exact same root cause (a 3-sample whole-edge gate with no sub-interval
    logic), confirmed directly: with a third, deliberately partial occluder
    added to this scene, the target edge (present and correct with no
    occluder, per `test_cluster_b_depth_tie_restoration`) disappears
    entirely, when the correct behaviour is for its two genuinely-unoccluded
    outer thirds to survive and only the genuinely-occluded middle to be
    dropped.

    Base geometry (SlabA/SlabB, camera) is `test_cluster_b_depth_tie_
    restoration`'s own already-proven depth-tie scene, verbatim -- reusing it
    rather than hand-designing a new depth-tie from scratch, since that
    test's own docstring records two prior hand-built attempts failing to
    reproduce a depth-tie at all. A third, small opaque box (`Occluder`) is
    added, positioned (by empirical placement against this exact scene, not
    hand-derived) to block only the middle portion of the target edge's
    world-space extent while leaving both outer thirds genuinely unoccluded.

    Second, related root cause found investigating the overshoot mode
    directly against the real EAST SECTION example above (not reproducible
    via this test's own scene, since it needs a candidate edge that HLR's OWN
    native computation *also* independently makes visible, which this
    2-product scene's target edge -- genuinely, fully HLR-hidden with no
    occluder -- structurally never does): `has_coincident_edge()`/
    `point_covered_by_visible()` (`SvgSerializer.h`) compared a candidate's
    transformed endpoints/samples against `visible_edges` using full 3D
    `Distance()`, but `visible_edges`'s own vertices always carry Z=0 in this
    projected space (HLR's reconstructed 2D screen output, depth already
    resolved and discarded) while a freshly-`projector.Transform()`-ed
    candidate point retains a real, generally-nonzero depth component --
    so neither check could ever actually match, even for a point genuinely
    coincident on screen. Confirmed via direct debug instrumentation this
    check never fired in practice. Fixed by flattening both sides to the
    screen plane (X, Y) before comparing. Verified directly against the real
    "coplanar join.ifc" EAST SECTION drawing (temporary debug instrumentation,
    fully reverted): `1I9V3NogL069$EyK070JfW`'s outline edges now match the
    `restore_coincident_hidden_edges()`-disabled baseline exactly (the
    genuinely-already-visible native edge stays as-is; the wrongly-restored,
    ~0.39-unit-overshooting duplicate is gone) -- not captured as a synthetic
    test here, per this suite's own established precedent (see
    `test_cluster_b_depth_tie_restoration`'s and item 5's own parked-test
    notes) of not shipping a non-reproducing test for a depth-tie-adjacent
    scenario that resists isolation from its full real-scene context.
    """
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
    ifcopenshell.api.unit.assign_unit(ifc_file, length={"is_metric": False, "raw": "FEET"})
    context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")
    body_context = ifcopenshell.api.context.add_context(
        ifc_file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey", name="Storey")
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=ifc_file.by_type("IfcProject")[0], products=[site])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=site, products=[building])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=building, products=[storey])

    # Verbatim from test_cluster_b_depth_tie_restoration.
    axis = (0.0, -0.24259928227576613, 0.9701265836164285)
    ref_direction = (1.0, 0.0, 0.0)
    slab_a = _add_arbitrary_profile_slab(
        ifc_file, body_context, storey, "SlabA",
        points_2d=[
            (-4.08607816696167, 2.661661148071289),
            (-4.08607816696167, 1.2422367334365845),
            (-2.0000345706939697, 1.2422367334365845),
            (-2.0000345706939697, 2.661661148071289),
            (-4.08607816696167, 2.661661148071289),
        ],
        depth=0.0644245835111433,
        location=(-44.95270296031721, 2.998521165272069, 14.503785944360446),
        axis=axis,
        ref_direction=ref_direction,
    )
    _add_arbitrary_profile_slab(
        ifc_file, body_context, storey, "SlabB",
        points_2d=[
            (4.086053371429443, -1.0950984687951859e-05),
            (2.086031198501587, -1.0950984687951859e-05),
            (2.086031198501587, -1.4194228649139404),
            (-1.2515411071944982e-05, -1.419427514076233),
            (-1.2515411071944982e-05, -2.6616580486297607),
            (4.086053371429443, -2.6616580486297607),
            (4.086053371429443, -1.0950984687951859e-05),
        ],
        depth=0.128849165102285,
        location=(-49.038768753292054, 5.596308257636123, 15.087005660289854),
        axis=axis,
        ref_direction=ref_direction,
    )
    # A small opaque box, positioned (empirically, against this exact scene)
    # to sit in front of (nearer the camera than) only the middle portion of
    # the target edge's world-space extent, leaving both outer thirds
    # genuinely unoccluded and still depth-tied.
    _add_arbitrary_profile_slab(
        ifc_file, body_context, storey, "Occluder",
        points_2d=[(0.0, 0.0), (0.7, 0.0), (0.7, 0.3), (0.0, 0.3), (0.0, 0.0)],
        depth=0.3,
        location=(-48.34, 4.0, 14.8),
        axis=(0.0, 0.0, 1.0),
        ref_direction=(1.0, 0.0, 0.0),
        ifc_class="IfcWall",
    )

    svg = render_svg(
        ifc_file,
        camera_pos=(0.0, 3.296240, 0.0),
        camera_dir=(0.0, 1.0, 0.0),
        camera_ref=(-1.0, 0.0, 0.0),
        scale=31.25 / 1000.0,
    )
    edges = parse_edges(svg)

    # Baseline (test_cluster_b_depth_tie_restoration, no occluder): this
    # exact edge is present in full, from target_p0 to target_p1. With the
    # occluder's middle-third obstruction added, current (unfixed) code drops
    # it ENTIRELY -- neither outer third survives -- because
    # `is_genuinely_occluded()` returns true at at least one of the 3 fixed
    # sample points (which fall inside the occluder's footprint), rejecting
    # the whole restore. The fix must restore the two genuinely-unoccluded
    # outer thirds independently of the genuinely-occluded middle -- each
    # reaching all the way to its own true endpoint (the corner-artifact
    # sampling gate only ever excludes the true endpoints from *occlusion*
    # sampling, never from the restored geometry itself).
    target_p0, target_p1 = (10019.459887439012, 10000.204735060386), (9999.590322184562, 10000.204735060386)

    def has_endpoint_near(guid: str, point: tuple[float, float], tol: float = 1e-3) -> bool:
        def close(a, b):
            return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol

        return any(e.guid == guid and (close(e.p0, point) or close(e.p1, point)) for e in edges)

    # This is the assertion that fails against unfixed code: today, the
    # occluder's mere presence makes the whole edge vanish, so NEITHER true
    # endpoint has any surviving edge touching it at all.
    assert has_endpoint_near(slab_a.GlobalId, target_p0), (
        f"expected a restored sub-edge reaching target_p0={target_p0} (the genuinely "
        f"unoccluded far third); unfixed code drops the whole edge instead"
    )
    assert has_endpoint_near(slab_a.GlobalId, target_p1), (
        f"expected a restored sub-edge reaching target_p1={target_p1} (the genuinely "
        f"unoccluded near third); unfixed code drops the whole edge instead"
    )

    # Exact coordinates below were captured empirically from this exact scene
    # (fixed code), not hand-derived -- same convention as
    # test_mat_style_change_case_b_partial_overlap_splits_correctly. Two
    # separate outline sub-edges, one reaching each true endpoint, with a
    # genuine gap over the occluder's own footprint -- this is what current
    # (unfixed) code structurally cannot produce (it only ever emits the
    # whole edge or nothing, never two disjoint pieces of one original edge).
    # Re-captured after a later fix (issue #3742 follow-up) that bisection-
    # refines each restorable/occluded transition instead of leaving it at
    # the coarse 31-sample bin midpoint -- these two values shifted slightly
    # (by less than one bin width) from that fix, which is expected: it
    # makes the cutoff track the real occluder silhouette more precisely,
    # not a regression in this test's own logic.
    far_third_inner = (10012.803980251783, 10000.204735060386)
    near_third_inner = (10006.136476218988, 10000.204735060386)
    assert has_edge(edges, slab_a.GlobalId, "outline", target_p0, far_third_inner)
    assert has_edge(edges, slab_a.GlobalId, "outline", near_third_inner, target_p1)
    # No edge may cross into the occluded middle band -- neither of the two
    # legitimate sub-edges reaches past its own inner endpoint, and no third,
    # wrongly-unified edge spans the whole original extent.
    assert not has_any_edge(edges, slab_a.GlobalId, target_p0, target_p1)


def test_mat_style_change_case_b_intra_product_layer_boundary():
    """Case B (as opposed to Case A's cross-product mismatch, see the
    `mat_style_change` namespace's own comment in `SvgSerializer.h`): a SINGLE
    product's own `IfcMaterialLayerSetUsage` has 2+ layers, and a face of its
    geometry spans across the layering axis (here, the wall's end-cap face,
    which cuts across the full thickness). There is no pre-existing HLR edge
    at the internal layer boundary at all -- real geometric layer-splitting is
    unimplemented for this kernel -- so `layer_boundary_edges_for_face()`
    constructs brand new line geometry clipped to the face's outline.

    Deliberately independent of cross-coplanar: `use_cross_coplanar` is left
    at its default `False` below. This pins the fix for a P1 known-issue
    (see [[project_cross_coplanar_known_issues]]): `SvgSerializer.cpp`'s
    `write()` used to only call `resolve_layer_projection()` -- which this
    Case relies on -- when `svg_use_cross_coplanar_classification_` was also
    true, so `use_mat_style_change=True` alone silently did nothing. See
    `test_mat_style_change_case_a_requires_cross_coplanar_too` for Case A's
    opposite requirement (it DOES need cross-coplanar, since it reuses that
    matching pass) -- the two tests together pin the full, corrected matrix.
    """
    ifc_file, body_context, storey = _make_project()
    wall = _add_box(ifc_file, body_context, storey, "Wall", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0))

    concrete = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    insulation = ifcopenshell.api.material.add_material(ifc_file, name="Insulation")
    layer_set = ifcopenshell.api.material.add_material_set(ifc_file, name="WallBuildUp", set_type="IfcMaterialLayerSet")
    layer1 = ifcopenshell.api.material.add_layer(ifc_file, layer_set=layer_set, material=concrete)
    ifcopenshell.api.material.edit_layer(ifc_file, layer=layer1, attributes={"LayerThickness": 0.15})
    layer2 = ifcopenshell.api.material.add_layer(ifc_file, layer_set=layer_set, material=insulation)
    ifcopenshell.api.material.edit_layer(ifc_file, layer=layer2, attributes={"LayerThickness": 0.05})
    # IfcWall isn't in SvgSerializer.cpp's AXIS3_CLASSES list, so this resolves
    # to LayerSetDirection AXIS2 -- the local Y axis, matching `_add_box`'s own
    # size=(x, y, z) convention where y is the wall's thickness.
    ifcopenshell.api.material.assign_material(
        ifc_file, products=[wall], type="IfcMaterialLayerSetUsage", material=layer_set
    )

    # A view straight down the wall's own length (world-X), so the end-cap
    # face (spanning the full Y thickness) faces the camera directly -- unlike
    # this file's other tests, which all view along Y.
    svg = render_svg(
        ifc_file,
        camera_pos=(5.0, 0.1, 1.0),
        camera_dir=(1.0, 0.0, 0.0),
        camera_ref=(0.0, 1.0, 0.0),
        use_mat_style_change=True,
    )
    edges = parse_edges(svg)

    # Visible plane is world-Y (thickness, horizontal) / world-Z (height,
    # vertical); offset/scale as in the cross-coplanar tests. The boundary
    # sits at Y=0.15 (end of the 0.15m Concrete layer, start of Insulation).
    boundary_p0, boundary_p1 = (10050.005, 9000.0), (10050.005, 11000.0)
    assert has_edge(edges, wall.GlobalId, "mat-style-change", boundary_p0, boundary_p1)
    # The wall's real outer silhouette at Y=0/Y=0.2 must remain plain outline.
    assert has_edge(edges, wall.GlobalId, "outline", (9900.0, 9000.0), (9900.0, 11000.0))
    assert has_edge(edges, wall.GlobalId, "outline", (10100.0, 9000.0), (10100.0, 11000.0))


@pytest.mark.skip(
    reason=(
        "Not yet a valid repro, same trap as test_cluster_a_exact_match_dedup_...: WallC sits "
        "nearer the camera (Y:[-0.05, 0]) than A/B's shared boundary (Y=0), so its own SOLID "
        "geometry genuinely occludes that screen region -- confirmed by disabling both "
        "compute_coincident_edge_best_priority() and compute_coincident_edge_overlap_coverage() "
        "in SvgSerializer.cpp entirely and rebuilding: the output was byte-for-byte IDENTICAL, "
        "proving this scenario's apparently-correct trimmed result comes from ordinary HLR "
        "occlusion, not the dedup pass this test claims to exercise. A genuine collinear-overlap "
        "case needs two products' OWN independently-classified edges (not a cross-coplanar match) "
        "to differ in classification while occupying the exact same 3D line with neither's solid "
        "geometry occluding the other -- e.g. a genuine face-angle difference between two touching "
        "products' adjacent geometry, not a third object placed in front. Needs a better geometry "
        "design. Also searched the primary fixture's ORTHOGRAPHIC/ORTHOGRAPHIC-X/EAST SECTION/"
        "NORTH SECTION TILT drawings directly (2026-07-30) for a genuinely NESTED (different-"
        "length, partial-overlap) differing-class real-world case, the specific pattern this "
        "second mechanism (as opposed to exact-match) targets -- every candidate found either fell "
        "outside the real ~1e-4 project-unit tolerance (a first, too-loose search bucket falsely "
        "matched unrelated edges) or, once the search was tightened to the real tolerance, turned "
        "out to have identical endpoints (an exact-match case already, not a distinctly nested "
        "one). Parked per explicit user instruction: if this can't be isolated before the PR, drop "
        "this placeholder rather than ship a fake/empty test."
    )
)
def test_cluster_a_collinear_overlap_dedup():
    """Cluster A (`a08873af07`)'s SECOND detection mechanism -- collinear-overlap,
    as opposed to `test_cluster_a_exact_match_dedup_...`'s (skipped) exact-match
    case. Catches a duplicate exact-match bucketing misses: one product's SHORT
    edge fully nested inside another product's collinear, LONGER edge, sharing
    at most one endpoint, genuinely coincident in full 3D (not merely
    same-2D-projection, which the exact-match test's own postmortem found
    isn't a valid repro at all -- see that test's skip reason).

    WallA/WallB (height 2.0, SAME material) touch at X=2, producing a
    `cross-coplanar` edge over their full shared boundary. WallC is a SHORT
    (height 1.0), DIFFERENT-material pilaster flush against that same X=2
    plane, sitting slightly nearer the camera (Y:[-0.05, 0]) -- intended to
    never be occluded, but see the skip reason: it actually DOES occlude the
    boundary it was meant to merely coincide with.
    """
    ifc_file, body_context, storey = _make_project()
    material = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    other = ifcopenshell.api.material.add_material(ifc_file, name="Timber")
    wall_a = _add_box(ifc_file, body_context, storey, "WallA", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0), material=material)
    wall_b = _add_box(ifc_file, body_context, storey, "WallB", (2.0, 0.2, 2.0), (2.0, 0.0, 0.0), material=material)
    wall_c = _add_box(ifc_file, body_context, storey, "WallC", (0.2, 0.05, 1.0), (2.0, -0.05, 0.0), material=other)

    svg = render_svg(
        ifc_file,
        camera_pos=(2.0, -5.0, 1.0),
        camera_dir=(0.0, -1.0, 0.0),
        use_cross_coplanar=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    # Only the non-overlapping (upper) half of the shared boundary survives as
    # cross-coplanar -- the lower half, coincident with WallC, must be gone
    # entirely (not just repainted; genuinely absent from both sides' output).
    surviving_p0, surviving_p1 = (10000.0, 9000.0), (10000.0, 10000.0)
    trimmed_p0, trimmed_p1 = (10000.0, 10000.0), (10000.0, 11000.0)
    assert has_edge(edges, wall_a.GlobalId, "cross-coplanar", surviving_p0, surviving_p1)
    assert has_edge(edges, wall_b.GlobalId, "cross-coplanar", surviving_p0, surviving_p1)
    assert not has_any_edge(edges, wall_a.GlobalId, trimmed_p0, trimmed_p1)
    assert not has_any_edge(edges, wall_b.GlobalId, trimmed_p0, trimmed_p1)

    # WallB's own outer edge is trimmed too, wherever WallC's footprint
    # coincides with it (WallC's own outline wins there instead).
    assert not has_any_edge(edges, wall_b.GlobalId, (10000.0, 11000.0), (10200.0, 11000.0))
    assert has_edge(edges, wall_b.GlobalId, "outline", (10200.0, 11000.0), (12000.0, 11000.0))

    # WallC's own genuine silhouette is untouched.
    assert has_edge(edges, wall_c.GlobalId, "outline", (10000.0, 10000.0), (10200.0, 10000.0))
    assert has_edge(edges, wall_c.GlobalId, "outline", (10000.0, 11000.0), (10200.0, 11000.0))


def test_cluster_b_self_occlusion_must_not_restore():
    """Cluster B regression guard: `is_genuinely_occluded()`'s ray-cast
    deliberately includes the edge's OWN product (not just foreign products)
    -- an object's own back-facing edge, truly hidden by its own nearer
    geometry, must stay hidden even when it also happens to sit on a
    coincident foreign face (satisfying `point_on_foreign_face()`'s gate).
    Only a genuine depth-tie (nothing nearer at all, including the product's
    own geometry) should ever be restored.

    BoxA is a solid cube; its BACK face (Y=2, far from the camera) is
    genuinely occluded by its own FRONT face (Y=0) -- not a depth-tie at all,
    ordinary self-occlusion. SlabD sits exactly at Y=2, coincident with BoxA's
    own back face, so a foreign face genuinely exists there too. Confirmed via
    a direct before/after check (forcing `is_genuinely_occluded()` to always
    return `false`, i.e. simulating the self-occlusion check never having
    existed): BoxA then shows 8 outline edges (the back face wrongly
    restored, duplicating all 4 front-face edges) instead of the correct 4 --
    this test would have caught that regression.
    """
    ifc_file, body_context, storey = _make_project()
    box_a = _add_box(ifc_file, body_context, storey, "BoxA", (2.0, 2.0, 2.0), (0.0, 0.0, 0.0))
    _add_box(ifc_file, body_context, storey, "SlabD", (2.0, 0.1, 2.0), (0.0, 2.0, 0.0))

    svg = render_svg(ifc_file, camera_pos=(1.0, -5.0, 1.0), camera_dir=(0.0, -1.0, 0.0))
    edges = parse_edges(svg)

    box_a_edges = [e for e in edges if e.guid == box_a.GlobalId]
    assert len(box_a_edges) == 4, f"expected only BoxA's 4 front-face edges, found {box_a_edges}"
    assert all(e.cls == "outline" for e in box_a_edges)


def test_full_duplicate_pair_silhouette_stays_outline():
    """Regression guard for `03865b02fe`: two exactly-overlapping duplicate
    products (identical footprint and placement, differing only in material)
    must keep their true outer silhouette as plain `outline`, not wrongly
    `mat-style-change`. The A2/B2 coplanarity gate that
    `find_cross_coplanar_matches()` normally relies on is a one-hop check --
    correct for a genuine partial touch, but a full duplicate has every face
    matching, including whatever's beyond any given edge, so that gate
    trivially passes even at edges that are the shape's true silhouette with
    nothing beyond them at all. Fixed via a bounding-box-equality pre-check
    that skips the whole face-pair loop for an exact-duplicate pair.

    Not verified against a pre-fix build for this one: temporarily disabling
    the bounding-box-equality skip (to confirm the old, buggy behaviour)
    produced completely empty SVG output instead of the documented wrong
    classification -- true full-volume duplicate geometry going through the
    disabled code path seems to hit a different, more degenerate case than
    the original bug report, not a faithful pre-fix reproduction. The
    assertion below is still a correct, meaningful regression guard for the
    documented behaviour either way.
    """
    ifc_file, body_context, storey = _make_project()
    concrete = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
    timber = ifcopenshell.api.material.add_material(ifc_file, name="Timber")
    wall_a = _add_box(ifc_file, body_context, storey, "WallA", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0), material=concrete)
    wall_dup = _add_box(ifc_file, body_context, storey, "WallDup", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0), material=timber)

    svg = render_svg(
        ifc_file,
        camera_pos=(1.0, -5.0, 1.0),
        camera_dir=(0.0, -1.0, 0.0),
        use_cross_coplanar=True,
        use_mat_style_change=True,
        render_cross_coplanar=True,
    )
    edges = parse_edges(svg)

    for product in (wall_a, wall_dup):
        product_edges = [e for e in edges if e.guid == product.GlobalId]
        assert len(product_edges) == 4, f"expected 4 silhouette edges for {product.Name}, found {product_edges}"
        assert all(e.cls == "outline" for e in product_edges), product_edges


@pytest.mark.skip(
    reason=(
        "Investigated but not yet reproducible standalone. Cluster B's third guard (0078c94872, "
        "'remaining false-positive class'): real GUIDs identified in the primary fixture's NORTH "
        "SECTION TILT drawing (143K2G_eT8tvByq93EgoU$ / 2jifPdGkTAYg1VkqWF2gAd, a straight two-"
        "segment wall run) via debug instrumentation confirming an edge-on match "
        "(face normal (-1,~0,0), dot~1.6e-7) is genuinely found and rejected in the FULL fixture "
        "at this exact query point. But extracting just these two products (via dst.add(), then "
        "separately re-verified via full hand-reconstruction from literal profile/placement data -- "
        "the same recipe that worked cleanly for both test_cluster_b_depth_tie_restoration and "
        "test_cluster_a_exact_match_dedup_outline_beats_sharp) does NOT reproduce it: the exact "
        "same query point instead matches a DIFFERENT, non-edge-on face first (the neighbour "
        "wall's own top face, normal (0,0,1), dot=0.397 -- a valid, unrejected match), so the edge "
        "restores via that path regardless of the edge-on gate. point_on_foreign_face() returns on "
        "the FIRST matching face found while iterating TopExp_Explorer -- which face is 'first' for "
        "a given query point is apparently sensitive to full-scene context (more surrounding "
        "geometry, more total topology) in a way isolating 2-3 objects doesn't preserve, unlike the "
        "other two scenarios above where isolation reproduced the bug byte-for-byte. Tried widening "
        "the extraction to 3 and then 16 nearby real products (walls, slabs, beams) from the "
        "original fixture -- neither reproduced it either. Root cause of the face-ordering "
        "sensitivity itself not identified. Parked per explicit user instruction (2026-07-30) after "
        "this investigation, same as test_cluster_a_collinear_overlap_dedup above -- if this can't "
        "be isolated before the PR, drop this placeholder rather than ship a fake/empty test."
    )
)
def test_cluster_b_edge_on_face_must_not_restore():
    """Placeholder for Cluster B's edge-on rejection guard -- see the skip
    reason for why this isn't constructed yet, and what's already been tried."""
    pass


def test_back_facing_convex_edge_on_closed_solid_stays_sharp():
    """P1-2 (known-issues backlog): `classify_edge_from_faces()`'s "view-relative
    flip for folds seen from behind through an opening" (`SvgSerializer.cpp`,
    the `if (back0 && back1)` block) wrongly reinterprets ANY back-facing
    convex fold as `crease`, with no check for whether the product actually
    HAS an opening at all -- found via a real user-reported bug on a genuine
    project file's window (flush-mounted, no recess -- confirmed with the
    user there is no plausible "seen through an opening" story for it).

    Not hand-designed -- two earlier attempts at a minimal synthetic
    reproduction (a chunky L-shaped extrusion at several camera angles) each
    genuinely reproduced the wrong classification at the pre-HLR
    `classify_edge_from_faces()` level, but the specific wrongly-classified
    edges never survived to the final HLR-visible output at any camera angle
    tried -- a plain L-shape's own bulk kept fully occluding them. The real
    trigger only reproduced once rebuilt from the real window's actual
    geometry (GUID `2NvX7VpZfB48hD$vRvyHVz`): 8 separate, genuinely thin
    (10-40mm deep) `IfcExtrudedAreaSolid` frame members with notched,
    non-convex profiles -- thinness plus non-convexity together are what let
    HLR legitimately keep some back-facing convex corners visible, unlike a
    single chunky solid. This test's profile points, depths, local positions,
    and the window's own resolved world placement matrix (via
    `ifcopenshell.util.placement.get_local_placement()`, verbatim, in the
    original file's own millimetre project units) are copied exactly from
    that real geometry -- not a real project *file* (no `.ifc` is read here
    or committed anywhere), just its bare numeric geometry, reconstructed via
    low-level entity creation, matching the same recipe as
    `test_cluster_b_depth_tie_restoration`.

    Verified via the real Bonsai/Blender `bpy.ops.bim.create_drawing()`
    pipeline (not just this module's own direct-serializer harness) before
    writing this assertion: with the fix, 9 of the product's edges that
    would have wrongly flipped to `crease` now correctly read `sharp`
    (`product_has_naked_edge` confirmed `False` for this product, matching
    the real window), and the final rendered elevation shows zero `crease`
    edges at all -- matching the real bug's own before/after.
    """
    ifc_file, body_context, storey = _make_project()
    ifcopenshell.api.unit.assign_unit(ifc_file, length={"is_metric": True, "raw": "MILLIMETERS"})

    items_data = [
        dict(points=[(1200.0, 1080.0), (1200.0, 0.0), (0.0, 0.0), (0.0, 1080.0), (25.0, 1080.0), (25.0, 25.0), (1175.0, 25.0), (1175.0, 1080.0)], position=(0.0, 90.0, 0.0), depth=9.99999523162842),
        dict(points=[(0.0, 0.0), (1200.0, 0.0), (1200.0, 1080.0), (0.0, 1080.0)], position=(0.0, 50.0, 0.0), depth=40.0000038146973),
        dict(points=[(0.0, 0.0), (1150.0, 0.0), (1150.0, 1055.0), (0.0, 1055.0)], position=(25.0, 90.0, 25.0), depth=34.9999961853027),
        dict(points=[(34.9999961853027, 34.9999961853027), (1115.0, 34.9999961853027), (1115.0, 1020.0), (34.9999961853027, 1020.0)], position=(25.0, 102.5, 25.0), depth=10.0),
        dict(points=[(0.0, 0.0), (0.0, 320.000061035156), (1200.0, 320.000061035156), (1200.0, 0.0), (1175.0, 0.0), (1175.0, 295.000061035156), (25.0, 295.000061035156), (25.0, 0.0)], position=(0.0, 90.0, 1080.0), depth=9.99999523162842),
        dict(points=[(0.0, 0.0), (1200.0, 0.0), (1200.0, 320.000061035156), (0.0, 320.000061035156)], position=(0.0, 50.0, 1080.0), depth=40.0000038146973),
        dict(points=[(0.0, 0.0), (1150.0, 0.0), (1150.0, 295.000061035156), (0.0, 295.000061035156)], position=(25.0, 90.0, 1080.0), depth=34.9999961853027),
        dict(points=[(34.9999961853027, 34.9999961853027), (1115.0, 34.9999961853027), (1115.0, 260.000061035156), (34.9999961853027, 260.000061035156)], position=(25.0, 102.5, 1080.0), depth=10.0),
    ]
    # Resolved world-space placement (get_local_placement(), collapsing the
    # real product's multi-level placement chain -- and its identity
    # mapped-item transform -- into one matrix): a 45-degree plan rotation
    # plus translation, in the project's own millimetre units.
    world_matrix = np.array([
        [0.7071067812, -0.7071067812, 0.0, 5742.3152923584],
        [0.7071067812, 0.7071067812, 0.0, -2819.2496299744],
        [0.0, 0.0, 1.0, 400.0000059605],
        [0.0, 0.0, 0.0, 1.0],
    ])

    window = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWindow", name="Window")
    ifcopenshell.api.spatial.assign_container(ifc_file, relating_structure=storey, products=[window])
    solids = []
    for item in items_data:
        point_list = ifc_file.createIfcCartesianPointList2D(item["points"])
        poly_curve = ifc_file.createIfcIndexedPolyCurve(point_list, None, None)
        profile = ifc_file.createIfcArbitraryClosedProfileDef("AREA", None, poly_curve)
        position = ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint(item["position"]),
            ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
            ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
        )
        direction = ifc_file.createIfcDirection((0.0, 0.0, -1.0))
        solids.append(ifc_file.createIfcExtrudedAreaSolid(profile, position, direction, item["depth"]))
    shape_rep = ifc_file.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", solids)
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=window, representation=shape_rep)
    # world_matrix's numbers are already in the project's own millimetre
    # units, not SI metres -- is_si=False so edit_object_placement doesn't
    # apply its default metre-to-project-unit conversion.
    ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=window, matrix=world_matrix, is_si=False)

    # Camera matches the real window's own EAST ELEVATION drawing (extracted
    # via bpy camera.matrix_world against this exact synthetic geometry).
    svg = render_svg(
        ifc_file,
        camera_pos=(16.0, -2.799999952316284, 0.8999999761581421),
        camera_dir=(1.0, 0.0, 0.0),
        camera_ref=(0.0, 1.0, 0.0),
    )
    edges = parse_edges(svg)

    window_edges = [e for e in edges if e.guid == window.GlobalId]
    assert window_edges, "expected the window to produce some visible edges"
    assert not any(e.cls == "crease" for e in window_edges), window_edges
    target_p0, target_p1 = (10028.284271247461, 9439.9999980926514), (10028.284271247461, 9480.0000019073486)
    assert has_edge(edges, window.GlobalId, "sharp", target_p0, target_p1)


def test_back_facing_fold_seen_through_genuine_opening_still_flips():
    """Regression guard for the fix above: the `back0 && back1` view-relative
    flip must still fire when the product genuinely HAS an opening -- the
    "Rotated Box w/Boundary" scenario the flip was originally built for (a
    box with a face actually removed, so its own naked/boundary edges ring
    the missing face). Narrowing the flip to require
    `product_has_naked_edge` must not disable it here, only for products
    (like the one above) that don't have any opening at all.

    Built as a genuinely open `IfcOpenShell`/`IfcShellBasedSurfaceModel` (5
    faces of a unit cube, top face omitted entirely -- not a closed solid
    with a boolean void, an actually-incomplete shell), so the rim around the
    missing top is a real naked-edge loop, confirmed present in the render as
    `boundary`-class edges. Viewed from a diagonal angle, one of the box's
    own outer vertical edges is genuinely concave pre-flip (`convex=0`,
    `deviation_deg=-90`, i.e. would show `crease`) and gets flipped to
    `sharp` by the `back0 && back1` block -- confirmed via direct debug
    trace before writing this assertion.
    """
    ifc_file, body_context, storey = _make_project()
    pts = {}
    for x in (0.0, 1.0):
        for y in (0.0, 1.0):
            for z in (0.0, 1.0):
                pts[(x, y, z)] = ifc_file.createIfcCartesianPoint((x, y, z))

    def face(*coords):
        poly = ifc_file.createIfcPolyLoop([pts[c] for c in coords])
        bound = ifc_file.createIfcFaceOuterBound(poly, True)
        return ifc_file.createIfcFace([bound])

    faces = [
        face((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)),  # bottom
        face((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)),
        face((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)),
        face((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)),
        face((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
        # top (Z=1) deliberately omitted -- a genuine opening, not a closed solid.
    ]
    shell = ifc_file.createIfcOpenShell(faces)
    ssm = ifc_file.createIfcShellBasedSurfaceModel([shell])

    open_box = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="OpenBox")
    ifcopenshell.api.spatial.assign_container(ifc_file, relating_structure=storey, products=[open_box])
    shape_rep = ifc_file.createIfcShapeRepresentation(body_context, "Body", "SurfaceModel", [ssm])
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=open_box, representation=shape_rep)
    ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=open_box, matrix=np.eye(4))

    svg = render_svg(
        ifc_file,
        camera_pos=(3.0, 3.0, 3.0),
        camera_dir=(1.0, 1.0, 1.0),
        camera_ref=(1.0, -1.0, 0.0),
    )
    edges = parse_edges(svg)

    assert any(e.cls == "boundary" for e in edges if e.guid == open_box.GlobalId), "expected a naked-edge rim around the missing top face"
    target_p0, target_p1 = (10000.0, 9183.5034190722745), (10000.0, 10000.0)
    assert has_edge(edges, open_box.GlobalId, "sharp", target_p0, target_p1)


def test_hole_rim_edge_stays_sharp_not_crease():
    """P1-2 (known-issues backlog), second and final root cause. The fix in
    `test_back_facing_convex_edge_on_closed_solid_stays_sharp` above
    (`product_has_naked_edge`) turned out not to be what the user's
    originally-reported edges depended on at all -- confirmed via a fresh
    real-project debug trace: `product_has_naked_edge` was `False` for this
    product (no `back0 && back1` flip ever fired), yet the exact reported
    edges were still `crease`. The user then supplied the real root cause
    from direct inspection: several of the window's 8 frame members are
    extruded from an `IfcArbitraryProfileDefWithVoids` profile -- a genuine
    hole through the member, not a notch -- and it's specifically the hole's
    own rim edges that misclassify.

    This test's geometry corrects TWO mistakes in the earlier (in this same
    session) reconstruction used above: that one (a) silently dropped the
    inner void loops entirely for 4 of the 8 members, turning them into
    solid blocks, and (b) used the wrong `IfcAxis2Placement3D` axis/ref
    (assumed `(0,0,1)`/`(1,0,0)`; the real members use `(0,-1,0)`/`(1,0,0)`).
    Both were wrong enough that the earlier reconstruction produced *zero*
    crease edges from the real drawing's own camera -- it simply didn't
    reproduce the bug at all. This test's `items_data` (outer AND inner loop
    points, axis, ref, depth, direction) and `world_matrix` are read back
    verbatim from the real window (GUID `2NvX7VpZfB48hD$vRvyHVz`) via
    `ifcopenshell.open()` + direct attribute access (`SweptArea.OuterCurve`/
    `InnerCurves`, `Position.Axis`/`RefDirection`) -- not a real project
    *file* (no `.ifc` is read here or committed anywhere), just its bare
    numeric geometry. With this corrected geometry, rendering with the
    user's own saved second camera (`EXISTING EAST ELEVATION-X`, extracted
    via `camera.matrix_world`) reproduces exactly the reported symptom: 4
    `crease` edges at the hole rims where there should be none.

    Root cause: `classify_edge_from_faces()`'s position-based convexity test
    (see `wire_neighbors_of_edge()`'s own comment) picks a "trustworthy
    candidate" vertex by walking further around a face's own boundary wire.
    That only reflects genuine material extent on a face's OUTER wire. Here,
    the shared edge sits on the flat cap face's INNER (hole) wire; the next
    vertex around that same rim lies on the *far side of the empty hole*,
    not on material, so the test's dot product is always positive (wrong)
    regardless of the true 3D fold -- not noise, a structural artifact of
    the hole, so no `|dot|`-based tie-break can fix it. The hole's own inner
    wall face (the other face at this edge) has no such issue -- it has no
    voids of its own, so its wire-neighbor candidate is reliable. Fix: pool
    candidates from BOTH faces (not just f1), each tested against the
    OTHER's normal, and strongly prefer whichever came from an outer wire.

    Verified via the real Bonsai/Blender `bpy.ops.bim.create_drawing()`
    pipeline (not just this module's own direct-serializer harness) against
    the real project file before writing this assertion: with the fix, all
    8 wrongly-`crease` hole-rim edges on this window (from the user's own
    saved camera view) now read `sharp`, at byte-identical coordinates to
    the pre-fix `crease` output, while the 4 genuinely-correct `crease`
    edges elsewhere on the same product (unrelated internal member-to-member
    boundaries, confirmed correct by the user) are untouched.
    """
    ifc_file, body_context, storey = _make_project()
    ifcopenshell.api.unit.assign_unit(ifc_file, length={"is_metric": True, "raw": "MILLIMETERS"})

    # Read back verbatim from the real window (position, axis, ref, depth, direction,
    # outer/inner profile loop points) via ifcopenshell.open() + direct attribute access --
    # see this test's own docstring for why the earlier reconstruction above got this wrong.
    items_data = [
        dict(position=(0.0, 90.0, 0.0), axis=(0.0, -1.0, 0.0), ref=(1.0, 0.0, 0.0), depth=9.99999523162842, direction=(0.0, 0.0, -1.0),
             outer=[(1200.0, 1080.0), (1200.0, 0.0), (0.0, 0.0), (0.0, 1080.0), (25.0, 1080.0), (25.0, 25.0), (1175.0, 25.0), (1175.0, 1080.0)], inner=[]),
        dict(position=(0.0, 50.0, 0.0), axis=(0.0, -1.0, 0.0), ref=(1.0, 0.0, 0.0), depth=40.0000038146973, direction=(0.0, 0.0, -1.0),
             outer=[(0.0, 0.0), (1200.0, 0.0), (1200.0, 1080.0), (0.0, 1080.0)], inner=[[(50.0, 50.0), (1150.0, 50.0), (1150.0, 1055.0), (50.0, 1055.0)]]),
        dict(position=(25.0, 90.0, 25.0), axis=(0.0, -1.0, 0.0), ref=(1.0, 0.0, 0.0), depth=34.9999961853027, direction=(0.0, 0.0, -1.0),
             outer=[(0.0, 0.0), (1150.0, 0.0), (1150.0, 1055.0), (0.0, 1055.0)], inner=[[(34.9999961853027, 34.9999961853027), (1115.0, 34.9999961853027), (1115.0, 1020.0), (34.9999961853027, 1020.0)]]),
        dict(position=(25.0, 102.5, 25.0), axis=(0.0, -1.0, 0.0), ref=(1.0, 0.0, 0.0), depth=10.0, direction=(0.0, 0.0, -1.0),
             outer=[(34.9999961853027, 34.9999961853027), (1115.0, 34.9999961853027), (1115.0, 1020.0), (34.9999961853027, 1020.0)], inner=[]),
        dict(position=(0.0, 90.0, 1080.0), axis=(0.0, -1.0, 0.0), ref=(1.0, 0.0, 0.0), depth=9.99999523162842, direction=(0.0, 0.0, -1.0),
             outer=[(0.0, 0.0), (0.0, 320.000061035156), (1200.0, 320.000061035156), (1200.0, 0.0), (1175.0, 0.0), (1175.0, 295.000061035156), (25.0, 295.000061035156), (25.0, 0.0)], inner=[]),
        dict(position=(0.0, 50.0, 1080.0), axis=(0.0, -1.0, 0.0), ref=(1.0, 0.0, 0.0), depth=40.0000038146973, direction=(0.0, 0.0, -1.0),
             outer=[(0.0, 0.0), (1200.0, 0.0), (1200.0, 320.000061035156), (0.0, 320.000061035156)], inner=[[(50.0, 25.0), (1150.0, 25.0), (1150.0, 270.000061035156), (50.0, 270.000061035156)]]),
        dict(position=(25.0, 90.0, 1080.0), axis=(0.0, -1.0, 0.0), ref=(1.0, 0.0, 0.0), depth=34.9999961853027, direction=(0.0, 0.0, -1.0),
             outer=[(0.0, 0.0), (1150.0, 0.0), (1150.0, 295.000061035156), (0.0, 295.000061035156)], inner=[[(34.9999961853027, 34.9999961853027), (1115.0, 34.9999961853027), (1115.0, 260.000061035156), (34.9999961853027, 260.000061035156)]]),
        dict(position=(25.0, 102.5, 1080.0), axis=(0.0, -1.0, 0.0), ref=(1.0, 0.0, 0.0), depth=10.0, direction=(0.0, 0.0, -1.0),
             outer=[(34.9999961853027, 34.9999961853027), (1115.0, 34.9999961853027), (1115.0, 260.000061035156), (34.9999961853027, 260.000061035156)], inner=[]),
    ]
    # Resolved world-space placement (get_local_placement()), same recipe as the earlier
    # reconstruction above -- this part was already correct, only the per-item axis/ref and
    # inner-loop points needed fixing.
    world_matrix = np.array([
        [0.7071067812, -0.7071067812, 0.0, 5742.3152923584],
        [0.7071067812, 0.7071067812, 0.0, -2819.2496299744],
        [0.0, 0.0, 1.0, 400.0000059605],
        [0.0, 0.0, 0.0, 1.0],
    ])

    window = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWindow", name="Window")
    ifcopenshell.api.spatial.assign_container(ifc_file, relating_structure=storey, products=[window])
    solids = []
    for item in items_data:
        position = ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint(item["position"]),
            ifc_file.createIfcDirection(item["axis"]),
            ifc_file.createIfcDirection(item["ref"]),
        )
        outer_pl = ifc_file.createIfcCartesianPointList2D(item["outer"])
        n_outer = len(item["outer"])
        outer_curve = ifc_file.createIfcIndexedPolyCurve(
            outer_pl, (ifc_file.createIfcLineIndex(tuple(list(range(1, n_outer + 1)) + [1])),), None
        )
        if item["inner"]:
            inner_curves = []
            for inner_pts in item["inner"]:
                inner_pl = ifc_file.createIfcCartesianPointList2D(inner_pts)
                n_inner = len(inner_pts)
                inner_curve = ifc_file.createIfcIndexedPolyCurve(
                    inner_pl, (ifc_file.createIfcLineIndex(tuple(list(range(1, n_inner + 1)) + [1])),), None
                )
                inner_curves.append(inner_curve)
            profile = ifc_file.createIfcArbitraryProfileDefWithVoids("AREA", None, outer_curve, inner_curves)
        else:
            profile = ifc_file.createIfcArbitraryClosedProfileDef("AREA", None, outer_curve)
        direction = ifc_file.createIfcDirection(item["direction"])
        solids.append(ifc_file.createIfcExtrudedAreaSolid(profile, position, direction, item["depth"]))
    shape_rep = ifc_file.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", solids)
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=window, representation=shape_rep)
    ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=window, matrix=world_matrix, is_si=False)

    # Camera matches the real window's own second, more oblique EXISTING EAST
    # ELEVATION-X drawing (extracted via bpy camera.matrix_world against the real
    # project file) -- the straight-on EAST ELEVATION camera used above doesn't put
    # the hole-rim edges at a angle where this specific bug is visible.
    svg = render_svg(
        ifc_file,
        camera_pos=(10.79759693145752, -2.690483808517456, 3.7899999618530273),
        camera_dir=(0.8627297282218933, -0.07547909766435623, 0.5000001192092896),
        camera_ref=(0.08715580403804779, 0.9961947202682495, -4.951073862002886e-08),
    )
    edges = parse_edges(svg)

    window_edges = [e for e in edges if e.guid == window.GlobalId]
    assert window_edges, "expected the window to produce some visible edges"

    def edge_length(e):
        return ((e.p1[0] - e.p0[0]) ** 2 + (e.p1[1] - e.p0[1]) ** 2) ** 0.5

    # From this camera, 4 SHORT `crease` edges are genuine, correct internal
    # member-to-member boundaries (confirmed by the user, unrelated to this bug) --
    # not asserted away here. The bug produced LONG `crease` edges specifically
    # along the hole rims; none of those should remain.
    long_crease_edges = [e for e in window_edges if e.cls == "crease" and edge_length(e) > 50]
    assert not long_crease_edges, long_crease_edges
    target_p0, target_p1 = (9595.977771701151, 9461.301506137414), (10405.254755114664, 9800.83355512243)
    assert has_edge(edges, window.GlobalId, "sharp", target_p0, target_p1)


def _add_layered_wall(
    ifc_file: ifcopenshell.file,
    body_context: ifcopenshell.entity_instance,
    storey: ifcopenshell.entity_instance,
    name: str,
    tag: str,
    size: tuple[float, float, float],
    translation: tuple[float, float, float],
) -> ifcopenshell.entity_instance:
    """A `_add_box` wall with its own 2-layer `IfcMaterialLayerSetUsage`
    (0.15m + 0.05m along local Y, matching `test_mat_style_change_case_b_
    intra_product_layer_boundary`'s own setup) -- `tag` keeps each wall's
    materials distinct so two touching walls never accidentally compare equal.
    """
    wall = _add_box(ifc_file, body_context, storey, name, size, translation)
    concrete = ifcopenshell.api.material.add_material(ifc_file, name=f"Concrete{tag}")
    insulation = ifcopenshell.api.material.add_material(ifc_file, name=f"Insulation{tag}")
    layer_set = ifcopenshell.api.material.add_material_set(ifc_file, name=f"WallBuildUp{tag}", set_type="IfcMaterialLayerSet")
    layer1 = ifcopenshell.api.material.add_layer(ifc_file, layer_set=layer_set, material=concrete)
    ifcopenshell.api.material.edit_layer(ifc_file, layer=layer1, attributes={"LayerThickness": 0.15})
    layer2 = ifcopenshell.api.material.add_layer(ifc_file, layer_set=layer_set, material=insulation)
    ifcopenshell.api.material.edit_layer(ifc_file, layer=layer2, attributes={"LayerThickness": 0.05})
    ifcopenshell.api.material.assign_material(ifc_file, products=[wall], type="IfcMaterialLayerSetUsage", material=layer_set)
    return wall


def _mat_style_change_y_values(edges: list[Edge], guid: str) -> list[float]:
    """Every endpoint Y (SVG-space) of every `mat-style-change` edge owned by
    `guid`, for the "must not enter this Z-band" gap assertions below.
    """
    ys = []
    for e in edges:
        if e.guid == guid and e.cls == "mat-style-change":
            ys.append(e.p0[1])
            ys.append(e.p1[1])
    return ys


def test_mat_style_change_case_b_must_not_fire_on_matched_touching_face():
    """P1 known-issue #4 (see [[project_cross_coplanar_known_issues]]): a
    `mat-style-change` Case B edge appeared where it shouldn't -- on the
    exact shared end-cap face between two products touching end-to-end,
    which is a genuine cross-product touching boundary, not an intra-product
    detail Case B should ever be drawing on.

    Two layered walls (`WallA`/`WallB`, each independently 2-layer) touch
    end-to-end at x=2.0. WallB is deliberately *shorter than WallA and
    vertically centred* (Z:[0.1, 1.9] vs WallA's own Z:[0, 2]) rather than
    exactly matching WallA's height -- this isn't testing a partial overlap
    (that's the sibling test below); it's specifically to avoid a confound
    found while developing this test: with same-height walls, a *tilted*
    camera (needed at all -- see below) also makes WallA's own top/bottom
    faces marginally visible, and their own entirely legitimate, WallB-
    independent Concrete/Insulation boundary line grazes into view right at
    the same shared corner as the bug, landing at nearly identical projected
    coordinates purely because of the simple box geometry -- making a
    same-height design unable to tell "the bug" and "an unrelated, correct
    result" apart by endpoint alone. Keeping WallB's own top/bottom strictly
    away from WallA's Z=0/Z=2 corners (even by a small 0.1m margin) removes
    that confound structurally: WallA's own top/bottom lines only ever touch
    Z=0/Z=2 exactly, nowhere near the matched interior this test targets.

    A slightly *tilted* camera (camera_dir's +Z component just 0.02) is
    needed at all: under an ordinary straight-on camera, WallB's solid
    ordinarily and unambiguously hides WallA's matched end-cap region (confirmed
    separately -- no edges at all for WallA there), so the bug never manifests
    without a depth-tie-inducing tilt of some kind, echoing the real report's
    "NORTH SECTION TILT" drawing. 0.02 was found empirically to be enough to
    expose the touching end cap's own depth-tie sliver.

    `use_cross_coplanar` is deliberately left at its default `False`, same
    rationale as `test_mat_style_change_case_b_intra_product_layer_boundary`:
    Case B must keep working (and must keep NOT over-firing) independently
    of cross-coplanar being on, per the matrix pinned by P1-1's own tests.
    """
    ifc_file, body_context, storey = _make_project()
    wallA = _add_layered_wall(ifc_file, body_context, storey, "WallA", "A", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0))
    wallB = _add_layered_wall(ifc_file, body_context, storey, "WallB", "B", (2.0, 0.2, 1.8), (2.0, 0.0, 0.1))

    svg = render_svg(
        ifc_file,
        camera_pos=(6.0, 0.1, 1.0),
        camera_dir=(1.0, 0.0, 0.02),
        camera_ref=(0.0, 1.0, 0.0),
        use_mat_style_change=True,
    )
    edges = parse_edges(svg)

    # Empirically captured: the SVG-Y range covered by WallB's matched band
    # (Z:[0.1, 1.9]). Nothing must fall strictly inside it.
    gap_lo, gap_hi = 9120.175947217595, 10959.808057580807
    a_ys = _mat_style_change_y_values(edges, wallA.GlobalId)
    assert a_ys, "expected WallA to produce at least some mat-style-change edges (the exposed slivers near Z=0/Z=2)"
    leaked = [y for y in a_ys if gap_lo < y < gap_hi]
    assert not leaked, leaked
    # Sanity: the exposed slivers right at the matched band's own edges are
    # genuinely present -- this isn't vacuously passing because nothing
    # rendered at all.
    assert any(abs(y - gap_lo) < 1e-6 for y in a_ys), a_ys
    assert any(abs(y - gap_hi) < 1e-6 for y in a_ys), a_ys


def test_mat_style_change_case_b_partial_overlap_splits_correctly():
    """The precise reason to fix P1-4 by teaching Case B about real matched
    geometry (rather than a coordinate-based post-hoc dedup pass -- see the
    conversation this fix came from, [[project_cross_coplanar_known_issues]]
    item #4): a real project's touching walls will very often NOT match
    exactly. Here WallB (Z:[0.5, 1.5], vertically centred within WallA's own
    Z:[0, 2] -- see the sibling test's own docstring for why centred rather
    than flush with WallA's own bottom or top) matches only the *middle*
    half of WallA's end cap: the lower quarter (Z:[0, 0.5]) and upper
    quarter (Z:[1.5, 2]) are both genuinely unmatched (Case B MUST still
    draw there) while the middle half is truly covered (Case B must NOT draw
    there, same bug as the sibling test) -- three regions on the exact same
    face. A dedup-after-the-fact approach has no principled way to remove
    just the matched middle third of a single generated edge; this only
    comes out right if Case B itself knows, per sub-range, whether a
    matching neighbour face covers it.

    Same tilted camera as the sibling test, same reasoning for the exact
    tilt magnitude and for keeping WallB away from WallA's own Z=0/Z=2
    corners (see that test's own docstring). Exact coordinates below were
    captured empirically from this exact scene (deterministic: synthetic
    geometry, fixed camera, no tolerance-edge ambiguity) rather than
    hand-derived, matching this suite's existing convention (e.g.
    `test_hole_rim_edge_stays_sharp_not_crease`).
    """
    ifc_file, body_context, storey = _make_project()
    wallA = _add_layered_wall(ifc_file, body_context, storey, "WallA", "A", (2.0, 0.2, 2.0), (0.0, 0.0, 0.0))
    wallB = _add_layered_wall(ifc_file, body_context, storey, "WallB", "B", (2.0, 0.2, 1.0), (2.0, 0.0, 0.5))

    svg = render_svg(
        ifc_file,
        camera_pos=(6.0, 0.1, 1.0),
        camera_dir=(1.0, 0.0, 0.02),
        camera_ref=(0.0, 1.0, 0.0),
        use_mat_style_change=True,
    )
    edges = parse_edges(svg)

    # Empirically captured: the SVG-Y range covered by WallB's matched
    # middle band (Z:[0.5, 1.5]). Nothing must fall strictly inside it.
    gap_lo, gap_hi = 9520.095971209596, 10559.888033588803
    a_ys = _mat_style_change_y_values(edges, wallA.GlobalId)
    assert a_ys, "expected WallA to produce at least some mat-style-change edges (the exposed lower/upper quarters)"
    leaked = [y for y in a_ys if gap_lo < y < gap_hi]
    assert not leaked, leaked
    # Sanity: the exposed quarters right at the matched band's own edges are
    # genuinely present -- not vacuously passing because nothing rendered.
    assert any(abs(y - gap_lo) < 1e-6 for y in a_ys), a_ys
    assert any(abs(y - gap_hi) < 1e-6 for y in a_ys), a_ys
