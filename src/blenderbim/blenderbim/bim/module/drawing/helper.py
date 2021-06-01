import bpy
import math
import mathutils.geometry
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
            # check all the faces of this object for a seperation axis
            for i, f in enumerate(self.face):
                d = f.normal
                if self.whichSide(bb.vertex, d, f.vertex[0]) > 0:
                    return False  # all the vertexes are on the +ve side of the face

            # now do it again for the other objects faces
            for i, f in enumerate(bb.face):
                d = f.normal
                if self.whichSide(self.vertex, d, f.vertex[0]) > 0:
                    return False  # all the vertexes are on the +ve side of the face

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
# In the future I will need to rewrite this to allow the user to have custom
# settings for each annotation object, not read from Blender.
def format_distance(value, isArea=False, hide_units=True):
    s_code = "\u00b2"  # Superscript two THIS IS LEGACY (but being kept for when Area Measurements are re-implimented)

    # Get Scene Unit Settings
    scaleFactor = bpy.context.scene.unit_settings.scale_length
    unit_system = bpy.context.scene.unit_settings.system
    unit_length = bpy.context.scene.unit_settings.length_unit

    toInches = 39.3700787401574887
    inPerFoot = 11.999

    if isArea:
        toInches = 1550
        inPerFoot = 143.999

    value *= scaleFactor

    # Imperial Formating
    if unit_system == "IMPERIAL":
        precision = bpy.context.scene.BIMProperties.imperial_precision
        if precision == "NONE":
            precision = 256
        elif precision == "1":
            precision = 1
        elif "/" in precision:
            precision = int(precision.split("/")[1])

        base = int(precision)
        decInches = value * toInches

        # Seperate ft and inches
        # Unless Inches are the specified Length Unit
        if unit_length != "INCHES":
            feet = math.floor(decInches / inPerFoot)
            decInches -= feet * inPerFoot
        else:
            feet = 0

        # Seperate Fractional Inches
        inches = math.floor(decInches)
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
            feet += 1
            inches = 0

        if not isArea:
            tx_dist = ""
            if feet:
                tx_dist += str(feet) + "'"
            if feet and inches:
                tx_dist += " - "
            if inches:
                tx_dist += str(inches)
            if inches and frac:
                tx_dist += " "
            if frac:
                tx_dist += str(frac) + "/" + str(base)
            if inches or frac:
                tx_dist += '"'
        else:
            tx_dist = str("%1.3f" % (value * toInches / inPerFoot)) + " sq. ft."

    # METRIC FORMATING
    elif unit_system == "METRIC":
        precision = bpy.context.scene.BIMProperties.metric_precision
        if precision != 0:
            value = precision * round(float(value) / precision)

        # Meters
        if unit_length == "METERS":
            fmt = "%1.3f"
            if hide_units is False:
                fmt += " m"
            tx_dist = fmt % value
        # Centimeters
        elif unit_length == "CENTIMETERS":
            fmt = "%1.1f"
            if hide_units is False:
                fmt += " cm"
            d_cm = value * (100)
            tx_dist = fmt % d_cm
        # Millimeters
        elif unit_length == "MILLIMETERS":
            fmt = "%1.0f"
            if hide_units is False:
                fmt += " mm"
            d_mm = value * (1000)
            tx_dist = fmt % d_mm

        # Otherwise Use Adaptive Units
        else:
            if round(value, 2) >= 1.0:
                fmt = "%1.3f"
                if hide_units is False:
                    fmt += " m"
                tx_dist = fmt % value
            else:
                if round(value, 2) >= 0.01:
                    fmt = "%1.1f"
                    if hide_units is False:
                        fmt += " cm"
                    d_cm = value * (100)
                    tx_dist = fmt % d_cm
                else:
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
    if props.active_drawing_index is None or len(props.drawings) == 0:
        return None, None
    try:
        drawing = props.drawings[props.active_drawing_index]
        return scene.collection.children["Views"].children[f"IfcGroup/{drawing.name}"], drawing.camera
    except (KeyError, IndexError):
        raise RuntimeError("missing drawing collection")


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


def ortho_view_frame(camera, margin=0.015):
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
