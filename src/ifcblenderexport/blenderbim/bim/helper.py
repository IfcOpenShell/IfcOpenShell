import math
from mathutils import geometry
from mathutils import Vector
import bpy


# TODO: Deprecate this in favour of ifcopenshell.util.unit


class SIUnitHelper:
    prefixes = {
        "EXA": 1e18,
        "PETA": 1e15,
        "TERA": 1e12,
        "GIGA": 1e9,
        "MEGA": 1e6,
        "KILO": 1e3,
        "HECTO": 1e2,
        "DECA": 1e1,
        "DECI": 1e-1,
        "CENTI": 1e-2,
        "MILLI": 1e-3,
        "MICRO": 1e-6,
        "NANO": 1e-9,
        "PICO": 1e-12,
        "FEMTO": 1e-15,
        "ATTO": 1e-18,
    }
    unit_names = [
        "AMPERE",
        "BECQUEREL",
        "CANDELA",
        "COULOMB",
        "CUBIC_METRE",
        "DEGREE CELSIUS",
        "FARAD",
        "GRAM",
        "GRAY",
        "HENRY",
        "HERTZ",
        "JOULE",
        "KELVIN",
        "LUMEN",
        "LUX",
        "MOLE",
        "NEWTON",
        "OHM",
        "PASCAL",
        "RADIAN",
        "SECOND",
        "SIEMENS",
        "SIEVERT",
        "SQUARE METRE",
        "METRE",
        "STERADIAN",
        "TESLA",
        "VOLT",
        "WATT",
        "WEBER",
    ]
    si_conversions = {
        "inch": 0.0254,
        "foot": 0.3048,
        "yard": 0.914,
        "mile": 1609,
        "square inch": 0.0006452,
        "square foot": 0.09290304,
        "square yard": 0.83612736,
        "acre": 4046.86,
        "square mile": 2588881,
        "cubic inch": 0.00001639,
        "cubic foot": 0.02831684671168849,
        "cubic yard": 0.7636,
        "litre": 0.001,
        "fluid ounce UK": 0.0000284130625,
        "fluid ounce US": 0.00002957353,
        "pint UK": 0.000568,
        "pint US": 0.000473,
        "gallon UK": 0.004546,
        "gallon US": 0.003785,
        "degree": math.pi / 180,
        "ounce": 0.02835,
        "pound": 0.454,
        "ton UK": 1016.0469088,
        "ton US": 907.18474,
        "lbf": 4.4482216153,
        "kip": 4448.2216153,
        "psi": 6894.7572932,
        "ksi": 6894757.2932,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "btu": 1055.056,
    }

    @staticmethod
    def get_prefix(text):
        for prefix in SIUnitHelper.prefixes.keys():
            if prefix in text.upper():
                return prefix

    @staticmethod
    def get_prefix_multiplier(text):
        if not text:
            return 1
        prefix = SIUnitHelper.get_prefix(text)
        if prefix:
            return SIUnitHelper.prefixes[prefix]
        return 1

    @staticmethod
    def get_unit_name(text):
        for name in SIUnitHelper.unit_names:
            if name in text.upper().replace("METER", "METRE"):
                return name

    @staticmethod
    def convert(value, from_prefix, from_unit, to_prefix, to_unit):
        """Converts between length, area, and volume units

        :param value: The numeric value you want to convert
        :type value: float
        :param from_prefix: A prefix from IfcSIPrefix. Can be None.
        :type from_prefix: string
        :param from_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
        :type from_unit: string
        :param to_prefix: A prefix from IfcSIPrefix. Can be None.
        :type to_prefix: string
        :param to_unit: IfcSIUnitName or IfcConversionBasedUnit.Name
        :type to_unit: string
        """
        if from_unit in SIUnitHelper.si_conversions:
            value *= SIUnitHelper.si_conversions[from_unit]
        elif from_prefix:
            value *= SIUnitHelper.get_prefix_multiplier(from_prefix)
            if "SQUARE" in from_unit:
                value *= SIUnitHelper.get_prefix_multiplier(from_prefix)
            elif "CUBIC" in from_unit:
                value *= SIUnitHelper.get_prefix_multiplier(from_prefix)
                value *= SIUnitHelper.get_prefix_multiplier(from_prefix)
        if to_unit in SIUnitHelper.si_conversions:
            return value * (1 / SIUnitHelper.si_conversions[to_unit])
        elif to_prefix:
            value *= 1 / SIUnitHelper.get_prefix_multiplier(to_prefix)
            if "SQUARE" in from_unit:
                value *= 1 / SIUnitHelper.get_prefix_multiplier(to_prefix)
            elif "CUBIC" in from_unit:
                value *= 1 / SIUnitHelper.get_prefix_multiplier(to_prefix)
                value *= 1 / SIUnitHelper.get_prefix_multiplier(to_prefix)
        return value


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
    :return: (xmin, xmax, ymin, ymax) in local camera coordinates
    """
    aspect = camera.BIMCameraProperties.raster_y / camera.BIMCameraProperties.raster_x
    size = camera.ortho_scale
    hwidth = size * .5
    hheight = size * .5 * aspect
    scale = parse_diagram_scale(camera)
    xmarg = margin * scale
    ymarg = margin * scale * aspect
    return (-hwidth + xmarg, hwidth - xmarg, -hheight + ymarg, hheight - ymarg)


def clip_segment(bounds, segm):
    """Clipping line segment to bounds

    :arg bounds: (xmin, xmax, ymin, ymax)
    :arg segm: 2 vertices of the segment
    :return: 2 new vertices of segment or None if segment outside the bounding box
    """
    # Liang–Barsky algorithm

    xmin, xmax, ymin, ymax = bounds
    p1, p2 = segm

    def clip_side(p, q):
        if abs(p) < 1e-10:  # ~= 0, parallel to the side
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
