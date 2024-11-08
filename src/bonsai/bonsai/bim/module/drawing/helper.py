# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import math
import mathutils.geometry
import bonsai.tool as tool
from mathutils import Vector

# Code taken and updated from https://blenderartists.org/t/detecting-intersection-of-bounding-boxes/457520/2


class BoundingEdge:
    def __init__(self, v0, v1):
        self.vertex = (v0, v1)
        self.vector = v1 - v0


class BoundingFace:
    def __init__(self, v0, v1, v2):
        self.vertex = (v0, v1, v2)
        self.normal = mathutils.geometry.normal(v0, v1, v2)


class BoundingBox:
    def __init__(self, ob, vertex=None):
        self.vertex = vertex or [ob.matrix_world @ Vector(v) for v in ob.bound_box]
        if self.vertex != None:
            self.edge = [
                BoundingEdge(self.vertex[0], self.vertex[1]),
                BoundingEdge(self.vertex[1], self.vertex[2]),
                BoundingEdge(self.vertex[2], self.vertex[3]),
                BoundingEdge(self.vertex[3], self.vertex[0]),
                BoundingEdge(self.vertex[4], self.vertex[5]),
                BoundingEdge(self.vertex[5], self.vertex[6]),
                BoundingEdge(self.vertex[6], self.vertex[7]),
                BoundingEdge(self.vertex[7], self.vertex[4]),
                BoundingEdge(self.vertex[0], self.vertex[4]),
                BoundingEdge(self.vertex[1], self.vertex[5]),
                BoundingEdge(self.vertex[2], self.vertex[6]),
                BoundingEdge(self.vertex[3], self.vertex[7]),
            ]
            self.face = [
                BoundingFace(self.vertex[0], self.vertex[1], self.vertex[3]),
                BoundingFace(self.vertex[0], self.vertex[4], self.vertex[1]),
                BoundingFace(self.vertex[0], self.vertex[3], self.vertex[4]),
                BoundingFace(self.vertex[6], self.vertex[5], self.vertex[7]),
                BoundingFace(self.vertex[6], self.vertex[7], self.vertex[2]),
                BoundingFace(self.vertex[6], self.vertex[2], self.vertex[5]),
            ]

    def whichSide(self, vtxs, normal, faceVtx):
        retVal = 0
        positive = 0
        negative = 0
        for v in vtxs:
            t = normal.dot(v - faceVtx)
            if t > 0:
                positive = positive + 1
            elif t < 0:
                negative = negative + 1

            if positive != 0 and negative != 0:
                return 0

        if positive != 0:
            retVal = 1
        else:
            retVal = -1
        return retVal

    # Taken from: http://www.geometrictools.com/Documentation/MethodOfSeparatingAxes.pdf
    def intersect(self, bb):
        retVal = False
        if self.vertex != None and bb.vertex != None:
            # check all the faces of this object for a separation axis
            for i, f in enumerate(self.face):
                d = f.normal
                if self.whichSide(bb.vertex, d, f.vertex[0]) > 0:
                    return False  # all the vertices are on the +ve side of the face

            # now do it again for the other objects faces
            for i, f in enumerate(bb.face):
                d = f.normal
                if self.whichSide(self.vertex, d, f.vertex[0]) > 0:
                    return False  # all the vertices are on the +ve side of the face

            # do edge checks
            for e1 in self.edge:
                for e2 in bb.edge:
                    d = e1.vector.cross(e2.vector)
                    side0 = self.whichSide(self.vertex, d, e1.vertex[0])
                    if side0 == 0:
                        continue
                    side1 = self.whichSide(bb.vertex, d, e1.vertex[0])
                    if side1 == 0:
                        continue

                    if (side0 * side1) < 0:
                        return False

            retVal = True
        return retVal


