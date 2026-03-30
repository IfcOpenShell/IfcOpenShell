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

import base64
import os
from io import BytesIO
from typing import Any

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.selector

try:
    import ifcopenshell.draw

    _HAS_DRAW = True
except ImportError:
    _HAS_DRAW = False

from xml.etree.ElementTree import Element, ElementTree, SubElement, register_namespace

try:
    import cairosvg  # type: ignore

    _HAS_CAIROSVG = True
except Exception:
    _HAS_CAIROSVG = False


try:
    from PIL import Image  # type: ignore

    _HAS_PIL = True
except Exception:
    _HAS_PIL = False

VIEWS = ("floorplan", "elevation", "section", "auto")
OUTPUT_FORMATS = ("svg", "png", "base64")


def _escape_css_attr(name: str) -> str:
    # CSS attribute selectors must escape ':' (e.g. ifc:guid -> ifc\:guid)
    return name.replace(":", "\\:")


def _highlight_css_from_ids(model: ifcopenshell.file, element_ids: list[int]) -> str:
    guids: list[str] = []
    for sid in element_ids:
        try:
            e = model.by_id(int(sid))
        except RuntimeError:
            continue
        if e is None:
            continue
        gid = getattr(e, "GlobalId", None)
        if isinstance(gid, str) and gid:
            guids.append(gid)

    if not guids:
        return ""

    attr = _escape_css_attr("ifc:guid")

    css = [
        "/* Auto-highlight injected by ifcquery.plot */",
        f"[{attr}] path {{ opacity: 0.10; }}",
        f"[{attr}] text {{ opacity: 0.25; }}",
    ]
    for gid in guids:
        css.append(f'[{attr}="{gid}"] path {{ opacity: 1.0; stroke: #d00; stroke-width: 0.25; }}')
        css.append(f'[{attr}="{gid}"] text {{ opacity: 1.0; fill: #d00; }}')
    return "\n".join(css) + "\n"


def _make_filtered_iterator(model: ifcopenshell.file, include_elements: list[Any]) -> ifcopenshell.geom.iterator:
    # Avoid multiprocessing in WASM; os.cpu_count is good enough.
    n_threads = os.cpu_count() or 1

    # These flags mirror the defaults used by ifcopenshell.draw in v0.8.x.
    geom_settings = ifcopenshell.geom.settings(
        REORIENT_SHELLS=False,
        ELEMENT_HIERARCHY=True,
    )

    # IfcOpenShell wrapper constants may live in different places across builds.
    wrapper = getattr(ifcopenshell, "ifcopenshell_wrapper", None)
    if wrapper is not None:
        try:
            geom_settings.set("iterator-output", wrapper.NATIVE)
        except Exception:
            pass
        try:
            geom_settings.set("apply-default-materials", True)
        except Exception:
            pass
        try:
            geom_settings.set("dimensionality", wrapper.SURFACES_AND_SOLIDS)
        except Exception:
            pass

    return ifcopenshell.geom.iterator(geom_settings, model, n_threads, include=include_elements)


def _diagnose_empty_drawing(model: ifcopenshell.file, view: str) -> str:
    """Return a helpful error message when ifcopenshell.draw produces no geometry groups."""
    hints = []

    if view in ("floorplan", "auto"):
        storeys = model.by_type("IfcBuildingStorey")
        if not storeys:
            hints.append("the model has no IfcBuildingStorey entities (required for auto_floorplan)")
        else:
            null_elevation = [s for s in storeys if getattr(s, "Elevation", None) is None]
            if null_elevation:
                names = ", ".join(f'"{s.Name or s.GlobalId}"' for s in null_elevation)
                hints.append(
                    f"storey Elevation is None for: {names} — "
                    "set IfcBuildingStorey.Elevation (e.g. 0.0) so the section cut height can be determined"
                )

    has_geom = any(getattr(e, "Representation", None) is not None for e in model.by_type("IfcProduct"))
    if not has_geom:
        hints.append("no IfcProduct entities have geometric representations")

    base = f"No plan geometry found for view={view!r}."
    if hints:
        return base + " Possible causes: " + "; ".join(hints) + "."
    return base + " The model may lack geometry visible in this view."


