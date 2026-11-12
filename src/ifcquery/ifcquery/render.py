# IfcQuery - IFC model interrogation CLI
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcQuery.
#
# IfcQuery is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcQuery is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcQuery.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import multiprocessing
import os
import tempfile

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.selector

try:
    import numpy as np
    import pyvista as pv

    _HAS_PYVISTA = True
except ImportError:
    _HAS_PYVISTA = False

VIEWS = ("iso", "top", "south", "north", "east", "west")


def _apply_view(plotter: pv.Plotter, view: str) -> None:
    """Set the camera to the requested named view. Z is up (IFC convention)."""
    if view == "top":
        plotter.view_xy()
    elif view == "south":
        # Camera at -Y looking toward +Y (south face of building)
        plotter.view_xz(negative=True)
    elif view == "north":
        plotter.view_xz(negative=False)
    elif view == "east":
        plotter.view_yz(negative=False)
    elif view == "west":
        plotter.view_yz(negative=True)
    else:
        plotter.view_isometric()
    # Ensure Z is world up for elevation views
    if view not in ("top",):
        plotter.camera.up = (0, 0, 1)


def _add_shape(
    shape: object,
    plotter: pv.Plotter,
    highlight_ids: frozenset[int] | None,
) -> None:
    """Triangulate and add a geometry shape to the plotter."""
    geom = shape.geometry
    verts = np.array(geom.verts, dtype=float).reshape(-1, 3)
    if verts.size == 0:
        return

    raw_faces = np.array(geom.faces, dtype=int)
    if raw_faces.size == 0 or raw_faces.size % 3 != 0:
        return  # degenerate geometry from kernel — skip silently
    faces = raw_faces.reshape(-1, 3)
    material_ids = np.array(geom.material_ids, dtype=int)

    is_subject = highlight_ids is not None and shape.product.id() in highlight_ids

    for midx, mat in enumerate(geom.materials):
        tri_mask = material_ids == midx
        if not np.any(tri_mask):
            continue

        sub_faces = faces[tri_mask]
        faces_pv = np.hstack([np.full((sub_faces.shape[0], 1), 3, dtype=int), sub_faces]).ravel()
        mesh = pv.PolyData(verts, faces_pv)

        if highlight_ids is not None and not is_subject:
            color = (180, 180, 180)
            opacity = 0.10
        else:
            diffuse = np.clip(np.array(mat.diffuse.components), 0.0, 1.0)
            color = tuple((diffuse * 255).astype(np.uint8))
            transparency = mat.transparency if mat.transparency == mat.transparency else 0.0
            opacity = float(np.clip(1.0 - transparency, 0.0, 1.0))

        plotter.add_mesh(mesh, color=color, opacity=opacity, show_edges=False)


def _render_iterator(
    iterator: object,
    highlight_ids: list[int] | None,
    view: str,
) -> bytes:
    """Drive a geometry iterator into a pyvista plotter and return PNG bytes."""
    plotter = pv.Plotter(off_screen=True, window_size=(1280, 960))
    plotter.background_color = "white"

    while True:
        try:
            _add_shape(iterator.get(), plotter, highlight_ids=frozenset(highlight_ids) if highlight_ids else None)
        except Exception:
            pass  # skip broken shapes, keep rendering the rest
        if not iterator.next():
            break

    plotter.reset_camera()
    _apply_view(plotter, view)

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".png")
    os.close(tmp_fd)
    try:
        plotter.show(screenshot=tmp_path, auto_close=True)
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _build_geom_settings(model: ifcopenshell.file) -> ifcopenshell.geom.settings:
    """Build geometry settings, excluding Clearance subcontexts."""
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)

    clearance_ids = {
        c.id() for c in model.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier == "Clearance"
    }
    if clearance_ids:
        ctx_ids = [c.id() for c in model.by_type("IfcGeometricRepresentationContext") if c.id() not in clearance_ids]
        if ctx_ids:
            settings.set("context-ids", ctx_ids)

    return settings


def _get_occurrence_class(type_entity) -> str:
    """Derive the occurrence IFC class from a type entity class name."""
    type_class = type_entity.is_a()
    if type_class.endswith("Type"):
        return type_class[:-4]
    return "IfcBuildingElementProxy"