# This function stolen from https://github.com/kevancress/MeasureIt_ARCH/blob/dcf607ce0896aa2284463c6b4ae9cd023fc54cbe/measureit_arch_baseclass.py
# MeasureIt-ARCH is GPL-v3
def format_distance(
    value,
    isArea=False,
    hide_units=True,
    precision=None,
    decimal_places=None,
    suppress_zero_inches=False,
    in_unit_length=False,
):
    s_code = "\u00b2"  # Superscript two THIS IS LEGACY (but being kept for when Area Measurements are re-implimented)

    # Get Scene Unit Settings
    scaleFactor = bpy.context.scene.unit_settings.scale_length
    unit_system = bpy.context.scene.unit_settings.system
    unit_length = bpy.context.scene.unit_settings.length_unit

    value *= scaleFactor

    # Imperial Formatting
    if unit_system == "IMPERIAL":
        if in_unit_length:
            if unit_length == "INCHES":
                toInches = 1
            if unit_length == "FEET":
                toInches = 11.9999
        else:
            toInches = 39.3700787401574887
        inPerFoot = 11.9999

        if isArea:
            toInches = 1550
            inPerFoot = 143.999
        if not precision:
            precision = 256
        elif precision == "1":
            precision = 1
        elif "/" in precision:
            precision = int(precision.split("/")[1])

        base = int(precision)
        decInches = value * toInches

        # Separate ft and inches
        # Unless Inches are the specified Length Unit
        if unit_length != "INCHES":
            feet = int(decInches / inPerFoot)  # remove decimal
            decInches -= feet * inPerFoot
        else:
            feet = 0

        # Separate Fractional Inches
        decInches = abs(decInches)  # ignore the sign for inches
        inches = math.floor(decInches)  # remove decimal
        if inches != 0:
            frac = round(base * (decInches - inches))
        else:
            frac = round(base * (decInches))

        # Set proper numerator and denominator
        if frac != base:
            numcycles = int(math.log2(base))
            for i in range(numcycles):
                if frac % 2 == 0:
                    frac = int(frac / 2)
                    base = int(base / 2)
                else:
                    break
        else:
            frac = 0
            inches += 1

        # Check values and compose string
        if inches == 12:
            if unit_length == "INCHES":
                inches = 12
            if unit_length == "FEET":
                feet += 1
                inches = 0

        if not isArea:
            add_inches = bool(inches) or not suppress_zero_inches or (inches == 0 and frac)
            tx_dist = ""
            if feet:
                tx_dist += str(feet) + "'"
            if not feet and not add_inches:
                tx_dist += str(feet) + "'"
            if feet and add_inches:
                tx_dist += " - "
            if not feet and value < 0:
                tx_dist += "-"
            if add_inches:
                if feet == 0 and inches == 0:
                    pass
                else:
                    tx_dist += str(inches)
            if add_inches and frac:
                if feet == 0 and inches == 0:
                    pass
                else:
                    tx_dist += " "
            if frac:
                tx_dist += str(frac) + "/" + str(base)
            if add_inches or frac:
                tx_dist += '"'
        else:
            tx_dist = str("%1.3f" % (value * toInches / inPerFoot)) + " sq. ft."

    # METRIC FORMATTING
    elif unit_system == "METRIC":
        if in_unit_length:
            if unit_length == "CENTIMETERS":
                value = value / 100
            if unit_length == "MILLIMETERS":
                value = value / 1000

        if precision:
            value = precision * round(float(value) / precision)

        if decimal_places is not None:
            fmt = "%1." + str(decimal_places) + "f"

        # Meters
        if unit_length == "METERS":
            if decimal_places is None:
                fmt = "%1.3f"
            if hide_units is False:
                fmt += " m"
            tx_dist = fmt % value
        # Centimeters
        elif unit_length == "CENTIMETERS":
            if decimal_places is None:
                fmt = "%1.1f"
            if hide_units is False:
                fmt += " cm"
            d_cm = value * (100)
            tx_dist = fmt % d_cm
        # Millimeters
        elif unit_length == "MILLIMETERS":
            if decimal_places is None:
                fmt = "%1.0f"
            if hide_units is False:
                fmt += " mm"
            d_mm = value * (1000)
            tx_dist = fmt % d_mm

        # Otherwise Use Adaptive Units
        else:
            if round(value, 2) >= 1.0 and decimal_places is None:
                fmt = "%1.3f"
                if hide_units is False:
                    fmt += " m"
                tx_dist = fmt % value
            else:
                if round(value, 2) >= 0.01 and decimal_places is None:
                    fmt = "%1.1f"
                    if hide_units is False:
                        fmt += " cm"
                    d_cm = value * (100)
                    tx_dist = fmt % d_cm
                else:
                    if decimal_places is None:
                        fmt = "%1.0f"
                    if hide_units is False:
                        fmt += " mm"
                    d_mm = value * (1000)
                    tx_dist = fmt % d_mm
        if isArea:
            tx_dist += s_code
    else:
        tx_dist = fmt % value

    return tx_dist


