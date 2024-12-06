# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

"""2D drawing generation and serialisation"""

import math
import json
import functools
import re
import warnings

import ifcopenshell
import ifcopenshell.geom

from xml.dom.minidom import parseString
from dataclasses import dataclass, fields, field
from typing import Callable, Sequence

import numpy

W = ifcopenshell.ifcopenshell_wrapper

WHITE = numpy.array((1.0, 1.0, 1.0))

DO_NOTHING = lambda *args: None


@dataclass
class draw_settings:
    width: float = 297.0
    height: float = 420.0
    scale: float = 1.0 / 100.0
    auto_elevation: bool = False
    auto_section: bool = False
    auto_floorplan: bool = True
    space_names: bool = False
    space_areas: bool = False
    door_arcs: bool = False
    subtract_before_hlr: bool = False
    cache: bool = False
    css: bool = True
    storey_heights: str = "none"
    include_entities: str = ""
    exclude_entities: str = "IfcOpeningElement"
    drawing_guid: str = field(
        default="",
        metadata={
            "doc": "Use a drawing with the provided GlobalId. Setting takes priority over 'drawing_object_type'."
        },
    )
    drawing_object_type: str = field(
        default="", metadata={"doc": 'Use IfcAnnotations with provided ObjectType for drawings (e.g. "DRAWING").'}
    )
    profile_threshold: int = -1
    cells: bool = True
    merge_cells: bool = False
    include_projection: bool = True
    hlr_poly: bool = False
    prefilter: bool = True
    include_curves: bool = False
    unify_inputs: bool = True
    arrange_spaces: bool = False