def _make_type_occurrence(model: ifcopenshell.file, type_entity) -> object | None:
    """Create a temporary occurrence for *type_entity* using its RepresentationMaps.

    The occurrence is added to *model* and references the type's existing
    RepresentationMap entities via IfcMappedItem.  Returns the occurrence entity,
    or ``None`` when the type has no usable RepresentationMaps.

    .. note::
        This function is intended for use on a temporary model copy.  The
        caller is responsible for discarding that copy after rendering.
    """
    rep_maps = getattr(type_entity, "RepresentationMaps", None) or []
    if not rep_maps:
        return None

    # One IfcMappedItem per RepresentationMap.
    mapped_items = []
    for rep_map in rep_maps:
        origin = model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        transform = model.create_entity(
            "IfcCartesianTransformationOperator3D",
            LocalOrigin=origin,
        )
        mapped_item = model.create_entity(
            "IfcMappedItem",
            MappingSource=rep_map,
            MappingTarget=transform,
        )
        mapped_items.append(mapped_item)

    context = rep_maps[0].MappedRepresentation.ContextOfItems
    shape_rep = model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="MappedRepresentation",
        Items=mapped_items,
    )
    prod_def_shape = model.create_entity(
        "IfcProductDefinitionShape",
        Representations=[shape_rep],
    )

    # Identity placement.
    pt = model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
    z_dir = model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
    x_dir = model.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
    axis2 = model.create_entity("IfcAxis2Placement3D", Location=pt, Axis=z_dir, RefDirection=x_dir)
    placement = model.create_entity("IfcLocalPlacement", RelativePlacement=axis2)

    occ_class = _get_occurrence_class(type_entity)
    try:
        occurrence = model.create_entity(
            occ_class,
            GlobalId=ifcopenshell.guid.new(),
            Name=f"_type_preview_{type_entity.id()}",
            ObjectPlacement=placement,
            Representation=prod_def_shape,
        )
    except Exception:
        occurrence = model.create_entity(
            "IfcBuildingElementProxy",
            GlobalId=ifcopenshell.guid.new(),
            Name=f"_type_preview_{type_entity.id()}",
            ObjectPlacement=placement,
            Representation=prod_def_shape,
        )
    return occurrence


def _make_profile_occurrence(model: ifcopenshell.file, type_entity) -> object | None:
    """Create a temporary occurrence for a type that has a material profile set.

    Finds the first profile in the type's IfcMaterialProfileSet and creates a
    1-metre IfcExtrudedAreaSolid body representation from it.  Returns the
    occurrence, or ``None`` when no usable profile is found.

    .. note::
        Intended for use on a temporary model copy; caller discards it after
        rendering.
    """
    # Locate the first profile from the type's material profile set.
    profile = None
    for rel in getattr(type_entity, "HasAssociations", []):
        if not rel.is_a("IfcRelAssociatesMaterial"):
            continue
        mat = rel.RelatingMaterial
        if mat.is_a("IfcMaterialProfileSetUsage"):
            mat = mat.ForProfileSet
        if mat.is_a("IfcMaterialProfileSet"):
            mat_profiles = list(getattr(mat, "MaterialProfiles", None) or [])
            if mat_profiles:
                profile = getattr(mat_profiles[0], "Profile", None)
        if profile is not None:
            break
    if profile is None:
        return None

    # Find a Body subcontext, or fall back to any Model context.
    body_ctx = None
    for ctx in model.by_type("IfcGeometricRepresentationSubContext"):
        if ctx.ContextIdentifier == "Body":
            body_ctx = ctx
            break
    if body_ctx is None:
        for ctx in model.by_type("IfcGeometricRepresentationContext"):
            if ctx.ContextType == "Model":
                body_ctx = ctx
                break
    if body_ctx is None:
        return None

    # Extrude 1 metre along Z (profile lies in XY plane).
    origin = model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
    z_axis = model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
    x_axis = model.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
    position = model.create_entity("IfcAxis2Placement3D", Location=origin, Axis=z_axis, RefDirection=x_axis)
    extrude_dir = model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
    extrusion = model.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=profile,
        Position=position,
        ExtrudedDirection=extrude_dir,
        Depth=1.0,
    )
    shape_rep = model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=body_ctx,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[extrusion],
    )
    prod_def_shape = model.create_entity(
        "IfcProductDefinitionShape",
        Representations=[shape_rep],
    )

    # Identity placement.
    pt = model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
    z_dir = model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
    x_dir = model.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
    axis2 = model.create_entity("IfcAxis2Placement3D", Location=pt, Axis=z_dir, RefDirection=x_dir)
    placement = model.create_entity("IfcLocalPlacement", RelativePlacement=axis2)

    occ_class = _get_occurrence_class(type_entity)
    try:
        occurrence = model.create_entity(
            occ_class,
            GlobalId=ifcopenshell.guid.new(),
            Name=f"_profile_preview_{type_entity.id()}",
            ObjectPlacement=placement,
            Representation=prod_def_shape,
        )
    except Exception:
        occurrence = model.create_entity(
            "IfcBuildingElementProxy",
            GlobalId=ifcopenshell.guid.new(),
            Name=f"_profile_preview_{type_entity.id()}",
            ObjectPlacement=placement,
            Representation=prod_def_shape,
        )
    return occurrence