def get_active_drawing(scene):
    """Get active drawing collection and camera"""
    props = scene.DocProperties
    try:
        camera = tool.Ifc.get_object(tool.Ifc.get().by_id(props.active_drawing_id))
        return camera.BIMObjectProperties.collection, camera
    except:
        return None, None


def get_project_collection(scene):
    """Get main project collection"""

    colls = [c for c in scene.collection.children if c.name.startswith("IfcProject")]
    if len(colls) != 1:
        raise RuntimeError("project collection missing or not unique")
    return colls[0]


def parse_diagram_scale(camera):
    """Returns numeric value of scale"""
    if camera.BIMCameraProperties.diagram_scale == "CUSTOM":
        _, fraction = camera.BIMCameraProperties.custom_diagram_scale.split("|")
    else:
        _, fraction = camera.BIMCameraProperties.diagram_scale.split("|")
    numerator, denominator = fraction.split("/")
    return float(numerator) / float(denominator)


def ortho_view_frame(
    camera: bpy.types.Camera, margin: float = 0.015
) -> tuple[float, float, float, float, float, float]:
    """Calculates 2d bounding box of camera view area.

    Similar to `bpy.types.Camera.view_frame`

    :arg camera: camera of drawing
    :type camera: bpy.types.Camera + BIMCameraProperties
    :arg margin: margins, in scene units
    :type margin: float
    :return: (xmin, xmax, ymin, ymax, zmin, zmax) in local camera coordinates
    """
    aspect = camera.BIMCameraProperties.raster_y / camera.BIMCameraProperties.raster_x
    size = camera.ortho_scale
    hwidth = size * 0.5
    hheight = size * 0.5 * aspect
    scale = parse_diagram_scale(camera)
    xmarg = margin * scale
    ymarg = margin * scale * aspect
    return (-hwidth + xmarg, hwidth - xmarg, -hheight + ymarg, hheight - ymarg, -camera.clip_start, -camera.clip_end)


def almost_zero(v):
    return abs(v) < 1e-5


def clip_segment(bounds, segm):
    """Clipping line segment to bounds

    :arg bounds: (xmin, xmax, ymin, ymax)
    :arg segm: 2 vertices of the segment
    :return: 2 new vertices of segment or None if segment outside the bounding box
    """
    # Liang–Barsky algorithm

    xmin, xmax, ymin, ymax, _, _ = bounds
    p1, p2 = segm

    def clip_side(p, q):
        if almost_zero(p):  # ~= 0, parallel to the side
            if q < 0:
                return None  # outside
            else:
                return 0, 1  # inside

        t = q / p  # the intersection point

        if p < 0:  # entering
            return t, 1
        else:  # leaving
            return 0, t

    dlt = p2 - p1

    tt = (
        clip_side(-dlt.x, p1.x - xmin),  # left
        clip_side(+dlt.x, xmax - p1.x),  # right
        clip_side(-dlt.y, p1.y - ymin),  # bottom
        clip_side(+dlt.y, ymax - p1.y),  # top
    )

    if None in tt:
        return None

    t1 = max(0, max(t[0] for t in tt))
    t2 = min(1, min(t[1] for t in tt))

    if t1 >= t2:
        return None

    p1c = p1 + dlt * t1
    p2c = p1 + dlt * t2

    return p1c, p2c


def elevate_segment(bounds, segm):
    """Elevate line xy-perpendicular segment vertically

    :arg bounds: (xmin, xmax, ymin, ymax)
    :arg segm: 2 vertices of the segment
    :return: 2 new vertices of segment or None if segment outside the bounding box
    """
    _, _, ymin, ymax, zmin, _ = bounds
    p1, p2 = segm
    dlt = p2 - p1
    if not (almost_zero(dlt.x) and almost_zero(dlt.y)):
        return None
    x = p1.x
    return [Vector((x, ymin, zmin)), Vector((x, ymax, zmin))]
