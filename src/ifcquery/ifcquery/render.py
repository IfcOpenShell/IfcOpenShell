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
import ifcopenshell.util.selector

try:
    import numpy as np
    import pyvista as pv

    _HAS_PYVISTA = True
except ImportError:
    _HAS_PYVISTA = False

VIEWS = ("iso", "top", "south", "north", "east", "west")


def _apply_view(plotter: "pv.Plotter", view: str) -> None:
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
    plotter: "pv.Plotter",
    highlight_ids: frozenset[int] | None,
) -> None:
    """Triangulate and add a geometry shape to the plotter."""
    geom = shape.geometry
    verts = np.array(geom.verts, dtype=float).reshape(-1, 3)
    if verts.size == 0:
        return

    faces = np.array(geom.faces, dtype=int).reshape(-1, 3)
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


def render(
    model: ifcopenshell.file,
    selector: str | None = None,
    element_ids: list[int] | None = None,
    view: str = "iso",
) -> bytes:
    """Render IFC model geometry to a PNG image.

    :param model: The in-memory IFC model.
    :param selector: ifcopenshell selector to restrict rendered elements
        (e.g. ``'IfcWall'`` or ``'IfcBuildingStorey[Name="Ground Floor"]'``).
        When omitted the whole model is rendered.
    :param element_ids: Step IDs of elements to highlight. The rest of the
        model is rendered in translucent grey so the highlighted elements
        stand out.
    :param view: Camera angle: ``iso``, ``top``, ``south``, ``north``,
        ``east``, or ``west``. Defaults to ``iso``.
    :return: PNG image as raw bytes.
    :raises ImportError: If pyvista is not installed.
    :raises ValueError: If the selector matches nothing or the model has no
        renderable geometry.
    """
    if not _HAS_PYVISTA:
        raise ImportError("pyvista is not installed. Install with: pip install pyvista")

    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)

    # Exclude 'Clearance' subcontexts (door/window operation zones) from rendering.
    clearance_ids = {
        c.id()
        for c in model.by_type("IfcGeometricRepresentationSubContext")
        if c.ContextIdentifier == "Clearance"
    }
    if clearance_ids:
        ctx_ids = [
            c.id()
            for c in model.by_type("IfcGeometricRepresentationContext")
            if c.id() not in clearance_ids
        ]
        if ctx_ids:
            settings.set("context-ids", ctx_ids)

    if selector:
        include_elements = list(ifcopenshell.util.selector.filter_elements(model, selector))
        if not include_elements:
            raise ValueError(f"Selector {selector!r} matched no elements")
        iterator = ifcopenshell.geom.iterator(
            settings,
            model,
            multiprocessing.cpu_count(),
            include=include_elements,
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

    plotter = pv.Plotter(off_screen=True, window_size=(1280, 960))
    plotter.background_color = "white"

    while True:
        _add_shape(iterator.get(), plotter, highlight_ids=frozenset(element_ids) if element_ids else None)
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