def main(
    settings: draw_settings,
    files: list[ifcopenshell.file],
    iterators: Sequence[ifcopenshell.geom.iterator] = (),
    merge_projection: bool = True,
    progress_function: Callable = DO_NOTHING,
):

    geom_settings = ifcopenshell.geom.settings(
        # when not doing booleans, proper solids from shells isn't a requirement
        REORIENT_SHELLS=settings.subtract_before_hlr,
        # SVG serialiazation depends on element hierarchy now to look up the parent
        ELEMENT_HIERARCHY=True,
    )

    # this is required for serialization
    dimensionality = W.CURVES_SURFACES_AND_SOLIDS if settings.include_curves else W.SURFACES_AND_SOLIDS
    geom_settings.set("dimensionality", dimensionality)
    geom_settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)
    geom_settings.set("apply-default-materials", True)

    if not iterators:
        iterator_kwargs = {}
        if settings.include_entities:
            iterator_kwargs["include"] = settings.include_entities.split(",")
        elif settings.exclude_entities:
            iterator_kwargs["exclude"] = settings.exclude_entities.split(",")

        # We have to keep the iterator in memory because otherwise
        # the styles are cleared up.
        iterators = list(
            map(
                functools.partial(ifcopenshell.geom.iterator, geom_settings, **iterator_kwargs),
                files,
            )
        )

        if settings.cache:
            serializer_settings = ifcopenshell.geom.serializer_settings()
            cache = ifcopenshell.geom.serializers.hdf5("cache.h5", geom_settings, serializer_settings)
            for it in iterators:
                it.set_cache(cache)

    # Initialize serializer
    buffer = ifcopenshell.geom.serializers.buffer()
    serialiser_settings = ifcopenshell.geom.serializer_settings()
    sr = ifcopenshell.geom.serializers.svg(buffer, geom_settings, serialiser_settings)

    sr.setFile(files[0])
    if settings.auto_floorplan:
        sr.setSectionHeightsFromStoreys()

    # setElevationRefGuid and setElevationRef are also mutually exclusive in C-code.
    # Note that guid or object type are not checked anywhere to be valid,
    # it's up to user to keep them valid for the provided projects.
    if settings.drawing_guid or settings.drawing_object_type:
        if settings.drawing_guid:
            found_guid = False
            for f in files:
                try:
                    f.by_guid(settings.drawing_guid)
                    found_guid = True
                except:
                    pass
            if not found_guid:
                raise ValueError(f"Unable to find guid {settings.drawing_guid!r}")
            sr.setElevationRefGuid(settings.drawing_guid)
        elif settings.drawing_object_type:
            sr.setElevationRef(settings.drawing_object_type)
        sr.setWithoutStoreys(True)

    # required for svgfill
    sr.setPolygonal(True)
    sr.setUseNamespace(True)

    sr.setAlwaysProject(settings.include_projection)

    sr.setProfileThreshold(settings.profile_threshold)
    sr.setBoundingRectangle(settings.width, settings.height)
    sr.setScale(settings.scale)
    sr.setAutoElevation(settings.auto_elevation)
    sr.setAutoSection(settings.auto_section)
    sr.setPrintSpaceNames(settings.space_names)
    sr.setPrintSpaceAreas(settings.space_areas)
    sr.setDrawDoorArcs(settings.door_arcs)
    sr.setNoCSS(not settings.css)
    if settings.subtract_before_hlr:
        sr.setSubtractionSettings(W.ALWAYS)

    sr.setUseHlrPoly(settings.hlr_poly)
    sr.setUsePrefiltering(settings.prefilter)
    sr.setUnifyInputs(settings.unify_inputs)

    try:
        sh = ["none", "full", "left"].index(settings.storey_heights)
        sr.setDrawStoreyHeights(sh)
    except:
        raise ValueError("storey_heights should be one of {'none', 'full', 'left'}")

    """
    # It is also possible to add drawing planes manually
    import bpy
    obj = bpy.context.active_object
    sr.addDrawing(
        obj.matrix_world.transposed()[3][0:3], # location
        obj.matrix_world.transposed()[2][0:3], # z axis (view direction)
        obj.matrix_world.transposed()[0][0:3], # x axis
        "Test", # drawing name
        True    # include projection
    )
    """

    # Initialize tree
    tree = ifcopenshell.geom.tree()
    # This instructs the tree to explode BReps into faces and return
    # the style of the face when running tree.select_ray()
    tree.enable_face_styles(True)

    # Loop over iterators for geometric content
    for i, it in enumerate(iterators):
        for elem in it:
            sr.write(elem)
            if elem.type != "IfcSpace":
                tree.add_element(elem)
                progress_function("file", i, "progress", it.progress())

    progress_function("hidden line rendering")
    sr.finalize()

    # Obtain SVG output from serializer buffer
    svg_data_1 = buffer.get_value()

    if not merge_projection:
        return svg_data_1

    if not settings.cells:
        return svg_data_1.encode("ascii", "xmlcharrefreplace")

    def yield_groups(n, tag="g"):
        if n.nodeType == n.ELEMENT_NODE and n.tagName == tag:
            yield n
        for c in n.childNodes:
            yield from yield_groups(c, tag=tag)

    dom1 = parseString(svg_data_1)
    svg1 = dom1.childNodes[0]
    # From file 1 we take the groups to be substituted
    groups1 = [g for g in yield_groups(svg1) if g.getAttribute("class") == "projection"]

    # Parse SVG into vector of line segments
    #
    # The second argument 'projection' tells the parser to only include <g> groups
    # that have the classname 'projection'. The IfcOpenShell SVG serializer puts
    # the hidden line rendering output into this group. So the sections are not
    # included here as they already form closed loops.

    ls_groups = W.svg_to_line_segments(svg_data_1, "projection")
    for i, (ls, g1) in enumerate(zip(ls_groups, groups1)):
        progress_function("creating cells", i)

        projection, g1 = g1, g1.parentNode

        svgfill_context = W.context(W.FILTERED_CARTESIAN_QUOTIENT, 1.0e-3)

        # remove duplicates (without tolerance)
        ls = list(map(tuple, set(map(frozenset, ls))))

        svgfill_context.add(ls)

        if settings.merge_cells:
            # To be refined:
            # - Find cells on original line segments
            # - Associate cells with IFC entities for merging
            # - Merge cells by discarding edges
            # - Associate cells with IFC entities for styling
            num_passes = 1
        else:
            num_passes = 0

        for iteration in range(num_passes + 1):

            # initialize empty group, note that in the current approach only one
            # group is stored
            ps = W.svg_groups_of_polygons()

            if iteration != 0 or svgfill_context.build():
                svgfill_context.write(ps)

            """
            # Debugging tool to plot line segments and cells
            from matplotlib import pyplot as plt

            arr = numpy.array(ls).reshape((-1, 2, 2))
            for x in arr:
                plt.plot(x.T[0], x.T[1])
            for x in ps[0]:
                plt.fill(numpy.array(x.boundary).T[0], numpy.array(x.boundary).T[1])
            """

            if iteration != num_passes:
                pairs = svgfill_context.get_face_pairs()
                semantics = [None] * (max(pairs) + 1)
                # For every edge print the two neighbouring faces
                # for x in range(0, len(pairs), 2):
                #     print(x // 2, *pairs[x:x+2])

            # Reserialize cells into an SVG string
            svg_data_2 = W.polygons_to_svg(ps, True)

            # We parse both SVG files to create on document with the combination of sections from
            # the output directly from the serializer and the cells found from the hidden line
            # rendering
            dom2 = parseString(svg_data_2)
            svg2 = dom2.childNodes[0]
            # file 2 only has the groups we are interested in.
            # in fact in the approach, it's only a single group

            g2 = list(yield_groups(svg2))[0]

            # These are attributes on the original group that we can use to reconstruct
            # a 4x4 matrix of the projection used in the SVG generation process
            nm = g1.getAttribute("ifc:name")
            m4 = numpy.array(json.loads(g1.getAttribute("ifc:plane")))
            m3 = numpy.array(json.loads(g1.getAttribute("ifc:matrix3")))
            m44 = numpy.eye(4)
            m44[0][0:2] = m3[0][0:2]
            m44[1][0:2] = m3[1][0:2]
            m44[0][3] = m3[0][2]
            m44[1][3] = m3[1][2]
            m44 = numpy.linalg.inv(m44)

            def project(xy, z=0.0):
                xyzw = m44 @ numpy.array(xy + [z, 1.0])
                xyzw[1] *= -1.0
                return (m4 @ xyzw)[0:3]

            def pythonize(arr):
                return tuple(map(float, arr))

            # Loop over the cell paths
            for pi, p in enumerate(g2.getElementsByTagName("path")):

                progress_function("group", i, "pass", iteration, "path", pi)

                d = p.getAttribute("d")
                # point inside is an attribute that comes from line_segments_to_polygons()
                # it is an arbitrary point guaranteed to be inside the polygon and outside
                # of any potential inner bounds. We can use this to construct a ray to find
                # the face of the IFC element that the cell belongs to.
                assert p.hasAttribute("ifc:pointInside")

                xy = list(map(float, p.getAttribute("ifc:pointInside").split(",")))

                a, b = project(xy, 0.0), project(xy, -100.0)

                inside_elements = tree.select(pythonize(a))

                if inside_elements:
                    elements = None
                    if iteration != num_passes:
                        semantics[pi] = (inside_elements[0], -1)
                else:
                    elements = tree.select_ray(pythonize(a), pythonize(b - a))

                if elements:
                    # Put the IFC element entity type on the path for CSS-based styling
                    p.setAttribute("class", elements[0].instance.is_a())

                    # Obtain style (IfcOpenShell IfcGeom::Material)
                    style = tree.styles()[elements[0].style_index]

                    # This is just a demonstration. We compose a factor of using:
                    # - ray intersection distance
                    # - dot product ray . face normal
                    # - style transparency
                    # the factor determines how much white will be interpolated
                    # into the style diffuse color.
                    def clr(c):
                        if isinstance(c, ifcopenshell.ifcopenshell_wrapper.colour):
                            return c.r(), c.g(), c.b()
                        else:
                            return c

                    clr = numpy.array(clr(style.diffuse) if style else (0.6, 0.6, 0.6))
                    factor = (math.log(elements[0].distance + 2.0) / 7.0) * (1.0 - 0.5 * abs(elements[0].dot_product))
                    if style and style.has_transparency:
                        factor *= 1.0 - style.transparency
                    clr = WHITE * (1.0 - factor) + clr * factor

                    svg_fill = "rgb(%s)" % ", ".join(str(f * 255.0) for f in clr[0:3])

                    if iteration != num_passes:
                        semantics[pi] = elements[0]
                else:
                    svg_fill = "none"

                p.setAttribute("style", "fill: " + svg_fill)

            if iteration != num_passes:
                to_remove = []

                for he_idx in range(0, len(pairs), 2):
                    # @todo instead of ray_distance, better do (x.point - y.point).dot(x.normal)
                    # to see if they're coplanar, because ray-distance will be different in case
                    # of element surfaces non-orthogonal to the view direction

                    def format(x):
                        if x is None:
                            return None
                        elif isinstance(x, tuple):
                            # found to be inside element using tree.select() no face or style info
                            return x
                        else:
                            return (x.instance.is_a(), x.ray_distance, tuple(x.position))

                    pp = pairs[he_idx : he_idx + 2]
                    if pp == (-1, -1):
                        continue
                    data = list(map(format, map(semantics.__getitem__, pp)))
                    if None not in data and data[0][0] == data[1][0] and abs(data[0][1] - data[1][1]) < 1.0e-5:
                        to_remove.append(he_idx // 2)
                        # Print edge index and semantic data
                        # print(he_idx // 2, *data)

                svgfill_context.merge(to_remove)

        # Swap the XML nodes from the files
        # Remove the original hidden line node we still have in the serializer output
        g1.removeChild(projection)
        g2.setAttribute("class", "projection")
        # Find the children of the projection node parent
        children = [x for x in g1.childNodes if x.nodeType == x.ELEMENT_NODE]
        if children:
            # Insert the new semantically enriched cell-based projection node
            # *before* the node with sections from the serializer. SVG derives
            # draw order from node order in the DOM so sections are draw over
            # the projections.
            g1.insertBefore(g2, children[0])
        else:
            # This generally shouldn't happen
            g1.appendChild(g2)

    if settings.arrange_spaces:
        root_groups = [g for g in yield_groups(svg1) if g.parentNode.tagName == "svg"]
        ref_node = root_groups[-1].nextSibling
        parent = root_groups[0].parentNode
        zone_groups = []

        for i in range(len(root_groups)):
            for j in range(len(root_groups)):
                if i != j:
                    parent.removeChild(root_groups[j])

            # wasteful and looses data for unknown reasons
            # svg_contents = svg1.toxml()
            # polies = W.svg_to_polygons(svg_contents, "IfcSpace")

            polies = [
                p.getAttribute("d")
                for p in yield_groups(svg1, "path")
                if "IfcSpace" in p.parentNode.getAttribute("class")
            ]
            assert all(s.count("M") == 1 for s in polies)
            polies = [[[*map(float, s[1:].split(","))] for s in d.split(" ")[:-1]] for d in polies]

            def create_poly(b):
                p = ifcopenshell.ifcopenshell_wrapper.polygon_2()
                p.boundary = b
                return p

            polies = [create_poly(p) for p in polies]

            def min_bound_extent(p):
                arr = numpy.array(p.boundary)
                return (arr.max(axis=0) - arr.min(axis=0)).min() > 0.5

            polies = type(polies)(filter(min_bound_extent, polies))
            arranged = W.arrange_polygons(polies)
            svg_data_3 = W.polygons_to_svg(arranged, False)
            dom3 = parseString(svg_data_3)
            svg3 = dom3.childNodes[0]
            g3 = next(yield_groups(svg3))
            for p in g3.getElementsByTagName("path"):
                p.setAttribute("style", "fill: none; stroke: black; stroke-width: 0.2")
            zone_groups.append(g3)
            parent.removeChild(root_groups[i])
            for j in range(len(root_groups)):
                parent.insertBefore(root_groups[j], ref_node)

        for rg, zg in zip(root_groups, zone_groups):
            for p in rg.getElementsByTagName("path"):
                p.setAttribute("style", "fill: none; stroke: black; stroke-width: 0.05")
            rg.appendChild(zg)

    data = dom1.toprettyxml()
    data = data.encode("ascii", "xmlcharrefreplace")

    return data


if __name__ == "__main__":
    import sys
    import time
    import argparse

    times = []

    def measure(task, fn):
        t0 = time.time()
        r = fn()
        dt = time.time() - t0
        times.append((task, dt))
        return r

    def print_progress(*args):
        print("\r", *args, " " * 10, end="", flush=True)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "files",
        type=str,
        nargs="+",
        help=(
            "List of files for script to use. "
            "Last file is considered an output file (.svg), all other files are existing IFC files."
        ),
    )

    for field in fields(draw_settings):
        name = field.name.replace("_", "-")
        description = field.metadata.get("doc") or ""
        description += " " if description else ""
        description += f"Default: {repr(field.default)}."
        if field.type == bool:
            parser.add_argument(
                f"--{name}",
                help=description,
                dest=field.name,
                action="store_true",
            )
            parser.add_argument(f"--no-{name}", dest=field.name, action="store_false")
            parser.set_defaults(**{field.name: field.default})
        else:
            parser.add_argument(f"--{name}", help=description, dest=field.name, type=field.type, default=field.default)

    args = vars(parser.parse_args())

    if len(args["files"]) < 2:
        parser.error("At least 2 files are required: one or more input files and one output file.")

    files = args.pop("files")
    output = files.pop()

    settings = draw_settings(**args)

    files = measure("open files", lambda: list(map(ifcopenshell.open, files)))
    result = measure("processing", lambda: main(settings, files, progress_function=print_progress))
    open(output, "wb").write(result)

    print("\r Done!", " " * 20)

    for t, dt in times:
        print(f"{t}: {dt}")
