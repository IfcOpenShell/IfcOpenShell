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

import ifcopenshell
import ifcopenshell.geom

from xml.dom.minidom import parseString
from dataclasses import dataclass, fields

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
    drawing_guid: str = ""
    profile_threshold: int = -1
    cells: bool = True
    merge_cells: bool = False
    include_projection: bool = True
    prefilter: bool = True
    include_curves: bool = False
    unify_inputs: bool = True


def main(settings, files, iterators=None, merge_projection=True, progress_function=DO_NOTHING):

    geom_settings = ifcopenshell.geom.settings(
        # this is required for serialization
        APPLY_DEFAULT_MATERIALS=True,
        DISABLE_TRIANGULATION=True,
        INCLUDE_CURVES=settings.include_curves,
        # when not doing booleans, proper solids from shells isn't a requirement
        SEW_SHELLS=settings.subtract_before_hlr,
    )

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
            cache = ifcopenshell.geom.serializers.hdf5("cache.h5", geom_settings)
            for it in iterators:
                it.set_cache(cache)

    def yield_from_iterator(it):
        if it.initialize():
            while True:
                yield it.get()
                if not it.next():
                    break

    # Initialize serializer
    buffer = ifcopenshell.geom.serializers.buffer()
    sr = ifcopenshell.geom.serializers.svg(buffer, geom_settings)

    sr.setFile(files[0])
    if settings.auto_floorplan:
        sr.setSectionHeightsFromStoreys()

    if settings.drawing_guid:
        sr.setElevationRefGuid(settings.drawing_guid)
        sr.setWithoutStoreys(True)
        # If you want to filter by IfcAnnotation ObjectType named "DRAWING"
        # sr.setElevationRef("DRAWING")

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
        for elem in yield_from_iterator(it):
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
    
    def yield_groups(n):
        if n.nodeType == n.ELEMENT_NODE and n.tagName == "g":
            yield n
        for c in n.childNodes:
            yield from yield_groups(c)

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
        
        for iteration in range(num_passes+1):
        
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
                semantics = [None] * (max(pairs)+1)
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
                    clr = numpy.array(style.diffuse)
                    factor = (math.log(elements[0].distance + 2.0) / 7.0) * (1.0 - 0.5 * abs(elements[0].dot_product))
                    if style.has_transparency:
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
                        if x is None: return None
                        elif isinstance(x, tuple):
                            # found to be inside element using tree.select() no face or style info
                            return x
                        else: return (x.instance.is_a(), x.ray_distance, tuple(x.position))
                    
                    pp = pairs[he_idx:he_idx+2]
                    if pp == (-1, -1):
                        continue
                    data = list(map(format, map(semantics.__getitem__, pp)))
                    if None not in data and data[0][0] == data[1][0] and abs(data[0][1] - data[1][1]) < 1.e-5:
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

    data = dom1.toxml()
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

    parser.add_argument("files", type=str, nargs="+")

    for field in fields(draw_settings):
        if field.type == bool:
            parser.add_argument("--" + field.name.replace("_", "-"), dest=field.name, action="store_true")
            parser.add_argument("--no-" + field.name.replace("_", "-"), dest=field.name, action="store_false")
            parser.set_defaults(**{field.name: field.default})
        else:
            parser.add_argument(
                "--" + field.name.replace("_", "-"), dest=field.name, type=field.type, default=field.default
            )

    args = vars(parser.parse_args(sys.argv))
    files = args.pop("files")
    files.remove(__file__)
    output = files.pop()

    settings = draw_settings(**args)

    files = measure("open files", lambda: list(map(ifcopenshell.open, files)))
    result = measure("processing", lambda: main(settings, files, progress_function=print_progress))
    open(output, "wb").write(result)

    print("\r Done!", " " * 20)

    for t, dt in times:
        print(f"{t}: {dt}")