def _render_with_types(
    model: ifcopenshell.file,
    types: list,
    selector_elements: list | None,
    element_ids: list[int] | None,
    type_highlight_ids: set[int],
    view: str,
) -> bytes:
    """Render type entities by creating occurrences in a temporary model copy.

    *types* — list of IfcTypeProduct entities to render.
    *selector_elements* — non-type elements from the selector (or ``None``).
    *element_ids* — original highlight IDs (may contain type IDs).
    *type_highlight_ids* — subset of *element_ids* that are type IDs.
    """
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".ifc")
    os.close(tmp_fd)
    try:
        model.write(tmp_path)
        tmp = ifcopenshell.open(tmp_path)

        # Map original type step-ID → new occurrence step-ID in the tmp model.
        type_id_to_occ_id: dict[int, int] = {}
        for t in types:
            tmp_type = tmp.by_id(t.id())
            occ = _make_type_occurrence(tmp, tmp_type) or _make_profile_occurrence(tmp, tmp_type)
            if occ:
                type_id_to_occ_id[t.id()] = occ.id()

        if not type_id_to_occ_id:
            raise ValueError("Type entities have no RepresentationMaps or material profile sets to render")

        include = [tmp.by_id(occ_id) for occ_id in type_id_to_occ_id.values()]
        if selector_elements:
            include.extend(tmp.by_id(e.id()) for e in selector_elements)

        settings = _build_geom_settings(tmp)
        iterator = ifcopenshell.geom.iterator(settings, tmp, multiprocessing.cpu_count(), include=include)
        if not iterator.initialize():
            raise ValueError("Type entities have no renderable geometry")

        # Remap type IDs → occurrence IDs in the highlight list.
        new_highlight = None
        if element_ids:
            new_highlight = []
            for hid in element_ids:
                if hid in type_highlight_ids:
                    mapped = type_id_to_occ_id.get(hid)
                    if mapped:
                        new_highlight.append(mapped)
                else:
                    new_highlight.append(hid)

        return _render_iterator(iterator, new_highlight, view)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def render(
    model: ifcopenshell.file,
    selector: str | None = None,
    element_ids: list[int] | None = None,
    view: str = "iso",
) -> bytes:
    """Render IFC model geometry to a PNG image.

    Supports both element instances and element types (e.g. ``IfcWallType``).
    When type entities are targeted — via *selector* or *element_ids* — a
    temporary copy of the model is used to create proxy occurrences that
    reference the type's RepresentationMaps; the original model is not
    modified.

    :param model: The in-memory IFC model.
    :param selector: ifcopenshell selector to restrict rendered elements
        (e.g. ``'IfcWall'``, ``'IfcWallType'``, or
        ``'IfcBuildingStorey[Name="Ground Floor"]'``).
        When omitted the whole model is rendered.
    :param element_ids: Step IDs of elements (or types) to highlight. The
        rest of the model is rendered in translucent grey so the highlighted
        items stand out.
    :param view: Camera angle: ``iso``, ``top``, ``south``, ``north``,
        ``east``, or ``west``. Defaults to ``iso``.
    :return: PNG image as raw bytes.
    :raises ImportError: If pyvista is not installed.
    :raises ValueError: If the selector matches nothing or the model has no
        renderable geometry.
    """
    if not _HAS_PYVISTA:
        raise ImportError("pyvista is not installed. Install with: pip install pyvista")

    # --- Partition selector results into types and elements ---
    if selector:
        matched = list(ifcopenshell.util.selector.filter_elements(model, selector))
        if not matched:
            raise ValueError(f"Selector {selector!r} matched no elements")
        types = [e for e in matched if e.is_a("IfcTypeProduct")]
        selector_elements: list | None = [e for e in matched if not e.is_a("IfcTypeProduct")]
    else:
        types = []
        selector_elements = None  # no restriction — render all elements

    # --- Collect any type entities from element_ids ---
    type_highlight_ids: set[int] = set()
    if element_ids:
        for eid in element_ids:
            entity = model.by_id(eid)
            if entity.is_a("IfcTypeProduct"):
                type_highlight_ids.add(eid)
                seen = {t.id() for t in types}
                if eid not in seen:
                    types.append(entity)

    # --- Delegate to temp-copy path when any type entities are involved ---
    if types:
        return _render_with_types(model, types, selector_elements, element_ids, type_highlight_ids, view)

    # --- Regular element rendering ---
    settings = _build_geom_settings(model)

    if selector_elements is not None:
        if not selector_elements:
            raise ValueError(f"Selector {selector!r} matched only type entities (use a type selector or IfcElement)")
        iterator = ifcopenshell.geom.iterator(
            settings,
            model,
            multiprocessing.cpu_count(),
            include=selector_elements,
        )
    else:
        exclude = list(model.by_type("IfcOpeningElement"))
        iterator = ifcopenshell.geom.iterator(
            settings,
            model,
            multiprocessing.cpu_count(),
            exclude=exclude if exclude else None,
        )

    if not iterator.initialize():
        raise ValueError("No renderable geometry found in model (or selector matched nothing)")

    return _render_iterator(iterator, element_ids, view)