def plot(
    model: ifcopenshell.file,
    *,
    output_format: str = "png",
    selector: str | None = None,
    element_ids: list[int] | None = None,
    view: str = "floorplan",
    # SVG / page sizing (draw works in mm coordinates)
    width_mm: float = 297.0,
    height_mm: float = 420.0,
    scale: float = 1.0 / 100.0,
    merge_projection: bool = True,
    # PNG sizing (only for output_format png/base64)
    png_width: int = 1024,
    png_height: int = 1024,
) -> bytes | dict[str, Any]:
    """
    Plot IFC model as SVG (via ifcopenshell.draw) or PNG/base64 (via CairoSVG).

    Args:
        model: In-memory IFC model.
        output_format: 'svg' | 'png' | 'base64'
            - 'svg'   -> returns SVG bytes
            - 'png'   -> returns PNG bytes
            - 'base64'-> returns dict: {mime, png_b64, width, height, view}
        selector: ifcopenshell selector query to restrict plotted elements.
        element_ids: STEP ids to highlight; non-highlighted geometry is faded.
        view: One of VIEWS ('floorplan', 'elevation', 'section', 'auto').
        width_mm, height_mm: Page size in mm.
        scale: Model-to-paper scale (0.01 means 1:100).
        merge_projection: Passed through to ifcopenshell.draw.main.
        png_width, png_height: Raster size in pixels for png/base64 outputs.

    Raises:
        ImportError: if ifcopenshell.draw or CairoSVG is not available (as required).
        ValueError: invalid args or selector matches nothing.
    """
    if output_format not in OUTPUT_FORMATS:
        raise ValueError(f"output_format must be one of {OUTPUT_FORMATS}, got {output_format!r}")
    if view not in VIEWS:
        raise ValueError(f"view must be one of {VIEWS}, got {view!r}")
    if not _HAS_DRAW:
        raise ImportError("ifcopenshell.draw is not available in this environment.")

    # Configure draw settings
    settings = ifcopenshell.draw.draw_settings(
        auto_floorplan=(view in ("floorplan", "auto")),
        auto_elevation=(view in ("elevation", "auto")),
        auto_section=(view in ("section", "auto")),
        width=width_mm,
        height=height_mm,
        scale=scale,
        css="",
    )

    # Optional highlight CSS overlay
    if element_ids:
        settings.css = _highlight_css_from_ids(model, element_ids)

    # Optional element restriction via selector -> custom iterator
    iterators: tuple[Any, ...] = ()
    if selector:
        include_elements = list(ifcopenshell.util.selector.filter_elements(model, selector))
        if not include_elements:
            raise ValueError(f"Selector {selector!r} matched no elements")
        it = _make_filtered_iterator(model, include_elements)
        iterators = (it,)
        # If we explicitly include elements, don't rely on exclude_entities (best-effort).
        settings.exclude_entities = ""

    # Generate SVG
    svg_bytes = ifcopenshell.draw.main(
        settings,
        files=[model],
        iterators=iterators,
        merge_projection=merge_projection,
    )

    register_namespace("", "http://www.w3.org/2000/svg")

    def svg_split(f):
        x = ElementTree(file=f)
        svg = x.getroot()
        resources = []
        for child in svg:
            if child.tag == "{http://www.w3.org/2000/svg}g":
                root = Element(svg.tag, svg.attrib)
                n = ElementTree(root)
                for r in resources + [child]:
                    root.append(r)
                b = BytesIO()
                n.write(b, xml_declaration=True, encoding="utf-8", method="xml")
                yield b.getvalue()
            else:
                resources.append(child)

    if output_format == "svg":
        return svg_bytes

    # Need CairoSVG for png/base64
    if not _HAS_CAIROSVG:
        raise ImportError("CairoSVG is not installed. Install with: pip install cairosvg")

    svgs = list(svg_split(BytesIO(svg_bytes)))
    if not svgs:
        raise ValueError(_diagnose_empty_drawing(model, view))

    composite = None
    png_bytes = None
    for i, svgb in enumerate(svgs):
        png_bytes = cairosvg.svg2png(bytestring=svgb, output_width=png_width, output_height=png_height)
        if len(svgs) == 1:
            break

        # Need Pillow for concatenating images
        if not _HAS_PIL:
            raise ImportError("Pillow is not installed. Install with: pip install Pillow")

        if composite is None:
            composite = Image.new("RGBA", (png_width, png_height * len(svgs)))
        img = Image.open(BytesIO(png_bytes))
        composite.paste(img, (0, png_height * i))
    if composite is not None:
        b = BytesIO()
        composite.save(b, "png")
        png_bytes = b.getvalue()

    if output_format == "base64":
        return {
            "mime": "image/png",
            "png_b64": base64.b64encode(png_bytes).decode(),
            "width": png_width,
            "height": png_height,
            "view": view,
        }

    return png_bytes
